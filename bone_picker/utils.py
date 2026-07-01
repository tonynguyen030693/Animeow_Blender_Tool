# ─────────────────────────────────────────────────────────────
# BonePicker – Utility helpers
# ─────────────────────────────────────────────────────────────
import math
import bpy


# ── Armature helpers ────────────────────────────────────────

def get_active_armature(context):
    """Return the active armature object, or None."""
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj
    # Fallback: look for the first selected armature
    for obj in context.selected_objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def get_pose_bone_names(armature_obj):
    """Return a sorted list of pose-bone names."""
    if armature_obj is None or armature_obj.pose is None:
        return []
    return sorted(pb.name for pb in armature_obj.pose.bones)


def select_bones_by_names(armature_obj, bone_names, mode='REPLACE'):
    """
    Select pose-bones on *armature_obj* whose names appear in *bone_names*.

    mode:
        REPLACE – clear selection first, then select targets
        ADD     – add targets to current selection
        REMOVE  – deselect targets
        INVERT  – toggle targets
    """
    if armature_obj is None or armature_obj.pose is None:
        return

    # Ensure pose-mode and the armature is active
    if bpy.context.view_layer.objects.active != armature_obj:
        bpy.context.view_layer.objects.active = armature_obj
    if armature_obj.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    if mode == 'REPLACE':
        bpy.ops.pose.select_all(action='DESELECT')

    for name in bone_names:
        pb = armature_obj.pose.bones.get(name)
        if pb is None:
            continue
        
        # Support Blender 4.0+ (PoseBone.select) and older (Bone.select)
        if hasattr(pb, "select"):
            if mode == 'REMOVE':
                pb.select = False
            elif mode == 'INVERT':
                pb.select = not pb.select
            else:  # REPLACE / ADD
                pb.select = True
        else:
            bone = armature_obj.data.bones.get(name)
            if bone is None:
                continue
            if mode == 'REMOVE':
                bone.select = False
            elif mode == 'INVERT':
                bone.select = not bone.select
            else:  # REPLACE / ADD
                bone.select = True

    # Set the last bone as active
    for name in reversed(bone_names):
        bone = armature_obj.data.bones.get(name)
        if bone:
            armature_obj.data.bones.active = bone
            break


def get_selected_bone_names(armature_obj):
    """Return a list of currently selected pose-bone names."""
    if armature_obj is None or armature_obj.pose is None:
        return []
    
    selected = []
    for pb in armature_obj.pose.bones:
        # Support Blender 4.0+ (PoseBone.select) and older (Bone.select)
        if hasattr(pb, "select"):
            if pb.select:
                selected.append(pb.name)
        else:
            bone = armature_obj.data.bones.get(pb.name)
            if bone and bone.select:
                selected.append(pb.name)
    return selected


# ── Hit-testing ─────────────────────────────────────────────

def point_in_rect(px, py, x, y, w, h):
    """Return True if (px, py) is inside the rectangle (x, y, w, h)."""
    return x <= px <= x + w and y <= py <= y + h


def point_in_ellipse(px, py, cx, cy, rx, ry):
    """Return True if (px, py) is inside the ellipse centered at (cx, cy)."""
    if rx <= 0 or ry <= 0:
        return False
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0


def point_in_rounded_rect(px, py, x, y, w, h, r):
    """Return True if (px, py) is inside a rounded rectangle."""
    r = min(r, w / 2, h / 2)
    # Quick bounding-box reject
    if not point_in_rect(px, py, x, y, w, h):
        return False
    # Check corners
    corners = [
        (x + r, y + r),             # top-left
        (x + w - r, y + r),         # top-right
        (x + r, y + h - r),         # bottom-left
        (x + w - r, y + h - r),     # bottom-right
    ]
    for (cx, cy) in corners:
        dx = px - cx
        dy = py - cy
        # Only test if we are in the corner zone
        in_corner_x = (px < x + r or px > x + w - r)
        in_corner_y = (py < y + r or py > y + h - r)
        if in_corner_x and in_corner_y:
            if dx * dx + dy * dy > r * r:
                return False
    return True


def hit_test_button(px, py, btn):
    """Test whether point (px, py) hits a picker button."""
    x, y, w, h = btn.pos_x, btn.pos_y, btn.width, btn.height
    shape = btn.shape
    if shape == 'ROUND':
        cx = x + w / 2
        cy = y + h / 2
        return point_in_ellipse(px, py, cx, cy, w / 2, h / 2)
    elif shape == 'ROUNDED_RECT':
        return point_in_rounded_rect(px, py, x, y, w, h, btn.corner_radius)
    else:  # RECT
        return point_in_rect(px, py, x, y, w, h)


# ── Color helpers ───────────────────────────────────────────

def hex_to_rgba(hex_str, alpha=1.0):
    """Convert '#RRGGBB' to (r, g, b, a) floats in [0,1]."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return (r, g, b, alpha)
    return (0.5, 0.5, 0.5, alpha)


def rgba_to_hex(r, g, b, a=1.0):
    """Convert (r, g, b, a) floats to '#RRGGBB'."""
    return '#{:02X}{:02X}{:02X}'.format(
        int(r * 255), int(g * 255), int(b * 255))


# ── Geometry helpers for GPU drawing ────────────────────────

def generate_circle_vertices(cx, cy, rx, ry, segments=32):
    """Return a list of (x, y) tuples forming an ellipse."""
    verts = []
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        verts.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    return verts


def generate_rounded_rect_vertices(x, y, w, h, r, segments_per_corner=8):
    """Return a list of (x, y) tuples forming a rounded rectangle."""
    r = min(r, w / 2, h / 2)
    verts = []
    corners = [
        (x + w - r, y + r, -math.pi / 2, 0),          # top-right
        (x + w - r, y + h - r, 0, math.pi / 2),        # bottom-right
        (x + r, y + h - r, math.pi / 2, math.pi),      # bottom-left
        (x + r, y + r, math.pi, 3 * math.pi / 2),      # top-left
    ]
    for (cx, cy, a_start, a_end) in corners:
        for i in range(segments_per_corner + 1):
            t = i / segments_per_corner
            angle = a_start + t * (a_end - a_start)
            verts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return verts
