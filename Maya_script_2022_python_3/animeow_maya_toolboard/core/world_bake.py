# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

def exception_to_unicode(e):
    try:
        msg = e.message if hasattr(e, 'message') and e.message else ""
        if not msg and e.args:
            msg = e.args[0]
        if isinstance(msg, str):
            return msg
        return str(msg)
    except Exception:
        return "Lỗi hệ thống"

def smart_bake_object(obj, start_frame, end_frame, step=1, smart_clean=True, channels='both'):
    """
    Nướng (Bake) chuyển động cho vật thể bất kỳ, hỗ trợ giữ lưới Grid Step
    và bảo toàn các keyframe cực trị nguồn (Extreme keyframes).
    """
    if not cmds.objExists(obj):
        return
        
    attrs = []
    if channels in ['both', 'translate']:
        attrs.extend(['translateX', 'translateY', 'translateZ'])
    if channels in ['both', 'rotate']:
        attrs.extend(['rotateX', 'rotateY', 'rotateZ'])
        
    if not attrs:
        attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']

    if smart_clean:
        # 1. Thu thập lưới Grid Step
        grid_frames = set(range(int(start_frame), int(end_frame) + 1, step))
        
        # 2. Thu thập keyframe thô nguồn
        source_keyframes = set()
        
        # Quét các keyframe sẵn có của chính vật thể hoặc driver của constraint nối vào nó
        targets_to_scan = [obj]
        incoming_constraints = cmds.listConnections(obj, source=True, destination=False, type="constraint") or []
        for con in incoming_constraints:
            inputs = cmds.listConnections(con, source=True, destination=False) or []
            targets_to_scan.extend(inputs)
            
        targets_to_scan = list(set(targets_to_scan))
        for target in targets_to_scan:
            if cmds.objExists(target):
                curves = cmds.keyframe(target, q=True, name=True) or []
                for curve in curves:
                    keys = cmds.keyframe(curve, q=True, timeChange=True) or []
                    for k in keys:
                        source_keyframes.add(int(round(k)))
                        
        # Hợp nhất lưới Grid và Keyframe nguồn
        keep_frames = grid_frames.union(source_keyframes)
        
        # 3. Bake bước 1 để có animation thô chính xác nhất
        cmds.bakeResults(
            obj,
            time=(start_frame, end_frame),
            sampleBy=1,
            simulation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            at=attrs
        )
        
        # 4. Chỉ xóa constraints hướng vào (đang ràng buộc đối tượng này)
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try:
                    cmds.delete(c)
                except Exception:
                    pass
                    
        # 5. Xóa keyframe nằm ngoài lưới giữ (keep_frames)
        all_keys = cmds.keyframe(obj, q=True, timeChange=True) or []
        all_keys = sorted(list(set([int(round(k)) for k in all_keys])))
        for k in all_keys:
            if k < start_frame or k > end_frame:
                continue
            if k not in keep_frames:
                cmds.cutKey(obj, time=(k, k), option="keys", clear=True)
                
    else:
        # Nướng thuần túy theo bước nhảy (Step)
        cmds.bakeResults(
            obj,
            time=(start_frame, end_frame),
            sampleBy=step,
            simulation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            at=attrs
        )
        
        # Chỉ xóa constraints hướng vào (đang ràng buộc đối tượng này)
        incoming_constraints = cmds.listConnections(obj, source=True, destination=False, type="constraint") or []
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try:
                    cmds.delete(c)
                except Exception:
                    pass

class WorldBakeManager(object):
    """
    Quản lý nướng chuyển động sang không gian thế giới thông qua Locator
    và trả ngược lại vật thể gốc, hỗ trợ lọc kênh (Translate, Rotate, Both)
    và bảo toàn keyframe cực trị.
    """
    PREFIX = "worldBake_loc_"
    
    def __init__(self):
        pass

    def get_clean_name(self, name):
        return name.replace(":", "_").replace("|", "_")

    def bake_to_locator(self, obj, start_frame, end_frame, step=1, smart_clean=True, channels='both'):
        """Bake vật thể sang một locator ở không gian thế giới"""
        if not cmds.objExists(obj):
            raise RuntimeError("Vật thể %s không tồn tại!" % obj)
            
        clean_name = self.get_clean_name(obj)
        locator_name = "%s%s" % (self.PREFIX, clean_name)
        
        # Xóa locator trùng cũ nếu có
        if cmds.objExists(locator_name):
            try:
                cmds.delete(locator_name)
            except Exception:
                pass
                
        # 1. Tạo locator mới tại vị trí vật thể
        loc = cmds.spaceLocator(name=locator_name)[0]
        cmds.matchTransform(loc, obj, pos=True, rot=True)
        cmds.setAttr(loc + ".rotateOrder", cmds.getAttr(obj + ".rotateOrder"))
        
        # Tăng scale hiển thị
        for axis in ['X','Y','Z']:
            cmds.setAttr(loc + ".localScale" + axis, 1.5)
            
        # Ghi nhận kết nối
        cmds.addAttr(loc, longName='animeow_bakeSource', attributeType='message')
        cmds.connectAttr(obj + '.message', loc + '.animeow_bakeSource')
        
        # 2. Tạo ràng buộc tạm thời từ vật thể gốc sang locator
        temp_con = cmds.parentConstraint(obj, loc, maintainOffset=False)[0]
        
        # 3. Nướng animation lên locator và tối ưu keyframe
        try:
            smart_bake_object(loc, start_frame, end_frame, step, smart_clean, channels)
        finally:
            if cmds.objExists(temp_con):
                try:
                    cmds.delete(temp_con)
                except Exception:
                    pass
                    
        # 4. Tạo ràng buộc ngược lại từ locator sang vật thể gốc theo kênh được chọn
        if channels == 'translate':
            cmds.pointConstraint(loc, obj, maintainOffset=True)
        elif channels == 'rotate':
            cmds.orientConstraint(loc, obj, maintainOffset=True)
        else: # both
            cmds.parentConstraint(loc, obj, maintainOffset=True)
            
        print("[WorldBake] Đã bake thành công %s sang locator %s." % (obj, loc))
        return loc

    def bake_from_locator(self, locator_or_obj, start_frame, end_frame, step=1, smart_clean=True):
        """Bake chuyển động từ locator thế giới ngược lại vật thể gốc và xóa locator"""
        if not cmds.objExists(locator_or_obj):
            raise RuntimeError("Không tìm thấy vật thể hoặc locator!")
            
        locator = None
        obj = None
        
        # Trường hợp 1: Chọn locator
        if self.PREFIX in locator_or_obj:
            locator = locator_or_obj
            conns = cmds.listConnections(locator + '.animeow_bakeSource', destination=False) or []
            if conns:
                obj = conns[0]
        # Trường hợp 2: Chọn vật thể gốc
        else:
            obj = locator_or_obj
            clean_name = self.get_clean_name(obj)
            possible_loc = "%s%s" % (self.PREFIX, clean_name)
            if cmds.objExists(possible_loc):
                locator = possible_loc
                
        if not locator or not obj or not cmds.objExists(locator) or not cmds.objExists(obj):
            # Thử quét các constraint kết nối
            constraints = cmds.listConnections(locator_or_obj, type="constraint") or []
            for con in constraints:
                inputs = cmds.listConnections(con, source=True, destination=False) or []
                for inp in inputs:
                    if self.PREFIX in inp:
                        locator = inp
                        obj = locator_or_obj if locator_or_obj != locator else inp
                        break
                        
        if not locator or not obj:
            raise RuntimeError("Vui lòng chọn Locator hoặc vật thể gốc đã được World Bake trước đó!")
            
        # Xác định các kênh ràng buộc hiện hành
        channels = 'both'
        if cmds.listConnections(obj, type="pointConstraint"):
            channels = 'translate'
        elif cmds.listConnections(obj, type="orientConstraint"):
            channels = 'rotate'
            
        # Nướng ngược lại lên vật thể gốc và tối ưu
        smart_bake_object(obj, start_frame, end_frame, step, smart_clean, channels)
        
        # Xóa locator sau khi hoàn thành
        if cmds.objExists(locator):
            try:
                cmds.delete(locator)
            except Exception:
                pass
                
        print("[WorldBake] Đã bake ngược thành công từ %s vào %s." % (locator, obj))
        return obj
