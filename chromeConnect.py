#!/usr/bin/env python3

import struct
import sys
import json
from getpasswd import manageCipher
import traceback
import time
from config import local_config


if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def printfile(text):
    with open(local_config.projectDir + "/logs/mypasswdChrome.log","a") as fp:
        fp.write(text)
    return 0


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
        try:
            self.control = manageCipher(self.account, self.passwd, register)
            if not self.control.success:
                self.success = False
                self.failInfo = self.control.failInfo
            else:
                self.success = True
        except Exception as e:
            print('Login failed with unknown error')
            print(e)
            self.success = False
            self.failInfo = 'Login failed with unknown error'

    def run(self, action, system='', sAccount='', sPasswd=''):
        printfile('Will do %s term!\n' % action)
        if action == 'query':
            try:
                result = self.control.queryRecord(system, sAccount)
                print(result)
                if isinstance(result, str):
                    return 'str', result
                elif isinstance(result, list):
                    return 'list', result
                else:
                    return None
            except Exception as e:
                    printfile(str(e))
                    info = traceback.format_exc()
                    printfile(info)


# main function
def login(connection):
    try:
        printfile('"Yes. The py program is starting"\n')
        receivedMessage = connection.readMessage()
        printfile(str(receivedMessage) + '\n')
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
        printfile(info)
        return None


def waitMessage():
    pass


if __name__ == '__main__':
    try:
        connection = chromeConnection()
        connection.sendMessage('"Yes. There is mypasswd"')
        mypasswd = login(connection)
        if mypasswd:
            printfile(str(mypasswd.success))
            if mypasswd.success:
                connection.sendMessage('"Logged"')
                time.sleep(10)
                resultType, result = mypasswd.run()
            printfile(resultType)
            connection.sendMessage('{"info": "%s"}' % result)
    except Exception as e:
        info = traceback.format_exc()
        printfile(info)
