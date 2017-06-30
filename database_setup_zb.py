from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Alcohol(Base):
    __tablename__ = 'alcohol'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Cocktail(Base):
    __tablename__ = 'cocktail'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    ingredients = Column(String(250))
    alcohol_id = Column(Integer, ForeignKey('alcohol.id'))
    alcohol = relationship(Alcohol)
    picture = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'ingredients': self.ingredients,
            'id': self.id,
        }


engine = create_engine('sqlite:///restaurantmenuwithusers.db')


Base.metadata.create_all(engine)
