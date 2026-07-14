# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

"""
Animeow Tween Machine - Module nội suy keyframe nội bộ.
Thay thế hoàn toàn Tween Machine bên ngoài.

Thuật toán: Nội suy tuyến tính (LERP) giữa keyframe trước và sau
    NewValue = PrevValue + (NextValue - PrevValue) * tween_percent

Trong đó tween_percent:
    0.0 = giá trị của keyframe trước (previous)
    0.5 = chính giữa 2 keyframe
    1.0 = giá trị của keyframe sau (next)
"""

import maya.cmds as cmds


def get_tweened_attrs(objects=None):
    """Lấy danh sách các thuộc tính có keyframe trên các đối tượng đang chọn.
    
    Args:
        objects: Danh sách đối tượng. Nếu None, lấy đối tượng đang chọn.
    
    Returns:
        list: Danh sách chuỗi 'object.attribute' có animation curve.
    """
    if objects is None:
        objects = cmds.ls(sl=True) or []
    
    if not objects:
        return []
    
    attrs = []
    for obj in objects:
        # Lấy tất cả animation curve kết nối tới object
        anim_curves = cmds.listConnections(obj, type='animCurve') or []
        if not anim_curves:
            continue
        
        for curve in anim_curves:
            # Lấy tên thuộc tính đầu ra của curve đang kết nối tới
            connections = cmds.listConnections(
                curve + '.output', plugs=True, destination=True
            ) or []
            for conn in connections:
                attrs.append(conn)
    
    # Loại bỏ trùng lặp và giữ thứ tự
    seen = set()
    unique_attrs = []
    for a in attrs:
        if a not in seen:
            seen.add(a)
            unique_attrs.append(a)
    
    return unique_attrs


def tween(tween_percent=0.5, objects=None):
    """Thực hiện nội suy keyframe tại frame hiện tại.
    
    Tính giá trị mới dựa trên tỷ lệ nội suy giữa keyframe phía trước
    và keyframe phía sau, rồi đặt key mới tại frame hiện tại.
    
    Args:
        tween_percent (float): Tỷ lệ nội suy từ 0.0 (prev key) đến 1.0 (next key).
                               Giá trị 0.5 = chính giữa 2 keyframe.
        objects (list, optional): Danh sách đối tượng. Nếu None, lấy selection.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if objects is None:
        objects = cmds.ls(sl=True) or []
    
    if not objects:
        return False, "Vui lòng chọn ít nhất một đối tượng có keyframe."
    
    current_time = cmds.currentTime(query=True)
    
    total_keyed = 0
    total_skipped = 0
    
    for obj in objects:
        # Lấy trực tiếp toàn bộ animCurves của đối tượng này
        anim_curves = cmds.keyframe(obj, query=True, name=True) or []
        
        # Tìm các thuộc tính (plugs) được kết nối từ các animCurves này
        attrs_to_tween = []
        for curve in anim_curves:
            plugs = cmds.listConnections(curve + '.output', plugs=True, destination=True) or []
            for plug in plugs:
                if plug.startswith(obj + '.'):
                    attrs_to_tween.append(plug)
                    
        # Loại bỏ trùng lặp
        attrs_to_tween = list(set(attrs_to_tween))
        
        for full_attr in attrs_to_tween:
            # Tìm keyframe trước và sau frame hiện tại
            prev_time = cmds.findKeyframe(
                full_attr, 
                time=(current_time, current_time), 
                which='previous'
            )
            next_time = cmds.findKeyframe(
                full_attr, 
                time=(current_time, current_time), 
                which='next'
            )
            
            # Bỏ qua nếu không tìm được key trước/sau
            # hoặc nếu prev == next (chỉ có 1 key duy nhất)
            if prev_time is None or next_time is None:
                total_skipped += 1
                continue
            
            if abs(prev_time - next_time) < 0.001:
                total_skipped += 1
                continue
            
            # Lấy giá trị tại keyframe trước và sau
            prev_vals = cmds.keyframe(
                full_attr, query=True,
                time=(prev_time, prev_time),
                valueChange=True
            )
            next_vals = cmds.keyframe(
                full_attr, query=True,
                time=(next_time, next_time),
                valueChange=True
            )
            
            if not prev_vals or not next_vals:
                total_skipped += 1
                continue
            
            prev_val = prev_vals[0]
            next_val = next_vals[0]
            
            # Tính giá trị nội suy LERP
            tweened_val = prev_val + (next_val - prev_val) * tween_percent
            
            # Đặt keyframe mới tại frame hiện tại
            cmds.setKeyframe(full_attr, time=current_time, value=tweened_val)
            total_keyed += 1
    
    if total_keyed == 0:
        return False, "Không tìm thấy thuộc tính nào có keyframe trước/sau frame hiện tại."
    
    return True, "Tween xong: %d thuộc tính tại frame %d (%.0f%%)" % (
        total_keyed, int(current_time), tween_percent * 100
    )


def tween_interactive(tween_percent=0.5):
    """Hàm wrapper bọc trong undo chunk để animator có thể Ctrl+Z hoàn tác.
    
    Args:
        tween_percent (float): Tỷ lệ nội suy từ 0.0 đến 1.0.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    cmds.undoInfo(openChunk=True)
    try:
        result = tween(tween_percent)
    except Exception as e:
        result = (False, "Lỗi khi tween: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)
    
    return result
