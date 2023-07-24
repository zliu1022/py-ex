#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import math
import re

def convert_to_sgf(chess_moves, date, player_black, player_white, result_detail):
    # Initialize an empty string to hold the SGF data
    #sgf_data = "("
    sgf_data = f"(;GM[1]FF[4]CA[UTF-8]AP[jiayi2sgf]KM[7.5]SZ[19]DT[{date}]PW[{player_white}]PB[{player_black}]RE[{result_detail}]\n"

    # Define the coordinate system
    coordinates = "abcdefghijklmnopqrs"

    move_num = 0
    # Loop over each move
    for move in chess_moves:
        # Extract the coordinates and color
        x, y, color = move

        # Convert the coordinates to the SGF format
        x_sgf = coordinates[x]
        y_sgf = coordinates[y]

        # Add the move to the SGF data
        if color == 0:  # black
            sgf_data += f";B[{x_sgf}{y_sgf}]"
        else:  # white
            sgf_data += f";W[{x_sgf}{y_sgf}]"

        move_num += 1
        if move_num % 10 == 0:
            sgf_data += "\n"

    # Close the SGF data
    sgf_data += ")"

    return sgf_data

id="17879992"
url = f"https://chess.91goodgo.com/index.php?s=/User/share/&id={id}&uid=451213"
response = requests.get(url)
with open(f"game-{id}.html", "w") as f:
    f.write(response.text)
soup = BeautifulSoup(response.text, "html.parser")
'''
with open("game.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")
'''

# Extract the JavaScript code
scripts = soup.find_all("script")
javascript_code = [script.string for script in scripts if script.string is not None]

# Find the arr variable
pattern = re.compile(r'var\s+arr\s*=\s*.*?;', re.DOTALL)
arr_vars = []
for code in javascript_code:
    matches = re.findall(pattern, code)
    arr_vars.extend(matches)

# Parse the arr variable
arr_str = arr_vars[0][len("var arr = "):-1]
arr = json.loads(arr_str)

# Calculate the chess moves
chess_moves = []
for dic in arr:
    x = (int(dic["step"]) - 1) % 19
    j = math.floor((int(dic["step"]) - 1) / 19)
    color = 0 if int(dic["step_num"]) % 2 else 1
    chess_moves.append((x, j, color))

pattern = re.compile(r'var\s+info\s*=\s*({.*?}\s*)', re.DOTALL)
info_vars = []
for code in javascript_code:
    if code is not None:
        matches = re.findall(pattern, code)
        info_vars.extend(matches)
info_str = info_vars[0]
info = json.loads(info_str)

# Extract the necessary information
play_time = info['play_time']
player_black = '来来' if info['u_id_1'] == '451213' else info['u_id_2']
player_white = info['u_id_2'] if player_black == '来来' else info['u_id_1']
result = 'B+' if info['winner'] == '451213' else 'W+'
win_over = info['win_over']

# Prepare the file name
date = play_time.split(' ')[0]
player_color = '执黑' if player_black == '451213' else '执白'
result_detail = f"胜{win_over}子" if result == 'B+' else f"败{win_over}子"
result_detail = "中盘败" if result_detail == "败0子" else result_detail
file_name = f"{date}，{player_color}，{result_detail}.sgf"

print(play_time, '->', file_name)

# Convert the chess moves to the SGF format
sgf_data = convert_to_sgf(chess_moves, date, player_black, player_white, result_detail)

# Save the SGF data to a file
with open(file_name, "w") as f:
    f.write(sgf_data)

