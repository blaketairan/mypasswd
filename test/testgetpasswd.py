import importParentDir
import sys
from getpasswd import AES_ENCRYPT
from getpasswd import secretIO
from getpasswd import manageCipher
from getpasswd import secretKey
from getpasswd import myPasswd


if __name__ == '__main__':
    # test AES_ENCRYPT
    # key = '!@#$%^&*12345678aaaaaaaaaaaaaaaa'
    # aes_encrypt = AES_ENCRYPT(key, key[:16])
    # passwd = 'where is the power!@#$%^&*()'
    # encode = aes_encrypt.encrypt(passwd)
    # unencode = aes_encrypt.decrypt(encode)
    # print(passwd)
    # print(encode.decode('ascii'))
    # print(unencode)

    # test secretIO
    # try:
    #     recordToWrite = sys.argv[1]
    # except:
    #     recordToWrite = '12345'
    # mypasswd = secretIO('blaketairan')
    # mypasswd.add(recordToWrite)
    # mypasswd.delete('11111')
    # mypasswd.query()

    # test secertKey
    # createkey = secretKey('blaketanra', 'fuck123')
    # print(createkey.acquireKey())

    # test manageCipher
    # mypassword = manageCipher('blaketairan')
    # mypassword.addRecord('qq', '111', 'aaa')
    # mypassword.addRecord('qq', '222', '223')
    # mypassword.addRecord('qq', '333', '123')
    # result = mypassword.queryRecord('qq','')
    # print(result)
    # mypassword.deleteRecord('qq', '584609377')

    # test m
    temp = secretIO(account='test')
    temp.deleteFile()
    temp = secretKey(account='test')
    temp.deleteKey()
    print('######### testing query when empty')
    mypasswd = myPasswd(action='query', account='test', system='test_system', sAccount='test_account')
    print(mypasswd.run())
    temp.deleteKey()
    print('######### testing add when empty')
    mypasswd = myPasswd(action='add', account='test', system='test_system', sAccount='test_account')
    print(mypasswd.run())
    temp.deleteKey()
    print('######### testing query when not empty')
    mypasswd = myPasswd(action='query', account='test', system='test_system', sAccount='test_account')
    print(mypasswd.run())
    temp.deleteKey()
    print('######### testing delete when empty')
    mypasswd = myPasswd(action='delete', account='test', system='test_system', sAccount='test_account')
    print(mypasswd.run())
    temp.deleteKey()
    print('######### testing query when empty again')
    mypasswd = myPasswd(action='query', account='test', system='test_system', sAccount='test_account')
    print(mypasswd.run())

