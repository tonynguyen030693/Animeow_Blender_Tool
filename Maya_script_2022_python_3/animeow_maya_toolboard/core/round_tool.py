# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

def round_selected_values(precision=0, target='channel_box'):
    """
    Làm tròn giá trị thuộc tính trong Channel Box hoặc làm tròn các keyframe trong Graph Editor.
    
    precision: Số chữ số sau dấu phẩy (0 = số nguyên, 1 = 1 số thập phân, 2 = 2 số thập phân...)
    target: 'channel_box' (Làm tròn thuộc tính tĩnh) hoặc 'graph_editor' (Làm tròn các key được chọn)
    """
    selected_objects = cmds.ls(sl=True) or []
    
    # 1. Làm tròn Keyframe trong Graph Editor
    if target == 'graph_editor':
        # Kiểm tra xem có keyframe nào được chọn trực tiếp trong Graph Editor hay không
        selected_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        if selected_curves:
            key_count = 0
            for curve in selected_curves:
                indices = cmds.keyframe(curve, query=True, selected=True, indexValue=True) or []
                for idx in indices:
                    val_list = cmds.keyframe(curve, index=(idx, idx), query=True, valueChange=True)
                    if val_list:
                        val = val_list[0]
                        rounded_val = round(val, precision) if precision > 0 else int(round(val))
                        cmds.keyframe(curve, index=(idx, idx), valueChange=rounded_val)
                        key_count += 1
            print("[RoundTool] Đã làm tròn %d keyframe được chọn trong Graph Editor." % key_count)
            return True, "Đã làm tròn %d keyframe được chọn trong Graph Editor!" % key_count
        else:
            # Nếu không chọn key trực tiếp, làm tròn TOÀN BỘ keyframe của các channel được chọn trên vật thể
            if not selected_objects:
                return False, "Vui lòng chọn ít nhất một vật thể hoặc chọn key trong Graph Editor!"
                
            selected_channels = mel.eval("selectedChannels") or []
            if not selected_channels:
                selected_channels = cmds.listAttr(selected_objects[0], keyable=True) or []
                
            total_keys = 0
            for obj in selected_objects:
                for attr in selected_channels:
                    attr_path = "%s.%s" % (obj, attr)
                    if cmds.objExists(attr_path):
                        times = cmds.keyframe(obj, attribute=attr, query=True, timeChange=True) or []
                        for t in times:
                            val_list = cmds.keyframe(obj, attribute=attr, time=(t, t), query=True, valueChange=True)
                            if val_list:
                                val = val_list[0]
                                rounded_val = round(val, precision) if precision > 0 else int(round(val))
                                cmds.keyframe(obj, attribute=attr, time=(t, t), valueChange=rounded_val)
                                total_keys += 1
            print("[RoundTool] Đã làm tròn toàn bộ %d keyframe của các channel được chọn." % total_keys)
            return True, "Đã làm tròn toàn bộ %d keyframe của các channel được chọn!" % total_keys

    # 2. Làm tròn thuộc tính tĩnh trong Channel Box
    else:
        if not selected_objects:
            return False, "Vui lòng chọn ít nhất một vật thể trong Viewport!"
            
        selected_channels = mel.eval("selectedChannels") or []
        if not selected_channels:
            # Nếu không chọn channel cụ thể, lấy các thuộc tính keyable chính (translateX, translateY, translateZ, rotateX...)
            selected_channels = cmds.listAttr(selected_objects[0], keyable=True) or []
            
        attr_count = 0
        curr_frame = cmds.currentTime(q=True)
        
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path) and not cmds.getAttr(attr_path, lock=True):
                    val = cmds.getAttr(attr_path)
                    if isinstance(val, (int, float)):
                        rounded_val = round(val, precision) if precision > 0 else int(round(val))
                        try:
                            # Đặt giá trị thuộc tính tĩnh
                            cmds.setAttr(attr_path, rounded_val)
                            
                            # Nếu thuộc tính đó có keyframe tại frame hiện tại, cập nhật giá trị của keyframe luôn
                            if cmds.copyKey(obj, attribute=attr, time=(curr_frame, curr_frame)):
                                cmds.setKeyframe(obj, attribute=attr, time=curr_frame, value=rounded_val)
                            attr_count += 1
                        except Exception:
                            pass
                            
        print("[RoundTool] Đã làm tròn %d thuộc tính trong Channel Box." % attr_count)
        return True, "Đã làm tròn %d thuộc tính trong Channel Box thành công!" % attr_count
