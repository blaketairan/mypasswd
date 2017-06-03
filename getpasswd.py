import sys
import os
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from binascii import b2a_hex, a2b_hex
from config import local_config
import threading
from time import sleep
import getpass


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
            print(e)
        self.secret = local_config.dataLocation + '/' + self.account

    def add(self, text):
        try:
            if not os.path.exists(self.secret):
                with open(self.secret, 'w') as secret:
                    secret.writelines(text + '\n')
            else:
                with open(self.secret, 'a') as secret:
                    secret.writelines(text + '\n')
        except Exception as e:
                print(e)

    def delete(self, text):
        try:
            if not os.path.exists(self.secret):
                raise Exception('The record of %s is empty!' % self.account)
            else:
                with open(self.secret, 'rt') as readfile:
                    data = readfile.readlines()
                    print(data)
                    with open(self.secret, 'wt') as writefile:
                        for line in data:
                            if text != line[:-1]:
                                writefile.writelines(line)
        except Exception as e:
            print(e)

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
            print(e)

    def fileExists(self, text):
        try:
            if not os.path.exists(self.secret):
                with open(self.secret, 'w') as secret:
                    secret.writelines(text + '\n')
        except Exception as e:
            os.remove(self.secret)
            print(e)


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
            print(e)

    def timer(self):
        try:
            sleep(self.keep)
            if self.secretKeyLocation:
                os.remove(self.secretKeyLocation)
        except Exception as e:
            print(e)


class manageCipher(object):
    def __init__(self, account, passwd=''):
        self.account = account
        self.passwd = passwd
        getKey = secretKey(self.account, self.passwd)
        self.key_32 = getKey.acquireKey()[:32]
        self.datafile = secretIO(self.account)
        self.secretDict = AES_ENCRYPT(self.key_32, self.key_32[:16])
        try:
            self.datafile.fileExists(self.secretDict.encrypt('Bingo').decode('ascii'))
            firstline = self.datafile.query()[0]
        except Exception as e:
            print(e)
            sys.exit(0)
        try:
            if firstline.encode() != self.secretDict.encrypt('Bingo'):
                print('Wrong password')
                sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(0)

    def printInfo(self):
        print(self.account)
        print(self.passwd)
        print(self.key_32)

    def queryRecord(self, qSystem):
        data = self.datafile.query()[1:]
        result = []
        for line in data:
            try:
                cleartext = self.secretDict.decrypt(line).rstrip('\x00')
                cleartext = cleartext.split('\x00')
                if qSystem == cleartext[0]:
                    temp = {}
                    temp['system'] = cleartext[0]
                    temp['account'] = cleartext[1]
                    temp['passwd'] = cleartext[2]
                    result.append(temp)
            except:
                continue
        return result

    def addRecord(self, system, sAccount, sPasswd):
        cleartext = system + '\x00' + sAccount + '\x00' + sPasswd
        ciphertext = self.secretDict.encrypt(cleartext)
        self.datafile.add(ciphertext.decode())

    def deleteRecord(self, system, sAccount):
        pass
