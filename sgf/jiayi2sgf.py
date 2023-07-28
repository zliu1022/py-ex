#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import math
import re
import sys

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

def get_url(url):
    resp = requests.get(url)
    with open(f"game-jiayi.html", "w") as f:
        f.write(resp.text)
    return resp

def extract_js(resp):
    '''
    with open("game.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    '''
    soup = BeautifulSoup(resp.text, "html.parser")

    scripts = soup.find_all("script")
    javascript_code = [script.string for script in scripts if script.string is not None]
    return javascript_code

def extract_chessmove(js):
    # Find the arr variable
    pattern = re.compile(r'var\s+arr\s*=\s*.*?;', re.DOTALL)
    arr_vars = []
    for code in js:
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
    return chess_moves

def extract_info(js):
    pattern = re.compile(r'var\s+info\s*=\s*({.*?}\s*)', re.DOTALL)
    info_vars = []
    for code in js:
        if code is not None:
            matches = re.findall(pattern, code)
            info_vars.extend(matches)
    info_str = info_vars[0]
    info = json.loads(info_str)

    # Extract the necessary information
    play_time = info['play_time']
    if info['player'] == '2':
        if info['u_id_1'] == '451213':
            player_white = '451213'
            player_black = info['u_id_2']
            player_color = '执白'
        else:
            player_black = '451213'
            player_white = info['u_id_1']
            player_color = '执黑'
    else:
        if info['u_id_1'] == '451213':
            player_black = '451213'
            player_white = info['u_id_2']
            player_color = '执黑'
        else:
            player_white = '451213'
            player_black = info['u_id_1']
            player_color = '执白'

    win_over = abs(float(info['win_over']))
    if win_over == 0:
        if info['winner'] == '451213':
            result_detail = "中盘胜"
        else:
            result_detail = "中盘败"
    else:
        if info['winner'] == '451213':
            result_detail = "胜" + str(win_over) + "子"
        else:
            result_detail = "败" + str(win_over) + "子"

    return play_time, player_black, player_white, player_color, result_detail

def jiayi2sgf(id):
    url = f"https://chess.91goodgo.com/index.php?s=/User/share/&id={id}&uid=451213"

    resp = get_url(url)
    js = extract_js(resp)
    chess_moves = extract_chessmove(js)
    play_time,player_black,player_white,player_color,result_detail = extract_info(js)

    date = play_time.split(' ')[0]
    file_name = f"{date}，{player_color}，{result_detail}.sgf"
    print(id, '->', file_name)

    # Convert the chess moves to the SGF format
    sgf_data = convert_to_sgf(chess_moves, date, player_black, player_white, player_color+result_detail)

    # Save the SGF data to a file
    with open(file_name, "w") as f:
        f.write(sgf_data)

id_arr = [
    "18489279",
    "18440845",
    "18398857",
    "18352522",
    "18224453",
    "18165047",
    "18135742",
    "17979247",
    "17879992",
    "17823401",
    "17521602"
    ]

if __name__ == "__main__":
    for id_item in id_arr:
        jiayi2sgf(id_item)
    quit()
    if len(sys.argv) == 2:
        id_item = sys.argv[1]
    jiayi2sgf(id_item)

