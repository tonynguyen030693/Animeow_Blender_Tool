# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

def get_selected_channels(obj):
    """Lấy danh sách các channel đang chọn trong Channel Box, nếu không có thì lấy tất cả keyable channels"""
    try:
        chans = mel.eval("selectedChannels")
    except Exception:
        chans = []
        
    if not chans:
        chans = []
    elif hasattr(chans, 'lower'): # Nếu chỉ có 1 channel chọn, mel.eval có thể trả về string đơn lẻ
        chans = [chans]
    elif not isinstance(chans, list):
        chans = []
        
    if not chans and obj and cmds.objExists(obj):
        chans = cmds.listAttr(obj, keyable=True) or []
        
    return chans

def round_selected_values(precision=0, target='channel_box'):
    """
    Làm tròn giá trị thuộc tính trong Channel Box hoặc làm tròn các keyframe.
    
    precision: Số chữ số sau dấu phẩy (0 = số nguyên, 1 = 1 số thập phân, 2 = 2 số thập phân...)
    target: 'channel_box', 'graph_editor', 'current_frame', 'all_keyframes'
    """
    selected_objects = cmds.ls(sl=True) or []
    curr_frame = cmds.currentTime(q=True)
    
    # 1. Chỉ làm tròn các keyframe được chọn thủ công trong Graph Editor
    if target == 'graph_editor':
        selected_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        if not selected_curves:
            return False, "Vui lòng quét chọn ít nhất một keyframe trong Graph Editor!"
            
        key_count = 0
        for curve in selected_curves:
            indices = cmds.keyframe(curve, query=True, selected=True, indexValue=True) or []
            if isinstance(indices, (int, float)):
                indices = [indices]
            for idx in indices:
                val_list = cmds.keyframe(curve, index=(idx, idx), query=True, valueChange=True)
                if val_list is not None and val_list != []:
                    val = val_list[0] if isinstance(val_list, list) else val_list
                    rounded_val = round(val, precision) if precision > 0 else int(round(val))
                    cmds.keyframe(curve, index=(idx, idx), valueChange=rounded_val)
                    key_count += 1
        return True, "Đã làm tròn %d keyframe được chọn trong Graph Editor!" % key_count

    # 2. Chỉ làm tròn keyframe tại đúng frame hiện tại của timeline
    elif target == 'current_frame':
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể!"
            
        selected_channels = get_selected_channels(selected_objects[0])
            
        key_count = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path):
                    # Truy vấn xem tại frame hiện tại có keyframe không
                    val_list = cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), query=True, valueChange=True)
                    if val_list is not None and val_list != []:
                        val = val_list[0] if isinstance(val_list, list) else val_list
                        rounded_val = round(val, precision) if precision > 0 else int(round(val))
                        cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), valueChange=rounded_val)
                        key_count += 1
        if key_count > 0:
            return True, "Đã làm tròn %d keyframe tại frame %d!" % (key_count, curr_frame)
        else:
            return False, "Không tìm thấy keyframe nào tại frame hiện tại (%d) cho các channel được chọn." % curr_frame

    # 3. Làm tròn toàn bộ keyframe của các channel được chọn trên timeline
    elif target == 'all_keyframes':
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể!"
            
        selected_channels = get_selected_channels(selected_objects[0])
            
        total_keys = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path):
                    times = cmds.keyframe(obj, attribute=attr, query=True, timeChange=True) or []
                    if isinstance(times, (int, float)):
                        times = [times]
                    for t in times:
                        val_list = cmds.keyframe(obj, attribute=attr, time=(t, t), query=True, valueChange=True)
                        if val_list is not None and val_list != []:
                            val = val_list[0] if isinstance(val_list, list) else val_list
                            rounded_val = round(val, precision) if precision > 0 else int(round(val))
                            cmds.keyframe(obj, attribute=attr, time=(t, t), valueChange=rounded_val)
                            total_keys += 1
        return True, "Đã làm tròn toàn bộ %d keyframe của các channel được chọn!" % total_keys

    # 4. Làm tròn thuộc tính tĩnh trong Channel Box
    else:
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể trong Viewport!"
            
        selected_channels = get_selected_channels(selected_objects[0])
            
        attr_count = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path) and not cmds.getAttr(attr_path, lock=True):
                    val = cmds.getAttr(attr_path)
                    if isinstance(val, (int, float)):
                        rounded_val = round(val, precision) if precision > 0 else int(round(val))
                        try:
                            cmds.setAttr(attr_path, rounded_val)
                            if cmds.copyKey(obj, attribute=attr, time=(curr_frame, curr_frame)):
                                cmds.setKeyframe(obj, attribute=attr, time=curr_frame, value=rounded_val)
                            attr_count += 1
                        except Exception:
                            pass
        return True, "Đã làm tròn %d thuộc tính trong Channel Box thành công!" % attr_count
