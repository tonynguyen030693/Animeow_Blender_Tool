# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import maya.cmds as cmds
import maya.api.OpenMaya as om

def get_relative_offset(parent_obj, child_obj):
    """
    Tinh toan va tra ve ma tran offset cua child_obj tuong doi voi parent_obj
    duoi dang danh sach 16 so thuc.
    """
    if not cmds.objExists(parent_obj) or not cmds.objExists(child_obj):
        raise ValueError(u"Vat the khong ton tai trong Scene!")
        
    parent_mat_list = cmds.xform(parent_obj, query=True, worldSpace=True, matrix=True)
    child_mat_list = cmds.xform(child_obj, query=True, worldSpace=True, matrix=True)
    
    parent_mat = om.MMatrix(parent_mat_list)
    child_mat = om.MMatrix(child_mat_list)
    
    # L = W_child * W_parent.inverse()
    offset_mat = child_mat * parent_mat.inverse()
    return list(offset_mat)

def apply_relative_offset(parent_obj, child_obj, offset_matrix_list):
    """
    Dich chuyen child_obj theo parent_obj su dung ma tran offset da luu.
    """
    if not cmds.objExists(parent_obj) or not cmds.objExists(child_obj):
        return
        
    parent_mat_list = cmds.xform(parent_obj, query=True, worldSpace=True, matrix=True)
    parent_mat = om.MMatrix(parent_mat_list)
    offset_mat = om.MMatrix(offset_matrix_list)
    
    # W_child_new = L * W_parent_new
    new_child_mat = offset_mat * parent_mat
    
    cmds.xform(child_obj, worldSpace=True, matrix=list(new_child_mat))

def bake_fake_constraint(parent_obj, child_obj, offset_matrix_list, start_frame, end_frame, step=1):
    """
    Bake khop chuyen dong cua child_obj theo parent_obj trong mot khoang thoi gian.
    """
    if not cmds.objExists(parent_obj) or not cmds.objExists(child_obj):
        raise ValueError(u"Vat the khong ton tai!")
        
    cmds.undoInfo(openChunk=True, chunkName="AnimeowBakeFakeConstraint")
    original_time = cmds.currentTime(query=True)
    
    try:
        current = float(start_frame)
        end = float(end_frame)
        
        while current <= end:
            cmds.currentTime(current, edit=True)
            apply_relative_offset(parent_obj, child_obj, offset_matrix_list)
            cmds.setKeyframe(child_obj, attribute=['translate', 'rotate'])
            current += step
            
        print(u"[AnimeowTool] Da bake Fake Constraint thanh cong tu frame %d den %d." % (start_frame, end_frame))
    except Exception as e:
        raise e
    finally:
        cmds.currentTime(original_time, edit=True)
        cmds.undoInfo(closeChunk=True)

def get_multi_offsets(parent_obj, children_list):
    """
    Tra ve dictionary luu ma tran offset cua tung child tuong doi voi parent.
    {child_name: [16 floats]}
    """
    offsets = {}
    for child in children_list:
        if cmds.objExists(child):
            try:
                offset = get_relative_offset(parent_obj, child)
                offsets[child] = offset
            except Exception as e:
                print(u"[AnimeowTool] Bo qua loi lay offset cho '%s': %s" % (child, str(e)))
    return offsets

def apply_multi_offsets(parent_obj, children_offsets_dict):
    """
    Dich chuyen cac child theo parent dua tren ma tran offset tuong ung.
    """
    for child, offset in children_offsets_dict.items():
        if cmds.objExists(child):
            try:
                apply_relative_offset(parent_obj, child, offset)
            except Exception as e:
                print(u"[AnimeowTool] Bo qua loi ap offset cho '%s': %s" % (child, str(e)))

def bake_multi_fake_constraints(parent_obj, children_offsets_dict, start_frame, end_frame, step=1):
    """
    Bake khop chuyen dong cua nhieu child theo parent cung luc trong mot khoang thoi gian.
    """
    if not cmds.objExists(parent_obj) or not children_offsets_dict:
        raise ValueError(u"Thong tin vat chu hoac vat theo khong hop le!")
        
    cmds.undoInfo(openChunk=True, chunkName="AnimeowBakeMultiFakeConstraints")
    original_time = cmds.currentTime(query=True)
    
    try:
        current = float(start_frame)
        end = float(end_frame)
        
        while current <= end:
            cmds.currentTime(current, edit=True)
            apply_multi_offsets(parent_obj, children_offsets_dict)
            for child in children_offsets_dict.keys():
                if cmds.objExists(child):
                    cmds.setKeyframe(child, attribute=['translate', 'rotate'])
            current += step
            
        print(u"[AnimeowTool] Da bake thanh cong %d vat the theo sau tu frame %d den %d." % (len(children_offsets_dict), start_frame, end_frame))
    except Exception as e:
        raise e
    finally:
        cmds.currentTime(original_time, edit=True)
        cmds.undoInfo(closeChunk=True)
