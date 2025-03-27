#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#主应用类（App） ：
#负责初始化Tkinter主窗口，管理主要的GUI组件和事件循环。
#处理按钮的创建和事件绑定。

import tkinter as tk
from board import GoBoard
from game import GoGame

class GoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Go Problem Viewer")

        # 创建主容器
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas
        self.canvas_size = 600
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Create game board
        self.board = GoBoard(self.canvas, size=19, canvas_size=self.canvas_size, margin=50)
        self.board.draw_board()

        # 题目列表区域 (右侧)
        self.problem_list_frame = tk.Frame(self.main_frame, width=200)
        self.problem_list_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)

        # 滚动条
        self.scrollbar = tk.Scrollbar(self.problem_list_frame)
        self.listbox = tk.Listbox(
            self.problem_list_frame,
            yscrollcommand=self.scrollbar.set,
            width=25,
            font=('Arial', 12)
        )
        self.scrollbar.config(command=self.listbox.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_problem_selected)

        # Create game instance
        self.game = GoGame(self.board)
        self.game.load_problems()


        # 创建一个容器 Frame，用于放置 info_label 和 result_label
        self.info_frame = tk.Frame(root)
        self.info_frame.pack(pady=5)

        # Info label
        self.info_label = tk.Label(self.info_frame, text="", fg='black', font=('Arial', 12))
        self.info_label.pack(side='left')

        # Result label
        self.result_label = tk.Label(self.info_frame, text="", font=('Arial', 14, 'bold'))
        self.result_label.pack(side='left')


        # 加载题目列表
        self.populate_problem_list()

        # Next problem button
        self.next_button = tk.Button(root, text="下一题 (Next Problem)", command=self.next_problem)
        self.next_button.pack(pady=5)

        # Bind the click event
        self.canvas.bind("<Button-1>", self.on_board_click)

        # Load the initial problem
        self.next_problem()

        # 横幅
        self.banner = None
        self.banner_text = None
        self.pending_action_after_banner = None

    def show_message_on_board(self, message):
        # 创建上方横幅的矩形，高度为棋盘的1/4
        banner_lr_margin = 50
        x0, y0 = banner_lr_margin, self.canvas_size / 4
        x1, y1 = self.canvas_size-banner_lr_margin, self.canvas_size / 8
        self.banner = self.canvas.create_rectangle(
            x0, y0, x1, y1, fill='lightblue'  # 选择温和的颜色
        )
        # 在横幅中心显示消息
        self.banner_text = self.canvas.create_text(
            x1 / 2, y0/2+y1 / 2,
            text=message, font=('Arial', 36), fill='black'  # 调整字体大小和颜色
        )
        # 3秒后移除横幅
        self.root.after(3000, self.remove_banner)

    def remove_banner(self):
        if self.banner:
            self.canvas.delete(self.banner)
            self.canvas.delete(self.banner_text)
            self.banner = None
            self.banner_text = None
        # 根据需要执行后续操作
        #if self.pending_action_after_banner == 'next_problem':
        #    self.next_problem()
        #elif self.pending_action_after_banner == 'reset_problem':
        #    self.reset_problem()
        self.pending_action_after_banner = None

    def update_lable_text(self, new_result):
        # 替换上次的追加（假设上次追加的内容在最后一个空格之后）
        text = self.info_label.cget("text")
        if text.endswith(" 正确") or text.endswith(" 错误"):
            text = text.rsplit(' ', 1)[0]
        new_text = text + ' ' + new_result
        return new_text

    def show_correct_message(self):
        result_info_text = "正确"
        self.show_message_on_board(result_info_text)
        # 在 info_label 中追加显示“正确”
        #self.info_label.config(text=self.info_label.cget("text") + " 正确")
        #self.pending_action_after_banner = 'next_problem'  # 横幅消失后进入下一题

        self.result_label.config(text=result_info_text, fg='green')

    def show_incorrect_message(self):
        result_info_text = "错误"
        self.show_message_on_board(result_info_text)
        # 在 info_label 中追加显示“错误”
        #self.info_label.config(text=self.info_label.cget("text") + " 错误")
        #self.pending_action_after_banner = 'reset_problem'  # 横幅消失后重置题目

        self.result_label.config(text=result_info_text, fg='red')

    def reset_problem(self):
        # 重新加载当前题目
        self.game.load_problem(index=self.game.current_problem_index)
        self.update_problem_info()
        self.board.clear_board()
        self.board.place_preset_stones(self.game.current_problem.prepos)

    def populate_problem_list(self):
        """填充题目列表"""
        self.listbox.delete(0, tk.END)  # 清空旧列表
        for idx, problem in enumerate(self.game.problems):
            problem_no = problem.publicid
            difficulty = problem.level
            self.listbox.insert(tk.END, f"[{difficulty}] {problem_no}")

    def on_problem_selected(self, event):
        """处理题目选择事件"""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.game.load_problem(index)
            self.update_problem_info()
            self.board.clear_board()
            self.board.place_preset_stones(self.game.current_problem.prepos)

    def update_problem_info(self):
        """更新题目信息显示"""
        problem_info = {
            'level': self.game.current_problem.level,
            'color': 'Black' if self.game.current_problem.blackfirst else 'White',
            'problem_no': self.game.current_problem.publicid,
            'type': self.game.current_problem.ty
        }
        self.root.title(
            f"Level {problem_info['level']} - {problem_info['type']} - "
            f"{problem_info['color']} first - No.{problem_info['problem_no']}"
        )

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
        result = self.game.make_move(row, col)
        if result == 'invalid_move':
            # 可以选择提示无效操作，这里省略
            pass
        elif result == 'incorrect':
            self.show_incorrect_message()
        elif result == 'correct':
            self.show_correct_message()
        elif result == 'continue':
            # 游戏继续，不需要额外操作
            pass

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
