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

def evaluate_expression(a, b, c, d, ops):
    op1, op2, op3 = ops
    results = []

    results.append(calculate(calculate(a, b, op1), calculate(c, d, op2), op3))
    results.append(calculate(calculate(calculate(a, b, op1), c, op2), d, op3))

    for result in results:
        if result is not None and round(result, 5) == 24:
            return True

    return False

found_solution = False

for num_permutation in itertools.permutations(numbers):
    for op_permutation in itertools.product(operations, repeat=3):
        if evaluate_expression(*num_permutation, op_permutation):
            found_solution = True
            print("Solution found:")
            print("Numbers:", num_permutation)
            print("Operations:", op_permutation)
            break

if not found_solution:
    print("No solution found.")

