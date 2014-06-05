# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vipsystem import app
import json
db = SQLAlchemy(app)

#积分获取日志model
class Log_Score(db.Model):
    #表名
    __tablename__ = 'Log_Score'
    
    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer)
    Type = db.Column(db.String(16))
    Score = db.Column(db.Integer)
    Way = db.Column(db.String(16))
    ScoreCode1 = db.Column(db.String(255))
    ScoreCode2 = db.Column(db.String(255))
    ScoreCode3 = db.Column(db.String(255))
    ScoreCode4 = db.Column(db.String(255))
    ScoreCode5 = db.Column(db.String(255))
    Writetime = db.Column(db.DateTime)


    def __init__(self, UserId, Way):
        self.UserId = UserId
        self.Way = Way
        
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
                    'UserId':objary[i].UserId,
                    'Type':objary[i].Type,
                    'Score':objary[i].Score,
                    'Way':objary[i].Way,
                    'ScoreCode1':objary[i].ScoreCode1 or '',
                    'ScoreCode2':objary[i].ScoreCode2 or '',
                    'ScoreCode3':objary[i].ScoreCode3 or '',
                    'ScoreCode4':objary[i].ScoreCode4 or '',
                    'ScoreCode5':objary[i].ScoreCode5 or '',
                    'Writetime' :objary[i].Writetime.strftime('%Y-%m-%d %H:%M:%S'),          
                })
        return tempArray

