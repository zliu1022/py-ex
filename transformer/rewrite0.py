#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

def extract_year(text):
    for pattern, offset in [("%Y年", 0), ("%Y中报", 0), ("%Y季报", 0)]:
        pos = text.find(pattern[2:])
        if pos != -1:
            return str(datetime.strptime(text, pattern).year)
    try:
        y = datetime.strptime(text, "%Y-%m-%d").year
        return str(y)
    except:
        return "1900"

def test_extract_year():
    def run_test(test_input, expected_output):
        result = extract_year(test_input)
        print('{} Input {} Expected {} Actual {}'.format(
            'OK ' if result == expected_output else 'ERR',
            test_input, expected_output, result))

    run_test("2021年", "2021")
    run_test("2021中报", "2021")
    run_test("2021季报", "2021")
    run_test("2021-06-30", "2021")
    run_test("No match found", "1900")

test_extract_year()
