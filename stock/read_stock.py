#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import csv
import datetime
import sys
import os
import matplotlib.pyplot as plt
import math
from scipy import signal

if len(sys.argv)!=5:
    print("Usage: ")
    print("./read_stock.py filename begin_date end_date")
    print('./read_stock.py 002475.sz.csv 20170102 20200102')
    print('./read_stock.py 002273.sz.csv 20150102 20201002 0')
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
        print('date      high  low      d_avg    avg  buy_p sell_p  buy_q sell_q         q     cost   benefit')
        for i in range(len(data)-1, -1, -1):
            r.append([data[i][0], 0, 0, 0.0, 0, 0.0])
            pos = len(r)-1
            d = datetime.datetime.strptime(data[i][0], '%Y%m%d')
            if d>end_d:
                continue
            if d>=begin_d:
                high = round(float(data[i][1]),2)
                low  = round(float(data[i][2]),2)
                avg  = round(float(data[i+1][3]),2)
                d_avg = data[i+1][0]
                #avg = float(data[i][3])

                sell_quantity = 0
                buy_quantity = 0.0

                # 1. Update target by known info
                # calculate the target price for buy or sell
                buy_p  = self.buy_price_ratio * avg
                sell_p = self.sell_price_ratio * avg

                # 2. calculate buy_q, sell_q by comparing target and today's high and low
                # update buy_quantity & sell_quantity
                if high>=sell_p:
                    sell_quantity = 1
                if low<=buy_p:
                    buy_quantity = 1
                    if buy_avg!=0:
                        buy_q_new = math.ceil(math.exp(self.buy_quantity_weight*buy_avg/low-1))
                    else:
                        buy_q_new = 1
                    buy_quantity = buy_quantity * buy_q_new
                if quantity<sell_quantity:
                    sell_quantity = quantity

                # update cost, quantity in hand, virtual benefit
                cost = cost + buy_quantity*buy_p - sell_quantity*sell_p
                quantity = quantity + buy_quantity - sell_quantity
                benefit = quantity*avg - cost

                # calculate the average buy cost
                buy_q_sum += buy_quantity
                buy_cost_sum += buy_quantity*buy_p
                if buy_q_sum!=0:
                    buy_avg = buy_cost_sum/buy_q_sum

                r[pos][1] = buy_quantity
                r[pos][2] = sell_quantity
                r[pos][3] = round(cost,2)
                r[pos][4] = quantity
                r[pos][5] = round(benefit,2)
                print('{} {:5.2f} {:5.2f}  | {} {:5.2f} {:.2f} {:.2f} | {:5.0f} {:5.0f}      | {:5.0f} {:8.2f} {:8.2f}'.format(r[pos][0], high, low, d_avg, avg, buy_p, sell_p, buy_quantity, sell_quantity, quantity, round(cost,2), round(benefit,2)))
                #print('')

        self.result = r
        return r

    def output(self):
        count = 0
        print(self.begin_d, ' ~ ', self.end_d)
        print('         buy sell cost quantity benefit')
        begin_d    = datetime.datetime.strptime(self.begin_d, '%Y%m%d')
        end_d      = datetime.datetime.strptime(self.end_d,   '%Y%m%d')
        max_b_index = 0
        max_b = 0.0
        max_b_rate = 0.0
        max_b_rate_index = 0
        rate = 0.0
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
        print('max     ', tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
        tmp = self.result[max_b_rate_index]
        print('max rate', tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
        print('')

    def get_date(self, i):
        tmp = self.result[i]
        print(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
        return self.result[i][0]

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
            plt.ylabel('RMB')
            #plt.ylim(0, 200)
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
            # 002475.sz.csv from tushare, data with amount
            #       0       1          2    3    4   5     6         7      8       9   10
            #print('ts_code trade_date open high low close pre_close change pct_chg vol amount')

            # sz002475.csv from ifeng without amount
            #    0    1    2     3   4      5   6    7   8    9   10   11    12    13       14
            # date,open,high,close,low,volume,chg,%chg,ma5,ma10,ma20,vma5,vma10,vma20,turnover

        '''
        #print('trade_date high low avg')
        for i in range(len(data)):
            data[i][5] = float(data[i][10]) *10 / float(data[i][9])
        data = np.delete(data, [0,2,6,7,8,9,10], axis=1)
        '''

        # date high low
        #data = np.delete(data, [0,1,3,5,6,7,8,9,10,11,12,13,14], axis=1)
        return data

    def draw(self, begin_date, end_date, show):
        t = []
        p = []
        high = []
        low = []
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
                high.append(round(float(tmp[1]),2))
                low.append(round(float(tmp[2]),2))

        #max_pos, tmp_pos = max_min(high)
        #tmp_pos, min_pos = max_min(low)

        max_pos = signal.argrelextrema(np.array(high), np.greater)[0] #极大值点，改为np.less即可得到极小值点
        min_pos  = signal.argrelextrema(np.array(low), np.less)[0] #极大值点，改为np.less即可得到极小值点

        if show==1:
            plt.figure()
            #plt.plot(t, p, "red", label="avg")
            plt.plot(t, high, "orange", label="high")
            plt.plot(t, low, "green", label="low")
            plt.legend(loc='best')
            plt.title(filename + " daily price " + begin_date + " ~ " + end_date)
            plt.xlabel('day')
            plt.ylabel('RMB')
            #plt.ylim(0, 60.0)
            #plt.axhline(100)
            plt.plot(max_pos+t[0], np.array(high)[max_pos], 'o', markersize=4)
            plt.plot(min_pos+t[0],  np.array(low)[min_pos], '*', markersize=4)
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
        #print('qfq', self.date)
        #print('date                  num   high    low    avg ->   high    low    avg')
        for j in range(len(self.date)):
            fq_d = datetime.datetime.strptime(self.date[j], '%Y%m%d')
            for i in range(len(tmp)):
                d = datetime.datetime.strptime(tmp[i][0], '%Y-%m-%d')
                if d<fq_d:
                    #print('%s %5d %.3f %.3f %.3f -> ' % (d, i, float(tmp[i][1]), float(tmp[i][2]), float(tmp[i][3])), end='')
                    '''
                    tmp[i][3] = self.fq(tmp[i][3], j)
                    tmp[i][4] = self.fq(tmp[i][4], j)
                    tmp[i][9] = self.fq(tmp[i][9], j)
                    tmp[i][10] = self.fq(tmp[i][10], j)
                    '''
                    tmp[i][1] = self.fq(tmp[i][1], j)
                    tmp[i][2] = self.fq(tmp[i][2], j)
                    #tmp[i][3] = self.fq(tmp[i][3], j)
                    #print(' %.3f %.3f %.3f' % (float(tmp[i][1]), float(tmp[i][2]), float(tmp[i][3])))
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

def draw_mix(t, p, b, c):
    # curve fit
    z1 = np.polyfit(t, b, 14)
    p1 = np.poly1d(z1)
    #print(p1)
    yvals = p1(t)

    # peak value
    num_peak_3 = signal.find_peaks(yvals, distance=10) #distance表极大值点的距离至少大于等于10个水平单位
    yyyd = np.polyder(p1, 1)
    print('yyyd ', yyyd)
    print('yyyd.r ', yyyd.r)

    # https://finthon.com/matplotlib-color-list/
    print('the number of peaks is ' + str(len(num_peak_3[0])))
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(t, b, "blue", label="benefit")
    ax1.plot(t, c, "dodgerblue", label="cost")
    ax1.plot(t, yvals, 'gray',label='polyfit values')
    for ii in range(len(num_peak_3[0])):
        ax1.plot(num_peak_3[0][ii]+t[0], yvals[num_peak_3[0][ii]],'*',markersize=10)
    ax1.set_title("cost & benefit " + begin_date + ' ~ ' + end_date)
    ax1.set_ylabel('RMB')
    ax1.legend(loc='best')
    ax1.axhline(0)

    ax2 = ax1.twinx()
    ax2.plot(t, p, "mistyrose", label="price")
    ax2.set_ylabel('RMB(avg price)')
    ax2.legend(loc='best')
    ax2.axhline(0)

    plt.xlabel('day')
    #plt.ylim(0, 200)
    plt.show()

    print(yvals[signal.argrelextrema(yvals, np.greater)]) #极大值的y轴, yvals为要求极值的序列
    print(signal.argrelextrema(yvals, np.greater)) #极大值的x轴
    peak_high_ind = signal.argrelextrema(yvals, np.greater)[0] #极大值点，改为np.less即可得到极小值点
    peak_low_ind  = signal.argrelextrema(yvals, np.less)[0] #极大值点，改为np.less即可得到极小值点

    plt.plot(t, b, '*',label='original values')
    plt.plot(t, yvals, 'r',label='polyfit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.legend(loc=4)
    plt.title('polyfitting')
    plt.plot(peak_high_ind+t[0], yvals[peak_high_ind], 'o', markersize=10)
    plt.plot(peak_low_ind+t[0],  yvals[peak_low_ind],  '*', markersize=10)
    plt.show()

def max_min(data):
    diff = np.diff(np.sign(np.diff(data)))
    max_pos = np.where(diff == -2)[0] + 1
    min_pos = np.where(diff ==  2)[0] + 1
    return max_pos, min_pos

def cal_energy(data, begin_date, end_date):
    t = []
    date = []
    high = []
    low = []
    count = 0

    begin_d    = datetime.datetime.strptime(begin_date, '%Y%m%d')
    end_d      = datetime.datetime.strptime(end_date, '%Y%m%d')
    #for i in range(len(data)-1, -1, -1):
    for i in range(0, len(data), 1):
        tmp = data[i]
        d = datetime.datetime.strptime(tmp[0], '%Y-%m-%d')
        if d>end_d:
            break
        if d>=begin_d:
            count +=1
            t.append(count)
            date.append(tmp[0])
            high.append(round(float(tmp[1]),2))
            low.append(round(float(tmp[2]),2))

    #max_pos, tmp_pos = max_min(high)
    #tmp_pos, min_pos = max_min(low)

    max_pos = signal.argrelextrema(np.array(high), np.greater)[0] #极大值点，改为np.less即可得到极小值点
    min_pos  = signal.argrelextrema(np.array(low), np.less)[0] #极大值点，改为np.less即可得到极小值点

    total_cost = 0    # 累计花费, 就是当前的持仓花费
    max_cost = 0      # 最高花费
    total_benefit = 0 # 累计收益
    total_num = 0     # 累计持股
    max_num = 0
    print('from sell:')
    print('')
    for j in range(0, len(max_pos), 1):
        print(date[max_pos[j]], high[max_pos[j]])
        total_cost = 0    # 累计花费, 每一个卖点，都重新计算当前还存在的买点，求和就是对应这个卖点所在时间点最大的买入量
        total_num = 0     # 累计持股
        for i in range(0, len(min_pos), 1):
            #已经卖出
            if min_pos[i]==-1: continue

            # 卖点在买点前面
            if max_pos[j]<=min_pos[i]: continue

            total_cost += low[min_pos[i]]
            print('    buy %s %.2f' % (date[min_pos[i]], low[min_pos[i]]))
            if total_cost > max_cost: max_cost = total_cost
            total_num += 1
            if total_num > max_num: max_num = total_num

            delta = high[max_pos[j]]-low[min_pos[i]]

            # 只要大于0.05就抛出
            if delta/low[min_pos[i]] >= float(sys.argv[4]):
                delta = low[min_pos[i]] * float(sys.argv[4])
                total_benefit += delta
                total_cost -= low[min_pos[i]]
                total_num -= 1
                print('    %d %s %.2f -> %s %.2f delta %.2f total_b %.2f total_c %.2f(%d) max_cost %.2f(%d)' % (min_pos[i], date[min_pos[i]], low[min_pos[i]], date[max_pos[j]], high[max_pos[j]], delta, total_benefit, total_cost, total_num, max_cost, max_num) )

                # 卖出后，把对应的买点置位无效，也就是只买卖一次
                # 有效的买点会继续在下一次作为cost累计
                min_pos[i]=-1
                continue
        print('    %s total_b %.2f total_c %.2f(%d) max_cost %.2f(%d)' % (date[max_pos[j]], total_benefit, total_cost, total_num, max_cost, max_num) )

    print('')
    print('from buy:')
    print('')
    min_pos  = signal.argrelextrema(np.array(low), np.less)[0] #极大值点，改为np.less即可得到极小值点
    total_cost = 0    # 累计花费
    total_benefit = 0 # 累计收益
    total_num = 0     # 累计持股
    max_cost = 0      # 最高花费
    for i in range(0, len(min_pos), 1):
        print(date[min_pos[i]], 'buy', low[min_pos[i]])
        total_cost += low[min_pos[i]]
        total_num += 1
        benefit = 9999
        for j in range(0, len(max_pos), 1):
            if max_pos[j]<=min_pos[i]: continue
            delta = high[max_pos[j]]-low[min_pos[i]]

            # 总是选择高位里面最差的点抛出
            '''
            if delta < benefit:
                benefit = delta
                total_num -= 1
            '''

            # 只要大于0.05就抛出
            if delta/low[min_pos[i]] >= float(sys.argv[4]):
                benefit = delta
                total_cost -= low[min_pos[i]]
                total_num -= 1
                print('   -> %s %.2f %.2f %.1f%% sell succ' % (date[max_pos[j]], high[max_pos[j]], delta, delta/low[min_pos[i]]*100))
                break

            print('   %s %.2f %.2f %.1f%% sell fail' % (date[max_pos[j]], high[max_pos[j]], delta, delta/low[min_pos[i]]*100))
        if benefit == 9999:
            benefit = 0
        total_benefit += benefit
        print('   benefit/cost %.2f/%.2f(%.2f%%) total_b/c %.2f/%.2f(hold %d)' % (benefit, low[min_pos[i]], benefit/low[min_pos[i]]*100, total_benefit, total_cost, total_num) )

    show = 1
    if show==1:
        plt.figure()
        plt.plot(t, high, "orange", label="high")
        plt.plot(t, low, "green", label="low")
        plt.legend(loc='best')
        plt.title(" daily " + begin_date + " ~ " + end_date)
        plt.xlabel('day')
        plt.ylabel('RMB')
        plt.plot(max_pos+t[0], np.array(high)[max_pos], 'o', markersize=4)
        plt.plot(min_pos+t[0],  np.array(low)[min_pos], '*', markersize=4)
        plt.show()

    return t, high, low, max_pos, min_pos


if __name__ == "__main__":
    filename = sys.argv[1]
    #check_qfq(filename)

    begin_date = sys.argv[2]
    end_date   = sys.argv[3]

    stock = Stock(filename)
    #print_price(stock.data,     '20140701', '20140731')
    #print_price(stock.qfq_data, '20140701', '20140731')
    #t,p = stock.draw(begin_date, end_date, 1)
 
    cal_energy(stock.qfq_data, begin_date, end_date)

    '''
    sim = Sim()
    sim.set(0.96, 1.04, float(sys.argv[4]))
    r = sim.simulate(stock.qfq_data, begin_date, end_date)
    #sim.output()
    t,b,c = sim.draw(1)

    #draw_mix(t, p, b, c)
    '''
