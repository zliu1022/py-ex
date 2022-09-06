#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pysnowball as ball
from datetime import datetime
import time

# get token use anonymous user
r = requests.get("https://xueqiu.com", headers={"user-agent":"Mozilla"})
t = r.cookies["xq_a_token"]
print('xq_a_token:', t)

def get_url(url, t):
    try:
        r = requests.get(url, cookies={"xq_a_token": t},  headers={"user-agent":"Mozilla/5.0"})
        r.raise_for_status() #如果状态不是200，引发HTTPError
        r.encoding = r.apparent_encoding #分析网页的编码形式

        '''
        print(r.status_code) # 200: succ; 404: fail
        print(r.text)
        print(r.encoding)
        print(r.appartent_encoding)
        print(r.content)
        print(data.json())
        '''

        return r.json()
    except:
        return "error"


if __name__ == '__main__':
    #url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=before&count=-365&symbol="+ts_code_symbol+"&begin="+self.dateTimp
    #url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ002475&begin=1647772635398&period=day&type=before&count=-284&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"

    stock_code = 'SZ002475'
    #stock_date = '2020-6-16' #除权日
    stock_date = '2022-8-3'

    #ts = str(int(datetime.timestamp(datetime.now()) * 1000))
    ts = str(int(datetime.timestamp(datetime.strptime(stock_date, '%Y-%m-%d')) * 1000))

    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=" + stock_code + \
        "&begin=" + ts + \
        "&period=day&" + \
        "type=" + "none" + \
        "&count=3" + \
        "&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"

    print(url)

    r = get_url(url, t)
    print(type(r))

    #print(r)

    # dict_keys(['data', 'error_code', 'error_description'])
    print(r.keys())

    print()

    # dict_keys(['data', 'error_code', 'error_description'])
    for i in r.keys():
        print(i, type(r[i]))
        if type(r[i]) == type(r): # class dict
            print('  ', r[i].keys())


            #dict_keys(['symbol', 'column', 'item'])
            #   symbol <class 'str'> 8
            #   column <class 'list'> 24
            #   item <class 'list'> 3
            for j in r[i].keys():
                print('  ', j, type(r[i][j]), len(r[i][j]))

                if j == 'column':
                    title = r[i][j]
                    print('  ', end=' ')

                    # timestamp volume open high low close chg percent turnoverrate amount 
                    # volume_post amount_post pe pb ps pcf market_capital balance 
                    # hold_volume_cn hold_ratio_cn net_volume_cn hold_volume_hk hold_ratio_hk net_volume_hk
                    for k in range(len(r[i][j])):
                        print(r[i][j][k], end=' ')
                    print()

                if j == 'item':
                    for k in range(len(r[i][j])): # print all item
                        item = r[i][j][k]
                        print(datetime.fromtimestamp(item[0]/1000).strftime("%Y-%m-%d"), item[1:]) # volume open high low close chg percent turnoverrate
                        for l in range(len(item)):
                            print(title[l], item[l])
                        print()
                    print()
