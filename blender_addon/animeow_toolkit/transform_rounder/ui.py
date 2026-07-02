"""
ui.py — Animeow Toolkit / Transform Rounder
==============================================
Panel giao diện cho module Transform Rounder, kế thừa AnimeowBasePanel.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel


class ANIMEOW_PT_transform_rounder(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Transform Rounder"""
    bl_label = "🔢 Transform Rounder"
    bl_idname = "ANIMEOW_PT_transform_rounder"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "animeow_active_tab"):
            return True
        return context.scene.animeow_active_tab == 'ROUNDER'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.prop(scene, "animeow_round_decimals", text="Chữ số thập phân")
        
        col.separator()
        col.label(text="Mục tiêu làm tròn:")
        row = col.row(align=True)
        row.prop(scene, "animeow_round_location", text="Loc", toggle=True)
        row.prop(scene, "animeow_round_rotation", text="Rot", toggle=True)
        row.prop(scene, "animeow_round_scale", text="Scale", toggle=True)

        col.separator()
        col.operator("animeow.round_transforms", text="Làm tròn đối tượng chọn", icon='FILE_REFRESH')
