import os
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


local_config = config()
