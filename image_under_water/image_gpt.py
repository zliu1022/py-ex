#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

def refract(v, n, n1, n2):
    v = v / np.linalg.norm(v)
    cos1 = -np.dot(n, v)
    sin2_t2 = (n1 / n2)**2 * (1 - cos1**2)
    if sin2_t2 > 1:
        return None  # Total internal reflection
    cos2 = np.sqrt(1 - sin2_t2)
    return (n1 / n2) * v + (n1 / n2 * cos1 - cos2) * n

# Parameters
obj = np.array([0.0, 0.0, -1.0])       # underwater object point
eye = np.array([0.5, 0.0,  2.0])       # eye position above water
n_water = 1.33
n_air = 1.0
normal = np.array([0.0, 0.0, 1.0])     # normal of water surface (z=0)

# Sampling directions in water (gamma cone)
theta_max = np.deg2rad(20)
phis = np.linspace(0, 2*np.pi, 8)
thetas = np.linspace(0, theta_max, 4)
rays = []
for theta in thetas:
    for phi in phis:
        dx = np.sin(theta) * np.cos(phi)
        dy = np.sin(theta) * np.sin(phi)
        dz = np.cos(theta)
        rays.append(np.array([dx, dy, dz]))

# Set up 3D plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Plot water surface (z=0)
xx, yy = np.meshgrid(np.linspace(-1, 1, 10), np.linspace(-1, 1, 10))
zz = np.zeros_like(xx)
ax.plot_surface(xx, yy, zz, alpha=0.3)

# Plot object, eye, and virtual image
ax.scatter(*obj, marker='o', s=60, label='Object (underwater)')
ax.scatter(*eye, marker='^', s=60, label='Eye (above water)')
# Virtual image apparent depth
z_image = obj[2] * (n_air / n_water)
virtual = np.array([0.0, 0.0, z_image])
ax.scatter(*virtual, marker='x', s=80, label='Virtual Image')

# Plot incident, refracted, and back-traced rays
for v in rays:
    # Intersection with water surface
    t = -obj[2] / v[2]
    P = obj + t * v
    # Incident ray (underwater)
    ax.plot([obj[0], P[0]], [obj[1], P[1]], [obj[2], P[2]])
    # Refract into air
    refr = refract(v, normal, n_water, n_air)
    if refr is None:
        continue
    # Refracted ray (towards eye direction)
    L = (eye[2] - P[2]) / refr[2] * 0.9
    Q = P + refr * L
    ax.plot([P[0], Q[0]], [P[1], Q[1]], [P[2], Q[2]])
    # Back-traced from eye (dashed)
    rev = -refr
    L2 = (P[2] - eye[2]) / rev[2] * 0.9
    R = eye + rev * L2
    ax.plot([eye[0], R[0]], [eye[1], R[1]], [eye[2], R[2]], linestyle='--')

# Labels and legend
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.title('3D Refraction Illustration: Object, Rays, Eye, and Virtual Image')
plt.tight_layout()
plt.show()

