#!/usr/bin/env python3
import importParentDir
from chromeConnect import chromeMypasswd
import sys


if __name__ == '__main__':
    chrome = chromeMypasswd('blaketairan', 'bla23', True)
    if not chrome.success:
        print(chrome.failInfo)
    print('finish')
    del chrome

    chrome = chromeMypasswd('blaketairan', 'bla23', False)
    if not chrome.success:
        print(chrome.failInfo)
    print('finish')
    del chrome

    chrome = chromeMypasswd('blaketairan', 'blake123', False)
    if not chrome.success:
        print(chrome.failInfo)
    else:
        resultType, result = chrome.run('query', 'qq', '58460')
        print(result)
    print('finish')
