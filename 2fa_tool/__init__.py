# -*- coding: utf-8 -*-

"""Generates 2 step verification (2FA) codes.

Save your key in a file located in "~/.2fa/.key", then it will work.

Save your key:
$ mkdir ~/.2fa
$ echo 'your key' > ~/.2fa/.key

Synopsis: <trigger> """

from albert import *
import os
import base64
import hashlib
import hmac
import time
import six
import struct

__title__ = "2FA Tool"
__version__ = "0.1.1"
__triggers__ = "2fa "
__authors__ = "geeknonerd"

iconPath = os.path.dirname(__file__) + "/2fa.svg"


def get_hotp(
        secret,
        intervals_no,
        as_string=False,
        casefold=True,
        digest_method=hashlib.sha1,
        token_length=6,
):
    """
    Get HMAC-based one-time password on the basis of given secret and
    interval number.

    :param secret: the base32-encoded string acting as secret key
    :type secret: str or unicode
    :param intervals_no: interval number used for getting different tokens, it
        is incremented with each use
    :type intervals_no: int
    :param as_string: True if result should be padded string, False otherwise
    :type as_string: bool
    :param casefold: True (default), if should accept also lowercase alphabet
    :type casefold: bool
    :param digest_method: method of generating digest (hashlib.sha1 by default)
    :type digest_method: callable
    :param token_length: length of the token (6 by default)
    :type token_length: int
    :return: generated HOTP token
    :rtype: int or str
    """
    if isinstance(secret, six.string_types):
        # It is unicode, convert it to bytes
        secret = secret.encode('utf-8')
    # Get rid of all the spacing:
    secret = secret.replace(b' ', b'')
    try:
        key = base64.b32decode(secret, casefold=casefold)
    except (TypeError):
        raise TypeError('Incorrect secret')
    msg = struct.pack('>Q', intervals_no)
    hmac_digest = hmac.new(key, msg, digest_method).digest()
    ob = hmac_digest[19] if six.PY3 else ord(hmac_digest[19])
    o = ob & 15
    token_base = struct.unpack('>I', hmac_digest[o:o + 4])[0] & 0x7fffffff
    token = token_base % (10 ** token_length)
    if as_string:
        # TODO: should as_string=True return unicode, not bytes?
        return six.b('{{:0{}d}}'.format(token_length).format(token))
    else:
        return token


def get_totp(
        secret,
        as_string=False,
        digest_method=hashlib.sha1,
        token_length=6,
        interval_length=30,
        clock=None,
):
    """Get time-based one-time password on the basis of given secret and time.

    :param secret: the base32-encoded string acting as secret key
    :type secret: str
    :param as_string: True if result should be padded string, False otherwise
    :type as_string: bool
    :param digest_method: method of generating digest (hashlib.sha1 by default)
    :type digest_method: callable
    :param token_length: length of the token (6 by default)
    :type token_length: int
    :param interval_length: length of TOTP interval (30 seconds by default)
    :type interval_length: int
    :param clock: time in epoch seconds to generate totp for, default is now
    :type clock: int
    :return: generated TOTP token
    :rtype: int or str
    """
    if clock is None:
        clock = time.time()
    interv_no = int(clock) // interval_length
    return get_hotp(
        secret,
        intervals_no=interv_no,
        as_string=as_string,
        digest_method=digest_method,
        token_length=token_length,
    )


def handleQuery(query):
    if query.isTriggered:
        item = Item(id=__title__, icon=iconPath)
        key_path = '~/.2fa/.key'
        if os.path.exists(os.path.expanduser(key_path)):
            try:
                with open(key_path, 'r') as f:
                    result = get_totp(f.read().strip(), as_string=True).decode('utf-8')
            except Exception as ex:
                result = ex
        else:
            result = 'Save key in a file located in "~/.2fa/.key"'
        item.text = str(result)
        item.subtext = type(result).__name__
        item.addAction(ClipAction("Copy result to clipboard", str(result)))
    return item
