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


# deepseek r1版本
import re
import base64

# Base64格式验证正则
r1_d = re.compile(r'^(?:[A-Za-z\d+/]{4})*?(?:[A-Za-z\d+/]{2}(?:==)?|[A-Za-z\d+/]{3}=?)?$')

def r1_u(t):
    # 移除空白字符
    t = re.sub(r'[\t\n\f\r ]+', '', t)
    # 验证Base64格式
    if not r1_d.match(t):
        raise TypeError("The string to be decoded is not correctly encoded.")

    # 补全等号
    mod = len(t) % 4
    if mod == 2:
        t += '=='
    elif mod == 3:
        t += '='

    # Base64解码
    decoded = base64.b64decode(t)
    # 将字节解码为latin1字符串（保留原始字节值）
    return decoded.decode('latin1')

def r1_f(t, e):
    # 解码Base64字符串
    decoded_str = r1_u(t)
    s = 0
    result = []
    # 遍历每个字符进行异或操作
    for char in decoded_str:
        # 获取字符的Unicode码点
        byte = ord(char)
        # 获取密钥字符的Unicode码点
        key_char = e[s]
        key_code = ord(key_char)
        # 异或操作并取低16位
        xor_value = byte ^ key_code
        result.append(chr(xor_value & 0xFFFF))
        # 更新密钥索引（循环使用密钥）
        s = (s + 1) % len(e)
    # 连接结果字符串
    return ''.join(result)

if __name__ == "__main__":
    testcase = [
        { 'c' : "amsTQkMQbBwRaRBDXhIdEhBcQRJsbw==", 'r': 1},
        { 'c' : "amsTQkMQbBwRaRBDXhIdEhBcQRJsbw==", 'r': 2},
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
        { 'c' : "amsTVVARHRATWVcRHRATQ1ARHRATQ0MRbBwRaBFQVxIdExFXVRIdExFXQRIdExFDVBJsbg==", 'r': 2},
        { 'c' : "amtsHxNobG0=", 'r': 2},
        { 'c' : "amtsHhJpbG0=", 'r': 1},
        { 'c' : "amsTQlYQHRATQ1oQbBwRaRBcUhIdEhBDVxJsbw==", 'r': 1},
    ]
    for t in testcase:
        r_str = str(t.get('r')+1)
        salt = db_name + r_str + r_str + r_str

        try:
            ret1 = decode_prepos(t.get('c'), t.get('r'))
        except Exception:
            ret1= None
        ret2 = f(t.get('c'), salt)
        ret3 = r1_f(t.get('c'), salt)
        print(ret1, ret2, ret3)

