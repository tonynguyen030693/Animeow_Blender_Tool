# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

def find_counterpart(obj, left_patterns=None, right_patterns=None):
    """
    Tim doi tuong doi xung cua obj va xac dinh ben doi xung (left/right/center).
    Ho tro ca namespace.
    """
    if not cmds.objExists(obj):
        return None, 'center'
        
    if not left_patterns or not right_patterns:
        left_patterns = ['_L', 'L_', '_l', 'l_', '_left', 'left_', 'Left']
        right_patterns = ['_R', 'R_', '_r', 'r_', '_right', 'right_', 'Right']
    
    parts = obj.split(":")
    short_name = parts[-1]
    ns_prefix = ":".join(parts[:-1]) + ":" if len(parts) > 1 else ""
    
    for lp, rp in zip(left_patterns, right_patterns):
        if short_name.endswith(lp):
            candidate = ns_prefix + short_name[:-len(lp)] + rp
            if cmds.objExists(candidate):
                return candidate, 'left'
                
        if short_name.startswith(lp):
            candidate = ns_prefix + rp + short_name[len(lp):]
            if cmds.objExists(candidate):
                return candidate, 'left'
                
        if short_name.endswith(rp):
            candidate = ns_prefix + short_name[:-len(rp)] + lp
            if cmds.objExists(candidate):
                return candidate, 'right'
                
        if short_name.startswith(rp):
            candidate = ns_prefix + lp + short_name[len(rp):]
            if cmds.objExists(candidate):
                return candidate, 'right'
                
    return obj, 'center'

def execute_mirror(objects, mode='swap', time_range=None, invert_map=None, left_patterns=None, right_patterns=None):
    """
    Thuc hien doi xung chuyen dong (Mirror Animation).
    """
    if not objects:
        return False, "Khong co doi tuong nao duoc chon!"
        
    if not invert_map:
        invert_map = {
            'translateX': True, 'translateY': False, 'translateZ': False,
            'rotateX': False, 'rotateY': True, 'rotateZ': True
        }
        
    if time_range:
        start_f, end_f = time_range
        time_arg = (start_f, end_f)
    else:
        start_f = cmds.playbackOptions(q=True, minTime=True)
        end_f = cmds.playbackOptions(q=True, maxTime=True)
        time_arg = (start_f, end_f)

    pairs = []
    processed = set()
    
    for obj in objects:
        if obj in processed:
            continue
            
        counterpart, side = find_counterpart(obj, left_patterns, right_patterns)
        
        if side == 'left':
            pairs.append((obj, counterpart, 'side'))
            processed.add(obj)
            processed.add(counterpart)
        elif side == 'right':
            pairs.append((counterpart, obj, 'side'))
            processed.add(obj)
            processed.add(counterpart)
        else:
            pairs.append((obj, obj, 'center'))
            processed.add(obj)
            
    if not pairs:
        return False, "Khong xac dinh duoc cap doi tuong doi xung nao!"

    temp_node = cmds.group(empty=True, name="animeow_temp_mirror_holder")
    
    success_count = 0
    try:
        for left_obj, right_obj, pair_type in pairs:
            keyable_attrs = cmds.listAttr(left_obj, keyable=True) or []
            
            for attr in keyable_attrs:
                if not any(t in attr for t in ['translate', 'rotate', 'scale', 'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']):
                    continue
                    
                should_invert = invert_map.get(attr, False)
                
                left_attr = "%s.%s" % (left_obj, attr)
                right_attr = "%s.%s" % (right_obj, attr)
                
                # Ensure attribute exists on temp node
                if not cmds.attributeQuery(attr, node=temp_node, exists=True):
                    cmds.addAttr(temp_node, longName=attr, attributeType='double')
                
                if pair_type == 'side':
                    if mode == 'swap':
                        if cmds.copyKey(left_obj, attribute=attr, time=time_arg):
                            cmds.pasteKey(temp_node, attribute=attr, option="replace")
                        else:
                            cmds.cutKey(temp_node, attribute=attr, time=time_arg, clear=True)
                            
                        if cmds.copyKey(right_obj, attribute=attr, time=time_arg):
                            cmds.pasteKey(left_obj, attribute=attr, option="replace")
                            if should_invert:
                                cmds.scaleKey(left_obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                        else:
                            cmds.cutKey(left_obj, attribute=attr, time=time_arg, clear=True)
                            
                        if cmds.copyKey(temp_node, attribute=attr, time=time_arg):
                            cmds.pasteKey(right_obj, attribute=attr, option="replace")
                            if should_invert:
                                cmds.scaleKey(right_obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                        else:
                            cmds.cutKey(right_obj, attribute=attr, time=time_arg, clear=True)
                            
                    elif mode == 'left_to_right':
                        if cmds.copyKey(left_obj, attribute=attr, time=time_arg):
                            cmds.pasteKey(right_obj, attribute=attr, option="replace")
                            if should_invert:
                                cmds.scaleKey(right_obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                        else:
                            cmds.cutKey(right_obj, attribute=attr, time=time_arg, clear=True)
                            
                    elif mode == 'right_to_left':
                        if cmds.copyKey(right_obj, attribute=attr, time=time_arg):
                            cmds.pasteKey(left_obj, attribute=attr, option="replace")
                            if should_invert:
                                cmds.scaleKey(left_obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                        else:
                            cmds.cutKey(left_obj, attribute=attr, time=time_arg, clear=True)
                            
                    elif mode == 'flip_selected':
                        for obj in [left_obj, right_obj]:
                            if should_invert and cmds.copyKey(obj, attribute=attr, time=time_arg):
                                cmds.scaleKey(obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                                
                else:
                    if should_invert and cmds.copyKey(left_obj, attribute=attr, time=time_arg):
                        cmds.scaleKey(left_obj, attribute=attr, time=time_arg, valueScale=-1.0, valuePivot=0.0)
                        
            success_count += 1
    finally:
        if cmds.objExists(temp_node):
            try:
                cmds.delete(temp_node)
            except Exception:
                pass
                
    return True, "Da thuc hien Mirror thanh cong cho %d cap doi tuong!" % success_count
