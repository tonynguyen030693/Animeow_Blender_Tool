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
from .core.pie_menu import ANIMEOW_MT_pie_menu, register_keymap, unregister_keymap

# Import các module con
from . import anim_linker
from . import graph_toolboard
from . import bone_picker
from . import transform_rounder
from . import anim_copy

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
    )
]


def register():
    # 1. Đăng ký các module sử dụng ToolkitModule
    for mod in modules:
        mod.register()

    # 2. Đăng ký các module tự quản lý (Graph Toolboard và Bone Picker)
    graph_toolboard.module_register()
    bone_picker.module_register()

    # 3. Đăng ký Pie Menu và phím tắt
    bpy.utils.register_class(ANIMEOW_MT_pie_menu)
    register_keymap()

    print("[Animeow Toolkit] Registered successfully.")


def unregister():
    # 1. Huỷ đăng ký Pie Menu và phím tắt
    unregister_keymap()
    bpy.utils.unregister_class(ANIMEOW_MT_pie_menu)

    # 2. Huỷ đăng ký các module tự quản lý (ngược thứ tự)
    bone_picker.module_unregister()
    graph_toolboard.module_unregister()

    # 3. Huỷ đăng ký các module qua ToolkitModule (ngược thứ tự)
    for mod in reversed(modules):
        mod.unregister()

    print("[Animeow Toolkit] Unregistered successfully.")


if __name__ == "__main__":
    register()
