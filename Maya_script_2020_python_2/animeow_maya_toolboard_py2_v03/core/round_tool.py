# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

def get_selected_channels(obj):
    """Lay danh sach cac channel dang chon trong Channel Box bang cach truy van truc tiep widget mainChannelBox"""
    chans = []
    try:
        # Lay ten Channel Box chinh cua Maya
        gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
        if not gChannelBoxName:
            gChannelBoxName = "mainChannelBox"
            
        if gChannelBoxName and cmds.channelBox(gChannelBoxName, exists=True):
            sma = cmds.channelBox(gChannelBoxName, query=True, sma=True) or []
            ssa = cmds.channelBox(gChannelBoxName, query=True, ssa=True) or []
            sha = cmds.channelBox(gChannelBoxName, query=True, sha=True) or []
            
            # Gop va loai bo trung lap
            raw_chans = list(set(sma + ssa + sha))
            # Dam bao cac channel hop le
            for c in raw_chans:
                if c and hasattr(c, 'lower'):
                    chans.append(str(c))
    except Exception:
        chans = []
        
    # Fallback: neu thuc su khong co channel nao duoc boi xanh thi moi lay toan bo thuoc tinh keyable
    if not chans and obj and cmds.objExists(obj):
        chans = cmds.listAttr(obj, keyable=True) or []
        
    return chans

def round_selected_values(precision=0, target='channel_box', channels=None):
    """
    Lam tron gia tri thuoc tinh trong Channel Box hoac lam tron cac keyframe.
    
    precision: So chu so sau dau phay (0 = so nguyen, 1 = 1 so thap phan, 2 = 2 so thap phan, -1 = reset ve 0)
    target: 'channel_box', 'graph_editor', 'current_frame', 'all_keyframes'
    channels: Danh sach thuoc tinh chi dinh (vi du: ['translateX', 'translateY', 'translateZ'])
    """
    selected_objects = cmds.ls(sl=True) or []
    curr_frame = cmds.currentTime(q=True)
    
    # 1. Chi lam tron cac keyframe duoc chon thu cong trong Graph Editor
    if target == 'graph_editor':
        selected_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        if channels:
            # Loc cac curve tuong ung voi channel mong muon
            selected_curves = [c for c in selected_curves if any(ch.lower() in c.lower() for ch in channels)]
            
        if not selected_curves:
            return False, "Vui long quet chon it nhat mot keyframe cua thuoc tinh tuong ung trong Graph Editor!"
            
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
        action_name = "dat ve 0" if precision == -1 else "lam tron"
        return True, "Da %s %d keyframe duoc chon trong Graph Editor!" % (action_name, key_count)

    # 2. Chi lam tron keyframe tai dung frame hien tai cua timeline
    elif target == 'current_frame':
        if not selected_objects:
            return False, "Vui long chon nhat mot vat the!"
            
        selected_channels = channels if channels is not None else get_selected_channels(selected_objects[0])
            
        key_count = 0
        for obj in selected_objects:
            for attr in selected_channels:
                attr_path = "%s.%s" % (obj, attr)
                if cmds.objExists(attr_path):
                    # Truy van xem tai frame hien tai co keyframe khong
                    val_list = cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), query=True, valueChange=True)
                    if val_list is not None and val_list != []:
                        val = val_list[0] if isinstance(val_list, list) else val_list
                        rounded_val = 0 if precision == -1 else (round(val, precision) if precision > 0 else int(round(val)))
                        cmds.keyframe(obj, attribute=attr, time=(curr_frame, curr_frame), valueChange=rounded_val)
                        key_count += 1
        if key_count > 0:
            action_name = "dat ve 0" if precision == -1 else "lam tron"
            return True, "Da %s %d keyframe tai frame %d!" % (action_name, key_count, curr_frame)
        else:
            return False, "Khong tim thay keyframe nao tai frame hien tai (%d) cho cac channel duoc chon." % curr_frame

    # 3. Lam tron toan bo keyframe cua cac channel duoc chon tren timeline
    elif target == 'all_keyframes':
        if not selected_objects:
            return False, "Vui long chon it nhat mot vat the!"
            
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
        action_name = "dat ve 0" if precision == -1 else "lam tron"
        return True, "Da %s toan bo %d keyframe cua cac channel duoc chon!" % (action_name, total_keys)

    # 4. Lam tron thuoc tinh tinh trong Channel Box
    else:
        if not selected_objects:
            return False, "Vui long chon it nhat mot vat the trong Viewport!"
            
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
        action_name = "dat ve 0" if precision == -1 else "lam tron"
        return True, "Da %s %d thuoc tinh trong Channel Box thanh cong!" % (action_name, attr_count)
