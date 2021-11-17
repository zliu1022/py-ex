import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy import signal
 
def prepare(data):
    data = data[1:-1].split(',')
    xs, ys = [], []
    for i in data:
        if 'x:' in i:
            x = i.strip().split(' ')[1]
            y = i.strip().split(' ')[3]
            xs.append(float(x) * 100 + 100)
            ys.append(float(y) * 100)
    return np.asarray(xs), np.asarray(ys)
 
def extrema(x, yvals):
    print('Extreme max x:', x[signal.argrelextrema(yvals, np.greater)[0]])
    print('Extreme min x:', x[signal.argrelextrema(yvals, np.less)[0]])
 
    plt.plot(x[signal.argrelextrema(yvals, np.greater)[0]], yvals[signal.argrelextrema(yvals, np.greater)], 'o', markersize=10) #极大值点
    plt.plot(x[signal.argrelextrema(yvals, np.less)[0]], yvals[signal.argrelextrema(yvals, np.less)],'+', markersize=10) #极小值点
 
def polyder(yvals):
    yyyd = np.polyder(yvals, 1) # 1表示一阶导
    print('grad=0:', yyyd)
 
flag = {
    '1': 'resultDataSmallWave',
    '2': 'resultDataReady',
    '3': 'resultDataTest',
    '4': 'resultDataNextWave',
    '5': 'resultDataSmall'
    }
 
with open('checkResultData.json','r',encoding='utf-8') as f:
    file = json.load(f)
    x, y = prepare(file[flag['2']])
 
# 最小二乘法计算拟合多项式系数
z = np.polyfit(x, y, 20)
# yvals = np.polyval(z, x)
p = np.poly1d(z)
yvals = p(x)
 
plt.legend(loc=4)
plt.plot(x, y, '*', label='original values')
plt.plot(x, yvals,'r',label='polyfit values')
extrema(x, yvals)
plt.show()
