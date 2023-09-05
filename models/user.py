#!/usr/bin/python3
""" holds class User"""

import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from hashlib import md5


class User(BaseModel, Base):
    """Representation of a user """
    if models.storage_t == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        user_name = Column(String(128), nullable=False) # make this primary key?
        is_active = Column(Boolean, default=True)
        # add photos / videos -> both for reviews & personal
        # add friends
        friends = relationship("User", backref="friend") # verify
        # add favorite__businesses
        fav_bizes = relationship("Biz", backref="fav_customer")
        # add favorite_reviews
        fav_reviews = relationship("Review", backref="fav_user")
        reviews = relationship("Review", backref="user")
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""
        user_name = ""
        is_active = True # manage account status
        friends = []
        fav_bizes = []
        fav_reviews = []
        reviews = []

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)

    def get_id(self):
        """ Required for Flask-login to get user's unique id
        """
        return self.id # or any other unique attr

    @property
    def is_authenticated(self):
        """ check if user is authenticated """
        return True # temp sln

    """
    def __setattr__(self, name, value):
        sets a password with md5 encryption
        if name == "password":
            value = md5(value.encode()).hexdigest()
        super().__setattr__(name, value)
     """
