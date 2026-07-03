"""
__init__.py — Animeow Toolkit / Anim Copy
============================================
Khai báo danh sách classes và properties cho module Anim Copy & Paste.
"""

import bpy
from .operators import (
    ANIMEOW_OT_copy_anim,
    ANIMEOW_OT_paste_anim,
    ANIMEOW_OT_paste_connect,
)
from .ui import ANIMEOW_PT_copy_panel

classes = (
    ANIMEOW_OT_copy_anim,
    ANIMEOW_OT_paste_anim,
    ANIMEOW_OT_paste_connect,
    ANIMEOW_PT_copy_panel,
)

properties = [
    ("animeow_copy_mirror", bpy.props.BoolProperty(
        name="Lật Đối Xứng (Mirror)",
        default=False,
        description="Đảo ngược các trục đối xứng tương ứng (X, Y, Z) khi dán keyframe"
    )),
    ("animeow_copy_range_type", bpy.props.EnumProperty(
        name="Phạm Vi Copy",
        items=[
            ('ALL', "Tất Cả (All)", "Sao chép toàn bộ keyframe"),
            ('TIMELINE', "Timeline (Preview)", "Sao chép trong khoảng timeline đang xem"),
            ('CUSTOM', "Tự Chọn (Custom)", "Sao chép trong khoảng frame tự cấu hình"),
        ],
        default='ALL',
        description="Chọn phạm vi frame muốn sao chép"
    )),
    ("animeow_copy_frame_start", bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        description="Frame bắt đầu cho phạm vi Custom"
    )),
    ("animeow_copy_frame_end", bpy.props.IntProperty(
        name="End Frame",
        default=250,
        description="Frame kết thúc cho phạm vi Custom"
    )),
    ("animeow_mirror_tx", bpy.props.BoolProperty(
        name="TX", default=True, description="Lật đối xứng trục Location X"
    )),
    ("animeow_mirror_ty", bpy.props.BoolProperty(
        name="TY", default=False, description="Lật đối xứng trục Location Y"
    )),
    ("animeow_mirror_tz", bpy.props.BoolProperty(
        name="TZ", default=False, description="Lật đối xứng trục Location Z"
    )),
    ("animeow_mirror_rx", bpy.props.BoolProperty(
        name="RX", default=False, description="Lật đối xứng trục Rotation X (Euler/Quaternion/AxisAngle)"
    )),
    ("animeow_mirror_ry", bpy.props.BoolProperty(
        name="RY", default=True, description="Lật đối xứng trục Rotation Y (Euler/Quaternion/AxisAngle)"
    )),
    ("animeow_mirror_rz", bpy.props.BoolProperty(
        name="RZ", default=True, description="Lật đối xứng trục Rotation Z (Euler/Quaternion/AxisAngle)"
    )),
]
