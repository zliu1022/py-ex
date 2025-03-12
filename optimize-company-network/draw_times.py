#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re

# 从 Markdown 文件中读取数据
def read_data_from_md(file_path):
    data = {
        "time": [],
        "chat-dns": [],
        "pt-com-dns": [],
        "pt-cn-dns": [],
        "ytb-dns": [],
        "chat-total": [],
        "pt-com-total": [],
        "pt-cn-total": [],
        "ytb-total": []
    }

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 检查文件是否使用 | 分隔的 Markdown 表格格式
    is_markdown_table = any(line.startswith('|') for line in lines)

    if is_markdown_table:
        # 使用正则表达式提取表格中的数据行
        for line in lines:
            match = re.match(r'\| ([\d-]+\s[\d:]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|', line)
            if match:
                data["time"].append(match.group(1))
                data["chat-dns"].append(float(match.group(2)))
                data["pt-com-dns"].append(float(match.group(3)))
                data["pt-cn-dns"].append(float(match.group(4)))
                data["ytb-dns"].append(float(match.group(5)))
                data["chat-total"].append(float(match.group(6)))
                data["pt-com-total"].append(float(match.group(7)))
                data["pt-cn-total"].append(float(match.group(8)))
                data["ytb-total"].append(float(match.group(9)))
    else:
        # 处理以制表符分隔的文本格式
        for line in lines:
            # 跳过标题行
            if line.startswith("time") or line.strip() == "":
                continue
            parts = line.strip().split('\t')
            if len(parts) == 7:
                data["time"].append(parts[0])
                data["chat-dns"].append(float(parts[1]))
                data["pt-com-dns"].append(float(parts[2]))
                data["pt-cn-dns"].append(float(parts[3]))
                data["chat-total"].append(float(parts[4]))
                data["pt-com-total"].append(float(parts[5]))
                data["pt-cn-total"].append(float(parts[6]))

    # 将数据转为 DataFrame
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])  # 将 time 列转换为 datetime 类型
    return df

# 筛选每天9点到18点的数据
def filter_data_by_time(data):
    # 转换为时间格式
    data['time'] = pd.to_datetime(data['time'])
    # 筛选9点到18点之间的数据
    filtered_data = data[(data['time'].dt.hour >= 9) & (data['time'].dt.hour <= 18)]
    return filtered_data

def add_relative_time(data):
    data = data.sort_values('time').copy()
    unique_dates = data['time'].dt.date.sort_values().unique()
    date_to_day_index = {date: idx for idx, date in enumerate(unique_dates)}
    
    # 计算每个数据点对应的分钟数
    data['minutes_since_9'] = data['time'].dt.hour * 60 + data['time'].dt.minute - 9 * 60
    data['minutes_since_9'] = data['minutes_since_9'].clip(lower=0)  # 确保无负值
    
    # 计算相对时间
    data['relative_time'] = data['time'].dt.date.map(date_to_day_index) * 540 + data['minutes_since_9']
    
    return data

# 绘制单日的 DNS 和 total 对比图（修改为使用相对时间）
def plot_daily_comparison(daily_data):
    # 创建一个figure和两个子图, 共享 X 轴
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 绘制 DNS 对比图
    ax1.plot(daily_data['relative_time'], daily_data['chat-dns'], label='chat-dns', marker='.')
    ax1.plot(daily_data['relative_time'], daily_data['pt-com-dns'], label='pt-com-dns', marker='.')
    ax1.plot(daily_data['relative_time'], daily_data['pt-cn-dns'], label='pt-cn-dns', marker='.')
    ax1.plot(daily_data['relative_time'], daily_data['ytb-dns'], label='ytb-dns', marker='.')
    ax1.set_title('DNS Comparison')
    ax1.set_xlabel('Relative Time (minutes)')
    ax1.set_ylabel('DNS Time (s)')
    ax1.legend()
    ax1.grid(True)  # 添加网格线
    ax1.set_ylim(0, 1.5)

    # 隐藏 ax1 的 X 轴刻度和标签
    ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # 绘制 total 对比图
    ax2.plot(daily_data['relative_time'], daily_data['chat-total'], label='chat-total', marker='.')
    ax2.plot(daily_data['relative_time'], daily_data['pt-com-total'], label='pt-com-total', marker='.')
    ax2.plot(daily_data['relative_time'], daily_data['pt-cn-total'], label='pt-cn-total', marker='.')
    ax2.plot(daily_data['relative_time'], daily_data['ytb-total'], label='ytb-total', marker='.')
    ax2.set_title('Total Time Comparison')
    ax2.set_xlabel('Relative Time (minutes)')
    ax2.set_ylabel('Total Time (s)')
    ax2.legend()
    ax2.grid(True)  # 添加网格线
    ax2.set_ylim(0, 4)

    unique_dates = daily_data['time'].dt.date.sort_values().unique()
    # 在每一天结束时添加一条垂直虚线，用于分隔不同天的数据
    # 假设每一天的数据区间为 540 分钟（9小时），所以分隔线的位置为 j*540
    for j in range(1, len(unique_dates)):
        ax2.axvline(x=j*540, color='grey', linestyle='--', linewidth=0.5)

    # 设置 X 轴刻度和标签
    ax2.set_xticks([i*540 for i in range(len(unique_dates)+1)])
    ax2.set_xticklabels([f'Day {i+1}' for i in range(len(unique_dates))] + [f'Day {len(unique_dates)+1}'], rotation=45)

    # 优化x轴显示
    plt.tight_layout()
    plt.show()

# 绘制多天的对比图
def plot_multiple_days_comparison(data):
    #metrics = ['chat-dns', 'pt-com-dns', 'pt-cn-dns', 'chat-total', 'pt-com-total', 'pt-cn-total']
    metrics = ['chat-total', 'pt-com-total', 'pt-cn-total', 'ytb-total']
    num_metrics = len(metrics)
    cols = 2
    rows = (num_metrics + 1) // cols

    fig, axs = plt.subplots(rows, cols, figsize=(14, 6 * rows), sharey=True)
    axs = axs.flatten()  # 将子图数组展平，方便迭代

    # 创建统一的5分钟时间轴（9:00到18:00）
    time_range = pd.date_range(start='09:00', end='18:00', freq='5T').time
    # 将时间范围转换为分钟数，以方便后续匹配
    time_range_minutes = [t.hour * 60 + t.minute for t in time_range]

    # 获取所有唯一日期
    unique_dates = data['time'].dt.date.unique()

    for i, metric in enumerate(metrics):
        ax = axs[i]
        for date in unique_dates:
            daily_data = data[data['time'].dt.date == date].copy()
            # 提取时间部分
            daily_data['time_of_day'] = daily_data['time'].dt.time
            # 将时间转换为分钟数
            daily_data['minutes'] = daily_data['time_of_day'].apply(lambda t: t.hour * 60 + t.minute)
            # 将时间映射到最近的5分钟区间
            daily_data['time_bin'] = daily_data['minutes'].apply(
                lambda x: 5 * round(x / 5)
            )
            # 限制在9:00到18:00
            daily_data = daily_data[(daily_data['time_bin'] >= 9*60) & (daily_data['time_bin'] <= 18*60)]
            # 将时间_bin转换回时间
            daily_data['time_bin_time'] = daily_data['time_bin'].apply(
                lambda x: (datetime.combine(datetime.min, datetime.min.time()) + timedelta(minutes=x)).time()
            )
            # 聚合每个5分钟区间的值（取平均值）
            aggregated = daily_data.groupby('time_bin_time')[metric].mean().reset_index()

            # 将 aggregated 的 time_bin_time 转换为 datetime.time 以匹配统一的time_range
            # 将 time_bin_time 转换为 datetime.datetime 方便绘图
            aggregated['time_bin_datetime'] = pd.to_datetime(aggregated['time_bin_time'].astype(str))

            # 仅保留时间在统一时间范围内的数据
            mask = aggregated['time_bin_time'].isin(time_range)
            aggregated = aggregated[mask]

            # 重新索引，以确保所有时间点都有数据
            aggregated = aggregated.set_index('time_bin_datetime').reindex(pd.to_datetime(time_range.astype(str)), method=None)

            # 取出时间点和对应的值
            x = pd.to_datetime(range(len(time_range)), unit='m', origin=pd.Timestamp('1900-01-01 09:00')) + pd.to_timedelta(0, unit='m')
            x = pd.to_datetime(['1900-01-01 ' + t.strftime('%H:%M:%S') for t in time_range])

            y = aggregated[metric].values

            # 绘制
            ax.plot(x, y, label=f'{date}', marker='.')

            ax.set_ylim(0, 4)

        ax.set_title(f'{metric} Comparison Over Multiple Days')
        ax.set_xlabel('Time of Day')
        ax.set_ylabel(metric)
        ax.legend()
        ax.grid(True)  # 添加网格线
        # 设置x轴范围为9:00到18:00
        ax.set_xlim(pd.to_datetime('1900-01-01 09:00:00'), pd.to_datetime('1900-01-01 18:00:00'))
        # 设置x轴刻度
        ax.set_xticks(pd.to_datetime(['1900-01-01 ' + t.strftime('%H:%M') for t in time_range][::6]))  # 每30分钟一个刻度
        ax.set_xticklabels([t.strftime('%H:%M') for t in time_range][::6], rotation=45)

    # 如果子图不够，删除多余的子图
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])

    # 调整布局并显示图像
    plt.tight_layout()
    plt.show()

# 主程序
def main():
    file_path = 'output.md'  # 文件路径
    data = read_data_from_md(file_path)

    # 筛选每天9点到18点的数据
    filtered_data = filter_data_by_time(data)

    # 对比多天9-18点的数据
    plot_multiple_days_comparison(filtered_data)

    # 添加相对时间列
    filtered_data = add_relative_time(filtered_data)
    # 对比不同列的多天数据
    plot_daily_comparison(filtered_data)

if __name__ == '__main__':
    main()

