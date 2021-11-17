#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
buhuan=0 #不换
huan=0 #换

for i in range(100000): #这意味着我们要做1000次实验
    car = random.choice([1,2,3]) #汽车随机出现在三扇门之中
    challenger = random.choice([1,2,3]) #挑战者随机选择了一扇门
    #以下五行代码：主持人随机选择一扇门，这扇门不是挑战者选择的门，也不是汽车所在的门
    host_list = [1,2,3]
    host_list.remove(challenger)
    if car in host_list:
        host_list.remove(car)
    host = random.choice(host_list)
    
    if challenger == car:
        buhuan = buhuan+1 #如果挑战者一开始选的门背后有汽车，那么不换是对的
    else:
        huan = huan+1 #如果挑战者一开始选的门背后没有汽车，那么换是对的
    
print(buhuan)
print(huan)
