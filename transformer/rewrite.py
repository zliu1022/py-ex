#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

def extract_year(text):
    for pattern, offset in [("%Y年", 0), ("中报", 0), ("季报", -1), ("-%m-%d", 0)]:
        pos = text.find(pattern[:-2])
        if pos != -1:
            return text[0:pos + offset] if pattern[-1] == "Y" else datetime.strptime(text, pattern).year
    return "1900"
        
def run_test(test_input, expected_output):
    result = extract_year(test_input)
    assert result == expected_output, f"Expected {expected_output}, but got {result} for input {test_input}"

def test_extract_year():
    run_test("2021年", "2021")
    run_test("2021中报", "2021")
    run_test("2021季报", "2020")
    run_test("2021-06-30", 2021)
    run_test("No match found", "1900")

test_extract_year()

