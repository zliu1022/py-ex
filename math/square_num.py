#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

print('')

arr = []
arr_adv = []

begin=11
end = 99

for i in range(begin,end,1):
    i_1 = i//10
    i_2 = i - i_1*10
    if i_1 != i_2: continue
    for j in range(begin,end,1):
        j_1 = j//10
        j_2 = j - j_1*10
        if j_1 != j_2: continue

        u = i * j
        v = (i * j) // 100
        arr.append([i, j, u, v])
        print(i, j, u, v)

        v_adv = i_1*j_1 + (i_1*j_2)//10 + (j_1*i_2)//10
        arr_adv.append([i, j, u, v_adv])

arr.sort(key=lambda x: (x[3], x[0], x[1]))

