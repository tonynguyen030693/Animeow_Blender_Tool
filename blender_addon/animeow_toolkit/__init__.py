"""
__init__.py — Animeow Toolkit
===============================
Điều phối trung tâm (Registry Hub) cho cả bộ công cụ Animeow Toolkit.
Tự động import và đăng ký/huỷ đăng ký toàn bộ các module con
theo thứ tự an toàn thông qua lớp quản lý ToolkitModule.
"""

bl_info = {
    "name": "Animeow Toolkit",
    "author": "Antigravity Agent & Tony Meow",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Tab: Animeow",
    "description": "Bộ công cụ hoạt hình chuyên nghiệp (Anim Linker, Graph Toolboard, Bone Picker, Transform Rounder) thống nhất.",
    "category": "Animation",
}

import bpy
from .core.base_module import ToolkitModule

# Import các module con
from . import anim_linker
from . import graph_toolboard
from . import bone_picker
from . import transform_rounder
from . import anim_copy
from . import anim_bake
from . import anim_layers


class ANIMEOW_PT_tab_selector(bpy.types.Panel):
    """Thanh Tab Ngang chuyển đổi giữa các công cụ trong Animeow Toolkit"""
    bl_label = "😸 Animeow Toolkit"
    bl_idname = "ANIMEOW_PT_tab_selector"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animeow'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Vẽ thanh tab ngang dạng nút bấm liền kề
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop(scene, "animeow_active_tab", expand=True)


# Tạo thực thể ToolkitModule cho các module khai báo cấu trúc classes/properties tiêu chuẩn
modules = [
    # 1. Anim Linker
    ToolkitModule(
        name="Anim Linker",
        classes=anim_linker.classes,
        properties=anim_linker.properties
    ),
    # 2. Transform Rounder
    ToolkitModule(
        name="Transform Rounder",
        classes=transform_rounder.classes,
        properties=transform_rounder.properties
    ),
    # 3. Anim Copy
    ToolkitModule(
        name="Anim Copy",
        classes=anim_copy.classes,
        properties=anim_copy.properties
    ),
    # 4. Anim Bake
    ToolkitModule(
        name="Anim Bake",
        classes=anim_bake.classes,
        properties=anim_bake.properties
    ),
    # 5. Anim Layers
    ToolkitModule(
        name="Anim Layers",
        classes=anim_layers.classes,
        properties=anim_layers.properties
    )
]


def register():
    # 1. Đăng ký tab property trên Scene
    bpy.types.Scene.animeow_active_tab = bpy.props.EnumProperty(
        name="Active Tab",
        description="Chọn công cụ hoạt hình cần hiển thị",
        items=[
            ('LINKER', "Linker", "Công cụ liên kết locator", 'CONSTRAINT_BONE', 0),
            ('COPY', "Copy", "Sao chép/Dán keyframes", 'COPYDOWN', 1),
            ('ROUNDER', "Rounder", "Làm tròn toạ độ", 'FILE_REFRESH', 2),
            ('BAKER', "Baker", "Bake & tối ưu keyframe", 'REC', 3),
            ('LAYERS', "Layers", "Animation Layers kiểu Maya", 'NLA', 4),
            ('PICKER', "Picker", "Chọn xương trực quan", 'POSE_HLT', 5),
        ],
        default='LINKER'
    )

    # 2. Đăng ký Tab Selector Panel chính
    bpy.utils.register_class(ANIMEOW_PT_tab_selector)

    # 3. Đăng ký các module sử dụng ToolkitModule
    for mod in modules:
        mod.register()

    # 4. Đăng ký các module tự quản lý (Graph Toolboard và Bone Picker)
    graph_toolboard.module_register()
    bone_picker.module_register()

    print("[Animeow Toolkit] Registered successfully.")


def unregister():
    # 1. Huỷ đăng ký các module tự quản lý (ngược thứ tự)
    bone_picker.module_unregister()
    graph_toolboard.module_unregister()

    # 2. Huỷ đăng ký các module qua ToolkitModule (ngược thứ tự)
    for mod in reversed(modules):
        mod.unregister()

    # 3. Huỷ đăng ký Tab Selector Panel chính
    bpy.utils.unregister_class(ANIMEOW_PT_tab_selector)

    # 4. Huỷ đăng ký tab property trên Scene
    if hasattr(bpy.types.Scene, "animeow_active_tab"):
        del bpy.types.Scene.animeow_active_tab

    print("[Animeow Toolkit] Unregistered successfully.")


if __name__ == "__main__":
    register()
