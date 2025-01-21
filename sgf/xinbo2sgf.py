#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

def print_json(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if prefix:
                key = f"{prefix}.{key}"
            print_json(value, key)
    else:
        print(f"{prefix}: {obj}")

def data2sgf(game_data, id_item):
    # gamekey: normal-20240303085359-9428
    game_date = game_data.get('gamekey', '').split('-')[1][0:8]
    file_date = game_date[0:4] + '-' + game_date[4:6] + '-' + game_date[6:8]

    # 提取落子信息
    move_data = game_data.get('pu', '')

    # 创建 SGF 文件内容
    # https://www.red-bean.com/sgf/properties.html#GN
    sgf_content = '(;FF[4]GM[1]SZ[19]KM[7.5]AP[Python]GN[新博' + str(id_item) + ']\n'

    # 添加黑白方信息
    black_name = game_data.get('blackname', 'Unknown')
    white_name = game_data.get('whitename', 'Unknown')
    black_level = game_data.get('black_level', 'Unknown')
    white_level = game_data.get('white_level', 'Unknown')
    sgf_content += f'PB[{black_name}-{black_level}]PW[{white_name}-{white_level}]\n'

    # 添加游戏结果
    game_result = game_data.get('gameresult', '')
    sgf_content += f'RESULT[{game_result}]\n'

    move_num = 0
    coord_board="ABCDEFGHJKLMNOPQRST"
    coord_sgf  ="abcdefghijklmnopqrs"
    moves = move_data.split(';')
    for move in moves:
        if move:
            color, pos = move.split('[')
            if pos[0:2]=="WW":
                sgf_content += f';{color}[]'
            else:
                x = coord_sgf[coord_board.find(pos[0])]
                y = coord_sgf[coord_board.find(pos[1])]
                sgf_content += f';{color}[{x}{y}]'

        move_num += 1
        if move_num % 10 == 0:
            sgf_content += "\n"

    # 结束 SGF 文件内容
    sgf_content += ')'

    if black_name == "刘欣来":
        turn = "执黑"
        # 新博结果总是标注胜利方的结果
        if game_result[0] == '白':
            game_result = game_result.replace('胜', '败')
        game_result = game_result[1:]
    else:
        turn = "执白"
        if game_result[0] == '黑':
            game_result = game_result.replace('胜', '败')
        game_result = game_result[1:]

    file_name = file_date + '，' + turn + game_result + '.sgf'

    return sgf_content, file_name

def xinbo(id_item):
    url = "https://duiyi.xbkids.cn/wx/pu/getpudata.php?type=0&pinglunid=&pid=" + id_item
    resp = requests.get(url)
    with open(f"game-xinbo.html", "w") as f:
        f.write(resp.text)
    game_data = json.loads(resp.text)
    #print_json(game_data)
    sgf_content,file_name = data2sgf(game_data, id_item)

    # 将 SGF 内容保存到文件
    with open(file_name, 'w') as sgf_file:
        sgf_file.write(sgf_content)
    print(f"{file_name} 已生成")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        id_item = sys.argv[1]
    else:
        id_item = input("Input id (ex. 446586451): ")
    if len(id_item) !=0 :
        xinbo(id_item)

