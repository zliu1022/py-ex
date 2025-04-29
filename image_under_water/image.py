#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define refractive indices
n_water = 1.333  # Refractive index of water
n_air = 1.000    # Refractive index of air

# Define water surface position
z_water_surface = 0

# Define position of the object underwater
object_point = np.array([0, 0, -5])  # (x, y, z)

# Define the position of the eye
eye_position = np.array([0, 0, 5])

# Define the directions of the light rays emitted from the object point (with various angles)
theta = np.linspace(-np.pi/4, np.pi/4, 200)  # Increased number of rays
phi = np.linspace(-np.pi/4, np.pi/4, 200)    # Increased number of rays

# Create the figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot water surface
xx, yy = np.meshgrid(np.linspace(-10, 10, 10), np.linspace(-10, 10, 10))
zz = np.zeros_like(xx) + z_water_surface
ax.plot_surface(xx, yy, zz, alpha=0.3, color='cyan')

# Plot the underwater object point
ax.scatter(object_point[0], object_point[1], object_point[2], color='red', s=100, label='Underwater Object')

# Plot the eye position
ax.scatter(eye_position[0], eye_position[1], eye_position[2], color='green', s=100, label='Eye Position')

# Initialize list to store virtual image points
virtual_points = []

# Loop over each light ray
for t in theta:
    for p in phi:
        # Calculate the direction vector of the light ray in water
        direction_in_water = np.array([
            np.sin(t)*np.cos(p),
            np.sin(t)*np.sin(p),
            np.cos(t)
        ])
        direction_in_water = direction_in_water / np.linalg.norm(direction_in_water)

        # Calculate intersection point with water surface
        # Parametric equation: r = object_point + s * direction_in_water
        # Solve for s such that z = z_water_surface
        if direction_in_water[2] == 0:
            continue
        s = (z_water_surface - object_point[2]) / direction_in_water[2]
        if s <= 0:
            continue  # The ray does not reach the water surface
        intersection_point = object_point + s * direction_in_water

        # Calculate incidence angle theta1
        cos_theta1 = abs(direction_in_water[2])  # cos(theta1) = |direction_in_water[2]|
        sin_theta1 = np.sqrt(1 - cos_theta1**2)
        theta1 = np.arccos(cos_theta1)

        # Use Snell's Law to calculate refraction angle theta2
        sin_theta2 = (n_water / n_air) * sin_theta1
        # Total internal reflection check
        if sin_theta2 > 1:
            continue  # Total internal reflection occurs, skip this ray
        theta2 = np.arcsin(sin_theta2)
        cos_theta2 = np.cos(theta2)

        # Calculate refracted ray direction in air
        # Adjust the x and y components based on the ratio of sin(theta2)/sin(theta1)
        if sin_theta1 != 0:
            ratio = sin_theta2 / sin_theta1
            direction_in_air = np.array([
                direction_in_water[0] * ratio,
                direction_in_water[1] * ratio,
                np.sign(direction_in_water[2]) * cos_theta2
            ])
        else:
            direction_in_air = np.array([0, 0, np.sign(direction_in_water[2]) * cos_theta2])
        direction_in_air = direction_in_air / np.linalg.norm(direction_in_air)

        # Ensure that the refracted ray is going upwards
        if direction_in_air[2] <= 0:
            continue

        # Check if the refracted ray reaches the eye
        delta = eye_position - intersection_point
        t_eye = np.dot(delta, direction_in_air) / np.dot(direction_in_air, direction_in_air)
        if t_eye <= 0:
            continue  # Refracted ray does not reach the eye

        # Calculate the point on the refracted ray that is closest to the eye position
        point_on_ray = intersection_point + t_eye * direction_in_air
        distance_to_eye = np.linalg.norm(point_on_ray - eye_position)
        if distance_to_eye > 0.1:  # Adjust the tolerance as needed
            continue

        # Plot the underwater light ray
        ax.plot(
            [object_point[0], intersection_point[0]],
            [object_point[1], intersection_point[1]],
            [object_point[2], intersection_point[2]],
            color='blue', linewidth=1
        )

        # Plot the refracted ray in air
        ax.plot(
            [intersection_point[0], eye_position[0]],
            [intersection_point[1], eye_position[1]],
            [intersection_point[2], eye_position[2]],
            color='orange', linewidth=1
        )

        # Extend the refracted ray backward to find the virtual image
        t_virtual = - (intersection_point[2] - object_point[2]) / direction_in_air[2]
        if t_virtual >= 0:
            virtual_point = intersection_point + t_virtual * direction_in_air
            virtual_points.append(virtual_point)

            # Plot the extension of the refracted ray (dashed line)
            ax.plot(
                [intersection_point[0], virtual_point[0]],
                [intersection_point[1], virtual_point[1]],
                [intersection_point[2], virtual_point[2]],
                color='gray', linestyle='dashed', linewidth=10
            )

# Plot virtual image points
if virtual_points:
    virtual_points = np.array(virtual_points)
    ax.scatter(virtual_points[:,0], virtual_points[:,1], virtual_points[:,2], color='purple', s=50, label='Virtual Image')

# Set axis labels
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# Set title
ax.set_title('3D Image Formation According to Snell\'s Law')

# Set legend
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

# Set display range
ax.set_xlim(-7, 7)
ax.set_ylim(-7, 7)
ax.set_zlim(-10, 10)

# Show grid
ax.grid(True)

# Show the figure
plt.show()
