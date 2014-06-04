# -*- coding: utf-8 -*-
import sys,os
def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        pass
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    return path+os.sep+'logs'

    
class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'mysql://root:123456@192.168.150.3/6998_VIPCenter'
    SQLALCHEMY_POOL_SIZE = 5
    HOST = "0.0.0.0"
    PORT = 5000
    PASSPORT_KEY = "77aa269c7ca8ea05d9f10bd0efa57fe3"
    CORESERVICE_HOST = "coreservice.6998test.com"
    PASSPORT_SERVER = "passport.6998test.com"
    GAMEAPP_HOST = "gameapp.6998.com"
    
    
    CURRENT_HOST = "http://www.mypc.com:5000"
    LOG_PATH = cur_file_dir()
    LOGGER_NAME = 'mylog'
    SESSION_KEY = '05599c095f5900cc288bcadd9f9b4c34'
    
    
class Production(Config):
    DATABASE_URI = 'mysql://root:123456@192.168.150.3/6998_VIPCenter'
    SQLALCHEMY_POOL_SIZE = 20
    CORESERVICE_HOST = "http://coreservice.6998.com"
    PORT = 6000
    PASSPORT_SERVER = "passport.6998.com"
    CURRENT_HOST = "http://www.mypc.com:5000"


class Debug(Config):
    DEBUG = True
    