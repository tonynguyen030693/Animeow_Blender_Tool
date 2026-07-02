# ─────────────────────────────────────────────────────────────
# BonePicker – Canvas drawing engine (GPU / BLF)
# ─────────────────────────────────────────────────────────────
"""
Draws the picker canvas inside a Blender region using the `gpu` module
for shapes and `blf` for text labels.
"""
import math
import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


from .utils import (
    generate_circle_vertices,
    generate_rounded_rect_vertices,
    get_selected_bone_names,
    hit_test_button,
)

# Lazy shader getter to prevent context errors during startup
_shader = None

def _get_shader():
    global _shader
    if _shader is None:
        _shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    return _shader


# ── Low-level drawing primitives ────────────────────────────

def _draw_filled_rect(x, y, w, h, color):
    """Draw a filled rectangle."""
    verts = [
        (x, y), (x + w, y),
        (x + w, y + h), (x, y + h),
    ]
    indices = [(0, 1, 2), (0, 2, 3)]
    shader = _get_shader()
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _draw_filled_polygon(verts, color):
    """Draw a filled convex polygon using triangle fan from centroid."""
    if len(verts) < 3:
        return
    # Compute centroid
    cx = sum(v[0] for v in verts) / len(verts)
    cy = sum(v[1] for v in verts) / len(verts)
    center = (cx, cy)
    all_verts = [center] + list(verts)
    indices = []
    n = len(verts)
    for i in range(n):
        indices.append((0, i + 1, (i % n) + 1 if i + 1 < n else 1))
    # Fix last triangle
    indices[-1] = (0, n, 1)
    shader = _get_shader()
    batch = batch_for_shader(
        shader, 'TRIS', {"pos": all_verts}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _draw_border_polygon(verts, color, line_width=1.0):
    """Draw the outline of a polygon."""
    gpu.state.line_width_set(line_width)
    closed = list(verts) + [verts[0]]
    shader = _get_shader()
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": closed})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)


def _draw_border_rect(x, y, w, h, color, line_width=1.0):
    """Draw a rectangle outline."""
    verts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    _draw_border_polygon(verts, color, line_width)


def _draw_text(text, x, y, size=12, color=(1, 1, 1, 1)):
    """Draw a text string at (x, y) using blf."""
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def _get_text_dimensions(text, size=12):
    """Return (width, height) of the text."""
    font_id = 0
    blf.size(font_id, size)
    return blf.dimensions(font_id, text)


# ── High-level shape drawing ────────────────────────────────

def draw_button(btn, vm, hovered=False, selected=False):
    """
    Draw a single picker button.

    btn      – PickerButtonItem property group
    vm       – ViewportMapper instance
    hovered  – whether the mouse is over this button
    selected – whether the bone(s) assigned to this button are selected
    """
    # Map data coords → viewport coords
    vx, vy = vm.to_viewport(btn.pos_x, btn.pos_y)
    vw = btn.width * vm.zoom
    vh = btn.height * vm.zoom

    # Pick color based on state
    if selected:
        fill_color = tuple(btn.color_selected)
    elif hovered:
        fill_color = tuple(btn.color_hover)
    else:
        fill_color = tuple(btn.color_normal)

    border_color = tuple(btn.border_color)
    text_color = tuple(btn.text_color)

    shape = btn.shape

    if shape == 'RECT':
        _draw_filled_rect(vx, vy, vw, vh, fill_color)
        _draw_border_rect(vx, vy, vw, vh, border_color)

    elif shape == 'ROUND':
        cx = vx + vw / 2
        cy = vy + vh / 2
        verts = generate_circle_vertices(cx, cy, vw / 2, vh / 2, segments=32)
        _draw_filled_polygon(verts, fill_color)
        _draw_border_polygon(verts, border_color)

    elif shape == 'ROUNDED_RECT':
        r = btn.corner_radius * vm.zoom
        verts = generate_rounded_rect_vertices(vx, vy, vw, vh, r)
        _draw_filled_polygon(verts, fill_color)
        _draw_border_polygon(verts, border_color)

    # Draw label text (centered)
    label = btn.label
    if label:
        font_size = max(8, int(12 * vm.zoom))
        tw, th = _get_text_dimensions(label, font_size)
        tx = vx + (vw - tw) / 2
        ty = vy + (vh - th) / 2
        _draw_text(label, tx, ty, font_size, text_color)


# ── Canvas background ──────────────────────────────────────

def draw_canvas_background(vm, canvas_w, canvas_h, tab_name=""):
    """Draw a subtle background rectangle and a top header bar for dragging."""
    vx, vy = vm.to_viewport(0, 0)
    vw = canvas_w * vm.zoom
    vh = canvas_h * vm.zoom
    
    # 1. Main canvas area background (dark gray)
    bg_color = (0.16, 0.16, 0.16, 0.95)
    _draw_filled_rect(vx, vy, vw, vh, bg_color)
    
    # 2. Header bar background (medium gray) with UI Scale
    ui_scale = bpy.context.preferences.system.ui_scale
    header_h = 24 * ui_scale
    header_y = vy + vh
    header_bg_color = (0.24, 0.24, 0.24, 1.0)
    _draw_filled_rect(vx, header_y, vw, header_h, header_bg_color)
    
    # Header separator line (darker gray)
    _draw_filled_rect(vx, header_y, vw, 1.0, (0.35, 0.35, 0.35, 1.0))
    
    # Outer border (dark gray border around the entire window including header)
    border_color = (0.35, 0.35, 0.35, 1.0)
    _draw_border_rect(vx, vy, vw, vh + header_h, border_color)
    
    # 3. Draw tab name inside header bar
    if tab_name:
        font_size = int(11 * ui_scale)
        text_y = header_y + 6 * ui_scale
        text_x = vx + 10 * ui_scale
        _draw_text(f"🦴 {tab_name}", text_x, text_y, font_size, (0.85, 0.85, 0.85, 1.0))

    # 4. Draw resize handle at bottom-right corner
    handle_size = 14 * ui_scale
    handle_color = (0.40, 0.40, 0.40, 1.0)
    verts = [
        (vx + vw, vy),
        (vx + vw, vy + handle_size),
        (vx + vw - handle_size, vy)
    ]
    _draw_filled_polygon(verts, handle_color)


# ── Edit-mode selection overlay ─────────────────────────────

def draw_edit_selection(btn, vm):
    """Draw a dashed highlight around a button in edit mode."""
    vx, vy = vm.to_viewport(btn.pos_x, btn.pos_y)
    vw = btn.width * vm.zoom
    vh = btn.height * vm.zoom
    sel_color = (0.2, 0.6, 1.0, 0.9)
    _draw_border_rect(vx - 2, vy - 2, vw + 4, vh + 4, sel_color, line_width=2.0)

    # Draw resize handles (small squares at corners)
    handle_size = 6
    handle_color = (1.0, 1.0, 1.0, 1.0)
    for hx, hy in [
        (vx - handle_size / 2, vy - handle_size / 2),
        (vx + vw - handle_size / 2, vy - handle_size / 2),
        (vx - handle_size / 2, vy + vh - handle_size / 2),
        (vx + vw - handle_size / 2, vy + vh - handle_size / 2),
    ]:
        _draw_filled_rect(hx, hy, handle_size, handle_size, handle_color)
        _draw_border_rect(hx, hy, handle_size, handle_size, (0, 0, 0, 1))


# ── Viewport Mapper ─────────────────────────────────────────

class ViewportMapper:
    """
    Translates between data coordinates (canvas units) and viewport
    coordinates (screen pixels within the region), handling zoom and pan.
    """

    def __init__(self):
        self.zoom = 1.0
        self.origin_x = 0.0  # pan offset in pixels
        self.origin_y = 0.0
        self.region_width = 300
        self.region_height = 300

    def to_viewport(self, ux, uy):
        """Convert data coords → pixel coords."""
        vx = ux * self.zoom + self.origin_x
        vy = uy * self.zoom + self.origin_y
        return vx, vy

    def to_data(self, vx, vy):
        """Convert pixel coords → data coords."""
        ux = (vx - self.origin_x) / self.zoom
        uy = (vy - self.origin_y) / self.zoom
        return ux, uy

    def update_from_props(self, picker_props):
        """Sync with scene properties."""
        self.zoom = picker_props.zoom
        self.origin_x = picker_props.pan_x
        self.origin_y = picker_props.pan_y

    def store_to_props(self, picker_props):
        """Write back to scene properties."""
        picker_props.zoom = self.zoom
        picker_props.pan_x = self.origin_x
        picker_props.pan_y = self.origin_y

    def zoom_at(self, factor, ref_vx, ref_vy):
        """Zoom centered on a reference viewport point."""
        old_ux, old_uy = self.to_data(ref_vx, ref_vy)
        self.zoom = max(0.1, min(5.0, self.zoom * (1.0 + factor)))
        new_vx = old_ux * self.zoom + self.origin_x
        new_vy = old_uy * self.zoom + self.origin_y
        self.origin_x += ref_vx - new_vx
        self.origin_y += ref_vy - new_vy


# ── Main draw callback ─────────────────────────────────────

def draw_picker_callback(context, target_area_ptr):
    """
    Main draw function called from a SpaceView3D draw handler.
    Draws the entire picker canvas with all buttons.
    """
    # Only draw in the area where the handler was registered
    if context.area is None or context.area.as_pointer() != target_area_ptr:
        return

    scene = context.scene
    if not hasattr(scene, 'bone_picker'):
        return
    picker = scene.bone_picker
    if not picker.tabs:
        return
    if picker.active_tab_index < 0 or picker.active_tab_index >= len(picker.tabs):
        return

    tab = picker.tabs[picker.active_tab_index]

    # Build viewport mapper
    vm = ViewportMapper()
    vm.update_from_props(picker)

    # Get region info
    region = context.region
    if region:
        vm.region_width = region.width
        vm.region_height = region.height

    # Enable blending for transparency
    gpu.state.blend_set('ALPHA')

    # Check if this is a dedicated float viewport
    is_dedicated = False
    space = context.space_data
    if space and space.type == 'VIEW_3D':
        if not space.overlay.show_overlays and not space.show_region_toolbar and not space.show_region_header:
            is_dedicated = True

    # If dedicated, draw a solid background covering the entire region to hide the 3D scene
    if is_dedicated:
        _draw_filled_rect(0, 0, vm.region_width, vm.region_height, (0.16, 0.16, 0.16, 1.0))

    # Draw canvas background
    draw_canvas_background(vm, tab.canvas_width, tab.canvas_height, tab.name)

    # Determine which bones are currently selected
    armature_obj = None
    if picker.armature_name:
        armature_obj = context.scene.objects.get(picker.armature_name)
    selected_bones = set()
    if armature_obj:
        selected_bones = set(get_selected_bone_names(armature_obj))

    # Draw each button
    for i, btn in enumerate(tab.buttons):
        bone_list = btn.get_bone_list()
        is_selected = bool(bone_list and all(b in selected_bones for b in bone_list))
        is_hovered = (i == getattr(draw_picker_callback, '_hovered_index', -1))
        is_edit_selected = (
            picker.edit_mode and (btn.selected or i == tab.active_button_index)
        )
        draw_button(btn, vm, hovered=is_hovered, selected=is_selected)
        if is_edit_selected:
            draw_edit_selection(btn, vm)

    # Draw marquee selection box in Edit Mode
    if picker.edit_mode:
        from .animate_handler import PICKER_OT_interact
        if getattr(PICKER_OT_interact, '_box_select_active', False):
            x1 = PICKER_OT_interact._box_select_start_mx
            y1 = PICKER_OT_interact._box_select_start_my
            x2 = PICKER_OT_interact._box_select_current_mx
            y2 = PICKER_OT_interact._box_select_current_my
            
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            w = max_x - min_x
            h = max_y - min_y
            
            # Explicitly re-enable alpha blending to overwrite font rendering side-effects
            gpu.state.blend_set('ALPHA')
            
            _draw_filled_rect(min_x, min_y, w, h, (0.2, 0.6, 1.0, 0.15))
            _draw_border_rect(min_x, min_y, w, h, (0.2, 0.6, 1.0, 0.85), line_width=1.5)

    gpu.state.blend_set('NONE')


# Storage for transient state used by the draw callback
draw_picker_callback._hovered_index = -1
