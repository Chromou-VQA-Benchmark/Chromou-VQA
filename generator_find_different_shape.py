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

def create_find_different_shape_image(same_shape, diff_shape, output_path, diff_idx, image_size=(512, 512), min_radius=60, max_radius=90):
    """
    Create an image with 4 shapes, where 3 are the same and 1 is different.
    Args:
        same_shape: Type of shape for the 3 identical shapes
        diff_shape: Type of shape for the 1 different shape
        output_path: Path to save the output image
        diff_idx: Index (0-3) of which quadrant should contain the different shape
        image_size: Size of the output image
        min_radius: Minimum radius for shapes
        max_radius: Maximum radius for shapes
    """
    # Quadrants in the same order as CHOICES in the dataset generator
    quadrants = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
    w, h = image_size
    margin = 20
    fig, ax = setup_image(image_size)
    
    for i, quad in enumerate(quadrants):
        # Choose shape type based on whether this is the different quadrant
        shape_type = diff_shape if i == diff_idx else same_shape
        radius = random.uniform(min_radius, max_radius)
            
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
    if len(sys.argv) != 5:
        print("Usage: python polygon_generator_find_different_shape.py <same_shape> <diff_shape> <output_path> <diff_idx>")
        sys.exit(1)
    
    same_shape = sys.argv[1]
    diff_shape = sys.argv[2]
    output_path = sys.argv[3]
    diff_idx = int(sys.argv[4])
    
    create_find_different_shape_image(same_shape, diff_shape, output_path, diff_idx) 