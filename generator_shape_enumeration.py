import sys
import os
import numpy as np
import random
from matplotlib.patches import Polygon
from dataset_shape_generation_utils import generate_shape, setup_image, save_image

def translate_shape_type(shape_type):
    """
    Translate numeric shape types to their string names.
    Args:
        shape_type: Shape type (int or str)
    Returns:
        String name of the shape
    """
    if isinstance(shape_type, int) or (isinstance(shape_type, str) and shape_type.isdigit()):
        num_edges = int(shape_type)
        if num_edges == 3:
            return "triangle"
        elif num_edges == 4:
            return "square"
        elif num_edges == 5:
            return "pentagon"
        elif num_edges == 6:
            return "hexagon"
        else:
            return f"unsupported polygon type!"
    else:
        return str(shape_type)

def generate_random_shapes(shape_assignments, image_size=(512, 512), min_radius=0.12, max_radius=0.2, max_attempts=2000):
    """
    Generate random shapes with collision avoidance based on provided assignments.
    Args:
        shape_assignments: List of shape types to generate
        image_size: Size of the output image
        min_radius: Minimum radius for shapes (relative to image size)
        max_radius: Maximum radius for shapes (relative to image size)
        max_attempts: Maximum number of attempts to place each shape
    Returns:
        List of shape vertices and their types
    """
    shapes = []
    centers_radii = []
    width, height = image_size
    
    for shape_type in shape_assignments:
        for attempt in range(max_attempts):
            # Generate random position and size
            radius = random.uniform(min_radius, max_radius) * min(width, height)
            margin = radius + 2
            cx = random.uniform(margin / width, 1 - margin / width)
            cy = random.uniform(margin / height, 1 - margin / height)
            center = (cx, cy)
            angle = random.uniform(0, 2 * np.pi)
            
            # Check for collisions with existing shapes
            too_close = False
            for (other_cx, other_cy, other_radius) in centers_radii:
                dist = ((cx - other_cx) * width) ** 2 + ((cy - other_cy) * height) ** 2
                min_dist = ((radius + other_radius) * 1.2 + 2) ** 2
                if dist < min_dist:
                    too_close = True
                    break
            if too_close:
                continue
            
            # Generate shape vertices
            pixel_center = (cx * width, cy * height)
            pixel_radius = radius
            pixel_vertices = generate_shape(shape_type, pixel_center, pixel_radius, angle)
            
            if pixel_vertices is None:
                continue
                
            # Check if shape is within image bounds
            if (pixel_vertices < 0).any() or (pixel_vertices[:, 0] > width).any() or (pixel_vertices[:, 1] > height).any():
                continue
                
            shapes.append((pixel_vertices, shape_type))
            centers_radii.append((cx, cy, radius))
            break
        else:
            print(f"WARNING: Could not place shape {shape_type} after {max_attempts} attempts.")
            
    return shapes

def create_shape_enumeration_image(shape_assignments, output_path, image_size=(512, 512), min_radius=0.12, max_radius=0.2):
    """
    Create an image with multiple randomly placed shapes of different types.
    Args:
        shape_assignments: List of shape types to generate
        output_path: Path to save the output image
        image_size: Size of the output image
        min_radius: Minimum radius for shapes (relative to image size)
        max_radius: Maximum radius for shapes (relative to image size)
    Returns:
        List of unique shape types that appeared in the image (translated to string names)
    """
    fig, ax = setup_image(image_size)
    shapes = generate_random_shapes(shape_assignments, image_size, min_radius, max_radius)
    
    shape_types = []
    for poly, shape_type in shapes:
        polygon = Polygon(poly, closed=True, fill=True, color='black')
        ax.add_patch(polygon)
        shape_types.append(shape_type)
    
    # Get unique shape types, translate them to string names, and sort alphabetically
    unique_shapes = sorted(list(set(shape_types)), key=lambda x: str(x))
    translated_shapes = [translate_shape_type(shape) for shape in unique_shapes]
    
    save_image(fig, output_path)
    return translated_shapes

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python generator_shape_enumeration.py <shape1> <shape2> ... <output_path>")
        print("Example: python generator_shape_enumeration.py 4 star circle output.png")
        sys.exit(1)

    # Parse shape assignments from command line arguments
    shape_assignments = []
    output_path = None
    
    for arg in sys.argv[1:]:
        if arg.endswith('.png'):
            output_path = arg
        else:
            # Accept both numbers (x-sided polygon) and strings (e.g., star, arrow)
            shape_type = int(arg) if arg.isdigit() else arg
            shape_assignments.append(shape_type)
    
    if output_path is None:
        print("Error: No output path specified")
        sys.exit(1)
    
    create_shape_enumeration_image(shape_assignments, output_path)
