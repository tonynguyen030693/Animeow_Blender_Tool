# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
pkg_name = __name__.split('.')[0]
world_bake = __import__(pkg_name + ".core.world_bake", fromlist=[
    "smart_bake_object", "get_incoming_constraints", "get_pair_blend_nodes", 
    "parent_to_animeow_group", "clean_empty_animeow_group"
])
smart_bake_object = world_bake.smart_bake_object
get_incoming_constraints = world_bake.get_incoming_constraints
get_pair_blend_nodes = world_bake.get_pair_blend_nodes
parent_to_animeow_group = world_bake.parent_to_animeow_group
clean_empty_animeow_group = world_bake.clean_empty_animeow_group

PREFIX_LOC = "Anm_loc_pivot_"
PREFIX_HELPER = "Anm_loc_pivot_helper_"

def get_clean_name(name):
    short_name = name.split("|")[-1]
    return short_name.replace(":", "_")

def create_temp_locator(controls, custom_pivot=None):
    """
    Tao Temp Locator lam tam xoay tam thoi, va tao cac helper locator tuong ung duoi no.
    """
    if not isinstance(controls, list):
        controls = [controls]
        
    valid_controls = [c for c in controls if cmds.objExists(c)]
    if not valid_controls:
        raise RuntimeError("Khong tim thay cac control hop le!")
        
    # 1. Tinh toan vi tri tam xoay (Rotate Pivot)
    custom_objs = []
    if custom_pivot:
        custom_objs = [o.strip() for o in custom_pivot.split(",") if o.strip() and cmds.objExists(o.strip())]
        
    if custom_objs:
        pos = [0.0, 0.0, 0.0]
        for obj in custom_objs:
            rp_pos = cmds.xform(obj, q=True, ws=True, rotatePivot=True)
            pos[0] += rp_pos[0]
            pos[1] += rp_pos[1]
            pos[2] += rp_pos[2]
        pos = [x / len(custom_objs) for x in pos]
    else:
        pos = [0.0, 0.0, 0.0]
        for ctrl in valid_controls:
            rp_pos = cmds.xform(ctrl, q=True, ws=True, rotatePivot=True)
            pos[0] += rp_pos[0]
            pos[1] += rp_pos[1]
            pos[2] += rp_pos[2]
        pos = [x / len(valid_controls) for x in pos]
    
    # 2. Tao Pivot Locator chinh
    if len(valid_controls) == 1:
        clean_name = get_clean_name(valid_controls[0])
        pivot_name = "%s%s" % (PREFIX_LOC, clean_name)
    else:
        pivot_name = "%sshared" % PREFIX_LOC
        
    if cmds.objExists(pivot_name):
        try:
            cmds.delete(pivot_name)
        except Exception:
            pass
        
    pivot_loc = cmds.spaceLocator(name=pivot_name)[0]
    cmds.xform(pivot_loc, ws=True, translation=pos)
    cmds.setAttr(pivot_loc + ".rotateOrder", cmds.getAttr(valid_controls[0] + ".rotateOrder"))
    
    for axis in ['X','Y','Z']:
        cmds.setAttr(pivot_loc + ".localScale" + axis, 1.8)
        
    parent_to_animeow_group(pivot_loc)
        
    # Luu danh sach cac control vao thuoc tinh string tren pivot locator
    cmds.addAttr(pivot_loc, longName='animeow_tempPivotControls', dataType='string')
    cmds.setAttr(pivot_loc + '.animeow_tempPivotControls', ",".join(valid_controls), type='string')
    
    # 3. Tao cac Helper Locators duoi Pivot Locator chinh
    for ctrl in valid_controls:
        clean_ctrl = get_clean_name(ctrl)
        helper_name = "%s%s" % (PREFIX_HELPER, clean_ctrl)
        
        if cmds.objExists(helper_name):
            try:
                cmds.delete(helper_name)
            except Exception:
                pass
            
        helper_loc = cmds.spaceLocator(name=helper_name)[0]
        cmds.matchTransform(helper_loc, ctrl, pos=True, rot=True)
        cmds.setAttr(helper_loc + ".rotateOrder", cmds.getAttr(ctrl + ".rotateOrder"))
        
        # Parent helper duoi pivot locator
        cmds.parent(helper_loc, pivot_loc)
        
        for axis in ['X','Y','Z']:
            cmds.setAttr(helper_loc + ".localScale" + axis, 0.5)
            
    print("[TempPivot] Da tao pivot %s va cac helper thanh cong." % pivot_loc)
    return pivot_loc

def find_pair(locator_or_control):
    """
    Tim Pivot Locator va danh sach controls lien ket.
    """
    if not cmds.objExists(locator_or_control):
        return None, []
        
    pivot_loc = None
    controls = []
    
    if PREFIX_LOC in locator_or_control:
        pivot_loc = locator_or_control
    elif PREFIX_HELPER in locator_or_control:
        parents = cmds.listRelatives(locator_or_control, parent=True)
        if parents and PREFIX_LOC in parents[0]:
            pivot_loc = parents[0]
            
    if pivot_loc:
        if cmds.attributeQuery('animeow_tempPivotControls', node=pivot_loc, exists=True):
            ctrls_str = cmds.getAttr(pivot_loc + '.animeow_tempPivotControls') or ""
            if ctrls_str:
                controls = ctrls_str.split(',')
    else:
        control = locator_or_control
        all_pivots = cmds.ls(PREFIX_LOC + "*", type="transform") or []
        for pl in all_pivots:
            if cmds.attributeQuery('animeow_tempPivotControls', node=pl, exists=True):
                ctrls_str = cmds.getAttr(pl + '.animeow_tempPivotControls') or ""
                loc_ctrls = ctrls_str.split(',')
                if control in loc_ctrls:
                    pivot_loc = pl
                    controls = loc_ctrls
                    break
                    
        if not pivot_loc:
            clean_name = get_clean_name(control)
            possible_loc = "%s%s" % (PREFIX_LOC, clean_name)
            if cmds.objExists(possible_loc):
                pivot_loc = possible_loc
                controls = [control]
                
    if not pivot_loc or not controls:
        return None, []
        
    valid_controls = [c for c in controls if cmds.objExists(c)]
    return pivot_loc, valid_controls

def active_temp_pivot(locator_or_control, start_frame, end_frame):
    """
    Kich hoat tam xoay tam thoi.
    """
    pivot_loc, controls = find_pair(locator_or_control)
    if not pivot_loc or not controls:
        raise RuntimeError("Khong tim thay bo Temp Pivot hop le!")
        
    for ctrl in controls:
        clean_ctrl = get_clean_name(ctrl)
        helper_name = "%s%s" % (PREFIX_HELPER, clean_ctrl)
        if not cmds.objExists(helper_name):
            continue
            
        temp_con = cmds.parentConstraint(ctrl, helper_name, maintainOffset=False)[0]
        
        try:
            smart_bake_object(
                obj=helper_name,
                start_frame=start_frame,
                end_frame=end_frame,
                step=1,
                smart_clean=False,
                channels='both',
                smart_bake=False
            )
        finally:
            if cmds.objExists(temp_con):
                try:
                    cmds.delete(temp_con)
                except Exception:
                    pass
                
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        cmds.cutKey(ctrl, attribute=attrs, time=(start_frame, end_frame), clear=True)
        
        for attr in attrs:
            path = "%s.%s" % (ctrl, attr)
            if cmds.objExists(path) and cmds.getAttr(path, lock=True):
                try:
                    cmds.setAttr(path, lock=False)
                except Exception:
                    pass
                
        cmds.parentConstraint(helper_name, ctrl, maintainOffset=True)
        
    print("[TempPivot] Kich hoat Temp Pivot thanh cong cho %d controls." % len(controls))
    return pivot_loc

def release_temp_pivot(locator_or_control, start_frame, end_frame):
    """
    Nuong tra chuyen dong ve cac control goc doc lap va xoa locator.
    """
    pivot_loc, controls = find_pair(locator_or_control)
    if not pivot_loc or not controls:
        raise RuntimeError("Khong tim thay bo Temp Pivot hop le!")
        
    for ctrl in controls:
        clean_ctrl = get_clean_name(ctrl)
        helper_name = "%s%s" % (PREFIX_HELPER, clean_ctrl)
        
        source_obj = helper_name if cmds.objExists(helper_name) else pivot_loc
        smart_bake_object(
            obj=ctrl,
            start_frame=start_frame,
            end_frame=end_frame,
            step=1,
            smart_clean=False,
            channels='both',
            smart_bake=True,
            source_obj=source_obj
        )
        
        incoming_cons = get_incoming_constraints(ctrl)
        for c in incoming_cons:
            inputs = cmds.listConnections(c, source=True, destination=False) or []
            if any(helper_name in inp or pivot_loc in inp for inp in inputs):
                if cmds.objExists(c):
                    try:
                        cmds.delete(c)
                    except Exception:
                        pass
                    
        pair_blends = get_pair_blend_nodes(ctrl)
        for pb in pair_blends:
            if cmds.objExists(pb):
                try:
                    cmds.delete(pb)
                except Exception:
                    pass
                
    if cmds.objExists(pivot_loc):
        try:
            cmds.delete(pivot_loc)
        except Exception:
            pass
        
    clean_empty_animeow_group()
        
    print("[TempPivot] Da giai phong Temp Pivot thanh cong.")
    return controls[0] if controls else None
