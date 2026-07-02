"""
operators.py — Animeow Toolkit / Anim Copy
=============================================
Operators xử lý tính năng sao chép, dán, dán nối tiếp (Paste Connect)
và dán đối xứng (Mirror) chuyển động cho các Control.
"""

import bpy
from mathutils import Matrix
from ..core.utils import get_constrained_target, mirror_keyframe_value

# Bộ nhớ tạm lưu trữ keyframe trong Python
animeow_clipboard = {}


class ANIMEOW_OT_copy_anim(bpy.types.Operator):
    """Sao chép toàn bộ keyframes của đối tượng đang chọn vào bộ nhớ tạm"""
    bl_idname = "animeow.copy_anim"
    bl_label = "Copy Anim"
    bl_description = "Sao chép toàn bộ keyframe của xương hoặc vật thể đang chọn"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global animeow_clipboard
        constrained_target, armature_obj = get_constrained_target(context)

        if not constrained_target:
            self.report({'WARNING'}, "Hãy chọn đối tượng hoặc xương để Copy!")
            return {'CANCELLED'}

        anim_target = armature_obj if armature_obj else constrained_target
        if not anim_target.animation_data or not anim_target.animation_data.action:
            self.report({'WARNING'}, f"Đối tượng '{constrained_target.name}' không có keyframe nào!")
            return {'CANCELLED'}

        action = anim_target.animation_data.action
        is_bone = (armature_obj is not None)

        # Lọc F-Curves thuộc về đối tượng đang chọn
        fcurves = []
        if is_bone:
            prefix = f'pose.bones["{constrained_target.name}"]'
            fcurves = [fc for fc in action.fcurves if fc.data_path.startswith(prefix)]
        else:
            # Đối với Object, các data_path thường là "location", "rotation_euler", v.v.
            # Tránh lấy nhầm các data_path trỏ tới sub-objects hoặc custom properties khác
            valid_paths = {"location", "rotation_euler", "rotation_quaternion", "rotation_axis_angle", "scale"}
            fcurves = [fc for fc in action.fcurves if fc.data_path in valid_paths]

        if not fcurves:
            self.report({'WARNING'}, f"Không tìm thấy keyframe hợp lệ cho '{constrained_target.name}'!")
            return {'CANCELLED'}

        # Đọc dữ liệu keyframe
        curves_data = []
        for fc in fcurves:
            clean_path = fc.data_path.split(".")[-1] if is_bone else fc.data_path
            keyframes = []
            for kp in fc.keyframe_points:
                keyframes.append({
                    "co": (kp.co[0], kp.co[1]),
                    "handle_left": (kp.handle_left[0], kp.handle_left[1]),
                    "handle_right": (kp.handle_right[0], kp.handle_right[1]),
                    "interpolation": kp.interpolation
                })
            curves_data.append({
                "data_path": clean_path,
                "array_index": fc.array_index,
                "keyframes": keyframes
            })

        animeow_clipboard = {
            "is_bone": is_bone,
            "owner_name": constrained_target.name,
            "curves": curves_data
        }

        self.report({'INFO'}, f"Đã copy anim của {constrained_target.name} ({len(fcurves)} kênh)!")
        return {'FINISHED'}


class ANIMEOW_OT_paste_anim(bpy.types.Operator):
    """Dán keyframes đã sao chép lên đối tượng đang chọn"""
    bl_idname = "animeow.paste_anim"
    bl_label = "Paste Anim"
    bl_description = "Dán keyframe bắt đầu tại frame hiện tại"
    bl_options = {'REGISTER', 'UNDO'}

    mirror: bpy.props.BoolProperty(name="Mirror (Đối xứng)", default=False)

    def execute(self, context):
        global animeow_clipboard
        if not animeow_clipboard:
            self.report({'WARNING'}, "Bộ nhớ tạm trống! Hãy Copy trước.")
            return {'CANCELLED'}

        constrained_target, armature_obj = get_constrained_target(context)
        if not constrained_target:
            self.report({'WARNING'}, "Hãy chọn đối tượng/xương để dán!")
            return {'CANCELLED'}

        anim_target = armature_obj if armature_obj else constrained_target
        if not anim_target.animation_data:
            anim_target.animation_data_create()
        if not anim_target.animation_data.action:
            anim_target.animation_data.action = bpy.data.actions.new(name=f"{anim_target.name}_Action")

        action = anim_target.animation_data.action
        is_bone = (armature_obj is not None)
        current_frame = context.scene.frame_current

        # Tính toán offset thời gian
        # Tìm frame đầu tiên trong đống keyframe đã copy
        all_frames = []
        for curve in animeow_clipboard["curves"]:
            for kp in curve["keyframes"]:
                all_frames.append(kp["co"][0])
        
        if not all_frames:
            self.report({'WARNING'}, "Dữ liệu keyframe đã copy bị trống!")
            return {'CANCELLED'}
            
        min_frame = min(all_frames)
        time_offset = current_frame - min_frame

        # Thực hiện dán
        for curve in animeow_clipboard["curves"]:
            # Tạo đường dẫn F-Curve mới
            if is_bone:
                full_path = f'pose.bones["{constrained_target.name}"].{curve["data_path"]}'
            else:
                full_path = curve["data_path"]

            # Tìm hoặc tạo mới F-Curve
            fc = action.fcurves.find(data_path=full_path, index=curve["array_index"])
            if not fc:
                fc = action.fcurves.new(data_path=full_path, index=curve["array_index"])

            for kp in curve["keyframes"]:
                new_frame = kp["co"][0] + time_offset
                new_val = kp["co"][1]
                
                # Tính toán Handle coordinates (lấy delta so với co)
                h_left_dx = kp["handle_left"][0] - kp["co"][0]
                h_left_dy = kp["handle_left"][1] - kp["co"][1]
                h_right_dx = kp["handle_right"][0] - kp["co"][0]
                h_right_dy = kp["handle_right"][1] - kp["co"][1]

                if self.mirror:
                    new_val = mirror_keyframe_value(curve["data_path"], curve["array_index"], new_val)
                    h_left_dy = mirror_keyframe_value(curve["data_path"], curve["array_index"], h_left_dy)
                    h_right_dy = mirror_keyframe_value(curve["data_path"], curve["array_index"], h_right_dy)

                # Chèn keyframe
                new_kp = fc.keyframe_points.insert(frame=new_frame, value=new_val)
                new_kp.interpolation = kp["interpolation"]
                new_kp.handle_left = (new_frame + h_left_dx, new_val + h_left_dy)
                new_kp.handle_right = (new_frame + h_right_dx, new_val + h_right_dy)

        context.view_layer.update()
        self.report({'INFO'}, f"Đã dán anim {'đối xứng ' if self.mirror else ''}lên {constrained_target.name}!")
        return {'FINISHED'}


class ANIMEOW_OT_paste_connect(bpy.types.Operator):
    """Dán nối tiếp keyframes đã sao chép mà không bị giật vị trí"""
    bl_idname = "animeow.paste_connect"
    bl_label = "Paste Connect"
    bl_description = "Dán nối tiếp chuyển động mượt mà vào vị trí hiện tại của đối tượng"
    bl_options = {'REGISTER', 'UNDO'}

    mirror: bpy.props.BoolProperty(name="Mirror (Đối xứng)", default=False)

    def execute(self, context):
        global animeow_clipboard
        if not animeow_clipboard:
            self.report({'WARNING'}, "Bộ nhớ tạm trống! Hãy Copy trước.")
            return {'CANCELLED'}

        constrained_target, armature_obj = get_constrained_target(context)
        if not constrained_target:
            self.report({'WARNING'}, "Hãy chọn đối tượng/xương để dán!")
            return {'CANCELLED'}

        anim_target = armature_obj if armature_obj else constrained_target
        if not anim_target.animation_data:
            anim_target.animation_data_create()
        if not anim_target.animation_data.action:
            anim_target.animation_data.action = bpy.data.actions.new(name=f"{anim_target.name}_Action")

        action = anim_target.animation_data.action
        is_bone = (armature_obj is not None)
        current_frame = context.scene.frame_current

        # Đọc thời gian của clipboard
        all_frames = []
        for curve in animeow_clipboard["curves"]:
            for kp in curve["keyframes"]:
                all_frames.append(kp["co"][0])
        
        if not all_frames:
            return {'CANCELLED'}
        min_frame = min(all_frames)
        time_offset = current_frame - min_frame

        # Duyệt qua các curve trong clipboard và tính toán offset cho từng kênh
        for curve in animeow_clipboard["curves"]:
            if is_bone:
                full_path = f'pose.bones["{constrained_target.name}"].{curve["data_path"]}'
            else:
                full_path = curve["data_path"]

            # Lấy giá trị của keyframe đầu tiên trong clipboard
            first_kp_val = None
            for kp in curve["keyframes"]:
                if kp["co"][0] == min_frame:
                    first_kp_val = kp["co"][1]
                    break
            if first_kp_val is None:
                first_kp_val = curve["keyframes"][0]["co"][1]

            # Đánh giá giá trị của đối tượng đích tại frame hiện tại trước khi dán
            fc_existing = action.fcurves.find(data_path=full_path, index=curve["array_index"])
            if fc_existing:
                v_target_end = fc_existing.evaluate(current_frame)
            else:
                # Nếu chưa có keyframe, lấy thuộc tính hiện tại của vật thể làm điểm kết nối
                try:
                    prop_val = getattr(constrained_target, curve["data_path"])
                    if hasattr(prop_val, "__len__"):
                        v_target_end = prop_val[curve["array_index"]]
                    else:
                        v_target_end = prop_val
                except Exception:
                    v_target_end = first_kp_val

            # Tính toán offset để triệt tiêu cú giật
            value_offset = v_target_end - first_kp_val

            # Tìm hoặc tạo F-Curve
            fc = action.fcurves.find(data_path=full_path, index=curve["array_index"])
            if not fc:
                fc = action.fcurves.new(data_path=full_path, index=curve["array_index"])

            # Chèn keyframes
            for kp in curve["keyframes"]:
                new_frame = kp["co"][0] + time_offset
                
                # Giá trị dán nối tiếp = giá trị gốc + value_offset
                new_val = kp["co"][1] + value_offset

                h_left_dx = kp["handle_left"][0] - kp["co"][0]
                h_left_dy = kp["handle_left"][1] - kp["co"][1]
                h_right_dx = kp["handle_right"][0] - kp["co"][0]
                h_right_dy = kp["handle_right"][1] - kp["co"][1]

                if self.mirror:
                    new_val = mirror_keyframe_value(curve["data_path"], curve["array_index"], new_val)
                    h_left_dy = mirror_keyframe_value(curve["data_path"], curve["array_index"], h_left_dy)
                    h_right_dy = mirror_keyframe_value(curve["data_path"], curve["array_index"], h_right_dy)

                new_kp = fc.keyframe_points.insert(frame=new_frame, value=new_val)
                new_kp.interpolation = kp["interpolation"]
                new_kp.handle_left = (new_frame + h_left_dx, new_val + h_left_dy)
                new_kp.handle_right = (new_frame + h_right_dx, new_val + h_right_dy)

        context.view_layer.update()
        self.report({'INFO'}, f"Đã dán nối tiếp (Paste Connect) thành công lên {constrained_target.name}!")
        return {'FINISHED'}
