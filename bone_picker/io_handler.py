# ─────────────────────────────────────────────────────────────
# BonePicker – Import / Export JSON
# ─────────────────────────────────────────────────────────────
import json
import os

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper


# ── Export ──────────────────────────────────────────────────

class PICKER_OT_export_json(bpy.types.Operator, ExportHelper):
    """Export the active picker tab to a JSON file"""
    bl_idname = "picker.export_json"
    bl_label = "Export Picker"
    filename_ext = ".json"

    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            self.report({'WARNING'}, "No picker tab to export")
            return {'CANCELLED'}

        tab = picker.tabs[picker.active_tab_index]
        data = _tab_to_dict(tab)
        wrapper = {
            "version": [1, 0, 0],
            "armature_name": picker.armature_name,
            "tabs": [data],
        }

        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(wrapper, f, indent=2, ensure_ascii=False)

        self.report({'INFO'}, f"Exported to {self.filepath}")
        return {'FINISHED'}


class PICKER_OT_export_all_json(bpy.types.Operator, ExportHelper):
    """Export all picker tabs to a single JSON file"""
    bl_idname = "picker.export_all_json"
    bl_label = "Export All Tabs"
    filename_ext = ".json"

    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        picker = context.scene.bone_picker
        if not picker.tabs:
            self.report({'WARNING'}, "No picker tabs to export")
            return {'CANCELLED'}

        tabs_data = [_tab_to_dict(tab) for tab in picker.tabs]
        wrapper = {
            "version": [1, 0, 0],
            "armature_name": picker.armature_name,
            "tabs": tabs_data,
        }

        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(wrapper, f, indent=2, ensure_ascii=False)

        self.report({'INFO'}, f"Exported {len(tabs_data)} tab(s) to {self.filepath}")
        return {'FINISHED'}


# ── Import ──────────────────────────────────────────────────

class PICKER_OT_import_json(bpy.types.Operator, ImportHelper):
    """Import picker tab(s) from a JSON file"""
    bl_idname = "picker.import_json"
    bl_label = "Import Picker"
    filename_ext = ".json"

    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        if not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}

        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        picker = context.scene.bone_picker

        tabs_data = data.get('tabs', [])
        if not tabs_data:
            self.report({'WARNING'}, "No tabs found in the file")
            return {'CANCELLED'}

        arm_name = data.get('armature_name', '')
        if arm_name and not picker.armature_name:
            picker.armature_name = arm_name

        count = 0
        for tab_data in tabs_data:
            _dict_to_tab(picker, tab_data)
            count += 1

        picker.active_tab_index = len(picker.tabs) - 1
        context.area.tag_redraw()
        self.report({'INFO'}, f"Imported {count} tab(s) from {self.filepath}")
        return {'FINISHED'}


# ── Serialization helpers ───────────────────────────────────

def _tab_to_dict(tab):
    """Convert a PickerTabItem to a dictionary."""
    buttons = []
    for btn in tab.buttons:
        buttons.append({
            "label": btn.label,
            "pos_x": btn.pos_x,
            "pos_y": btn.pos_y,
            "width": btn.width,
            "height": btn.height,
            "shape": btn.shape,
            "corner_radius": btn.corner_radius,
            "color_normal": list(btn.color_normal),
            "color_hover": list(btn.color_hover),
            "color_selected": list(btn.color_selected),
            "border_color": list(btn.border_color),
            "text_color": list(btn.text_color),
            "bone_targets": btn.get_bone_list(),
            "armature_name": btn.armature_name,
        })

    return {
        "name": tab.name,
        "canvas_width": tab.canvas_width,
        "canvas_height": tab.canvas_height,
        "background_image": tab.background_image,
        "buttons": buttons,
    }


def _dict_to_tab(picker, tab_data):
    """Create a new PickerTabItem from a dictionary and add it to *picker*."""
    tab = picker.tabs.add()
    tab.name = tab_data.get('name', 'Imported')
    tab.canvas_width = tab_data.get('canvas_width', 600.0)
    tab.canvas_height = tab_data.get('canvas_height', 400.0)
    tab.background_image = tab_data.get('background_image', '')

    for btn_data in tab_data.get('buttons', []):
        btn = tab.buttons.add()
        btn.label = btn_data.get('label', 'Button')
        btn.pos_x = btn_data.get('pos_x', 0.0)
        btn.pos_y = btn_data.get('pos_y', 0.0)
        btn.width = btn_data.get('width', 80.0)
        btn.height = btn_data.get('height', 25.0)
        btn.shape = btn_data.get('shape', 'ROUNDED_RECT')
        btn.corner_radius = btn_data.get('corner_radius', 4.0)

        for color_prop in [
            'color_normal', 'color_hover', 'color_selected',
            'border_color', 'text_color',
        ]:
            vals = btn_data.get(color_prop)
            if vals and len(vals) >= 4:
                prop = getattr(btn, color_prop)
                for i in range(4):
                    prop[i] = vals[i]

        targets = btn_data.get('bone_targets', [])
        if isinstance(targets, list):
            btn.set_bone_list(targets)
        elif isinstance(targets, str):
            btn.bone_targets = targets
        btn.armature_name = btn_data.get('armature_name', '')


# ═════════════════════════════════════════════════════════════
#  Registration
# ═════════════════════════════════════════════════════════════

classes = (
    PICKER_OT_export_json,
    PICKER_OT_export_all_json,
    PICKER_OT_import_json,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
