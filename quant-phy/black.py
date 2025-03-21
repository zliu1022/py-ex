#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# 定义普朗克黑体辐射函数
def planck(wavelength, T):
    """
    计算黑体在给定波长和温度下的辐射能量密度

    参数：
    wavelength : 波长（米）
    T         : 温度（开尔文）

    返回：
    辐射能量密度
    """
    h = 6.62607015e-34  # 普朗克常数 (J·s)
    c = 3.0e8           # 光速 (m/s)
    k = 1.380649e-23    # 玻尔兹曼常数 (J/K)

    exponent = (h * c) / (wavelength * k * T)
    intensity = (2 * h * c**2) / (wavelength**5) / (np.exp(exponent) - 1)
    return intensity

# 设置波长范围（400 nm 到 3000 nm）
wavelength_nm = np.linspace(100, 3000, 1000)  # 波长范围从100nm到3000nm
wavelength_m = wavelength_nm * 1e-9        # 转换为米

# 设置不同温度
temperatures = [3000, 4000, 5000, 6000]  # 温度范围从3000K到6000K

plt.figure(figsize=(10, 6))

for T in temperatures:
    intensity = planck(wavelength_m, T)
    plt.plot(wavelength_nm, intensity, label=f'{T} K')

plt.title('普朗克黑体辐射谱')
plt.xlabel('波长 (nm)')
plt.ylabel('辐射能量密度 (W·sr⁻¹·m⁻³)')
plt.legend()
plt.grid(True)
plt.xlim(100, 3000)
plt.ylim(0, None)
plt.show()

