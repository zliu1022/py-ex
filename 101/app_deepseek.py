#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox
from config import db_name

class GoBoard:
    def __init__(self, canvas, size=19, canvas_size=600, margin=20):
        self.canvas = canvas
        self.size = size
        self.canvas_size = canvas_size
        self.margin = margin
        self.cell_size = (canvas_size - 2 * margin) / (size - 1)
        self.board = [[None for _ in range(size)] for _ in range(size)]

    def draw_board(self):
        for i in range(self.size):
            # Vertical lines
            x = self.margin + i * self.cell_size
            self.canvas.create_line(x, self.margin, x, self.canvas_size - self.margin)
            # Horizontal lines
            y = self.margin + i * self.cell_size
            self.canvas.create_line(self.margin, y, self.canvas_size - self.margin, y)

    def coord_to_position(self, coord):
        columns = 'abcdefghijklmnopqrst'
        col_letter, row_letter = coord[1], coord[0]
        col = columns.index(col_letter)
        row = columns.index(row_letter)
        row = self.size - row - 1  # Adjust row index to match the display
        return row, col

    def position_to_coord(self, row, col):
        columns = 'abcdefghijklmnopqrst'
        row_letter = columns[self.size - row - 1]
        col_letter = columns[col]
        return col_letter + row_letter

    def draw_stone(self, row, col, color):
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        r = self.cell_size / 2 - 2
        stone = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
        return stone

    def draw_hint(self, coord):
        row, col = self.coord_to_position(coord)
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        r = self.cell_size / 2 - 2
        hint = self.canvas.create_oval(x - r, y - r, x + r, y + r, outline='red', width=2)
        return hint

    def clear_board(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] is not None:
                    self.canvas.delete(self.board[row][col]['stone'])
                    if self.board[row][col]['label'] is not None:
                        self.canvas.delete(self.board[row][col]['label'])
                    self.board[row][col] = None

    def place_preset_stones(self, prepos):
        for color, positions in prepos.items():
            for coord in positions:
                row, col = self.coord_to_position(coord)
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                r = self.cell_size / 2 - 2
                stone_color = 'black' if color == 'b' else 'white'
                stone = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=stone_color, tags='preset_stone')
                self.board[row][col] = {'color': stone_color, 'stone': stone, 'label': None}

class GoGame:
    def __init__(self, board):
        self.board = board
        self.user_moves = []
        self.current_color = None
        self.move_number = 1
        self.hint_items = []
        self.prepos = {}
        self.blackfirst = True
        self.level = 'N/A'
        self.answers = []
        self.problem = {}
        self.black_captures = 0
        self.white_captures = 0
        self.problems = []
        self.current_problem_index = -1

    def load_problems(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db['q']
        problems_cursor = collection.find({"status": 2, "qtype": "死活题", "level": "9K"})
        self.problems = list(problems_cursor)
        if not self.problems:
            raise Exception("No problems found")

    def load_problem(self, index=None):
        if index is None:
            self.problem = random.choice(self.problems)
        else:
            self.problem = self.problems[index]

        self.prepos = self.problem.get('prepos', {})
        self.blackfirst = self.problem.get('blackfirst', True)
        self.level = self.problem.get('level', 'N/A')
        self.answers = self.problem.get('answers', [])
        problem_no = self.problem.get('publicie', 'N/A')
        ty = self.problem.get('qtype', 'N/A')

        self.reset_game()

        self.current_color = 'black' if self.blackfirst else 'white'

        # Place preset stones
        self.board.place_preset_stones(self.prepos)

        # Display hint for the first move
        first_move = None
        if self.answers:
            for ans in self.answers:
                if ans['ty'] == 1 and ans['st'] == 2:
                    first_move = ans['p'][0]
                    break
            if first_move is None:
                print('Warning no answers ty==1 st==2')
                first_move = 'jj'
            self.hint_items.append(self.board.draw_hint(first_move))

        return {
            'level': self.level,
            'color': 'Black' if self.blackfirst else 'White',
            'problem_no': problem_no,
            'type': ty
        }

    def reset_game(self):
        self.board.clear_board()
        self.user_moves = []
        self.move_number = 1
        self.hint_items = []
        self.black_captures = 0
        self.white_captures = 0

    def get_group(self, row, col):
        color = self.board.board[row][col]['color']
        group = set()
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) not in group:
                group.add((r, c))
                # Check the four neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.board.size and 0 <= nc < self.board.size:
                        if self.board.board[nr][nc] is not None and self.board.board[nr][nc]['color'] == color:
                            stack.append((nr, nc))
        return group

    def has_liberties(self, group):
        for r, c in group:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.board.size and 0 <= nc < self.board.size:
                    if self.board.board[nr][nc] is None:
                        return True
        return False

    def remove_group(self, group):
        for r, c in group:
            self.board.canvas.delete(self.board.board[r][c]['stone'])
            if self.board.board[r][c]['label'] is not None:
                self.board.canvas.delete(self.board.board[r][c]['label'])
            self.board.board[r][c] = None

    def get_expected_coords(self, move_number):
        expected_coords = set()
        for answer in self.answers:
            if len(answer['p']) >= move_number:
                expected_coords.add(answer['p'][move_number - 1])
        return expected_coords

    def get_expected_next_coords(self, user_moves):
        expected_coords = set()
        for answer in self.answers:
            if answer['p'][:len(user_moves)] == user_moves:
                if len(answer['p']) > len(user_moves):
                    expected_coords.add(answer['p'][len(user_moves)])
        return expected_coords

    def make_move(self, row, col):
        # Check if the position is unoccupied
        if self.board.board[row][col] is not None:
            messagebox.showwarning("Invalid move", "That position is occupied.")
            return False

        # Get expected coordinates for the current move number
        expected_coords = self.get_expected_coords(self.move_number)
        tolerance = self.board.cell_size / 2  # Allowable distance from the correct point
        match_found = False
        coord = None

        for exp_coord in expected_coords:
            exp_row, exp_col = self.board.coord_to_position(exp_coord)
            x_expected = exp_col * self.board.cell_size
            y_expected = exp_row * self.board.cell_size
            x_click = col * self.board.cell_size
            y_click = row * self.board.cell_size
            dx = x_click - x_expected
            dy = y_click - y_expected
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= tolerance:
                # Correct move found within tolerance
                row, col = exp_row, exp_col  # Correct the position to the expected one
                coord = exp_coord  # Use the expected coordinate
                match_found = True
                break

        if not match_found:
            return False

        # Place the stone tentatively
        stone = self.board.draw_stone(row, col, self.current_color)
        label = self.board.canvas.create_text(
            self.board.margin + col * self.board.cell_size,
            self.board.margin + row * self.board.cell_size,
            text=str(self.move_number), fill='red')
        self.board.board[row][col] = {'color': self.current_color, 'stone': stone, 'label': label}

        # Perform captures
        opponent_color = 'white' if self.current_color == 'black' else 'black'
        captured_stones = 0

        # Check adjacent positions for opponent stones
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.board.size and 0 <= nc < self.board.size:
                if self.board.board[nr][nc] is not None and self.board.board[nr][nc]['color'] == opponent_color:
                    opponent_group = self.get_group(nr, nc)
                    if not self.has_liberties(opponent_group):
                        self.remove_group(opponent_group)
                        captured_stones += len(opponent_group)
                        # Record captures
                        if self.current_color == 'black':
                            self.black_captures += len(opponent_group)
                        else:
                            self.white_captures += len(opponent_group)

        # Now check if own group has liberties
        own_group = self.get_group(row, col)
        if not self.has_liberties(own_group):
            # Invalid move: self-capture not allowed
            # Remove the placed stone
            self.board.canvas.delete(self.board.board[row][col]['stone'])
            self.board.canvas.delete(self.board.board[row][col]['label'])
            self.board.board[row][col] = None
            return False

        # The move is valid, proceed
        self.user_moves.append(coord)
        self.move_number += 1

        # Switch color
        self.current_color = 'white' if self.current_color == 'black' else 'black'

        # Clear previous hints
        for item in self.hint_items:
            self.board.canvas.delete(item)
        self.hint_items.clear()

        # Check if the user's sequence matches any of the answers
        matched_answers = []
        for answer in self.answers:
            answer_moves = answer['p']
            if self.user_moves == answer_moves[:len(self.user_moves)]:
                matched_answers.append(answer)
                if len(self.user_moves) == len(answer_moves):
                    messagebox.showinfo("Result", "正确！(Correct!)")
                    # Prepare for next problem or reset
                    return True  # End the game
                break  # Found a matching answer

        # Display hints for the next expected moves
        next_expected_coords = self.get_expected_next_coords(self.user_moves)
        for coord in next_expected_coords:
            self.hint_items.append(self.board.draw_hint(coord))

        return True

class GoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Go Problem Viewer")

        # Create canvas
        self.canvas_size = 600
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Create game board
        self.board = GoBoard(self.canvas)
        self.board.draw_board()

        # Create game instance
        self.game = GoGame(self.board)
        self.game.load_problems()

        # Info label
        self.info_label = tk.Label(root, text="")
        self.info_label.pack()

        # Next problem button
        self.next_button = tk.Button(root, text="下一题 (Next Problem)", command=self.next_problem)
        self.next_button.pack(pady=5)

        # Bind the click event
        self.canvas.bind("<Button-1>", self.on_board_click)

        # Load the initial problem
        self.next_problem()

    def on_board_click(self, event):
        x_click = event.x - self.board.margin
        y_click = event.y - self.board.margin
        if (x_click < -self.board.cell_size / 2 or y_click < -self.board.cell_size / 2 or
            x_click > self.canvas_size - self.board.margin or y_click > self.canvas_size - self.board.margin):
            # Click outside the board area
            return

        # Calculate approximate grid position from click
        col_click = x_click / self.board.cell_size
        row_click = y_click / self.board.cell_size
        col = int(round(col_click))
        row = int(round(row_click))

        if not (0 <= row < self.board.size and 0 <= col < self.board.size):
            # Click is outside the board grid
            return

        # Try to make the move
        if not self.game.make_move(row, col):
            self.show_error_message()

    def show_error_message(self):
        error_window = tk.Toplevel(self.root)
        error_window.title("Result")
        tk.Label(error_window, text="错误！(Incorrect!)", font=('Arial', 16)).pack(padx=20, pady=20)
        error_window.after(2000, error_window.destroy)

    def next_problem(self):
        problem_info = self.game.load_problem()
        self.root.title(
            f"Level {problem_info['level']} - {problem_info['type']} - "
            f"{problem_info['color']} first - No.{problem_info['problem_no']}"
        )
        self.info_label.config(
            text=f"Level: {problem_info['level']} | "
            f"{problem_info['color']} plays first | No.{problem_info['problem_no']}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = GoApp(root)
    root.mainloop()
