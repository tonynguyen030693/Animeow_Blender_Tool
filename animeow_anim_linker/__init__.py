"""
__init__.py - Animeow Anim Linker
=================================
Đăng ký và khởi tạo addon Animeow Anim Linker trong Blender.
"""

bl_info = {
    "name": "Animeow Anim Linker",
    "author": "Antigravity Agent & Tony Meow",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Tab: Animeow",
    "description": "Hỗ trợ gán nhanh constraint Child Of, chuyển đổi tay cầm vật thể và Bake Action cho Animator.",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
from .operators import (
    ANIMEOW_OT_quick_link,
    ANIMEOW_OT_get_active_bone,
    ANIMEOW_OT_switch_parent,
    ANIMEOW_OT_quick_bake
)
from .ui import ANIMEOW_PT_anim_linker_panel

# Danh sách các class cần đăng ký với Blender
classes = (
    ANIMEOW_OT_quick_link,
    ANIMEOW_OT_get_active_bone,
    ANIMEOW_OT_switch_parent,
    ANIMEOW_OT_quick_bake,
    ANIMEOW_PT_anim_linker_panel,
)

def register():
    # 1. Đăng ký các class
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # 2. Định nghĩa các custom properties trên Scene
    bpy.types.Scene.animeow_target_object = bpy.props.PointerProperty(
        name="Target Object",
        type=bpy.types.Object,
        description="Đối tượng đích cần liên kết tới"
    )
    
    bpy.types.Scene.animeow_target_bone = bpy.props.StringProperty(
        name="Target Bone",
        description="Xương đích cần liên kết tới"
    )
    
    bpy.types.Scene.animeow_use_locator = bpy.props.BoolProperty(
        name="Sử dụng Smart Locator (Empty)",
        default=True,
        description="Tạo một Empty làm trung gian để giữ cho Transform của vật thể sạch sẽ (0,0,0)"
    )
    
    bpy.types.Scene.animeow_clear_parents = bpy.props.BoolProperty(
        name="Clear Parents",
        default=False,
        description="Gỡ bỏ liên kết cha-con (Empty) sau khi bake xong để đưa vật thể về World Space"
    )

def unregister():
    # 1. Hủy đăng ký các custom properties
    del bpy.types.Scene.animeow_target_object
    del bpy.types.Scene.animeow_target_bone
    del bpy.types.Scene.animeow_use_locator
    del bpy.types.Scene.animeow_clear_parents
    
    # 2. Hủy đăng ký các class
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
