import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random

def generate_regular_polygon(num_edges, center=(0.5, 0.5), radius=0.4):
    """
    Generate vertices for a regular polygon with specified number of edges.
    
    Args:
        num_edges: Number of edges in the polygon
        center: Center point of the polygon (x, y) as fraction of image size
        radius: Radius of the polygon as fraction of image size
        
    Returns:
        Array of vertices for the polygon
    """
    if num_edges < 3:
        raise ValueError("Number of edges must be greater than or equal to 3.")
        
    # Generate a random starting angle for rotation
    start_angle = random.uniform(0, 2 * np.pi)
    
    # Generate the angles for each vertex
    angles = np.linspace(start_angle, start_angle + 2 * np.pi, num_edges, endpoint=False)
    
    # Calculate the vertices
    vertices = []
    for angle in angles:
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        vertices.append((x, y))
    
    return np.array(vertices)

def create_polygon_image(num_edges, output_path, image_size=(512, 512)):
    """
    Create and save an image of a regular polygon.
    
    Args:
        num_edges: Number of edges in the polygon
        output_path: Path to save the output image
        image_size: Size of the output image (width, height)
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(image_size[0]/100, image_size[1]/100))
    
    # Generate polygon vertices
    vertices = generate_regular_polygon(num_edges)
    
    # Create polygon
    polygon = Polygon(vertices, closed=True, fill=True, color='black')
    
    # Add polygon to plot
    ax.add_patch(polygon)
    
    # Set axis limits
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Remove axes and set equal aspect ratio
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set tight layout
    plt.tight_layout(pad=0)
    
    # Save figure
    plt.savefig(output_path, bbox_inches='tight', dpi=100)
    plt.close(fig)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <number_of_images> <number_of_edges> <output_directory>")
        print("Example: python polygon_generator.py 1 6 out  # Generates one hexagon")
        sys.exit(1)

    # Get the number of images to generate
    number_of_images = int(sys.argv[1])
    if number_of_images < 1:
        raise ValueError("Number of images must be greater than or equal to 1.")

    # Get the number of edges for the regular polygon
    number_of_edges = int(sys.argv[2])
    if number_of_edges < 3:
        raise ValueError("Number of edges must be greater than or equal to 3.")

    # Get the output directory
    output_directory = sys.argv[3]

    for ni in range(number_of_images):
        # Generate the image path
        image_path = f"{output_directory}/polygon_{number_of_edges}_sides_{ni}.png"
        
        # Create the polygon image
        create_polygon_image(number_of_edges, image_path)