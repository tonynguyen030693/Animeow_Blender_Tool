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

def get_incoming_constraints(obj):
    """Tìm tất cả các constraint node trực tiếp hoặc gián tiếp (qua pairBlend) đang ràng buộc obj"""
    if not cmds.objExists(obj):
        return []
        
    found_constraints = []
    
    # 1. Tìm các constraint kết nối trực tiếp (source)
    direct_cons = cmds.listConnections(obj, source=True, destination=False, type="constraint") or []
    found_constraints.extend(direct_cons)
    
    # 2. Tìm qua pairBlend nodes (dữ liệu đi từ Constraint -> pairBlend -> Object)
    pair_blends = cmds.listConnections(obj, source=True, destination=False, type="pairBlend") or []
    for pb in pair_blends:
        pb_cons = cmds.listConnections(pb, source=True, destination=False, type="constraint") or []
        found_constraints.extend(pb_cons)
        
    return list(set(found_constraints))

def get_pair_blend_nodes(obj):
    """Tìm tất cả pairBlend nodes đầu vào của obj"""
    if not cmds.objExists(obj):
        return []
    return cmds.listConnections(obj, source=True, destination=False, type="pairBlend") or []

def get_extreme_frames(curve, tolerance=0.001):
    """Tìm các frame cực trị (đỉnh/đáy) thực sự của đường cong animation"""
    if not cmds.objExists(curve):
        return []
        
    keys = cmds.keyframe(curve, q=True, timeChange=True) or []
    values = cmds.keyframe(curve, q=True, valueChange=True) or []
    
    if len(keys) <= 2:
        return [int(round(k)) for k in keys]
        
    extreme_frames = []
    # Luôn giữ key đầu và key cuối
    extreme_frames.append(int(round(keys[0])))
    extreme_frames.append(int(round(keys[-1])))
    
    for i in range(1, len(keys) - 1):
        prev_val = values[i-1]
        curr_val = values[i]
        next_val = values[i+1]
        
        diff1 = curr_val - prev_val
        diff2 = next_val - curr_val
        
        # Nếu đổi chiều độ dốc (đổi dấu nhân) và sự thay đổi lớn hơn sai số tolerance
        if diff1 * diff2 < -1e-8:
            if abs(diff1) > tolerance or abs(diff2) > tolerance:
                extreme_frames.append(int(round(keys[i])))
                
    return list(set(extreme_frames))

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

    # Tìm các constraint thực tế đang ràng buộc vật thể này
    incoming_constraints = get_incoming_constraints(obj)

    if smart_clean:
        # 1. Thu thập lưới Grid Step
        grid_frames = set(range(int(start_frame), int(end_frame) + 1, step))
        
        # 2. Thu thập keyframe cực trị nguồn từ driver của constraint
        source_keyframes = set()
        targets_to_scan = []
        for con in incoming_constraints:
            inputs = cmds.listConnections(con, source=True, destination=False) or []
            targets_to_scan.extend(inputs)
            
        targets_to_scan = list(set(targets_to_scan))
        for target in targets_to_scan:
            if cmds.objExists(target):
                curves = cmds.keyframe(target, q=True, name=True) or []
                for curve in curves:
                    extreme_keys = get_extreme_frames(curve)
                    for k in extreme_keys:
                        source_keyframes.add(k)
                        
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
        
        # 4. Chỉ xóa constraints và pairBlends hướng vào
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try:
                    cmds.delete(c)
                except Exception:
                    pass
        pair_blends = get_pair_blend_nodes(obj)
        for pb in pair_blends:
            if cmds.objExists(pb):
                try:
                    cmds.delete(pb)
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
        
        # Chỉ xóa constraints và pairBlends hướng vào
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try:
                    cmds.delete(c)
                except Exception:
                    pass
        pair_blends = get_pair_blend_nodes(obj)
        for pb in pair_blends:
            if cmds.objExists(pb):
                try:
                    cmds.delete(pb)
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
            constraints = get_incoming_constraints(locator_or_obj)
            for con in constraints:
                inputs = cmds.listConnections(con, source=True, destination=False) or []
                for inp in inputs:
                    if self.PREFIX in inp:
                        locator = inp
                        obj = locator_or_obj if locator_or_obj != locator else inp
                        break
                        
        if not locator or not obj:
            raise RuntimeError("Vui lòng chọn Locator hoặc vật thể gốc đã được World Bake trước đó!")
            
        # Xác định các kênh ràng buộc hiện hành bằng cách quét get_incoming_constraints
        channels = 'both'
        incoming_cons = get_incoming_constraints(obj)
        has_point = False
        has_orient = False
        for c in incoming_cons:
            n_type = cmds.nodeType(c)
            if n_type == 'pointConstraint':
                has_point = True
            elif n_type == 'orientConstraint':
                has_orient = True
                
        if has_point and not has_orient:
            channels = 'translate'
        elif has_orient and not has_point:
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
