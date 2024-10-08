#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time

def prevent_sleep_with_caffeinate():
    # 启动 caffeinate 进程，防止系统睡眠
    caffeinate_process = subprocess.Popen(['caffeinate', '-iu'])
    subprocess.run(['sudo', 'pmset', '-a', 'sleep', '0', 'disksleep', '0'], check=True)

    try:
        # 你的主要程序逻辑
        while True:
            # 示例：每隔一段时间执行网络操作
            print("程序正在运行...")
            time.sleep(10)  # 模拟长时间运行的任务
    except KeyboardInterrupt:
        print("程序终止，关闭 caffeinate...")
    finally:
        # 终止 caffeinate 进程
        caffeinate_process.terminate()
        subprocess.run(['sudo', 'pmset', '-a', 'sleep', '10', 'disksleep', '10'], check=True)

if __name__ == "__main__":
    prevent_sleep_with_caffeinate()

