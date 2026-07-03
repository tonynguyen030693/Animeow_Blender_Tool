"""
__init__.py — Animeow Toolkit / Anim Bake
============================================
Khai báo danh sách classes và properties cho module Anim Bake & Clean.
"""

import bpy
from .operators import ANIMEOW_OT_smart_bake
from .ui import ANIMEOW_PT_smart_bake_panel

classes = (
    ANIMEOW_OT_smart_bake,
    ANIMEOW_PT_smart_bake_panel,
)

properties = [
    ("animeow_bake_use_timeline", bpy.props.BoolProperty(
        name="Timeline Range",
        default=True,
        description="Sử dụng frame bắt đầu và kết thúc của Timeline hiện tại"
    )),
    ("animeow_bake_start", bpy.props.IntProperty(
        name="Frame Bắt đầu",
        default=1,
        description="Frame bắt đầu bake"
    )),
    ("animeow_bake_end", bpy.props.IntProperty(
        name="Frame Kết thúc",
        default=250,
        description="Frame kết thúc bake"
    )),
    ("animeow_bake_step", bpy.props.IntProperty(
        name="Bước Bake (Step)",
        default=1,
        min=1,
        max=10,
        description="Bước nhảy frame khi bake (1 = bake mọi frame)"
    )),
    ("animeow_bake_visual_keying", bpy.props.BoolProperty(
        name="Visual Keying",
        default=True,
        description="Ghi keyframe dựa trên toạ độ trực quan thực tế (sau constraint)"
    )),
    ("animeow_bake_clear_constraints", bpy.props.BoolProperty(
        name="Xóa Constraints",
        default=False,
        description="Xóa bỏ các constraint sau khi đã bake chuyển động vào keyframe"
    )),
    ("animeow_bake_smart_clean", bpy.props.BoolProperty(
        name="Smart Clean",
        default=True,
        description="Tự động tối ưu/lọc keyframe thừa và bảo vệ cực trị"
    )),
    ("animeow_bake_clean_threshold", bpy.props.FloatProperty(
        name="Ngưỡng lọc",
        default=0.005,
        min=0.0001,
        max=0.1,
        precision=4,
        description="Độ sai lệch cho phép khi lọc keyframe"
    )),
]
