from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationship with HeroPower and Power
    hero_powers = relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power', creator=lambda power_obj: HeroPower(hero=power_obj))

    # Serialization rules
    serialize_rules = ('-hero_powers.hero', '-powers.heroes')

    def __repr__(self):
        return f'<Hero {self.id}, {self.name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers=db.relationship('HeroPower', back_populates="power" ,cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero', creator=lambda hero_obj: HeroPower(hero=hero_obj))
    # add serialization rules
    serialize_rules=('-hero_powers.power',) 
    # add validation
    @validates('description')
    def validate_description(self, key, description):
        if not description:
            raise ValueError("Description must be present.")
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return description
    
    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')
    # add serialization rules
    serialize_rules=('-hero.hero_powers','-power.hero_powers')
    
    # add validation
    @validates('strength')
    def validate_strength(self, key, strength):
        valid_strengths = {'Strong', 'Weak', 'Average'}
        if strength not in valid_strengths:
            raise ValueError(f"Strength must be one of the following values: {', '.join(valid_strengths)}")
        return strength
    
    def __repr__(self):
        return f'<HeroPower {self.id}>'
