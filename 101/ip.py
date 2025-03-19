#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
macos电脑有2个IP可以向外访问，
一个IP通过网线获得，
一个IP通过连接外部wifi热点拿到
使用python的request库时，指定使用其中的某个IP
进行session.post, session.get
'''

import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import socket

# 自定义 Adapter，绑定 source IP
class SourceIPAdapter(HTTPAdapter):
    def __init__(self, source_ip, **kwargs):
        self.source_ip = source_ip
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        # 强制来源 IP 地址
        kwargs['source_address'] = (self.source_ip, 0)
        return super().init_poolmanager(*args, **kwargs)

# office
eth_ip  = '192.168.8.46'
wifi_ip = '192.168.4.9'

# home
eth_ip = '172.16.0.2'
wifi_ip = '192.168.3.24'

# 选择走有线 or Wi-Fi
source_ip_list = [
    {'type':'eth', 'ip':eth_ip}, 
    {'type':'wifi','ip':wifi_ip}
]

for ip in source_ip_list:
    print(ip)
    source_ip = ip['ip']

    try:
        # 新建 Session，绑定 IP
        session = requests.Session()
        adapter = SourceIPAdapter(source_ip)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # 测试请求，看看出口 IP
        resp = session.get('https://api.ipify.org?format=json')
    except Exception as e:
        print(e)
        print()
        continue

    print(f'出口 IP ({source_ip}) 返回结果: {resp.json()}')
    print()

