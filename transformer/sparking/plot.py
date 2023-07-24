#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Data
x = [1, 3, 5, 6, 8]
y1 = [2, 3, 5, 18, 1]
y2 = [3, 5, 6, 8, 1]
y3 = [5, 1, 2, 3, 4]
y4 = [9, 7, 2, 3, 1]

# Smooth interpolation function
def smooth_interpolation(x, y):
    xnew = np.linspace(min(x), max(x), 300)
    spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline interpolation
    ynew = spl(xnew)
    return xnew, ynew

# Smoothed curves and error bars
x1_new, y1_new = smooth_interpolation(x, y1)
x2_new, y2_new = smooth_interpolation(x, y2)
x3_new, y3_new = smooth_interpolation(x, y3)
x4_new, y4_new = smooth_interpolation(x, y4)

# TODO: Add random error bars, zig-zag effect, baseline, pie chart, and animation

# Create subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 10))

# Plot y1 and y2 in the same subplot (ax1)
ax1.plot(x1_new, y1_new, label='bob')
ax1.plot(x2_new, y2_new, label='alice')
ax1.set_xlabel('time')
ax1.set_ylabel('money')
ax1.legend()

# Plot y3 in another subplot (ax2)
ax2.plot(x3_new, y3_new, label='bilbo')
ax2.set_xlabel('time')
ax2.set_ylabel('money')
ax2.legend()

# Plot y4 in the subplot below (ax3)
ax3.plot(x4_new, y4_new, label='allie')
ax3.set_xlabel('time')
ax3.set_ylabel('money')
ax3.legend()

# TODO: Add pie chart to ax4

plt.show()

