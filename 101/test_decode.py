#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from getq_v1 import decode_prepos
from config import db_name, base_url

import re

c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
d = re.compile(r"^(?:[A-Za-z\d+/]{4})*?(?:[A-Za-z\d+/]{2}(?:==)?|[A-Za-z\d+/]{3}=?)?$")

def u(t):
    t = re.sub(r'[\t\n\f\r ]+', '', str(t))
    if not d.match(t):
        raise TypeError("The string to be decoded is not correctly encoded.")
    pos = 2 - (3 & len(t))
    t += '=='[pos:] if pos < 2 else ''
    o = ''
    for n in range(0, len(t), 4):
        e = (c.index(t[n]) << 18) | (c.index(t[n + 1]) << 12)
        i = c.index(t[n + 2])
        e |= (i << 6)
        s = c.index(t[n + 3])
        e |= s

        if i == 64:
            o += chr((e >> 16) & 0xFF)
        elif s == 64:
            o += chr((e >> 16) & 0xFF)
            o += chr((e >> 8) & 0xFF)
        else:
            o += chr((e >> 16) & 0xFF)
            o += chr((e >> 8) & 0xFF)
            o += chr(e & 0xFF)
    return o

def f(t, e):
    i = u(t)
    s = 0
    o = []
    for n in range(len(i)):
        o.append(chr(ord(i[n]) ^ ord(e[s])))
        s = (s + 1) % len(e)
    return ''.join(o)

if __name__ == "__main__":
    testcase = [
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
        { 'c' : "amsTVVARHRATWVcRHRATQ1ARHRATQ0MRbBwRaBFQVxIdExFXVRIdExFXQRIdExFDVBJsbg==", 'r': 2},
        { 'c' : "amtsHxNobG0=", 'r': 2},
        { 'c' : "amtsHhJpbG0=", 'r': 1},
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
    ]
    for t in testcase:
        r_str = str(t.get('r')+1)
        salt = '101' + r_str + r_str + r_str

        ret1 = decode_prepos(t.get('c'), t.get('r'))
        ret2 = f(t.get('c'), salt)
        print(ret1, ret2)

