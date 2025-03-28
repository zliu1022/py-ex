#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from requests.cookies import RequestsCookieJar
import sys
from bs4 import BeautifulSoup
import re
import json
import base64
from matchq import canonicalize_positions
from bson import ObjectId
from config import site_name, base_url, cache_dir, db_name, headers_get, headers_login
import time
from getq_v1 import resp_json_url_frombook, update_q_v1, get_url_v1, login

if __name__ == "__main__":
    if len(sys.argv) == 3:
        username = sys.argv[1]
        target_url = sys.argv[2]
        url = base_url + target_url
    else:
        quit()

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_collection = db['q']

    session = login(client, username)

    response = get_url_v1(session, url)
    if response.status_code == 200:
        ret = resp_json_url_frombook(client, response.text, url_frombook)
        if ret.get('ret'):
            # 成功：更新q表，更新book_n_q表, 不锁定book_n_q表，确保一本book_id只有一个任务
            retcode = update_q_v1(client, ret.get('data')) # 0:新增,1:更新
        else:
            print(f"fail")
    else:
        print(f"fail {response.status_code}")

