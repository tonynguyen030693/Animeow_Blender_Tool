"""
operators.py — Animeow Toolkit / Anim Bake
==============================================
Định nghĩa toán tử Smart Bake hoạt họa chung cho cả xương và vật thể.
"""

import bpy
from ..core.utils import get_action_fcurves, clean_fcurve_keyframes

class ANIMEOW_OT_smart_bake(bpy.types.Operator):
    """Bake chuyển động và tối ưu hóa đồ thị bằng Smart Clean bảo vệ cực trị"""
    bl_idname = "animeow.smart_bake"
    bl_label = "Smart Bake Animation"
    bl_description = "Bake chuyển động của xương hoặc vật thể được chọn, tự động tối ưu hóa keyframe và giữ các cực trị"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Yêu cầu phải có đối tượng hoạt động
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        active_obj = context.active_object
        
        # 1. Xác định tầm frame
        if scene.animeow_bake_use_timeline:
            start_frame = scene.frame_start
            end_frame = scene.frame_end
        else:
            start_frame = scene.animeow_bake_start
            end_frame = scene.animeow_bake_end
            
        if start_frame >= end_frame:
            self.report({'WARNING'}, "Frame bắt đầu phải nhỏ hơn Frame kết thúc!")
            return {'CANCELLED'}
            
        # 2. Xác định danh sách xương hoặc vật thể cần bake
        mode = context.mode
        selected_bones = []
        selected_objs = []
        bake_type_set = set()
        
        if mode == 'POSE':
            selected_bones = context.selected_pose_bones
            if not selected_bones:
                self.report({'WARNING'}, "Vui lòng chọn ít nhất một xương trong Pose Mode!")
                return {'CANCELLED'}
            bake_type_set = {'POSE'}
        elif mode in ('OBJECT', 'NUMBERS'):
            selected_objs = context.selected_objects
            if not selected_objs:
                self.report({'WARNING'}, "Vui lòng chọn ít nhất một vật thể trong Object Mode!")
                return {'CANCELLED'}
            bake_type_set = {'OBJECT'}
        else:
            self.report({'WARNING'}, f"Chế độ '{mode}' không được hỗ trợ để bake!")
            return {'CANCELLED'}
            
        # 3. Lấy cấu hình Bake
        step = scene.animeow_bake_step
        smart_clean = scene.animeow_bake_smart_clean
        threshold = scene.animeow_bake_clean_threshold
        visual_keying = scene.animeow_bake_visual_keying
        clear_constraints = scene.animeow_bake_clear_constraints
        
        # Nếu bật Smart Clean, bake step=1 nội bộ để thu thập toàn bộ các cực trị
        bake_step = 1 if smart_clean else step
        
        self.report({'INFO'}, "Đang tiến hành Bake chuyển động...")
        
        # 4. Thực hiện Bake NLA gốc của Blender
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            step=bake_step,
            only_selected=True,
            visual_keying=visual_keying,
            clear_constraints=clear_constraints,
            clear_parents=False,
            bake_types=bake_type_set
        )
        
        # 5. Thực hiện Smart Clean và định hình Auto Tangent
        if mode == 'POSE':
            action = active_obj.animation_data.action if active_obj.animation_data else None
            if action:
                fcurves = get_action_fcurves(action)
                # Xử lý cho từng xương được chọn
                for bone in selected_bones:
                    prefix = f'pose.bones["{bone.name}"]'
                    for fc in fcurves:
                        if fc.data_path.startswith(prefix):
                            # 5.1 Smart Clean
                            if smart_clean:
                                clean_fcurve_keyframes(fc, threshold, step=step, start_frame=start_frame)
                            
                            # 5.2 Auto Tangents
                            for kp in fc.keyframe_points:
                                kp.interpolation = 'BEZIER'
                                kp.handle_left_type = 'AUTO'
                                kp.handle_right_type = 'AUTO'
                            fc.update()
                            
        else: # Object Mode
            # Xử lý cho từng vật thể được chọn
            for obj in selected_objs:
                action = obj.animation_data.action if obj.animation_data else None
                if action:
                    fcurves = get_action_fcurves(action)
                    for fc in fcurves:
                        # 5.1 Smart Clean
                        if smart_clean:
                            clean_fcurve_keyframes(fc, threshold, step=step, start_frame=start_frame)
                        
                        # 5.2 Auto Tangents
                        for kp in fc.keyframe_points:
                            kp.interpolation = 'BEZIER'
                            kp.handle_left_type = 'AUTO'
                            kp.handle_right_type = 'AUTO'
                        fc.update()
                        
        self.report({'INFO'}, "Smart Bake và tối ưu hóa keyframe thành công!")
        return {'FINISHED'}
