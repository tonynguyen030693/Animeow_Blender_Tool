"""
ui.py - Animeow Anim Linker
===========================
Thiết kế giao diện Panel cho Addon, hiển thị ở Sidebar (N Panel) 
phía bên phải 3D Viewport dưới tab "Animeow".
"""

import bpy

class ANIMEOW_PT_anim_linker_panel(bpy.types.Panel):
    """Panel giao diện chính cho Animeow Anim Linker"""
    bl_label = "😸 Animeow Anim Linker"
    bl_idname = "ANIMEOW_PT_anim_linker_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animeow'  # Tab hiển thị ở Sidebar (N-panel)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # --- SECTION 1: TARGET DEFINITION ---
        box = layout.box()
        box.label(text="🎯 Thiết lập Target", icon='CONSTRAINT_BONE')
        
        # Nút lấy xương đang chọn nhanh
        box.operator("animeow.get_active_bone", icon='EYEDROPPER')
        
        col = box.column(align=True)
        col.prop(scene, "animeow_target_object", text="Target Object")
        
        # Chỉ hiện Target Bone nếu Target Object là Armature
        target_obj = scene.animeow_target_object
        if target_obj and target_obj.type == 'ARMATURE':
            col.prop(scene, "animeow_target_bone", text="Target Bone")
        
        # --- SECTION 2: QUICK LINK ---
        box_link = layout.box()
        box_link.label(text="🔗 Gán Ràng Buộc Nhanh", icon='LINKED')
        
        box_link.prop(scene, "animeow_use_locator")
        
        # Nút tạo constraint
        box_link.operator("animeow.quick_link", text="Link Object to Bone", icon='ADD')
        
        # --- SECTION 3: SPACE SWITCHER ---
        box_switch = layout.box()
        box_switch.label(text="🔄 Chuyển Đổi Không Gian", icon='FILE_REFRESH')
        
        # Thông tin hướng dẫn nhỏ
        box_switch.label(text="Chọn Object -> Set Target mới -> Click:", icon='INFO')
        box_switch.operator("animeow.switch_parent", text="Switch Parent", icon='FILE_REFRESH')
        
        # --- SECTION 4: BAKE ANIMATION ---
        box_bake = layout.box()
        box_bake.label(text="🔥 Khóa Keyframe (Bake Animation)", icon='REC')
        
        box_bake.prop(scene, "animeow_clear_parents")
        
        # Nút Bake
        box_bake.operator("animeow.quick_bake", text="Bake & Clean Constraint", icon='NONE')
