# Chromou-VQA
Code for paper: "ChromouVQA: Benchmarking Vision–-Language Models under Chromatic Camouflaged Images"
This repository provides tools to create custom Ishihara-style color blindness test plates. You can generate input images with text, numbers, or polygons, and then convert them into Ishihara plates.

## Workflow Overview

1.  **Generate an Input Image**:
    *   Use `text_to_image.py` for text or numbers.
    *   Use `polygon_generator.py` for regular polygons.
2.  **Convert to Ishihara Plate**:
    *   Use `ishihara_generator.py` to transform the input image.
3.  **Color Sampling Tool (Optional)**:
    *   Use `cie_1931.py` to sample scientifically accurate colors from colorblind confusion lines.

## Requirements

- Python 3.6+
- Pillow (PIL)
- colour-science library (for CIE 1931 functionality)
- matplotlib (for visualization)
- scipy (for geometric calculations)
- See `environment.yml` for specific Python packages.

## Installation

1.  Clone the repository

2.  Set up the Conda environment:
    ```bash
    conda env create -f environment.yml
    conda activate ishihara
    ```
## Step 1: Generate an Input Image

Choose one of the following methods to create your base image.

### Option A: Text/Number Image (`text_to_image.py`)

Generates a high-resolution square image with your specified text or numbers.

**Usage:**
```bash
python text_to_image.py "Your Text" --image-size 500 --output text_output.png
```

**Key Options for `text_to_image.py`:**

| Option            | Description                                    | Default        |
|-------------------|------------------------------------------------|----------------|
| `text`            | Text to render (required)                      | -              |
| `--image-size`    | Size of the square output image (pixels)       | `500`          |
| `--output`        | Output filename                                | `output.png`   |
| `--dpi`           | Resolution (DPI) for sharpness                 | `300`          |
| `--bold-level`    | Boldness: 1 (normal), 2 (bold), 3 (extra bold) | `1`            |
| `--no-line-break` | Disable automatic line breaking for long text  | `False`        |

*For a full list of options, see the script or previous README versions.*
*Automatic line breaking is enabled by default to maximize font size for long text.*

### Option B: Polygon Image (`polygon_generator.py`)

Creates images of regular polygons (e.g., triangles, hexagons).

**Usage:**
```bash
python LLM_color_blindness/polygon_generator.py <num_images> <num_edges> <output_dir>
```

**Example:**
```bash
python LLM_color_blindness/polygon_generator.py 1 6 out_polygons
# Generates: out_polygons/polygon_6_sides_0.png
```

**Arguments for `polygon_generator.py`:**

| Argument           | Description                                      |
|--------------------|--------------------------------------------------|
| `<num_images>`     | Number of images to generate (>=1)               |
| `<num_edges>`      | Number of edges for the polygon (>=3)            |
| `<output_dir>`     | Directory to save the generated image(s)         |

### Option C: CIE 1931 Color Sampling (`cie_1931.py`)

This tool provides scientifically accurate color sampling based on colorblind confusion lines in the CIE 1931 chromaticity diagram. It generates colors that are indistinguishable to people with specific types of color blindness, making it ideal for creating more precise Ishihara plates.

**Usage:**
```bash
python cie_1931.py <colorblind_type> <num_on_color> <num_off_color>
```

**Examples:**

*   Sample colors for protanopia (red-green color blindness):
    ```bash
    python cie_1931.py protan 5 5
    ```
*   Sample colors for deuteranopia:
    ```bash
    python cie_1931.py deutan 3 7
    ```
*   Sample colors for tritanopia (blue-yellow color blindness):
    ```bash
    python cie_1931.py tritan 4 6
    ```

**Arguments for `cie_1931.py`:**

| Argument            | Description                                          | Options                    |
|---------------------|------------------------------------------------------|----------------------------|
| `<colorblind_type>` | Type of color blindness to simulate                 | `protan`, `deutan`, `tritan` |
| `<num_on_color>`    | Number of colors to sample on the confusion line    | Any positive integer       |
| `<num_off_color>`   | Number of colors to sample off the confusion line   | Any positive integer       |

**What it does:**

1.  **Visualizes Confusion Lines**: Displays the CIE 1931 chromaticity diagram with confusion lines specific to the chosen color blindness type.
2.  **Samples Colors**: Randomly selects one confusion line and samples the specified number of colors along it.
3.  **Generates Two Color Sets**: 
    *   Set 1: Colors sampled directly on the confusion line (indistinguishable to colorblind individuals)
    *   Set 2: Colors sampled from the same confusion line but at different positions
4.  **Provides Hex Values**: Outputs the exact hex color codes that can be used in Ishihara plate configurations.
5.  **Shows Visual Plot**: Displays an interactive plot showing the sampled points on the chromaticity diagram.

**Color Blindness Types Supported:**

| Type       | Full Name    | Confusion Point      | Description                           |
|------------|--------------|----------------------|---------------------------------------|
| `protan`   | Protanopia   | (0.747, 0.253)      | Missing L-cones (red-green blindness) |
| `deutan`   | Deuteranopia | (1.080, -0.080)     | Missing M-cones (red-green blindness) |
| `tritan`   | Tritanopia   | (0.171, 0.000)      | Missing S-cones (blue-yellow blindness) |

**Output Example:**
```
Color blindness type: PROTAN
Selected confusion line from wavelength: 505 nm
SET 1 COLORS (5 points on confusion line):
  Point 1: xy=(0.247, 0.713) -> RGB=(0.123, 0.891, 0.456) -> #1fe374
  Point 2: xy=(0.341, 0.623) -> RGB=(0.567, 0.789, 0.234) -> #91c93b
  ...
SET 2 COLORS (5 points on same confusion line):
  Point 1: xy=(0.289, 0.667) -> RGB=(0.345, 0.812, 0.398) -> #58cf65
  ...
```

**Using the Generated Colors:**

The hex color values can be directly used in custom JSON configuration files for `ishihara_generator.py`:

```json
{
  "color_on0": "#1fe374",
  "color_on1": "#91c93b",
  "color_off0": "#58cf65",
  "color_off1": "#7ba142",
  "color_off2": "#9d8f33"
}
```

## Step 2: Generate Ishihara Plate (`ishihara_generator.py`)

Converts your input image (from Step 1 or an external source) into an Ishihara plate.

**Usage:**
```bash
python ishihara_generator.py <input_image_path> <output_image_path> --config <config_file_path>
```

**Examples:**

*   Using a text image:
    ```bash
    python ishihara_generator.py text_output.png ishihara_from_text.png --config protanopia_config.json
    ```
*   Using a polygon image:
    ```bash
    python ishihara_generator.py out_polygons/polygon_6_sides_0.png ishihara_from_polygon.png --config protanopia_config.json
    ```
*   With custom options (bypassing a config file):
    ```bash
    python ishihara_generator.py your_input.png ishihara_custom.png --circular false --min-radius 4
    ```

**Using External Images:**

If using your own image (not from Step 1 scripts):
1.  **Important**: Resize to 512x512 pixels for best results.
    ```bash
    # Example with ImageMagick:
    convert your_image.png -resize 512x512 resized_image.png
    ```
2.  Then, generate the plate:
    ```bash
    python ishihara_generator.py resized_image.png ishihara_output.png
    ```

**Batch Processing:**

Process multiple input images from a folder:
```bash
# For Linux/macOS:
for img in input_folder/*.png; do
    out_name="output_folder/$(basename "$img" .png)_ishihara.png"
    python ishihara_generator.py "$img" --config protanopia_config.json --output "$out_name"
done
```
```batch
@echo off
REM For Windows:
for %%f in (input_folder\*.png) do (
    python ishihara_generator.py "%%f" --config protanopia_config.json --output "output_folder\%%~nf_ishihara.png"
)
```

**Key Options for `ishihara_generator.py`:**

| Option            | Description                                         | Default         |
|-------------------|-----------------------------------------------------|-----------------|
| `<input_image>`   | Path to the input image (required)                  | -               |
| `<output_image>`  | Path for the generated Ishihara plate (required)    | -               |
| `--config`        | Path to a JSON configuration file (e.g., `protanopia_config.json`) | None            |
| `--circular`      | Generate dots in a circular pattern                                | `true`          |
| `--min-radius`    | Minimum radius of dots                                             | Auto-calculated |
| `--max-radius`    | Maximum radius of dots                                             | Auto-calculated |
| `--shape-factory` | Dot shape: 'Circle', 'Regular polygon', etc.                       | `Circle`        |
| `--rotation_angle` | Image rotation angle                                               | 0               |

*For a full list of options, see the script or previous README versions.*

## Predefined Configuration Files

Several JSON configuration files are provided for common color vision deficiencies:
- `protanopia_config.json` (Red-Green, Protanopia)
- `deuteranopia_config.json` (Red-Green, Deuteranopia)
- `viewable_by_all_config.json` (Visible to most)

Explore [franciscouzo.github.io/ishihara](https://franciscouzo.github.io/ishihara/) for an interactive tool to help customize parameters for your own JSON configs.

## Quick Start: Complete Example

**1. Generate an Input Image:**

*   **Text Image:**
    ```bash
    python text_to_image.py "74" --image-size 500 --output num_74.png
    ```
*   **Polygon Image (e.g., a pentagon):**
    ```bash
    python LLM_color_blindness/polygon_generator.py 1 5 poly_images
    # Creates: poly_images/polygon_5_sides_0.png
    ```

**2. Generate Scientifically Accurate Colors (Optional):**

*   **Sample colors for protanopia:**
    ```bash
    python cie_1931.py protan 3 3
    # Outputs hex colors for confusion lines, e.g., #1fe374, #91c93b, etc.
    ```
*   **Create custom config with sampled colors:**
    ```json
    # Save as custom_protan_config.json
    {
      "color_on0": "#1fe374",
      "color_on1": "#91c93b", 
      "color_on2": "#7ba142",
      "color_off0": "#58cf65",
      "color_off1": "#9d8f33",
      "color_off2": "#bc7a21"
    }
    ```

**3. Generate an Ishihara Plate:**

*   **From the Text Image (using predefined config):**
    ```bash
    python ishihara_generator.py num_74.png ishihara_74.png --config protanopia_config.json
    ```
*   **From the Text Image (using CIE 1931 sampled colors):**
    ```bash
    python ishihara_generator.py num_74.png ishihara_74_cie.png --config custom_protan_config.json
    ```
*   **From the Polygon Image:**
    ```bash
    python ishihara_generator.py poly_images/polygon_5_sides_0.png ishihara_poly.png --config protanopia_config.json
    ```

**Complete Workflow with CIE 1931 Color Sampling:**

```bash
# 1. Generate a text image
python text_to_image.py "8" --image-size 500 --output number_8.png

# 2. Sample scientifically accurate colors for deuteranopia
python cie_1931.py deutan 2 4
# Note the hex colors from output, e.g., #a8c945, #6fb156, #4d9a67, #359078, #1d8589, #05799a

# 3. Create custom config file
echo '{
  "color_on0": "#a8c945",
  "color_on1": "#6fb156", 
  "color_off0": "#4d9a67",
  "color_off1": "#359078",
  "color_off2": "#1d8589",
  "color_off3": "#05799a"
}' > custom_deutan_config.json

# 4. Generate Ishihara plate with scientifically accurate colors
python ishihara_generator.py number_8.png ishihara_8_scientific.png --config custom_deutan_config.json
```

## Customizing Colors

Colors for the "figure" (text/shape) and "background" dots are defined in the JSON configuration files (e.g., `protanopia_config.json`) or can be overridden via command-line arguments to `ishihara_generator.py`.

**Scientific Color Selection:**

For the most accurate color blindness testing, use the `cie_1931.py` tool to generate scientifically precise colors based on actual confusion lines in the CIE 1931 chromaticity diagram. This ensures that the colors are truly indistinguishable to people with the specific type of color blindness you're targeting.

**Manual Color Selection:**

Example snippet from `protanopia_config.json`:
```json
{
  "color_on0": "#E96B6C", // Color for figure dots
  "color_on1": "#F7989C",
  "color_off0": "#635A4A", // Color for background dots
  "color_off1": "#817865",
  "color_off2": "#9C9C84"
}
```

Also extracted different color palettes e.g., 'rg_color_palette_1.json', and these files are referenced in config files like 'rg_1_config.json':  "color_palette": "rg_color_palette_2.json"

**Color Configuration Guidelines:**

*   `color_on*`: Colors that form the visible figure/text (usually 1-3 colors)
*   `color_off*`: Colors that form the background pattern (usually 1-5 colors)
*   For scientific accuracy, prefer colors generated by `cie_1931.py`
*   For custom colors, test with actual color blind individuals or simulation tools

## Advanced Usage

For fine-grained control, create custom JSON configuration files or directly modify script parameters.

## License

This project builds upon [franciscouzo's Ishihara generator](https://github.com/franciscouzo/ishihara) and shares its license.

## Dataset Generators

### Find Different Shape Dataset Generator
The `generate_ishihara_dataset_shape_find_difference.py` script generates a dataset where each image contains four shapes, with three being identical and one being different. The task is to identify which quadrant contains the different shape.

Key features:
- Generates images with 4 shapes in quadrants
- Three shapes are identical, one is different
- Supports various shape types (polygons, stars, arrows, etc.)
- Creates corresponding JSON files with questions and answers

Usage:
```bash
python generate_ishihara_dataset_shape_find_difference.py
```

Parameters (configurable in the script):
- `GENERATION_START_INDEX`: Index to start generating the samples
- `NUM_SAMPLES`: Number of samples to generate at once
- `SHAPE_CHOICES`: List of available shape types to randomly choose from
- `POLYGON_IMAGE_DIR`: Output directory for generated images

### Size Comparison Dataset Generator
The `generate_ishihara_dataset_shape_size_comparison.py` script generates a dataset where each image contains four shapes of the same type, with one shape being larger than the others. The task is to identify which quadrant contains the larger shape.

Key features:
- Generates images with 4 shapes of the same type
- One shape is larger than the others
- Supports various shape types (polygons, stars, arrows, etc.)
- Creates corresponding JSON files with questions and answers

Usage:
```bash
python generate_ishihara_dataset_shape_size_comparison.py
```

Parameters (configurable in the script):
- `GENERATION_START_INDEX`: Index to start generating the samples
- `NUM_SAMPLES`: Number of samples to generate at once
- `SHAPE_CHOICES`: List of available shape types to randomly choose from
- `POLYGON_IMAGE_DIR`: Output directory for generated images

### Size Sort Dataset Generator
The `generate_ishihara_dataset_shape_size_sort.py` script generates a dataset where each image contains four shapes of the same type with different sizes randomly placed in the 4 quadrants. The task is to sort the shapes from smallest to largest and provide the quadrant names in the correct order.

Key features:
- Generates images with 4 shapes of the same type with visually distinct sizes
- Sizes are randomly distributed across the 4 quadrants
- Supports various shape types (polygons, stars, arrows, etc.)
- Creates corresponding JSON files with questions and answers
- Uses Ishihara color plates for color blindness testing

Usage:
```bash
python generate_ishihara_dataset_shape_size_sort.py
```

Parameters (configurable in the script):
- `GENERATION_START_INDEX`: Index to start generating the samples
- `NUM_SAMPLES`: Number of samples to generate at once
- `SHAPE_CHOICES`: List of available shape types to randomly choose from
- `POLYGON_IMAGE_DIR`: Output directory for generated images

The answer format is a comma-separated string of quadrant names in order from smallest to largest (e.g., "top_left,bottom_right,top_right,bottom_left").

### Shape Enumeration Dataset Generator
The `generate_ishihara_dataset_shape_enumeration.py` script generates a dataset where each image contains multiple shapes of different types randomly placed in the image. The task is to enumerate the different shapes that appeared in the image, sorted alphabetically.

Key features:
- Generates images with 3-6 shapes of different types
- Shapes are randomly placed with collision avoidance
- Supports various shape types (polygons, stars, arrows, etc.)
- Creates corresponding JSON files with questions and answers
- Uses Ishihara color plates for color blindness testing
- Translates numeric shape types to readable names (3→triangle, 4→square, etc.)
- Provides a list of possible shape names for the model to choose from

Usage:
```bash
python generate_ishihara_dataset_shape_enumeration.py
```

Parameters (configurable in the script):
- `GENERATION_START_INDEX`: Index to start generating the samples
- `NUM_SAMPLES`: Number of samples to generate at once
- `SHAPE_CHOICES`: List of available shape types to randomly choose from
- `POLYGON_IMAGE_DIR`: Output directory for generated images

The answer format is a comma-separated string of unique shape types sorted alphabetically (e.g., "circle,square,star"). Numeric shape types are translated to readable names (3→triangle, 4→square, 5→pentagon, 6→hexagon).

### Mixed Shape Dataset Generator
The `generate_ishihara_dataset_shape_count.py` script generates a dataset where each image contains multiple shapes of different types randomly placed in the image. The task is to identify and count specific shapes.

Key features:
- Generates images with multiple shapes of different types
- Shapes are randomly placed with collision avoidance
- Supports various shape types (polygons, stars, arrows, etc.)
- Creates corresponding JSON files with questions and answers

Usage:
```bash
python generate_ishihara_dataset_shape_count.py
```

Parameters (configurable in the script):
- `GENERATION_START_INDEX`: Index to start generating the samples
- `NUM_SAMPLES`: Number of samples to generate
- `SHAPE_CHOICES`: List of available shape types
- `POLYGON_IMAGE_DIR`: Output directory for generated images


### Output Format
Each dataset generator creates:
1. PNG images with shapes
2. Ishihara color plates
3. JSON files containing:
   - Question ID
   - Image path
   - Task type
   - Question
   - Answer choices
   - Correct answer
   - Ishihara configuration used
