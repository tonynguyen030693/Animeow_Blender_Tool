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
            box.label("Sao Chép Chuyển Động", icon='COPYDOWN')

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
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            box = layout.box()
            box.alert = True
            box.label(text="Loi ve UI (UI Draw Error):", icon='ERROR')
            for line in tb.split("\n")[:5]:
                if line.strip():
                    box.label(text=line[:50], icon='NONE')

