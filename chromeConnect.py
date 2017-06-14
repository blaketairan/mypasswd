#!/usr/bin/env python
import struct
import sys
import json


if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def printfile(text):
    with open("/Users/chentairan/temp/mypasswdChrome.log","a") as fp:
        fp.write(text + '\n')
    return 0


def send_message(message):
    sys.stdout.write(struct.pack('I', len(message)))
    sys.stdout.write(message)
    sys.stdout.flush()


def read_message():
    # message_number = 0
    text_length_bytes = sys.stdin.read(4)
    # message_number += 1

    if len(text_length_bytes) == 0:
        sys.exit(0)

    text_length = struct.unpack('i', text_length_bytes)[0]

    text = sys.stdin.read(text_length).decode('utf-8')
    jsondata = json.loads(text)
    username = jsondata['username']
    passwd = jsondata['passwd']
    system = jsondata['system']
    suser = jsondata['suser']
    total = username + passwd + system + suser

    send_message('{"info": "Get"}')


def main():
    send_message('"Yes. There is mypasswd"')
    read_message()
    sys.exit(0)


if __name__ == '__main__':
    main()
