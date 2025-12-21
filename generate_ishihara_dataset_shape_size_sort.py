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
POLYGON_IMAGE_DIR = 'out_shape_size_sort_mixed_shape'
SHAPE_CONFIG_DEFAULT = 'shape_config_default.json'

QUESTION_TYPE = 'generation'
TASK_TYPE = 'shape'
SUB_TASK_TYPE = 'size_sort'
QUESTION_TEMPLATE = 'Sort the shapes from smallest to largest. Provide the quadrant names in order from smallest to largest, separated by commas (e.g., "top_left,bottom_right,top_right,bottom_left").'

os.makedirs(POLYGON_IMAGE_DIR, exist_ok=True)

start_time = time.time()
for i in range(GENERATION_START_INDEX, GENERATION_START_INDEX + NUM_SAMPLES):
    print(f"Processing sample {i}")  # Debug print
    if (i - GENERATION_START_INDEX + 1) % 10 == 0:
        elapsed = (time.time() - start_time) / 60  # minutes
        print(f"Processed {i - GENERATION_START_INDEX + 1} examples, elapsed time: {elapsed:.2f} minutes")
    
    # Randomly select a shape type from SHAPE_CHOICES
    shape_type = random.choice(SHAPE_CHOICES)
    
    # Randomly assign size indices to quadrants (0=smallest, 3=largest)
    size_indices = [0, 1, 2, 3]  # 0=smallest, 1=small, 2=large, 3=largest
    random.shuffle(size_indices)
    
    size_assignments = {
        'top_left': size_indices[0],
        'top_right': size_indices[1],
        'bottom_left': size_indices[2],
        'bottom_right': size_indices[3]
    }
    
    # Calculate the sorted order from smallest to largest
    sorted_quadrants = sorted(size_assignments.keys(), key=lambda x: size_assignments[x])
    sorted_order = ','.join(sorted_quadrants)
    
    poly_img_name = f'shape_size_sort_{i}.png'
    poly_img_path = os.path.join(POLYGON_IMAGE_DIR, poly_img_name)
    
    # Generate the polygon image with the assigned sizes
    result = subprocess.run([
        'python', 'generator_size_sort.py', str(shape_type), poly_img_path,
        str(size_assignments['top_left']), str(size_assignments['top_right']),
        str(size_assignments['bottom_left']), str(size_assignments['bottom_right'])
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Polygon generation failed: {result.stderr}")
    
    # Load the default config
    with open(SHAPE_CONFIG_DEFAULT, 'r') as f:
        config = json.load(f)

    question_json = {
        # 'question_id': str(uuid.uuid4()),
        'image_path': os.path.join(POLYGON_IMAGE_DIR, poly_img_name),
        'task_type': TASK_TYPE,
        'sub_task_type': SUB_TASK_TYPE,
        'shape_type': shape_type,
        'question_type': QUESTION_TYPE,
        'question': QUESTION_TEMPLATE,
        'answer': sorted_order,
    }

    json_path = os.path.splitext(os.path.join(POLYGON_IMAGE_DIR, poly_img_name))[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(question_json, f, ensure_ascii=False, indent=2) 