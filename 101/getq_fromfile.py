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
from getq_v1 import resp_json_url_frombook, update_q_v1

if __name__ == "__main__":
    if len(sys.argv) == 2:
        q_htmlfile = sys.argv[1]
    else:
        quit()

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    with open(q_htmlfile, "r", encoding="utf-8") as file:
        html_content = file.read()

    url_frombook = ''
    ret = resp_json_url_frombook(client, html_content, url_frombook)
    if ret.get('ret'):
        retcode = update_q_v1(client, ret.get('data')) # 0:新增,1:更新
    else:
        print('fail')

