#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib

# 设置中文字体，防止中文乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False    # 解决保存图像是负号'-'显示为方块的问题

# 定义折射率
n_water = 1.333  # 水的折射率
n_air = 1.000    # 空气的折射率

# 定义水面位置
z_water_surface = 0

# 定义水下物体点的位置
object_point = np.array([0, 0, -5])  # (x, y, z)

# 定义眼睛的位置
eye_position = np.array([0, 0, 5])

# 定义从物体点出发的光线方向（以不同的角度）
theta = np.linspace(-np.pi/6, np.pi/6, 5)  # 从 -30度到 30度，选取5条光线
phi = np.linspace(-np.pi/6, np.pi/6, 5)    # 从 -30度到 30度，选取5条光线

# 创建图形
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 绘制水面
xx, yy = np.meshgrid(np.linspace(-10, 10, 10), np.linspace(-10, 10, 10))
zz = np.zeros_like(xx) + z_water_surface
ax.plot_surface(xx, yy, zz, alpha=0.3, color='cyan')

# 绘制水下物体点
ax.scatter(object_point[0], object_point[1], object_point[2], color='red', s=100, label='水下物体点')

# 绘制眼睛位置
ax.scatter(eye_position[0], eye_position[1], eye_position[2], color='green', s=100, label='眼睛位置')

# 初始化虚像点的列表
virtual_points = []

# 遍历每一条光线
for t in theta:
    for p in phi:
        # 计算水下光线的方向向量
        direction_in_water = np.array([
            np.sin(t)*np.cos(p),
            np.sin(t)*np.sin(p),
            np.cos(t)
        ])

        # 计算光线与水面的交点
        # 参数方程：r = object_point + s * direction_in_water
        # 求解s使得z = z_water_surface
        s = (z_water_surface - object_point[2]) / direction_in_water[2]
        intersection_point = object_point + s * direction_in_water

        # 计算入射角theta1
        cos_theta1 = abs(direction_in_water[2]) / np.linalg.norm(direction_in_water)
        theta1 = np.arccos(cos_theta1)

        # 使用斯涅尔定律计算折射角theta2
        sin_theta2 = (n_water / n_air) * np.sin(theta1)
        # 防止全反射
        if sin_theta2 > 1:
            continue  # 跳过此光线
        theta2 = np.arcsin(sin_theta2)

        # 计算折射后的方向向量
        direction_in_air = np.array([
            direction_in_water[0],
            direction_in_water[1],
            np.sign(direction_in_water[2]) * np.cos(theta2)
        ])
        direction_in_air = direction_in_air / np.linalg.norm(direction_in_air)

        # 从交点到眼睛的光线参数方程
        # r = intersection_point + t * direction_in_air
        # 求解t使得r到达眼睛位置
        # 即 eye_position = intersection_point + t * direction_in_air
        # 解方程求t
        # 如果方向不对，跳过
        t_eye = (eye_position - intersection_point) / direction_in_air
        if not np.allclose(t_eye[0], t_eye[1], atol=1e-2) or not np.allclose(t_eye[0], t_eye[2], atol=1e-2):
            continue  # 不满足，则跳过
        t_eye = t_eye[0]
        if t_eye < 0:
            continue  # 光线方向不对，跳过

        # 绘制水下的光线
        ax.plot(
            [object_point[0], intersection_point[0]],
            [object_point[1], intersection_point[1]],
            [object_point[2], intersection_point[2]],
            color='blue'
        )

        # 绘制折射后的光线
        ax.plot(
            [intersection_point[0], eye_position[0]],
            [intersection_point[1], eye_position[1]],
            [intersection_point[2], eye_position[2]],
            color='orange'
        )

        # 延长折射后的光线（反向延长），找到虚像位置
        t_virtual = - (intersection_point[2] - object_point[2]) / direction_in_air[2]
        virtual_point = intersection_point + t_virtual * direction_in_air
        virtual_points.append(virtual_point)

        # 绘制虚像光线的延长线（虚线）
        ax.plot(
            [intersection_point[0], virtual_point[0]],
            [intersection_point[1], virtual_point[1]],
            [intersection_point[2], virtual_point[2]],
            color='gray', linestyle='dashed'
        )

# 绘制虚像点
for vp in virtual_points:
    ax.scatter(vp[0], vp[1], vp[2], color='purple', s=50, label='虚像点')

# 设置轴标签
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
ax.set_zlabel('Z轴')

# 设置标题
ax.set_title('根据光的折射定律绘制三维物体的成像图')

# 设置图例
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

# 设置显示范围
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(-10, 10)

# 显示图形
plt.show()
