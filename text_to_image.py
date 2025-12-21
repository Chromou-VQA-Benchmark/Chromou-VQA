from PIL import Image, ImageDraw, ImageFont
import argparse
import textwrap

def create_text_image(text, image_size=500, output_file="output.png", dpi=300, 
                      text_color=(0, 0, 0), bg_color=(255, 255, 255), 
                      padding_percent=10, font_path=None, stroke_width=0, bold_level=1, 
                      auto_line_break=True):
    """
    Create a high-resolution square PNG image with bold text that fills the image.
    
    Args:
        text (str): The text to render
        image_size (int): Size of the square output image in pixels
        output_file (str): Output filename
        dpi (int): Resolution in dots per inch (higher values create sharper images)
        text_color (tuple): RGB color tuple for text
        bg_color (tuple): RGB color tuple for background
        padding_percent (int): Percentage of padding around text (1-20)
        font_path (str): Path to custom font file (.ttf). Uses default bold if None.
        stroke_width (int): Width of text outline for additional boldness (0 for none)
        bold_level (int): Level of boldness: 1=normal, 2=bold, 3=extra bold (by repeated drawing)
        auto_line_break (bool): Whether to automatically add line breaks to maximize font size
    """
    # Validate padding percentage
    padding_percent = max(1, min(20, padding_percent))
    
    # Calculate the ratio between the requested DPI and standard 72 DPI
    dpi_ratio = dpi / 72.0
    
    # Create the base image at the requested size
    img = Image.new('RGB', (image_size, image_size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate padding in pixels
    padding_px = int(image_size * (padding_percent / 100))
    
    # Available space for text (accounting for padding)
    available_width = image_size - (2 * padding_px)
    available_height = image_size - (2 * padding_px)
    
    # Choose a font (default bold system font if no path provided)
    if font_path:
        try:
            test_font = lambda size: ImageFont.truetype(font_path, size)
        except IOError:
            print(f"Font file {font_path} not found, using default font")
            test_font = lambda size: ImageFont.truetype("Arial Bold", size) if "Arial Bold" in ImageFont.truetype.__doc__ else ImageFont.load_default()
    else:
        # Try to use a bold system font
        try:
            test_font = lambda size: ImageFont.truetype("Arial Bold", size)
        except IOError:
            try:
                test_font = lambda size: ImageFont.truetype("Arial", size)
            except IOError:
                test_font = lambda size: ImageFont.load_default()
                print("Default system fonts not found, using fallback font")

    # Check if we have multiple words and should try line breaking
    words = text.split()
    if len(words) <= 1 or not auto_line_break:
        # Single word or line breaking disabled - use original approach
        optimal_font_size, final_text = find_optimal_font_size_single_line(text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw)
    else:
        # Multiple words - try different line break arrangements
        optimal_font_size, final_text = find_optimal_font_size_with_line_breaks(text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw)
    
    # Use the optimal font size
    scaled_optimal_size = int(optimal_font_size * dpi_ratio)
    if scaled_optimal_size < 1:
        scaled_optimal_size = 1
    font = test_font(scaled_optimal_size)
    
    # Recalculate text dimensions with the optimal font
    scaled_stroke_width = int(stroke_width * dpi_ratio) if stroke_width > 0 else 0
    
    # For multiline text, we need to calculate the total height differently
    lines = final_text.split('\n')
    total_height = 0
    line_heights = []
    line_widths = []
    
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font, stroke_width=scaled_stroke_width)
        line_width = text_bbox[2] - text_bbox[0]
        line_height = text_bbox[3] - text_bbox[1]
        line_heights.append(line_height)
        line_widths.append(line_width)
        total_height += line_height
    
    # Add some spacing between lines if there are multiple lines
    line_spacing = max(line_heights) * 0.2 if len(lines) > 1 else 0
    total_height += line_spacing * (len(lines) - 1) if len(lines) > 1 else 0
    
    # Find the widest line
    max_width = max(line_widths) if line_widths else 0
    
    # Calculate text position to center it
    start_y = (image_size - total_height) // 2
    
    # Add extra padding for the bold effect if needed
    extra_padding = scaled_stroke_width * 2 + (bold_level - 1) * 4
    
    # Draw each line centered
    current_y = start_y
    for i, line in enumerate(lines):
        line_width = line_widths[i]
        text_x = (image_size - line_width) // 2
        
        # Bold level implementation by drawing multiple times with slight offsets
        text_position = (text_x, current_y)
        
        if bold_level >= 3:  # Extra bold
            offsets = [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1)]
            for offset in offsets[:4]:  # Use first 4 offsets for level 3
                offset_x, offset_y = offset
                pos = (text_position[0] + offset_x, text_position[1] + offset_y)
                draw.text(pos, line, font=font, fill=text_color, stroke_width=scaled_stroke_width, stroke_fill=text_color)
        
        if bold_level >= 2:  # Bold
            offsets = [(0.5, 0.5), (-0.5, 0.5), (0.5, -0.5), (-0.5, -0.5)]
            for offset in offsets:
                offset_x, offset_y = offset
                pos = (text_position[0] + offset_x, text_position[1] + offset_y)
                draw.text(pos, line, font=font, fill=text_color, stroke_width=scaled_stroke_width, stroke_fill=text_color)
        
        # Always draw the main text
        draw.text(text_position, line, font=font, fill=text_color, stroke_width=scaled_stroke_width, stroke_fill=text_color)
        
        # Move to the next line position
        current_y += line_heights[i] + line_spacing
    
    # Save with correct DPI metadata
    img.save(output_file, dpi=(dpi, dpi))
    print(f"Image saved as {output_file} with {dpi} DPI ({image_size}x{image_size} pixels)")
    print(f"Text boldness: {'Normal' if bold_level == 1 else 'Bold' if bold_level == 2 else 'Extra Bold'}, Stroke width: {stroke_width}")
    if '\n' in final_text:
        print(f"Text was formatted with {len(lines)} lines to maximize size")
    
    return output_file

def find_optimal_font_size_single_line(text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw):
    """Find the optimal font size for a single line of text"""
    min_size = 1
    max_size = 1000  # Start with a large maximum
    optimal_font_size = min_size
    
    while min_size <= max_size:
        mid_size = (min_size + max_size) // 2
        
        # Apply DPI scaling to font size
        scaled_size = int(mid_size * dpi_ratio)
        if scaled_size < 1:
            scaled_size = 1
            
        font = test_font(scaled_size)
        
        # Calculate text size with consideration for stroke width
        scaled_stroke_width = int(stroke_width * dpi_ratio) if stroke_width > 0 else 0
        text_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=scaled_stroke_width)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Check if text fits within available space (with a small margin)
        if text_width <= available_width and text_height <= available_height:
            optimal_font_size = mid_size
            min_size = mid_size + 1
        else:
            max_size = mid_size - 1
    
    return optimal_font_size, text

def find_optimal_font_size_with_line_breaks(text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw):
    """Find the optimal font size by trying different line breaking arrangements"""
    words = text.split()
    
    # Try different numbers of words per line
    best_font_size = 0
    best_text_arrangement = text
    
    # Single line is one option
    single_size, _ = find_optimal_font_size_single_line(text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw)
    if single_size > best_font_size:
        best_font_size = single_size
        best_text_arrangement = text
    
    # For very short text (1-3 words), let's prioritize single line
    if len(words) <= 3 and best_font_size > 0:
        return best_font_size, best_text_arrangement
    
    # Try different lengths from 2 to min(10, num_words)
    max_lines = min(10, len(words))
    
    for line_count in range(2, max_lines + 1):
        # Distribute words among lines
        chars_per_line = len(text) // line_count
        
        # Use textwrap for intelligent wrapping
        wrapped_text = textwrap.fill(text, width=chars_per_line)
        
        # Test this arrangement
        test_font_size = test_line_arrangement(wrapped_text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw)
        
        if test_font_size > best_font_size:
            best_font_size = test_font_size
            best_text_arrangement = wrapped_text
    
    # Try a more aggressive approach for longer text - create more balanced lines
    if len(words) > 5:
        # Try different number of words per line
        for words_per_line in range(1, len(words) // 2 + 1):
            arranged_text = ""
            for i in range(0, len(words), words_per_line):
                line = " ".join(words[i:i+words_per_line])
                arranged_text += line + "\n" if i + words_per_line < len(words) else line
            
            # Test this arrangement
            test_font_size = test_line_arrangement(arranged_text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw)
            
            if test_font_size > best_font_size:
                best_font_size = test_font_size
                best_text_arrangement = arranged_text
    
    return best_font_size, best_text_arrangement

def test_line_arrangement(arranged_text, available_width, available_height, test_font, dpi_ratio, stroke_width, draw):
    """Test a specific line arrangement and return the optimal font size"""
    min_size = 1
    max_size = 1000  # Start with a large maximum
    optimal_font_size = min_size
    
    while min_size <= max_size:
        mid_size = (min_size + max_size) // 2
        
        # Apply DPI scaling to font size
        scaled_size = int(mid_size * dpi_ratio)
        if scaled_size < 1:
            scaled_size = 1
            
        font = test_font(scaled_size)
        
        # Calculate total height and maximum width of all lines
        lines = arranged_text.split('\n')
        total_height = 0
        max_width = 0
        
        for line in lines:
            scaled_stroke_width = int(stroke_width * dpi_ratio) if stroke_width > 0 else 0
            text_bbox = draw.textbbox((0, 0), line, font=font, stroke_width=scaled_stroke_width)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            total_height += text_height
            max_width = max(max_width, text_width)
        
        # Add line spacing (20% of line height)
        if len(lines) > 1:
            line_spacing = text_height * 0.2
            total_height += line_spacing * (len(lines) - 1)
        
        # Check if this arrangement fits within available space
        if max_width <= available_width and total_height <= available_height:
            optimal_font_size = mid_size
            min_size = mid_size + 1
        else:
            max_size = mid_size - 1
    
    return optimal_font_size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bold text as a high-resolution PNG image")
    parser.add_argument("text", help="Text to render")
    parser.add_argument("--image-size", type=int, default=500, help="Size of square output image in pixels (default: 500)")
    parser.add_argument("--output", default="output.png", help="Output filename (default: output.png)")
    parser.add_argument("--dpi", type=int, default=300, help="Resolution in DPI - higher values create sharper images (default: 300)")
    parser.add_argument("--text-color", default="0,0,0", help="Text color as R,G,B (default: 0,0,0)")
    parser.add_argument("--bg-color", default="255,255,255", help="Background color as R,G,B (default: 255,255,255)")
    parser.add_argument("--padding-percent", type=int, default=10, help="Percentage of padding around text (1-20, default: 10)")
    parser.add_argument("--font", help="Path to a .ttf font file")
    parser.add_argument("--stroke-width", type=int, default=0, help="Width of text outline (0-5, default: 0)")
    parser.add_argument("--bold-level", type=int, default=1, choices=[1, 2, 3], 
                       help="Boldness level: 1=normal, 2=bold, 3=extra bold (default: 1)")
    parser.add_argument("--no-line-break", action="store_true", help="Disable automatic line breaking")
    
    args = parser.parse_args()
    
    # Parse color tuples
    text_color = tuple(map(int, args.text_color.split(',')))
    bg_color = tuple(map(int, args.bg_color.split(',')))
    
    create_text_image(
        args.text,
        image_size=args.image_size,
        output_file=args.output,
        dpi=args.dpi,
        text_color=text_color,
        bg_color=bg_color,
        padding_percent=args.padding_percent,
        font_path=args.font,
        stroke_width=args.stroke_width,
        bold_level=args.bold_level,
        auto_line_break=not args.no_line_break
    ) 