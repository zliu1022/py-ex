#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools

numbers = [1, 2, 3, 4]
operations = ['+', '-', '*', '/']

def calculate(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            return None
        return a / b

found_solution = False

for num_permutation in itertools.permutations(numbers):
    for op_permutation in itertools.product(operations, repeat=3):
        result = calculate(num_permutation[0], num_permutation[1], op_permutation[0])
        if result is None: continue
        result = calculate(result, num_permutation[2], op_permutation[1])
        if result is None: continue
        result = calculate(result, num_permutation[3], op_permutation[2])
        if result is None: continue
        if round(result, 5) == 24:  # rounding to avoid float imprecision
            found_solution = True
            break

print("Solution found:", found_solution)

