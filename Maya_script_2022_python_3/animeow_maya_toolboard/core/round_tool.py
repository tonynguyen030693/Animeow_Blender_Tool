# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

def get_selected_channels(obj):
    """Lấy danh sách các channel đang chọn trong Channel Box bằng cách truy vấn trực tiếp widget mainChannelBox"""
    chans = []
    try:
        # Lấy tên Channel Box chính của Maya
        gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
        if not gChannelBoxName:
            gChannelBoxName = "mainChannelBox"
            
        if gChannelBoxName and cmds.channelBox(gChannelBoxName, exists=True):
            sma = cmds.channelBox(gChannelBoxName, query=True, sma=True) or []
            ssa = cmds.channelBox(gChannelBoxName, query=True, ssa=True) or []
            sha = cmds.channelBox(gChannelBoxName, query=True, sha=True) or []
            
            # Gộp và loại bỏ trùng lặp
            raw_chans = list(set(sma + ssa + sha))
            # Đảm bảo các channel hợp lệ
            for c in raw_chans:
                if c and hasattr(c, 'lower'):
                    chans.append(str(c))
    except Exception:
        chans = []
        
    # Fallback: nếu thực sự không có channel nào được bôi xanh thì mới lấy toàn bộ thuộc tính keyable
    if not chans and obj and cmds.objExists(obj):
        chans = cmds.listAttr(obj, keyable=True) or []
        
    return chans

def round_selected_values(precision=0, target='channel_box', channels=None):
    """
    Làm tròn giá trị thuộc tính trong Channel Box hoặc làm tròn các keyframe.
    
    precision: Số chữ số sau dấu phẩy (0 = số nguyên, 1 = 1 số thập phân, 2 = 2 số thập phân, -1 = reset về 0)
    target: 'channel_box', 'graph_editor', 'current_frame', 'all_keyframes'
    channels: Danh sách thuộc tính chỉ định (ví dụ: ['translateX', 'translateY', 'translateZ'])
    """
    selected_objects = cmds.ls(sl=True) or []
    curr_frame = cmds.currentTime(q=True)
    
    # 1. Chỉ làm tròn các keyframe được chọn thủ công trong Graph Editor
    if target == 'graph_editor':
        selected_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        if channels:
            # Lọc các curve tương ứng với channel mong muốn
            selected_curves = [c for c in selected_curves if any(ch.lower() in c.lower() for ch in channels)]
            
        if not selected_curves:
            return False, "Vui lòng quét chọn ít nhất một keyframe của thuộc tính tương ứng trong Graph Editor!"
            
        key_count = 0
        for curve in selected_curves:
            indices = cmds.keyframe(curve, query=True, selected=True, indexValue=True) or []
            if isinstance(indices, (int, float)):
                indices = [indices]
            for idx in indices:
                val_list = cmds.keyframe(curve, index=(idx, idx), query=True, valueChange=True)
                if val_list is not None and val_list != []:
                    val = val_list[0] if isinstance(val_list, list) else val_list
                    rounded_val = 0 if precision == -1 else (round(val, precision) if precision > 0 else int(round(val)))
                    cmds.keyframe(curve, index=(idx, idx), valueChange=rounded_val)
                    key_count += 1
        action_name = "đặt về 0" if precision == -1 else "làm tròn"
        return True, "Đã %s %d keyframe được chọn trong Graph Editor!" % (action_name, key_count)

    # 2. Chỉ làm tròn keyframe tại đúng frame hiện tại của timeline
    elif target == 'current_frame':
        if not selected_objects:
            return False, "Vui lòng chọn nhất một vật thể!"
            
        selected_channels = channels if channels is not None else get_selected_channels(selected_objects[0])
            
        key_count = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path):
                    # Truy vấn xem tại frame hiện tại có keyframe không
                    val_list = cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), query=True, valueChange=True)
                    if val_list is not None and val_list != []:
                        val = val_list[0] if isinstance(val_list, list) else val_list
                        rounded_val = 0 if precision == -1 else (round(val, precision) if precision > 0 else int(round(val)))
                        cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), valueChange=rounded_val)
                        key_count += 1
        if key_count > 0:
            action_name = "đặt về 0" if precision == -1 else "làm tròn"
            return True, "Đã %s %d keyframe tại frame %d!" % (action_name, key_count, curr_frame)
        else:
            return False, "Không tìm thấy keyframe nào tại frame hiện tại (%d) cho các channel được chọn." % curr_frame

    # 3. Làm tròn toàn bộ keyframe của các channel được chọn trên timeline
    elif target == 'all_keyframes':
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể!"
            
        selected_channels = channels if channels is not None else get_selected_channels(selected_objects[0])
            
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
                            rounded_val = 0 if precision == -1 else (round(val, precision) if precision > 0 else int(round(val)))
                            cmds.keyframe(obj, attribute=attr, time=(t, t), valueChange=rounded_val)
                            total_keys += 1
        action_name = "đặt về 0" if precision == -1 else "làm tròn"
        return True, "Đã %s toàn bộ %d keyframe của các channel được chọn!" % (action_name, total_keys)

    # 4. Làm tròn thuộc tính tĩnh trong Channel Box
    else:
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể trong Viewport!"
            
        selected_channels = channels if channels is not None else get_selected_channels(selected_objects[0])
            
        attr_count = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path) and not cmds.getAttr(attr_path, lock=True):
                    val = cmds.getAttr(attr_path)
                    if isinstance(val, (int, float)):
                        rounded_val = 0 if precision == -1 else (round(val, precision) if precision > 0 else int(round(val)))
                        try:
                            cmds.setAttr(attr_path, rounded_val)
                            if cmds.copyKey(obj, attribute=attr, time=(curr_frame, curr_frame)):
                                cmds.setKeyframe(obj, attribute=attr, time=curr_frame, value=rounded_val)
                            attr_count += 1
                        except Exception:
                            pass
        action_name = "đặt về 0" if precision == -1 else "làm tròn"
        return True, "Đã %s %d thuộc tính trong Channel Box thành công!" % (action_name, attr_count)
