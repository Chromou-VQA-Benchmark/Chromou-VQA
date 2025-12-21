import os
import subprocess
import json
import uuid
import random
from shutil import copyfile
import time

# Parameters
GENERATION_START_INDEX = 0
NUM_SAMPLES = 300

# 3, 4, 5, 6 means polygons of that many sides
SHAPE_CHOICES = [3, 4, 5, 6, "parallelogram", "ellipse", "semicircle", "cross", "ring", "heart", "star", "circle", "arrow"]
POLYGON_IMAGE_DIR = 'out_shape_count_mixed_shape'
SHAPE_CONFIG_DEFAULT = 'shape_config_default.json'

QUESTION_TYPE = 'generation'  # choice / generation
TASK_TYPE = 'shape'
SUB_TASK_TYPE = 'count'
QUESTION_TEMPLATE = 'Count the total number of large shapes (constructed by smaller colored dots) in the image. Do not count the individual dots themselves. Respond with a single number only, like: 4.'

os.makedirs(POLYGON_IMAGE_DIR, exist_ok=True)

start_time = time.time()
for i in range(GENERATION_START_INDEX, GENERATION_START_INDEX + NUM_SAMPLES):
    print(f"Processing sample {i}")  # Debug print
    if (i - GENERATION_START_INDEX + 1) % 10 == 0:
        elapsed = (time.time() - start_time) / 60  # minutes
        print(f"Processed {i - GENERATION_START_INDEX + 1} examples, elapsed time: {elapsed:.2f} minutes")
    # 1. Generate random shape types for this image
    NUM_POLYGONS = random.choice([2, 3, 4])
    this_shapes = [random.choice(SHAPE_CHOICES) for _ in range(NUM_POLYGONS)]
    shape_choices_str = ','.join(str(e) for e in this_shapes)
    poly_img_name = f'shape_count_{i}.png'
    poly_img_path = os.path.join(POLYGON_IMAGE_DIR, poly_img_name)

    # Call polygon_generator_shape_count.py with shape_choices as a string argument
    subprocess.run([
        'python', 'generator_shape_count.py', str(NUM_POLYGONS), shape_choices_str, POLYGON_IMAGE_DIR, poly_img_name
    ], check=True)

    # Load the default config
    with open(SHAPE_CONFIG_DEFAULT, 'r') as f:
        config = json.load(f)
    

    question_json = {
        # 'question_id': str(uuid.uuid4()),
        'image_path': os.path.join(POLYGON_IMAGE_DIR, poly_img_name),
        'task_type': TASK_TYPE,
        'sub_task_type': SUB_TASK_TYPE,
        'shape_types': this_shapes,
        'question_type': QUESTION_TYPE,
        'question': QUESTION_TEMPLATE,
        'answer': str(NUM_POLYGONS),
    }

    json_path = os.path.splitext(os.path.join(POLYGON_IMAGE_DIR, poly_img_name))[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(question_json, f, ensure_ascii=False, indent=2) 