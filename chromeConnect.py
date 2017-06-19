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

    def send_message(self, message):
        # same in python2 and python3
        temp = struct.pack('i', len(message))
        sys.stdout.buffer.write(temp)
        sys.stdout.buffer.write(message.encode('utf-8'))
        sys.stdout.flush()

    def read_message(self):
        # message_number = 0
        text_length_bytes = sys.stdin.buffer.read(4)
        # message_number += 1

        if len(text_length_bytes) == 0:
            sys.exit(0)

        text_length = struct.unpack('i', text_length_bytes)[0]

        text = sys.stdin.buffer.read(text_length).decode('utf-8')
        jsondata = json.loads(text)
        username = jsondata['username']
        passwd = jsondata['passwd']
        system = jsondata['system']
        suser = jsondata['suser']
        return username, passwd, system, suser


class chromeMypasswd():
    def __init__(
            self,
            action,
            account,
            password,
            system,
            sAccount,
            sPasswd=''):
        self.action = action
        self.account = account
        self.passwd = password
        self.system = system
        self.sAccount = sAccount
        try:
            self.control = manageCipher(self.account, self.passwd)
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


    def run(self):
        printfile('Will %s terms for %s')
        if self.action == 'query':
            try:
                result = self.control.queryRecord(self.system, self.sAccount)
                if isinstance(result, str):
                    return result
            except Exception as e:
                    printfile(e)
                    info = traceback.format_exc()
                    printfile(info)


if __name__ == '__main__':
    try:
        connection = chromeConnection()
        time.sleep(10)
        connection.send_message('"Yes. There is mypasswd"')
        username, passwd, system, suser = connection.read_message()
        printfile(username + passwd + system + suser)
        mypasswd = chromeMypasswd('query',username, passwd, system, suser)
        if isinstance(mypasswd, str)
        result = mypasswd.run()
        printfile('\n' + result + '\n')
        connection.send_message('{"info": "%s"}' % result)
    except Exception as e:
        info = traceback.format_exc()
        printfile(info)
