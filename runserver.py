# -*- coding: utf-8 -*-
import os
import sys
import getopt
import flask
from vipsystem import app
from vipsystem import config


#获取配置参数并return {'error':1,'data':'不能补签过期日期'}
__opts, _ = getopt.getopt(sys.argv[1:], "e:") #获取命令行参数
__scritpEnv = ""

for name, value in __opts:
    if name == "-e": #获取命令行参数e
        __scritpEnv = value    
if __scritpEnv == "Production" :
    app.config.from_object(config.Production())
else:
    app.config.from_object(config.Debug())

#session支持
app.secret_key = app.config['SESSION_KEY']

def mkdir(path):
    # 引入模块
    
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print path+' create success'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+' is exist'
        return False


#计算路径，然后创建文件夹
curPath = os.path.split(os.path.realpath(__file__))[0]
logsPath = curPath + os.sep + 'vipsystem' + os.sep + 'logs'

mkdir(logsPath)


from vipsystem.controllers import *
from vipsystem.models import *




if __name__ == '__main__':
    app.run(host=app.config.get("HOST"),port=app.config.get("PORT"))
    
    
    
