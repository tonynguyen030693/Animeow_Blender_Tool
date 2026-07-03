# ─────────────────────────────────────────────────────────────
# BonePicker – Operators (Edit Mode + General)
# ─────────────────────────────────────────────────────────────
import bpy
from bpy.props import (
    EnumProperty, FloatProperty, FloatVectorProperty,
    IntProperty, StringProperty,
)

from .utils import get_active_armature, get_selected_bone_names


# ═════════════════════════════════════════════════════════════
#  Tab management
# ═════════════════════════════════════════════════════════════

class PICKER_OT_add_tab(bpy.types.Operator):
    """Add a new picker tab"""
    bl_idname = "picker.add_tab"
    bl_label = "Add Tab"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        tab = picker.tabs.add()
        tab.name = f"Tab {len(picker.tabs)}"
        picker.active_tab_index = len(picker.tabs) - 1
        return {'FINISHED'}


class PICKER_OT_remove_tab(bpy.types.Operator):
    """Remove the active picker tab"""
    bl_idname = "picker.remove_tab"
    bl_label = "Remove Tab"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            return {'CANCELLED'}
        idx = picker.active_tab_index
        picker.tabs.remove(idx)
        picker.active_tab_index = max(0, min(idx, len(picker.tabs) - 1))
        return {'FINISHED'}


class PICKER_OT_rename_tab(bpy.types.Operator):
    """Rename the active picker tab"""
    bl_idname = "picker.rename_tab"
    bl_label = "Rename Tab"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: StringProperty(name="New Name", default="Untitled")

    def invoke(self, context, event):
        picker = context.scene.bone_picker
        if picker.tabs:
            self.new_name = picker.tabs[picker.active_tab_index].name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        picker = context.scene.bone_picker
        if picker.tabs:
            picker.tabs[picker.active_tab_index].name = self.new_name
        return {'FINISHED'}


# ═════════════════════════════════════════════════════════════
#  Button management
# ═════════════════════════════════════════════════════════════

class PICKER_OT_add_button(bpy.types.Operator):
    """Add a new button to the active picker tab"""
    bl_idname = "picker.add_button"
    bl_label = "Add Button"
    bl_options = {'REGISTER', 'UNDO'}

    pos_x: FloatProperty(name="X", default=50.0)
    pos_y: FloatProperty(name="Y", default=50.0)

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            # Auto-create a tab if none exists
            tab = picker.tabs.add()
            tab.name = "Tab 1"
            picker.active_tab_index = 0

        tab = picker.tabs[picker.active_tab_index]
        btn = tab.buttons.add()
        btn.pos_x = self.pos_x
        btn.pos_y = self.pos_y
        btn.label = f"Btn {len(tab.buttons)}"

        # Auto-assign armature if one is active
        arm = get_active_armature(context)
        if arm:
            btn.armature_name = arm.name
            picker.armature_name = arm.name

        tab.active_button_index = len(tab.buttons) - 1
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_delete_button(bpy.types.Operator):
    """Delete the selected button(s)"""
    bl_idname = "picker.delete_button"
    bl_label = "Delete Button"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            return {'CANCELLED'}
        tab = picker.tabs[picker.active_tab_index]
        
        # Get indices of buttons to delete (either selected or active)
        selected_indices = [i for i, b in enumerate(tab.buttons) if b.selected]
        if not selected_indices and (0 <= tab.active_button_index < len(tab.buttons)):
            selected_indices = [tab.active_button_index]
            
        if not selected_indices:
            return {'CANCELLED'}
            
        # Delete from end to start to preserve indices
        for idx in reversed(selected_indices):
            tab.buttons.remove(idx)
            
        # Set active button index to the last remaining button or -1
        if tab.buttons:
            tab.active_button_index = len(tab.buttons) - 1
        else:
            tab.active_button_index = -1
            
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_duplicate_button(bpy.types.Operator):
    """Duplicate the selected button(s)"""
    bl_idname = "picker.duplicate_button"
    bl_label = "Duplicate Button"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            return {'CANCELLED'}
        tab = picker.tabs[picker.active_tab_index]

        selected_buttons = [b for b in tab.buttons if b.selected]
        if not selected_buttons and (0 <= tab.active_button_index < len(tab.buttons)):
            selected_buttons = [tab.buttons[tab.active_button_index]]

        if not selected_buttons:
            return {'CANCELLED'}

        # Deselect old selection to highlight the duplicates
        for b in tab.buttons:
            b.selected = False

        for src in selected_buttons:
            new_btn = tab.buttons.add()

            # Copy all properties
            for prop_name in [
                'pos_x', 'pos_y', 'width', 'height',
                'shape', 'corner_radius',
                'label', 'bone_targets', 'armature_name',
            ]:
                setattr(new_btn, prop_name, getattr(src, prop_name))
            for color_prop in [
                'color_normal', 'color_hover', 'color_selected',
                'border_color', 'text_color',
            ]:
                src_val = getattr(src, color_prop)
                getattr(new_btn, color_prop)[0] = src_val[0]
                getattr(new_btn, color_prop)[1] = src_val[1]
                getattr(new_btn, color_prop)[2] = src_val[2]
                getattr(new_btn, color_prop)[3] = src_val[3]

            # Offset the duplicate slightly and select it
            new_btn.pos_x += 20
            new_btn.pos_y += 20
            new_btn.label = src.label + " (copy)"
            new_btn.selected = True

        tab.active_button_index = len(tab.buttons) - 1
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_assign_bones(bpy.types.Operator):
    """Assign currently selected pose bones to the active button"""
    bl_idname = "picker.assign_bones"
    bl_label = "Assign Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            self.report({'WARNING'}, "No picker tab exists")
            return {'CANCELLED'}
        tab = picker.tabs[picker.active_tab_index]
        idx = tab.active_button_index
        if idx < 0 or idx >= len(tab.buttons):
            self.report({'WARNING'}, "No button selected in Edit Mode")
            return {'CANCELLED'}

        arm = get_active_armature(context)
        if arm is None:
            self.report({'WARNING'}, "No armature active")
            return {'CANCELLED'}

        bone_names = get_selected_bone_names(arm)
        if not bone_names:
            self.report({'WARNING'}, "No bones selected in Pose Mode")
            return {'CANCELLED'}

        btn = tab.buttons[idx]
        btn.set_bone_list(bone_names)
        btn.armature_name = arm.name
        picker.armature_name = arm.name

        # Auto-set label to first bone name if label is default
        if btn.label.startswith("Btn ") or btn.label == "Button":
            if len(bone_names) == 1:
                btn.label = bone_names[0]
            else:
                btn.label = f"{bone_names[0]} +{len(bone_names)-1}"

        self.report({'INFO'}, f"Assigned {len(bone_names)} bone(s)")
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_toggle_mode(bpy.types.Operator):
    """Toggle between Edit Mode and Animate Mode"""
    bl_idname = "picker.toggle_mode"
    bl_label = "Toggle Picker Mode"

    def execute(self, context):
        picker = context.scene.bone_picker
        picker.edit_mode = not picker.edit_mode
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_set_button_color(bpy.types.Operator):
    """Quick color preset for a button"""
    bl_idname = "picker.set_button_color"
    bl_label = "Set Button Color"
    bl_options = {'REGISTER', 'UNDO'}

    preset: EnumProperty(
        name="Color Preset",
        items=[
            ('RED', "Red (Left)", "Red for left side"),
            ('BLUE', "Blue (Right)", "Blue for right side"),
            ('YELLOW', "Yellow (Center)", "Yellow for center"),
            ('GREEN', "Green", "Green"),
            ('PURPLE', "Purple", "Purple"),
            ('ORANGE', "Orange", "Orange"),
            ('GRAY', "Gray (Default)", "Default gray"),
        ],
        default='GRAY',
    )

    COLOR_MAP = {
        'RED':    ((0.75, 0.20, 0.20, 1.0), (0.90, 0.30, 0.30, 1.0)),
        'BLUE':   ((0.20, 0.35, 0.75, 1.0), (0.30, 0.45, 0.90, 1.0)),
        'YELLOW': ((0.75, 0.65, 0.15, 1.0), (0.90, 0.80, 0.20, 1.0)),
        'GREEN':  ((0.20, 0.60, 0.30, 1.0), (0.30, 0.75, 0.40, 1.0)),
        'PURPLE': ((0.55, 0.25, 0.70, 1.0), (0.70, 0.35, 0.85, 1.0)),
        'ORANGE': ((0.80, 0.45, 0.15, 1.0), (0.95, 0.55, 0.20, 1.0)),
        'GRAY':   ((0.35, 0.35, 0.35, 1.0), (0.50, 0.50, 0.50, 1.0)),
    }

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            return {'CANCELLED'}
        tab = picker.tabs[picker.active_tab_index]
        idx = tab.active_button_index
        if idx < 0 or idx >= len(tab.buttons):
            return {'CANCELLED'}

        btn = tab.buttons[idx]
        normal, hover = self.COLOR_MAP[self.preset]
        for i in range(4):
            btn.color_normal[i] = normal[i]
            btn.color_hover[i] = hover[i]

        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_auto_create_from_bones(bpy.types.Operator):
    """Auto-create buttons for all bones in the active armature"""
    bl_idname = "picker.auto_create_from_bones"
    bl_label = "Auto-Create from Bones"
    bl_description = "Create one button per selected bone in the active armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picker = context.scene.bone_picker
        arm = get_active_armature(context)
        if arm is None:
            self.report({'WARNING'}, "No armature active")
            return {'CANCELLED'}

        bone_names = get_selected_bone_names(arm)
        if not bone_names:
            self.report({'WARNING'}, "Select bones in Pose Mode first")
            return {'CANCELLED'}

        # Ensure a tab exists
        if not picker.tabs:
            tab = picker.tabs.add()
            tab.name = arm.name
            picker.active_tab_index = 0
        tab = picker.tabs[picker.active_tab_index]

        # Layout bones in a grid
        cols = 4
        cell_w = 100
        cell_h = 35
        margin = 10

        for i, bone_name in enumerate(bone_names):
            row = i // cols
            col = i % cols
            btn = tab.buttons.add()
            btn.pos_x = margin + col * (cell_w + margin)
            btn.pos_y = margin + row * (cell_h + margin)
            btn.width = cell_w
            btn.height = cell_h
            btn.label = bone_name
            btn.bone_targets = bone_name
            btn.armature_name = arm.name

            # Color left/right heuristic
            lower_name = bone_name.lower()
            if lower_name.endswith('.l') or '_l_' in lower_name or lower_name.startswith('l_'):
                for j in range(4):
                    btn.color_normal[j] = (0.75, 0.20, 0.20, 1.0)[j]
                    btn.color_hover[j] = (0.90, 0.30, 0.30, 1.0)[j]
            elif lower_name.endswith('.r') or '_r_' in lower_name or lower_name.startswith('r_'):
                for j in range(4):
                    btn.color_normal[j] = (0.20, 0.35, 0.75, 1.0)[j]
                    btn.color_hover[j] = (0.30, 0.45, 0.90, 1.0)[j]

        picker.armature_name = arm.name
        tab.active_button_index = len(tab.buttons) - 1
        self.report({'INFO'}, f"Created {len(bone_names)} buttons")
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_clear_all_buttons(bpy.types.Operator):
    """Remove all buttons from the active tab"""
    bl_idname = "picker.clear_all_buttons"
    bl_label = "Clear All Buttons"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            return {'CANCELLED'}
        tab = picker.tabs[picker.active_tab_index]
        tab.buttons.clear()
        tab.active_button_index = -1
        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_create_float_window(bpy.types.Operator):
    """Create a dedicated floating viewport window for the Bone Picker"""
    bl_idname = "picker.create_float_window"
    bl_label = "Float Viewport"
    bl_description = "Duplicate the viewport into a new floating window and configure it for the Bone Picker"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (
            context.area and
            context.area.type == 'VIEW_3D' and
            hasattr(context.scene, 'bone_picker')
        )

    def execute(self, context):
        # Track existing windows
        old_windows = set(bpy.context.window_manager.windows)

        # 1. Stop any currently running interact modal operator instance
        from .animate_handler import PICKER_OT_interact
        if PICKER_OT_interact._is_running:
            if PICKER_OT_interact._draw_handler:
                try:
                    bpy.types.SpaceView3D.draw_handler_remove(
                        PICKER_OT_interact._draw_handler, 'WINDOW')
                except Exception:
                    pass
                PICKER_OT_interact._draw_handler = None
            PICKER_OT_interact._is_running = False

        # 2. Duplicate the active 3D Viewport area into a new window
        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')

        # 3. Use a timer to wait for the window/screen areas to be created/populated
        def configure_window():
            current_windows = set(bpy.context.window_manager.windows)
            new_windows = current_windows - old_windows
            if not new_windows:
                return 0.05
            
            win = list(new_windows)[0]
            if not win.screen or not win.screen.areas:
                return 0.05
            
            target_area = None
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    target_area = area
                    break
            
            if not target_area:
                target_area = win.screen.areas[-1]
                target_area.type = 'VIEW_3D'
                
            if target_area:
                print(f"[BonePicker] Found target area in new window: {target_area}")
                for space in target_area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_overlays = False
                        space.show_region_toolbar = False
                        space.show_region_ui = False
                        space.show_region_header = False
                        space.show_gizmo = False
                        print("[BonePicker] Configured SpaceView3D: overlays=False, toolbar=False, UI=False, header=False, gizmo=False")
                
                target_area.tag_redraw()
                
                with bpy.context.temp_override(window=win, area=target_area):
                    bpy.ops.picker.interact('INVOKE_DEFAULT')
            else:
                print("[BonePicker] No target area found in new window.")
            
            return None

        # Start the timer to configure the new window
        bpy.app.timers.register(configure_window, first_interval=0.1)

        return {'FINISHED'}


class PICKER_OT_align_buttons(bpy.types.Operator):
    """Align selected picker buttons"""
    bl_idname = "picker.align_buttons"
    bl_label = "Align Buttons"
    bl_options = {'REGISTER', 'UNDO'}

    type: EnumProperty(
        name="Alignment Type",
        items=[
            ('LEFT', "Left", "Align left edges"),
            ('CENTER_X', "Center X", "Align horizontal centers"),
            ('RIGHT', "Right", "Align right edges"),
            ('TOP', "Top", "Align top edges"),
            ('CENTER_Y', "Center Y", "Align vertical centers"),
            ('BOTTOM', "Bottom", "Align bottom edges"),
        ],
        default='LEFT',
    )

    @classmethod
    def poll(cls, context):
        picker = getattr(context.scene, "bone_picker", None)
        if not picker or not picker.tabs:
            return False
        tab = picker.tabs[picker.active_tab_index]
        selected_count = sum(1 for b in tab.buttons if b.selected)
        return selected_count >= 2

    def execute(self, context):
        picker = context.scene.bone_picker
        tab = picker.tabs[picker.active_tab_index]
        selected_buttons = [b for b in tab.buttons if b.selected]

        if len(selected_buttons) < 2:
            self.report({'WARNING'}, "Select at least 2 buttons to align")
            return {'CANCELLED'}

        if self.type == 'LEFT':
            min_x = min(b.pos_x for b in selected_buttons)
            for b in selected_buttons:
                b.pos_x = min_x
        elif self.type == 'CENTER_X':
            avg_center_x = sum(b.pos_x + b.width / 2.0 for b in selected_buttons) / len(selected_buttons)
            for b in selected_buttons:
                b.pos_x = avg_center_x - b.width / 2.0
        elif self.type == 'RIGHT':
            max_right = max(b.pos_x + b.width for b in selected_buttons)
            for b in selected_buttons:
                b.pos_x = max_right - b.width
        elif self.type == 'TOP':
            max_top = max(b.pos_y + b.height for b in selected_buttons)
            for b in selected_buttons:
                b.pos_y = max_top - b.height
        elif self.type == 'CENTER_Y':
            avg_center_y = sum(b.pos_y + b.height / 2.0 for b in selected_buttons) / len(selected_buttons)
            for b in selected_buttons:
                b.pos_y = avg_center_y - b.height / 2.0
        elif self.type == 'BOTTOM':
            min_y = min(b.pos_y for b in selected_buttons)
            for b in selected_buttons:
                b.pos_y = min_y

        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_distribute_buttons(bpy.types.Operator):
    """Distribute selected picker buttons evenly"""
    bl_idname = "picker.distribute_buttons"
    bl_label = "Distribute Buttons"
    bl_options = {'REGISTER', 'UNDO'}

    type: EnumProperty(
        name="Distribution Type",
        items=[
            ('HORIZONTAL', "Horizontal", "Distribute horizontally"),
            ('VERTICAL', "Vertical", "Distribute vertically"),
        ],
        default='HORIZONTAL',
    )

    @classmethod
    def poll(cls, context):
        picker = getattr(context.scene, "bone_picker", None)
        if not picker or not picker.tabs:
            return False
        tab = picker.tabs[picker.active_tab_index]
        selected_count = sum(1 for b in tab.buttons if b.selected)
        return selected_count >= 3

    def execute(self, context):
        picker = context.scene.bone_picker
        tab = picker.tabs[picker.active_tab_index]
        selected_buttons = [b for b in tab.buttons if b.selected]

        n = len(selected_buttons)
        if n < 3:
            self.report({'WARNING'}, "Select at least 3 buttons to distribute")
            return {'CANCELLED'}

        if self.type == 'HORIZONTAL':
            sorted_buttons = sorted(selected_buttons, key=lambda b: b.pos_x + b.width / 2.0)
            b_first = sorted_buttons[0]
            b_last = sorted_buttons[-1]
            
            total_span = (b_last.pos_x + b_last.width) - b_first.pos_x
            sum_widths = sum(b.width for b in sorted_buttons)
            total_spacing = total_span - sum_widths
            
            if total_spacing > 0:
                gap = total_spacing / (n - 1)
                for i in range(1, n - 1):
                    sorted_buttons[i].pos_x = sorted_buttons[i-1].pos_x + sorted_buttons[i-1].width + gap
            else:
                center_first = b_first.pos_x + b_first.width / 2.0
                center_last = b_last.pos_x + b_last.width / 2.0
                step = (center_last - center_first) / (n - 1)
                for i in range(1, n - 1):
                    target_center = center_first + i * step
                    sorted_buttons[i].pos_x = target_center - sorted_buttons[i].width / 2.0

        elif self.type == 'VERTICAL':
            sorted_buttons = sorted(selected_buttons, key=lambda b: b.pos_y + b.height / 2.0)
            b_first = sorted_buttons[0]
            b_last = sorted_buttons[-1]
            
            total_span = (b_last.pos_y + b_last.height) - b_first.pos_y
            sum_heights = sum(b.height for b in sorted_buttons)
            total_spacing = total_span - sum_heights
            
            if total_spacing > 0:
                gap = total_spacing / (n - 1)
                for i in range(1, n - 1):
                    sorted_buttons[i].pos_y = sorted_buttons[i-1].pos_y + sorted_buttons[i-1].height + gap
            else:
                center_first = b_first.pos_y + b_first.height / 2.0
                center_last = b_last.pos_y + b_last.height / 2.0
                step = (center_last - center_first) / (n - 1)
                for i in range(1, n - 1):
                    target_center = center_first + i * step
                    sorted_buttons[i].pos_y = target_center - sorted_buttons[i].height / 2.0

        context.area.tag_redraw()
        return {'FINISHED'}


class PICKER_OT_mirror_buttons(bpy.types.Operator):
    """Mirror selected buttons across the canvas center X-axis with automatic L/R name swapping"""
    bl_idname = "picker.mirror_buttons"
    bl_label = "Mirror Selected"
    bl_description = "Duplicate selected buttons mirrored across the canvas center, swapping .L/.R bone names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        picker = getattr(context.scene, "bone_picker", None)
        if not picker or not picker.tabs:
            return False
        tab = picker.tabs[picker.active_tab_index]
        return any(b.selected for b in tab.buttons)

    @staticmethod
    def _swap_lr(name):
        """Swap .L/.R, .l/.r, _L/_R, _l/_r suffixes in a bone name."""
        import re
        # Patterns: .L <-> .R, .l <-> .r, _L <-> _R, _l <-> _r
        swaps = [
            (r'\.L$', '.R'), (r'\.R$', '.L'),
            (r'\.l$', '.r'), (r'\.r$', '.l'),
            (r'_L$', '_R'), (r'_R$', '_L'),
            (r'_l$', '_r'), (r'_r$', '_l'),
            (r'\.L\.', '.R.'), (r'\.R\.', '.L.'),
            (r'_L_', '_R_'), (r'_R_', '_L_'),
        ]
        for pattern, replacement in swaps:
            new_name = re.sub(pattern, replacement, name)
            if new_name != name:
                return new_name
        return name

    def execute(self, context):
        picker = context.scene.bone_picker
        tab = picker.tabs[picker.active_tab_index]
        selected_buttons = [b for b in tab.buttons if b.selected]

        if not selected_buttons:
            self.report({'WARNING'}, "No buttons selected to mirror")
            return {'CANCELLED'}

        canvas_center_x = tab.canvas_width / 2.0

        # Deselect old buttons
        for b in tab.buttons:
            b.selected = False

        for src in selected_buttons:
            new_btn = tab.buttons.add()

            # Copy all visual properties
            for prop_name in [
                'width', 'height', 'shape', 'corner_radius',
                'button_type', 'script_text',
            ]:
                setattr(new_btn, prop_name, getattr(src, prop_name))
            for color_prop in [
                'color_normal', 'color_hover', 'color_selected',
                'border_color', 'text_color',
            ]:
                src_val = getattr(src, color_prop)
                for i in range(4):
                    getattr(new_btn, color_prop)[i] = src_val[i]

            # Mirror X position across canvas center
            src_center_x = src.pos_x + src.width / 2.0
            mirror_center_x = 2 * canvas_center_x - src_center_x
            new_btn.pos_x = mirror_center_x - src.width / 2.0
            new_btn.pos_y = src.pos_y

            # Swap L/R in bone names
            src_bones = src.get_bone_list()
            mirrored_bones = [self._swap_lr(n) for n in src_bones]
            new_btn.set_bone_list(mirrored_bones)

            # Swap L/R in label
            new_btn.label = self._swap_lr(src.label)

            # Copy armature reference
            new_btn.armature_name = src.armature_name

            # Select the new mirrored button
            new_btn.selected = True

        tab.active_button_index = len(tab.buttons) - 1
        self.report({'INFO'}, f"Mirrored {len(selected_buttons)} button(s)")
        context.area.tag_redraw()
        return {'FINISHED'}


# ═════════════════════════════════════════════════════════════
#  Registration
# ═════════════════════════════════════════════════════════════

classes = (
    PICKER_OT_add_tab,
    PICKER_OT_remove_tab,
    PICKER_OT_rename_tab,
    PICKER_OT_add_button,
    PICKER_OT_delete_button,
    PICKER_OT_duplicate_button,
    PICKER_OT_assign_bones,
    PICKER_OT_toggle_mode,
    PICKER_OT_set_button_color,
    PICKER_OT_auto_create_from_bones,
    PICKER_OT_clear_all_buttons,
    PICKER_OT_create_float_window,
    PICKER_OT_align_buttons,
    PICKER_OT_distribute_buttons,
    PICKER_OT_mirror_buttons,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
