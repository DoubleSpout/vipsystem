# -*- coding: utf-8 -*-
#coding=utf-8
from datetime import datetime
import os
import sys
import subprocess
f = open("deploy.log", 'a')
f.write('\n')
f.write('redeploying at {0} --username svnsync_s --password D518F02BE90EACF5BB15976E13711CA8'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
f.write('\n')
f.flush() 
try:
    runFolder = sys.path[0] + os.sep + 'redeploy.py'
    
    output = subprocess.popen('/etc/init.d/uwsgi stop',stdout=f, stderr=f, shell=True)
    #f.write(output.read())
    
    output = subprocess.popen('svn update {0}'.format(runFolder),stdout=f, stderr=f, shell=True)
    #f.write(output.read())
    #print output.read()
    
    output = subprocess.popen('/etc/init.d/uwsgi start',stdout=f, stderr=f, shell=True)
    #f.write(output.read())
    
except:
    pass
finally:
     f.flush() 
     f.close( )
