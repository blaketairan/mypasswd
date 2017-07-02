#!/usr/bin/env python3

import struct
import sys
import json
from getpasswd import manageCipher
import traceback
import time
from config import local_config
from logging.handlers import TimedRotatingFileHandler
import logging

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


chromeLog = logging.getLogger(__name__)
logHandler = TimedRotatingFileHandler(
    filename=local_config.chromeLog,
    when='D',
    interval=1,
    backupCount=7)
logHandler.setFormatter(logging.Formatter(local_config.LOG_FORMAT))
chromeLog.addHandler(logHandler)
chromeLog.setLevel(local_config.logLevel)


class chromeConnection():
    def __init__(self):
        pass

    def sendMessage(self, message):
        # same in python2 and python3
        temp = struct.pack('i', len(message))
        sys.stdout.buffer.write(temp)
        sys.stdout.buffer.write(message.encode('utf-8'))
        sys.stdout.flush()

    def readMessage(self):
        # message_number = 0
        text_length_bytes = sys.stdin.buffer.read(4)
        # message_number += 1

        if len(text_length_bytes) == 0:
            sys.exit(0)

        text_length = struct.unpack('i', text_length_bytes)[0]

        text = sys.stdin.buffer.read(text_length).decode('utf-8')
        jsondata = json.loads(text)
        return jsondata


class chromeMypasswd():
    def __init__(
            self,
            account,
            password,
            register=False):
        self.account = account
        self.passwd = password
        self.state = 'login'
        self.result = ''
        try:
            self.control = manageCipher(self.account, self.passwd, register)
            if not self.control.success:
                self.success = False
                self.result = self.control.result
                self.state = 'login-failed'
            else:
                self.success = True
                self.state = 'logged'
        except Exception as e:
            chromeLog.debug('Login failed with unknown error')
            chromeLog.debug(e)
            info = traceback.format_exc()
            chromeLog.warning(info)
            self.success = False
            self.result = 'Login failed with unknown error'
            self.state = 'login-failed'

    def printSelf(self):
        try:
            for item in self.__dict__.items():
                chromeLog.debug(item)
        except Exception as e:
            chromeLog.debug(e)
            info = traceback.format_exc()
            chromeLog.warning(info)

    def run(self, rMsg):
        self.success = False
        sysName = rMsg['sysName']
        sAccount = rMsg['sAccount']
        action = rMsg['action']
        chromeLog.info('Will do %s term!\n' % action)
        chromeLog.debug(str(rMsg))
        if action == 'query':
            try:
                result = self.control.queryRecord(sysName, sAccount)
                chromeLog.debug(result)
                if isinstance(result, str):
                    self.success = True
                    self.state = 'specified-search-success'
                    self.result = result
                elif isinstance(result, list):
                    self.success = True
                    self.state = 'list-search-success'
                    self.result = result
                else:
                    self.success = False
                    self.state = 'search-failed'
                    self.result = 'Search failed with uncatched error'
            except Exception as e:
                    chromeLog.warning(str(e))
                    info = traceback.format_exc()
                    chromeLog.warning(info)
                    self.success = False
                    self.state = 'search-failed'
                    self.result = info


# main function
def login(rMsg):
    try:
        chromeLog.debug('Try login\n')
        chromeLog.debug(str(receivedMessage) + '\n')
        account = receivedMessage['account']
        password = receivedMessage['password']
        register = receivedMessage['register']
        if register == 'True':
            register = True
        elif register == 'False':
            register = False
        else:
            sys.exit(1)
        result = chromeMypasswd(account, password, register)
        return result
    except Exception as e:
        info = traceback.format_exc()
        chromeLog.debug(info)
        return None


if __name__ == '__main__':
    try:
        connection = chromeConnection()
        connection.sendMessage('"Yes. There is mypasswd"')
        while(connection):
            result = ''
            state = ''
            receivedMessage = connection.readMessage()
            chromeLog.debug(str(receivedMessage))
            if receivedMessage['action'] == 'login':
                chromeLog.debug('is login')
                mypasswd = login(receivedMessage)
            else:
                chromeLog.debug('is not login')
                if 'mypasswd' not in locals():
                    chromeLog.debug('did not define mypasswd')
                    state='login-failed'
                    result = 'not login'
                    break
                if receivedMessage['action'] == 'query':
                    chromeLog.debug('is query')
                    mypasswd.run(receivedMessage)
                else:
                    pass

            chromeLog.debug(str(mypasswd.success))
            if mypasswd.success:
                state = mypasswd.state
                result = mypasswd.result
            else:
                result = mypasswd.result
                state = mypasswd.state
                chromeLog.debug(result)
            chromeLog.debug(state)
            chromeLog.debug(result)
            connection.sendMessage(
                '{"info": "%s", "state": "%s"}' % (result, state))
    except Exception as e:
        info = traceback.format_exc()
        chromeLog.debug(info)










