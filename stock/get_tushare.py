#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tushare as ts
import time
import sys

if len(sys.argv)!=4:
    print("Usage: ")
    print("get_tushare.py 603060.SH 20220608 20220609")
    sys.exit()

def main():
    # ts.set_token('5f6fb605103f595ba5e9b8e1286e64a6841beddfe66b664c4de31655')
    #pro = ts.pro_api()
    pro = ts.pro_api('5f6fb605103f595ba5e9b8e1286e64a6841beddfe66b664c4de31655')

    #ts_code=['002475.SZ', '600519.SH']

    #ts_code = '600570.SH'
    #start_date = '20220817'
    #end_date = '20220818'

    #ts_code = '603088.SH'
    #start_date = '20220530'
    #end_date = '20220531'

    #ts_code = '603005.SH'
    #start_date = '20220519'
    #end_date = '20220520'

    ts_code = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    filename = ts_code + '.tushare.csv'
    print(ts_code, start_date, end_date)
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    print(df)


    #df.to_csv(filename, index=False)

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

