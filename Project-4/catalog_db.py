import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class User(Base):
    """This table store the user's info"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    picture = Column(String(250))
        
class CatalogCategory(Base):
    """This table store the catalog category data"""
    __tablename__ = 'catalog_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serializeable format"""
        return {
            "id" : self.id,
            "name" : self.name,
        }


class CategoryItem(Base):
    """This table store the items data"""
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(1000))
    catalog_category_id = Column(Integer, ForeignKey('catalog_category.id'))
    catalog_category = relationship(CatalogCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serializeable format"""
        return {
            "id" : self.id,
            "category" : self.catalog_category.name,
            "name" : self.name,
            "description" : self.description,
        }


engine = create_engine('sqlite:///catalog_app.db')
Base.metadata.create_all(engine)
