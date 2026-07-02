"""
__init__.py — Animeow Toolkit / Transform Rounder
====================================================
Khai báo danh sách classes và properties cho module Transform Rounder.
"""

import bpy
from .operators import ANIMEOW_OT_round_transforms
from .ui import ANIMEOW_PT_transform_rounder

classes = (
    ANIMEOW_OT_round_transforms,
    ANIMEOW_PT_transform_rounder,
)

properties = [
    ("animeow_round_decimals", bpy.props.IntProperty(
        name="Decimals",
        description="Số chữ số sau dấu phẩy",
        default=2,
        min=0,
        max=6
    )),
    ("animeow_round_location", bpy.props.BoolProperty(
        name="Location",
        default=True
    )),
    ("animeow_round_rotation", bpy.props.BoolProperty(
        name="Rotation",
        default=True
    )),
    ("animeow_round_scale", bpy.props.BoolProperty(
        name="Scale",
        default=True
    )),
]
