# ─────────────────────────────────────────────────────────────
# BonePicker – UI Panels (Sidebar / N-Panel)
# ─────────────────────────────────────────────────────────────
import bpy

from .animate_handler import PICKER_OT_interact


# ═════════════════════════════════════════════════════════════
#  Tab list for UIList
# ═════════════════════════════════════════════════════════════

class PICKER_UL_tabs(bpy.types.UIList):
    """UI list for picker tabs."""
    bl_idname = "PICKER_UL_tabs"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon='FILE_FOLDER')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='FILE_FOLDER')


class PICKER_UL_buttons(bpy.types.UIList):
    """UI list for buttons within a tab."""
    bl_idname = "PICKER_UL_buttons"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "label", text="", emboss=False, icon='BONE_DATA')
            if item.bone_targets:
                row.label(text="", icon='CHECKMARK')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.label, icon='BONE_DATA')


# ═════════════════════════════════════════════════════════════
#  Main panel
# ═════════════════════════════════════════════════════════════

class PICKER_PT_main(bpy.types.Panel):
    """BonePicker – Main panel"""
    bl_label = "🦴 Bone Picker"
    bl_idname = "PICKER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Picker"

    def draw(self, context):
        layout = self.layout
        picker = context.scene.bone_picker

        # ── Mode toggle & Interact button ───────────────────
        row = layout.row(align=True)
        if picker.edit_mode:
            row.operator("picker.toggle_mode", text="🎨 Edit Mode", icon='GREASEPENCIL', depress=True)
        else:
            row.operator("picker.toggle_mode", text="🎬 Animate Mode", icon='ARMATURE_DATA', depress=True)

        # Start/Stop interactive picker
        if PICKER_OT_interact._is_running:
            row.operator("picker.interact", text="", icon='PAUSE', depress=True)
        else:
            row.operator("picker.interact", text="", icon='PLAY')

        row = layout.row(align=True)
        row.operator("picker.create_float_window", text="📺 Float Viewport", icon='WINDOW')

        # ── Armature selector ───────────────────────────────
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Armature:", icon='ARMATURE_DATA')
        row.prop_search(picker, "armature_name", context.scene, "objects", text="")

        # ── Zoom/Pan info ───────────────────────────────────
        row = box.row(align=True)
        row.label(text=f"Zoom: {picker.zoom:.1f}x")
        row.label(text="Scroll=Zoom  |  MMB=Pan")


# ═════════════════════════════════════════════════════════════
#  Tabs panel
# ═════════════════════════════════════════════════════════════

class PICKER_PT_tabs(bpy.types.Panel):
    """BonePicker – Tabs management"""
    bl_label = "Tabs"
    bl_idname = "PICKER_PT_tabs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Picker"
    bl_parent_id = "PICKER_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        picker = context.scene.bone_picker

        row = layout.row()
        row.template_list(
            "PICKER_UL_tabs", "",
            picker, "tabs",
            picker, "active_tab_index",
            rows=2,
        )
        col = row.column(align=True)
        col.operator("picker.add_tab", text="", icon='ADD')
        col.operator("picker.remove_tab", text="", icon='REMOVE')
        col.separator()
        col.operator("picker.rename_tab", text="", icon='GREASEPENCIL')


# ═════════════════════════════════════════════════════════════
#  Buttons panel (always visible, lists all buttons)
# ═════════════════════════════════════════════════════════════

class PICKER_PT_buttons(bpy.types.Panel):
    """BonePicker – Buttons list"""
    bl_label = "Buttons"
    bl_idname = "PICKER_PT_buttons"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Picker"
    bl_parent_id = "PICKER_PT_main"

    def draw(self, context):
        layout = self.layout
        picker = context.scene.bone_picker

        if not picker.tabs:
            layout.label(text="No tabs. Add a tab first.", icon='INFO')
            return

        tab = picker.tabs[picker.active_tab_index]

        row = layout.row()
        row.template_list(
            "PICKER_UL_buttons", "",
            tab, "buttons",
            tab, "active_button_index",
            rows=4,
        )
        col = row.column(align=True)
        col.operator("picker.add_button", text="", icon='ADD')
        col.operator("picker.delete_button", text="", icon='REMOVE')
        col.separator()
        col.operator("picker.duplicate_button", text="", icon='DUPLICATE')

        # Quick actions
        row = layout.row(align=True)
        row.operator("picker.assign_bones", icon='BONE_DATA')
        row = layout.row(align=True)
        row.operator("picker.auto_create_from_bones", icon='OUTLINER_OB_ARMATURE')


# ═════════════════════════════════════════════════════════════
#  Edit Tools panel (only in Edit Mode)
# ═════════════════════════════════════════════════════════════

class PICKER_PT_edit_tools(bpy.types.Panel):
    """BonePicker – Edit Tools (only visible in Edit Mode)"""
    bl_label = "Edit Tools"
    bl_idname = "PICKER_PT_edit_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Picker"
    bl_parent_id = "PICKER_PT_main"

    @classmethod
    def poll(cls, context):
        return context.scene.bone_picker.edit_mode

    def draw(self, context):
        layout = self.layout
        picker = context.scene.bone_picker

        if not picker.tabs:
            return
        tab = picker.tabs[picker.active_tab_index]
        selected_buttons = [b for b in tab.buttons if b.selected]

        # ── Alignment & Spacing ──────────────────────────────
        if len(selected_buttons) >= 2:
            box_align = layout.box()
            box_align.label(text="Alignment & Spacing", icon='ALIGN_JUSTIFY')
            
            col = box_align.column(align=True)
            row1 = col.row(align=True)
            row1.operator("picker.align_buttons", text="Center X", icon='ALIGN_CENTER').type = 'CENTER_X'
            row1.operator("picker.align_buttons", text="Middle Y", icon='ALIGN_MIDDLE').type = 'CENTER_Y'
            
            row2 = col.row(align=True)
            row2.active = len(selected_buttons) >= 3
            row2.operator("picker.distribute_buttons", text="Distribute Horiz", icon='ALIGN_JUSTIFY').type = 'HORIZONTAL'
            row2.operator("picker.distribute_buttons", text="Distribute Vert", icon='ALIGN_JUSTIFY').type = 'VERTICAL'
            
            if len(selected_buttons) < 3:
                row3 = col.row()
                row3.label(text="Select 3+ buttons to distribute", icon='INFO')

        idx = tab.active_button_index

        if idx < 0 or idx >= len(tab.buttons):
            if len(selected_buttons) < 2:
                layout.label(text="Select a button to edit", icon='INFO')
            return

        btn = tab.buttons[idx]

        # ── Button properties ───────────────────────────────
        box = layout.box()
        box.label(text="Button Properties", icon='PREFERENCES')

        col = box.column(align=True)
        col.prop(btn, "label")
        col.prop(btn, "shape")
        if btn.shape == 'ROUNDED_RECT':
            col.prop(btn, "corner_radius")

        # Position & Size
        box2 = box.box()
        box2.label(text="Position & Size", icon='FULLSCREEN_ENTER')
        row = box2.row(align=True)
        row.prop(btn, "pos_x", text="X")
        row.prop(btn, "pos_y", text="Y")
        row = box2.row(align=True)
        row.prop(btn, "width")
        row.prop(btn, "height")

        # ── Colors ──────────────────────────────────────────
        box3 = box.box()
        box3.label(text="Colors", icon='COLOR')
        col = box3.column(align=True)
        col.prop(btn, "color_normal")
        col.prop(btn, "color_hover")
        col.prop(btn, "color_selected")
        col.prop(btn, "border_color")
        col.prop(btn, "text_color")

        # Quick color presets
        box4 = box.box()
        box4.label(text="Color Presets", icon='PRESET')
        grid = box4.grid_flow(columns=4, align=True)
        for preset in ['RED', 'BLUE', 'YELLOW', 'GREEN', 'PURPLE', 'ORANGE', 'GRAY']:
            op = grid.operator("picker.set_button_color", text=preset.capitalize())
            op.preset = preset

        # ── Bone assignment info ────────────────────────────
        box5 = box.box()
        box5.label(text="Bone Assignment", icon='BONE_DATA')
        if btn.bone_targets:
            for bone_name in btn.get_bone_list():
                row = box5.row()
                row.label(text=bone_name, icon='BONE_DATA')
        else:
            box5.label(text="No bones assigned", icon='ERROR')
        box5.prop(btn, "armature_name", text="Armature")

        # Danger zone
        layout.separator()
        row = layout.row()
        row.alert = True
        row.operator("picker.clear_all_buttons", icon='TRASH')


# ═════════════════════════════════════════════════════════════
#  Import/Export panel
# ═════════════════════════════════════════════════════════════

class PICKER_PT_io(bpy.types.Panel):
    """BonePicker – Import/Export"""
    bl_label = "Import / Export"
    bl_idname = "PICKER_PT_io"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Picker"
    bl_parent_id = "PICKER_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("picker.export_json", icon='EXPORT', text="Export Active Tab")
        col.operator("picker.export_all_json", icon='EXPORT', text="Export All Tabs")
        col.separator()
        col.operator("picker.import_json", icon='IMPORT', text="Import Picker")


# ═════════════════════════════════════════════════════════════
#  Registration
# ═════════════════════════════════════════════════════════════

classes = (
    PICKER_UL_tabs,
    PICKER_UL_buttons,
    PICKER_PT_main,
    PICKER_PT_tabs,
    PICKER_PT_buttons,
    PICKER_PT_edit_tools,
    PICKER_PT_io,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
