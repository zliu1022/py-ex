#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pysnowball as ball
import requests
from datetime import datetime

# txtplan_digit can deal with three text condition:
# 10转2.999711股派1.199884元
# 10转2.999711股
# 10派1.199884元
def txtplan_digit(s):
    base, new, bonus = 0,0,0
    zhuan_pos = s.find('转')
    gu_pos =    s.find('股')
    pai_pos =   s.find('派')
    yuan_pos =  s.find('元')
    if zhuan_pos != -1:
        new = s[zhuan_pos+1:gu_pos]
        if pai_pos != -1:
            bonus = s[pai_pos+1:yuan_pos]
            if zhuan_pos < pai_pos:
                base = s[0:zhuan_pos]
            else:
                base = s[0:pai_pos]
        else:
            bonus = 0
    else:
        if pai_pos != -1:
            bonus = s[pai_pos+1:yuan_pos]
            base = s[0:pai_pos]
        else:
            base = 0
        new = 0
    return base, new, bonus

# get token use anonymous user
r = requests.get("https://xueqiu.com", headers={"user-agent":"Mozilla"})
t = r.cookies["xq_a_token"]
print('xq_a_token:', t)

ball.set_token('xq_a_token=' + t + ';')
stock_code = 'SZ002475'

'''
out = ball.quotec(stock_code)
print('实时行情')

获取某支股票的行情数据-详细
import pysnowball as ball
ball.quote_detail("SH600104")
'''

out = ball.bonus(stock_code)
print('F10 分红融资(bonus)')

for i in range(len(out['data']['items'])):
    d = out['data']['items'][i]
    base,new,bonus = txtplan_digit(d['plan_explain'])
    print(d['dividend_year'], 
        '除息日', datetime.fromtimestamp(d['ashare_ex_dividend_date']/1000).strftime("%Y-%m-%d"),
        '权益日', datetime.fromtimestamp(d['equity_date']/1000).strftime("%Y-%m-%d"),
        base, '股', '转', new, '分红', bonus,
        d['cancle_dividend_date'])

'''
type(out) <class 'dict'>
out.keys() dict_keys(['data', 'error_code', 'error_description'])
out['data'].keys() dict_keys(['addtions', 'allots', 'items'])
type(out['data']['items']) <class 'list'>
type(out['data']['items'][0]) <class 'dict'>
out['data']['items'][0].keys() dict_keys(['dividend_year', 'ashare_ex_dividend_date', 'equity_date', 'plan_explain', 'cancle_dividend_date'])

时间转换：https://www.runoob.com/python3/python-timstamp-str.html
'''

if __name__ == '__main__':
    quit()
