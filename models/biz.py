#!/usr/bin/python
""" holds class Biz"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship

if models.storage_t == 'db':
    place_amenity = Table('place_amenity', Base.metadata,
                          Column('place_id', String(60),
                                 ForeignKey('places.id', onupdate='CASCADE',
                                            ondelete='CASCADE'),
                                 primary_key=True),
                          Column('amenity_id', String(60),
                                 ForeignKey('amenities.id', onupdate='CASCADE',
                                            ondelete='CASCADE'),
                                 primary_key=True))


class Biz(BaseModel, Base):
    """Representation of a Business """
    if models.storage_t == 'db':
        __tablename__ = 'biz'
        city_id = Column(String(60), ForeignKey('cities.id'), nullable=False)
        user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
        name = Column(String(128), nullable=False)
        description = Column(String(1024), nullable=True)
        # biz image ids?
        latitude = Column(Float, nullable=True)
        longitude = Column(Float, nullable=True)
        category = Column(String(10),ForeignKey('categories.id'), nullable=True) # biz can lack a category
        reviews = relationship("Review",
                               backref="place",
                               cascade="all, delete, delete-orphan")
        # make biz tags? eg pet friendly (amenities)
        amenities = relationship("Amenity",
                                 secondary=place_amenity,
                                 viewonly=False)
        # add biz opening and closing hours? -> not necessary when creating
    else:
        city_id = ""
        user_id = ""
        name = ""
        description = ""
        latitude = 0.0
        longitude = 0.0
        category_id = ""
        reviews = []
        amenity_ids = []

    def __init__(self, *args, **kwargs):
        """initializes Place"""
        super().__init__(*args, **kwargs)

    if models.storage_t != 'db':
        @property
        def reviews(self):
            """getter attribute returns the list of Review instances"""
            from models.review import Review
            review_list = []
            all_reviews = models.storage.all(Review)
            for review in all_reviews.values():
                if review.biz_id == self.id:
                    review_list.append(review)
            return review_list

        """
        def amenities(self):
            getter attribute returns the list of Amenity instances
            from models.amenity import Amenity
            amenity_list = []
            all_amenities = models.storage.all(Amenity)
            for amenity in all_amenities.values():
                if amenity.biz_id == self.id:
                    amenity_list.append(amenity)
            return amenity_list
        """
