# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vipsystem import app


db = SQLAlchemy(app)

#虚拟货物的model
class Goods(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Price = db.Column(db.Integer)
    Inventory =  db.Column(db.Integer)
    Type = db.Column(db.String(255))
    Code1 = db.Column(db.String(255))
    Code2 = db.Column(db.String(255))
    IsShow = db.Column(db.Integer)
    WriteTime = db.Column(db.DateTime)
    EName = db.Column(db.String(255))
    
    def __init__(self, UserId):
        self.UserId = UserId

    def __repr__(self):
        return '<Category %r>' % self.name
