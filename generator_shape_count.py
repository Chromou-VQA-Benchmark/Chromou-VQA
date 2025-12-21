import sys
import os
import numpy as np
import random
from matplotlib.patches import Polygon
from dataset_shape_generation_utils import generate_shape, setup_image, save_image

def generate_random_shapes(num_polygons, shape_choices, image_size=(512, 512), min_radius=0.12, max_radius=0.2, max_attempts=2000):
    """
    Generate random shapes with collision avoidance.
    Args:
        num_polygons: Number of shapes to generate
        shape_choices: List of shape types to choose from
        image_size: Size of the output image
        min_radius: Minimum radius for shapes (relative to image size)
        max_radius: Maximum radius for shapes (relative to image size)
        max_attempts: Maximum number of attempts to place each shape
    Returns:
        List of shape vertices and their centers/radii
    """
    polygons = []
    centers_radii = []
    width, height = image_size
    
    for idx in range(num_polygons):
        for attempt in range(max_attempts):
            # Choose shape type
            shape_type = shape_choices[idx] if len(shape_choices) == num_polygons else random.choice(shape_choices)
            
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
                
            polygons.append(pixel_vertices)
            centers_radii.append((cx, cy, radius))
            break
        else:
            print(f"WARNING: Could not place shape {shape_type} after {max_attempts} attempts.")
            
    return polygons

def create_multiple_polygons_image(num_polygons, shape_choices, output_path, image_size=(512, 512), min_radius=0.12, max_radius=0.2):
    """
    Create an image with multiple randomly placed shapes.
    Args:
        num_polygons: Number of shapes to generate
        shape_choices: List of shape types to choose from
        output_path: Path to save the output image
        image_size: Size of the output image
        min_radius: Minimum radius for shapes (relative to image size)
        max_radius: Maximum radius for shapes (relative to image size)
    """
    fig, ax = setup_image(image_size)
    polygons = generate_random_shapes(num_polygons, shape_choices, image_size, min_radius, max_radius)
    
    for poly in polygons:
        polygon = Polygon(poly, closed=True, fill=True, color='black')
        ax.add_patch(polygon)
    
    save_image(fig, output_path)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python polygon_generator_mixed_shape.py <num_polygons> <shape_choices> <output_directory> [output_filename]")
        print("Example: python polygon_generator_mixed_shape.py 3 3,4,star out_polygons out.png  # 3 shapes: triangle, quadrilateral, star")
        sys.exit(1)

    number_of_polygons = int(sys.argv[1])
    shape_choices_str = sys.argv[2]
    output_directory = sys.argv[3]
    output_filename = None
    if len(sys.argv) > 4:
        output_filename = sys.argv[4]

    # Accept both numbers (x-sided polygon) and strings (e.g., star, arrow)
    shape_choices = [int(e) if e.isdigit() else e for e in shape_choices_str.split(",") if e.strip()]

    os.makedirs(output_directory, exist_ok=True)
    if output_filename:
        image_path = os.path.join(output_directory, output_filename)
    else:
        shape_choices_label = '_'.join(str(e) for e in shape_choices)
        image_path = os.path.join(output_directory, f"{number_of_polygons}_shapes_{shape_choices_label}_0.png")

    create_multiple_polygons_image(number_of_polygons, shape_choices, image_path) 