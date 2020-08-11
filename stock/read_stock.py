#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import csv
import datetime
import sys
import os
import matplotlib.pyplot as plt
import math

if len(sys.argv)!=4:
    print("Usage: ")
    print("read_stock.py filename begin_date end_date")
    print('read_stock.py 002475.sz.csv 20170102 20200102')
    sys.exit()

# buy and sell trigger by yesterday's average trade price
# buy quantity will exp according to the average buy price
class Sim:
    def __init__(self):
        self.buy_price_ratio = 0.96
        self.sell_price_ratio = 1.04
        self.buy_quantity_weight = 1

    def set(self, br, sr, bqw):
        self.buy_price_ratio = br
        self.sell_price_ratio = sr
        self.buy_quantity_weight = bqw

    def simulate(self, data, begin_date, end_date):
        # create original data with buy_quantity sell_quantity quantity	cost benefit
        begin_d    = datetime.datetime.strptime(begin_date, '%Y%m%d')
        end_d      = datetime.datetime.strptime(end_date, '%Y%m%d')
        self.begin_d = begin_date
        self.end_d = end_date
        assert(begin_d<end_d)
        # from early time to current
        #     find the begin_date, set quantity,cost,benefit to 0
        #         calculate buy_price, sell_price
        #         compare price, compare quantity, refresh quantity,cost,benefit
        quantity = 0
        cost = 0
        benefit = 0

        buy_q_sum = 0.0
        buy_cost_sum = 0.0
        buy_avg = 0.0

        r = []
        for i in range(len(data)-1, -1, -1):
            r.append([data[i][0], 0, 0, 0.0, 0, 0.0])
            pos = len(r)-1
            d = datetime.datetime.strptime(data[i][0], '%Y%m%d')
            if d>end_d:
                continue
            if d>=begin_d:
                high = float(data[i][1])
                low = float(data[i][2])
                avg = float(data[i][3])
                sell_quantity = 0
                buy_quantity = 0.0

                buy_p = self.buy_price_ratio * avg
                sell_p = self.sell_price_ratio * avg
                if high>=sell_p:
                    sell_quantity = 1
                if low<=buy_p:
                    #buy_q_new = round(math.exp(self.buy_quantity_weight*buy_avg/low-1))
                    buy_q_new = 1
                    buy_quantity = 1
                    if buy_avg!=0:
                        buy_q_new = round(math.exp(buy_avg/low-1))

                    if buy_quantity != buy_q_new:
                        print("buy_q_new ", buy_quantity, ' -> ', buy_q_new, '(', buy_avg, low, buy_avg/low, math.exp(buy_avg/low-1))

                    buy_quantity = buy_q_new

                if quantity<sell_quantity:
                    sell_quantity = quantity

                cost = cost + buy_quantity*buy_p - sell_quantity*sell_p
                quantity = quantity + buy_quantity - sell_quantity
                benefit = quantity*avg - cost

                buy_q_sum += buy_quantity
                buy_cost_sum += buy_quantity*buy_p
                if buy_q_sum!=0:
                    buy_avg = buy_cost_sum/buy_q_sum

                r[pos][1] = buy_quantity
                r[pos][2] = sell_quantity
                r[pos][3] = round(cost,2)
                r[pos][4] = quantity
                r[pos][5] = round(benefit,2)

        # save result to private
        self.result = r
        return r

    def print(self):
        count = 0
        print(self.begin_d, ' ~ ', self.end_d)
        begin_d    = datetime.datetime.strptime(self.begin_d, '%Y%m%d')
        end_d      = datetime.datetime.strptime(self.end_d, '%Y%m%d')
        max_b_index = 0
        max_b = 0.0
        max_b_rate = 0.0
        max_b_rate_index = 0
        rate = 0.0
        print('         buy sell cost quantity benefit')
        for i in range(len(self.result)):
            tmp = self.result[i]
            d = datetime.datetime.strptime(tmp[0], '%Y%m%d')
            if d>end_d:
                break
            duration = float(getattr(d - begin_d, 'days'))
            if duration!=0:
                rate = tmp[5] / duration
            if d>end_d-datetime.timedelta(days=1):
            #if d>=begin_d:
                print(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
                count+=1
            if d>begin_d:
                if tmp[5]>max_b:
                    max_b_index = i
                    max_b = tmp[5]
                if rate>max_b_rate:
                    max_b_rate = rate
                    max_b_rate_index = i

        tmp = self.result[max_b_index]
        print('max ', tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
        tmp = self.result[max_b_rate_index]
        print('max rate', tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])

    def draw(self, show):
        t = []
        b = []
        c = []
        begin_d    = datetime.datetime.strptime(self.begin_d, '%Y%m%d')
        end_d      = datetime.datetime.strptime(self.end_d, '%Y%m%d')
        for i in range(len(self.result)):
            tmp = self.result[i]
            d = datetime.datetime.strptime(tmp[0], '%Y%m%d')
            if d>end_d:
                break
            if d>=begin_d:
                t.append(i)
                b.append(tmp[5])
                c.append(tmp[3])

        if show==1:
            plt.figure()
            plt.plot(t, b, "dodgerblue", label="benefit")
            plt.plot(t, c, "blue", label="cost")
            plt.legend(loc='best')
            plt.title("cost & benefit " + self.begin_d + " ~ " + self.end_d)
            plt.xlabel('day')
            plt.ylabel('￥')
            plt.ylim(0, 200)
            #plt.axhline(100)
            plt.show()
        return t,b,c

class Stock:
    def __init__(self):
        self.data = []

    def __init__(self, filename):
        self.data = self.read_original(filename)
        self.quan = Quan(filename)
        self.qfq_data = self.quan.qfq(self.data)

    def read_original(self, filename):
        with open(filename, encoding = 'utf-8') as f:
            data = np.loadtxt(f, str, delimiter = ",", skiprows=1)
            #print('ts_code trade_date open high low close pre_close change pct_chg vol amount')

        for i in range(len(data)):
            data[i][5] = float(data[i][10]) *10 / float(data[i][9])
        data = np.delete(data, [0,2,6,7,8,9,10], axis=1)
        #print('trade_date high low avg')
        return data

    def draw(self, begin_date, end_date, show):
        t = []
        p = []
        count = 0
        begin_d    = datetime.datetime.strptime(begin_date, '%Y%m%d')
        end_d      = datetime.datetime.strptime(end_date, '%Y%m%d')
        for i in range(len(self.qfq_data)-1, -1, -1):
            tmp = self.qfq_data[i]
            d = datetime.datetime.strptime(tmp[0], '%Y%m%d')
            if d>end_d:
                break
            if d>=begin_d:
                count +=1
                t.append(count)
                p.append(round(float(tmp[3]),2))

        if show==1:
            plt.figure()
            plt.plot(t, p, "red", label="avg price")
            plt.legend(loc='best')
            plt.title("avg price " + begin_date + " ~ " + end_date)
            plt.xlabel('day')
            plt.ylabel('￥')
            plt.ylim(0, 60.0)
            #plt.axhline(100)
            plt.show()
        return t,p

class Quan:
    def __init__(self):
        self.date = []
        self.interest = []
        self.ratio = []

    def __init__(self, filename):
        self.date = []
        self.interest = []
        self.ratio = []
        quan_filename = os.path.splitext(filename)[0] + '.quan'
        self.set_fromfile(quan_filename)

    def set(self, date, interest, ratio):
        self.date.append(date)
        self.interest.append(interest)
        self.ratio.append(ratio)

    def set_fromfile(self, filename):
        with open(filename, encoding = 'utf-8') as f:
            d = np.loadtxt(f, str, delimiter = ",", skiprows=1)
            #print('quan_date base new interest

        for i in range(len(d)):
            date = d[i][0]
            base = float(d[i][1])
            new  = float(d[i][2])
            interest = float(d[i][3])
            total = base + new
            self.set(date, float(interest/total), float(base/total))

    def fq(self, p, i):
        #return round((float(p) * self.ratio[i] - self.interest[i]), 3)
        return (float(p) * self.ratio[i] - self.interest[i])

    def qfq(self, data):
        tmp = data.copy()
        for j in range(len(self.date)):
            fq_d = datetime.datetime.strptime(self.date[j], '%Y%m%d')
            for i in range(len(tmp)):
                d = datetime.datetime.strptime(tmp[i][0], '%Y%m%d')
                if d<fq_d:
                    #print(i, tmp[i][1], tmp[i][3], tmp[i][4], tmp[i][9], tmp[i][10], ' -> ', end='')
                    '''
                    tmp[i][3] = self.fq(tmp[i][3], j)
                    tmp[i][4] = self.fq(tmp[i][4], j)
                    tmp[i][9] = self.fq(tmp[i][9], j)
                    tmp[i][10] = self.fq(tmp[i][10], j)
                    '''
                    tmp[i][1] = self.fq(tmp[i][1], j)
                    tmp[i][2] = self.fq(tmp[i][2], j)
                    tmp[i][3] = self.fq(tmp[i][3], j)
                    #print(i, tmp[i][1], tmp[i][3], tmp[i][4], tmp[i][9], tmp[i][10])
        return tmp


def print_price(data, begin_date, end_date):
    begin_d    = datetime.datetime.strptime(begin_date, '%Y%m%d')
    end_d      = datetime.datetime.strptime(end_date, '%Y%m%d')
    print('date high low avg')
    for i in range(len(data)):
        d = datetime.datetime.strptime(data[i][0], '%Y%m%d')
        if d<=end_d and d>=begin_d:
            #print(data[i][1], data[i][3], data[i][4], data[i][9], data[i][10])
            high = round(float(data[i][1]),2)
            low = round(float(data[i][2]), 2)
            avg = round(float(data[i][3]), 2)
            print(data[i][0], high, low, avg)
    print('')

def check_qfq(filename):
    now_a = datetime.datetime.now()

    stock = Stock(filename)
    data = stock.data

    print_price(data, '20200616', '20200618')
    print('')
    print_price(data, '20190704', '20190708')
    print('')
    print_price(data, '20180716', '20180718')
    print('')

    '''
    quan = Quan()
    quan.set('20200617', float(1.2/13), float(10/13))
    quan.set('20190705', float(0.5/13), float(10/13))
    quan.set('20180717', float(0.6/13), float(10/13))
    quan.set('20170706', float(0.8/15), float(10/15))
    quan.set('20160613', float(0.9/15), float(10/15))
    quan.set('20150619', float(0.8/15), float(10/15))
    qfq_data = quan.qfq(data)
    '''

    qfq_data = stock.qfq_data
    print('----- after fu quan -----')
    print_price(qfq_data, '20200616', '20200618')
    print('')
    print_price(qfq_data, '20190704', '20190708')
    print('')
    print_price(qfq_data, '20180716', '20180718')
    print('')
    print_price(qfq_data, '20170705', '20170707')
    print('')
    print_price(qfq_data, '20160612', '20160614')
    print('')
    print_price(qfq_data, '20150618', '20150620')
    print('')

    now_b = datetime.datetime.now()
    print("cost time  ", now_b-now_a, file=sys.stdout)

if __name__ == "__main__":
    filename = sys.argv[1]
    #check_qfq(filename)

    begin_date = sys.argv[2]
    end_date   = sys.argv[3]
    #begin_date = '20200102'
    #end_date   = '20200730'

    stock = Stock(filename)
    print_price(stock.data,     '20140701', '20140731')
    print_price(stock.qfq_data, '20140701', '20140731')
    t,p = stock.draw(begin_date, end_date, 0)
 
    sim = Sim()
    #sim.set(0.96, 1.04, 1)
    r = sim.simulate(stock.qfq_data, begin_date, end_date)
    sim.print()
    t,b,c = sim.draw(0)

    plt.figure()
    plt.plot(t, p, "red", label="price")
    plt.plot(t, b, "blue", label="benefit")
    plt.plot(t, c, "dodgerblue", label="cost")
    plt.legend(loc='best')
    plt.title("cost & benefit " + begin_date + ' ~ ' + end_date)
    plt.xlabel('day')
    plt.ylabel('￥')
    #plt.ylim(0, 200)
    plt.axhline(0)
    plt.show()

