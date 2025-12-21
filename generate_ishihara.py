import os
import subprocess
import json
import uuid
import glob
import re
from multiprocessing import Pool, cpu_count, freeze_support
import time
import random

# Top parameter: set color level to 'easy', 'medium', or 'hard'
color_level = 'hard'  # Change to 'medium' or 'hard' as needed

# Parameters for batch processing
START_INDEX = 0  # inclusive
NUM_FILES = 300  # number of files to process
NUM_WORKERS = min(cpu_count(), 6)  # Use up to 6 cores, or all available cores if less than 6

# Input and output parameters
TASK_NAME = 'shape_size_comparison' # 'shape_count', 'shape_enumeration', 'shape_find_difference', 'shape_size_comparison', 'shape_size_sort'
INPUT_DIR = 'out_' + TASK_NAME + "_mixed_shape"
# New output structure: easy/shape_size_comparison/
OUTPUT_DIR = os.path.join(color_level, TASK_NAME)

# Specify the desired palette order based on color_level
if color_level == 'easy':
    palette_names = ['color_palette_7.json', 'color_palette_11.json', 'color_palette_13.json']
elif color_level == 'medium':
    palette_names = ['color_palette_9.json', 'color_palette_12.json', 'color_palette_16.json']
elif color_level == 'hard':
    palette_names = ['color_palette_1.json', 'color_palette_2.json', 'color_palette_5.json']
else:
    raise ValueError(f"Unknown color_level: {color_level}. Use 'easy', 'medium', or 'hard'.")

palette_dir = os.path.join('ishihara_color_config', color_level)
color_palette_files = [os.path.join(palette_dir, name) for name in palette_names]

SHAPE_CONFIG_CHOICES = ['shape_config_star.json', 'shape_config_cross.json', 'shape_config_triangle.json']

def extract_index(filename):
    match = re.search(TASK_NAME + r'_(\d+)\.png', filename)
    return int(match.group(1)) if match else -1

def process_single_file(args):
    """Process a single file - this function will be called by worker processes"""
    png_file, index = args
    
    filename = os.path.basename(png_file)
    
    # Get corresponding JSON file
    json_file = os.path.join(INPUT_DIR, filename.replace('.png', '.json'))
    
    if not os.path.exists(json_file):
        return f"Warning: No JSON file found for {filename}, skipping..."
    
    # Get color palette for this index (cycle through the mapping)
    palette_file = color_palette_files[index % len(color_palette_files)]
    
    result_msg = f"Processing {filename} (index {index}) -> {palette_file}"
    
    # Randomly select a shape config file for this image
    shape_config_file = random.choice(SHAPE_CONFIG_CHOICES)
    try:
        # Load the original JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            original_json = json.load(f)
        
        # Load the randomly selected shape config
        with open(shape_config_file, 'r') as f:
            default_config = json.load(f)
        
        # Create Ishihara config
        ishihara_config = default_config.copy()
        ishihara_config['color_palette'] = palette_file
        
        # Write temp config file for Ishihara generation
        temp_config_path = f'temp_config_{index}.json'
        with open(temp_config_path, 'w') as f:
            json.dump(ishihara_config, f, indent=2)
        
        # Generate Ishihara plate
        ishihara_filename = f'ishihara_{filename}'
        ishihara_path = os.path.join(OUTPUT_DIR, ishihara_filename)
        
        subprocess.run([
            'python', 'ishihara_generator.py', 
            png_file, ishihara_path, 
            '--config', temp_config_path
        ], check=True, capture_output=True)
        
        # Create new JSON with Ishihara data
        new_json = original_json.copy()
        new_json['question_id'] = str(uuid.uuid4())
        
        # New image_path format: "easy/shape_size_comparison/ishihara_shape_size_comparison_X.png"
        new_json['image_path'] = f"{color_level}/{TASK_NAME}/{ishihara_filename}"
        
        # Add source_image_path pointing to the original file
        new_json['source_image_path'] = f"{INPUT_DIR}/{filename}"
        
        new_json['ishihara_config'] = ishihara_config
        
        # Write new JSON file
        new_json_path = os.path.splitext(ishihara_path)[0] + '.json'
        with open(new_json_path, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, ensure_ascii=False, indent=2)
        
        result_msg += f" ✓ Generated: {ishihara_filename}"
        
    except subprocess.CalledProcessError as e:
        result_msg += f" ✗ Failed: {e}"
    except Exception as e:
        result_msg += f" ✗ Error: {e}"
    finally:
        # Clean up temp config file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
    
    return result_msg

def main():
    # Create output directory and subdirectories
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all PNG files from input directory
    png_files = glob.glob(os.path.join(INPUT_DIR, TASK_NAME + '_*.png'))
    png_files.sort(key=extract_index)

    # Only process the specified range
    end_index = START_INDEX + NUM_FILES
    png_files = png_files[START_INDEX:end_index]

    print(f"Found {len(png_files)} shape size comparison files to process (from index {START_INDEX} to {end_index-1})")
    print(f"Using color palettes: {palette_names} in {palette_dir}.")
    print(f"Using {NUM_WORKERS} worker processes for parallel processing")
    print(f"Output will be organized in: {OUTPUT_DIR}")

    # Prepare arguments for multiprocessing
    args_list = []
    for i, png_file in enumerate(png_files):
        filename = os.path.basename(png_file)
        index = int(filename.replace(TASK_NAME + '_', '').replace('.png', ''))
        args_list.append((png_file, index))

    # Process files in parallel
    start_time = time.time()
    with Pool(processes=NUM_WORKERS) as pool:
        results = pool.map(process_single_file, args_list)

    # Print results
    for i, result in enumerate(results):
        if i % 10 == 0:
            print(result)

    elapsed_time = time.time() - start_time
    print(f"\nGeneration complete in {elapsed_time:.2f} seconds!")
    print(f"Check the '{OUTPUT_DIR}' directory for results.")
    print("Files are organized in the new structure: {color_level}/{task_name}/")

if __name__ == '__main__':
    freeze_support()  # Required for macOS multiprocessing
    main() 