#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import random

def calculate(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b if b != 0 else None

def find_expressions(numbers, target=24):
    operators = ['+', '-', '*', '/']
    for num_permutation in itertools.permutations(numbers):
        for op_permutation in itertools.product(operators, repeat=len(numbers) - 1):
            a, b, c, d = num_permutation
            op1, op2, op3 = op_permutation

            temp1 = calculate(calculate(a, b, op1), calculate(c, d, op3), op2)
            if temp1 == target:
                print(f"({a} {op1} {b}) {op2} ({c} {op3} {d}) = {target}")

            temp2 = calculate(calculate(a, calculate(b, c, op2), op1), d, op3)
            if temp2 == target:
                print(f"({a} {op1} ({b} {op2} {c})) {op3} {d} = {target}")

            temp3 = calculate(a, calculate(b, calculate(c, d, op3), op2), op1)
            if temp3 == target:
                print(f"{a} {op1} ({b} {op2} ({c} {op3} {d})) = {target}")

def generate_random_numbers():
    return [random.randint(1, 9) for _ in range(4)]

#numbers = generate_random_numbers()
numbers = [6, 2, 8, 4]

print(f"Generated random numbers: {numbers}")
find_expressions(numbers)

