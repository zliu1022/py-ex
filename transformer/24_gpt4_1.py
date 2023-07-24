#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools

def apply_operation(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b if b != 0 else None

def eval_expression(nums, ops):
    a, b, c, d = nums
    op1, op2, op3 = ops

    results = []

    results.append(apply_operation(apply_operation(a, b, op1), apply_operation(c, d, op3), op2))
    results.append(apply_operation(a, apply_operation(apply_operation(b, c, op2), d, op3), op1))
    results.append(apply_operation(a, apply_operation(b, apply_operation(c, d, op3), op2), op1))

    return results

numbers = [6, 2, 8, 4]
operators = ['+', '-', '*', '/']
solutions = set()

for num_permutation in itertools.permutations(numbers):
    for op_permutation in itertools.product(operators, repeat=3):
        for result in eval_expression(num_permutation, op_permutation):
            if result is not None and abs(result - 24) < 1e-6:
                solutions.add((num_permutation, op_permutation))

for solution in solutions:
    print(f"({solution[0][0]} {solution[1][0]} {solution[0][1]}) {solution[1][1]} ({solution[0][2]} {solution[1][2]} {solution[0][3]}) = 24")

