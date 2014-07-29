# -*- coding: utf-8 -*-
from vipsystem import app
import flask
import json
import re
from flask import render_template, request, redirect, url_for, sessions, Response
from vipsystem.models import UsersModel
from vipsystem.bussiness import UsersBl
from vipsystem.bussiness import GoodsBl
from vipsystem.bussiness import LoggerBl
from vipsystem import config
import httplib
import urllib
from xml.dom.minidom import parse, parseString


#获取虚拟商品列表
@app.route(app.config['SELF_PREFIX']+'/goods/listajax', methods=['GET'])
@UsersBl.checkLoginJson
def goods_listajax():
    uid = flask.session['userid']
    uname = flask.session['username']
    uip = request.remote_addr
    goodsbl = GoodsBl.GoodsBl(uid,uname,uip)
        
    #执行操作
    r = goodsbl.getGoods()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return json.dumps(r)

#获取虚拟商品列表
@app.route(app.config['SELF_PREFIX']+'/goods/listjs', methods=['GET'])
@UsersBl.getUserStatus
def goods_listjs(udict):
    uid = udict['uid']
    uname = udict['uname']
    uip = request.remote_addr
    goodsbl = GoodsBl.GoodsBl(uid,uname,uip)
        
    #执行操作
    r = goodsbl.getGoods()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return 'window["_gooslist"]={0}'.format(json.dumps(r))

#获取特定虚拟商品
@app.route(app.config['SELF_PREFIX']+'/goods/infoajax', methods=['GET'])
@UsersBl.checkLoginJson
def goods_infoajax():
    
   #判断参数ename
    ename = request.args.get('ename') or ''
    if not ename.isalnum():
        return Response(json.dumps({'error':1,'data':'参数ename有误'}),mimetype='application/json')
        
    uid = flask.session['userid']
    uname = flask.session['username']
    uip = request.remote_addr
    goodsbl = GoodsBl.GoodsBl(uid,uname,uip)
        
    #执行操作
    r = goodsbl.getGoodsDetail(ename)
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return Response(json.dumps(r),mimetype='application/json')


#换取虚拟物品
@app.route(app.config['SELF_PREFIX']+'/goods/exchange', methods=['GET','POST'])
@UsersBl.checkLoginJson
def goods_exchange():
    
    #判断参数ename
    ename = request.form["ename"] or ''
    #print(ename)
    if not ename.isalnum():
        return Response(json.dumps({'error':1,'data':'参数ename有误'}),mimetype='application/json')
    
    
    uid = flask.session['userid']
    uname = flask.session['username']
    uip = request.remote_addr
    goodsbl = GoodsBl.GoodsBl(uid,uname,uip)
        
    #执行操作
    r = goodsbl.exchangeGoods(ename)
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return Response(json.dumps(r),mimetype='application/json')



#以下是页面控制器
#兑换首页
@app.route(app.config['SELF_PREFIX']+'/goods/index', methods=['GET'])
@UsersBl.getUserStatus
def goods_index(udict):
        
    return render_template('goods_index.html',data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'],user=udict['user'])

@app.route('/vip/goods/list', methods=['GET'])
@UsersBl.getUserStatus
def goods_list(udict):
    
    return render_template('goods_list.html', data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'],user=udict['user'])

#物品详细页面
@app.route(app.config['SELF_PREFIX']+'/goods/info', methods=['GET'])
@UsersBl.getUserStatus
def goods_info(udict):
    #判断参数ename
    ename = request.args.get('ename') or ''
    if not ename.isalnum():
        return 'ename参数有误'
    
    uip = request.remote_addr   
    #执行操作    
    goodsbl = GoodsBl.GoodsBl(udict['uid'],udict['uname'],uip)
    goodsDetail = goodsbl.getGoodsDetail(ename)['data']
    if 'Id' not in goodsDetail:
        return 'not found goods.',404
         
    return render_template('goods_detail.html', data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'],user=udict['user'],goods=goodsDetail,ename=ename,) 
