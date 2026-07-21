# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel
pkg_name = __name__.split('.')[0]
world_bake = __import__(pkg_name + ".core.world_bake", fromlist=["smart_bake_object"])
smart_bake_object = world_bake.smart_bake_object

def get_all_namespaces():
    """Lay danh sach tat ca cac namespace dang ton tai trong Scene (tru namespace he thong)"""
    namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
    default_ns = ['UI', 'shared']
    filtered_ns = [ns for ns in namespaces if ns not in default_ns]
    return sorted(list(set(filtered_ns)))

def auto_map_rigs(source_ns, target_ns):
    """
    Tu dong khop noi cac control cua 2 rig dua tren ten giong nhau.
    """
    source_prefix = source_ns + ":" if source_ns else ""
    target_prefix = target_ns + ":" if target_ns else ""
    
    source_objects = []
    if source_ns:
        source_objects = cmds.ls(source_prefix + "*", type="transform") or []
    else:
        source_objects = cmds.ls(sl=True, type="transform") or []
        
    target_objects = []
    if target_ns:
        target_objects = cmds.ls(target_prefix + "*", type="transform") or []
    else:
        target_objects = cmds.ls(type="transform") or []
        
    target_map = {}
    for obj in target_objects:
        short_name = obj.split(":")[-1]
        target_map[short_name] = obj
        
    mapping_pairs = []
    for src in source_objects:
        short_src = src.split(":")[-1]
        if short_src in target_map:
            mapping_pairs.append((src, target_map[short_src]))
            
    return mapping_pairs

def execute_retarget(mapping_pairs, start_frame, end_frame, step=1, maintain_offset=True, channels='both', smart_bake=False):
    """
    Thuc hien retarget chuyen dong tu Source Rig sang Target Rig.
    """
    valid_pairs = []
    for src, tgt in mapping_pairs:
        if cmds.objExists(src) and cmds.objExists(tgt):
            valid_pairs.append((src, tgt))
            
    if not valid_pairs:
        return False, "Khong tim thay bat ky cap doi tuong hop le nao de Retarget!"
        
    temp_constraints = []
    targets_to_bake = []
    
    for src, tgt in valid_pairs:
        attrs_to_unlock = []
        if channels in ['both', 'translate']:
            attrs_to_unlock.extend(['tx', 'ty', 'tz'])
        if channels in ['both', 'rotate']:
            attrs_to_unlock.extend(['rx', 'ry', 'rz'])
            
        for attr in attrs_to_unlock:
            path = "%s.%s" % (tgt, attr)
            if cmds.objExists(path) and cmds.getAttr(path, lock=True):
                try:
                    cmds.setAttr(path, lock=False)
                except Exception:
                    pass
                
        con = None
        try:
            if channels == 'translate':
                con = cmds.pointConstraint(src, tgt, maintainOffset=maintain_offset)[0]
            elif channels == 'rotate':
                con = cmds.orientConstraint(src, tgt, maintainOffset=maintain_offset)[0]
            else: # both
                con = cmds.parentConstraint(src, tgt, maintainOffset=maintain_offset)[0]
                
            if con:
                temp_constraints.append(con)
                targets_to_bake.append((tgt, src))
        except Exception as e:
            print("[Retarget] Khong the rang buoc %s -> %s: %s" % (src, tgt, str(e)))
            
    if not targets_to_bake:
        return False, "Khong tao duoc bat ky rang buoc tam thoi nao!"
        
    baked_count = 0
    try:
        for tgt, src in targets_to_bake:
            smart_bake_object(
                obj=tgt,
                start_frame=start_frame,
                end_frame=end_frame,
                step=step,
                smart_clean=False,
                channels=channels,
                smart_bake=smart_bake,
                source_obj=src
            )
            baked_count += 1
    finally:
        for con in temp_constraints:
            if cmds.objExists(con):
                try:
                    cmds.delete(con)
                except Exception:
                    pass
                    
    return True, "Da Retarget thanh cong %d bo dieu khien!" % baked_count
