#!/usr/bin/python
#****************************************************************#
# ScriptName: getpasswd.py
# Create Date: 2017-06-01 20:44
# Modify Date: 2017-06-01 20:44
#***************************************************************#
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import sys
AES_SECRET_KEY = 'aaaaaaaaaaaaaaaa'

class AES_ENCRYPT(object):
    def __init__(self):
        self.key = AES_SECRET_KEY
        self.mode = AES.MODE_CBC


    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        print('tes')
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)


    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        plain_text = plain_text.decode('utf-8')
        result = plain_text
        return result

if __name__ == '__main__':
    print(len(AES_SECRET_KEY))
    print(sys.getsizeof(AES_SECRET_KEY))
    aes_encrypt = AES_ENCRYPT()
    passwd = 'where is the power!@#$%^&*()'
    encode = aes_encrypt.encrypt(passwd)
    unencode = aes_encrypt.decrypt(encode)
    print(passwd)
    print(encode.decode('ascii'))
    print(unencode)
