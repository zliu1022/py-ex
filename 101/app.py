#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# app.py

import tkinter as tk
from tkinter import messagebox
import random

class GoBoard:
    def __init__(self, canvas, game_logic):
        self.canvas = canvas
        self.game_logic = game_logic
        self.board_size = 9  # 使用9x9的棋盘，便于展示
        self.margin = 20
        self.canvas_size = 400
        self.cell_size = (self.canvas_size - 2 * self.margin) / (self.board_size - 1)
        self.stone_radius = self.cell_size / 2 - 2
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.stones = {}
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_board_click)

    def draw_board(self):
        # 绘制棋盘线
        for i in range(self.board_size):
            x0 = self.margin
            y0 = self.margin + i * self.cell_size
            x1 = self.canvas_size - self.margin
            y1 = y0
            self.canvas.create_line(x0, y0, x1, y1)
            x0 = self.margin + i * self.cell_size
            y0 = self.margin
            x1 = x0
            y1 = self.canvas_size - self.margin
            self.canvas.create_line(x0, y0, x1, y1)

        # 绘制星位（可选）
        if self.board_size == 9:
            star_points = [(2, 2), (6, 2), (2, 6), (6, 6), (4, 4)]
            for row, col in star_points:
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                self.canvas.create_oval(
                    x - 2, y - 2, x + 2, y + 2, fill='black')

    def on_board_click(self, event):
        x = event.x
        y = event.y
        col = round((x - self.margin) / self.cell_size)
        row = round((y - self.margin) / self.cell_size)
        if 0 <= col < self.board_size and 0 <= row < self.board_size:
            self.game_logic.handle_click(row, col)

    def draw_stone(self, row, col, color):
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        x1 = x - self.stone_radius
        y1 = y - self.stone_radius
        x2 = x + self.stone_radius
        y2 = y + self.stone_radius
        stone_id = self.canvas.create_oval(x1, y1, x2, y2, fill=color)
        self.stones[(row, col)] = stone_id

    def remove_stone(self, row, col):
        stone_id = self.stones.get((row, col))
        if stone_id:
            self.canvas.delete(stone_id)
            del self.stones[(row, col)]
            self.board[row][col] = None

    def clear_board(self):
        for stone_id in self.stones.values():
            self.canvas.delete(stone_id)
        self.stones = {}
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]

    def draw_preset_stones(self, prepos):
        '''
        prepos: 包含初始棋子的字典，例如：{'AB': ['dd', 'ee'], 'AW': ['df']}
        'AB' 表示黑棋，'AW' 表示白棋
        '''
        for stone_type, positions in prepos.items():
            color = 'black' if stone_type == 'AB' else 'white'
            for pos in positions:
                if len(pos) == 2:
                    col = ord(pos[0]) - ord('a')
                    row = ord(pos[1]) - ord('a')
                    self.board[row][col] = color
                    self.draw_stone(row, col, color)
                else:
                    pass  # 处理更长的坐标（如果需要）

class GameLogic:
    def __init__(self, board, info_label):
        self.board = board
        self.info_label = info_label
        self.current_color = 'black'
        self.move_number = 1
        self.user_moves = []
        self.black_captures = 0
        self.white_captures = 0
        self.problem = None
        self.answers = []
        self.load_problems()
        self.load_problem()

    def load_problems(self):
        # 示例题目数据，在实际应用中，您可以从数据库加载
        self.problems = [
            {
                'prepos': {
                    'AB': ['dd', 'de', 'ed'],
                    'AW': ['ee', 'df', 'fe']
                },
                'blackfirst': True,
                'answers': [['ef', 'ff']]  # 正确的走子序列
            },
            {
                'prepos': {
                    'AB': ['cc', 'cd', 'dc'],
                    'AW': ['ce', 'dd']
                },
                'blackfirst': True,
                'answers': [['bd', 'be']]
            }
        ]

    def load_problem(self):
        self.problem = random.choice(self.problems)
        self.setup_problem(self.problem)

    def setup_problem(self, problem):
        self.board.clear_board()
        self.current_color = 'black' if problem.get('blackfirst', True) else 'white'
        self.move_number = 1
        self.user_moves = []
        self.black_captures = 0
        self.white_captures = 0
        self.answers = problem.get('answers', [])
        # 更新信息标签
        self.info_label.config(text=f"{'黑方' if self.current_color == 'black' else '白方'}先行")
        # 设置初始棋子
        prepos = problem.get('prepos', {})
        self.board.draw_preset_stones(prepos)

    def handle_click(self, row, col):
        if self.board.board[row][col] is None:
            # 下棋子
            self.board.board[row][col] = self.current_color
            self.board.draw_stone(row, col, self.current_color)
            self.user_moves.append((row, col))
            # 检查提子等规则（此处略）
            # 切换玩家
            self.current_color = 'white' if self.current_color == 'black' else 'black'
            self.move_number += 1

            # 检查是否解答正确
            self.check_solution()
        else:
            messagebox.showinfo("无效位置", "该位置已有棋子，请选择其他位置。")

    def check_solution(self):
        # 将用户的走子序列转换为字符串列表，例如 ['dd', 'ee']
        user_sequence = [''.join([chr(col+97), chr(row+97)]) for row, col in self.user_moves]
        for answer_sequence in self.answers:
            if user_sequence == answer_sequence[:len(user_sequence)]:
                if len(user_sequence) == len(answer_sequence):
                    messagebox.showinfo("成功", "恭喜！您解答正确。")
                    return
                else:
                    # 目前为止都正确，继续
                    return
        # 如果没有匹配的答案，表示用户走错了
        messagebox.showinfo("错误", "解答不正确，请再试一次。")
        # 您可以选择在这里重置题目或允许用户继续尝试

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("围棋题目查看器")
        self.canvas_size = 400
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack()
        self.next_button = tk.Button(self.root, text="下一题", command=self.on_next_problem)
        self.next_button.pack(pady=5)

        self.board = GoBoard(self.canvas, None)  # 初始化时暂时不传入 game_logic
        self.game_logic = GameLogic(self.board, self.info_label)
        self.board.game_logic = self.game_logic  # 在此处设置 game_logic

        self.root.mainloop()

    def on_next_problem(self):
        self.game_logic.load_problem()

if __name__ == "__main__":
    app = App()
