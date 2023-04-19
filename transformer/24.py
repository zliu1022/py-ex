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

def evaluate_expression(num_permutation, op_permutation):
    for paren_permutation in itertools.product(range(3), repeat=2):
        expression = list(num_permutation)
        ops = list(op_permutation)

        indices = list(paren_permutation) + [2]

        for index in indices:
            result = calculate(expression[index], expression[index+1], ops[index])
            if result is None:
                continue
            expression[index+1] = result
            del expression[index]
            del ops[index]
            if len(expression) == 1:
                break
        if len(expression) == 1 and round(expression[0], 5) == 24:
            return True
    return False

found_solution = False

for num_permutation in itertools.permutations(numbers):
    for op_permutation in itertools.product(operations, repeat=3):
        if evaluate_expression(num_permutation, op_permutation):
            found_solution = True
            print("Solution found:")
            print("Numbers:", num_permutation)
            print("Operations:", op_permutation)
            break

if not found_solution:
    print("No solution found.")

