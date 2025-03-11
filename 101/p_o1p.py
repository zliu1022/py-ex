#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox

# Function to convert Go board coordinates (e.g., 'cs') to (row, column)
def coord_to_position(coord):
    columns = 'abcdefghijklmnopqrst'
    col_letter, row_letter = coord[0], coord[1]
    col = columns.index(col_letter)
    row = 19 - columns.index(row_letter) - 1
    return row, col

# Function to convert (row, column) to Go board coordinates
def position_to_coord(row, col):
    columns = 'abcdefghijklmnopqrst'
    row_letter = columns[19 - row - 1]
    col_letter = columns[col]
    return col_letter + row_letter

# Connect to MongoDB and retrieve a random problem
client = MongoClient('mongodb://localhost:27017/')
db = client['101']
collection = db['q']

# Filter for "qtype": "死活题" and retrieve problems
problems_cursor = collection.find({"qtype": "死活题"})
problems_cursor = collection.find({"no": "4958"})

problems = list(problems_cursor)

# Check if any problems are found
if not problems:
    raise Exception("No problems found with qtype '死活题'.")

# Randomly select a problem
problem = random.choice(problems)

# Extract necessary data
prepos = problem['prepos']
blackfirst = problem['blackfirst']
level = problem.get('level', 'N/A')
answers = problem['answers']

# Initialize GUI
root = tk.Tk()
root.title(f"Go Problem - Level {level} - {'Black' if blackfirst else 'White'} to play first")

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

# Draw pre-set stones
board = [[None for _ in range(board_size)] for _ in range(board_size)]

def draw_stone(row, col, color):
    x = margin + col * cell_size
    y = margin + row * cell_size
    r = cell_size / 2 - 2
    stone = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
    return stone

for color, positions in prepos.items():
    for coord in positions:
        row, col = coord_to_position(coord)
        draw_stone(row, col, 'black' if color == 'b' else 'white')
        board[row][col] = color

# Display hint for the first correct move
def draw_hint(coord):
    row, col = coord_to_position(coord)
    x = margin + col * cell_size
    y = margin + row * cell_size
    r = cell_size / 2 - 2
    hint = canvas.create_oval(x - r, y - r, x + r, y + r, outline='red', width=2)
    return hint

# Get the first move from the first answer as a hint
first_move = None
if answers:
    first_move = answers[0]['p'][0]
    draw_hint(first_move)

# Handle user moves
user_moves = []
user_stones = []
current_color = 'black' if blackfirst else 'white'
move_number = 1

def get_expected_coords(move_number):
    expected_coords = set()
    for answer in answers:
        if len(answer['p']) >= move_number:
            expected_coords.add(answer['p'][move_number - 1])
    return expected_coords

def show_error_message():
    error_window = tk.Toplevel(root)
    error_window.title("Result")
    tk.Label(error_window, text="错误！(Incorrect!)", font=('Arial', 16)).pack(padx=20, pady=20)
    error_window.after(2000, error_window.destroy)

def on_board_click(event):
    global current_color, move_number
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

    # Check if the user's sequence matches any of the answers
    for answer in answers:
        answer_moves = answer['p']
        if user_moves == answer_moves[:len(user_moves)]:
            if len(user_moves) == len(answer_moves):
                messagebox.showinfo("Result", "正确！(Correct!)")
                root.destroy()
            break
    else:
        # No matching answer; allow the user to continue
        pass

canvas.bind("<Button-1>", on_board_click)

# Display who plays first and the level
info_label = tk.Label(root, text=f"Level: {level} | {'Black' if blackfirst else 'White'} plays first")
info_label.pack()

root.mainloop()
