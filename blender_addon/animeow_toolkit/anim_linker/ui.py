"""
ui.py — Animeow Toolkit / Anim Linker
=======================================
Panel giao diện cho module Anim Linker, kế thừa AnimeowBasePanel.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel


class ANIMEOW_PT_linker_panel(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Anim Linker"""
    bl_label = "🎯 Anim Linker"
    bl_idname = "ANIMEOW_PT_linker_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- SECTION 1: TARGET DEFINITION ---
        box = layout.box()
        box.label(text="Thiết lập Target", icon='CONSTRAINT_BONE')
        box.operator("animeow.get_active_bone", icon='EYEDROPPER')

        col = box.column(align=True)
        col.prop(scene, "animeow_target_object", text="Target Object")

        target_obj = scene.animeow_target_object
        if target_obj and target_obj.type == 'ARMATURE':
            col.prop(scene, "animeow_target_bone", text="Target Bone")

        # --- SECTION 2: QUICK LINK ---
        box_link = layout.box()
        box_link.label(text="Gán Ràng Buộc Nhanh", icon='LINKED')
        box_link.prop(scene, "animeow_use_locator")
        box_link.operator("animeow.quick_link", text="Link Object to Bone", icon='ADD')

        # --- SECTION 3: SPACE SWITCHER ---
        box_switch = layout.box()
        box_switch.label(text="Chuyển Đổi Không Gian", icon='FILE_REFRESH')
        box_switch.label(text="Chọn Object -> Set Target mới -> Click:", icon='INFO')
        box_switch.operator("animeow.switch_parent", text="Switch Parent", icon='FILE_REFRESH')

        # --- SECTION 4: BAKE ANIMATION ---
        box_bake = layout.box()
        box_bake.label(text="Khóa Keyframe (Bake Animation)", icon='REC')
        box_bake.prop(scene, "animeow_clear_parents")
        box_bake.operator("animeow.quick_bake", text="Bake & Clean Constraint", icon='NONE')
