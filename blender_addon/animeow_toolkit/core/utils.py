"""
utils.py — Animeow Toolkit
============================
Hàm tiện ích dùng chung cho nhiều module trong Toolkit.
Tập trung các hàm xử lý Pose Bone, Auto Keyframe, và Ma trận
để tránh trùng lặp code giữa các module con.
"""

import bpy
import math
from mathutils import Euler, Quaternion, Vector


def get_active_pose_bone(context):
    """Lấy xương đang được chọn hoạt động trong Pose Mode.

    Returns:
        Tuple (armature_obj, pose_bone) nếu đang ở Pose Mode,
        hoặc (None, None) nếu không.
    """
    if context.active_object and context.active_object.type == 'ARMATURE':
        if context.active_pose_bone:
            return context.active_object, context.active_pose_bone
    return None, None


def get_constrained_target(context):
    """Xác định đối tượng thực tế nhận constraint.

    Nếu đang ở Pose Mode -> trả về Active Pose Bone và Armature object.
    Nếu đang ở Object Mode -> trả về Active Object và None.

    Returns:
        Tuple (constrained_target, armature_obj)
    """
    owner_obj = context.active_object
    if owner_obj and owner_obj.type == 'ARMATURE' and context.active_pose_bone:
        return context.active_pose_bone, owner_obj
    return owner_obj, None


def insert_auto_keyframe(context, target, data_path, armature_obj=None):
    """Tự động chèn keyframe nếu tính năng Auto Keying đang bật.

    Hỗ trợ cả chế độ 'Only Insert Available' (chỉ chèn vào kênh đã có key).

    Args:
        context: Blender context.
        target: Object hoặc PoseBone cần chèn keyframe.
        data_path: Đường dẫn thuộc tính (ví dụ: "location", "rotation_euler").
        armature_obj: Nếu target là PoseBone, truyền Armature object vào đây.
    """
    ts = context.scene.tool_settings
    if not ts.use_keyframe_insert_auto:
        return

    anim_target = armature_obj if armature_obj else target
    pref_edit = context.preferences.edit

    # Nếu bật chế độ "Only Insert Available" (chỉ chèn vào kênh đã có key)
    if pref_edit.use_keyframe_insert_available:
        if not anim_target.animation_data or not anim_target.animation_data.action:
            return

        if armature_obj:
            full_path = f'pose.bones["{target.name}"].{data_path}'
        else:
            full_path = data_path

        has_fcurve = any(
            fc.data_path == full_path
            for fc in get_action_fcurves(anim_target.animation_data.action)
        )
        if not has_fcurve:
            return

    target.keyframe_insert(data_path=data_path)


def record_world_matrix(target, armature_obj=None):
    """Lấy ma trận thế giới (World Matrix) hiện tại của đối tượng hoặc Pose Bone.

    Args:
        target: Object hoặc PoseBone.
        armature_obj: Nếu target là PoseBone, truyền Armature object vào đây.

    Returns:
        mathutils.Matrix: Bản sao ma trận thế giới.
    """
    if armature_obj:
        return armature_obj.matrix_world @ target.matrix
    return target.matrix_world.copy()


def mirror_keyframe_value(data_path, array_index, value, mirror_axes=(True, False, False, False, True, True)):
    """Tính toán đảo ngược giá trị đối xứng (Mirroring) cho một kênh keyframe cụ thể.

    Args:
        data_path: Đường dẫn thuộc tính (ví dụ: "location", "rotation_euler").
        array_index: Vị trí kênh (0=X, 1=Y, 2=Z, v.v.).
        value: Giá trị gốc cần lật.
        mirror_axes: Tuple chứa trạng thái bật/tắt lật của 6 trục (tx, ty, tz, rx, ry, rz).

    Returns:
        float: Giá trị đã được đối xứng hóa.
    """
    tx, ty, tz, rx, ry, rz = mirror_axes

    # 1. Location
    if data_path.endswith("location"):
        if array_index == 0 and tx:
            return -value
        if array_index == 1 and ty:
            return -value
        if array_index == 2 and tz:
            return -value

    # 2. Rotation Euler
    elif data_path.endswith("rotation_euler"):
        if array_index == 0 and rx:
            return -value
        if array_index == 1 and ry:
            return -value
        if array_index == 2 and rz:
            return -value

    # 3. Rotation Quaternion (w, x, y, z)
    elif data_path.endswith("rotation_quaternion"):
        if array_index == 1 and rx:
            return -value
        if array_index == 2 and ry:
            return -value
        if array_index == 3 and rz:
            return -value

    # 4. Rotation Axis Angle (angle, x, y, z)
    elif data_path.endswith("rotation_axis_angle"):
        if array_index == 1 and rx:
            return -value
        if array_index == 2 and ry:
            return -value
        if array_index == 3 and rz:
            return -value

    return value


def get_action_fcurves(action):
    """Lấy tất cả các FCurves từ Action (hỗ trợ cả Layered Action, Slotted Action và Legacy Action)."""
    fcurves = []
    if not action:
        return fcurves
        
    # Hỗ trợ Legacy Action (Blender cũ hoặc NLA Legacy)
    if hasattr(action, "fcurves") and action.fcurves:
        fcurves.extend(action.fcurves)

    # Hỗ trợ Blender 4.3+ Slotted Action (bindings)
    if hasattr(action, "bindings"):
        for binding in action.bindings:
            if hasattr(binding, "fcurves") and binding.fcurves:
                fcurves.extend(binding.fcurves)
        
    # Hỗ trợ Layered Action (Blender 5.1/4.2+)
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        if hasattr(bag, "fcurves"):
                            fcurves.extend(bag.fcurves)
                elif hasattr(strip, "channelbag") and strip.channelbag:
                    bag = strip.channelbag
                    if hasattr(bag, "fcurves"):
                        fcurves.extend(bag.fcurves)
                        
    return fcurves


def ensure_fcurve(action, datablock, data_path, index):
    """Find or create an FCurve in action, compatible with Blender 3.x, 4.x, and 5.x."""
    if not action:
        return None

    # 1. Try new Blender 5.0+ method
    if hasattr(action, "fcurve_ensure_for_datablock"):
        try:
            return action.fcurve_ensure_for_datablock(datablock=datablock, data_path=data_path, index=index)
        except Exception:
            pass

    # 2. Legacy fallback
    if hasattr(action, "fcurves") and action.fcurves:
        try:
            fc = action.fcurves.find(data_path=data_path, index=index)
            if not fc:
                fc = action.fcurves.new(data_path=data_path, index=index)
            return fc
        except Exception:
            pass

    return None


def remove_action_fcurve(action, fcurve):
    """Safely remove an FCurve from its owner collection (legacy Action, Binding, or Channelbag)."""
    if not action or not fcurve:
        return False
        
    # 1. Try removing from action.fcurves directly
    if hasattr(action, "fcurves") and action.fcurves:
        try:
            action.fcurves.remove(fcurve)
            return True
        except Exception:
            pass
            
    # 2. Try removing from action.bindings or other collections
    if hasattr(action, "bindings"):
        for binding in action.bindings:
            if hasattr(binding, "fcurves") and binding.fcurves:
                try:
                    binding.fcurves.remove(fcurve)
                    return True
                except Exception:
                    pass

    # 3. Try removing from strips/channelbags (layered action)
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        if hasattr(bag, "fcurves") and bag.fcurves:
                            try:
                                bag.fcurves.remove(fcurve)
                                return True
                            except Exception:
                                pass
                elif hasattr(strip, "channelbag") and strip.channelbag:
                    bag = strip.channelbag
                    if hasattr(bag, "fcurves") and bag.fcurves:
                        try:
                            bag.fcurves.remove(fcurve)
                            return True
                        except Exception:
                            pass
                            
    # Fallback
    try:
        action.fcurves.remove(fcurve)
        return True
    except Exception:
        pass
        
    return False


def clean_fcurve_keyframes(fcurve, threshold=0.001, step=1, start_frame=1):
    """Đơn giản hóa F-curve bằng cách loại bỏ các keyframe thừa nằm trên đường thẳng,
    đồng thời bảo vệ các điểm cực trị (extremes) và giữ mốc keyframe theo step.
    Sử dụng thuật toán 2-Pass để đảm bảo độ chính xác tuyệt đối.
    """
    points = fcurve.keyframe_points
    if len(points) <= 2:
        return
        
    # --- PASS 1: XÓA CÁC FRAME LỆCH MỐC STEP MÀ KHÔNG PHẢI CỰC TRỊ ---
    if step > 1:
        indices_to_remove = []
        for i in range(1, len(points) - 1):
            prev_p = points[i - 1]
            curr_p = points[i]
            next_p = points[i + 1]
            
            t2 = curr_p.co[0]
            v1 = prev_p.co[1]
            v2 = curr_p.co[1]
            v3 = next_p.co[1]
            
            # Kiểm tra cực trị (đảo chiều chuyển động)
            is_extreme = (v2 - v1) * (v3 - v2) < 0
            if is_extreme:
                # Bảo vệ cực trị, không đưa vào danh sách xóa ở Pass 1
                continue
                
            # Kiểm tra mốc nhảy frame (Bake Step)
            frame_offset = int(t2) - start_frame
            if frame_offset % step != 0:
                indices_to_remove.append(i)
                
        # Thực hiện xóa ở Pass 1
        for idx in reversed(indices_to_remove):
            points.remove(points[idx])
        fcurve.update()
        
    # --- PASS 2: LỌC TUYẾN TÍNH TRÊN CÁC KEYFRAME CÒN LẠI (LUÔN GIỮ CỰC TRỊ) ---
    points = fcurve.keyframe_points
    if len(points) <= 2:
        return
        
    indices_to_remove = []
    i = 1
    while i < len(points) - 1:
        prev_p = points[i - 1]
        curr_p = points[i]
        next_p = points[i + 1]
        
        t1 = prev_p.co[0]
        t2 = curr_p.co[0]
        t3 = next_p.co[0]
        
        v1 = prev_p.co[1]
        v2 = curr_p.co[1]
        v3 = next_p.co[1]
        
        # Luôn bảo vệ cực trị khỏi bộ lọc tuyến tính
        is_extreme = (v2 - v1) * (v3 - v2) < 0
        if is_extreme:
            i += 1
            continue
            
        # Lọc tuyến tính thông thường
        if t3 - t1 == 0:
            val_interp = v1
        else:
            val_interp = v1 + (v3 - v1) * ((t2 - t1) / (t3 - t1))
            
        if abs(v2 - val_interp) < threshold:
            indices_to_remove.append(i)
            # Nhảy 2 bước để không tạo hiệu ứng chuỗi tuyến tính bị lọc dây chuyền gây méo dạng đồ thị
            i += 2
        else:
            i += 1
            
    # Thực hiện xóa ở Pass 2
    for idx in reversed(indices_to_remove):
        points.remove(points[idx])
        
    fcurve.update()


