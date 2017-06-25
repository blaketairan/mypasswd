#!/usr/local/bin/python3
"""myPasswd

usage:
  getpasswd.py --action=<action> --account=<account> --system=<system> [--sAccount=<sAccount>]
  getpasswd.py -r --account=<account>
  getpasswd.py (-h | --help)
  getpasswd.py --version

options:
  -h --help        show this screen
  -v --version     Show version
  -r --register    Register account.
  --action=<action>         Only in query,add or delete(required)
  --account=<account>       Your mypasswd account(required)
  --system=<system>         Which term do you want to deal(required)
  --sAccount<sAccount>      Only required when you are adding(optional)

"""
import sys
import os
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from config import local_config
import getpass
from docopt import docopt
from secret import secretKey
import subprocess
from threading import Timer
import signal
import pyperclip
import traceback


def execSystemCommand(cmd, timeout=10):
    """ run cmd return output and status"""
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
    killProc = lambda pid: os.killpg(pid, signal.SIGKILL)
    timer = Timer(timeout, killProc, [popen.pid])
    timer.start()
    popen.wait()
    output = popen.stdout.read()
    timer.cancel()
    return popen.returncode, output


# control git
class manageGit(object):
    def __init__(self):
        self.projectDir = local_config.projectDir
        self.remoteRepo = local_config.remoteRepo
        self.remoteBranch = local_config.remoteBranch

    def changeIgnore(self):
        pass

    # add & commit
    def addNCommit(self):
        os.chdir(self.projectDir)
        returnCode, result = execSystemCommand('git add .')
        if returnCode != 0:
            print('Failed to exec: git add')
            os.system('git reset .')
            sys.exit(1)
        returnCode, result = execSystemCommand('git commit -m "update secret data"')
        if returnCode != 0:
            print('Failed to exec: git commit')
            os.system('git reset .')
            sys.exit(1)
        returnCode, result = execSystemCommand('git push %s %s' % (self.remoteRepo, self.remoteBranch))
        if returnCode != 0:
            print('Failed to exec: git push')
            sys.exit(1)


# encrypt and decrypt
class AES_ENCRYPT(object):
    def __init__(self, key, iv):
        self.key = key
        self.mode = AES.MODE_CBC
        self.iv = iv

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt(a2b_hex(text))
        plain_text = plain_text.decode('utf-8')
        result = plain_text
        return result


# the secret data i/o
class secretIO(object):
    def __init__(self, account):
        self.account = account
        try:
            if not os.path.isdir(local_config.dataLocation):
                os.mkdir(local_config.dataLocation)
        except Exception as e:
            print('Failed to check data path in secretIO')
            print(e)
            sys.exit(1)
        self.secret = local_config.dataLocation + '/' + self.account

    def add(self, text):
        try:
            if not os.path.exists(self.secret):
                with open(self.secret, 'w') as secret:
                    secret.writelines(text + '\n')
            else:
                with open(self.secret, 'a') as secret:
                    secret.writelines(text + '\n')
            return text
        except Exception as e:
            print('Failed to add in secretIO')
            print(e)
            sys.exit(1)

    def delete(self, text):
        try:
            if not os.path.exists(self.secret):
                raise Exception('The record of %s is empty!' % self.account)
            else:
                with open(self.secret, 'rt') as readfile:
                    data = readfile.readlines()
                    with open(self.secret, 'wt') as writefile:
                        for line in data:
                            if text != line[:-1]:
                                writefile.writelines(line)
        except Exception as e:
            print('Failed to delete in secretIO')
            print(e)
            sys.exit(1)

    def query(self):
        try:
            if not os.path.exists(self.secret):
                return None
            else:
                with open(self.secret, 'rt') as readfile:
                    data = readfile.readlines()
                    for num in range(0, len(data)):
                        data[num] = data[num][:-1]
                    return data
        except Exception as e:
            print('Failed to query in secretIO')
            print(e)
            sys.exit(1)

    def fileExists(self, text, register):
        try:
            if register:
                if not os.path.exists(self.secret):
                    with open(self.secret, 'w') as secret:
                        secret.writelines(text + '\n')
                    return False
                else:
                    return 'Account already exists'
            else:
                if os.path.exists(self.secret):
                    return False
                else:
                    return 'Account not exists'
        except Exception as e:
            print('Failed confirm fileExists in secretIO. Maybe try to remove %s ' % self.secret)
            print(e)
            sys.exit(1)

    def deleteFile(self):
        try:
            os.remove(self.secret)
        except Exception as e:
            print('Failed to remove %s' % self.secret)
            print(e)


# manage cipher
class manageCipher(object):
    def __init__(self, account, password='', register=False):
        self.account = account
        self.getKey = secretKey(self.account, password)
        self.key_32 = self.getKey.acquireKey()[:32]
        self.datafile = secretIO(self.account)
        self.secretDict = AES_ENCRYPT(self.key_32, self.key_32[:16])
        self.projectGit = manageGit()
        try:
            checkAccount = self.datafile.fileExists(
                self.secretDict.encrypt(
                    self.getKey.randomSubstr(self.key_32)).decode('ascii'),
                register)
            if not checkAccount:
                firstline = self.datafile.query()[0]
                self.success = True
            else:
                self.success = False
                self.failInfo = checkAccount
                return None
        except Exception as e:
            traceback.print_exc()
            self.success = False
            self.failInfo = 'Failed to init manageCipher while check fileExists'
            return None
        try:
            if self.getKey.checkSubstr(
                    self.secretDict.decrypt(firstline.encode()), self.key_32):
                print('Wrong password')
                self.success = False
                self.failInfo = 'Wrong password'
                self.getKey.deleteKey()
                return None
            else:
                self.success = True
        except UnicodeDecodeError:
            self.success = False
            self.failInfo = 'Wrong password'
            self.getKey.deleteKey()
            return None
        except Exception as e:
            traceback.print_exc()
            self.success = False
            self.failInfo = 'Failed to init manageCipher while decode secret'
            return None

    def printInfo(self):
        print(self.account)
        print(self.key_32)

    def queryRecord(self, system, sAccount=''):
        data = self.datafile.query()[1:]
        result = []
        try:
            for line in data:
                try:
                    cleartext = self.secretDict.decrypt(line).rstrip('\x00')
                    cleartext = cleartext.split('\x00')
                    if system == cleartext[0]:
                        if sAccount == '':
                            temp = {}
                            temp['system'] = cleartext[0]
                            temp['account'] = cleartext[1]
                            temp['passwd'] = cleartext[2]
                            result.append(temp)
                        else:
                            if sAccount == cleartext[1]:
                                result = cleartext[2]
                except:
                    continue
            return result
        except Exception as e:
            print(e)
            print('Failed to query record')
            sys.exit(1)

    def addRecord(self, system, sAccount, sPasswd):
        cleartext = system + '\x00' + sAccount + '\x00' + sPasswd
        ciphertext = self.secretDict.encrypt(cleartext)
        try:
            result = self.datafile.add(ciphertext.decode())
            self.projectGit.addNCommit()
            return result
        except Exception as e:
            print('Failed to add record')
            print(e)
            sys.exit(1)

    def deleteRecord(self, system, sAccount):
        data = self.datafile.query()[1:]
        try:
            for line in data:
                try:
                    cleartext = self.secretDict.decrypt(line).rstrip('\x00')
                    cleartext = cleartext.split('\x00')
                    if system == cleartext[0] and sAccount == cleartext[1]:
                        self.datafile.delete(line)
                except:
                    continue
            self.projectGit.addNCommit()
            return True
        except Exception as e:
            print('Failed to add record')
            print(e)
            sys.exit(1)


class myPasswd(object):
    def __init__(
            self,
            account,
            action='',
            system='',
            sAccount='',
            register=False):
        self.action = action
        self.account = account
        self.system = system
        self.sAccount = sAccount
        if register:
            self.action = 'register'
            self.control = manageCipher(self.account, register=register)
            if not self.control.success:
                self.success = False
                self.failInfo = self.control.failInfo
                return None
            else:
                self.success = True
        else:
            self.control = manageCipher(self.account, register=False)
            if not self.control.success:
                self.success = False
                self.failInfo = self.control.failInfo
                return None
            else:
                self.success = True

    def actionAdd(self):
        pass

    def actionDelete(self):
        pass

    def actionQuery(self):
        pass

    def run(self):
        if self.action == 'query':
            print('Will %s terms for %s.' % (self.action, self.account))
            # print('Record: system: %s; sAccount: %s' % (
            #     self.system,
            #     self.sAccount))
            try:
                if not self.sAccount:
                    self.sAccount = ''
                result = self.control.queryRecord(self.system, self.sAccount)
                if isinstance(result, str):
                    result = pyperclip.copy(result)
                    return 'Copied'
                else:
                    return result
            except Exception as e:
                print('Failed to run your command')
                print(e)
                sys.exit(1)
        elif self.action == 'add':
            print('Will %s terms for %s.' % (self.action, self.account))
            self.sPasswd = getpass.getpass('%s password: ' % self.sAccount)
            # print('Record: system: %s; sAccount: %s; sPasswd: %s' % (
            #     self.system,
            #     self.sAccount,
            #     self.sPasswd))
            try:
                result = self.control.addRecord(
                    self.system,
                    self.sAccount,
                    self.sPasswd)
                return result
            except Exception as e:
                print('Failed to run your command')
                print(e)
                return None
        elif self.action == 'delete':
            print('Will %s terms for %s.' % (self.action, self.account))
            # print('Record: system: %s; sAccount: %s' % (
            #     self.system,
            #     self.sAccount))
            try:
                result = self.control.deleteRecord(
                    self.system,
                    self.sAccount)
                return result
            except Exception as e:
                print('Failed to run your command')
                print(e)
                sys.exit(1)
        elif self.action == 'register':
            return 'register success'
        else:
            print('Wrong action!')
            sys.exit(1)


if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='myPasswd 0.0.1')
        print(arguments)
        _mypasswd = myPasswd(
            arguments['--account'],
            arguments['--action'],
            arguments['--system'],
            arguments['--sAccount'],
            arguments['--register'])
        if _mypasswd.success:
            result = _mypasswd.run()
            print(result)
            sys.exit(0)
        else:
            print(_mypasswd.failInfo)
            sys.exit(1)
    except Exception as e:
        print('Wrong in main')
        print(e)

