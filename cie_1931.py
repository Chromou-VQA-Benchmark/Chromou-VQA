import numpy as np
import matplotlib.pyplot as plt
import argparse
import random
import json
from colour import wavelength_to_XYZ, XYZ_to_xy, xy_to_XYZ, XYZ_to_sRGB, xyY_to_XYZ
from colour.plotting import plot_chromaticity_diagram_CIE1931
from scipy.spatial import ConvexHull
from matplotlib.path import Path

def xy_to_hex_randY(x, y, Ymin_ratio=0.3, seed=None):
    """
    将 (x, y) 随机亮度映射到可显示的 sRGB（0-1），再转 Hex。
    Ymin_ratio: 随机亮度下限占 Y_max 的比例 (0~1)。
    返回 (hex_color, rgb)；若 xy 色域外则返回 (None, None)。
    """
    rng = np.random.default_rng(seed)

    # 1) 先假设 Y=1 计算一次 XYZ
    XYZ1 = xyY_to_XYZ([x, y, 1.0])

    # 2) 线性 sRGB，不 gamma
    rgb_lin1 = XYZ_to_sRGB(XYZ1, apply_cctf_encoding=False)

    # 3) 若有负值则色域外
    if (rgb_lin1 < 0).any():
        return None, None

    # 4) 最大可用亮度缩放因子 Y_max
    m = rgb_lin1.max()
    Y_max = 1.0 / m if m > 1 else 1.0

    # 5) 在 [Y_min, Y_max] 随机取亮度
    Y_min = Ymin_ratio * Y_max
    Y_rand = rng.uniform(Y_min, Y_max)

    # 6) 用随机亮度重新算 XYZ、线性 sRGB
    XYZ = xyY_to_XYZ([x, y, Y_rand])
    rgb_lin = XYZ_to_sRGB(XYZ, apply_cctf_encoding=False)

    # 7) γ-编码 (sRGB EOTF)
    rgb = np.where(
        rgb_lin <= 0.0031308,
        12.92 * rgb_lin,
        1.055 * np.power(rgb_lin, 1/2.4) - 0.055
    )
    rgb = np.clip(rgb, 0, 1)

    # 8) 转 Hex
    rgb8 = (rgb * 255 + 0.5).astype(int)
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb8)

    return hex_color, rgb

def get_cie1931_boundary():
    """Get the boundary of the CIE1931 chromaticity diagram."""
    # Get spectral locus points (visible wavelengths)
    wavelengths = np.arange(380, 781, 5)  # 5nm steps for better resolution
    spectral_xy = np.array([XYZ_to_xy(wavelength_to_XYZ(wl)) for wl in wavelengths])
    
    # The boundary consists of the spectral locus plus the purple line
    # Purple line connects the endpoints (shortest wavelength to longest wavelength)
    boundary_points = np.vstack([spectral_xy, spectral_xy[0:1]])  # Close the loop
    
    return boundary_points

def is_within_cie1931(x, y, boundary_path=None, sRGB_path=None):
    """Check if a point (x, y) is within the CIE1931 chromaticity diagram and optionally within sRGB gamut."""
    if boundary_path is None:
        boundary_points = get_cie1931_boundary()
        boundary_path = Path(boundary_points)
    
    # Basic constraints
    if x < 0 or y < 0 or x + y > 1:
        return False
    
    # Check if point is within the spectral locus boundary
    if not boundary_path.contains_point([x, y]):
        return False
    
    # Check if point is within sRGB gamut (if specified)
    if sRGB_path is not None:
        if not sRGB_path.contains_point([x, y]):
            return False
    
    return True

def find_line_boundary_intersections(start_point, end_point, boundary_points, sRGB_path=None):
    """Find intersection points of a line with the CIE1931 boundary and optionally sRGB gamut."""
    from matplotlib.path import Path
    
    boundary_path = Path(boundary_points)
    
    # Sample many points along the line to find valid segments
    t_values = np.linspace(0, 1, 1000)
    line_points = np.array([start_point + t * (end_point - start_point) for t in t_values])
    
    # Check which points are valid (within CIE1931 and optionally within sRGB)
    valid_mask = np.array([is_within_cie1931(p[0], p[1], boundary_path, sRGB_path) for p in line_points])
    
    if not np.any(valid_mask):
        return None, None  # No valid segment
    
    # Find the continuous valid segment(s)
    valid_indices = np.where(valid_mask)[0]
    
    if len(valid_indices) == 0:
        return None, None
    
    # Get the first and last valid points (assuming one continuous segment)
    first_valid_idx = valid_indices[0]
    last_valid_idx = valid_indices[-1]
    
    # Get corresponding t values
    t_start = t_values[first_valid_idx]
    t_end = t_values[last_valid_idx]
    
    # Calculate actual intersection points
    valid_start = start_point + t_start * (end_point - start_point)
    valid_end = start_point + t_end * (end_point - start_point)
    
    return valid_start, valid_end

def sample_points_on_line_uniform(start_point, end_point, num_points, sRGB_path=None):
    """Uniformly sample points along the valid segment of a line within CIE1931 boundary and optionally within sRGB gamut."""
    if num_points <= 0:
        return np.array([]).reshape(0, 2)
    
    # Get CIE1931 boundary
    boundary_points = get_cie1931_boundary()
    
    # Find the valid segment of the line within the boundary (and optionally sRGB gamut)
    valid_start, valid_end = find_line_boundary_intersections(start_point, end_point, boundary_points, sRGB_path)
    
    if valid_start is None or valid_end is None:
        print(f"Warning: No valid segment found on the confusion line")
        return np.array([]).reshape(0, 2)
    
    # Uniformly sample along the valid segment
    if num_points == 1:
        # If only one point, sample at the middle
        t_values = np.array([0.5])
    else:
        # Uniformly distribute points along the valid segment
        t_values = np.linspace(0, 1, num_points)
    
    # Generate points along the valid segment
    points = np.array([valid_start + t * (valid_end - valid_start) for t in t_values])
    
    return points

def sample_distinct_points_on_line(start_point, end_point, num_set1, num_set2, sRGB_path=None):
    """Sample points uniformly along the valid segment, then randomly assign to two groups."""
    total_points = num_set1 + num_set2
    
    if total_points <= 0:
        return np.array([]).reshape(0, 2), np.array([]).reshape(0, 2)
    
    # Get all points uniformly sampled along the valid segment
    all_points = sample_points_on_line_uniform(start_point, end_point, total_points, sRGB_path)
    
    if len(all_points) == 0:
        return np.array([]).reshape(0, 2), np.array([]).reshape(0, 2)
    
    # Randomly assign points to two groups without replacement
    indices = np.random.permutation(len(all_points))
    
    # Split indices for the two sets
    set1_indices = indices[:num_set1]
    set2_indices = indices[num_set1:num_set1+num_set2]
    
    # Get the corresponding points
    set1_points = all_points[set1_indices] if len(set1_indices) > 0 else np.array([]).reshape(0, 2)
    set2_points = all_points[set2_indices] if len(set2_indices) > 0 else np.array([]).reshape(0, 2)
    
    return set1_points, set2_points

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sample colors from colorblind confusion lines')
    parser.add_argument('colorblind_type', type=str, choices=['protan', 'deutan', 'tritan'], 
                       help='Type of color blindness: protan, deutan, or tritan')
    parser.add_argument('num_on_color', type=int, help='Number of points to sample on the confusion line')
    parser.add_argument('num_off_color', type=int, help='Number of points to sample off the confusion line')
    
    args = parser.parse_args()
    
    # Define copunctal points and wavelength ranges for different color blindness types
    colorblind_config = {
        'protan': {
            'copunctal': np.array([0.747, 0.253]),
            'wavelengths': np.arange(480, 520, 5),  # Green to red wavelengths
            'title': 'Protanopia'
        },
        'deutan': {
            'copunctal': np.array([1.080, -0.080]),  # Fixed the y-coordinate
            'wavelengths': np.arange(490, 520, 5),  # Blue-green to red wavelengths
            'title': 'Deuteranopia'
        },
        'tritan': {
            'copunctal': np.array([0.171, 0.000]),
            'wavelengths': np.arange(520, 610, 5),  # UV to green wavelengths
            'title': 'Tritanopia'
        }
    }
    
    # Get configuration for the selected color blindness type
    config = colorblind_config[args.colorblind_type]
    copunctal = config['copunctal']
    wavelengths = config['wavelengths']
    title = config['title']

    # ------------------------------------------------------------------
    # 1) Draw the base chromaticity diagram and keep the fig/axes handles
    # ------------------------------------------------------------------
    fig, ax = plot_chromaticity_diagram_CIE1931(
        standalone=False,  # <- don't call plt.show() yet
        show_grid=True,
    )

    # ------------------------------------------------------------------
    # 2) Protan copunctal point  (Smith & Pokorny, 1975; Wyszecki & Stiles)
    # ------------------------------------------------------------------

    ax.plot(*copunctal, "ko", ms=5)
    ax.annotate(f"{title}\ncopunctal", copunctal,
                xytext=(copunctal[0] + 0.05, copunctal[1] + 0.05),
                arrowprops=dict(arrowstyle="->", lw=.8))

    # ------------------------------------------------------------------
    # 3) Pick anchor wavelengths on the spectral locus
    # ------------------------------------------------------------------
    print(f"Color blindness type: {args.colorblind_type.upper()}")
    print(f"Copunctal point: ({copunctal[0]:.3f}, {copunctal[1]:.3f})")
    print(f"Wavelengths: {wavelengths}")
    xy_locus = np.array([XYZ_to_xy(wavelength_to_XYZ(wl))
                         for wl in wavelengths])

    # ------------------------------------------------------------------
    # 4) Plot the confusion lines
    # ------------------------------------------------------------------
    confusion_lines = []
    for xy in xy_locus:
        ax.plot([copunctal[0], xy[0]],
                [copunctal[1], xy[1]],
                color="gray", lw=0.5, alpha=.5)
        confusion_lines.append((copunctal, xy))
    
    # Define sRGB gamut boundary
    sRGB_xy = np.array([[0.640, 0.330],   # R
                    [0.300, 0.600],   # G
                    [0.150, 0.060]])  # B
    ax.plot(*np.vstack([sRGB_xy, sRGB_xy[0]]).T, '--', color='white', label='sRGB gamut')
    
    # Create sRGB path for point-in-gamut checking
    sRGB_path = Path(np.vstack([sRGB_xy, sRGB_xy[0]]))  # Close the loop

    # ------------------------------------------------------------------
    # 5) Randomly select one confusion line
    # ------------------------------------------------------------------
    selected_index = np.random.randint(0, len(confusion_lines))
    selected_line = confusion_lines[selected_index]
    start_point, end_point = selected_line
    
    # Highlight the selected confusion line
    ax.plot([start_point[0], end_point[0]],
            [start_point[1], end_point[1]],
            color="red", lw=2.0, alpha=1.0, label="Selected confusion line")

    # ------------------------------------------------------------------
    # 6) Sample points on and off the confusion line
    # ------------------------------------------------------------------
    
    # Sample points ON the confusion line (first set)
    on_line_points, off_line_points = sample_distinct_points_on_line(start_point, end_point, args.num_on_color, args.num_off_color, sRGB_path)

    # Plot sampled points
    if len(on_line_points) > 0:
        ax.scatter(on_line_points[:, 0], on_line_points[:, 1], 
                  c='blue', s=50, label=f'Set 1: {args.num_on_color} points', zorder=5, marker='o')
    
    if len(off_line_points) > 0:
        ax.scatter(off_line_points[:, 0], off_line_points[:, 1], 
                  c='red', s=50, label=f'Set 2: {args.num_off_color} points', zorder=5, marker='s')

    # ------------------------------------------------------------------
    # 7) Convert points to hex colors and print results
    # ------------------------------------------------------------------
    
    print(f"\nSelected confusion line from wavelength: {wavelengths[selected_index]} nm")
    print(f"Line endpoints: ({start_point[0]:.3f}, {start_point[1]:.3f}) to ({end_point[0]:.3f}, {end_point[1]:.3f})")
    
    # Store colors for JSON output
    color_palette = {
        "n_colors_on": args.num_on_color,
        "n_colors_off": args.num_off_color
    }
    
    valid_on_colors = []
    valid_off_colors = []
    
    print(f"\nSET 1 COLORS ({args.num_on_color} points on confusion line):")
    for i, point in enumerate(on_line_points):
        hex_color, rgb = xy_to_hex_randY(point[0], point[1], Ymin_ratio=0.4)
        if hex_color is None:
            continue  # 丢弃色域外点或重新取样
        valid_on_colors.append(hex_color)
        print(f"  Point {i+1}: xy=({point[0]:.3f}, {point[1]:.3f}) -> RGB=({rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f}) -> {hex_color}")
    
    print(f"\nSET 2 COLORS ({args.num_off_color} points on same confusion line):")
    for i, point in enumerate(off_line_points):
        # hex_color, rgb = xy_to_hex(point[0], point[1])
        hex_color, rgb = xy_to_hex_randY(point[0], point[1], Ymin_ratio=0.4)
        if hex_color is None:
            continue  # 丢弃色域外点或重新取样
        valid_off_colors.append(hex_color)
        print(f"  Point {i+1}: xy=({point[0]:.3f}, {point[1]:.3f}) -> RGB=({rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f}) -> {hex_color}")
    
    # Add valid colors to the palette dictionary
    for i, color in enumerate(valid_on_colors):
        color_palette[f"color_on{i}"] = color
    
    for i, color in enumerate(valid_off_colors):
        color_palette[f"color_off{i}"] = color
    
    # Update actual counts in case some colors were invalid
    color_palette["n_colors_on"] = len(valid_on_colors)
    color_palette["n_colors_off"] = len(valid_off_colors)
    
    # Generate JSON filename based on colorblind type and color counts
    json_filename = f"cie_{args.colorblind_type}_{len(valid_on_colors)}_{len(valid_off_colors)}.json"
    
    # Save to JSON file
    with open(json_filename, 'w') as f:
        json.dump(color_palette, f, indent=4)
    
    print(f"\nColor palette saved to: {json_filename}")
    print(f"Total valid colors: {len(valid_on_colors)} on-line, {len(valid_off_colors)} off-line")

    # ------------------------------------------------------------------
    # 8) Add legend and show plot
    # ------------------------------------------------------------------
    ax.legend()
    plt.title(f'{title} Confusion Line with Sampled Points\n'
             f'Set 1: {len(on_line_points)} points (blue circles), Set 2: {len(off_line_points)} points (red squares)')
    plt.show()

if __name__ == "__main__":
    main()