# ─────────────────────────────────────────────────────────────
# Graph Toolboard – Operators
# ─────────────────────────────────────────────────────────────
import bpy
import blf
import math
import gpu
from gpu_extras.batch import batch_for_shader

# Helper: Draw HUD background and text in the Graph Editor
def draw_hud_rect(x, y, width, height, color):
    vertices = (
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height)
    )
    indices = ((0, 1, 2), (2, 3, 0))
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    
    shader.bind()
    shader.uniform_float("color", color)
    
    gpu.state.blend_set('ALPHA')
    batch.draw(shader)
    gpu.state.blend_set('NONE')

def draw_hud_callback(self, context):
    if context.area != self._area:
        return
        
    # Get dimensions
    region = context.region
    hud_w = 320
    hud_h = 75
    hud_x = int((region.width - hud_w) / 2)
    hud_y = region.height - hud_h - 20
    
    # Draw Background (Glassmorphism Dark)
    draw_hud_rect(hud_x, hud_y, hud_w, hud_h, (0.1, 0.1, 0.12, 0.85))
    draw_hud_rect(hud_x, hud_y + hud_h - 4, hud_w, 4, (0.2, 0.6, 1.0, 1.0)) # Top blue accent line
    
    # Draw Slider Bar
    bar_w = hud_w - 40
    bar_h = 8
    bar_x = hud_x + 20
    bar_y = hud_y + 25
    draw_hud_rect(bar_x, bar_y, bar_w, bar_h, (0.2, 0.2, 0.25, 1.0)) # Bar background
    
    # Draw Fill based on factor
    # We map factor to slider fill.
    # Modes: TWEEN [0, 1], EASE [-1, 1], PUSH_PULL [-2, 2], SCALE [-5, 5]
    if self.mode == 'TWEEN':
        percentage = self.factor
        fill_w = int(bar_w * percentage)
        draw_hud_rect(bar_x, bar_y, fill_w, bar_h, (0.0, 0.8, 0.6, 1.0))
        val_str = f"{int(percentage * 100)}%"
    elif self.mode in ('EASE', 'EASE_BOTH'):
        # Map [-1, 1] to slider
        percentage = (self.factor + 1.0) / 2.0
        fill_w = int(bar_w * percentage)
        draw_hud_rect(bar_x, bar_y, fill_w, bar_h, (1.0, 0.6, 0.1, 1.0))
        val_str = f"{int(self.factor * 100)}%"
    elif self.mode == 'PUSH_PULL':
        # Map [-1, 2] to slider
        percentage = min(max((self.factor + 1.0) / 3.0, 0.0), 1.0)
        fill_w = int(bar_w * percentage)
        draw_hud_rect(bar_x, bar_y, fill_w, bar_h, (0.8, 0.2, 0.8, 1.0))
        val_str = f"{self.factor:.2f}x"
    elif self.mode == 'SCALE':
        # Map [0, 2] to slider
        percentage = min(max(self.factor / 2.0, 0.0), 1.0)
        fill_w = int(bar_w * percentage)
        draw_hud_rect(bar_x, bar_y, fill_w, bar_h, (0.2, 0.6, 1.0, 1.0))
        val_str = f"{int(self.factor * 100)}%"
    else:
        val_str = f"{self.factor:.2f}"

    # Draw Font
    font_id = 0
    blf.size(font_id, 13)
    
    # Title
    blf.color(font_id, 0.9, 0.9, 0.9, 1.0)
    blf.position(font_id, hud_x + 20, hud_y + 45, 0)
    blf.draw(font_id, f"GRAPH TOOLBOARD: {self.mode}")
    
    # Value Text
    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
    # Calculate right-aligned position roughly
    blf.position(font_id, hud_x + hud_w - 60, hud_y + 45, 0)
    blf.draw(font_id, val_str)
    
    # Help instructions
    blf.size(font_id, 11)
    blf.color(font_id, 0.6, 0.6, 0.6, 1.0)
    blf.position(font_id, hud_x + 20, hud_y + 8, 0)
    blf.draw(font_id, "[Drag Mouse] Adjust  |  [L-Click/Enter] Apply  |  [R-Click/Esc] Cancel")


import time

# Global cache for panel-based tween slider
_tween_cache = {}
_last_tween_time = 0.0
_timer_registered = False

def clear_tween_cache_timer():
    global _tween_cache, _timer_registered, _last_tween_time
    now = time.time()
    if now - _last_tween_time > 0.2:
        _tween_cache.clear()
        _timer_registered = False
        
        # Reset slider to 50% without applying to keyframes
        scene = bpy.context.scene
        if scene and hasattr(scene, "graph_toolboard"):
            # Set direct without calling updates (it will trigger update, but cache is empty and val is 50, so it returns immediately)
            scene.graph_toolboard.tween_slider = 50.0
            
        bpy.ops.ed.undo_push(message="Tween Slider")
        
        # Force Graph Editor redraw
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'GRAPH_EDITOR':
                    area.tag_redraw()
        return None
    return 0.05

def update_tween_slider(self, context):
    global _tween_cache, _timer_registered, _last_tween_time
    
    if not _tween_cache and self.tween_slider == 50.0:
        return
        
    selected_fcurves = context.selected_editable_fcurves
    if not selected_fcurves:
        return
        
    now = time.time()
    _last_tween_time = now
    
    if not _tween_cache:
        # Cache keyframes
        for fcurve in selected_fcurves:
            keys_info = []
            selected_indices = []
            for idx, k in enumerate(fcurve.keyframe_points):
                if k.select_control_point:
                    keys_info.append((
                        idx,
                        k.co.x, k.co.y,
                        k.handle_left.x, k.handle_left.y,
                        k.handle_right.x, k.handle_right.y
                    ))
                    selected_indices.append(idx)
            if keys_info:
                min_idx = min(selected_indices)
                max_idx = max(selected_indices)
                left_y = fcurve.keyframe_points[min_idx - 1].co.y if min_idx > 0 else fcurve.keyframe_points[min_idx].co.y
                right_y = fcurve.keyframe_points[max_idx + 1].co.y if max_idx < len(fcurve.keyframe_points) - 1 else fcurve.keyframe_points[max_idx].co.y
                
                _tween_cache[fcurve] = {
                    'keys': keys_info,
                    'left_y': left_y,
                    'right_y': right_y
                }
                
        if not _timer_registered and _tween_cache:
            _timer_registered = True
            bpy.app.timers.register(clear_tween_cache_timer)
            
    if _tween_cache:
        factor = self.tween_slider / 100.0  # factor is [0, 1]
        
        for fcurve, data in _tween_cache.items():
            keys = data['keys']
            
            # First restore all keys to their original cached state
            for info in keys:
                idx = info[0]
                k = fcurve.keyframe_points[idx]
                k.co.y = info[2]
                k.handle_left.y = info[4]
                k.handle_right.y = info[6]
                
            # Perform sequential tweening
            selected_indices = [info[0] for info in keys]
            min_idx = min(selected_indices)
            max_idx = max(selected_indices)
            
            left_idx = min_idx - 1 if min_idx > 0 else min_idx
            right_idx = max_idx + 1 if max_idx < len(fcurve.keyframe_points) - 1 else max_idx
            
            left_y = fcurve.keyframe_points[left_idx].co.y
            left_x = fcurve.keyframe_points[left_idx].co.x
            right_y = fcurve.keyframe_points[right_idx].co.y
            right_x = fcurve.keyframe_points[right_idx].co.x
            min_selected_x = fcurve.keyframe_points[min_idx].co.x
            max_selected_x = fcurve.keyframe_points[max_idx].co.x
            
            denom_left = right_x - min_selected_x
            denom_right = max_selected_x - left_x
            
            for info in keys:
                idx = info[0]
                k = fcurve.keyframe_points[idx]
                orig_y = info[2]
                orig_hl_y = info[4]
                orig_hr_y = info[6]
                curr_x = info[1]
                
                # Left-aligned target (at factor = 0.0)
                t_left = (curr_x - min_selected_x) / denom_left if denom_left != 0.0 else 0.0
                sp_left = 0.5 * (1.0 - math.cos(t_left * math.pi))
                target_left_y = left_y + (right_y - left_y) * sp_left
                
                # Right-aligned target (at factor = 1.0)
                t_right = (curr_x - left_x) / denom_right if denom_right != 0.0 else 1.0
                sp_right = 0.5 * (1.0 - math.cos(t_right * math.pi))
                target_right_y = left_y + (right_y - left_y) * sp_right
                
                # Blend
                new_y = target_left_y + (target_right_y - target_left_y) * factor
                dy = new_y - orig_y
                
                k.co.y = new_y
                k.handle_left.y = orig_hl_y + dy
                k.handle_right.y = orig_hr_y + dy
                    
            fcurve.update()


# ═════════════════════════════════════════════════════════════
#  Cache Helper Functions
# ═════════════════════════════════════════════════════════════

def cache_keyframe_data(context):
    """
    Returns a dictionary of the initial state of all selected keyframes.
    Format:
    {
        fcurve: [
            (index, co_x, co_y, hl_x, hl_y, hr_x, hr_y, hl_type, hr_type, interpolation)
        ]
    }
    """
    cache = {}
    selected_fcurves = context.selected_editable_fcurves
    if not selected_fcurves:
        return cache
        
    for fcurve in selected_fcurves:
        keys_info = []
        for idx, k in enumerate(fcurve.keyframe_points):
            if k.select_control_point:
                keys_info.append((
                    idx,
                    k.co.x, k.co.y,
                    k.handle_left.x, k.handle_left.y,
                    k.handle_right.x, k.handle_right.y,
                    k.handle_left_type, k.handle_right_type,
                    k.interpolation
                ))
        if keys_info:
            cache[fcurve] = keys_info
    return cache


def get_cached_val(fcurve, idx, cache_map):
    """Gets the original Y value from cache, or falls back to live keyframe."""
    if (fcurve, idx) in cache_map:
        return cache_map[(fcurve, idx)][2] # co_y
    if 0 <= idx < len(fcurve.keyframe_points):
        return fcurve.keyframe_points[idx].co.y
    return None


def get_cached_frame(fcurve, idx, cache_map):
    """Gets the original X frame from cache, or falls back to live keyframe."""
    if (fcurve, idx) in cache_map:
        return cache_map[(fcurve, idx)][1] # co_x
    if 0 <= idx < len(fcurve.keyframe_points):
        return fcurve.keyframe_points[idx].co.x
    return None


# ═════════════════════════════════════════════════════════════
#  Modal Operator for Interactive Slider Dragging
# ═════════════════════════════════════════════════════════════

class GRAPH_OT_modal_slider(bpy.types.Operator):
    """Interactive slider overlay to adjust keyframes by dragging the mouse"""
    bl_idname = "graph.toolboard_modal_slider"
    bl_label = "Interactive Tool Board Slider"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(
        items=[
            ('TWEEN', 'Tween', 'Blend between neighbors'),
            ('EASE', 'Ease', 'Blend handles to flat/steep'),
            ('EASE_BOTH', 'Ease Both', 'Blend both handles together'),
            ('PUSH_PULL', 'Push & Pull', 'Magnify deviation from linear interpolation'),
            ('SCALE', 'Scale', 'Scale key values relative to pivot')
        ],
        default='TWEEN'
    )
    
    pivot_mode: bpy.props.EnumProperty(
        items=[
            ('AVERAGE', 'Average', ''),
            ('CURSOR', 'Cursor', ''),
            ('ZERO', 'Zero', ''),
            ('NEIGHBOR_LEFT', 'Neighbor Left', ''),
            ('NEIGHBOR_RIGHT', 'Neighbor Right', '')
        ],
        default='AVERAGE'
    )
    
    factor: bpy.props.FloatProperty(default=0.0)
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'GRAPH_EDITOR' and context.selected_editable_fcurves

    def modal(self, context, event):
        # Redraw
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            dx = event.mouse_x - self.start_mouse_x
            
            # Map mouse movement to factor based on mode
            if self.mode == 'TWEEN':
                # Map 0 to 1 (0 to 200px)
                self.factor = min(max(dx / 200.0, 0.0), 1.0)
            elif self.mode in ('EASE', 'EASE_BOTH'):
                # Map -1 to 1 (-200px to 200px)
                self.factor = min(max(dx / 200.0, -1.0), 1.0)
            elif self.mode == 'PUSH_PULL':
                # Map -1 to 2 (-100px to 200px)
                self.factor = (dx / 150.0) + 1.0
                self.factor = min(max(self.factor, -1.0), 3.0)
            elif self.mode == 'SCALE':
                # Map 0 to 2 (0 to 200px, 1.0 is default)
                self.factor = (dx / 200.0) + 1.0
                self.factor = min(max(self.factor, 0.0), 5.0)
                
            self.apply_transformation(context)
            
        elif event.type == 'LEFTMOUSE' or event.type in ('RET', 'NUMPAD_ENTER'):
            # Confirm
            self.cleanup(context)
            # Push history state
            bpy.ops.ed.undo_push(message=f"Graph Toolboard: {self.mode}")
            return {'FINISHED'}
            
        elif event.type in ('RIGHTMOUSE', 'ESC'):
            # Cancel: Restore original values
            self.restore_keys()
            self.cleanup(context)
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self._area = context.area
        self.start_mouse_x = event.mouse_x
        
        # Cache current keys
        self.cache = cache_keyframe_data(context)
        if not self.cache:
            self.report({'WARNING'}, "No selected keyframes found!")
            return {'CANCELLED'}
            
        # Create a fast lookup map: (fcurve, idx) -> original data
        self.cache_map = {}
        for fcurve, keys_info in self.cache.items():
            for info in keys_info:
                self.cache_map[(fcurve, info[0])] = info

        # Precompute pivots if needed for SCALE or TWEEN
        if self.mode == 'SCALE':
            if self.pivot_mode == 'AVERAGE':
                total_y = 0.0
                count = 0
                for fcurve, keys_info in self.cache.items():
                    for info in keys_info:
                        total_y += info[2] # co_y
                        count += 1
                self.avg_y = total_y / count if count > 0 else 0.0
            elif self.pivot_mode == 'NEIGHBOR_LEFT':
                self.pivot_y_map = {}
                for fcurve, keys_info in self.cache.items():
                    min_idx = min(info[0] for info in keys_info)
                    prev_y = get_cached_val(fcurve, min_idx - 1, self.cache_map)
                    if prev_y is None:
                        prev_y = self.cache_map[(fcurve, min_idx)][2]
                    self.pivot_y_map[fcurve] = prev_y
            elif self.pivot_mode == 'NEIGHBOR_RIGHT':
                self.pivot_y_map = {}
                for fcurve, keys_info in self.cache.items():
                    max_idx = max(info[0] for info in keys_info)
                    next_y = get_cached_val(fcurve, max_idx + 1, self.cache_map)
                    if next_y is None:
                        next_y = self.cache_map[(fcurve, max_idx)][2]
                    self.pivot_y_map[fcurve] = next_y
        elif self.mode == 'TWEEN':
            pass
            
        # Initialize default factor
        if self.mode == 'TWEEN':
            self.factor = 0.5
        elif self.mode in ('EASE', 'EASE_BOTH'):
            self.factor = 0.0
        elif self.mode == 'PUSH_PULL':
            self.factor = 1.0
        elif self.mode == 'SCALE':
            self.factor = 1.0
            
        # Apply initial state
        self.apply_transformation(context)
        
        # Register drawing handler
        self._draw_handle = bpy.types.SpaceGraphEditor.draw_handler_add(
            draw_hud_callback, (self, context), 'WINDOW', 'POST_PIXEL'
        )
        
        # Change cursor
        context.window.cursor_modal_set('SCROLL_X')
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def cleanup(self, context):
        bpy.types.SpaceGraphEditor.draw_handler_remove(self._draw_handle, 'WINDOW')
        context.window.cursor_modal_restore()
        context.area.tag_redraw()

    def restore_keys(self):
        for fcurve, keys_info in self.cache.items():
            for info in keys_info:
                idx = info[0]
                k = fcurve.keyframe_points[idx]
                k.co.x = info[1]
                k.co.y = info[2]
                k.handle_left.x = info[3]
                k.handle_left.y = info[4]
                k.handle_right.x = info[5]
                k.handle_right.y = info[6]
                k.handle_left_type = info[7]
                k.handle_right_type = info[8]
                k.interpolation = info[9]
            fcurve.update()

    def apply_transformation(self, context):
        # Restore keys to avoid stale modified neighbor values
        self.restore_keys()
        
        # Perform transformations based on mode and self.factor
        for fcurve, keys_info in self.cache.items():
            if self.mode == 'TWEEN':
                selected_indices = [info[0] for info in keys_info]
                min_idx = min(selected_indices)
                max_idx = max(selected_indices)
                
                left_idx = min_idx - 1 if min_idx > 0 else min_idx
                right_idx = max_idx + 1 if max_idx < len(fcurve.keyframe_points) - 1 else max_idx
                
                left_y = fcurve.keyframe_points[left_idx].co.y
                left_x = fcurve.keyframe_points[left_idx].co.x
                right_y = fcurve.keyframe_points[right_idx].co.y
                right_x = fcurve.keyframe_points[right_idx].co.x
                min_selected_x = fcurve.keyframe_points[min_idx].co.x
                max_selected_x = fcurve.keyframe_points[max_idx].co.x
                
                denom_left = right_x - min_selected_x
                denom_right = max_selected_x - left_x
                
                for info in keys_info:
                    idx = info[0]
                    k = fcurve.keyframe_points[idx]
                    orig_y = info[2]
                    orig_hl_y = info[4]
                    orig_hr_y = info[6]
                    curr_x = info[1]
                    
                    # Left-aligned target (at factor = 0.0)
                    t_left = (curr_x - min_selected_x) / denom_left if denom_left != 0.0 else 0.0
                    sp_left = 0.5 * (1.0 - math.cos(t_left * math.pi))
                    target_left_y = left_y + (right_y - left_y) * sp_left
                    
                    # Right-aligned target (at factor = 1.0)
                    t_right = (curr_x - left_x) / denom_right if denom_right != 0.0 else 1.0
                    sp_right = 0.5 * (1.0 - math.cos(t_right * math.pi))
                    target_right_y = left_y + (right_y - left_y) * sp_right
                    
                    # Blend
                    new_y = target_left_y + (target_right_y - target_left_y) * self.factor
                    dy = new_y - orig_y
                    
                    k.co.y = new_y
                    k.handle_left.y = orig_hl_y + dy
                    k.handle_right.y = orig_hr_y + dy
                fcurve.update()
                continue
                
            if self.mode in ('EASE', 'EASE_BOTH'):
                selected_indices = sorted([info[0] for info in keys_info])
                if len(selected_indices) >= 3:
                    first_idx = selected_indices[0]
                    last_idx = selected_indices[-1]
                    
                    fv = self.cache_map[(fcurve, first_idx)][2]
                    lv = self.cache_map[(fcurve, last_idx)][2]
                    ff = self.cache_map[(fcurve, first_idx)][1]
                    lf = self.cache_map[(fcurve, last_idx)][1]
                    
                    tf = lf - ff
                    tv = lv - fv
                    
                    if tf != 0:
                        for info in keys_info:
                            idx = info[0]
                            if idx == first_idx or idx == last_idx:
                                continue
                                
                            k = fcurve.keyframe_points[idx]
                            orig_x, orig_y = info[1], info[2]
                            orig_hl_y = info[4]
                            orig_hr_y = info[6]
                            
                            currTime = orig_x - ff
                            timePos = currTime / tf
                            
                            if self.mode == 'EASE':
                                t_blend = abs(self.factor)
                                str_val = t_blend * 9.0 + 1.0
                                if self.factor < 0:
                                    # Ease In
                                    eased_y = fv + tv * (timePos ** str_val)
                                else:
                                    # Ease Out
                                    eased_y = fv + tv * (1.0 - (1.0 - timePos) ** str_val)
                                new_y = orig_y + (eased_y - orig_y) * t_blend
                            else:  # EASE_BOTH
                                t_blend = abs(self.factor)
                                str_val = t_blend * 9.0 + 1.0
                                if timePos < 0.5:
                                    eased_y = fv + tv * (0.5 * (2.0 * timePos) ** str_val)
                                else:
                                    eased_y = fv + tv * (1.0 - 0.5 * (2.0 * (1.0 - timePos)) ** str_val)
                                new_y = orig_y + (eased_y - orig_y) * t_blend
                                
                            dy = new_y - orig_y
                            k.co.y = new_y
                            k.handle_left.y = orig_hl_y + dy
                            k.handle_right.y = orig_hr_y + dy
                fcurve.update()
                continue
            if self.mode == 'PUSH_PULL':
                selected_indices = [info[0] for info in keys_info]
                min_idx = min(selected_indices)
                max_idx = max(selected_indices)
                
                left_idx = min_idx - 1 if min_idx > 0 else min_idx
                right_idx = max_idx + 1 if max_idx < len(fcurve.keyframe_points) - 1 else max_idx
                
                left_y = get_cached_val(fcurve, left_idx, self.cache_map)
                left_x = get_cached_frame(fcurve, left_idx, self.cache_map)
                right_y = get_cached_val(fcurve, right_idx, self.cache_map)
                right_x = get_cached_frame(fcurve, right_idx, self.cache_map)
                
                if left_y is None: left_y = fcurve.keyframe_points[left_idx].co.y
                if left_x is None: left_x = fcurve.keyframe_points[left_idx].co.x
                if right_y is None: right_y = fcurve.keyframe_points[right_idx].co.y
                if right_x is None: right_x = fcurve.keyframe_points[right_idx].co.x
                
                denom = right_x - left_x
                
                for info in keys_info:
                    idx = info[0]
                    k = fcurve.keyframe_points[idx]
                    orig_x, orig_y = info[1], info[2]
                    orig_hl_y = info[4]
                    orig_hr_y = info[6]
                    
                    if denom != 0.0:
                        t_frame = (orig_x - left_x) / denom
                        linear_y = left_y + (right_y - left_y) * t_frame
                    else:
                        linear_y = left_y
                        
                    orig_dev = orig_y - linear_y
                    new_y = linear_y + orig_dev * self.factor
                    
                    dy = new_y - orig_y
                    k.co.y = new_y
                    k.handle_left.y = orig_hl_y + dy
                    k.handle_right.y = orig_hr_y + dy
                fcurve.update()
                continue
                
            for info in keys_info:
                idx = info[0]
                k = fcurve.keyframe_points[idx]
                
                # Retrieve original data
                orig_x, orig_y = info[1], info[2]
                orig_hl_x, orig_hl_y = info[3], info[4]
                orig_hr_x, orig_hr_y = info[5], info[6]
                
                if self.mode == 'SCALE':
                    # Determine pivot
                    if self.pivot_mode == 'ZERO':
                        p_y = 0.0
                    elif self.pivot_mode == 'CURSOR':
                        # Get cursor value from editor space
                        p_y = context.space_data.cursor_value if context.space_data else 0.0
                    elif self.pivot_mode in ('NEIGHBOR_LEFT', 'NEIGHBOR_RIGHT'):
                        p_y = self.pivot_y_map.get(fcurve, 0.0)
                    else: # AVERAGE
                        p_y = self.avg_y
                        
                    new_y = p_y + (orig_y - p_y) * self.factor
                    dy = new_y - orig_y
                    k.co.y = new_y
                    k.handle_left.y = orig_hl_y + dy
                    k.handle_right.y = orig_hr_y + dy
                    
            fcurve.update()


# ═════════════════════════════════════════════════════════════
#  Standard Discrete Operators (Buttons & Menu Items)
# ═════════════════════════════════════════════════════════════

class GRAPH_OT_quick_tween(bpy.types.Operator):
    """Tween selected keys by a fixed preset value"""
    bl_idname = "graph.toolboard_quick_tween"
    bl_label = "Quick Tween"
    bl_options = {'REGISTER', 'UNDO'}
    
    factor: bpy.props.FloatProperty(name="Factor", default=0.5, min=0.0, max=1.0)
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        scene = context.scene
        if scene and hasattr(scene, "graph_toolboard"):
            # Set the slider value directly, which triggers the cache-aware update_tween_slider callback
            scene.graph_toolboard.tween_slider = self.factor * 100.0
            
            # Push undo history for discrete operator
            bpy.ops.ed.undo_push(message=f"Tween {int(self.factor * 100)}%")
            
        return {'FINISHED'}


class GRAPH_OT_quick_ease(bpy.types.Operator):
    """Ease selected keys by a fixed preset value"""
    bl_idname = "graph.toolboard_quick_ease"
    bl_label = "Quick Ease"
    bl_options = {'REGISTER', 'UNDO'}
    
    factor: bpy.props.FloatProperty(name="Factor", default=0.5, min=-1.0, max=1.0)
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        cache = cache_keyframe_data(context)
        if not cache:
            return {'CANCELLED'}
            
        for fcurve, keys_info in cache.items():
            for info in keys_info:
                idx = info[0]
                k = fcurve.keyframe_points[idx]
                k.handle_left_type = 'FREE'
                k.handle_right_type = 'FREE'
                
                orig_x, orig_y = info[1], info[2]
                orig_hl_x, orig_hl_y = info[3], info[4]
                orig_hr_x, orig_hr_y = info[5], info[6]
                
                if self.factor < 0: # Ease In
                    t = abs(self.factor)
                    k.handle_left.y = orig_hl_y + (orig_y - orig_hl_y) * t
                    k.handle_left.x = orig_x + (orig_hl_x - orig_x) * (1.0 + t * 0.5)
                elif self.factor > 0: # Ease Out
                    t = self.factor
                    k.handle_right.y = orig_hr_y + (orig_y - orig_hr_y) * t
                    k.handle_right.x = orig_x + (orig_hr_x - orig_x) * (1.0 + t * 0.5)
                else: # Reset to linear interpolation of handles or flat
                    k.handle_left.y = orig_hl_y
                    k.handle_left.x = orig_hl_x
                    k.handle_right.y = orig_hr_y
                    k.handle_right.x = orig_hr_x
                    
            fcurve.update()
        return {'FINISHED'}


class GRAPH_OT_nudge_keys(bpy.types.Operator):
    """Shift selected keyframes in time"""
    bl_idname = "graph.toolboard_nudge_keys"
    bl_label = "Nudge Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: bpy.props.EnumProperty(
        items=[
            ('LEFT', 'Left', 'Shift keys earlier'),
            ('RIGHT', 'Right', 'Shift keys later')
        ],
        default='RIGHT'
    )
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        props = context.scene.graph_toolboard
        delta = props.nudge_frames if self.direction == 'RIGHT' else -props.nudge_frames
        
        for fcurve in context.selected_editable_fcurves:
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    k.co.x += delta
                    k.handle_left.x += delta
                    k.handle_right.x += delta
            fcurve.keyframe_points.sort()
            fcurve.update()
        return {'FINISHED'}


class GRAPH_OT_scale_spacing(bpy.types.Operator):
    """Double or Halve the timing spacing between selected keys"""
    bl_idname = "graph.toolboard_scale_spacing"
    bl_label = "Scale Time Spacing"
    bl_options = {'REGISTER', 'UNDO'}
    
    factor: bpy.props.FloatProperty(name="Factor", default=1.0)
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        # Calculate pivot: average frame of selected keys
        frames = []
        for fcurve in context.selected_editable_fcurves:
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    frames.append(k.co.x)
                    
        if not frames:
            return {'CANCELLED'}
            
        pivot = sum(frames) / len(frames)
        
        for fcurve in context.selected_editable_fcurves:
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    k.co.x = pivot + (k.co.x - pivot) * self.factor
                    k.handle_left.x = pivot + (k.handle_left.x - pivot) * self.factor
                    k.handle_right.x = pivot + (k.handle_right.x - pivot) * self.factor
            fcurve.keyframe_points.sort()
            fcurve.update()
        return {'FINISHED'}


class GRAPH_OT_clean_redundant(bpy.types.Operator):
    """Remove keys that do not contribute to the animation curve shape"""
    bl_idname = "graph.toolboard_clean_redundant"
    bl_label = "Clean Redundant Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        props = context.scene.graph_toolboard
        threshold = props.clean_threshold
        removed_count = 0
        
        for fcurve in context.selected_editable_fcurves:
            # We must compile a list of keys to remove, then remove them.
            # Avoid removing while iterating index.
            keys_to_remove = []
            points = fcurve.keyframe_points
            
            # Find selected keys that are not the start/end of fcurve
            for idx in range(1, len(points) - 1):
                k = points[idx]
                if k.select_control_point:
                    prev_k = points[idx - 1]
                    next_k = points[idx + 1]
                    
                    # Linearly interpolated value at current frame
                    denom = next_k.co.x - prev_k.co.x
                    if denom != 0:
                        t = (k.co.x - prev_k.co.x) / denom
                        linear_y = prev_k.co.y + (next_k.co.y - prev_k.co.y) * t
                        
                        if abs(k.co.y - linear_y) <= threshold:
                            keys_to_remove.append(k)
                            
            for k in keys_to_remove:
                points.remove(k)
                removed_count += 1
                
            fcurve.update()
            
        self.report({'INFO'}, f"Cleaned {removed_count} redundant keyframes.")
        return {'FINISHED'}


class GRAPH_OT_mirror_keys(bpy.types.Operator):
    """Mirror selected keyframes over a chosen anchor"""
    bl_idname = "graph.toolboard_mirror_keys"
    bl_label = "Mirror Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(
        items=[
            ('TIME_LEFT', 'By Times Over Neighbor Left', ''),
            ('VALUE_LEFT', 'By Values Over Neighbor Left', ''),
            ('TIME_RIGHT', 'By Times Over Neighbor Right', ''),
            ('VALUE_RIGHT', 'By Values Over Neighbor Right', ''),
            ('TIME_AVG', 'By Times Over Neighbor Average', ''),
            ('VALUE_AVG', 'By Values Over Neighbor Average', ''),
            ('TIME_ZERO', 'By Times Over Zero (Default)', ''),
            ('VALUE_ZERO', 'By Values Over Zero (Default)', '')
        ],
        default='TIME_LEFT'
    )
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        is_time_mirror = self.mode in ('TIME_LEFT', 'TIME_RIGHT', 'TIME_AVG', 'TIME_ZERO')
        
        for fcurve in context.selected_editable_fcurves:
            # Gather indices of all selected keys in this fcurve
            sel_indices = [idx for idx, k in enumerate(fcurve.keyframe_points) if k.select_control_point]
            if not sel_indices:
                continue
                
            # Determine pivot per fcurve based on selection boundary
            if self.mode in ('TIME_ZERO', 'VALUE_ZERO'):
                pivot_val = 0.0
            elif self.mode in ('TIME_LEFT', 'VALUE_LEFT'):
                min_idx = min(sel_indices)
                pivot_k_idx = min_idx - 1
                if pivot_k_idx < 0:
                    pivot_k_idx = min_idx # fallback to first selected key
                pivot_key = fcurve.keyframe_points[pivot_k_idx]
                pivot_val = pivot_key.co.x if is_time_mirror else pivot_key.co.y
            elif self.mode in ('TIME_RIGHT', 'VALUE_RIGHT'):
                max_idx = max(sel_indices)
                pivot_k_idx = max_idx + 1
                if pivot_k_idx >= len(fcurve.keyframe_points):
                    pivot_k_idx = max_idx # fallback to last selected key
                pivot_key = fcurve.keyframe_points[pivot_k_idx]
                pivot_val = pivot_key.co.x if is_time_mirror else pivot_key.co.y
            else: # TIME_AVG or VALUE_AVG (Average of Neighbor Left + Neighbor Right)
                min_idx = min(sel_indices)
                max_idx = max(sel_indices)
                
                prev_idx = min_idx - 1
                next_idx = max_idx + 1
                
                if prev_idx < 0:
                    prev_idx = min_idx
                if next_idx >= len(fcurve.keyframe_points):
                    next_idx = max_idx
                    
                prev_key = fcurve.keyframe_points[prev_idx]
                next_key = fcurve.keyframe_points[next_idx]
                
                if is_time_mirror:
                    pivot_val = (prev_key.co.x + next_key.co.x) / 2.0
                else:
                    pivot_val = (prev_key.co.y + next_key.co.y) / 2.0
                
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    if is_time_mirror:
                        # X Mirroring
                        k.co.x = 2 * pivot_val - k.co.x
                        
                        # Swap and mirror X handles
                        hl_x_orig = k.handle_left.x
                        hr_x_orig = k.handle_right.x
                        k.handle_left.x = 2 * pivot_val - hr_x_orig
                        k.handle_right.x = 2 * pivot_val - hl_x_orig
                        
                        # Swap Y handles as well to keep tangent intact
                        hl_y_orig = k.handle_left.y
                        hr_y_orig = k.handle_right.y
                        k.handle_left.y = hr_y_orig
                        k.handle_right.y = hl_y_orig
                    else:
                        # Y Mirroring
                        k.co.y = 2 * pivot_val - k.co.y
                        k.handle_left.y = 2 * pivot_val - k.handle_left.y
                        k.handle_right.y = 2 * pivot_val - k.handle_right.y
                        
            if is_time_mirror:
                fcurve.keyframe_points.sort()
            fcurve.update()
            
        return {'FINISHED'}


class GRAPH_OT_snap_keys(bpy.types.Operator):
    """Snap selected keyframes to targets"""
    bl_idname = "graph.toolboard_snap_keys"
    bl_label = "Snap Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    target: bpy.props.EnumProperty(
        items=[
            ('FRAME', 'To Nearest Frame', ''),
            ('CURSOR_X', 'To Cursor Time', ''),
            ('CURSOR_Y', 'To Cursor Value', ''),
            ('VALUE_ZERO', 'To Zero Value', '')
        ],
        default='FRAME'
    )
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        space = context.space_data if context.space_data.type == 'GRAPH_EDITOR' else None
        
        for fcurve in context.selected_editable_fcurves:
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    if self.target == 'FRAME':
                        # Snap X to nearest integer
                        orig_x = k.co.x
                        new_x = round(orig_x)
                        dx = new_x - orig_x
                        k.co.x = new_x
                        k.handle_left.x += dx
                        k.handle_right.x += dx
                    elif self.target == 'CURSOR_X':
                        # Snap X to Cursor Time
                        if space:
                            orig_x = k.co.x
                            new_x = space.cursor_time
                            dx = new_x - orig_x
                            k.co.x = new_x
                            k.handle_left.x += dx
                            k.handle_right.x += dx
                    elif self.target == 'CURSOR_Y':
                        # Snap Y to Cursor Value
                        if space:
                            orig_y = k.co.y
                            new_y = space.cursor_value
                            dy = new_y - orig_y
                            k.co.y = new_y
                            k.handle_left.y += dy
                            k.handle_right.y += dy
                    elif self.target == 'VALUE_ZERO':
                        # Snap Y to 0
                        orig_y = k.co.y
                        dy = -orig_y
                        k.co.y = 0.0
                        k.handle_left.y += dy
                        k.handle_right.y += dy
            fcurve.keyframe_points.sort()
            fcurve.update()
        return {'FINISHED'}


# Global clipboard variables
_copied_data = []
_copied_min_frame = 0.0
_copied_max_frame = 0.0

class GRAPH_OT_copy_keys(bpy.types.Operator):
    """Copy selected keyframes of selected channels"""
    bl_idname = "graph.toolboard_copy_keys"
    bl_label = "Copy Keys"
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves
        
    def execute(self, context):
        global _copied_data, _copied_min_frame, _copied_max_frame
        _copied_data.clear()
        
        selected_fcurves = context.selected_editable_fcurves
        
        frames = []
        for fcurve in selected_fcurves:
            for k in fcurve.keyframe_points:
                if k.select_control_point:
                    frames.append(k.co.x)
                    
        if not frames:
            self.report({'WARNING'}, "No selected keyframes to copy!")
            return {'CANCELLED'}
            
        _copied_min_frame = min(frames)
        _copied_max_frame = max(frames)
        
        for fcurve in selected_fcurves:
            keys_list = []
            for idx, k in enumerate(fcurve.keyframe_points):
                if k.select_control_point:
                    keys_list.append({
                        'co_x': k.co.x,
                        'co_y': k.co.y,
                        'hl_x': k.handle_left.x,
                        'hl_y': k.handle_left.y,
                        'hr_x': k.handle_right.x,
                        'hr_y': k.handle_right.y,
                        'hl_type': k.handle_left_type,
                        'hr_type': k.handle_right_type,
                        'interp': k.interpolation
                    })
            if keys_list:
                _copied_data.append({
                    'keys': keys_list
                })
                
        self.report({'INFO'}, f"Copied {len(frames)} keyframes across {len(_copied_data)} channels.")
        return {'FINISHED'}


class GRAPH_OT_paste_keys(bpy.types.Operator):
    """Paste copied keyframes with chosen mode and pivot options"""
    bl_idname = "graph.toolboard_paste_keys"
    bl_label = "Paste Keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves and _copied_data
        
    def execute(self, context):
        global _copied_data, _copied_min_frame, _copied_max_frame
        
        props = context.scene.graph_toolboard
        paste_mode = props.paste_mode
        paste_pivot = props.paste_pivot
        
        target_fcurves = context.selected_editable_fcurves
        if not target_fcurves:
            return {'CANCELLED'}
            
        if paste_pivot == 'CURRENT':
            F_start = context.scene.frame_current
        else: # CUSTOM
            F_start = props.paste_custom_frame
            
        duration = _copied_max_frame - _copied_min_frame
        
        for i, target_fcurve in enumerate(target_fcurves):
            copied_idx = i % len(_copied_data)
            copied_channel = _copied_data[copied_idx]
            copied_keys = copied_channel['keys']
            
            if paste_mode == 'INSERT':
                keys_to_shift = sorted(
                    [k for k in target_fcurve.keyframe_points if k.co.x >= F_start],
                    key=lambda k: k.co.x,
                    reverse=True
                )
                for k in keys_to_shift:
                    k.co.x += duration
                    k.handle_left.x += duration
                    k.handle_right.x += duration
                    
            elif paste_mode == 'REPLACE':
                keys_to_delete = [
                    k for k in target_fcurve.keyframe_points 
                    if F_start <= k.co.x <= F_start + duration
                ]
                for k in keys_to_delete:
                    target_fcurve.keyframe_points.remove(k)
            
            for ck in copied_keys:
                rel_x = ck['co_x'] - _copied_min_frame
                new_x = F_start + rel_x
                
                if paste_mode == 'MERGE':
                    dups = [k for k in target_fcurve.keyframe_points if abs(k.co.x - new_x) < 0.001]
                    for d in dups:
                        target_fcurve.keyframe_points.remove(d)
                
                new_k = target_fcurve.keyframe_points.insert(new_x, value=ck['co_y'])
                
                rel_hl_x = ck['hl_x'] - _copied_min_frame
                rel_hr_x = ck['hr_x'] - _copied_min_frame
                
                new_k.handle_left.x = F_start + rel_hl_x
                new_k.handle_left.y = ck['hl_y']
                new_k.handle_right.x = F_start + rel_hr_x
                new_k.handle_right.y = ck['hr_y']
                
                new_k.handle_left_type = ck['hl_type']
                new_k.handle_right_type = ck['hr_type']
                new_k.interpolation = ck['interp']
                new_k.select_control_point = True
                
            target_fcurve.keyframe_points.sort()
            target_fcurve.update()
            
        self.report({'INFO'}, f"Pasted copied keyframes at frame {F_start:.1f} using {paste_mode} mode.")
        return {'FINISHED'}


class GRAPH_OT_toggle_cycles(bpy.types.Operator):
    """Toggle Cycle extrapolation and Cycles modifiers on selected curves"""
    bl_idname = "graph.toolboard_toggle_cycles"
    bl_label = "Toggle Infinity Cycles"
    bl_options = {'REGISTER', 'UNDO'}

    action: bpy.props.EnumProperty(
        items=[
            ('ADD', 'Make Cyclic', ''),
            ('REMOVE', 'Remove Cyclic', ''),
            ('CONSTANT', 'Set Constant', ''),
            ('LINEAR', 'Set Linear', '')
        ],
        default='ADD'
    )

    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves

    def execute(self, context):
        selected_fcurves = context.selected_editable_fcurves
        for fcurve in selected_fcurves:
            if self.action == 'CONSTANT':
                fcurve.extrapolation = 'CONSTANT'
                for mod in list(fcurve.modifiers):
                    if mod.type == 'CYCLES':
                        fcurve.modifiers.remove(mod)
            elif self.action == 'LINEAR':
                fcurve.extrapolation = 'LINEAR'
                for mod in list(fcurve.modifiers):
                    if mod.type == 'CYCLES':
                        fcurve.modifiers.remove(mod)
            elif self.action == 'ADD':
                cycles_mod = None
                for mod in fcurve.modifiers:
                    if mod.type == 'CYCLES':
                        cycles_mod = mod
                        break
                if not cycles_mod:
                    cycles_mod = fcurve.modifiers.new(type='CYCLES')
                cycles_mod.mode_before = 'REPEAT'
                cycles_mod.mode_after = 'REPEAT'
                cycles_mod.cycles_before = 0
                cycles_mod.cycles_after = 0
                cycles_mod.mute = False
                cycles_mod.use_restricted_range = False
            elif self.action == 'REMOVE':
                for mod in list(fcurve.modifiers):
                    if mod.type == 'CYCLES':
                        fcurve.modifiers.remove(mod)
            fcurve.update()
        return {'FINISHED'}


class GRAPH_OT_match_loop_values(bpy.types.Operator):
    """Match the start and end keyframe values for seamless looping"""
    bl_idname = "graph.toolboard_match_loop_values"
    bl_label = "Match Loop Values"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=[
            ('START_TO_END', 'Start to End', 'Copy the value of the first keyframe to the last keyframe'),
            ('END_TO_START', 'End to Start', 'Copy the value of the last keyframe to the first keyframe'),
            ('AVERAGE', 'Average', 'Set both start and end keyframes to their average value')
        ],
        default='START_TO_END'
    )

    @classmethod
    def poll(cls, context):
        return context.selected_editable_fcurves

    def execute(self, context):
        selected_fcurves = context.selected_editable_fcurves
        for fcurve in selected_fcurves:
            sel_keys = [k for k in fcurve.keyframe_points if k.select_control_point]
            if sel_keys:
                k_first = min(sel_keys, key=lambda k: k.co.x)
                k_last = max(sel_keys, key=lambda k: k.co.x)
            else:
                if len(fcurve.keyframe_points) < 2:
                    continue
                k_first = fcurve.keyframe_points[0]
                k_last = fcurve.keyframe_points[-1]
                
            if k_first == k_last:
                continue
                
            val_first = k_first.co.y
            val_last = k_last.co.y
            
            if self.direction == 'START_TO_END':
                k_last.co.y = val_first
                dy = val_first - val_last
                k_last.handle_left.y += dy
                k_last.handle_right.y += dy
            elif self.direction == 'END_TO_START':
                k_first.co.y = val_last
                dy = val_last - val_first
                k_first.handle_left.y += dy
                k_first.handle_right.y += dy
            elif self.direction == 'AVERAGE':
                avg_val = (val_first + val_last) / 2.0
                
                dy_first = avg_val - val_first
                k_first.co.y = avg_val
                k_first.handle_left.y += dy_first
                k_first.handle_right.y += dy_first
                
                dy_last = avg_val - val_last
                k_last.co.y = avg_val
                k_last.handle_left.y += dy_last
                k_last.handle_right.y += dy_last
                
            fcurve.update()
            
        self.report({'INFO'}, "Matched loop start/end values.")
        return {'FINISHED'}


# ═════════════════════════════════════════════════════════════
#  Registration
# ═════════════════════════════════════════════════════════════

_classes = (
    GRAPH_OT_modal_slider,
    GRAPH_OT_quick_tween,
    GRAPH_OT_quick_ease,
    GRAPH_OT_nudge_keys,
    GRAPH_OT_scale_spacing,
    GRAPH_OT_clean_redundant,
    GRAPH_OT_mirror_keys,
    GRAPH_OT_snap_keys,
    GRAPH_OT_copy_keys,
    GRAPH_OT_paste_keys,
    GRAPH_OT_toggle_cycles,
    GRAPH_OT_match_loop_values,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
