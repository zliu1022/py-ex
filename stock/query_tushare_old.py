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

    ret = ts.get_hist_data(code)
    #ret = ts.get_h_data(code)
    #ret = ts.get_h_data(code, start='2020-01-01', end='2020-07-30')
    print(ret)
    # pandas guide: https://www.jianshu.com/p/218baa41bab9
    '''
    print('ret.index\n', ret.index, '\n')
    print('ret.columns\n', ret.columns, '\n')
    print('ret.values\n', ret.values, '\n')
    print('ret.describe()\n', ret.describe(), '\n')
    print('ret.T\n', ret.T, '\n')
    print('ret.sort_index(axis=1, ascending=False)\n', ret.sort_index(axis=1, ascending=False), '\n')
    print('ret.sort_values(by=\'open\')\n', ret.sort_values(by='open'), '\n')
    print('ret[\'open\']\n', ret['open'], '\n')
    print('ret.loc\n', ret.loc, '\n')
    print('ret.dtypes\n', ret.dtypes, '\n')
    '''
    print('ret[0:30]\n', ret[0:30], '\n')

    ret = ts.get_hist_data(code, start='2017-01-01', end='2017-06-31')

if __name__ == "__main__":
   main()
