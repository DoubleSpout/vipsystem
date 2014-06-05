# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vipsystem import app
import json

db = SQLAlchemy(app)

#vip用户的model
class VIP_User(db.Model):
    #表名
    __tablename__ = 'VIP_User'
    
    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer)
    CurrentLevel = db.Column(db.Integer)
    HistoryLevel = db.Column(db.Integer)
    Score = db.Column(db.Integer)
    HistoryScore = db.Column(db.Integer)
    WriteTime = db.Column(db.DateTime)

    def __init__(self, UserId,CurrentLevel=0,HistoryLevel=0,Score=0,HistoryScore=0):
        self.UserId = UserId
        self.CurrentLevel = CurrentLevel
        self.HistoryLevel = HistoryLevel
        self.Score = Score
        self.HistoryScore = HistoryScore
        self.WriteTime = datetime.now()
        
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
                    'CurrentLevel':objary[i].CurrentLevel,
                    'HistoryLevel':objary[i].HistoryLevel,
                    'Score':objary[i].Score,
                    'HistoryScore':objary[i].HistoryScore,
                    'WriteTime' :objary[i].WriteTime.strftime('%Y-%m-%d %H:%M:%S'),          
                })
        return tempArray