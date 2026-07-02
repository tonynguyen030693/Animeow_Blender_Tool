"""
__init__.py — Animeow Toolkit / Anim Linker
=============================================
Khai báo danh sách classes và properties cho module Anim Linker.
"""

import bpy
from .operators import (
    ANIMEOW_OT_quick_link,
    ANIMEOW_OT_get_active_bone,
    ANIMEOW_OT_switch_parent,
    ANIMEOW_OT_quick_bake,
)
from .ui import ANIMEOW_PT_linker_panel

classes = (
    ANIMEOW_OT_quick_link,
    ANIMEOW_OT_get_active_bone,
    ANIMEOW_OT_switch_parent,
    ANIMEOW_OT_quick_bake,
    ANIMEOW_PT_linker_panel,
)

properties = [
    ("animeow_target_object", bpy.props.PointerProperty(
        name="Target Object",
        type=bpy.types.Object,
        description="Đối tượng đích cần liên kết tới"
    )),
    ("animeow_target_bone", bpy.props.StringProperty(
        name="Target Bone",
        description="Xương đích cần liên kết tới"
    )),
    ("animeow_use_locator", bpy.props.BoolProperty(
        name="Sử dụng Smart Locator (Empty)",
        default=True,
        description="Tạo cặp Empty (Hook & Offset) làm trung gian để giữ Transform sạch sẽ"
    )),
    ("animeow_bake_step", bpy.props.IntProperty(
        name="Bước Bake (Step)",
        default=1,
        min=1,
        max=10,
        description="Số lượng frame nhảy khi bake (1 = bake mọi frame)"
    )),
    ("animeow_smart_clean", bpy.props.BoolProperty(
        name="Smart Clean",
        default=False,
        description="Tự động lọc bỏ các keyframe thừa, giữ đồ thị mượt mà sau khi bake"
    )),
    ("animeow_clean_threshold", bpy.props.FloatProperty(
        name="Ngưỡng lọc",
        default=0.001,
        min=0.0001,
        max=0.1,
        precision=4,
        description="Độ sai lệch cho phép khi lọc keyframe (nhỏ = chính xác hơn)"
    )),
]
