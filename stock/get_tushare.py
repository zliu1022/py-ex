#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tushare as ts
import time
import sys

if len(sys.argv)!=1:
    print("Usage: ")
    print("query.py code")
    sys.exit()

def main():
    code = '002475'
    # ts.set_token('5f6fb605103f595ba5e9b8e1286e64a6841beddfe66b664c4de31655')
    pro = ts.pro_api()
    pro = ts.pro_api('5f6fb605103f595ba5e9b8e1286e64a6841beddfe66b664c4de31655')

    start_date='20200701'
    end_date='20200807'
    ts_code=['002475.SZ', '600519.SH']

    df = pro.daily(ts_code='002475.SZ', start_date='20200701', end_date='20200807')
    df.to_csv('./002475.sz.csv.1', index=False)

    print(df)
    print(len(df))
    print(df[0:1])
    print(df[0:1]['amount'])

    amount = float(df[0:1]['amount'])
    vol = float(df[0:1]['vol'])
    amount*10/vol

    '''
    df = pro.daily(ts_code='600519.SH', start_date='20100701', end_date='20200730')
    df.to_csv('./600519.sh.csv', index=False)
    df = pro.daily(ts_code='000425.SZ', start_date='20100701', end_date='20200730')
    df.to_csv('./000425.sz.csv', index=False)
    df = pro.daily(ts_code='002273.SZ', start_date='20100701', end_date='20200730')
    df.to_csv('./002273.sz.csv', index=False)
    df = pro.daily(ts_code='000858.SZ', start_date='20100701', end_date='20200730')
    df.to_csv('./000858.sz.csv', index=False)
    df = pro.daily(ts_code='600745.SH', start_date='20100701', end_date='20200730')
    df.to_csv('./600745.sh.csv', index=False)
    df = pro.daily(ts_code='601818.SH', start_date='20100701', end_date='20200730')
    df.to_csv('./601818.sh.csv', index=False)
    df = pro.daily(ts_code='600031.SH', start_date='20100701', end_date='20200730')
    df.to_csv('./600031.sh.csv', index=False)
    '''

if __name__ == "__main__":
   main()

