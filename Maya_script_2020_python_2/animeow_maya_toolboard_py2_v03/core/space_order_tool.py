# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
pkg_name = __name__.split('.')[0]
world_bake = __import__(pkg_name + ".core.world_bake", fromlist=[
    "parent_to_animeow_group", "clean_empty_animeow_group"
])
parent_to_animeow_group = world_bake.parent_to_animeow_group
clean_empty_animeow_group = world_bake.clean_empty_animeow_group

def get_all_keys(obj):
    """Lay tat ca cac khung hinh co keyframe bat ky (translate, rotate...) de lam kenh mau"""
    keys = set()
    curves = cmds.keyframe(obj, query=True, name=True) or []
    for curve in curves:
        curve_keys = cmds.keyframe(curve, query=True, timeChange=True) or []
        for k in curve_keys:
            keys.add(int(round(k)))
    return sorted(list(keys))

def key_transforms(obj, time):
    """Dat keyframe cho cac kenh translate va rotate cua obj neu chung khong bi khoa"""
    attrs_to_key = []
    for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
        if cmds.objExists("%s.%s" % (obj, attr)) and not cmds.getAttr("%s.%s" % (obj, attr), lock=True):
            attrs_to_key.append(attr)
    if attrs_to_key:
        cmds.setKeyframe(obj, attribute=attrs_to_key, time=time)

def change_rotate_order(obj, new_order):
    """
    Thay doi Rotate Order cua vat the ma van bao toan chuyen dong va so luong/vi tri keyframe.
    new_order: string ('xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx') hoac int (0 -> 5)
    """
    if not cmds.objExists(obj):
        return False, "Khong tim thay doi tuong %s!" % obj
        
    # Chuyen doi ten order sang gia tri so nguyen cua Maya
    order_map = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}
    if hasattr(new_order, 'lower'):
        new_order_val = order_map.get(new_order.lower(), 0)
    else:
        new_order_val = int(new_order)
        
    curr_order = cmds.getAttr(obj + ".rotateOrder")
    if curr_order == new_order_val:
        return True, "Doi tuong da o Rotate Order nay roi!"

    keys = get_all_keys(obj)
    if not keys:
        # Neu doi tuong khong co keyframe nao, chi can doi rotateOrder truc tiep
        cmds.setAttr(obj + ".rotateOrder", new_order_val)
        return True, "Da doi Rotate Order truc tiep (doi tuong khong co anim)."

    # 2. Tao locator the gioi tam thoi
    clean_name = obj.replace(":", "_").replace("|", "_")
    loc = cmds.spaceLocator(name="Anm_loc_rotOrder_%s" % clean_name)[0]
    cmds.matchTransform(loc, obj, pos=True, rot=True)
    parent_to_animeow_group(loc)
    cmds.setAttr(loc + ".rotateOrder", curr_order)
    
    # 3. Ghi anim the gioi len locator tai cac frame k qua matchTransform (Khong dung constraint de tranh bi lock kenh)
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.matchTransform(loc, obj, pos=True, rot=True)
            key_transforms(loc, k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)

    # 4. Xoa keyframe cu tren obj goc
    cmds.cutKey(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                'rotateX', 'rotateY', 'rotateZ'], clear=True)
                                
    # 5. Doi rotate order moi tren obj
    cmds.setAttr(obj + ".rotateOrder", new_order_val)
    
    # 6. Khop nguoc lai tu locator sang obj va dat keyframe
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.matchTransform(obj, loc, pos=True, rot=True)
            key_transforms(obj, k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    # 7. Don dep locator tam
    if cmds.objExists(loc):
        cmds.delete(loc)
        
    clean_empty_animeow_group()
    return True, "Da chuyen doi Rotate Order thanh cong va bao toan %d keyframe!" % len(keys)

def record_world_space(obj):
    """
    Ghi hinh chuyen dong the gioi cua obj sang mot locator, luu giu cac vi tri keyframe goc.
    """
    if not cmds.objExists(obj):
        return None, "Khong tim thay doi tuong %s!" % obj
        
    keys = get_all_keys(obj)
    if not keys:
        return None, "Doi tuong khong co keyframe hoat hoa nao!"
        
    clean_name = obj.replace(":", "_").replace("|", "_")
    loc_name = "Anm_loc_space_record_%s" % clean_name
    
    # Xoa locator trung cu neu co
    if cmds.objExists(loc_name):
        try:
            cmds.delete(loc_name)
        except Exception:
            pass
            
    loc = cmds.spaceLocator(name=loc_name)[0]
    cmds.matchTransform(loc, obj, pos=True, rot=True)
    cmds.setAttr(loc + ".rotateOrder", cmds.getAttr(obj + ".rotateOrder"))
    
    # Tang kich thuoc locator hien thi
    for axis in ['X','Y','Z']:
         cmds.setAttr(loc + ".localScale" + axis, 2.0)
         
    # Bat Override Color (mau xanh la cay 14 lam noi bat)
    cmds.setAttr(loc + ".overrideEnabled", 1)
    cmds.setAttr(loc + ".overrideColor", 14)
    parent_to_animeow_group(loc)
    
    # Luu danh sach keyframe goc vao locator duoi dang chuoi attribute de khi restore doc lai
    cmds.addAttr(loc, longName="animeow_saved_keys", dataType="string")
    keys_str = ",".join([str(k) for k in keys])
    cmds.setAttr(loc + ".animeow_saved_keys", keys_str, type="string")
    
    # Luu lien ket doi tuong goc
    cmds.addAttr(loc, longName="animeow_sourceObj", attributeType="message")
    cmds.connectAttr(obj + ".message", loc + ".animeow_sourceObj")
    
    # Ghi anim the gioi qua matchTransform
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.matchTransform(loc, obj, pos=True, rot=True)
            key_transforms(loc, k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    cmds.select(loc)
    return loc, "Da ghi nhan thanh cong %d keyframe the gioi vao locator: %s" % (len(keys), loc)

def restore_world_space(obj, locator):
    """
    Khoi phuc chuyen dong the gioi cua obj tu locator tai dung cac keyframe da luu.
    """
    if not cmds.objExists(obj):
        return False, "Khong tim thay doi tuong %s!" % obj
    if not cmds.objExists(locator):
        return False, "Khong tim thay locator luu tru %s!" % locator
        
    # Doc lai danh sach keyframe luu tru
    if not cmds.attributeQuery("animeow_saved_keys", node=locator, exists=True):
        return False, "Locator khong chua du lieu keyframe hop le!"
        
    keys_str = cmds.getAttr(locator + ".animeow_saved_keys")
    if not keys_str:
        return False, "Du lieu keyframe trong!"
        
    keys = [int(k) for k in keys_str.split(",")]
    
    # Xoa key cu tren obj truoc khi bake de nhan key moi sach se
    cmds.cutKey(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                'rotateX', 'rotateY', 'rotateZ'], clear=True)
                                
    # Bake nguoc lai obj tai dung cac keyframe bang cach khop truc tiep, khong dung constraint
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.matchTransform(obj, locator, pos=True, rot=True)
            key_transforms(obj, k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    # Xoa locator luu tru
    if cmds.objExists(locator):
        cmds.delete(locator)
        
    clean_empty_animeow_group()
    cmds.select(obj)
    return True, "Da khoi phuc thanh cong toa do the gioi cho %s tai %d keyframe!" % (obj, len(keys))
