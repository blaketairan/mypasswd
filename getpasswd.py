#!/usr/local/bin/python3
"""myPasswd

usage:
  getpasswd.py --action=<action> --account=<account> --system=<system> [--sAccount=<sAccount>]
  getpasswd.py (-h | --help)
  getpasswd.py --version

options:
  -h --help        show this screen
  -v --version     Show version
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

    def fileExists(self, text):
        try:
            if not os.path.exists(self.secret):
                with open(self.secret, 'w') as secret:
                    secret.writelines(text + '\n')
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


class manageCipher(object):
    def __init__(self, account):
        self.account = account
        self.getKey = secretKey(self.account)
        self.key_32 = self.getKey.acquireKey()[:32]
        self.datafile = secretIO(self.account)
        self.secretDict = AES_ENCRYPT(self.key_32, self.key_32[:16])
        try:
            self.datafile.fileExists(self.secretDict.encrypt('Bingo').decode('ascii'))
            firstline = self.datafile.query()[0]
        except Exception as e:
            print('Failed to init manageCipher')
            print(e)
            sys.exit(0)
        try:
            if firstline.encode() != self.secretDict.encrypt('Bingo'):
                print('Wrong password')
                self.getKey.deleteKey()
                sys.exit(1)
        except Exception as e:
            print('Failed to init manageCipher')
            print(e)
            sys.exit(1)

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
                                temp = {}
                                temp['system'] = cleartext[0]
                                temp['account'] = cleartext[1]
                                temp['passwd'] = cleartext[2]
                                result.append(temp)
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
            return True
        except Exception as e:
            print('Failed to add record')
            print(e)
            sys.exit(1)


class myPasswd(object):
    def __init__(
            self,
            action,
            account,
            system='',
            sAccount=''):
        self.action = action
        self.account = account
        self.system = system
        self.sAccount = sAccount
        self.control = manageCipher(self.account)

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
        else:
            print('Wrong action!')
            sys.exit(1)


if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='myPasswd 0.0.1')
        _mypasswd = myPasswd(
            arguments['--action'],
            arguments['--account'],
            arguments['--system'],
            arguments['--sAccount'])
        result = _mypasswd.run()
        print(result)
    except Exception as e:
        print('Wrong in main')
        print(e)

