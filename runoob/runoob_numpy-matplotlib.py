# -*- coding: utf-8 -*-
import numpy as np 
from matplotlib import pyplot as plt 
 
def t1():
    x = np.arange(1,11) 
    y =  2  * x +  5 
    plt.title("Matplotlib demo") 
    plt.xlabel("x axis caption") 
    plt.ylabel("y axis caption") 
    plt.plot(x,y)
    plt.show()


def t2():
    x = np.arange(1,11)
    y =  2  * x +  5
    plt.title("Matplotlib demo")
    plt.xlabel("x axis caption")
    plt.ylabel("y axis caption")
    plt.plot(x,y,"ob")
    plt.show()

def t3():
    # 计算正弦曲线上点的 x 和 y 坐标
    x = np.arange(0,  3  * np.pi,  0.1)
    y = np.sin(x)
    plt.title("sine wave form")
    # 使用 matplotlib 来绘制点
    plt.plot(x, y)
    plt.show()

def t4():
    # 计算正弦和余弦曲线上的点的 x 和 y 坐标
    x = np.arange(0,  3  * np.pi,  0.1)
    y_sin = np.sin(x)
    y_cos = np.cos(x)
    # 建立 subplot 网格，高为 2，宽为 1
    # 激活第一个 subplot
    plt.subplot(2,  1,  1)
    # 绘制第一个图像
    plt.plot(x, y_sin)
    plt.title('Sine')
    # 将第二个 subplot 激活，并绘制第二个图像
    plt.subplot(2,  1,  2)
    plt.plot(x, y_cos)
    plt.title('Cosine')
    # 展示图像
    plt.show()

def t5():
    x =  [5,8,10]
    y =  [12,16,6]
    x2 =  [6,9,11]
    y2 =  [6,15,7]
    plt.bar(x, y, align =  'center')
    plt.bar(x2, y2, color =  'g', align =  'center')
    plt.title('Bar graph')
    plt.ylabel('Y axis')
    plt.xlabel('X axis')
    plt.show()

def t6():
    a = np.array([22,87,5,43,56,73,55,54,11,20,51,5,79,31,27])
    np.histogram(a,bins =  [0,20,40,60,80,100])
    hist,bins = np.histogram(a,bins =  [0,20,40,60,80,100])
    print (hist)
    print (bins)

def t7():
    a = np.array([22,87,5,43,56,73,55,54,11,20,51,5,79,31,27])
    plt.hist(a, bins =  [0,20,40,60,80,100])
    plt.title("histogram")
    plt.show()

if __name__ == "__main__":
    t7()

