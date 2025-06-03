#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def refract(v_in, n, n1, n2):
    """计算折射光线方向"""
    eta = n1 / n2
    dot = np.dot(v_in, n)
    discriminant = 1.0 - eta**2 * (1.0 - dot**2)
    if discriminant < 0:
        return None  # 全内反射
    sqrt_d = np.sqrt(discriminant)
    t = eta * (v_in - n * dot) - n * sqrt_d
    return t / np.linalg.norm(t)  # 归一化

# 场景设置
n1, n2 = 1.33, 1.0  # 水和空气的折射率
P = np.array([0.0, 0.0, -2.0])  # 水下物体点
Q_z = -P[2] * (n2 / n1)  # 虚像点的z坐标（视深公式）
Q = np.array([0.0, 0.0, Q_z])  # 虚像点
Eye = np.array([0.0, 0.0, 2.0])  # 眼睛位置

# 创建图形
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 绘制水面
xx, yy = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
z = np.zeros_like(xx)
ax.plot_surface(xx, yy, z, alpha=0.3, color='blue', linewidth=0)

# 绘制关键点
ax.scatter(*P, color='red', s=50, label='物体点 P')
ax.scatter(*Q, color='purple', s=50, label='虚像点 Q')
ax.scatter(*Eye, color='blue', s=50, label='眼睛位置')

# 生成光线
num_rays = 6  # 光线数量
for _ in range(num_rays):
    # 生成随机方向（向上）
    dx, dy = np.random.uniform(-1, 1, 2)
    dz = np.abs(np.random.randn())  # 向上z分量
    direction = np.array([dx, dy, dz])
    direction /= np.linalg.norm(direction)  # 归一化

    # 计算与水面交点
    t_intersect = (0 - P[2]) / direction[2]
    S = P + direction * t_intersect

    # 计算折射方向
    v_in = direction  # 水中的单位方向向量
    n_normal = np.array([0, 0, -1])  # 法线指向水中
    dir_air = refract(v_in, n_normal, n1, n2)

    if dir_air is None:
        continue  # 发生全内反射时跳过

    # 绘制水下光线段
    ax.plot([P[0], S[0]], [P[1], S[1]], [P[2], S[2]], 'r-', linewidth=1)

    # 绘制空气中的光线段
    length_air = 3  # 折射光线长度
    end_air = S + dir_air * length_air
    ax.plot([S[0], end_air[0]], [S[1], end_air[1]], [S[2], end_air[2]], 'g-', linewidth=1)

    # 绘制反向延长线
    back_length = 5  # 反向延长长度
    back_start = S - dir_air * back_length
    ax.plot([S[0], back_start[0]], [S[1], back_start[1]], [S[2], back_start[2]],
            'g:', linewidth=0.8, alpha=0.7)

# 设置图形属性
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
ax.set_title('三维折射成像示意图')
ax.legend()
ax.set_box_aspect([1,1,1])  # 保持比例
plt.tight_layout()
plt.show()
