#!/usr/bin/python
""" holds class Review"""
import models
from models.base_model import BaseModel, Base
from models.user import User
from models.biz import Biz
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, ForeignKey


class Review(BaseModel, Base):
    """Representation of Review """
    if models.storage_t == 'db':
        __tablename__ = 'reviews'
        biz_id = Column(String(60), ForeignKey('bizs.id'), nullable=False)
        user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
        text = Column(String(1024), nullable=False)
        # add button count for found useful
        found_useful = Column(Integer, nullable=False, default=0)
        # add user ability to favorite review
        # add rating

    else:
        biz_id = ""
        user_id = ""
        text = ""
        found_useful = 0
        rating = 1 # lowest by default

    def __init__(self, *args, **kwargs):
        """initializes Review"""
        super().__init__(*args, **kwargs)
    
    if models.storage_t != "db":
        @property
        def get_biz_name(self):
            """ return the business name for the review"""
            biz_obj = models.storage.get(Biz, self.biz_id)
            if biz_obj is None:
                biz_name = ""
            else:
                biz_name = biz_obj.name
            return biz_name

        @property
        def get_user_name(self):
            """ get user who reviewed """
            user_obj = models.storage.get(User, self.user_id)
            u_name = user_obj.user_name
            return u_name
