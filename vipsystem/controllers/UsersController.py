# -*- coding: utf-8 -*-
#coding=utf-8
from vipsystem import app
import os
import flask
import json
from flask import render_template, request, redirect, url_for, sessions, Response, session, make_response
from vipsystem.models import UsersModel
from vipsystem.bussiness import UsersBl
from vipsystem.bussiness import LoggerBl
from vipsystem import config
import httplib
import urllib
from xml.dom.minidom import parse, parseString
from datetime import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#实现登录跳转
@app.route(app.config['SELF_PREFIX']+'/login')
def login():
    jumpto = urllib.unquote(request.args.get('jumpto') or app.config['SELF_PREFIX'])

    backUrl = urllib.urlencode({'service':app.config['CURRENT_HOST']+ app.config['SELF_PREFIX'] +'/loginjump?jumpto='+urllib.quote(jumpto)})
    #print(backUrl)
    passprotHost = app.config['PASSPORT_SERVER']
    url = 'https://{0}{1}?{2}'.format(passprotHost,app.config['LOGIN_JUMP'],backUrl)

    return redirect(url, code=302)

#登录跳转回来之后，
@app.route(app.config['SELF_PREFIX']+'/loginjump')
def loginjump():
    #获得登录的ticket
    ticket = request.args.get('ticket')
    jumpto = request.args.get('jumpto')
    print(jumpto)
    if not jumpto:
        return '没有jumpto参数'
    
    jumpto = urllib.unquote(jumpto)
    uip = request.remote_addr
    
    #定义service和验证ticket的host
    passprotHost = app.config['PASSPORT_SERVER']
    #定义参数  
    try:
        params = urllib.urlencode({'ticket':ticket, 'service':app.config['CURRENT_HOST']+ app.config['SELF_PREFIX'] +'/loginjump?jumpto='+urllib.quote(jumpto)})
        #print(params)
        conn = httplib.HTTPSConnection(passprotHost,timeout=10)
        conn.request('GET', '/ServiceValidate?'+params)
        res = conn.getresponse()
        data = res.read()  #读取响应的xml文档
    except Exception as e:
        LoggerBl.log.error('userbl.initUser() 验证ticket错误,params:{0},错误:{1}, 响应:{2}'.format(params,e,data))
    finally:
        conn.close()       #关闭连接
    
    if res.status != 200:
        LoggerBl.log.error('请求{0}/ServiceValidate?{1}出错,错误信息{2}'.format(passprotHost, params, data))
        return data
    
    #开始解析cas的xml文档
    try:
        doc = parseString(data)
        failNode = doc.getElementsByTagName('cas:authenticationFailure')
        if len(failNode)>0:
            return data
        
        userid=0
        username=''
        sucNode = doc.getElementsByTagName('cas:attribute')
        for item in sucNode:
            t1 = item.getElementsByTagName('cas:name')[0].childNodes[0].data
            t2 = item.getElementsByTagName('cas:value')[0].childNodes[0].data
            if t1 == 'UserID':
                userid = int(t2)
            elif t1 == 'UserName':
                username = t2
    except Exception as e:
        LoggerBl.log.error('userbl.initUser() 解析xml错误, 原因:{0},xml文档:{1}'.format(e,data))
    
    #如果获取用户信息失败
    if userid == 0 or username =='':
        LoggerBl.log.error('登录成功,解析xml获取用户信息失败,返回数据{0}'.format(data))
        return '获取用户信息失败'
    
    #写入session
    try:
        flask.session['userid'] = userid
        flask.session['username'] = urllib.unquote(username.encode('utf8')).decode('utf8')       
    except Exception as e:
        LoggerBl.log.error('userbl.initUser() 写入session出错, 原因:{0},userid:{1}'.format(e,userid))
    #print(flask.session['username'])
    
    
    try:
        userbl = UsersBl.UsersBl(userid)
        userbl.initUser(uip)#初始化用户，如果不存在就插入数据库
    except Exception as e:
        LoggerBl.log.error('userbl.initUser()错误,userid:{0},错误:{1}'.format(userid,e))
    #跳转到首页
    #print(flask.session)
    #return 'login ok'
    return redirect(jumpto, code=302)


#用户签到ajax
@app.route(app.config['SELF_PREFIX']+'/sign/sign', methods=['GET', 'POST'])
@UsersBl.checkLoginJson
def sign_sign():
    
    #判断timestamp的合法性
    timestamp = request.args.get('ts') or ''
    if not timestamp.isdigit():
        return Response(json.dumps({'error':1,'data':'ts 参数非法'}),mimetype='application/json')        
    
    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    
    #执行签到的操作
    r = userbl.daySign(int(timestamp))
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return Response(json.dumps(r),mimetype='application/json')


#用户领取薪水ajax
@app.route(app.config['SELF_PREFIX']+'/salary/get', methods=['GET', 'POST'])
@UsersBl.checkLoginJson
def salary_get():

    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    uip = request.remote_addr
    
    #执行操作
    r = userbl.getSalary(uip)
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
        
    return Response(json.dumps(r),mimetype='application/json')
    


#获取用户状态ajax
@app.route(app.config['SELF_PREFIX']+'/user/status', methods=['GET'])
@UsersBl.checkLoginJson
def user_status():
    
    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r['data'])
        r['data'] = str(r['data'])
    return Response(json.dumps(r),mimetype='application/json')



#以下是页面控制器
@app.route(app.config['SELF_PREFIX'], methods=['GET'])
@UsersBl.getUserStatus
def index(udict):
    #print(flask.session)
    return render_template('index.html', data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'],user=udict['user']) 

#每日签到页面
@app.route(app.config['SELF_PREFIX']+'/sign/index', methods=['GET'])
@UsersBl.checkLoginJson
@UsersBl.getUserStatus
def sign_index(udict):        
    r2 = userbl.getCurMonthSign()    
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')   
    return render_template('day_sign.html', data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'], signArray=json.dumps(r2['data']),today=today)


#常见问题
@app.route(app.config['SELF_PREFIX']+'/qa/index', methods=['GET'])
@UsersBl.getUserStatus
def qa_index(udict):
     return render_template('qa_index.html', data=udict['user']['data'],uid=udict['uid'],uname=udict['uname'],user=udict['user'])

#以下是页面控制器
@app.route(app.config['SELF_PREFIX']+'/logout', methods=['GET'])
def logout():
    session.clear()
    return 'logout'



