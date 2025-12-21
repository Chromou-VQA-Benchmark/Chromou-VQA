import os
import subprocess
import json
import uuid
import random
import time

# Parameters (edit as needed)
GENERATION_START_INDEX = 0
NUM_SAMPLES = 2
# SHAPE_CHOICES can include both polygon sides (int) and shape names (str)
SHAPE_CHOICES = [3, 4, 5, 6, "parallelogram", "ellipse", "semicircle", "cross", "ring", "heart", "star", "circle", "arrow"]
POLYGON_IMAGE_DIR = 'out_shape_size_comparison_mixed_shape'
SHAPE_CONFIG_DEFAULT = 'shape_config_default.json'

QUESTION_TYPE = 'choice'
TASK_TYPE = 'shape'
SUB_TASK_TYPE = 'size_comparison'
QUESTION_TEMPLATE = "Which quadrant contains the largest shape? Respond with one of the following: 'top_left', 'top_right', 'bottom_left', or 'bottom_right'."
CHOICES = ['top_left', 'top_right', 'bottom_left', 'bottom_right']

os.makedirs(POLYGON_IMAGE_DIR, exist_ok=True)

start_time = time.time()
for i in range(GENERATION_START_INDEX, GENERATION_START_INDEX + NUM_SAMPLES):
    print(f"Processing sample {i}")  # Debug print
    if (i - GENERATION_START_INDEX + 1) % 10 == 0:
        elapsed = (time.time() - start_time) / 60  # minutes
        print(f"Processed {i - GENERATION_START_INDEX + 1} examples, elapsed time: {elapsed:.2f} minutes")
    # Randomly select a shape type
    shape_type = random.choice(SHAPE_CHOICES)
    # Randomly select which shape will be larger
    large_idx = random.randint(0, 3)
    
    poly_img_name = f'shape_size_comparison_{i}.png'
    poly_img_path = os.path.join(POLYGON_IMAGE_DIR, poly_img_name)
    
    # Generate the polygon image
    result = subprocess.run([
        'python', 'generator_size_comparison.py', str(shape_type), poly_img_path, str(large_idx)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Polygon generation failed: {result.stderr}")
    
    question_json = {
        # 'question_id': str(uuid.uuid4()),
        'image_path': os.path.join(POLYGON_IMAGE_DIR, poly_img_name),
        'task_type': TASK_TYPE,
        'sub_task_type': SUB_TASK_TYPE,
        'shape_type': shape_type,
        'question_type': QUESTION_TYPE,
        'question': QUESTION_TEMPLATE,
        'choices': CHOICES,
        'answer': CHOICES[large_idx],
    }

    json_path = os.path.splitext(os.path.join(POLYGON_IMAGE_DIR, poly_img_name))[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(question_json, f, ensure_ascii=False, indent=2) 