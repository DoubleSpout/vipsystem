# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vipsystem import app
import json


db = SQLAlchemy(app)

#虚拟货物的model
class Goods(db.Model):
    #表名
    __tablename__ = 'Goods'
    
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
        
    @staticmethod
    def parseToList(objary):
        objLen = len(objary)
        tempArray = []
        for i in range(0,objLen):
            if not objary[i]:
                tempArray.append({})
            else:
                tempArray.append({
                    'Id':objary[i].Id,
                    'Name':objary[i].Name,
                    'Price':objary[i].Price,
                    'Inventory':objary[i].Inventory,
                    'Type':objary[i].Type,
                    'Code1':objary[i].Code1 or '',
                    'Code2':objary[i].Code2 or '',
                    'IsShow':objary[i].IsShow,
                    'EName':objary[i].EName,
                    'WriteTime' :objary[i].WriteTime.strftime('%Y-%m-%d %H:%M:%S'),          
                })
        return tempArray
   
