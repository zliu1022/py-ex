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
#problems_cursor = collection.find({"qtype": "死活题"})
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
level = problem['level']
answers = problem['answers']

# Initialize GUI
root = tk.Tk()
root.title(f"Go Problem - Level {level} - {'Black' if blackfirst else 'White'} to play first")

canvas_size = 600
board_size = 19
cell_size = canvas_size / (board_size - 1)
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
canvas.pack()

# Draw the Go board
for i in range(board_size):
    # Vertical lines
    x = i * cell_size
    canvas.create_line(x, 0, x, canvas_size)
    # Horizontal lines
    y = i * cell_size
    canvas.create_line(0, y, canvas_size, y)

# Draw pre-set stones
board = [[None for _ in range(board_size)] for _ in range(board_size)]

def draw_stone(row, col, color):
    x = col * cell_size
    y = row * cell_size
    r = cell_size / 2 - 2
    stone = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
    return stone

for color, positions in prepos.items():
    for coord in positions:
        row, col = coord_to_position(coord)
        draw_stone(row, col, 'black' if color == 'b' else 'white')
        board[row][col] = color

# Handle user moves
user_moves = []
current_color = 'black' if blackfirst else 'white'
move_number = 1

def on_board_click(event):
    global current_color, move_number
    col = int(round(event.x / cell_size))
    row = int(round(event.y / cell_size))
    if 0 <= row < board_size and 0 <= col < board_size and board[row][col] is None:
        draw_stone(row, col, current_color)
        # Label the stone with move number
        canvas.create_text(col * cell_size, row * cell_size, text=str(move_number), fill='red')
        board[row][col] = current_color
        coord = position_to_coord(row, col)
        user_moves.append(coord)
        move_number += 1
        # Switch color
        current_color = 'white' if current_color == 'black' else 'black'
        # Check if the user's sequence matches any of the answers
        match_found = False
        for answer in answers:
            answer_moves = answer['p']
            if user_moves == answer_moves[:len(user_moves)]:
                match_found = True
                if len(user_moves) == len(answer_moves):
                    messagebox.showinfo("Result", "正确！(Correct!)")
                    root.destroy()
                break
        if not match_found:
            messagebox.showinfo("Result", "错误！(Incorrect!)")
            root.destroy()
    else:
        messagebox.showwarning("Invalid move", "That position is occupied or out of bounds.")

canvas.bind("<Button-1>", on_board_click)

# Display who plays first and the level
info_label = tk.Label(root, text=f"Level: {level} | {'Black' if blackfirst else 'White'} plays first")
info_label.pack()

root.mainloop()
