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
]
