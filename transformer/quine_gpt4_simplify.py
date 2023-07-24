#!/usr/bin/env python3
# -*- coding: utf-8 -*-

l = [
    "l = [",
    "    ",
    "]",
    "for i, line in enumerate(l):",
    "    if i == 1:",
    "        print(l[0] + chr(34) + chr(92) + chr(34) + chr(34) + chr(92) + chr(34) + chr(34) + ',')",
    "    else:",
    "        print(line)",
]

for i, line in enumerate(l):
    if i == 1:
        print(l[0] + chr(34) + chr(92) + chr(34) + chr(34) + chr(92) + chr(34) + chr(34) + ',')
    else:
        print(line)

