# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

def get_all_keys(obj):
    """Lấy tất cả các khung hình có keyframe bất kỳ (translate, rotate...) để làm kênh mẫu"""
    keys = set()
    curves = cmds.keyframe(obj, query=True, name=True) or []
    for curve in curves:
        curve_keys = cmds.keyframe(curve, query=True, timeChange=True) or []
        for k in curve_keys:
            keys.add(int(round(k)))
    return sorted(list(keys))

def change_rotate_order(obj, new_order):
    """
    Thay đổi Rotate Order của vật thể mà vẫn bảo toàn chuyển động và số lượng/vị trí keyframe.
    new_order: string ('xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx') hoặc int (0 -> 5)
    """
    if not cmds.objExists(obj):
        return False, "Không tìm thấy đối tượng %s!" % obj
        
    # Chuyển đổi tên order sang giá trị số nguyên của Maya
    order_map = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}
    if isinstance(new_order, str):
        new_order_val = order_map.get(new_order.lower(), 0)
    else:
        new_order_val = int(new_order)
        
    curr_order = cmds.getAttr(obj + ".rotateOrder")
    if curr_order == new_order_val:
        return True, "Đối tượng đã ở Rotate Order này rồi!"

    # 1. Thu thập tất cả các keyframe hiện có của đối tượng
    keys = get_all_keys(obj)
    if not keys:
        # Nếu đối tượng không có keyframe nào, chỉ cần đổi rotateOrder trực tiếp
        cmds.setAttr(obj + ".rotateOrder", new_order_val)
        return True, "Đã đổi Rotate Order trực tiếp (đối tượng không có anim)."

    # 2. Tạo locator thế giới tạm thời
    clean_name = obj.replace(":", "_").replace("|", "_")
    loc = cmds.spaceLocator(name="temp_rotateOrder_loc_%s" % clean_name)[0]
    cmds.matchTransform(loc, obj, pos=True, rot=True)
    cmds.setAttr(loc + ".rotateOrder", curr_order)
    
    # 3. Tạo constraint từ obj sang locator
    temp_constraint = cmds.parentConstraint(obj, loc, maintainOffset=False)[0]
    
    # 4. Bake locator tại đúng các keyframe gốc
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.setKeyframe(loc, attribute=['translateX', 'translateY', 'translateZ', 
                                              'rotateX', 'rotateY', 'rotateZ'], time=k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    if cmds.objExists(temp_constraint):
        cmds.delete(temp_constraint)

    # 5. Xóa keyframe xoay và dịch chuyển trên obj gốc để nhận giá trị mới sạch sẽ
    cmds.cutKey(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                'rotateX', 'rotateY', 'rotateZ'], clear=True)
                                
    # 6. Đổi rotate order mới
    cmds.setAttr(obj + ".rotateOrder", new_order_val)
    
    # 7. Ràng buộc ngược lại từ locator sang obj
    restore_constraint = cmds.parentConstraint(loc, obj, maintainOffset=False)[0]
    
    # 8. Bake ngược lại obj tại đúng các keyframe gốc
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.setKeyframe(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                              'rotateX', 'rotateY', 'rotateZ'], time=k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    # 9. Dọn dẹp
    if cmds.objExists(restore_constraint):
        cmds.delete(restore_constraint)
    if cmds.objExists(loc):
        cmds.delete(loc)
        
    return True, "Đã chuyển đổi Rotate Order thành công và bảo toàn %d keyframe!" % len(keys)

def record_world_space(obj):
    """
    Ghi hình chuyển động thế giới của obj sang một locator, lưu giữ các vị trí keyframe gốc.
    """
    if not cmds.objExists(obj):
        return None, "Không tìm thấy đối tượng %s!" % obj
        
    keys = get_all_keys(obj)
    if not keys:
        return None, "Đối tượng không có keyframe hoạt họa nào!"
        
    clean_name = obj.replace(":", "_").replace("|", "_")
    loc_name = "animeow_space_record_%s" % clean_name
    
    # Xóa locator trùng cũ nếu có
    if cmds.objExists(loc_name):
        try:
            cmds.delete(loc_name)
        except Exception:
            pass
            
    loc = cmds.spaceLocator(name=loc_name)[0]
    cmds.matchTransform(loc, obj, pos=True, rot=True)
    cmds.setAttr(loc + ".rotateOrder", cmds.getAttr(obj + ".rotateOrder"))
    
    # Tăng kích thước locator hiển thị
    for axis in ['X','Y','Z']:
         cmds.setAttr(loc + ".localScale" + axis, 2.0)
         
    # Bật Override Color (màu xanh lá cây 14 làm nổi bật)
    cmds.setAttr(loc + ".overrideEnabled", 1)
    cmds.setAttr(loc + ".overrideColor", 14)
    
    # Lưu danh sách keyframe gốc vào locator dưới dạng chuỗi attribute để khi restore đọc lại
    cmds.addAttr(loc, longName="animeow_saved_keys", dataType="string")
    keys_str = ",".join([str(k) for k in keys])
    cmds.setAttr(loc + ".animeow_saved_keys", keys_str, type="string")
    
    # Lưu liên kết đối tượng gốc
    cmds.addAttr(loc, longName="animeow_sourceObj", attributeType="message")
    cmds.connectAttr(obj + ".message", loc + ".animeow_sourceObj")
    
    # Ghi parentConstraint tạm từ obj sang locator
    temp_con = cmds.parentConstraint(obj, loc, maintainOffset=False)[0]
    
    # Ghi anim thế giới
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.setKeyframe(loc, attribute=['translateX', 'translateY', 'translateZ', 
                                              'rotateX', 'rotateY', 'rotateZ'], time=k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    if cmds.objExists(temp_con):
        cmds.delete(temp_con)
        
    cmds.select(loc)
    return loc, "Đã ghi nhận thành công %d keyframe thế giới vào locator: %s" % (len(keys), loc)

def restore_world_space(obj, locator):
    """
    Khôi phục chuyển động thế giới của obj từ locator tại đúng các keyframe đã lưu.
    """
    if not cmds.objExists(obj):
        return False, "Không tìm thấy đối tượng %s!" % obj
    if not cmds.objExists(locator):
        return False, "Không tìm thấy locator lưu trữ %s!" % locator
        
    # Đọc lại danh sách keyframe lưu trữ
    if not cmds.attributeQuery("animeow_saved_keys", node=locator, exists=True):
        return False, "Locator không chứa dữ liệu keyframe hợp lệ!"
        
    keys_str = cmds.getAttr(locator + ".animeow_saved_keys")
    if not keys_str:
        return False, "Dữ liệu keyframe trống!"
        
    keys = [int(k) for k in keys_str.split(",")]
    
    # Ràng buộc obj vào locator
    restore_constraint = cmds.parentConstraint(locator, obj, maintainOffset=False)[0]
    
    # Xóa key cũ trên obj trước khi bake để nhận key mới sạch sẽ
    cmds.cutKey(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                'rotateX', 'rotateY', 'rotateZ'], clear=True)
                                
    # Bake ngược lại obj tại đúng các keyframe
    curr_time = cmds.currentTime(q=True)
    cmds.refresh(suspend=True)
    try:
        for k in keys:
            cmds.currentTime(k, edit=True)
            cmds.setKeyframe(obj, attribute=['translateX', 'translateY', 'translateZ', 
                                              'rotateX', 'rotateY', 'rotateZ'], time=k)
    finally:
        cmds.refresh(suspend=False)
        cmds.currentTime(curr_time, edit=True)
        
    # Xóa constraint và locator
    if cmds.objExists(restore_constraint):
        cmds.delete(restore_constraint)
    if cmds.objExists(locator):
        cmds.delete(locator)
        
    cmds.select(obj)
    return True, "Đã khôi phục thành công tọa độ thế giới cho %s tại %d keyframe!" % (obj, len(keys))
