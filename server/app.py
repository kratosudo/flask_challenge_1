#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route("/heroes")
def heroes():
    heroes = Hero.query.all()
    response = [hero.to_dict(only=("id", "name", "super_name")) for hero in heroes]
    return make_response(response, 200)

@app.route('/heroes/<int:id>')
def heroes_by_id(id):
    hero = Hero.query.filter(Hero.id==id).first()
    if not hero:
        error_body = {
            "error": "Hero not found"
            }
        return make_response(error_body, 404)
    
    return make_response(hero.to_dict(), 200)

@app.route('/powers')
def powers():
    powers = [power.to_dict(only=('description', 'id', 'name')) for power in Power.query.all()]
    return make_response(powers, 200)

@app.route('/powers/<int:id>',  methods=['GET', 'PATCH'])
def powers_by_id(id):
    power = Power.query.filter(Power.id==id).first()
    if not power:
        error_body = {
            "error": "Power not found"
            }
        return make_response(error_body, 404)
    if request.method == 'GET':
        return make_response(power.to_dict(only=('description', 'id', 'name')), 200)
    elif request.method == 'PATCH':
        validation_errors = []

        # Update power attributes and validate
        for attr in request.json:
            if attr == 'description':
                description_value = request.json.get(attr)
                if not isinstance(description_value, str) or len(description_value) < 20:
                    validation_errors.append("validation errors")
            else:
                setattr(power, attr, request.json.get(attr))

        # If there are validation errors, return a standardized error response
        if validation_errors:
            return make_response({"errors": validation_errors}, 400)  # Bad Request status code

        # Update valid fields and commit changes
        for attr in request.json:
            setattr(power, attr, request.json.get(attr))

        db.session.commit()
        return make_response(power.to_dict(), 200)

@app.route('/hero_powers', methods=['GET', 'POST'])
def hero_powers():
    if request.method == 'GET':
        hero_power = HeroPower.query.all()
        return make_response([hero_power.to_dict() for hero_power in hero_power], 200)

    elif request.method == 'POST':
        strength = request.json.get('strength')
        power_id = request.json.get('power_id')
        hero_id = request.json.get('hero_id')

        #Could not figure out how to import validation
        valid_strengths = {'Strong', 'Weak', 'Average'}
        if strength not in valid_strengths:
            return make_response({"errors": ["validation errors"]}, 400)

        # Create a new HeroPower instance
        new_power = HeroPower(
            strength=strength,
            power_id=power_id,
            hero_id=hero_id
        )

        # Commit changes
        db.session.add(new_power)
        db.session.commit()
        return make_response(new_power.to_dict(), 200)
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)