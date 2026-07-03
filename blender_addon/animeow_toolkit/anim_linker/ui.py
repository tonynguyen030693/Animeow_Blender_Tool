"""
ui.py — Animeow Toolkit / Anim Linker
=======================================
Panel giao diện cho module Anim Linker, kế thừa AnimeowBasePanel.
Cải tiến UX/UI với thiết kế compact, dynamic warnings và feedback thông tin.
"""

import bpy
from ..core.base_panel import AnimeowBasePanel
from ..core.utils import get_action_fcurves


class ANIMEOW_PT_linker_panel(AnimeowBasePanel, bpy.types.Panel):
    """Panel giao diện chính cho Anim Linker"""
    bl_label = "🎯 Anim Linker"
    bl_idname = "ANIMEOW_PT_linker_panel"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "animeow_active_tab"):
            return True
        return context.scene.animeow_active_tab == 'LINKER'

    def draw(self, context):
        layout = self.layout
        try:
            scene = context.scene
            active_obj = context.active_object

            # UX CẢNH BÁO ĐỘNG DỰA TRÊN SELECTION
            if not active_obj:
                box_warn = layout.box()
                box_warn.label(text="Hãy chọn vật thể/xương để diễn!", icon='INFO')
                return

            # Kiểm tra trạng thái liên kết hiện tại của đối tượng hoạt động
            is_linked = False
            has_anim = False
            constrained_target = active_obj
            armature_obj = None

            if active_obj.type == 'ARMATURE' and context.active_pose_bone:
                constrained_target = context.active_pose_bone
                armature_obj = active_obj

            # 1. Check link
            if any(c.name.startswith("ChildOf_loc_child_") for c in constrained_target.constraints):
                is_linked = True

            # 2. Check animation
            if armature_obj:
                if armature_obj.animation_data and armature_obj.animation_data.action:
                    action = armature_obj.animation_data.action
                    prefix = f'pose.bones["{constrained_target.name}"]'
                    has_anim = any(fc.data_path.startswith(prefix) for fc in get_action_fcurves(action))
            else:
                if constrained_target.animation_data and constrained_target.animation_data.action:
                    has_anim = True

            # Hộp trạng thái phản hồi động (Dynamic Feedback Header)
            box_status = layout.box()
            col_status = box_status.column(align=True)
            if is_linked:
                col_status.label(text=f"Trạng thái: Đang Liên Kết ({constrained_target.name})", icon='LINKED')
            else:
                col_status.label(text=f"Trạng thái: Sẵn Sàng ({constrained_target.name})", icon='INFO')
                if has_anim:
                    col_status.label(text="Dang co Anim cu - Se tu dong chuyen sang Locator", icon='INFO')

            # --- SECTION 1: TARGET DEFINITION ---
            box = layout.box()
            row_target = box.row(align=True)
            row_target.label(text="Thiết lập Target", icon='CONSTRAINT_BONE')
            row_target.operator("animeow.get_active_bone", text="", icon='EYEDROPPER')

            col = box.column(align=True)
            col.prop(scene, "animeow_target_object", text="Target Obj")

            target_obj = scene.animeow_target_object
            if target_obj and target_obj.type == 'ARMATURE':
                col.prop(scene, "animeow_target_bone", text="Target Bone")

            # --- SECTION 2: QUICK LINK ---
            box_link = layout.box()
            box_link.label(text="Gán Ràng Buộc Nhanh", icon='LINKED')
            
            # Grid layout gọn gàng
            row_link = box_link.row(align=True)
            row_link.prop(scene, "animeow_use_locator", text="Locator", toggle=True)
            row_link.operator("animeow.quick_link", text="Link", icon='ADD')

            # --- SECTION 3: SPACE SWITCHER ---
            box_switch = layout.box()
            box_switch.label(text="Chuyển Đổi Không Gian", icon='FILE_REFRESH')
            
            col_switch = box_switch.column(align=True)
            col_switch.label(text="Chọn Target mới rồi Click:")
            col_switch.operator("animeow.switch_parent", text="Switch Parent", icon='FILE_REFRESH')
            # Grey-out nút Switch nếu không ở trạng thái liên kết locator
            if not is_linked:
                col_switch.active = False

            # --- SECTION 4: BAKE ANIMATION ---
            box_bake = layout.box()
            box_bake.label(text="Khóa Keyframe (Bake Animation)", icon='REC')
            
            col_bake = box_bake.column(align=True)
            # Thiết lập bước bake nhảy frame
            col_bake.prop(scene, "animeow_bake_step", text="Bước Bake (Step)")
            
            col_bake.separator()
            # Thiết lập Smart Clean lọc keyframe thừa
            row_clean = col_bake.row(align=True)
            row_clean.prop(scene, "animeow_smart_clean", text="Smart Clean", toggle=True)
            if scene.animeow_smart_clean:
                row_clean.prop(scene, "animeow_clean_threshold", text="Ngưỡng lọc")
                
            col_bake.separator()
            
            # Nút Bake & Clean chính
            row_btn = col_bake.row(align=True)
            row_btn.scale_y = 1.2
            row_btn.operator("animeow.quick_bake", text="Bake & Clean", icon='FILE_REFRESH')
            
            # Grey-out toàn bộ khối cấu hình nếu không ở trạng thái liên kết
            if not is_linked:
                col_bake.active = False
                
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            box = layout.box()
            box.alert = True
            box.label(text="Loi ve UI (UI Draw Error):", icon='ERROR')
            for line in tb.split("\n")[:5]:
                if line.strip():
                    box.label(text=line[:50], icon='NONE')

