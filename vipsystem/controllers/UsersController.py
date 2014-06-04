# -*- coding: utf-8 -*-
from vipsystem import app
from vipsystem import app
import flask
import json
from flask import render_template, request, redirect, url_for, sessions
from vipsystem.models import UsersModel
from vipsystem.bussiness import UsersBl
from vipsystem.bussiness import LoggerBl
from vipsystem import config
import httplib
import urllib
from xml.dom.minidom import parse, parseString

#实现登录跳转
@app.route('/login')
def login():
    backUrl = urllib.urlencode({'service':app.config['CURRENT_HOST']+'/loginjump'})
    passprotHost = app.config['PASSPORT_SERVER']
    url = 'https://{0}/login/mini/?{1}'.format(passprotHost, backUrl)
    return redirect(url, code=302)

#登录跳转回来之后，
@app.route('/loginjump')
def loginjump():
    #获得登录的ticket
    ticket = request.args.get('ticket')
    #定义service和验证ticket的host
    passprotHost = app.config['PASSPORT_SERVER']
    #定义参数
    params = urllib.urlencode({'ticket':ticket, 'service':app.config['CURRENT_HOST']+'/loginjump'});
    conn = httplib.HTTPSConnection(passprotHost)
    conn.request('GET', '/ServiceValidate?'+params,)
    res = conn.getresponse()
    data = res.read()  #读取响应的xml文档
    conn.close()       #关闭连接
    
    #开始解析cas的xml文档
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
            userid = t2
        elif t1 == 'UserName':
            username = t2
    
    #如果获取用户信息失败
    if userid == 0 or username =='':
        LoggerBl.log.error('登录成功,解析xml获取用户信息失败,返回数据{0}'.format(data))
        return '获取用户信息失败'
    
    #写入session
    flask.session['userid'] = userid
    flask.session['username'] = username
    
    userbl = UsersBl.UsersBl(userid)
    userbl.initUser()#初始化用户，如果不存在就插入数据库
    #跳转到首页
    return redirect('/', code=302)


#用户签到ajax
@app.route('/sign/sign', methods=['GET', 'POST'])
def sign_sign():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return json.dumps({'error':1,data:'请先登录'})
    
    timestamp = request.args.get('timestamp')
    
    try:
        timestamp = int(timestamp);
    except ValueError:
        return json.dumps({'error':1,data:'timestamp参数非法'})
    
    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    
    #执行签到的操作
    r = userbl.daySign()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        
    return json.dumps(r)


#用户领取薪水ajax
@app.route('/salary/get', methods=['GET', 'POST'])
def salary_get():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return json.dumps({'error':1,data:'请先登录'})
    
    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getSalary()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        
    return json.dumps(r)


#获取用户状态ajax
@app.route('/user/status', methods=['GET'])
def user_status():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return json.dumps({'error':1,data:'请先登录'})
    
    uid = flask.session['userid']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        
    return json.dumps(r)



#以下是页面控制器
@app.route('/', methods=['GET'])
def index():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)
        
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
        
    return render_template('index.html', data=r['data'],uid=uid,uname=uname) 


#每日签到页面
@app.route('/sign/index', methods=['GET'])
def index():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)
        
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
    
    r2 = userbl.getCurMonthSign()
        
    return render_template('day_sign.html', data=r['data'],uid=uid,uname=uname,signArray = r2['data'])


#常见问题
@app.route('/qa/index', methods=['GET'])
def index():
    if not flask.session.has_key('userid') or flask.session['userid'] == 0:
        return redirect('/login', code=302)
        
    uid = flask.session['userid']
    uname = flask.session['username']
    userbl = UsersBl.UsersBl(uid)
    
    #执行操作
    r = userbl.getUserVipStatus()
    
    #如果出错，记录日志
    if r['error'] == 1:
        LoggerBl.log.error(r.data)
        #出错跳转到6998主页
        return redirect('http://www.6998.com', code=302)
        
    return render_template('qa_index.html', data=r['data'],uid=uid,uname=uname) 


