#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import re

def extract_year(text):
    patterns = [
        (r"(\d{4})年", None),
        (r"(\d{4})中报", None),
        (r"(\d{4})季报", None),
        (r"(\d{4})-\d{2}-\d{2}", "%Y"),
    ]

    for pattern, date_format in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                year_str = match.group(1)
                if date_format:
                    return datetime.strptime(year_str, date_format).year
                return int(year_str)
            except IndexError:
                pass

    return 1900

def test_extract_year():
    def run_test(test_input, expected_output):
        result = extract_year(test_input)
        assert result == expected_output, f"Expected {expected_output}, but got {result} for input {test_input}"

    run_test("2021年", 2021)
    run_test("2021中报", 2021)
    run_test("2021季报", 2021)
    run_test("2021-06-30", 2021)
    run_test("No match found", 1900)

test_extract_year()

