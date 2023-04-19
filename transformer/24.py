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

def evaluate_expression(nums, ops):
    if len(nums) == 1:
        return round(nums[0], 5) == 24

    for i in range(len(ops)):
        a = nums[i]
        b = nums[i + 1]
        op = ops[i]

        result = calculate(a, b, op)
        if result is None:
            continue

        new_nums = nums[:i] + [result] + nums[i + 2:]
        new_ops = ops[:i] + ops[i + 1:]

        if evaluate_expression(new_nums, new_ops):
            return True

    return False

found_solution = False

for num_permutation in itertools.permutations(numbers):
    for op_permutation in itertools.product(operations, repeat=3):
        if evaluate_expression(list(num_permutation), list(op_permutation)):
            found_solution = True
            print("Solution found:")
            print("Numbers:", num_permutation)
            print("Operations:", op_permutation)
            break

if not found_solution:
    print("No solution found.")

