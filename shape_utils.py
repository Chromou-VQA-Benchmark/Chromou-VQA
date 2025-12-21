import numpy as np
import random

def generate_regular_polygon(num_edges, center=(0.5, 0.5), radius=0.4):
    if num_edges < 3:
        raise ValueError("Number of edges must be greater than or equal to 3.")
    start_angle = random.uniform(0, 2 * np.pi)
    angles = np.linspace(start_angle, start_angle + 2 * np.pi, num_edges, endpoint=False)
    vertices = []
    for angle in angles:
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        vertices.append((x, y))
    return np.array(vertices)

def generate_star(center, radius, num_points=5):
    cx, cy = center
    vertices = []
    for i in range(2 * num_points):
        angle = i * np.pi / num_points
        r = radius if i % 2 == 0 else radius * 0.4
        x = cx + r * np.cos(angle)
        y = cy + r * np.sin(angle)
        vertices.append((x, y))
    return np.array(vertices)

def generate_circle(center, radius, num_points=40):
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    return np.array([(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles])

def generate_parallelogram(center, width, height, slant=0.4):
    cx, cy = center
    w, h = width / 2, height / 2
    dx = slant * w
    return np.array([
        (cx - w + dx, cy - h),
        (cx + w + dx, cy - h),
        (cx + w - dx, cy + h),
        (cx - w - dx, cy + h)
    ])

def generate_ellipse(center, width, height, num_points=40):
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    return np.array([(cx + width/2 * np.cos(a), cy + height/2 * np.sin(a)) for a in angles])

def generate_semicircle(center, radius, num_points=24):
    cx, cy = center
    angles = np.linspace(0, np.pi, num_points)
    points = [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]
    points.append((cx, cy))
    return np.array(points)

def generate_cross(center, size, thickness):
    cx, cy = center
    t = thickness / 2
    s = size / 2
    # 12-point polygon for a cross
    return np.array([
        (cx - t, cy - s), (cx + t, cy - s), (cx + t, cy - t), (cx + s, cy - t),
        (cx + s, cy + t), (cx + t, cy + t), (cx + t, cy + s), (cx - t, cy + s),
        (cx - t, cy + t), (cx - s, cy + t), (cx - s, cy - t), (cx - t, cy - t)
    ])

def generate_ring(center, outer_radius, inner_radius, num_points=100):
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, num_points + 1, endpoint=True)
    outer = [(cx + outer_radius * np.cos(a), cy + outer_radius * np.sin(a)) for a in angles]
    inner = [(cx + inner_radius * np.cos(a), cy + inner_radius * np.sin(a)) for a in angles[::-1]]
    return np.array(outer + inner)

def generate_heart(center, radius, num_points=100):
    cx, cy = center
    t = np.linspace(0, 2 * np.pi, num_points)
    x = radius * 16 * np.sin(t) ** 3
    # Use a more traditional heart shape formula for y
    y = -radius * (12 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - 0.5 * np.cos(4 * t))
    return np.column_stack((cx + x, cy + y))

def generate_arrow(center, radius):
    cx, cy = center
    shaft_width = 0.2 * radius
    shaft_length = 0.4 * radius
    head_width = 0.5 * radius
    head_length = 0.4 * radius

    # Arrow points upward, centered at (cx, cy)
    vertices = [
        (cx, cy - shaft_length - head_length),  # tip of arrow head
        (cx - head_width, cy - shaft_length),   # left corner of arrow head
        (cx - shaft_width, cy - shaft_length),  # left side of shaft at head
        (cx - shaft_width, cy + shaft_length),  # left side of shaft at tail
        (cx + shaft_width, cy + shaft_length),  # right side of shaft at tail
        (cx + shaft_width, cy - shaft_length),  # right side of shaft at head
        (cx + head_width, cy - shaft_length),   # right corner of arrow head
    ]
    return np.array(vertices)

def generate_sector(center, radius, num_points=30):
    cx, cy = center
    start_angle = random.uniform(0, 2 * np.pi)
    angle_span = random.uniform(np.pi/4, 2*np.pi/3)
    end_angle = start_angle + angle_span
    angles = np.linspace(start_angle, end_angle, num_points)
    points = [(cx, cy)]
    points += [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]
    return np.array(points) 