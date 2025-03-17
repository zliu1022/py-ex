#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox
import sys
from bson import ObjectId

# Function to convert Go board coordinates (e.g., 'cs') to (row, column)
def prepos_coord_to_position(coord):
    columns = 'abcdefghijklmnopqrst'
    col_letter, row_letter = coord[0], coord[1]
    col = columns.index(col_letter)
    row = columns.index(row_letter)
    row = board_size - row - 1  # Adjust row index to match the display
    return row, col

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

def on_board_click(event):
    global current_color, move_number, user_moves
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

    # Place the stone
    stone = draw_stone(row, col, current_color)
    label = canvas.create_text(margin + col * cell_size, margin + row * cell_size, text=str(move_number), fill='red')
    user_stones.append((stone, label))
    board[row][col] = current_color
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
    global board, user_moves, user_stones, move_number, current_color, hint_items
    # Clear all stones from the canvas
    for row in range(board_size):
        for col in range(board_size):
            board[row][col] = None
    for stone, label in user_stones:
        canvas.delete(stone)
        canvas.delete(label)
    user_stones.clear()
    # Clear hints
    for item in hint_items:
        canvas.delete(item)
    hint_items.clear()
    # Clear pre-set stones
    canvas.delete('preset_stone')
    user_moves = []
    move_number = 1
    current_color = 'black'  # Default to black, will be set in load_problem()

def load_problem():
    global problem, prepos, blackfirst, level, answers, current_color, info_label, board
    # Randomly select a problem
    problem = random.choice(problems)

    # Extract necessary data
    prepos = problem.get('prepos', {})
    blackfirst = problem.get('blackfirst', True)
    level = problem.get('level', 'N/A')
    answers = problem.get('answers', [])
    problem_no = problem.get('url_no', 'N/A')
    salt_r = problem.get('r', 'N/A')
    ty = problem.get('qtype', 'N/A')

    # Clear the board and reset variables
    clear_board()

    # Set current color
    current_color = 'black' if blackfirst else 'white'

    # Update window title
    root.title(f"Level {level} - {ty} - {'Black' if blackfirst else 'White'} first - No.{problem_no} - {salt_r}")

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
            stone = canvas.create_oval(x - r, y - r, x + r, y + r, fill='black' if color == 'b' else 'white', tags='preset_stone')
            board[row][col] = color

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

if __name__ == "__main__":
    # Connect to MongoDB and retrieve problems
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    collection = db['q']

    # Filter for "qtype": "死活题" and retrieve problems
    if len(sys.argv) == 2:
        #url_no = sys.argv[1]
        #problems_cursor = collection.find({"url_no": url_no})

        obj_id_str = sys.argv[1]
        problems_cursor = collection.find({"_id": ObjectId(obj_id_str)})
    else:
        problems_cursor = collection.find()
        #problems_cursor = collection.find({"qtype": "死活题"})
    problems = list(problems_cursor)
    print(len(problems))
    for p in problems:
        print(p.get('url_no'), p.get('title_id'), p.get('status'))

    # Check if any problems are found
    if not problems:
        raise Exception("No problems found with url_no.")
        quit()

    # Initialize GUI
    root = tk.Tk()
    root.title("Go Problem Viewer")

    canvas_size = 600
    margin = 20  # Margin around the board
    board_size = 19
    cell_size = (canvas_size - 2 * margin) / (board_size - 1)
    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
    canvas.pack()

    # Draw the Go board
    for i in range(board_size):
        # Vertical lines
        x = margin + i * cell_size
        canvas.create_line(x, margin, x, canvas_size - margin)
        # Horizontal lines
        y = margin + i * cell_size
        canvas.create_line(margin, y, canvas_size - margin, y)

    # Initialize variables to store game state
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    user_moves = []
    user_stones = []
    current_color = None
    move_number = 1
    hint_items = []
    prepos = {}
    blackfirst = True
    level = 'N/A'
    answers = []
    problem = {}
    info_label = None

    next_button = tk.Button(root, text="下一题 (Next Problem)", command=on_next_problem)
    next_button.pack(pady=5)

    # Bind the click event
    canvas.bind("<Button-1>", on_board_click)

    # Load the initial problem
    load_problem()

    root.mainloop()

