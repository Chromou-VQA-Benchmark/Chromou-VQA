import numpy as np
import matplotlib.pyplot as plt

from shape_utils import (
    generate_regular_polygon, generate_star, generate_circle, generate_parallelogram,
    generate_ellipse, generate_semicircle, generate_cross, generate_ring,
    generate_heart, generate_arrow, generate_sector
)

def get_quadrant_position(quad, w, h, margin):
    """
    Get the center position for a given quadrant.
    Args:
        quad: Quadrant name ('top_left', 'top_right', 'bottom_left', 'bottom_right')
        w, h: Image width and height
        margin: Margin from edges
    Returns:
        (cx, cy): Center coordinates for the quadrant
    """
    if quad == 'top_left':
        cx = margin + (w//4)
        cy = h - margin - (h//4)
    elif quad == 'top_right':
        cx = w - margin - (w//4)
        cy = h - margin - (h//4)
    elif quad == 'bottom_left':
        cx = margin + (w//4)
        cy = margin + (h//4)
    else:  # bottom_right
        cx = w - margin - (w//4)
        cy = margin + (h//4)
    return cx, cy

def generate_shape(shape_type, center, radius, angle=0):
    """
    Generate vertices for a shape.
    Args:
        shape_type: Type of shape (int for polygon sides, str for special shapes)
        center: (x, y) center coordinates
        radius: Size of the shape
        angle: Rotation angle in radians
    Returns:
        vertices: Array of (x, y) coordinates for the shape
    """
    if (isinstance(shape_type, int)) or (isinstance(shape_type, str) and str(shape_type).isdigit()):
        num_edges = int(shape_type)
        vertices = generate_regular_polygon(num_edges, center=center, radius=radius)
        rel_vertices = vertices - np.array(center)
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        rotated_vertices = np.dot(rel_vertices, rot_matrix.T) + np.array(center)
        return rotated_vertices
    else:
        if shape_type == "star":
            vertices = generate_star(center=center, radius=radius)
        elif shape_type == "arrow":
            vertices = generate_arrow(center=center, radius=radius)
        elif shape_type == "circle":
            vertices = generate_circle(center=center, radius=radius)
        elif shape_type == "parallelogram":
            side = radius * np.sqrt(1.5)
            vertices = generate_parallelogram(center=center, width=side, height=side, slant=0.4)
        elif shape_type == "ellipse":
            vertices = generate_ellipse(center=center, width=2*radius, height=1.2*radius)
        elif shape_type == "semicircle":
            vertices = generate_semicircle(center=center, radius=radius)
        elif shape_type == "cross":
            vertices = generate_cross(center=center, size=2*radius, thickness=0.5*radius)
        elif shape_type == "ring":
            vertices = generate_ring(center=center, outer_radius=radius, inner_radius=0.6*radius)
        elif shape_type == "heart":
            vertices = generate_heart(center=center, radius=radius * 0.06)
        elif shape_type == "sector":
            vertices = generate_sector(center=center, radius=radius)
        else:
            return None
        rel_vertices = vertices - np.array(center)
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        return np.dot(rel_vertices, rot_matrix.T) + np.array(center)

def setup_image(image_size=(512, 512)):
    """
    Set up a matplotlib figure for drawing shapes.
    Args:
        image_size: (width, height) of the image
    Returns:
        fig, ax: Matplotlib figure and axes
    """
    w, h = image_size
    fig, ax = plt.subplots(figsize=(w/100, h/100))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax

def save_image(fig, output_path):
    """
    Save the figure to a file.
    Args:
        fig: Matplotlib figure
        output_path: Path to save the image
    """
    plt.tight_layout(pad=0)
    plt.savefig(output_path, bbox_inches='tight', dpi=100)
    plt.close(fig) 