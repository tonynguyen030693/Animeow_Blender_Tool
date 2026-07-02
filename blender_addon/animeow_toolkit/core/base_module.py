"""
base_module.py — Animeow Toolkit
=================================
Lớp cơ sở quản lý vòng đời (Lifecycle) của một Module con trong Toolkit.
Mỗi module con (anim_linker, graph_toolboard, bone_picker, transform_rounder)
sẽ được bọc trong một đối tượng ToolkitModule để đăng ký/huỷ đăng ký
một cách thống nhất và an toàn.
"""

import bpy


class ToolkitModule:
    """Đóng gói logic đăng ký và huỷ đăng ký của một module con.

    Args:
        name: Tên hiển thị của module (dùng cho logging).
        classes: Tuple/List các class Blender cần đăng ký (Operators, Panels, ...).
        properties: Danh sách tuple (attr_name, bpy.props.*) để gán lên bpy.types.Scene.
        cleanup_fn: Hàm callback dọn dẹp đặc biệt (ví dụ: xoá draw handler của bone_picker).
    """

    def __init__(self, name, classes, properties=None, cleanup_fn=None):
        self.name = name
        self.classes = classes
        self.properties = properties or []
        self.cleanup_fn = cleanup_fn

    def register(self):
        """Đăng ký toàn bộ class và properties của module lên Blender."""
        for cls in self.classes:
            bpy.utils.register_class(cls)
        for attr_name, prop in self.properties:
            setattr(bpy.types.Scene, attr_name, prop)
        print(f"[Animeow Toolkit] Module '{self.name}' registered.")

    def unregister(self):
        """Huỷ đăng ký toàn bộ class, properties và chạy cleanup nếu có."""
        if self.cleanup_fn:
            try:
                self.cleanup_fn()
            except Exception as e:
                print(f"[Animeow Toolkit] Cleanup error in '{self.name}': {e}")

        for attr_name, _ in reversed(self.properties):
            if hasattr(bpy.types.Scene, attr_name):
                delattr(bpy.types.Scene, attr_name)

        for cls in reversed(self.classes):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass  # Class đã bị huỷ đăng ký trước đó

        print(f"[Animeow Toolkit] Module '{self.name}' unregistered.")
