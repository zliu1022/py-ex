#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import random
from functools import reduce

def evaluate_expression(expr):
    try:
        return eval(expr)
    except (SyntaxError, ZeroDivisionError):
        return None

def generate_digits():
    return [random.randint(1, 9) for _ in range(4)]

def find_all_solutions(digits):
    operators = ['+', '-', '*', '/']
    all_combinations = []

    for num_permutation in itertools.permutations(digits):
        for op_permutation in itertools.product(operators, repeat=3):

            bracket_combinations = [
                '({0}{4}{1}){5}{2}{6}{3}',
                '{0}{4}({1}{5}{2}){6}{3}',
                '{0}{4}{1}{5}({2}{6}{3})',
                '({0}{4}{1}){5}({2}{6}{3})',
                '({0}{4}{1}{5}{2}){6}{3}',
                '{0}{4}({1}{5}{2}{6}{3})',
            ]

            for with_brackets in bracket_combinations:
                temp_expression = with_brackets.format(*num_permutation, *op_permutation)
                result = evaluate_expression(temp_expression)
                if result is not None and abs(result - 24) < 1e-9:
                    all_combinations.append(temp_expression)
    return set(all_combinations)

def main():
    digits = generate_digits()

    while True:
        print(f"Digits: {digits}")
        user_input = input("Enter your expression (q to quit, ! to generate new digits, !! to input new digits, ? to find all solutions): ")

        if user_input.lower() == 'q':
            break
        elif user_input == '!':
            digits = generate_digits()
        elif user_input == '!!':
            digits = list(map(int, input("Enter 4 digits between 1 and 9, separated by space: ").split()))
            if len(digits) != 4 or not all(1 <= d <= 9 for d in digits):
                print("Invalid input. Generating random digits.")
                digits = generate_digits()
        elif user_input == '?':
            solutions = find_all_solutions(digits)
            print("All possible solutions:")
            for solution in solutions:
                print(solution)
        else:
            result = evaluate_expression(user_input)
            if result is not None and abs(result - 24) < 1e-9:
                print("Correct!")
                digits = generate_digits()
            else:
                print("Incorrect. Try again.")

if __name__ == "__main__":
    main()

