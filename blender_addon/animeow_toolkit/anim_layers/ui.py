"""
ui.py — Animeow Toolkit / Anim Layers
=========================================
Panel giao diện cho module Global Animation Layers, kế thừa AnimeowBasePanel.
Hiển thị global layer stack, cấu hình blend/weight, và thao tác merge.

KIẾN TRÚC GLOBAL:
- Danh sách layer đọc từ scene.animeow_global_layers (không phụ thuộc active object).
- Bảng điều khiển KHÔNG thay đổi khi người dùng chọn object khác.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel
from .layer_manager import LayerManager


# ══════════════════════════════════════════
#  UIList — Hiển thị từng Layer trong Stack
# ══════════════════════════════════════════

class ANIMEOW_UL_layer_list(bpy.types.UIList):
    """Danh sách hiển thị layer stack trong giao diện (dự phòng)."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name)


# ══════════════════════════════════════════
#  Panel chính — Global Animation Layers
# ══════════════════════════════════════════

class ANIMEOW_PT_anim_layers_panel(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Global Animation Layers"""
    bl_label = "🎭 Animation Layers"
    bl_idname = "ANIMEOW_PT_anim_layers_panel"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "animeow_active_tab"):
            return True
        return context.scene.animeow_active_tab == 'LAYERS'

    def draw(self, context):
        layout = self.layout
        try:
            scene = context.scene
            layers = scene.animeow_global_layers
            active_index = scene.animeow_global_active_index
            has_layers = len(layers) > 0

            # ── THÔNG TIN SELECTION ──
            box_info = layout.box()
            row_info = box_info.row(align=True)
            num_selected = len(context.selected_objects)
            active_obj = context.active_object
            if active_obj:
                obj_icon = 'ARMATURE_DATA' if active_obj.type == 'ARMATURE' else 'OBJECT_DATA'
                row_info.label(
                    text=f"Active: {active_obj.name}  |  Selected: {num_selected}",
                    icon=obj_icon
                )
            else:
                row_info.label(text=f"Selected: {num_selected}", icon='OBJECT_DATA')

            # ── GLOBAL LAYER STACK ──
            box_stack = layout.box()
            box_stack.label(text="Global Layer Stack", icon='NLA')

            if has_layers:
                # Vẽ danh sách layers (ngược: Base ở đáy, layer mới ở trên)
                for i in reversed(range(len(layers))):
                    layer = layers[i]
                    is_selected = (i == active_index)

                    row = box_stack.row(align=True)
                    if is_selected:
                        row.alert = True

                    # Số thứ tự
                    row.label(text=f"[{i}]")

                    # Tên layer làm nút bấm chọn
                    name = layer.name
                    if layer.is_base:
                        name = f"★ {name}"
                    if is_selected:
                        name = f"✏ {name}"
                    else:
                        name = f"   {name}"

                    sub = row.row()
                    sub.scale_x = 2.0
                    op_select = sub.operator(
                        "animeow.layer_select",
                        text=name, emboss=False
                    )
                    op_select.index = i

                    # Blend mode viết tắt
                    blend = layer.blend_type
                    blend_map = {
                        'ADD': 'ADD', 'REPLACE': 'RPL', 'COMBINE': 'CMB',
                        'SUBTRACT': 'SUB', 'MULTIPLY': 'MUL'
                    }
                    row.label(text=blend_map.get(blend, blend[:3]))

                    # Weight
                    row.label(text=f"{layer.influence:.2f}")

                    # Số objects tham gia layer này
                    member_count = len(LayerManager.get_member_objects(scene, layer.name))
                    row.label(text=f"[{member_count}]")

                    # Mute toggle
                    if not is_selected:
                        mute_icon = 'HIDE_ON' if layer.mute else 'HIDE_OFF'
                        op_mute = row.operator(
                            "animeow.layer_mute", text="", icon=mute_icon, emboss=False
                        )
                        op_mute.index = i
                    else:
                        row.label(text="", icon='BLANK1')

                    if is_selected:
                        row.alert = False

            else:
                box_stack.label(text="Chưa có layer nào", icon='INFO')

            # ── TOOLBAR: Add / Delete / Move ──
            row_tools = box_stack.row(align=True)
            row_tools.operator("animeow.layer_add", text="Add", icon='ADD')
            row_tools.operator("animeow.layer_delete", text="Delete", icon='REMOVE')
            row_tools.separator()

            op_up = row_tools.operator("animeow.layer_move", text="", icon='TRIA_UP')
            op_up.direction = 'UP'
            op_down = row_tools.operator("animeow.layer_move", text="", icon='TRIA_DOWN')
            op_down.direction = 'DOWN'

            # ── TOOLBAR: Add/Remove Objects ──
            if has_layers:
                row_obj = box_stack.row(align=True)
                row_obj.operator(
                    "animeow.layer_add_objects",
                    text="+ Add Selected", icon='LINKED'
                )
                row_obj.operator(
                    "animeow.layer_remove_objects",
                    text="- Remove Selected", icon='UNLINKED'
                )

            # ── CẤU HÌNH LAYER ĐANG CHỌN ──
            if has_layers and active_index < len(layers):
                selected_layer = layers[active_index]

                box_config = layout.box()
                box_config.label(text="Cấu hình Layer đang chọn", icon='PREFERENCES')

                col_cfg = box_config.column(align=True)

                # Blend Mode — dùng property trực tiếp từ global layer
                col_cfg.prop(selected_layer, "blend_type", text="Blend Mode")

                # Weight slider — dùng property trực tiếp từ global layer
                col_cfg.prop(selected_layer, "influence", text="Weight", slider=True)

                # Keyframe weight button
                col_cfg.operator(
                    "animeow.layer_keyframe_weight",
                    text="Key Weight", icon='KEYTYPE_KEYFRAME_VEC'
                )

                # Solo button (chỉ cho non-active, non-base layers)
                if not selected_layer.is_base:
                    row_solo = col_cfg.row(align=True)
                    op_solo = row_solo.operator(
                        "animeow.layer_solo",
                        text="Solo", icon='SOLO_ON'
                    )
                    op_solo.index = active_index

                # Hiển thị danh sách objects tham gia layer
                members = LayerManager.get_member_objects(scene, selected_layer.name)
                if members:
                    box_members = box_config.box()
                    row_members = box_members.row(align=True)
                    row_members.label(text=f"Objects trong layer ({len(members)}):", icon='GROUP')
                    row_members.operator("animeow.layer_select_members", text="Select", icon='RESTRICT_SELECT_OFF')
                    col_members = box_members.column(align=True)
                    for obj in members[:10]:  # Giới hạn hiển thị 10 objects
                        obj_icon = 'ARMATURE_DATA' if obj.type == 'ARMATURE' else 'OBJECT_DATA'
                        col_members.label(text=obj.name, icon=obj_icon)
                    if len(members) > 10:
                        col_members.label(text=f"... và {len(members) - 10} objects khác")

            # ── MERGE ACTIONS ──
            box_merge = layout.box()
            box_merge.label(text="Gộp Layers", icon='IMPORT')

            col_merge = box_merge.column(align=True)
            col_merge.operator(
                "animeow.layer_merge_down",
                text="Merge Down", icon='TRIA_DOWN'
            )

            row_merge_all = col_merge.row(align=True)
            row_merge_all.scale_y = 1.3
            row_merge_all.operator(
                "animeow.layer_merge_all",
                text="Merge All Layers", icon='IMPORT'
            )

            # Smart Clean option cho Merge
            col_merge.separator()
            row_clean = col_merge.row(align=True)
            row_clean.prop(scene, "animeow_layers_smart_clean", text="Smart Clean", toggle=True)
            if scene.animeow_layers_smart_clean:
                row_clean.prop(scene, "animeow_layers_clean_threshold", text="Ngưỡng")

            # Grey-out merge nếu không có layers
            if not has_layers:
                box_merge.active = False

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            box = layout.box()
            box.alert = True
            box.label(text="Lỗi vẽ giao diện (UI Draw Error):", icon='ERROR')
            for line in tb.split("\n")[:5]:
                if line.strip():
                    box.label(text=line[:80], icon='NONE')
