# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

"""
Animeow Tween Machine - Module noi suy keyframe noi bo.
Thay the hoan toan Tween Machine ben ngoai.

Thuat toan: Noi suy tuyen tinh (LERP) giua keyframe truoc va sau
    NewValue = PrevValue + (NextValue - PrevValue) * tween_percent

Trong do tween_percent:
    0.0 = gia tri cua keyframe truoc (previous)
    0.5 = chinh giua 2 keyframe
    1.0 = gia tri cua keyframe sau (next)
"""

import maya.cmds as cmds


def get_tweened_attrs(objects=None):
    """Lay danh sach cac thuoc tinh co keyframe tren cac doi tuong dang chon.
    
    Args:
        objects: Danh sach doi tuong. Neu None, lay doi tuong dang chon.
    
    Returns:
        list: Danh sach chuoi 'object.attribute' co animation curve.
    """
    if objects is None:
        objects = cmds.ls(sl=True) or []
    
    if not objects:
        return []
    
    attrs = []
    for obj in objects:
        # Lay tat ca animation curve ket noi toi object
        anim_curves = cmds.listConnections(obj, type='animCurve') or []
        if not anim_curves:
            continue
        
        for curve in anim_curves:
            # Lay ten thuoc tinh dau ra cua curve dang ket noi toi
            connections = cmds.listConnections(
                curve + '.output', plugs=True, destination=True
            ) or []
            for conn in connections:
                attrs.append(conn)
    
    # Loai bo trung lap va giu thu tu
    seen = set()
    unique_attrs = []
    for a in attrs:
        if a not in seen:
            seen.add(a)
            unique_attrs.append(a)
    
    return unique_attrs


def tween(tween_percent=0.5, objects=None):
    """Thuc hien noi suy keyframe tai frame hien tai.
    
    Tinh gia tri moi dua tren ty le noi suy giua keyframe phia truoc
    va keyframe phia sau, roi dat key moi tai frame hien tai.
    
    Args:
        tween_percent (float): Ty le noi suy tu 0.0 (prev key) den 1.0 (next key).
                               Gia tri 0.5 = chinh giua 2 keyframe.
        objects (list, optional): Danh sach doi tuong. Neu None, lay selection.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if objects is None:
        objects = cmds.ls(sl=True) or []
    
    if not objects:
        return False, "Vui long chon it nhat mot doi tuong co keyframe."
    
    current_time = cmds.currentTime(query=True)
    
    total_keyed = 0
    total_skipped = 0
    
    for obj in objects:
        # Lay truc tiep toan bo animCurves cua doi tuong nay
        anim_curves = cmds.keyframe(obj, query=True, name=True) or []
        
        # Tim cac thuoc tinh (plugs) duoc ket noi tu cac animCurves nay
        attrs_to_tween = []
        for curve in anim_curves:
            plugs = cmds.listConnections(curve + '.output', plugs=True, destination=True) or []
            for plug in plugs:
                if plug.startswith(obj + '.'):
                    attrs_to_tween.append(plug)
                    
        # Loai bo trung lap
        attrs_to_tween = list(set(attrs_to_tween))
        
        for full_attr in attrs_to_tween:
            current_val = cmds.getAttr(full_attr)
            
            # Tim keyframe truoc
            prev_time = cmds.findKeyframe(
                full_attr, 
                time=(current_time, current_time), 
                which='previous'
            )
            prev_val = current_val
            if prev_time is not None and abs(prev_time - current_time) > 0.001:
                prev_vals = cmds.keyframe(
                    full_attr, query=True,
                    time=(prev_time, prev_time),
                    valueChange=True
                )
                if prev_vals:
                    prev_val = prev_vals[0]
            
            # Tim keyframe sau
            next_time = cmds.findKeyframe(
                full_attr, 
                time=(current_time, current_time), 
                which='next'
            )
            next_val = current_val
            if next_time is not None and abs(next_time - current_time) > 0.001:
                next_vals = cmds.keyframe(
                    full_attr, query=True,
                    time=(next_time, next_time),
                    valueChange=True
                )
                if next_vals:
                    next_val = next_vals[0]
            
            # Tinh gia tri noi suy LERP
            tweened_val = prev_val + (next_val - prev_val) * tween_percent
            
            # Gan truc tiep vao thuoc tinh de cap nhat viewport lap tuc
            try:
                cmds.setAttr(full_attr, tweened_val)
            except Exception:
                pass
                
            # Dat keyframe moi tai frame hien tai
            cmds.setKeyframe(full_attr, time=current_time, value=tweened_val)
            total_keyed += 1
    
    if total_keyed == 0:
        return False, "Khong tim thay thuoc tinh nao co keyframe truoc/sau frame hien tai."
    
    return True, "Tween xong: %d thuoc tinh tai frame %d (%.0f%%)" % (
        total_keyed, int(current_time), tween_percent * 100
    )


def tween_interactive(tween_percent=0.5):
    """Ham wrapper boc trong undo chunk de animator co the Ctrl+Z hoan tac.
    
    Args:
        tween_percent (float): Ty le noi suy tu 0.0 den 1.0.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    cmds.undoInfo(openChunk=True)
    try:
        result = tween(tween_percent)
    except Exception as e:
        result = (False, "Loi khi tween: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)
    
    return result
