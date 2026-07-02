"""
pie_menu.py — Animeow Toolkit
===============================
Định nghĩa và đăng ký Pie Menu phím tắt nhanh (Alt + Shift + A)
giúp animator gọi nhanh các lệnh Link, Bake, Switch Parent, và Copy/Paste.
"""

import bpy

class ANIMEOW_MT_pie_menu(bpy.types.Menu):
    """Pie Menu giúp gọi nhanh các tính năng cốt lõi của Animeow Toolkit"""
    bl_label = "😸 Animeow Anim Pie"
    bl_idname = "ANIMEOW_MT_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        # 1. Hướng Tây (Trái - West): Link Object
        pie.operator("animeow.quick_link", text="Link Object", icon='LINKED')
        
        # 2. Hướng Đông (Phải - East): Switch Parent
        pie.operator("animeow.switch_parent", text="Switch Parent", icon='FILE_REFRESH')
        
        # 3. Hướng Nam (Dưới - South): Bake & Clean
        pie.operator("animeow.quick_bake", text="Bake & Clean", icon='REC')
        
        # 4. Hướng Bắc (Trên - North): Menu Copy/Paste nhanh
        box = pie.box()
        col = box.column(align=True)
        col.label(text="Copy/Paste Animation", icon='COPYDOWN')
        col.separator()
        col.operator("animeow.copy_anim", text="Copy Anim", icon='COPYDOWN')
        col.operator("animeow.paste_anim", text="Paste Anim", icon='PASTEDOWN')
        col.operator("animeow.paste_connect", text="Paste Connect", icon='LINKED')


addon_keymaps = []

def register_keymap():
    """Đăng ký phím tắt Alt + Shift + A kích hoạt Pie Menu"""
    wm = bpy.context.window_manager
    if not wm:
        return
        
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', alt=True, shift=True)
        kmi.properties.name = "ANIMEOW_MT_pie_menu"
        addon_keymaps.append((km, kmi))


def unregister_keymap():
    """Huỷ đăng ký phím tắt Pie Menu"""
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()
