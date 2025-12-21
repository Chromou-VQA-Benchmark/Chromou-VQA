import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random
from dataset_shape_generation_utils import get_quadrant_position, generate_shape, setup_image, save_image

def get_quadrant_center(quadrant, img_size, margin):
    w, h = img_size
    cx = margin + (w//4) if quadrant in ['top-left', 'bottom-left'] else w - margin - (w//4)
    cy = margin + (h//4) if quadrant in ['top-left', 'top-right'] else h - margin - (h//4)
    return (cx, cy)

def create_compare_size_shape_image(shape_type, output_path, large_idx, image_size=(512, 512), min_radius=60, max_radius=90, size_ratio=1.5):
    """
    Create an image with 4 shapes of the same type, where one is larger than the others.
    Args:
        shape_type: Type of shape to generate
        output_path: Path to save the output image
        large_idx: Index (0-3) of which quadrant should contain the larger shape
        image_size: Size of the output image
        min_radius: Minimum radius for shapes
        max_radius: Maximum radius for shapes
        size_ratio: Ratio of the larger shape's size to the base size
    """
    # Quadrants in the same order as CHOICES in the dataset generator
    quadrants = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
    w, h = image_size
    margin = 20
    fig, ax = setup_image(image_size)
    
    # Generate a single base radius for all shapes
    base_radius = random.uniform(min_radius, max_radius)
    
    for i, quad in enumerate(quadrants):
        # Use larger radius for the specified quadrant
        radius = base_radius * size_ratio if i == large_idx else base_radius
            
        # Get position for this quadrant
        cx, cy = get_quadrant_position(quad, w, h, margin)
        pixel_center = (cx, cy)
        pixel_radius = radius
        angle = random.uniform(0, 2 * np.pi)
        
        # Generate shape vertices
        pixel_vertices = generate_shape(shape_type, pixel_center, pixel_radius, angle)
        if pixel_vertices is not None:
            polygon = Polygon(pixel_vertices, closed=True, fill=True, color='black')
            ax.add_patch(polygon)
    
    save_image(fig, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python polygon_generator_size_comparison.py <shape_type> <output_path> <large_idx>")
        sys.exit(1)
    
    shape_type = sys.argv[1]
    output_path = sys.argv[2]
    large_idx = int(sys.argv[3])
    
    create_compare_size_shape_image(shape_type, output_path, large_idx) 