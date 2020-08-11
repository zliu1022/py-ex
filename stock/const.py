# -*- coding: utf-8 -*-
"""
功能：        
放置常量，列表    
Created on Thu Jul 23 09:17:27 2015
@author: jet
"""

DAY_PRICE_COLS = ['date', 'open', 'high', 'close', 'low', 'volume',                                   
'chg', '%chg', 'ma5', 'ma10', 'ma20',                                   
'vma5', 'vma10', 'vma20', 'turnover']

DAY_PRICE_URL = '%sapi.finance.%s/%s/?code=%s&type=last'

INDEX_KEY = ['SH', 'SZ', 'HS300', 'SZ50', 'GEB', 'SMEB']

INDEX_LIST = {'SH': 'sh000001', 'SZ': 'sz399001', 'HS300': 'sz399300',                                                
'SZ50': 'sh000016', 'GEB': 'sz399006', 'SMEB': 'sz399005'}

INDEX_DAY_PRICE_COLS= ['date', 'open', 'high', 'close', 'low', 'volume',                                                                                          
'chg', '%chg', 'ma5', 'ma10', 'ma20',                                                                                          
'vma5', 'vma10', 'vma20']              

K_TYPE_KEY = ['D', 'W', 'M']

K_TYPE_MIN_KEY = ['5', '15', '30', '60']

K_TYPE = {'D': 'akdaily', 'W': 'akweekly', 'M': 'akmonthly'}

MIN_PRICE_URL = '%sapi.finance.%s/akmin?scode=%s&type=%s'              

PAGE_TYPE = {'http': 'http://', 'ftp': 'ftp://'}

PAGE_DOMAIN = {'sina': 'sina.com.cn', 'ifeng': 'ifeng.com'}

URL_ERROR_MSG = '获取失败，请检查网络状态，或者API端口URL已经不匹配！'
