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
@app.route('/goods/listajax', methods=['GET'])
def goods_listajax():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return json.dumps({'error':1,'data':'请先登录'})
    
    uid = flask.session['userid']
    uname = flask.session['userid']
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
@app.route('/goods/listjs', methods=['GET'])
def goods_listjs():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return json.dumps({'error':1,'data':'请先登录'})
    
    uid = flask.session['userid']
    uname = flask.session['userid']
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
@app.route('/goods/infoajax', methods=['GET'])
def goods_infoajax():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return Response(json.dumps({'error':1,'data':'请先登录'}),mimetype='application/json')
    
   #判断参数ename
    ename = request.args.get('ename') or ''
    if not ename.isalnum():
        return Response(json.dumps({'error':1,'data':'参数ename有误'}),mimetype='application/json')
        
    uid = flask.session['userid']
    uname = flask.session['userid']
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
@app.route('/goods/exchange', methods=['GET','POST'])
def goods_exchange():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return Response(json.dumps({'error':1,'data':'请先登录'}),mimetype='application/json')
    
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
@app.route('/goods/index', methods=['GET'])
def goods_index():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)
        
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
        
    return render_template('goods_index.html', data=r['data'],uid=uid,uname=uname,user=r)

@app.route('/goods/list', methods=['GET'])
def goods_list():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)
        
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
        
    return render_template('goods_list.html', data=r['data'],uid=uid,uname=uname,user=r)

#物品详细页面
@app.route('/goods/info', methods=['GET'])
def goods_info():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)

    #判断参数ename
    ename = request.args.get('ename') or ''
    if not ename.isalnum():
        return 'ename参数有误'
    
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    uip = request.remote_addr
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
    
    goodsbl = GoodsBl.GoodsBl(uid,uname,uip)
    goodsDetail = goodsbl.getGoodsDetail(ename)['data']
    if 'Id' not in goodsDetail:
        return 'not found goods.',404
         
    return render_template('goods_detail.html', data=r['data'],uid=uid,uname=uname,ename=ename,user=r,goods=goodsDetail) 
