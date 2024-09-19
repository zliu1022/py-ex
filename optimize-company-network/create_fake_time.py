#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from datetime import datetime, timedelta

def generate_fake_data():
    start_date = datetime(2024, 9, 18)
    end_date = datetime(2024, 9, 20)
    current_date = start_date

    # 打开文件并写入表头
    with open('fake.md', 'w', encoding='utf-8') as file:
        # 写入Markdown表头
        header = "| time | chat-dns | pt-com-dns | pt-cn-dns | chat-total | pt-com-total | pt-cn-total |\n"
        separator = "|---|---|---|---|---|---|---|\n"
        file.write(header)
        file.write(separator)

        while current_date <= end_date:
            # 生成每天的时间从09:00到18:00，每5分钟一个数据
            for hour in range(9, 18):
                for minute in range(0, 60, 5):
                    # 随机生成秒数
                    second = random.randint(0, 59)
                    timestamp = current_date.replace(hour=hour, minute=minute, second=second)
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                    # 生成随机数值
                    if current_date == datetime(2024, 9, 18):
                        chat_dns = round(random.uniform(0.01, 0.5), 6)
                        pt_com_dns = round(random.uniform(1.5, 2), 6)
                        pt_cn_dns = round(random.uniform(4, 10), 6)

                        chat_total = round(random.uniform(1, 2), 6)
                        pt_com_total = round(random.uniform(8, 10), 6)
                        pt_cn_total = round(random.uniform(15, 20), 6)
                    elif current_date == datetime(2024, 9, 19):
                        chat_dns = round(random.uniform(0.5, 1), 6)
                        pt_com_dns = round(random.uniform(2, 3), 6)
                        pt_cn_dns = round(random.uniform(4, 10), 6)

                        chat_total = round(random.uniform(2, 3), 6)
                        pt_com_total = round(random.uniform(10, 15), 6)
                        pt_cn_total = round(random.uniform(20, 25), 6)
                    elif current_date == datetime(2024, 9, 20):
                        chat_dns = round(random.uniform(1, 2), 6)
                        pt_com_dns = round(random.uniform(4, 5), 6)
                        pt_cn_dns = round(random.uniform(4, 10), 6)

                        chat_total = round(random.uniform(4, 5), 6)
                        pt_com_total = round(random.uniform(15, 20), 6)
                        pt_cn_total = round(random.uniform(25, 30), 6)
                    else:
                        pass

                    # 创建表格行
                    row = f"| {time_str} | {chat_dns} | {pt_com_dns} | {pt_cn_dns} | {chat_total} | {pt_com_total} | {pt_cn_total} |\n"
                    file.write(row)

            # 进入下一天
            current_date += timedelta(days=1)

if __name__ == "__main__":
    generate_fake_data()
    print("假数据已生成并保存到fake.md文件中。")

