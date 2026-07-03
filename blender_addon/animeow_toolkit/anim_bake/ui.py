"""
ui.py — Animeow Toolkit / Anim Bake
======================================
Panel giao diện cho module Anim Bake, kế thừa AnimeowBasePanel.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel

class ANIMEOW_PT_smart_bake_panel(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Anim Bake & Keyframe Optimization"""
    bl_label = "🎬 Smart Bake & Optimize"
    bl_idname = "ANIMEOW_PT_smart_bake_panel"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "animeow_active_tab"):
            return True
        return context.scene.animeow_active_tab == 'BAKER'

    def draw(self, context):
        layout = self.layout
        try:
            scene = context.scene
            active_obj = context.active_object
            mode = context.mode

            # 1. Hộp thông tin lựa chọn hiện tại (Target Scope)
            box_target = layout.box()
            box_target.label("Mục tiêu Bake (Target Scope)", icon='TRACKING')
            
            if not active_obj:
                box_target.alert = True
                box_target.label("Vui lòng chọn Xương hoặc Vật thể!", icon='ERROR')
                is_valid_selection = False
            elif mode == 'POSE':
                selected_bones = context.selected_pose_bones
                if selected_bones:
                    box_target.label(f"Pose Mode: {len(selected_bones)} xương được chọn", icon='POSE_HLT')
                    is_valid_selection = True
                else:
                    box_target.alert = True
                    box_target.label("Chưa chọn xương nào trong Rig!", icon='WARNING')
                    is_valid_selection = False
            elif mode in ('OBJECT', 'NUMBERS'):
                selected_objs = context.selected_objects
                if selected_objs:
                    box_target.label(f"Object Mode: {len(selected_objs)} vật thể được chọn", icon='OBJECT_DATAMODE')
                    is_valid_selection = True
                else:
                    box_target.alert = True
                    box_target.label("Chưa chọn vật thể nào!", icon='WARNING')
                    is_valid_selection = False
            else:
                box_target.alert = True
                box_target.label(f"Chế độ '{mode}' không hỗ trợ bake!", icon='ERROR')
                is_valid_selection = False

            # 2. Cấu hình Frame Range
            box_range = layout.box()
            box_range.label("Khoảng Frame (Bake Range)", icon='TIME')
            
            box_range.prop(scene, "animeow_bake_use_timeline", text="Sử dụng tầm Timeline", toggle=True)
            if not scene.animeow_bake_use_timeline:
                row_f = box_range.row(align=True)
                row_f.prop(scene, "animeow_bake_start", text="Bắt đầu")
                row_f.prop(scene, "animeow_bake_end", text="Kết thúc")

            # 3. Cấu hình Bake Options
            box_opts = layout.box()
            box_opts.label("Cấu hình Bake (Bake Settings)", icon='PREFERENCES')
            
            col_opts = box_opts.column(align=True)
            col_opts.prop(scene, "animeow_bake_step", text="Bước Bake (Step)")
            col_opts.separator()
            col_opts.prop(scene, "animeow_bake_visual_keying", text="Bake Visual Keying")
            col_opts.prop(scene, "animeow_bake_clear_constraints", text="Xóa Constraints sau khi Bake")

            # 4. Cấu hình Smart Clean
            box_clean = layout.box()
            box_clean.label("Bộ lọc Keyframe (Smart Clean)", icon='REC')
            
            row_clean = box_clean.row(align=True)
            row_clean.prop(scene, "animeow_bake_smart_clean", text="Smart Clean", toggle=True)
            if scene.animeow_bake_smart_clean:
                row_clean.prop(scene, "animeow_bake_clean_threshold", text="Ngưỡng")

            layout.separator()

            # 5. Nút nhấn Bake chính
            row_bake = layout.row(align=True)
            row_bake.scale_y = 1.3
            row_bake.operator("animeow.smart_bake", text="Smart Bake Animation", icon='REC')
            
            # Khóa nút nếu lựa chọn không hợp lệ
            if not is_valid_selection:
                row_bake.active = False
                box_opts.active = False
                box_clean.active = False
                box_range.active = False

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            box = layout.box()
            box.alert = True
            box.label("Lỗi vẽ giao diện (UI Draw Error):", icon='ERROR')
            for line in tb.split("\n")[:5]:
                if line.strip():
                    box.label(line[:50], icon='NONE')
