# -*- coding: utf-8 -*-
import hashlib
import time
import httplib
import json
import calendar
from datetime import *

from vipsystem import config
from vipsystem.models import UsersModel
from sqlalchemy import *

#vip对应等级可以补签的次数
vipPatchTimes = (1,2,3,5,8,10)




    
#定义用户业务层
class UsersBl(object):

    def __init__(self,uid):
        self.uid = uid
    
    #初始化用户
    def initUser(self):
        userDict = UsersModel.VIP_User.query.filter_by(UserId=self.uid).first()
        if userDict.Id :
            pass
        
        #如果没有记录,将用户信息插入数据库
        me = VIP_User(self.uid)
        db.session.add(me)
        db.session.commit()
        pass
    
    def sendRequest(self,method,url,paramDict,host=app.config['CORESERVICE_HOST']):
        #请求coreservice接口，获取用户vip信息
        headers = {}
        paramDictStr = urllib.urlencode(paramDict)
        if method == 'POST':
            headers = {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": "text/plain"}
            conn = httplib.HTTPConnection(host)    
            conn.request(method, url, paramDictStr, headers)
        else:    
            headers = {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": "text/plain"}
            conn = httplib.HTTPConnection(app.config['CORESERVICE_HOST'])    
            conn.request(method, url+'?'+paramDictStr)
            
        res = conn.getresponse()
        if res.status != 200 :
            return {'error':1,'data':'coreservice服务异常'}
        data = res.read()  #读取响应
        conn.close()       #关闭连接
        
        #将data转换成dict
        dataDict = {}
        try:
            dataDict = json.loads(data)
        except Exception as err:
             return {'error':1,'data':err}
        
        #如果接口处理失败
        if not dataDict.has_key('ret'):
            return 
        
        if dataDict['ret'] == false:
            return {'error':1,'data':dataDict.errMsg}
        #接口处理成功
        return {'error':0,'data':dataDict}
        
    
    #public获取用户vip状态
    def getUserVipStatus(self):
        #请求coreservice接口，获取用户vip信息
        dataDict = self.sendRequest('GET','/vip/getsalary',{'userid':self.uid})       
        return dataDict
        
    #public用户领取工资
    def getSalary(self):
        dataDict = self.sendRequest('GET','/vip/getsalary',{'userid':self.uid})       
        return dataDict
    
    #public获取当月的签到状态列表
    def getCurMonthSign(self):
        now = datetime.datetime.now()
        curMonthTime = time.struct_time(tm_year=now.year, tm_mon=now.month, tm_mday=1, tm_hour=00, tm_min=00, tm_sec=00)
        #获取当月的签到状态列表
        signArray = UsersModel.Log_Score.query.filter_by(Way='day',UserId=self.uid).filter(UsersModel.Log_Score.Writetime >= curMonthTime).order_by(desc(UsersModel.ScoreCode1)).all()       
        
        return {'error':0, data:signArray}
    
    
    def daySign(self,signTime):
        #积分获取和消费的url
        scoreLogUrl = '/score/log'
        
        uid = self.uid
        #转换signTime类型
        signDateDict = datetime.datetime.fromtimestamp(signTime)
        signDateTime = time.struct_time(tm_year=signDateDict.year, tm_mon=signDateDict.month, tm_mday=signDateDict.day, tm_hour=00, tm_min=00, tm_sec=00)
        signTime = int(signDateTime.time())
                    
        #设置当天时间
        now = datetime.datetime.now()
        todayZeroTime = time.struct_time(tm_year=now.year, tm_mon=now.month, tm_mday=now.day, tm_hour=00, tm_min=00, tm_sec=00)
        todayZeroTs = int(todayZeroTime.time())
        #设置当月时间
        curMonthTime = time.struct_time(tm_year=now.year, tm_mon=now.month, tm_mday=1, tm_hour=00, tm_min=00, tm_sec=00)
        monthInDay = int(now.day)
        #如果没有传signTime默认使用当天的
        if not signTime:
            signTime = todayZeroTs
    
        #判断signTime时间戳是否合法,sign时间戳表示的年月和当前年月不相符，则表示非法
        if signDateDict.year != now.year or signDateDict.month != now.month or todayZeroTs - signTime >3600*24*monthInDay:
            return {'error':1,data:'不能补签上个月的'}
        
        #初始化是否是补签
        isPatch = false                      
        #如果签名的时间戳小于当天的，则认为是补签
        if signTime < todayZeroTs:
            isPatch = true
            
        #获得用户信息
        userDict = UsersModel.VIP_User.query.filter_by(UserId='uid').first()
        #获得用户签名的日志
        signArray = UsersModel.Log_Score.query.filter_by(Way='day',UserId=uid).filter(UsersModel.Log_Score.Writetime >= curMonthTime).order_by(desc(UsersModel.ScoreCode1)).all()
                
        vipLevel = int(userDict.CurrentLevel)
        #已经补签次数为0
        hasPathCount = 0
        continueSign = 0
        #设置本次签到获得积分      
        dayScore = 0
        hasBreak = false #已经断了,没连续
        signLen = len(signArray)
        
        if signLen > 0: #以下全是本月第二次签到需要的判断
            #判断今天是否已经签过到
            hasSign = false
            for item in signArray:
                if int(item.ScoreCode1) == signTime: 
                    hasSign = true
                if item.ScoreCode3:
                        hasPathCount += 1

            #判断是不是超过最大补签次数
            if isPatch and hasPathCount>0 and hasPathCount >= vipPatchTimes[vipLevel]:
                return {'error':1,data:'补签次数过多'}                
            #判断当天是否已经签过到了
            if hasSign:
                return {'error':1,'data':'已经签到过了'}
            
            #如果不是补签
            #补签将不记录连续获得积分
            if not isPatch:
                #判断当前日期和最后一条日期是否在48小时内，如果在则表示连续补签
                if signTime - signArray[0].ScoreCode1 <=3600*24*2:
                    continueSign += 1
                else:
                    hasBreak = true
                    
                #判断是否已经连续签到
                #循环sign数组           
                for i in range(0,signLen):
                    item = signArray[i]
                    if i != signLen-1 and not hasBreak:
                        citemTs = int(item.ScoreCode1)
                        nitemTs = int(signArray[i+1].ScoreCode1)
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
        
        #去coreservice处理积分         
        reqResult = self.sendRequest('POST',scoreLogUrl,{
                    'UserId':uid,
                    'Type':'up',
                    'Score':dayScore,
                    'Way':'day',
                    'ScoreCode1':signTime,
                    'ScoreCode2':continueSign,
                    'ScoreCode3':isPatch
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
    

