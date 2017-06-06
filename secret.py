#!/usr/local/bin/python3
import os
import sys
import getpass
from config import local_config
from time import sleep
from Crypto.Hash import MD5
import random


class secretKey(object):
    def __init__(self, account, passwd=''):
        self.account = account
        self.passwd = passwd
        self.secretKeyLocation = local_config.dataLocation + '/.' + self.account
        self.keep = local_config.keyKeepTime

    def acquireKey(self):
        try:
            if not os.path.exists(self.secretKeyLocation):
                if self.passwd == '':
                    self.passwd = getpass.getpass('password: ')
                createKey = MD5.new()
                createKey.update(self.passwd.encode())
                self.key_32 = createKey.hexdigest()
                with open(self.secretKeyLocation, 'w') as writeKey:
                    writeKey.writelines(self.key_32)
                return self.key_32
            else:
                with open(self.secretKeyLocation, 'r') as readKey:
                    return readKey.readline()
        except Exception as e:
            print('Failed to acquireKey')
            print(e)
            sys.exit(1)

    def randomSubstr(self, fullStr):
        subLength = random.randint(16, 32)
        subStartPoint = random.randint(0, 32)
        length = len(fullStr)
        substr = fullStr[subStartPoint : length \
            if subStartPoint + subLength > length \
            else subStartPoint + subLength ] + \
            fullStr[0 : 0 if length - subLength > subStartPoint \
            else subStartPoint + subLength - length]
        return substr

    def checkSubstr(self, fullStr, substr):
        judgeStr = fullStr * 3
        if substr in judgeStr:
            return True
        else:
            return False

    def timer(self):
        try:
            sleep(self.keep)
            if self.secretKeyLocation:
                os.remove(self.secretKeyLocation)
        except Exception as e:
            print('Failed to remove secretKey with timer, you may try it self')
            print('Location: %s' % self.secretKeyLocation)
            print(e)
            sys.exit(1)

    def deleteKey(self):
        try:
            os.remove(self.secretKeyLocation)
        except Exception as e:
            print('Failed to delete secretKey, you may try it self')
            print('Location: %s' % self.secretKeyLocation)
            print(e)

# class manageGit(object):
#     def __init__(self, projectDir):
#         self.projectDir = projectDir
#         self.repo = Repo(self.projectDir)
#         print(dir(self.repo))
#         print(self.repo.heads.master.commit.tree)
#         print(dir(self.repo.remotes))
#         getUrlCmd = "self.remote = self.repo.remotes.%s" % self.repo.remotes[0]
#         exec(getUrlCmd)
#         print(dir(self.remote))

#     def changeIgnore(self):
#         pass

#     def addNCommit(self):
#         self.repo.index.add('.')


if __name__ == '__main__':
    _secretKey = secretKey(sys.argv[1])
    sleep(_secretKey.keep * 1000)
    _secretKey.deleteKey()
