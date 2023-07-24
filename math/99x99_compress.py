#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

print('99x99乘法表，只看结果前2位，不到100个，数值的分布')
print('其实能速算前2位基本够了, 我没有想出来怎么速算')
print()
print('进一步，不考虑进位，可以得到另外一个前2位分布')
print('也就是：头头 + 头尾交叉的十位数')


def print_special(arr):
    for i in range(len(arr)):
        if arr[i][0] == 56 and arr[i][1] == 89 or (arr[i][0] == 89 and arr[i][1] == 56):
            print(arr[i])

def print_arr(arr):
    v_only = 0
    v_count = 0
    for i in range(len(arr)):
        if arr[i][3] != v_only:
            if v_count!=0:
                print(v_count)
            print(arr[i], end=' ')
            v_only = arr[i][3]
            v_count = 1
        else:
            v_count += 1
    print(v_count)
    print()

arr = []
arr_adv = []

begin=11
end = 19

for i in range(begin,end,1):
    i_1 = i//10
    i_2 = i - i_1*10
    for j in range(begin,end,1):
        j_1 = j//10
        j_2 = j - j_1*10

        u = i * j
        v = (i * j) // 100
        arr.append([i, j, u, v])

        v_adv = i_1*j_1 + (i_1*j_2)//10 + (j_1*i_2)//10
        arr_adv.append([i, j, u, v_adv])

arr.sort(key=lambda x: (x[3], x[0], x[1]))

arr_adv.sort(key=lambda x: (x[3], x[0], x[1]))

print_arr(arr)
print_arr(arr_adv)

# only print 56x89
print_special(arr)
print_special(arr_adv)
