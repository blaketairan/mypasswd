import os
import logging
os.path.split(os.path.realpath(__file__))[0]


class config(object):
    def __init__(self):
        self.projectDir = os.path.split(os.path.realpath(__file__))[0]
        self.dataLocation = self.projectDir + '/SECRET'
        self.AES_SECRET_KEY = b'1234567812345678aaaaaaaaaaaaaaaa'
        self.iv = 'aaaaaaaaaaaaaaaa'
        self.keyKeepTime = 10
        self.remoteRepo = 'github'
        self.remoteBranch = 'master'
        self.LOG_FORMAT = '%(asctime)s %(levelname)s [%(pathname)s-127.0.0.1:8081-%(process)d-%(thread)d] %(module)s.%(funcName)s %(message)s'
        self.chromeLog = self.projectDir + "/logs/mypasswdChrome.log"
        self.logLevel = logging.DEBUG


local_config = config()
