#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
def solve_24_1(nums):
    for a, b, c, d in itertools.permutations(nums):
        for op1, op2, op3 in itertools.product(["+", "-", "*", "/"], repeat=3):
            try:
                expr = f"(({a} {op1} {b}) {op2} {c}) {op3} {d}"
                if abs(eval(expr) - 24) < 1e-6:
                    return expr
            except ZeroDivisionError:
                pass
    return None

#print(solve_24([1, 2, 3, 4]))

def solve_24(nums, target):
    results = []
    for a, b, c, d in itertools.permutations(nums):
        for op1, op2, op3 in itertools.product(["+", "-", "*", "/"], repeat=3):
            try:
                expr = f"(({a} {op1} {b}) {op2} {c}) {op3} {d}"
                if abs(eval(expr) - target) < 1e-6:
                    results.append(expr)
            except ZeroDivisionError:
                pass
    return results

print(solve_24([1, 2, 3, 4], 24))
