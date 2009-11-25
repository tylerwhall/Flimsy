# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, String, Numeric, Boolean, DateTime
#from sqlalchemy.orm import relation, backref

from flimsy.model import DeclarativeBase, metadata, DBSession

from datetime import datetime

__all__ = ["Sensor"]

class Sensor(DeclarativeBase):
    __tablename__ = 'fl_sensor'
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Numeric, default=0)
    lng = Column(Numeric, default=0)
    flooded = Column(Boolean, default=False)
    updated = Column(DateTime, default=datetime.now)
    
    #}
