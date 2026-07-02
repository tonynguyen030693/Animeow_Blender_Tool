"""
__init__.py — Animeow Toolkit / Bone Picker
=============================================
Khai báo danh sách classes cho module Bone Picker.
"""

from . import properties
from . import operators
from . import animate_handler
from . import io_handler
from . import panels

_sub_modules = (properties, operators, animate_handler, io_handler, panels)


def module_register():
    """Đăng ký toàn bộ classes trong Bone Picker."""
    for mod in _sub_modules:
        mod.register()


def module_unregister():
    """Huỷ đăng ký toàn bộ classes trong Bone Picker."""
    # Dọn dẹp draw handler trước khi unregister
    try:
        from .animate_handler import PICKER_OT_interact
        import bpy
        if PICKER_OT_interact._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(
                PICKER_OT_interact._draw_handler, 'WINDOW')
            PICKER_OT_interact._draw_handler = None
            PICKER_OT_interact._is_running = False
    except Exception:
        pass

    for mod in reversed(_sub_modules):
        mod.unregister()
