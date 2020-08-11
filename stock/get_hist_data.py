# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 09:15:40 2015
@author: jet
"""

import const as ct
import pandas as pd
import json
#from urllib2 import urlopen,Request
import requests

def get_hist_data(code = None, start = None, end = None, ktype = 'D'):
    """
    功能:
    获取个股历史交易数据
    --------
    输入:
    --------
    code:string
    股票代码 比如:601989
    start:string
    开始日期 格式:YYYY-MM-DD 为空时取到API所提供的最早日期数据
    end:string
    结束日期 格式:YYYY-MM-DD 为空时取到最近一个交易日数据
    ktype:string(default=D, 函数内部自动统一为大写)
    数据类型 D=日K线，W=周K线，M=月K线，5=5分钟，15=15分钟
    30=30分钟，60=60分钟 
    输出:
    --------
    DataFrame
    date 日期
    open 开盘价
    high 最高价
    close 收盘价
    low 最低价
    chg 涨跌额 
    p_chg 涨跌幅
    ma5 5日均价
    ma10 10日均价
    ma20 20日均价
    vma5 5日均量
    vma10 10日均量
    vma20 20日均量
    turnover换手率(指数无此项)
    """ 

    code = code_to_APIcode(code.upper())
    ktype = ktype.upper()

    url = '' 
    url = get_url(ktype, code) 
    print(url)

    js = json.loads(ping_API(url))
    cols = []

    if len(js['record'][0]) == 14:
        cols = ct.INDEX_DAY_PRICE_COLS
    else:
        cols = ct.DAY_PRICE_COLS
    df = pd.DataFrame(js['record'], columns=cols)

    if ktype in ct.K_TYPE_KEY:
        df = df.applymap(lambda x:x.replace(u',', u''))
    for col in cols[1:]:
        df[col]=df[col].astype(float)
    if start is not None:
        df = df [df.date >= start]
    if end is not None:
        df = df[df.date <= end]
    df = df.set_index('date')
    return df 

def code_to_APIcode(code):
    """
    功能：
    验证输入的股票代码是否正确，若正确则返回API对应使用的股票代码
    """
    print(code)
    if code in ct.INDEX_KEY:
        return ct.INDEX_LIST[code]
    else:
        if len(code) != 6:
            raise IOError('code input error!')
        else:
            return 'sh%s'%code if code[:1] in ['5', '6'] else 'sz%s'%code

def get_url(ktype, code):
    """
    功能：
    验证输入的K线类型是否正确，若正确则返回url
    """ 
    if ktype in ct.K_TYPE_KEY:
        url = ct.DAY_PRICE_URL % (ct.PAGE_TYPE['http'], ct.PAGE_DOMAIN['ifeng'], ct.K_TYPE[ktype], code)
        return url
    elif ktype in ct.K_TYPE_MIN_KEY:
        url = ct.MIN_PRICE_URL % (ct.PAGE_TYPE['http'], ct.PAGE_DOMAIN['ifeng'], code, ktype)
        return url
    else:
        raise IOError('ktype input error!')

def ping_API(url):
    """
    功能：
    向API发送数据请求，若链接正常返回数据
    """
    text = ''

    try:
        r=requests.get(url)
        req_status = "Normal"
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        req_status = "Connection refused"
    except requests.exceptions.Timeout:
        req_status = "Connection Timeout"
    except requests.exceptions.HTTPError as e:
        print("requests.exceptions.HTTPError")
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        print("requests.exceptions", e)
        raise SystemExit(e)
    if req_status == "Normal":
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            print(req_status)
            print('error')
    else:
        print(req_status)
        print('error')

    '''
    try:
        req = Request(url)
        text = urlopen(req,timeout=10).read() 
        if len(text) < 15:
            raise IOError('no data!') 
    except Exception as e:
        print(e)
    else:
        return text
    '''

#测试入口
#print(get_hist_data('601989','2015-07-11','2015-07-22'))
print(get_hist_data('002475','2018-01-01','2020-07-30'))

