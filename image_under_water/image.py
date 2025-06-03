#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# Refractive indices
n_air = 1.000
n_water = 1.333

# Positions
z_water_surface = 0
object_depth = -5  # Depth of the object below the water surface
eye_height = 5     # Height of the eye above the water surface

# Define positions
object_point = np.array([0, object_depth])  # (x, z)
eye_position = np.array([0, eye_height])

# Field of view and number of rays
fov = np.pi / 3  # 60 degrees field of view
num_rays = 20    # Number of rays to plot

# Generate angles within the field of view
theta = np.linspace(-fov / 2, fov / 2, num_rays)

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))

# Plot water surface
ax.axhline(y=z_water_surface, color='blue', linestyle='-', linewidth=2, label='Water Surface')

# Plot object and eye
ax.plot(object_point[0], object_point[1], 'ro', markersize=10, label='Underwater Object')
ax.plot(eye_position[0], eye_position[1], 'go', markersize=10, label='Eye Position')

# Initialize virtual image points list
virtual_image_points = []

# Loop over each ray
for t in theta:
    # Direction vector of the ray in air (from eye to water surface)
    direction_in_air = np.array([
        np.sin(t),    # Horizontal component
        -np.cos(t)    # Vertical component (negative because ray goes down)
    ])
    direction_in_air = direction_in_air / np.linalg.norm(direction_in_air)

    # Calculate intersection with water surface
    s = (z_water_surface - eye_position[1]) / direction_in_air[1]
    if s <= 0:
        continue  # Ray does not intersect the water surface in front of the eye
    intersection_point = eye_position + s * direction_in_air

    # Calculate angle of incidence
    cos_theta1 = -direction_in_air[1]  # Negative because normal is upward
    sin_theta1 = np.sqrt(1 - cos_theta1**2)

    # Apply Snell's Law to find the angle of refraction
    sin_theta2 = (n_air / n_water) * sin_theta1
    if abs(sin_theta2) > 1:
        continue  # Total internal reflection (should not occur from air to water)
    cos_theta2 = np.sqrt(1 - sin_theta2**2)

    # Direction of refracted ray in water
    direction_in_water = np.array([
        (n_air / n_water) * direction_in_air[0],
        -cos_theta2   # Negative because ray continues downwards in water
    ])
    direction_in_water = direction_in_water / np.linalg.norm(direction_in_water)

    # Calculate intersection with the underwater object depth
    t_object = (object_point[1] - intersection_point[1]) / direction_in_water[1]
    if t_object <= 0:
        continue  # The refracted ray does not reach the object
    point_on_object = intersection_point + t_object * direction_in_water

    # Plot incident ray in air
    ax.plot(
        [eye_position[0], intersection_point[0]],
        [eye_position[1], intersection_point[1]],
        color='orange',
        linewidth=2
    )

    # Plot refracted ray in water
    ax.plot(
        [intersection_point[0], point_on_object[0]],
        [intersection_point[1], point_on_object[1]],
        color='blue',
        linewidth=2
    )

    # Extend the incident ray backward to find the virtual image
    t_virtual = (object_point[1] - intersection_point[1]) / direction_in_air[1]
    virtual_point = intersection_point + t_virtual * direction_in_air
    virtual_image_points.append(virtual_point)

    # Plot the extension of the incident ray (virtual ray) as a dashed line
    ax.plot(
        [intersection_point[0], virtual_point[0]],
        [intersection_point[1], virtual_point[1]],
        color='gray',
        linestyle='dashed',
        linewidth=1
    )

# Plot all virtual image points
virtual_image_points = np.array(virtual_image_points)
if virtual_image_points.size > 0:
    ax.plot(
        virtual_image_points[:,0],
        virtual_image_points[:,1],
        'm*',
        markersize=10,
        label='Virtual Image'
    )

# Labels and title
ax.set_xlabel('Horizontal Position (X)')
ax.set_ylabel('Vertical Position (Z)')
ax.set_title('Refraction at Water Surface and Virtual Image Formation')

# Legend
ax.legend(loc='upper right')

# Axes limits
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

# Grid
ax.grid(True)

# Show plot
plt.show()
