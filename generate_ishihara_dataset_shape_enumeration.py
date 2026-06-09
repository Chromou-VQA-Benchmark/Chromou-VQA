import os
import subprocess
import json
import uuid
import random
import time

# Parameters (edit as needed)
GENERATION_START_INDEX = 0
NUM_SAMPLES = 300
# SHAPE_CHOICES can include both polygon sides (int) and shape names (str)
SHAPE_CHOICES = [3, 4, 5, 6, "parallelogram", "ellipse", "semicircle", "cross", "ring", "heart", "star", "circle", "arrow"]
POLYGON_IMAGE_DIR = 'out_shape_enumeration_mixed_shape'
SHAPE_CONFIG_DEFAULT = 'shape_config_default.json'

QUESTION_TYPE = 'generation'
TASK_TYPE = 'shape'
SUB_TASK_TYPE = 'enumeration' 
QUESTION_TEMPLATE = 'This image contains multiple shapes formed by colored dot patterns, similar to a color vision test. Look carefully at ALL areas of the image to identify shapes formed by different color clusters against the background. Some shapes may be more subtle or harder to distinguish than others. Enumerate ALL the different shapes that appear in the image, sorted alphabetically. Do NOT count the individual dots themselves - only identify the larger shapes formed by groups of colored dots. Look for shapes that may be formed by different color combinations (red/pink dots, orange/yellow dots, etc.) and different color contrasts against the green background. Choose from the following shape names: arrow, circle, cross, ellipse, heart, hexagon, parallelogram, pentagon, ring, semicircle, square, star, triangle. Provide the shape names separated by commas (e.g., "circle,square,star").'

# List of all possible shape names for the model to choose from
POSSIBLE_SHAPE_NAMES = [
    "arrow", "circle", "cross", "ellipse", "heart", "hexagon", "parallelogram", 
    "pentagon", "ring", "semicircle", "square", "star", "triangle"
]

def translate_shape_type(shape_type):
    """
    Translate numeric shape types to their string names.
    Args:
        shape_type: Shape type (int or str)
    Returns:
        String name of the shape
    """
    if shape_type == "3":
        return "triangle"
    elif shape_type == "4":
        return "square"
    elif shape_type == "5":
        return "pentagon"
    elif shape_type == "6":
        return "hexagon"
    else:
        return shape_type

os.makedirs(POLYGON_IMAGE_DIR, exist_ok=True)

start_time = time.time()
for i in range(GENERATION_START_INDEX, GENERATION_START_INDEX + NUM_SAMPLES):
    print(f"Processing sample {i}") 
    if (i - GENERATION_START_INDEX + 1) % 10 == 0:
        elapsed = (time.time() - start_time) / 60  # minutes
        print(f"Processed {i - GENERATION_START_INDEX + 1} examples, elapsed time: {elapsed:.2f} minutes")
    # Randomly select number of shapes and shape types
    num_shapes = random.randint(2, 4)   # Generate 2-4 shapes
    selected_shapes = random.sample(SHAPE_CHOICES, num_shapes)
    
    # Calculate the unique shapes and their translated names
    # Convert all shapes to strings first to avoid sorting issues with mixed types
    unique_shapes = list(set(selected_shapes))
    # Translate 3, 4, 5 to their shape names for the answer string
    translated_shapes = [translate_shape_type(str(shape)) for shape in unique_shapes]
    unique_shapes_str = ','.join(sorted(translated_shapes, key=lambda x: str(x)))
    
    poly_img_name = f'shape_enumeration_{i}.png'
    poly_img_path = os.path.join(POLYGON_IMAGE_DIR, poly_img_name)
    
    # Generate the polygon image with the assigned shapes
    cmd = ['python', 'generator_shape_enumeration.py'] + [str(shape) for shape in selected_shapes] + [poly_img_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("CMD:", cmd)
        raise RuntimeError(f"Polygon generation failed: {result.stderr}")
    
    # # Format the question with available shape names
    formatted_question = QUESTION_TEMPLATE.format(shape_names=', '.join(POSSIBLE_SHAPE_NAMES))
    
    question_json = {
        # 'question_id': str(uuid.uuid4()),
        'image_path': os.path.join(POLYGON_IMAGE_DIR, poly_img_name),
        'task_type': TASK_TYPE,
        'sub_task_type': SUB_TASK_TYPE,
        'shape_types': selected_shapes,
        'question_type': QUESTION_TYPE,
        'question': formatted_question,
        'possible_shapes': POSSIBLE_SHAPE_NAMES,
        'answer': unique_shapes_str,
    }

    json_path = os.path.splitext(os.path.join(POLYGON_IMAGE_DIR, poly_img_name))[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(question_json, f, ensure_ascii=False, indent=2) 