#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
from datetime import datetime
import os

# 定义目标URL和对应的短名称
urls = {
    "chat": "https://chatgptd-dev.tvunetworks.com/",
    "pt-com": "https://partyline.tvunetworks.com/partyline/participate/party?id=942382705012",
    "pt-cn": "https://partyline.tvunetworks.cn/partyline/participate/party?id=199966092325",
    "ytb": "https://www.youtube.com/"
}

# 获取当前时间戳，时间戳格式为 年-月-日 小时:分钟:秒
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 生成文件名，格式为 output_202409190939.md
def generate_filename():
    return f"output_{datetime.now().strftime('%Y%m%d%H%M')}.md"

# 使用 curl 命令抓取 DNS 和 total 时间
def get_timing_info(url):
    result = subprocess.run(
        [
            "curl", "-w",
            "dns: %{time_namelookup}\ntotal: %{time_total}\n",
            "-o", "/dev/null",  # 不保存输出
            "-s", url
        ],
        capture_output=True,
        text=True
    )

    # 提取dns和total的时间
    timings = result.stdout.strip().split("\n")
    dns_time = timings[0].split(": ")[1]
    total_time = timings[1].split(": ")[1]

    return dns_time, total_time

# 输出表格的表头
def print_table_header(file):
    header = "| time | chat-dns | pt-com-dns | pt-cn-dns | ytb_dns | chat-total | pt-com-total | pt-cn-total | ytb_total |\n"
    separator = "|---|---|---|---|---|---|---|---|---|\n"
    # 打印到屏幕
    print(header + separator, end="")
    # 保存到文件
    file.write(header)
    file.write(separator)
    # 强制写入文件
    file.flush()
    os.fsync(file.fileno())

# 输出表格的每一行
def print_table_row(file, time_str, chat_dns, pt_com_dns, pt_cn_dns, ytb_dns, chat_total, pt_com_total, pt_cn_total, ytb_total):
    row = f"| {time_str} | {chat_dns} | {pt_com_dns} | {pt_cn_dns} | {ytb_dns} | {chat_total} | {pt_com_total} | {pt_cn_total} | {ytb_total} |\n"
    # 打印到屏幕
    print(row, end="")
    # 保存到文件
    file.write(row)
    # 强制写入文件
    file.flush()
    os.fsync(file.fileno())

# 主要循环逻辑
def main():
    # 启动 caffeinate 防止 macOS 休眠
    caffeinate = subprocess.Popen(['caffeinate',  '-iu'])
    subprocess.run(['sudo', 'pmset', '-a', 'sleep', '0', 'disksleep', '0'], check=True)

    # 生成文件名并打开文件
    filename = generate_filename()
    with open(filename, "w") as file:
        # 打印和保存表头
        print_table_header(file)

        try:
            while True:
                current_hour = datetime.now().hour
                current_minute = datetime.now().minute

                # 检查是否在9点到18点之间
                if 9 <= current_hour <= 17:
                    # 检查当前时间是否为5分钟的整数倍
                    if current_minute % 5 == 0:
                        current_time = get_current_time()

                        # 获取 chat 的 DNS 和 total 时间
                        chat_dns, chat_total = get_timing_info(urls["chat"])
                        # 获取 pt-com 的 DNS 和 total 时间
                        pt_com_dns, pt_com_total = get_timing_info(urls["pt-com"])
                        # 获取 pt-cn 的 DNS 和 total 时间
                        pt_cn_dns, pt_cn_total = get_timing_info(urls["pt-cn"])

                        ytb_dns, ytb_total = get_timing_info(urls["ytb"])

                        # 打印表格行并保存到文件
                        print_table_row(file, current_time, chat_dns, pt_com_dns, pt_cn_dns, ytb_dns, chat_total, pt_com_total, pt_cn_total, ytb_total)

                # 每60秒检测一次
                time.sleep(60)
        finally:
            # 确保程序结束时，关闭 caffeinate
            caffeinate.terminate()
            subprocess.run(['sudo', 'pmset', '-a', 'sleep', '10', 'disksleep', '10'], check=True)

if __name__ == "__main__":
    main()

