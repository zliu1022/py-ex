#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
mongodb, db_name库，表格q，筛选 "qtype": "死活题"
1. 随机选取一道题目
- 字段"prepos"，黑子和白子的初始位置
- "blackfirst": true，表示这道题目是黑先
- "level": "9K"，题目难度9K
- "answers"是这道题目的答案，字段ty：1正解，2变化，3失败，4淘汰；字段st：2审核完毕，1等待审核
2. 把题目显示在围棋棋盘上
- 根据题目里初始位置计算需要显示的棋盘大小
- 棋盘周围要预留空隙, 并标注坐标
- 显示按钮“下一道”，“提示”
- 提示信息区域，显示最终用户做题的结果
- 标题显示题目的publicid，黑先还是白先
3.用户鼠标点击后，根据先走的颜色，显示对应颜色的棋子
- 根据围棋的规则，计算是否出现对方棋子没有气的情况，需要提去，然后判断本方颜色的棋子有没有出现没有“气”的情况，不允许本方颜色的棋子有没有出现没有“气”的情况
- 如果走的位置不是正解，则提示“错误”，等待2秒消失后再允许点击棋盘
- 如果走的位置正确，则根据答案，显示下一步的棋子
- 如果用户点击“提示”，则在第一步的位置，显示一个红色圆圈
- 如果用户点击“下一道”，则选取下一道题目显示
'''

import random
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox
from config import db_name

# Function to convert Go board coordinates (e.g., 'cs') to (row, column)
def coord_to_position(coord):
    columns = 'abcdefghijklmnopqrst'
    col_letter, row_letter = coord[1], coord[0]
    col = columns.index(col_letter)
    row = columns.index(row_letter)
    row = board_size - row - 1  # Adjust row index to match the display
    return row, col

# Function to convert (row, column) to Go board coordinates
def position_to_coord(row, col):
    columns = 'abcdefghijklmnopqrst'
    row_letter = columns[board_size - row - 1]
    col_letter = columns[col]
    return col_letter + row_letter

def draw_stone(row, col, color):
    x = margin + col * cell_size
    y = margin + row * cell_size
    r = cell_size / 2 - 2
    stone = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
    return stone

def draw_hint(coord):
    row, col = coord_to_position(coord)
    x = margin + col * cell_size
    y = margin + row * cell_size
    r = cell_size / 2 - 2
    hint = canvas.create_oval(x - r, y - r, x + r, y + r, outline='red', width=2)
    return hint

def get_expected_coords(move_number):
    expected_coords = set()
    for answer in answers:
        if len(answer['p']) >= move_number:
            expected_coords.add(answer['p'][move_number - 1])
    return expected_coords

def get_expected_next_coords(user_moves):
    expected_coords = set()
    for answer in answers:
        if answer['p'][:len(user_moves)] == user_moves:
            if len(answer['p']) > len(user_moves):
                expected_coords.add(answer['p'][len(user_moves)])
    return expected_coords

def show_error_message():
    error_window = tk.Toplevel(root)
    error_window.title("Result")
    tk.Label(error_window, text="错误！(Incorrect!)", font=('Arial', 16)).pack(padx=20, pady=20)
    error_window.after(2000, error_window.destroy)

def get_group(row, col):
    color = board[row][col]['color']
    group = set()
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        if (r, c) not in group:
            group.add((r, c))
            # Check the four neighbors
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board_size and 0 <= nc < board_size:
                    if board[nr][nc] is not None and board[nr][nc]['color'] == color:
                        stack.append((nr, nc))
    return group

def has_liberties(group):
    for r, c in group:
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < board_size and 0 <= nc < board_size:
                if board[nr][nc] is None:
                    return True
    return False

def remove_group(group):
    for r, c in group:
        canvas.delete(board[r][c]['stone'])
        canvas.delete(board[r][c]['label'])
        board[r][c] = None

def on_board_click(event):
    global current_color, move_number, user_moves, black_captures, white_captures
    x_click = event.x - margin
    y_click = event.y - margin
    if x_click < -cell_size / 2 or y_click < -cell_size / 2 or x_click > canvas_size - margin or y_click > canvas_size - margin:
        # Click outside the board area
        return

    # Calculate approximate grid position from click
    col_click = x_click / cell_size
    row_click = y_click / cell_size
    col = int(round(col_click))
    row = int(round(row_click))

    if not (0 <= row < board_size and 0 <= col < board_size):
        # Click is outside the board grid
        return

    # Check if the position is unoccupied
    if board[row][col] is not None:
        messagebox.showwarning("Invalid move", "That position is occupied.")
        return

    # Get expected coordinates for the current move number
    expected_coords = get_expected_coords(move_number)
    tolerance = cell_size / 2  # Allowable distance from the correct point
    match_found = False
    for coord in expected_coords:
        exp_row, exp_col = coord_to_position(coord)
        x_expected = exp_col * cell_size
        y_expected = exp_row * cell_size
        dx = x_click - x_expected
        dy = y_click - y_expected
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= tolerance:
            # Correct move found within tolerance
            row, col = exp_row, exp_col  # Correct the position to the expected one
            coord = coord  # Use the expected coordinate
            match_found = True
            break

    if not match_found:
        show_error_message()
        return  # Allow the user to try again without changing state

    # Place the stone tentatively
    stone = draw_stone(row, col, current_color)
    label = canvas.create_text(margin + col * cell_size, margin + row * cell_size, text=str(move_number), fill='white')
    board[row][col] = {'color': current_color, 'stone': stone, 'label': label}

    # Perform captures
    opponent_color = 'white' if current_color == 'black' else 'black'
    captured_stones = 0

    # Check adjacent positions for opponent stones
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            if board[nr][nc] is not None and board[nr][nc]['color'] == opponent_color:
                opponent_group = get_group(nr, nc)
                if not has_liberties(opponent_group):
                    remove_group(opponent_group)
                    captured_stones += len(opponent_group)
                    # 记录提子数量
                    if current_color == 'black':
                        black_captures += len(opponent_group)
                    else:
                        white_captures += len(opponent_group)

    # Now check if own group has liberties
    own_group = get_group(row, col)
    if not has_liberties(own_group):
        # Invalid move: self-capture not allowed
        # Remove the placed stone
        canvas.delete(board[row][col]['stone'])
        canvas.delete(board[row][col]['label'])
        board[row][col] = None
        show_error_message()
        return

    # The move is valid, proceed

    # Update move number and user moves
    user_moves.append(coord)
    move_number += 1

    # Switch color
    current_color = 'white' if current_color == 'black' else 'black'

    # Clear previous hints
    for item in hint_items:
        canvas.delete(item)
    hint_items.clear()

    # Check if the user's sequence matches any of the answers
    matched_answers = []
    for answer in answers:
        answer_moves = answer['p']
        if user_moves == answer_moves[:len(user_moves)]:
            matched_answers.append(answer)
            if len(user_moves) == len(answer_moves):
                messagebox.showinfo("Result", "正确！(Correct!)")
                # Prepare for next problem or reset
                return  # End the game
            break  # Found a matching answer
    else:
        # No matching answer; allow the user to continue
        pass

    # Display hints for the next expected moves
    next_expected_coords = get_expected_next_coords(user_moves)
    for coord in next_expected_coords:
        hint_items.append(draw_hint(coord))

def clear_board():
    global board, user_moves, move_number, current_color, hint_items, black_captures, white_captures
    # Clear all stones from the canvas
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] is not None:
                canvas.delete(board[row][col]['stone'])
                canvas.delete(board[row][col]['label'])
                board[row][col] = None
    # Clear hints
    for item in hint_items:
        canvas.delete(item)
    hint_items.clear()
    # Clear pre-set stones
    canvas.delete('preset_stone')
    user_moves = []
    move_number = 1
    current_color = 'black'  # Default to black, will be set in load_problem()
    black_captures = 0
    white_captures = 0

def load_problem():
    global problem, prepos, blackfirst, level, answers, current_color, info_label, board
    # Randomly select a problem
    problem = random.choice(problems)

    # Extract necessary data
    prepos = problem.get('prepos', {})
    blackfirst = problem.get('blackfirst', True)
    level = problem.get('level', 'N/A')
    answers = problem.get('answers', [])
    problem_no = problem.get('publicid', 'N/A')
    ty = problem.get('qtype', 'N/A')

    # Clear the board and reset variables
    clear_board()

    # Set current color
    current_color = 'black' if blackfirst else 'white'

    # Update window title
    root.title(f"Level {level} - {ty} - {'Black' if blackfirst else 'White'} first - No.{problem_no}")

    # Update info label
    if info_label:
        info_label.config(text=f"Level: {level} | {'Black' if blackfirst else 'White'} plays first | No.{problem_no}")
    else:
        info_label = tk.Label(root, text=f"Level: {level} | {'Black' if blackfirst else 'White'} plays first | No.{problem_no}")
        info_label.pack()

    # Redraw pre-set stones
    for color, positions in prepos.items():
        for coord in positions:
            row, col = coord_to_position(coord)
            x = margin + col * cell_size
            y = margin + row * cell_size
            r = cell_size / 2 - 2
            stone_color = 'black' if color == 'b' else 'white'
            stone = canvas.create_oval(x - r, y - r, x + r, y + r, fill=stone_color, tags='preset_stone')
            label = None  # 预置的棋子没有标号
            board[row][col] = {'color': stone_color, 'stone': stone, 'label': label}

    # Display hint for the correct moves
    # Get the first move from the first answer as a hint
    first_move = None
    if answers:
        for ans in answers:
            if ans['ty'] == 1 and ans['st'] == 2:
                first_move = ans['p'][0]
        if first_move == None:
            print(f'Warning no answers ty==1 st==2')
            first_move = 'jj'
        hint_items.append(draw_hint(first_move))

# Add a "Next Problem" button
def on_next_problem():
    load_problem()

# Draw the Go board
def draw_board(canvas, board_size, margin, cell_size):
    for i in range(board_size):
        # Vertical lines
        x = margin + i * cell_size
        canvas.create_line(x, margin, x, canvas_size - margin)
        # Horizontal lines
        y = margin + i * cell_size
        canvas.create_line(margin, y, canvas_size - margin, y)

if __name__ == "__main__":
    # Connect to MongoDB and retrieve problems
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db['q']
    problems_cursor = collection.find({"status":2, "qtype": "死活题", "level":"9K"})
    problems = list(problems_cursor)
    if not problems:
        raise Exception("No problems found")

    canvas_size = 800
    margin = 40  # Margin around the board
    board_size = 19
    cell_size = (canvas_size - 2 * margin) / (board_size - 1)

    # Initialize variables to store game state
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    user_moves = []
    current_color = None
    move_number = 1
    hint_items = []
    prepos = {}
    blackfirst = True
    level = 'N/A'
    answers = []
    problem = {}
    info_label = None
    black_captures = 0
    white_captures = 0

    # Initialize GUI
    root = tk.Tk()
    root.title("Go Problem Viewer")
    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
    canvas.pack()
    draw_board(canvas, board_size, margin, cell_size)
    next_button = tk.Button(root, text="下一题 (Next Problem)", command=on_next_problem)
    next_button.pack(pady=5)

    # Bind the click event
    canvas.bind("<Button-1>", on_board_click)

    # Load the initial problem
    load_problem()

    root.mainloop()
