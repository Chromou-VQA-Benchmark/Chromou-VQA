import sys
import random
import numpy as np
from matplotlib.patches import Polygon
from dataset_shape_generation_utils import get_quadrant_position, generate_shape, setup_image, save_image

def create_size_sort_shape_image(shape_type, output_path, size_assignments, image_size=(512, 512), min_radius=30, max_radius=90):
    """
    Create an image with 4 shapes of the same type with different sizes placed according to the provided assignments.
    Args:
        shape_type: Type of shape to generate
        output_path: Path to save the output image
        size_assignments: Dictionary mapping quadrant names to size indices (0=smallest, 3=largest)
        image_size: Size of the output image
        min_radius: Minimum radius for the smallest shape
        max_radius: Maximum radius for the largest shape
    """
    # Quadrants
    quadrants = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
    w, h = image_size
    margin = 20
    fig, ax = setup_image(image_size)
    
    # Generate 4 visually distinct sizes with larger gaps between them
    size_ratios = [0.2, 0.4, 0.7, 1.0]  # More distinct size differences
    sizes = [min_radius + (max_radius - min_radius) * ratio for ratio in size_ratios]
    
    for quad in quadrants:
        size_index = size_assignments[quad]
        radius = sizes[size_index]
            
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
    if len(sys.argv) != 7:
        print("Usage: python generator_size_sort.py <shape_type> <output_path> <top_left_size> <top_right_size> <bottom_left_size> <bottom_right_size>")
        print("Size values: 0=smallest, 1=small, 2=large, 3=largest")
        sys.exit(1)
    
    shape_type = sys.argv[1]
    output_path = sys.argv[2]
    
    # Parse size assignments from command line arguments
    size_assignments = {
        'top_left': int(sys.argv[3]),
        'top_right': int(sys.argv[4]),
        'bottom_left': int(sys.argv[5]),
        'bottom_right': int(sys.argv[6])
    }
    
    create_size_sort_shape_image(shape_type, output_path, size_assignments) 