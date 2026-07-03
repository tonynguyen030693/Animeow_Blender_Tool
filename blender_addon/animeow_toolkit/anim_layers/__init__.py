"""
__init__.py — Animeow Toolkit / Anim Layers
===============================================
Khai báo danh sách classes và properties cho module Animation Layers.
Sử dụng kiến trúc Global (scene-wide) thay vì per-object.
"""

import bpy
from .operators import (
    ANIMEOW_OT_layer_add,
    ANIMEOW_OT_layer_select,
    ANIMEOW_OT_layer_delete,
    ANIMEOW_OT_layer_mute,
    ANIMEOW_OT_layer_solo,
    ANIMEOW_OT_layer_merge_down,
    ANIMEOW_OT_layer_merge_all,
    ANIMEOW_OT_layer_move,
    ANIMEOW_OT_layer_keyframe_weight,
    ANIMEOW_OT_layer_add_objects,
    ANIMEOW_OT_layer_remove_objects,
    ANIMEOW_OT_layer_select_members,
)
from .ui import (
    ANIMEOW_UL_layer_list,
    ANIMEOW_PT_anim_layers_panel,
)


# ══════════════════════════════════════════
#  PropertyGroup — Global Layer Entry
# ══════════════════════════════════════════

class AnimeowGlobalLayer(bpy.types.PropertyGroup):
    """Một layer trong danh sách global Animation Layers.

    Lưu trữ trên Scene, không phụ thuộc vào object nào.
    Mỗi entry tương ứng với một nhóm NLA tracks cùng tên
    trên các objects tham gia.
    """
    name: bpy.props.StringProperty(
        name="Layer Name",
        default="New Layer",
        description="Tên hiển thị của layer"
    )
    blend_type: bpy.props.EnumProperty(
        name="Blend Mode",
        items=[
            ('ADD', "Additive", "Cộng thêm chuyển động lên các layer bên dưới"),
            ('REPLACE', "Replace", "Ghi đè chuyển động của các layer bên dưới"),
            ('COMBINE', "Combine", "Kết hợp thông minh dựa trên loại kênh"),
        ],
        default='ADD',
        description="Chế độ pha trộn của layer"
    )
    influence: bpy.props.FloatProperty(
        name="Weight",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Trọng số ảnh hưởng của layer (0.0 = không ảnh hưởng, 1.0 = đầy đủ)"
    )
    mute: bpy.props.BoolProperty(
        name="Mute",
        default=False,
        description="Tắt tiếng layer (không ảnh hưởng lên kết quả)"
    )
    is_base: bpy.props.BoolProperty(
        name="Is Base",
        default=False,
        description="Đánh dấu layer này là Base (layer gốc)"
    )


classes = (
    # PropertyGroup (phải đăng ký TRƯỚC operators và panels sử dụng nó)
    AnimeowGlobalLayer,
    # Operators
    ANIMEOW_OT_layer_add,
    ANIMEOW_OT_layer_select,
    ANIMEOW_OT_layer_delete,
    ANIMEOW_OT_layer_mute,
    ANIMEOW_OT_layer_solo,
    ANIMEOW_OT_layer_merge_down,
    ANIMEOW_OT_layer_merge_all,
    ANIMEOW_OT_layer_move,
    ANIMEOW_OT_layer_keyframe_weight,
    ANIMEOW_OT_layer_add_objects,
    ANIMEOW_OT_layer_remove_objects,
    ANIMEOW_OT_layer_select_members,
    # UI
    ANIMEOW_UL_layer_list,
    ANIMEOW_PT_anim_layers_panel,
)

properties = [
    # Danh sách global layers (CollectionProperty)
    ("animeow_global_layers", bpy.props.CollectionProperty(
        type=AnimeowGlobalLayer,
        name="Global Animation Layers",
        description="Danh sách Animation Layers toàn cục cho Scene"
    )),
    # Index layer đang active
    ("animeow_global_active_index", bpy.props.IntProperty(
        name="Active Layer Index",
        default=0,
        description="Index của layer đang được chọn/chỉnh sửa"
    )),
    # Smart Clean khi Merge
    ("animeow_layers_smart_clean", bpy.props.BoolProperty(
        name="Smart Clean khi Merge",
        default=True,
        description="Tự động tối ưu/lọc keyframe thừa khi gộp layers"
    )),
    # Ngưỡng lọc
    ("animeow_layers_clean_threshold", bpy.props.FloatProperty(
        name="Ngưỡng lọc",
        default=0.005,
        min=0.0001,
        max=0.1,
        precision=4,
        description="Độ sai lệch cho phép khi lọc keyframe lúc merge"
    )),
]
