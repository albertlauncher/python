# -*- coding: utf-8 -*-

"""Generates 2 step verification (2FA) codes.

Save your key in a file located in "~/.2fa/.key", then it will work.

This extension require oathtool command line tool.

CentOS run the following command:
$ sudo yum install oathtool
Ubuntu run the following command:
$ sudo apt install oathtool

Save your key:
$ mkdir ~/.2fa
$ echo 'your key' > ~/.2fa/.key

Synopsis: <trigger> """

from albert import *
import os

__title__ = "2FA Tool"
__version__ = "0.1.0"
__triggers__ = "2fa "
__authors__ = "levi"


iconPath = os.path.dirname(__file__)+"/2fa.svg"


def handleQuery(query):
    if query.isTriggered:
        item = Item(id=__title__, icon=iconPath)
        key_path = '~/.2fa/.key'
        if os.path.exists(os.path.expanduser(key_path)):
            try:
                result = os.popen('oathtool -b --totp $(cat {}) 2>&1'.format(key_path)).read()[:-1]
            except Exception as ex:
                result = ex
        else:
            result = 'Save key in a file located in "~/.2fa/.key"'
        item.text = str(result)
        item.subtext = type(result).__name__
        item.addAction(ClipAction("Copy result to clipboard", str(result)))
        item.addAction(FuncAction("Execute", lambda: exec(str(result))))
    return item
