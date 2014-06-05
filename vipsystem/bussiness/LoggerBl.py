# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from vipsystem import app


#设置logger模块
log = logging.getLogger('mylogger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler( os.path.join('vipsystem','logs','vipsystem.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
log.info('log start in {0}'.format(app.config['ENV']))