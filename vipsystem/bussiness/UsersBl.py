# -*- coding: utf-8 -*-
from functools import wraps
import flask
import hashlib
import time
import httplib
import urllib
import json
import calendar
from datetime import datetime
from vipsystem import app
from vipsystem import config
from vipsystem.models import UsersModel
from vipsystem.models import LogscoreModel
from vipsystem.bussiness import LoggerBl
from flask import render_template, request, redirect, url_for, sessions, Response, session
from sqlalchemy import *
from flask.ext.sqlalchemy import SQLAlchemy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#数据库访问
db = SQLAlchemy(app)

#vip对应等级可以补签的次数
vipPatchTimes = (0,2,3,5,8,10)
weekToCH = (u"日",u"一",u"二",u"三",u"四",u"五",u"六")

#定义用户业务层
class UsersBl(object):

    def __init__(self,uid):
        self.uid = int(uid)
    
    #初始化用户
    def initUser(self,uip):
        userDict = UsersModel.VIP_User.query.filter_by(UserId=self.uid).all()
        uip = uip or '127.0.0.1'
        if len(userDict) > 0 :
            return
        
        #如果没有记录,将用户信息插入数据库
        me = UsersModel.VIP_User(int(self.uid))
        db.session.add(me)
        db.session.commit()
        #插入完成之后,请求coreservice 更新用户vip等级
        updateDict = {'UserID':self.uid, 'IPAddress':uip, 'RechargeID':0}
        updateResult = self.sendRequest('POST','/VIPCenter/UserVIPDoPay',updateDict)

        if updateResult['error'] == 1:
            host=app.config['CORESERVICE_HOST']
            LoggerBl.log.error('请求 {0}/VIPCenter/UserVIPDoPay出错,参数 {1}, 错误信息{2}'.format(host, json.dumps(updateDict), updateResult['data']))
        pass
    
    def getUserSignDayCount(self):
        uid = self.uid
        dayDict = {}
        now = datetime.now()
        #获得当前日期格式
        dayDict['signDate'] = now.strftime('%m-%d')
        dayDict['signWeek'] = u'周{0}'.format(weekToCH[int(now.strftime('%w'))])
        #获得当月签到次数
        curMonthTime = datetime(now.year,now.month,1,0,0,0)
        dayDict['signCount'] = LogscoreModel.Log_Score.query.filter_by(Way='day',UserId=self.uid).filter(LogscoreModel.Log_Score.Writetime >= curMonthTime).count()
        return dayDict
        
    def sendRequest(self,method,url,paramDict,host=''):
        #请求coreservice接口，获取用户vip信息
        #如果没有传递host参数
        if not host or host == '':
            host=app.config['CORESERVICE_HOST']
        
        #生成参数    
        if not paramDict:
            paramDict = {}
        paramDictStr = urllib.urlencode(paramDict)
        
        #如果是coreservice服务器，则前缀加上/api
        if host == app.config['CORESERVICE_HOST']:
            url = '/api'+url
            paramDictStr = json.dumps(paramDict)       
           
        conn = httplib.HTTPConnection(host)
        #尝试连接coreservice主机
        
        errPrefix = 'method:{0},host:{1},url:{2},param:{3}'.format(method,host,url,paramDictStr)
        
        try:
            if method == 'POST':
                headers = {"Content-type": "application/x-www-form-urlencoded",
                            "Accept": "text/plain"}
                #如果是coreservice转json
                if host == app.config['CORESERVICE_HOST']:
                    headers = {"Content-type": "application/json",
                            "Accept": "application/json"}
                    
                
                conn.request(method, url, paramDictStr, headers)
            else: 
                conn.request(method, url+'?'+paramDictStr)
        except Exception as err:
             return {'error':1,'data':'{0},{1}'.format(errPrefix,err)}
        
        #获取响应  
        res = conn.getresponse()
        data = res.read()  #读取响应
             #关闭连接
        #print(res)
        
        if res.status != 200 :
            return {'error':1,'data':'{0}, coreservice服务异常,状态:{1},响应:{2}'.format(errPrefix,res.status,data)}
        conn.close()       
        
        if app.config['ENV'] == 'Debug':
            print('--------------')
            print(errPrefix)
            print(res.status)
            print(data)
            print('--------------')       
        
        #将data转换成dict
        dataDict = {}
        try:
            dataDict = json.loads(data)
        except Exception as err:
             return {'error':1,'data':'json decode error,{0},{1}'.format(errPrefix,err)}
        
        #如果接口处理失败
        if not dataDict.has_key('ret'):
            return dataDict
        
        if dataDict['ret'] == False:
            return {'error':1,'data':dataDict['errMsg']}
        #接口处理成功
        return {'error':0,'data':dataDict}
        
    def getUserLastGame(self):
        dataDict = self.sendRequest('POST','/passport/GameLoadByUser',{'userid':self.uid})
        userGame = []
        if dataDict['result'] == 'SUCCESS':
            userGame = dataDict['list']
        return userGame
    
    #public获取用户vip状态
    def getUserVipStatus(self):
        #请求coreservice接口，获取用户vip信息
        dataDict = self.sendRequest('POST','/VIPCenter/UserVIPDetail',{'UserID':self.uid})
        #获取签名次数
        tempDict = self.getUserSignDayCount()
        #更新到字典
        dataDict.update(tempDict)
        if dataDict['error'] != 1:
            dataDict['data']['amountNext'] = dataDict['data']['amountNearly'] + dataDict['data']['amountNeed']
            #print(dataDict['data']['amountNearly']/dataDict['data']['amountNext'])
            if dataDict['data']['amountNeed'] == 0:
                 dataDict['data']['amountRate1'] = 85
                 dataDict['data']['amountRate2'] = 0
            else:                
                #dataDict['data']['amountNearly'] = dataDict['data']['amountNext']
                dataDict['data']['amountRate1'] = int((float(dataDict['data']['amountNearly'])/float(dataDict['data']['amountNext'])) *0.85*100)
                dataDict['data']['amountRate2'] = int((1 - float(dataDict['data']['amountNearly'])/float(dataDict['data']['amountNext']))*0.85*100)
                if dataDict['data']['amountRate1']>= 85:
                    dataDict['data']['amountRate1'] = 85
                    dataDict['data']['amountRate2'] = 0
        
        userGame = self.getUserLastGame()
        dataDict['userGame'] = userGame
        print(dataDict)
        return dataDict
        
    #public用户领取工资
    def getSalary(self,ip='127.0.0.1'):
        dataDict = self.sendRequest('POST','/VIPCenter/UserVIPSalaryGet',{'UserID':self.uid,'IPAddress':ip})       
        return dataDict
    
    #public获取当月的签到状态列表
    def getCurMonthSign(self):
        now = datetime.now()
        curMonthTime = datetime(now.year,now.month,1,0,0,0)
        #获取当月的签到状态列表
        signArray = LogscoreModel.Log_Score.query.filter_by(Way='day',UserId=self.uid).filter(LogscoreModel.Log_Score.Writetime >= curMonthTime).order_by(desc(LogscoreModel.Log_Score.ScoreCode1)).all()       
        #转换成list
        signArray = LogscoreModel.Log_Score.parseToList(signArray)        
        return {'error':0, 'data':signArray}
    
    
    def daySign(self,signTime):
        #积分获取和消费的url
        scoreLogUrl = '/VIPCenter/UserVIPScoreUpdate'
        
        uid = self.uid
        
        
        #转换signTime类型
        now = datetime.now()
        signDateDict = datetime.fromtimestamp(signTime)
        
        #转时间戳
        signTime = datetime(signDateDict.year, signDateDict.month, signDateDict.day,0,0,0)
        signTime = int(time.mktime(signTime.timetuple()))
        
        #设置当天时间    
        todayZeroTime = datetime(now.year,now.month,now.day,0,0,0)
        todayZeroTs = todayZeroTime.timetuple()
        todayZeroTs = int(time.mktime(todayZeroTs))
        #设置当月时间
        curMonthTime = datetime(now.year,now.month,1,0,0,0)
        monthInDay = int(now.day)
        #如果没有传signTime默认使用当天的
        if not signTime:
            signTime = todayZeroTs
    
        #判断signTime时间戳是否合法,sign时间戳表示的年月和当前年月不相符，则表示非法
        if signDateDict.year != now.year or signDateDict.month != now.month or todayZeroTs - signTime >3600*24*monthInDay or signTime > todayZeroTs:
            return {'error':1,'data':'不能补签过期日期或未达到日期'}
        
        #初始化是否是补签
        isPatch = 0                      
        #如果签名的时间戳小于当天的，则认为是补签
        if signTime < todayZeroTs:
            isPatch = 1
        
        #print('#########')
        #print(signTime)
        #print(todayZeroTs)
        #print(monthInDay)
        #print(isPatch)
        #print(curMonthTime)
        
        #获得用户信息并转换为list
        userDict = UsersModel.VIP_User.query.filter_by(UserId=uid).first()
        userDict = UsersModel.VIP_User.parseToList([userDict])[0]
        #获得用户签名的日志并转换为list
        signArray = LogscoreModel.Log_Score.query.filter_by(Way='day',UserId=uid).filter(LogscoreModel.Log_Score.Writetime >= curMonthTime).order_by(desc(LogscoreModel.Log_Score.ScoreCode1)).all()
        signArray = LogscoreModel.Log_Score.parseToList(signArray)
        
        #print('******')
        #print(userDict)
        #print(signArray)
        
        
        vipLevel = int(userDict['CurrentLevel'])
        #已经补签次数为0
        hasPathCount = 0
        continueSign = 1
        #设置本次签到获得积分      
        dayScore = 0
        hasBreak = false #已经断了,没连续
        signLen = len(signArray)
        
        #判断补签不是已经超过次数了
        for item in signArray:
            if item['ScoreCode3'] != '0':
                    hasPathCount += 1                     
        if isPatch == 1 and hasPathCount>=0 and hasPathCount >= vipPatchTimes[vipLevel]:
                return {'error':1,'data':'补签次数不足,升级vip可增加补签次数'}     
        
        if signLen > 0: #以下全是本月第二次签到需要的判断
            #判断今天是否已经签过到
            hasSign = false
            for item in signArray:
                signArray[0]['ScoreCode1'] = int(signArray[0]['ScoreCode1'])
                if int(item['ScoreCode1']) == signTime: 
                    hasSign = true
                if item['ScoreCode3'] != '0':
                        hasPathCount += 1
   
            #判断当天是否已经签过到了
            if hasSign == true:
                return {'error':1,'data':'已经签到过了'}

            #如果不是补签
            #补签将不记录连续获得积分
            if isPatch == 0:
                #判断当前日期和最后一条日期是否在48小时内，如果在则表示连续补签
                if signTime - signArray[0]['ScoreCode1'] <=3600*24*2:
                    continueSign += 1
                else:
                    hasBreak = true
                    
                #判断是否已经连续签到
                #循环sign数组           
                for i in range(0,signLen):
                    item = signArray[i]
                    if i != signLen-1 and not hasBreak:
                        citemTs = item['ScoreCode1']
                        nitemTs = int(signArray[i+1]['ScoreCode1'])
                        if citemTs - nitemTs > 0 and citemTs - nitemTs <= 3600*24:
                            continueSign+=1
                        else:
                            hasBreak = true
                
                #开始进行连续签到的处理,必须不是补签
                if continueSign>=2 and continueSign<5:
                    dayScore += 5
                elif continueSign>=5 and continueSign<10:
                    dayScore += 15
                elif continueSign>=10 and continueSign<17:
                    dayScore += 30
                elif continueSign>=17 and continueSign<26:
                    dayScore += 50    
                elif continueSign>=26:
                    dayScore += 100
            
        
        #如果vip等级大于3，本次签到就将获得5分
        if vipLevel>=3:
            dayScore += 5
        
        #print(dayScore)
        #print(hasBreak)
        
        
        #去coreservice处理积分         
        reqResult = self.sendRequest('POST',scoreLogUrl,{
                    'UserId':uid,
                    'Type':'up',
                    'Score':dayScore,
                    'Way':'day',
                    'Code1':signTime,
                    'Code2':continueSign,
                    'Code3':isPatch
                    })   
        
        return reqResult  
    
    
#定义检查签名是否合法
class CheckSign(object):

    def __init__(self,time,uid,oldsign):
        self.time = time
        self.uid = uid
        self.key = app.config['PASSPORT_KEY']
        self.oldsign = oldsign

    def __createSign(self):
        md5Str = '{0}&{1}&{2}'.format(self.time, self.uid, self.key)
        #md5两次
        md5Str = hashlib.md5(md5Str).hexdigest().lower()
        md5Str = hashlib.md5(md5Str).hexdigest().lower()
        return md5Str
      
    def __checkTime(self):
        now = time.time()
        gap = now - self.time
        
        #如果当前时间和时间戳相差在1天以上，则认为不合法
        if gap < 0 or gap > 24*3600 :
            return false
        return true
    
    def __checkParam(self):
        #如果其中参数有一个不存在，则返回错误
        if not self.time or not self.uid or not self.key or not self.oldsign :
            return false
        return true
        
    def check(self):

        if not self.__checkParam():
            return false
        
        if not self.__checkTime():
            return false
        
        md5Str = self.__createSign()
        #检查新生成的签名是否合法
        if md5Str != oldsign:
            return false
        
        return true


#检查是否登录
def checkLogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.has_key('userid') or flask.session['userid'] == 0:
            return redirect('/login', code=302)
        flask.session['username'] = urllib.unquote(flask.session['username'].encode('utf8')).decode('utf8')
        return f(*args, **kwargs)
    return decorated_function

def getUserStatus(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        uid = flask.session.get('userid') or 0
        uname = flask.session.get('username') or '0'
        if uid != 0:
            userbl = UsersBl(uid)
            #执行操作
            r = userbl.getUserVipStatus()        
            #如果出错，记录日志
            if r['error'] == 1:
                LoggerBl.log.error(r['data'])
        else:
            r = {
                'data':''
            }
            
        paramDict = {
            'uid':uid,
            'uname':uname,
            'user':r
        }
        return f(paramDict, *args, **kwargs)
    return decorated_function



#检查是否登录，json返回版本
def checkLoginJson(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.has_key('userid') or flask.session['userid'] == 0:
            return json.dumps({'error':1,data:'请先登录'},mimetype='application/json')
        flask.session['username'] = urllib.unquote(flask.session['username'].encode('utf8')).decode('utf8')
        return f(*args, **kwargs)
    return decorated_function

