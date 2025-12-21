# import math
# import random
# from PIL import Image, ImageDraw, ImageOps
# import argparse
# import os
# import heapq # For BinaryHeap implementation
# import json # For JSON config file

# Image.MAX_IMAGE_PIXELS = None  # Remove the limit entirely
# # --- KDTree and BinaryHeap Implementation (from kdTree.js) ---
# # (KDNode, BinaryHeap, KDTree classes remain unchanged from the previous version)
# class KDNode:
#     def __init__(self, obj, dimension, parent):
#         self.obj = obj
#         self.left = None
#         self.right = None
#         self.parent = parent
#         self.dimension = dimension

# class BinaryHeap:
#     def __init__(self, score_function):
#         self.content = []
#         self.score_function = score_function

#     def push(self, element):
#         score = self.score_function(element)
#         heapq.heappush(self.content, (score, element))

#     def pop(self):
#         score, element = heapq.heappop(self.content)
#         return element

#     def peek(self):
#         if not self.content:
#             return None
#         score, element = self.content[0]
#         return element

#     def size(self):
#         return len(self.content)

# class KDTree:
#     def __init__(self, points, metric, dimensions):
#         self.metric = metric
#         self.dimensions = dimensions
#         self.root = self._build_tree(list(points), 0, None)

#     def _build_tree(self, points, depth, parent):
#         if not points:
#             return None
#         dim_idx = depth % len(self.dimensions)
#         dimension_name = self.dimensions[dim_idx]
#         if len(points) == 1:
#             return KDNode(points[0], dim_idx, parent)
#         points.sort(key=lambda p: getattr(p, dimension_name))
#         median_idx = len(points) // 2
#         node = KDNode(points[median_idx], dim_idx, parent)
#         node.left = self._build_tree(points[:median_idx], depth + 1, node)
#         node.right = self._build_tree(points[median_idx+1:], depth + 1, node)
#         return node

#     def insert(self, point_obj):
#         if self.root is None:
#             self.root = KDNode(point_obj, 0, None)
#             return
#         def find_insert_position(node, current_parent):
#             if node is None: return current_parent
#             dim_name = self.dimensions[node.dimension]
#             if getattr(point_obj, dim_name) < getattr(node.obj, dim_name):
#                 return find_insert_position(node.left, node)
#             else:
#                 return find_insert_position(node.right, node)
#         insert_parent_node = find_insert_position(self.root, None)
#         new_dim_idx = (insert_parent_node.dimension + 1) % len(self.dimensions)
#         new_node = KDNode(point_obj, new_dim_idx, insert_parent_node)
#         parent_dim_name = self.dimensions[insert_parent_node.dimension]
#         if getattr(point_obj, parent_dim_name) < getattr(insert_parent_node.obj, parent_dim_name):
#             insert_parent_node.left = new_node
#         else:
#             insert_parent_node.right = new_node
            
#     def nearest(self, query_point_obj, max_nodes, max_distance_sq=float('inf')):
#         best_nodes = BinaryHeap(score_function=lambda e: -e[1])
#         def nearest_search(node):
#             if node is None: return
#             dim_name = self.dimensions[node.dimension]
#             own_dist_sq = self.metric(query_point_obj, node.obj)
#             if getattr(query_point_obj, dim_name) < getattr(node.obj, dim_name):
#                 best_child, other_child = node.left, node.right
#             else:
#                 best_child, other_child = node.right, node.left
#             nearest_search(best_child)
#             if best_nodes.size() < max_nodes or own_dist_sq < best_nodes.peek()[1]:
#                 if own_dist_sq <= max_distance_sq:
#                     best_nodes.push([node.obj, own_dist_sq])
#                     if best_nodes.size() > max_nodes: best_nodes.pop()
#             axis_dist_sq = (getattr(query_point_obj, dim_name) - getattr(node.obj, dim_name)) ** 2
#             if best_nodes.size() < max_nodes or axis_dist_sq < best_nodes.peek()[1]:
#                 if axis_dist_sq <= max_distance_sq: nearest_search(other_child)
#         if self.root: nearest_search(self.root)
#         result = []
#         while best_nodes.size() > 0: result.append(best_nodes.pop())
#         return result[::-1]

# # --- Helper function to convert hex colors to RGB ---
# def hex_to_rgb(hex_color):
#     hex_color = hex_color.lstrip('#')
#     return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# # --- Point and Polygon Classes ---
# class Point:
#     def __init__(self, x, y): self.x, self.y = x, y

# class Polygon:
#     def __init__(self, x_center, y_center):
#         self.x, self.y, self.points = x_center, y_center, []
#     def add_point(self, p_relative): self.points.append(p_relative)
#     def get_absolute_points(self): return [Point(self.x + p.x, self.y + p.y) for p in self.points]
#     def get_absolute_points_for_drawing(self, draw_ratio): return [Point(self.x + p.x * draw_ratio, self.y + p.y * draw_ratio) for p in self.points]
#     def rotate(self, rads):
#         cos_r, sin_r = math.cos(rads), math.sin(rads)
#         for p in self.points: p.x, p.y = cos_r * p.x - sin_r * p.y, sin_r * p.x + cos_r * p.y
#     def _project(self, axis_x, axis_y, pts):
#         min_p, max_p = float('inf'), float('-inf')
#         for p_obj in pts:
#             dot = p_obj.x * axis_x + p_obj.y * axis_y
#             min_p, max_p = min(min_p, dot), max(max_p, dot)
#         return min_p, max_p
#     def intersects_with(self, other_polygon):
#         abs_pts1, abs_pts2 = self.get_absolute_points(), other_polygon.get_absolute_points()
#         for poly_pts in [abs_pts1, abs_pts2]:
#             for i in range(len(poly_pts)):
#                 p1, p2 = poly_pts[i], poly_pts[(i + 1) % len(poly_pts)]
#                 edge_x, edge_y = p2.x - p1.x, p2.y - p1.y
#                 axis_x, axis_y = -edge_y, edge_x
#                 norm = math.sqrt(axis_x**2 + axis_y**2)
#                 if norm == 0: continue
#                 axis_x /= norm; axis_y /= norm
#                 minA, maxA = self._project(axis_x, axis_y, abs_pts1)
#                 minB, maxB = self._project(axis_x, axis_y, abs_pts2)
#                 if maxA < minB or minA > maxB: return False
#         return True

# # --- Shape Classes ---
# class Shape:
#     def __init__(self, options):
#         self.options = options
#         self.center_x = 0 
#         self.center_y = 0 
#         self.shape_type = "BaseShape"
#     @property
#     def x(self): return self.center_x
#     @property
#     def y(self): return self.center_y
#     def get_center_for_distance_check(self): return Point(self.center_x, self.center_y)

# class CircleShape(Shape):
#     def __init__(self, x_pos, y_pos, radius, options):
#         super().__init__(options)
#         self.center_x, self.center_y, self.radius = x_pos, y_pos, radius
#         self.shape_type = "Circle"
#     def intersects(self, other_circle):
#         d_sq = (other_circle.center_x - self.center_x)**2 + (other_circle.center_y - self.center_y)**2
#         return d_sq < (self.radius + other_circle.radius)**2
#     def overlaps_image(self, img_px_data, img_w, img_h):
#         total_pts, overlaps = 0, 0
#         for i_spoke in range(math.floor(self.radius) + 1):
#             for r_sample in range(math.floor(self.radius) + 1):
#                 total_pts += 1
#                 px = self.center_x + math.cos(i_spoke * math.pi*2) * r_sample
#                 py = self.center_y + math.sin(i_spoke * math.pi*2) * r_sample
#                 if 0 <= px < img_w and 0 <= py < img_h:
#                     try:
#                         r,g,b,a = img_px_data[math.floor(px), math.floor(py)]
#                         if (r+g+b) * (a/255.0) < 127: overlaps +=1
#                     except IndexError: pass
#         return total_pts, overlaps
#     def draw(self, draw_ctx, style_rgb):
#         r_draw = self.radius * self.options['draw_ratio']
#         draw_ctx.ellipse([self.center_x-r_draw, self.center_y-r_draw, self.center_x+r_draw, self.center_y+r_draw], fill=style_rgb)

# class PolygonShapeComposite(Shape):
#     def __init__(self, options, x_center, y_center):
#         super().__init__(options)
#         self.polygons, self.center_x, self.center_y = [], x_center, y_center
#         self.shape_type = "PolygonComposite"
#     def intersects(self, other_shape_composite):
#         if not isinstance(other_shape_composite, PolygonShapeComposite): return False
#         for poly1 in self.polygons:
#             for poly2 in other_shape_composite.polygons:
#                 if poly1.intersects_with(poly2): return True
#         return False
#     def overlaps_image(self, img_px_data, img_w, img_h):
#         grp_total_pts, grp_overlaps = 0,0
#         for poly_inst in self.polygons:
#             pts_check = [Point(poly_inst.x, poly_inst.y)] + [Point(poly_inst.x + p.x, poly_inst.y + p.y) for p in poly_inst.points]
#             curr_poly_total, curr_poly_overlaps = len(pts_check), 0
#             for p_chk in pts_check:
#                 if 0 <= p_chk.x < img_w and 0 <= p_chk.y < img_h:
#                     try:
#                         r,g,b,a = img_px_data[math.floor(p_chk.x), math.floor(p_chk.y)]
#                         if (r+g+b) * (a/255.0) < 127: curr_poly_overlaps +=1
#                     except IndexError: pass
#             grp_total_pts += curr_poly_total; grp_overlaps += curr_poly_overlaps
#         return grp_total_pts, grp_overlaps
#     def draw(self, draw_ctx, style_rgb):
#         dr = self.options['draw_ratio']
#         for poly_inst in self.polygons:
#             abs_pts = poly_inst.get_absolute_points_for_drawing(dr)
#             if len(abs_pts) >=2: draw_ctx.polygon([(p.x,p.y) for p in abs_pts], fill=style_rgb)

# # --- Factory functions ---
# def generate_shapes(options): # (Unchanged from previous version)
#     factory_type = options['shape_factory']
#     min_r, max_r = options['min_radius'], options['max_radius']
#     radius = min_r + random.random() * (max_r - min_r)
#     img_w, img_h = options['width'], options['height']
#     if options['circular']:
#         angle = random.random()*2*math.pi
#         dist_c = random.random()*(min(img_w,img_h)*0.48-radius)
#         x_pos, y_pos = img_w*0.5+math.cos(angle)*dist_c, img_h*0.5+math.sin(angle)*dist_c
#     else:
#         x_pos, y_pos = radius+random.random()*(img_w-radius*2), radius+random.random()*(img_h-radius*2)
#     x_pos, y_pos = max(radius,min(x_pos,img_w-radius)), max(radius,min(y_pos,img_h-radius))

#     if factory_type == 'Circle': return [CircleShape(x_pos, y_pos, radius, options)]
#     elif factory_type == 'Regular polygon':
#         psc = PolygonShapeComposite(options, x_pos, y_pos)
#         poly = Polygon(x_pos, y_pos)
#         for i in range(options['sides']):
#             a = math.pi*2*(i/options['sides'])
#             poly.add_point(Point(math.cos(a)*radius, math.sin(a)*radius))
#         poly.rotate(random.random()*2*math.pi); psc.polygons.append(poly)
#         return [psc]
#     elif factory_type == 'Cross':
#         psc = PolygonShapeComposite(options, x_pos, y_pos)
#         pt = options['pointiness']
#         p1,p2 = Polygon(x_pos,y_pos), Polygon(x_pos,y_pos)
#         for p_obj in [p1,p2]:
#             p_obj.add_point(Point(-radius, -(1-pt)*radius)); p_obj.add_point(Point(radius, -(1-pt)*radius))
#             p_obj.add_point(Point(radius, (1-pt)*radius)); p_obj.add_point(Point(-radius, (1-pt)*radius))
#         rot = random.random()*2*math.pi
#         p1.rotate(rot); p2.rotate(rot+math.pi/2)
#         psc.polygons.extend([p1,p2])
#         return [psc]
#     elif factory_type == 'Star':
#         psc = PolygonShapeComposite(options, x_pos, y_pos)
#         sides, pt = options['sides'], options['pointiness']
#         rot = random.random()*2*math.pi
#         for i in range(sides):
#             poly = Polygon(x_pos,y_pos)
#             poly.add_point(Point(-(1-pt)*radius,0)); poly.add_point(Point((1-pt)*radius,0)); poly.add_point(Point(0,radius))
#             poly.rotate((i/sides)*math.pi*2+rot); psc.polygons.append(poly)
#         return [psc]
#     else: raise ValueError(f"Unknown factory: {factory_type}")

# def preprocess_image(input_img, target_shape_size, pad_fraction):
#     # Resize the image to fit within target_size, keeping aspect ratio
#     w, h = input_img.size
#     max_dim = max(w, h)
    
#     # Create a square image with white background
#     square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 255))
    
#     # Paste the original image centered in the square
#     left = (max_dim - w) // 2
#     top = (max_dim - h) // 2
#     square_img.paste(input_img, (left, top), input_img if input_img.mode == 'RGBA' else None)
    
#     # Step 2: Resize the square image to target size
#     final_img = square_img.resize((target_shape_size, target_shape_size), Image.LANCZOS)
        
#     return final_img

# # --- Main Ishihara Generation Logic ---
# def generate_ishihara_plate(image_path, options): # (KD-Tree initialization and usage unchanged)
#     # Load color palette from external file if specified 
#     import os
#     import json
#     if 'color_palette' in options and isinstance(options['color_palette'], str):
#         palette_path = options['color_palette']
#         if os.path.exists(palette_path):
#             with open(palette_path, 'r') as f:
#                 palette = json.load(f)
#             options.update(palette)
#         else:
#             print(f"Warning: color_palette file {palette_path} not found. Using defaults in config.")
#     try:
#         input_img = Image.open(image_path).convert("RGBA")
#         if options['resize']:
#             input_img = preprocess_image(input_img, target_shape_size=options["target_shape_size"], pad_fraction=options["pad_fraction"])
#     except FileNotFoundError:
#         print(f"Error: Input image not found at {image_path}"); return None
#     options['width'], options['height'] = input_img.size
#     img_px_data = input_img.load()
#     if 'min_radius_factor' in options: # Handle potential factors if used in JSON
#         options['min_radius'] = (options['width'] + options['height']) / options['min_radius_factor']
#         options['max_radius'] = (options['width'] + options['height']) / options['max_radius_factor']
#     if options['min_radius'] > options['max_radius']: options['min_radius'] = options['max_radius']
#     options['check_nearest'] = math.ceil(max(options['min_radius'],options['max_radius'])/options['min_radius']*5) if options['min_radius']>0 else 5
    
#     def kd_metric(a,b): return (a.center_x-b.center_x)**2 + (a.center_y-b.center_y)**2
#     kd_tree = KDTree([], kd_metric, ['center_x','center_y'])
#     placed_shapes_draw, tries, num_placed = [], 0, 0
#     print(f"Starting. Stop after: {options['stop_after']} tries. Max check: {options['check_nearest']}")

#     while tries < options['stop_after']:
#         tries += 1
#         # if tries % 1000 == 0: print(f"Tries: {tries}, Placed: {num_placed}")
#         logical_shape = generate_shapes(options)[0]
#         coll_det = False
#         if kd_tree.root:
#             nearest = kd_tree.nearest(logical_shape, options['check_nearest'])
#             for near_data in nearest:
#                 near_shape = near_data[0]
#                 if logical_shape.shape_type == near_shape.shape_type: # Basic type check for appropriate intersect
#                     if logical_shape.intersects(near_shape): coll_det=True; break
#             if coll_det: continue
        
#         total_pts, img_hits = logical_shape.overlaps_image(img_px_data,options['width'],options['height'])
#         hits_pat = (img_hits > 0)
#         if options['edge_detection'] and hits_pat and total_pts > 0 and img_hits != total_pts: continue
        
#         tries = 0
#         style_key, num_cols = ('color_on',options['n_colors_on']) if hits_pat != options['invert_colors'] else ('color_off',options['n_colors_off'])
#         style_rgb = (0,0,0)
#         if num_cols > 0: style_rgb = hex_to_rgb(options[style_key + str(random.randint(0,num_cols-1))])
        
#         kd_tree.insert(logical_shape)
#         placed_shapes_draw.append((logical_shape, style_rgb)); num_placed +=1
#         # if num_placed % 100 == 0: print(f"Placed {num_placed} shapes.")
    
#     out_img = Image.new("RGBA", (options['width'],options['height']), hex_to_rgb(options['background_color']))
#     draw_ctx = ImageDraw.Draw(out_img)
#     print(f"Drawing {len(placed_shapes_draw)} shapes...")
#     for shape, style in placed_shapes_draw: shape.draw(draw_ctx, style)
#     print("Generation complete."); return out_img

# # --- Default Options and Main CLI ---
# def get_default_options(): # These are the base defaults
#     return {
#         'circular': True, 'resize': True, 'target_shape_size': 512, 'pad_fraction': 0.2, 'edge_detection': True, 'invert_colors': False,
#         'background_color': '#FFFFFF', 'n_colors_on': 3, 'n_colors_off': 6,
#         'color_on0': '#F9BB82', 'color_on1': '#EBA170', 'color_on2': '#FCCD84',
#         'color_on3': '#000000', 'color_on4': '#000000', 'color_on5': '#000000',
#         'color_off0': '#9CA594', 'color_off1': '#ACB4A5', 'color_off2': '#BBB964',
#         'color_off3': '#D7DAAA', 'color_off4': '#E5D57D', 'color_off5': '#D1D6AF',
#         'min_radius': 5, 'max_radius': 20, 'draw_ratio': 1.0,
#         'stop_after': 10000, 'shape_factory': 'Circle',
#         'sides': 4, 'pointiness': 0.75,
#         # width, height, check_nearest are determined at runtime or by options
#     }

# def main():
#     parser = argparse.ArgumentParser(description="Generate Ishihara plate images.",
#                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#     parser.add_argument("input_path", help="Path to the input image or directory of images.")
#     parser.add_argument("output_path", help="Path to save the output image or directory for output images.")
#     parser.add_argument("--config", help="Path to a JSON configuration file.", default=None)

#     # Add arguments for all hyperparameters present in default_options
#     # This allows CLI overrides *after* JSON config is loaded.
#     temp_defaults = get_default_options()
#     for key, value in temp_defaults.items():
#         arg_type = type(value)
#         if arg_type == bool:
#             # For bools, store_true/store_false is better if default is False/True
#             # Simple type=lambda approach for now to match other types.
#             parser.add_argument(f"--{key}", type=lambda x: (str(x).lower() == 'true'),
#                                 help=f"Override {key.replace('_', ' ')}")
#         else:
#             parser.add_argument(f"--{key}", type=arg_type,
#                                 help=f"Override {key.replace('_', ' ')}")
#     args = parser.parse_args()

#     # 1. Start with hardcoded defaults
#     current_options = get_default_options()

#     # 2. Load options from JSON config file if provided
#     if args.config:
#         try:
#             with open(args.config, 'r') as f:
#                 json_options = json.load(f)
#             current_options.update(json_options) # JSON overrides defaults
#             print(f"Loaded configuration from {args.config}")
#         except FileNotFoundError:
#             print(f"Warning: Config file {args.config} not found. Using defaults/CLI args.")
#         except json.JSONDecodeError:
#             print(f"Warning: Error decoding JSON from {args.config}. Using defaults/CLI args.")

#     # 3. Override with any command-line arguments provided
#     # These have the highest precedence.
#     cli_overrides = {k: v for k, v in vars(args).items() 
#                      if v is not None and k not in ['input_path', 'output_path', 'config']}
#     current_options.update(cli_overrides)
    
#     input_path = args.input_path
#     output_path = args.output_path

#     if os.path.isdir(input_path):
#         # Batch processing
#         if not os.path.exists(output_path) or not os.path.isdir(output_path):
#             print(f"Output path {output_path} for directory input must be an existing directory or will be created.")
#             os.makedirs(output_path, exist_ok=True)
#             if not os.path.isdir(output_path): # Double check creation
#                  print(f"Error: Could not create output directory {output_path}.")
#                  return

#         print(f"Processing directory: {input_path}")
#         for filename in os.listdir(input_path):
#             if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
#                 img_file_path = os.path.join(input_path, filename)
#                 # Ensure output is PNG
#                 output_img_name = f"ishihara_{os.path.splitext(filename)[0]}.png"
#                 output_file_path = os.path.join(output_path, output_img_name)
                
#                 print(f"Processing {img_file_path} -> {output_file_path}")
#                 # Each image in batch uses the fully resolved options
#                 result_image = generate_ishihara_plate(img_file_path, current_options.copy()) # Pass a copy
#                 if result_image:
#                     result_image.save(output_file_path)
#                     print(f"Saved {output_file_path}")
#     else:
#         # Single image processing
#         print(f"Processing single file: {input_path}")
#         final_output_path = output_path
#         # If output_path is a directory, save inside with a generated name
#         if os.path.isdir(output_path):
#             base_name = os.path.basename(input_path)
#             output_file_name = f"ishihara_{os.path.splitext(base_name)[0]}.png"
#             final_output_path = os.path.join(output_path, output_file_name)
        
#         # Ensure output directory exists if a full path is given
#         output_dir_for_single = os.path.dirname(final_output_path)
#         if output_dir_for_single and not os.path.exists(output_dir_for_single):
#             os.makedirs(output_dir_for_single)
            
#         result_image = generate_ishihara_plate(input_path, current_options.copy()) # Pass a copy
#         if result_image:
#             result_image.save(final_output_path)
#             print(f"Saved {final_output_path}")

# if __name__ == "__main__":
#     main()

import math
import random
from PIL import Image, ImageDraw, ImageOps
import argparse
import os
import heapq # For BinaryHeap implementation
import json # For JSON config file

Image.MAX_IMAGE_PIXELS = None  # Remove the limit entirely
# --- KDTree and BinaryHeap Implementation (from kdTree.js) ---
# (KDNode, BinaryHeap, KDTree classes remain unchanged from the previous version)
class KDNode:
    def __init__(self, obj, dimension, parent):
        self.obj = obj
        self.left = None
        self.right = None
        self.parent = parent
        self.dimension = dimension

class BinaryHeap:
    def __init__(self, score_function):
        self.content = []
        self.score_function = score_function

    def push(self, element):
        score = self.score_function(element)
        heapq.heappush(self.content, (score, element))

    def pop(self):
        score, element = heapq.heappop(self.content)
        return element

    def peek(self):
        if not self.content:
            return None
        score, element = self.content[0]
        return element

    def size(self):
        return len(self.content)

class KDTree:
    def __init__(self, points, metric, dimensions):
        self.metric = metric
        self.dimensions = dimensions
        self.root = self._build_tree(list(points), 0, None)

    def _build_tree(self, points, depth, parent):
        if not points:
            return None
        dim_idx = depth % len(self.dimensions)
        dimension_name = self.dimensions[dim_idx]
        if len(points) == 1:
            return KDNode(points[0], dim_idx, parent)
        points.sort(key=lambda p: getattr(p, dimension_name))
        median_idx = len(points) // 2
        node = KDNode(points[median_idx], dim_idx, parent)
        node.left = self._build_tree(points[:median_idx], depth + 1, node)
        node.right = self._build_tree(points[median_idx+1:], depth + 1, node)
        return node

    def insert(self, point_obj):
        if self.root is None:
            self.root = KDNode(point_obj, 0, None)
            return
        def find_insert_position(node, current_parent):
            if node is None: return current_parent
            dim_name = self.dimensions[node.dimension]
            if getattr(point_obj, dim_name) < getattr(node.obj, dim_name):
                return find_insert_position(node.left, node)
            else:
                return find_insert_position(node.right, node)
        insert_parent_node = find_insert_position(self.root, None)
        new_dim_idx = (insert_parent_node.dimension + 1) % len(self.dimensions)
        new_node = KDNode(point_obj, new_dim_idx, insert_parent_node)
        parent_dim_name = self.dimensions[insert_parent_node.dimension]
        if getattr(point_obj, parent_dim_name) < getattr(insert_parent_node.obj, parent_dim_name):
            insert_parent_node.left = new_node
        else:
            insert_parent_node.right = new_node
            
    def nearest(self, query_point_obj, max_nodes, max_distance_sq=float('inf')):
        best_nodes = BinaryHeap(score_function=lambda e: -e[1])
        def nearest_search(node):
            if node is None: return
            dim_name = self.dimensions[node.dimension]
            own_dist_sq = self.metric(query_point_obj, node.obj)
            if getattr(query_point_obj, dim_name) < getattr(node.obj, dim_name):
                best_child, other_child = node.left, node.right
            else:
                best_child, other_child = node.right, node.left
            nearest_search(best_child)
            if best_nodes.size() < max_nodes or own_dist_sq < best_nodes.peek()[1]:
                if own_dist_sq <= max_distance_sq:
                    best_nodes.push([node.obj, own_dist_sq])
                    if best_nodes.size() > max_nodes: best_nodes.pop()
            axis_dist_sq = (getattr(query_point_obj, dim_name) - getattr(node.obj, dim_name)) ** 2
            if best_nodes.size() < max_nodes or axis_dist_sq < best_nodes.peek()[1]:
                if axis_dist_sq <= max_distance_sq: nearest_search(other_child)
        if self.root: nearest_search(self.root)
        result = []
        while best_nodes.size() > 0: result.append(best_nodes.pop())
        return result[::-1]

# --- Helper function to convert hex colors to RGB ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# --- Point and Polygon Classes ---
class Point:
    def __init__(self, x, y): self.x, self.y = x, y

class Polygon:
    def __init__(self, x_center, y_center):
        self.x, self.y, self.points = x_center, y_center, []
    def add_point(self, p_relative): self.points.append(p_relative)
    def get_absolute_points(self): return [Point(self.x + p.x, self.y + p.y) for p in self.points]
    def get_absolute_points_for_drawing(self, draw_ratio): return [Point(self.x + p.x * draw_ratio, self.y + p.y * draw_ratio) for p in self.points]
    def rotate(self, rads):
        cos_r, sin_r = math.cos(rads), math.sin(rads)
        for p in self.points: p.x, p.y = cos_r * p.x - sin_r * p.y, sin_r * p.x + cos_r * p.y
    def _project(self, axis_x, axis_y, pts):
        min_p, max_p = float('inf'), float('-inf')
        for p_obj in pts:
            dot = p_obj.x * axis_x + p_obj.y * axis_y
            min_p, max_p = min(min_p, dot), max(max_p, dot)
        return min_p, max_p
    def intersects_with(self, other_polygon):
        abs_pts1, abs_pts2 = self.get_absolute_points(), other_polygon.get_absolute_points()
        for poly_pts in [abs_pts1, abs_pts2]:
            for i in range(len(poly_pts)):
                p1, p2 = poly_pts[i], poly_pts[(i + 1) % len(poly_pts)]
                edge_x, edge_y = p2.x - p1.x, p2.y - p1.y
                axis_x, axis_y = -edge_y, edge_x
                norm = math.sqrt(axis_x**2 + axis_y**2)
                if norm == 0: continue
                axis_x /= norm; axis_y /= norm
                minA, maxA = self._project(axis_x, axis_y, abs_pts1)
                minB, maxB = self._project(axis_x, axis_y, abs_pts2)
                if maxA < minB or minA > maxB: return False
        return True

# --- Shape Classes ---
class Shape:
    def __init__(self, options):
        self.options = options
        self.center_x = 0 
        self.center_y = 0 
        self.shape_type = "BaseShape"
    @property
    def x(self): return self.center_x
    @property
    def y(self): return self.center_y
    def get_center_for_distance_check(self): return Point(self.center_x, self.center_y)

class CircleShape(Shape):
    def __init__(self, x_pos, y_pos, radius, options):
        super().__init__(options)
        self.center_x, self.center_y, self.radius = x_pos, y_pos, radius
        self.shape_type = "Circle"
    def intersects(self, other_circle):
        d_sq = (other_circle.center_x - self.center_x)**2 + (other_circle.center_y - self.center_y)**2
        return d_sq < (self.radius + other_circle.radius)**2
    def overlaps_image(self, img_px_data, img_w, img_h):
        total_pts, overlaps = 0, 0
        for i_spoke in range(math.floor(self.radius) + 1):
            for r_sample in range(math.floor(self.radius) + 1):
                total_pts += 1
                px = self.center_x + math.cos(i_spoke * math.pi*2) * r_sample
                py = self.center_y + math.sin(i_spoke * math.pi*2) * r_sample
                if 0 <= px < img_w and 0 <= py < img_h:
                    try:
                        r,g,b,a = img_px_data[math.floor(px), math.floor(py)]
                        if (r+g+b) * (a/255.0) < 127: overlaps +=1
                    except IndexError: pass
        return total_pts, overlaps
    def draw(self, draw_ctx, style_rgb):
        r_draw = self.radius * self.options['draw_ratio']
        draw_ctx.ellipse([self.center_x-r_draw, self.center_y-r_draw, self.center_x+r_draw, self.center_y+r_draw], fill=style_rgb)

class PolygonShapeComposite(Shape):
    def __init__(self, options, x_center, y_center):
        super().__init__(options)
        self.polygons, self.center_x, self.center_y = [], x_center, y_center
        self.shape_type = "PolygonComposite"
    def intersects(self, other_shape_composite):
        if not isinstance(other_shape_composite, PolygonShapeComposite): return False
        for poly1 in self.polygons:
            for poly2 in other_shape_composite.polygons:
                if poly1.intersects_with(poly2): return True
        return False
    def _point_in_polygon(self, px, py, polygon):
        """Check if a point is inside a polygon using ray casting algorithm"""
        abs_points = polygon.get_absolute_points()
        n = len(abs_points)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = abs_points[i].x, abs_points[i].y
            xj, yj = abs_points[j].x, abs_points[j].y
            
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside
    
    def overlaps_image(self, img_px_data, img_w, img_h):
        """Improved overlap detection with dense sampling for polygon shapes"""
        grp_total_pts, grp_overlaps = 0, 0
        
        for poly_inst in self.polygons:
            # Get polygon bounds for efficient sampling
            abs_points = poly_inst.get_absolute_points()
            if not abs_points:
                continue
                
            min_x = min(p.x for p in abs_points)
            max_x = max(p.x for p in abs_points)
            min_y = min(p.y for p in abs_points)
            max_y = max(p.y for p in abs_points)
            
            # Calculate sampling density based on polygon size
            poly_width = max_x - min_x
            poly_height = max_y - min_y
            poly_size = max(poly_width, poly_height)
            
            # Dense sampling: sample approximately every 0.5 pixels for better accuracy
            sample_density = max(1, math.ceil(poly_size / 2))
            
            curr_poly_total, curr_poly_overlaps = 0, 0
            
            # Sample within bounding box
            for dx in range(sample_density * 2 + 1):
                for dy in range(sample_density * 2 + 1):
                    # Convert to actual coordinates
                    sample_x = poly_inst.x + (dx - sample_density) * 0.5
                    sample_y = poly_inst.y + (dy - sample_density) * 0.5
                    
                    # Check if point is inside polygon
                    if self._point_in_polygon(sample_x, sample_y, poly_inst):
                        curr_poly_total += 1
                        
                        # Check if point is within image bounds
                        if 0 <= sample_x < img_w and 0 <= sample_y < img_h:
                            try:
                                r, g, b, a = img_px_data[math.floor(sample_x), math.floor(sample_y)]
                                if (r + g + b) * (a / 255.0) < 127:
                                    curr_poly_overlaps += 1
                            except IndexError:
                                pass
            
            # If no samples were inside polygon (shouldn't happen), fall back to vertex sampling
            if curr_poly_total == 0:
                pts_check = [Point(poly_inst.x, poly_inst.y)] + abs_points
                curr_poly_total = len(pts_check)
                for p_chk in pts_check:
                    if 0 <= p_chk.x < img_w and 0 <= p_chk.y < img_h:
                        try:
                            r, g, b, a = img_px_data[math.floor(p_chk.x), math.floor(p_chk.y)]
                            if (r + g + b) * (a / 255.0) < 127:
                                curr_poly_overlaps += 1
                        except IndexError:
                            pass
            
            grp_total_pts += curr_poly_total
            grp_overlaps += curr_poly_overlaps
            
        return grp_total_pts, grp_overlaps
    def draw(self, draw_ctx, style_rgb):
        dr = self.options['draw_ratio']
        for poly_inst in self.polygons:
            abs_pts = poly_inst.get_absolute_points_for_drawing(dr)
            if len(abs_pts) >=2: draw_ctx.polygon([(p.x,p.y) for p in abs_pts], fill=style_rgb)

# --- Factory functions ---
def generate_shapes(options): # (Unchanged from previous version)
    factory_type = options['shape_factory']
    min_r, max_r = options['min_radius'], options['max_radius']
    radius = min_r + random.random() * (max_r - min_r)
    img_w, img_h = options['width'], options['height']
    if options['circular']:
        angle = random.random()*2*math.pi
        dist_c = random.random()*(min(img_w,img_h)*0.48-radius)
        x_pos, y_pos = img_w*0.5+math.cos(angle)*dist_c, img_h*0.5+math.sin(angle)*dist_c
    else:
        x_pos, y_pos = radius+random.random()*(img_w-radius*2), radius+random.random()*(img_h-radius*2)
    x_pos, y_pos = max(radius,min(x_pos,img_w-radius)), max(radius,min(y_pos,img_h-radius))

    if factory_type == 'Circle': return [CircleShape(x_pos, y_pos, radius, options)]
    elif factory_type == 'Regular polygon':
        psc = PolygonShapeComposite(options, x_pos, y_pos)
        poly = Polygon(x_pos, y_pos)
        for i in range(options['sides']):
            a = math.pi*2*(i/options['sides'])
            poly.add_point(Point(math.cos(a)*radius, math.sin(a)*radius))
        poly.rotate(random.random()*2*math.pi); psc.polygons.append(poly)
        return [psc]
    elif factory_type == 'Cross':
        psc = PolygonShapeComposite(options, x_pos, y_pos)
        pt = options['pointiness']
        p1,p2 = Polygon(x_pos,y_pos), Polygon(x_pos,y_pos)
        for p_obj in [p1,p2]:
            p_obj.add_point(Point(-radius, -(1-pt)*radius)); p_obj.add_point(Point(radius, -(1-pt)*radius))
            p_obj.add_point(Point(radius, (1-pt)*radius)); p_obj.add_point(Point(-radius, (1-pt)*radius))
        rot = random.random()*2*math.pi
        p1.rotate(rot); p2.rotate(rot+math.pi/2)
        psc.polygons.extend([p1,p2])
        return [psc]
    elif factory_type == 'Star':
        psc = PolygonShapeComposite(options, x_pos, y_pos)
        sides, pt = options['sides'], options['pointiness']
        rot = random.random()*2*math.pi
        for i in range(sides):
            poly = Polygon(x_pos,y_pos)
            poly.add_point(Point(-(1-pt)*radius,0)); poly.add_point(Point((1-pt)*radius,0)); poly.add_point(Point(0,radius))
            poly.rotate((i/sides)*math.pi*2+rot); psc.polygons.append(poly)
        return [psc]
    else: raise ValueError(f"Unknown factory: {factory_type}")

def preprocess_image(input_img, target_shape_size, pad_fraction):
    # Resize the image to fit within target_size, keeping aspect ratio
    w, h = input_img.size
    max_dim = max(w, h)
    
    # Create a square image with white background
    square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 255))
    
    # Paste the original image centered in the square
    left = (max_dim - w) // 2
    top = (max_dim - h) // 2
    square_img.paste(input_img, (left, top), input_img if input_img.mode == 'RGBA' else None)
    
    # Step 2: Resize the square image to target size
    final_img = square_img.resize((target_shape_size, target_shape_size), Image.LANCZOS)
        
    return final_img

# --- Main Ishihara Generation Logic ---
def generate_ishihara_plate(image_path, options): # (KD-Tree initialization and usage unchanged)
    # Load color palette from external file if specified 
    import os
    import json
    if 'color_palette' in options and isinstance(options['color_palette'], str):
        palette_path = options['color_palette']
        if os.path.exists(palette_path):
            with open(palette_path, 'r') as f:
                palette = json.load(f)
            options.update(palette)
        else:
            print(f"Warning: color_palette file {palette_path} not found. Using defaults in config.")
    try:
        input_img = Image.open(image_path).convert("RGBA")
        if options['resize']:
            input_img = preprocess_image(input_img, target_shape_size=options["target_shape_size"], pad_fraction=options["pad_fraction"])
    except FileNotFoundError:
        print(f"Error: Input image not found at {image_path}"); return None
    options['width'], options['height'] = input_img.size
    img_px_data = input_img.load()
    if 'min_radius_factor' in options: # Handle potential factors if used in JSON
        options['min_radius'] = (options['width'] + options['height']) / options['min_radius_factor']
        options['max_radius'] = (options['width'] + options['height']) / options['max_radius_factor']
    if options['min_radius'] > options['max_radius']: options['min_radius'] = options['max_radius']
    options['check_nearest'] = math.ceil(max(options['min_radius'],options['max_radius'])/options['min_radius']*5) if options['min_radius']>0 else 5
    
    def kd_metric(a,b): return (a.center_x-b.center_x)**2 + (a.center_y-b.center_y)**2
    kd_tree = KDTree([], kd_metric, ['center_x','center_y'])
    placed_shapes_draw, tries, num_placed = [], 0, 0
    print(f"Starting. Stop after: {options['stop_after']} tries. Max check: {options['check_nearest']}")

    while tries < options['stop_after']:
        tries += 1
        if tries % 1000 == 0: print(f"Tries: {tries}, Placed: {num_placed}")
        logical_shape = generate_shapes(options)[0]
        coll_det = False
        if kd_tree.root:
            nearest = kd_tree.nearest(logical_shape, options['check_nearest'])
            for near_data in nearest:
                near_shape = near_data[0]
                if logical_shape.shape_type == near_shape.shape_type: # Basic type check for appropriate intersect
                    if logical_shape.intersects(near_shape): coll_det=True; break
            if coll_det: continue
        
        total_pts, img_hits = logical_shape.overlaps_image(img_px_data,options['width'],options['height'])
        hits_pat = (img_hits > 0)
        if options['edge_detection'] and hits_pat and total_pts > 0 and img_hits != total_pts: continue
        
        tries = 0
        style_key, num_cols = ('color_on',options['n_colors_on']) if hits_pat != options['invert_colors'] else ('color_off',options['n_colors_off'])
        style_rgb = (0,0,0)
        if num_cols > 0: style_rgb = hex_to_rgb(options[style_key + str(random.randint(0,num_cols-1))])
        
        kd_tree.insert(logical_shape)
        placed_shapes_draw.append((logical_shape, style_rgb)); num_placed +=1
        if num_placed % 100 == 0: print(f"Placed {num_placed} shapes.")
    
    out_img = Image.new("RGBA", (options['width'],options['height']), hex_to_rgb(options['background_color']))
    draw_ctx = ImageDraw.Draw(out_img)
    print(f"Drawing {len(placed_shapes_draw)} shapes...")
    for shape, style in placed_shapes_draw: shape.draw(draw_ctx, style)
    print("Generation complete."); return out_img

# --- Default Options and Main CLI ---
def get_default_options(): # These are the base defaults
    return {
        'circular': True, 'resize': True, 'target_shape_size': 512, 'pad_fraction': 0.2, 'edge_detection': True, 'invert_colors': False,
        'background_color': '#FFFFFF', 'n_colors_on': 3, 'n_colors_off': 6,
        'color_on0': '#F9BB82', 'color_on1': '#EBA170', 'color_on2': '#FCCD84',
        'color_on3': '#000000', 'color_on4': '#000000', 'color_on5': '#000000',
        'color_off0': '#9CA594', 'color_off1': '#ACB4A5', 'color_off2': '#BBB964',
        'color_off3': '#D7DAAA', 'color_off4': '#E5D57D', 'color_off5': '#D1D6AF',
        'min_radius': 5, 'max_radius': 20, 'draw_ratio': 1.0,
        'stop_after': 10000, 'shape_factory': 'Circle',
        'sides': 4, 'pointiness': 0.75,
        # width, height, check_nearest are determined at runtime or by options
    }

def main():
    parser = argparse.ArgumentParser(description="Generate Ishihara plate images.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_path", help="Path to the input image or directory of images.")
    parser.add_argument("output_path", help="Path to save the output image or directory for output images.")
    parser.add_argument("--config", help="Path to a JSON configuration file.", default=None)

    # Add arguments for all hyperparameters present in default_options
    # This allows CLI overrides *after* JSON config is loaded.
    temp_defaults = get_default_options()
    for key, value in temp_defaults.items():
        arg_type = type(value)
        if arg_type == bool:
            # For bools, store_true/store_false is better if default is False/True
            # Simple type=lambda approach for now to match other types.
            parser.add_argument(f"--{key}", type=lambda x: (str(x).lower() == 'true'),
                                help=f"Override {key.replace('_', ' ')}")
        else:
            parser.add_argument(f"--{key}", type=arg_type,
                                help=f"Override {key.replace('_', ' ')}")
    args = parser.parse_args()

    # 1. Start with hardcoded defaults
    current_options = get_default_options()

    # 2. Load options from JSON config file if provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                json_options = json.load(f)
            current_options.update(json_options) # JSON overrides defaults
            print(f"Loaded configuration from {args.config}")
        except FileNotFoundError:
            print(f"Warning: Config file {args.config} not found. Using defaults/CLI args.")
        except json.JSONDecodeError:
            print(f"Warning: Error decoding JSON from {args.config}. Using defaults/CLI args.")

    # 3. Override with any command-line arguments provided
    # These have the highest precedence.
    cli_overrides = {k: v for k, v in vars(args).items() 
                     if v is not None and k not in ['input_path', 'output_path', 'config']}
    current_options.update(cli_overrides)
    
    input_path = args.input_path
    output_path = args.output_path

    if os.path.isdir(input_path):
        # Batch processing
        if not os.path.exists(output_path) or not os.path.isdir(output_path):
            print(f"Output path {output_path} for directory input must be an existing directory or will be created.")
            os.makedirs(output_path, exist_ok=True)
            if not os.path.isdir(output_path): # Double check creation
                 print(f"Error: Could not create output directory {output_path}.")
                 return

        print(f"Processing directory: {input_path}")
        for filename in os.listdir(input_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img_file_path = os.path.join(input_path, filename)
                # Ensure output is PNG
                output_img_name = f"ishihara_{os.path.splitext(filename)[0]}.png"
                output_file_path = os.path.join(output_path, output_img_name)
                
                print(f"Processing {img_file_path} -> {output_file_path}")
                # Each image in batch uses the fully resolved options
                result_image = generate_ishihara_plate(img_file_path, current_options.copy()) # Pass a copy
                if result_image:
                    result_image.save(output_file_path)
                    print(f"Saved {output_file_path}")
    else:
        # Single image processing
        print(f"Processing single file: {input_path}")
        final_output_path = output_path
        # If output_path is a directory, save inside with a generated name
        if os.path.isdir(output_path):
            base_name = os.path.basename(input_path)
            output_file_name = f"ishihara_{os.path.splitext(base_name)[0]}.png"
            final_output_path = os.path.join(output_path, output_file_name)
        
        # Ensure output directory exists if a full path is given
        output_dir_for_single = os.path.dirname(final_output_path)
        if output_dir_for_single and not os.path.exists(output_dir_for_single):
            os.makedirs(output_dir_for_single)
            
        result_image = generate_ishihara_plate(input_path, current_options.copy()) # Pass a copy
        if result_image:
            result_image.save(final_output_path)
            print(f"Saved {final_output_path}")

if __name__ == "__main__":
    main()