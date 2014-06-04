# -*- coding: utf-8 -*-
import hashlib
import time
import httplib
import json
import calendar
from datetime import *

from vipsystem import config
from vipsystem.bussiness import UsersBl
from vipsystem.models import UsersModel
from vipsystem.models import GoodsModel
from sqlalchemy import *


#vip对应等级可以补签的次数
vipPatchTimes = (1,2,3,5,8,10)

   
#定义检查签名是否合法
class GoodsBl(object):

    def __init__(self,uid,uname,ip='127.0.0.1'):
        self.uid = uid
        self.uname = uname
        self.userIp = ip
    
    def sendRequest(self,method,url,paramDict):
        userbl = UsersBl(uid)
        return userbl.sendRequest(method,url,paramDict)
         
    #获取所有虚拟商品，limit最多100个
    def getGoods(self):
        #请求coreservice接口，获取用户vip信息
        goodsArray = GoodsModel.query.filter_by(IsShow=1).limit(100).all()
        return {error:0,data:goodsArray}
        
    #获取指定商品的详细信息
    def getGoodsDetail(self,ename):
        goodsDict = GoodsModel.query.filter_by(IsShow=1, EName=ename).first()
        return {error:0,data:goodsDict}
    
    def exchangeGoods(self,ename):
        #积分获取和消费的url
        scoreLogUrl = '/score/log'
        uid = self.uid
        #获取goods字典
        goodsDict = GoodsModel.query.filter_by(IsShow=1, EName=ename).first()
        #获得用户信息
        userDict = UsersModel.VIP_User.query.filter_by(UserId='uid').first()
        
        #当前用户积分 = 今年积分 + 去年积分
        userScore = userDict.Score + userDict.HistoryScore
        #此商品是否下架
        if not goodsDict.Id:
            return {'error':1,data:'未找到商品,或商品已下架'}
        #判断积分是否够兑换
        if goodsDict.Price > userScore:
            return {'error':1,data:'对不起您的积分不够'}
        #判断是否有库存
        if goodsDict.Inventory < 1:
            return {'error':1,data:'对不起没有库存了'}
        
        logScoreDict = {
            'UserId':uid,
            'Type':'down',
            'Score':goodsDict.Price,
            'Way':'exchange',
            'ScoreCode1':goodsDict.type,
            'ScoreCode2':goodsDict.Id,
            'ScoreCode3':'',
            'ScoreCode4':'',
        }
        
        if goodsDict.Type == 'tryMember':
            #去获取唐人游会员
            r = self.sendRequest('POST','/member/UseMember',{
                    'UserID':uid,
                    'VIPType':goodsDict.type,
                    'VIPDays':30,
                    })
            if r['result'] != 0 :
                return {'error':1,data:'发货唐人游会员失败,错误代码:'+r['result']}

        elif goodsDict.Type == 'tryGift':
            #去获取唐人游会员
            r = self.sendRequest('POST','/money/UpdateCash',{
                    'UserID':uid,
                    'WantedAmount':goodsDict.code2,
                    'ModeName':'积分兑换',
                    'SourceName':'6998vip',
                    'Remark':'exchange',
                    'Tax':0,
                    'IPAddress':self.userIp,
                    'MachineNumber':'',
                    })
            if r['result'] != 0 :
                return {'error':1,data:'发货银子失败,错误代码:'+r['result']}
            #保存发货量
            logScoreDict['ScoreCode3'] = goodsDict.code2
            
        elif goodsDict.Type == 'tryCoin':
           
            r = self.sendRequest('POST','/bean/UpdateCash',{
                    'UserID':uid,
                    'WantedAmount':goodsDict.code2,
                    'ModeName':'积分兑换',
                    'SourceName':'6998vip',
                    'Remark':'exchange',
                    'Tax':0,
                    'IPAddress':self.userIp,
                    'MachineNumber':'',
                    })
            if r['result'] != 0 :
                return {'error':1,data:'发货游戏币失败,错误代码:'+r['result']}
            
            logScoreDict['ScoreCode3'] = goodsDict.code1
            
        elif goodsDict.Type == '6998Vip':
            logScoreDict['ScoreCode3'] = goodsDict.code1
            logScoreDict['ScoreCode4'] = int(time.time()) + 3600*24*3
            
        elif goodsDict.Type == 'gameCard':
            #去获取新手卡
            r = self.sendRequest('GET','/GameGift/Index',{
                    GroupId:goodsDict.code1,
                    UserName:self.uname,
                },app.config['GAMEAPP_HOST'])
            if r['Result'] != true:
                return {'error':1,data:'发货游戏币失败,错误代码:'+r['Message']}
            
            logScoreDict['ScoreCode3'] = r['Message']
        else:
            return {'error':1, 'data':'未知商品类型:'+goodsDict.Type}
             
        #去coreservice处理积分,记录扣除用户积分
        reqResult = self.sendRequest('POST',scoreLogUrl,logScoreDict)
        
        #发货成功,写入数据库
        dbResult = db.session.query(GoodsModel).filter_by(Id = goodsDict.Id).update({'Inventory': goodsDict.Inventory-1 }, synchronize_session=False)
        
        if dbResult != 1:
            return {'error':1, data:'更新库存失败'}
        
        return {'error':0, data:''}
    


