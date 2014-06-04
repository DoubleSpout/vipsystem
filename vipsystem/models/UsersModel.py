# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vipsystem import app
db = SQLAlchemy(app)

#vip用户的model
class VIP_User(db.Model):
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


    def __repr__(self):
        return '<Category %r>' % self.name

#积分获取日志model
class Log_Score(db.Model):
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

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, UserId, Way):
        self.UserId = UserId
        self.Way = Way
     

    def __repr__(self):
        return '<Post %r>' % self.title

