"""
ui.py — Animeow Toolkit / Anim Copy
======================================
Panel giao diện cho module Anim Copy & Paste, kế thừa AnimeowBasePanel.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel


class ANIMEOW_PT_copy_panel(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Anim Copy & Paste"""
    bl_label = "📋 Anim Copy & Paste"
    bl_idname = "ANIMEOW_PT_copy_panel"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "animeow_active_tab"):
            return True
        return context.scene.animeow_active_tab == 'COPY'

    def draw(self, context):
        layout = self.layout
        try:
            scene = context.scene

            box = layout.box()
            box.label(text="Sao Chép Chuyển Động", icon='COPYDOWN')

            # Cấu hình phạm vi Copy
            col_range = box.column(align=True)
            col_range.prop(scene, "animeow_copy_range_type", text="Phạm vi")
            if scene.animeow_copy_range_type == 'CUSTOM':
                row_frames = col_range.row(align=True)
                row_frames.prop(scene, "animeow_copy_frame_start", text="Từ")
                row_frames.prop(scene, "animeow_copy_frame_end", text="Đến")

            box.separator()
            # Nút Copy chính
            row_copy = box.row(align=True)
            row_copy.scale_y = 1.2
            row_copy.operator("animeow.copy_anim", text="Copy Anim", icon='COPYDOWN')

            col = box.column(align=True)
            col.separator()
            
            # Nút Paste dạng Grid xếp ngang gọn gàng
            row_paste = col.row(align=True)
            row_paste.scale_y = 1.2
            
            op_paste = row_paste.operator("animeow.paste_anim", text="Paste Normal", icon='PASTEDOWN')
            op_paste.mirror = scene.animeow_copy_mirror

            op_connect = row_paste.operator("animeow.paste_connect", text="Paste Connect", icon='LINKED')
            op_connect.mirror = scene.animeow_copy_mirror

            # Checkbox cấu hình Mirror lật đối xứng
            col.separator()
            col.prop(scene, "animeow_copy_mirror", text="Lật Đối Xứng (Mirror)")
            
            if scene.animeow_copy_mirror:
                box_axes = col.box()
                box_axes.label(text="Trục đối xứng:", icon='ORIENTATION_LOCAL')
                grid = box_axes.grid_flow(columns=3, align=True)
                grid.prop(scene, "animeow_mirror_tx", text="TX")
                grid.prop(scene, "animeow_mirror_ty", text="TY")
                grid.prop(scene, "animeow_mirror_tz", text="TZ")
                grid.prop(scene, "animeow_mirror_rx", text="RX")
                grid.prop(scene, "animeow_mirror_ry", text="RY")
                grid.prop(scene, "animeow_mirror_rz", text="RZ")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            box = layout.box()
            box.alert = True
            box.label(text="Loi ve UI (UI Draw Error):", icon='ERROR')
            for line in tb.split("\n")[:5]:
                if line.strip():
                    box.label(text=line[:50], icon='NONE')

