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
            for fc in anim_target.animation_data.action.fcurves
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


def mirror_keyframe_value(data_path, array_index, value):
    """Tính toán đảo ngược giá trị đối xứng (Mirroring) cho một kênh keyframe cụ thể.

    Args:
        data_path: Đường dẫn thuộc tính (ví dụ: "location", "rotation_euler").
        array_index: Vị trí kênh (0=X, 1=Y, 2=Z, v.v.).
        value: Giá trị gốc cần lật.

    Returns:
        float: Giá trị đã được đối xứng hóa.
    """
    # 1. Location: Đảo ngược trục X (array_index == 0)
    if data_path.endswith("location") and array_index == 0:
        return -value

    # 2. Rotation Euler: Đảo ngược trục Y và Z (array_index == 1 hoặc 2)
    elif data_path.endswith("rotation_euler") and array_index in (1, 2):
        return -value

    # 3. Rotation Quaternion: Đảo ngược Y và Z (chỉ số 2 và 3 trong [w, x, y, z])
    elif data_path.endswith("rotation_quaternion") and array_index in (2, 3):
        return -value

    # 4. Rotation Axis Angle: Đảo ngược trục Y và Z của Axis (chỉ số 2 và 3 trong [angle, x, y, z])
    elif data_path.endswith("rotation_axis_angle") and array_index in (2, 3):
        return -value

    return value


def get_action_fcurves(action):
    """Lấy tất cả các FCurves từ Action (hỗ trợ cả Layered Action và Legacy Action)."""
    fcurves = []
    if not action:
        return fcurves
        
    # Hỗ trợ Legacy Action (Blender cũ hoặc NLA Legacy)
    if hasattr(action, "fcurves") and action.fcurves:
        fcurves.extend(action.fcurves)
        
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


def clean_fcurve_keyframes(fcurve, threshold=0.001):
    """Đơn giản hóa F-curve bằng cách loại bỏ các keyframe thừa nằm trên đường thẳng."""
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
        
        if t3 - t1 == 0:
            val_interp = v1
        else:
            val_interp = v1 + (v3 - v1) * ((t2 - t1) / (t3 - t1))
            
        if abs(v2 - val_interp) < threshold:
            indices_to_remove.append(i)
            # Nhảy sang điểm kế tiếp để không bị trùng lặp khoảng kiểm tra
            i += 2
        else:
            i += 1
            
    # Xóa các điểm từ dưới lên trên để không làm lệch chỉ mục (index)
    for idx in reversed(indices_to_remove):
        points.remove(points[idx])
        
    fcurve.update()


