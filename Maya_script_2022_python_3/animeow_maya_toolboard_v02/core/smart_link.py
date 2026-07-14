# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import re

def exception_to_unicode(e):
    try:
        msg = e.message if hasattr(e, 'message') and e.message else ""
        if not msg and e.args:
            msg = e.args[0]
        if isinstance(msg, str):
            return msg
        return str(msg)
    except Exception:
        return "Lỗi ngoại lệ hệ thống"

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

class SmartLinkManager(object):
    """
    Quản lý vòng đời cặp Locator (Hook & Offset) và chuyển đổi Animation trong Maya.
    Hook (Parent Locator) theo đuôi Target (vật dẫn).
    Offset (Child Locator) chứa khoảng cách tương đối và nhận keyframe.
    """
    def __init__(self, owner, target):
        self.owner = owner
        self.target = target
        self.loc_parent = None
        self.loc_child = None

    def detect_existing_animation(self):
        """Kiểm tra xem owner có sẵn animation (keyframe) hay không"""
        anim_curves = cmds.keyframe(self.owner, query=True, name=True)
        return bool(anim_curves)

    def record_world_animation(self, start_frame, end_frame):
        """Ghi hình chuyển động thế giới của owner sang một locator tạm thời bằng Constraint & Bake"""
        # Tạo locator tạm
        loc_temp = cmds.spaceLocator(name="loc_temp_" + self.owner)[0]
        
        # Tạo parentConstraint tạm thời từ owner sang loc_temp
        const = cmds.parentConstraint(self.owner, loc_temp, maintainOffset=False)[0]
        scale_const = None
        try:
            scale_const = cmds.scaleConstraint(self.owner, loc_temp, maintainOffset=False)[0]
        except Exception:
            pass
            
        # Bake kết quả bằng engine cực nhanh của Maya
        cmds.bakeResults(
            loc_temp,
            time=(start_frame, end_frame),
            sampleBy=1,
            simulation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            at=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        )
        
        # Xóa constraint tạm thời
        cmds.delete(const)
        if scale_const and cmds.objExists(scale_const):
            cmds.delete(scale_const)
            
        return loc_temp

    def clear_owner_keyframes(self):
        """Xóa toàn bộ keyframe cũ trên owner để giải phóng toạ độ"""
        cmds.cutKey(self.owner, clear=True)

    def create_locator_pair(self):
        """Tạo cặp Locator Parent (Hook) và Child (Offset) tại vị trí thế giới của owner hiện tại"""
        # 1. Tạo Parent (Hook)
        self.loc_parent = cmds.spaceLocator(name="loc_parent_" + self.owner)[0]
        cmds.matchTransform(self.loc_parent, self.owner, pos=True, rot=True)
        
        # 2. Tạo Child (Offset)
        self.loc_child = cmds.spaceLocator(name="loc_child_" + self.owner)[0]
        cmds.matchTransform(self.loc_child, self.owner, pos=True, rot=True)
        
        # Thiết lập tỷ lệ hiển thị cho dễ nhìn trong viewport
        for axis in ['X', 'Y', 'Z']:
            cmds.setAttr(self.loc_parent + ".localScale" + axis, 2.0)
            cmds.setAttr(self.loc_child + ".localScale" + axis, 1.2)
            
        # 3. Lồng làm cha con
        cmds.parent(self.loc_child, self.loc_parent)
        
        return self.loc_parent, self.loc_child

    def apply_constraint_to_target(self):
        """Gán parentConstraint & scaleConstraint từ target (vật dẫn) tới loc_parent"""
        cmds.parentConstraint(self.target, self.loc_parent, maintainOffset=True)
        try:
            cmds.scaleConstraint(self.target, self.loc_parent, maintainOffset=True)
        except Exception:
            pass

    def apply_constraint_to_owner(self):
        """Gán parentConstraint & scaleConstraint từ loc_child tới owner (vật bị dẫn)"""
        cmds.parentConstraint(self.loc_child, self.owner, maintainOffset=True)
        try:
            cmds.scaleConstraint(self.loc_child, self.owner, maintainOffset=True)
        except Exception:
            pass

    def match_animation_to_child(self, loc_temp, start_frame, end_frame):
        """Khớp chuyển động từ loc_temp sang loc_child bằng parentConstraint và bakeResults"""
        # Tạo constraint tạm thời từ loc_temp sang loc_child
        const = cmds.parentConstraint(loc_temp, self.loc_child, maintainOffset=False)[0]
        scale_const = None
        try:
            scale_const = cmds.scaleConstraint(loc_temp, self.loc_child, maintainOffset=False)[0]
        except Exception:
            pass
            
        # Bake kết quả trực tiếp sang loc_child (Maya tự động tính toán toạ độ cục bộ dưới loc_parent)
        cmds.bakeResults(
            self.loc_child,
            time=(start_frame, end_frame),
            sampleBy=1,
            simulation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            at=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        )
        
        # Xóa constraint tạm thời
        cmds.delete(const)
        if scale_const and cmds.objExists(scale_const):
            cmds.delete(scale_const)

    def reset_owner_transforms(self):
        """Đưa toạ độ cục bộ của owner về mặc định (0 cho dịch chuyển/xoay, 1 cho scale)"""
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            try:
                cmds.setAttr(self.owner + "." + attr, 0)
            except Exception:
                pass
        for attr in ['sx', 'sy', 'sz']:
            try:
                cmds.setAttr(self.owner + "." + attr, 1)
            except Exception:
                pass

    @staticmethod
    def cleanup_temp(loc_temp):
        """Xóa locator tạm"""
        if loc_temp and cmds.objExists(loc_temp):
            cmds.delete(loc_temp)


class AnimationBaker(object):
    """
    Chịu trách nhiệm Bake (Bake) chuyển động từ locator sang keyframe thực trên vật thể
    và dọn dẹp sạch sẽ các constraints/locator thừa.
    """
    def __init__(self, owner):
        self.owner = owner

    def find_locator_names(self):
        """Tìm cặp Locator đang liên kết với owner"""
        loc_parent = "loc_parent_" + self.owner
        loc_child = "loc_child_" + self.owner
        
        # Nếu không tìm thấy trực tiếp theo tên, quét ngược qua các constraint
        if not cmds.objExists(loc_child):
            constraints = cmds.listConnections(self.owner, type="parentConstraint") or []
            for con in constraints:
                targets = cmds.parentConstraint(con, query=True, targetList=True) or []
                for target in targets:
                    if "loc_child_" in target:
                        loc_child = target
                        parents = cmds.listRelatives(loc_child, parent=True) or []
                        if parents and "loc_parent_" in parents[0]:
                            loc_parent = parents[0]
                        break
        
        return (loc_parent if cmds.objExists(loc_parent) else None,
                loc_child if cmds.objExists(loc_child) else None)

    def bake(self, start_frame, end_frame, step=1, smart_clean=True, clean_threshold=0.05):
        """Bake chuyển động và dọn dẹp"""
        # 1. Định vị locators
        loc_parent, loc_child = self.find_locator_names()
        
        # Tự động tối ưu hóa khoảng bake dựa trên phạm vi keyframe thực tế của locator
        # để tránh bị mất animation trước/sau timeline hiển thị khi xóa constraint
        if loc_child and cmds.objExists(loc_child):
            all_loc_keys = cmds.keyframe(loc_child, q=True, timeChange=True) or []
            if all_loc_keys:
                loc_min = min(all_loc_keys)
                loc_max = max(all_loc_keys)
                start_frame = min(start_frame, loc_min)
                end_frame = max(end_frame, loc_max)
        
        # Quét thêm keyframe trên target (vật dẫn gốc của loc_parent) để mở rộng thời gian
        target_obj = None
        if loc_parent and cmds.objExists(loc_parent):
            cons = cmds.listConnections(loc_parent, type="parentConstraint") or []
            if cons:
                targets = cmds.parentConstraint(cons[0], query=True, targetList=True) or []
                if targets:
                    target_obj = targets[0]
                    
        if target_obj and cmds.objExists(target_obj):
            all_target_keys = cmds.keyframe(target_obj, q=True, timeChange=True) or []
            if all_target_keys:
                target_min = min(all_target_keys)
                target_max = max(all_target_keys)
                start_frame = min(start_frame, target_min)
                end_frame = max(end_frame, target_max)
                
        attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        incoming_constraints = cmds.listConnections(self.owner, source=True, destination=False, type="constraint") or []
        
        if smart_clean:
            # Thu thập các frame theo lưới Grid Step (ví dụ step=2: 1, 3, 5, 7...)
            grid_frames = set(range(int(start_frame), int(end_frame) + 1, step))
            
            # Thu thập các keyframe nguồn từ locator hoặc các vật dẫn của constraint
            source_keyframes = set()
            targets_to_scan = []
            if loc_child and cmds.objExists(loc_child):
                targets_to_scan.append(loc_child)
            else:
                for con in incoming_constraints:
                    # Lấy các kết nối đầu vào (drivers) của constraint
                    inputs = cmds.listConnections(con, source=True, destination=False) or []
                    targets_to_scan.extend(inputs)
            
            targets_to_scan = list(set(targets_to_scan))
            for target in targets_to_scan:
                if cmds.objExists(target):
                    loc_curves = cmds.keyframe(target, q=True, name=True) or []
                    for curve in loc_curves:
                        extreme_keys = get_extreme_frames(curve)
                        for k in extreme_keys:
                            source_keyframes.add(k)
            
            # Tập hợp các frame cần giữ lại (Hợp của lưới Grid và Keyframe nguồn)
            keep_frames = grid_frames.union(source_keyframes)
            
            # Bake với step = 1 để ghi nhận đầy đủ chuyển động chính xác nhất
            cmds.bakeResults(
                self.owner,
                time=(start_frame, end_frame),
                sampleBy=1,
                simulation=True,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                at=attrs
            )
            
            # Xoá các constraints trên owner sau khi Bake
            for c in list(set(incoming_constraints)):
                if cmds.objExists(c):
                    try:
                        cmds.delete(c)
                    except Exception:
                        pass
            
            # Lọc bỏ các keyframe thô không nằm trong danh sách keep_frames
            all_keys = cmds.keyframe(self.owner, q=True, timeChange=True) or []
            all_keys = sorted(list(set([int(round(k)) for k in all_keys])))
            delete_frames = [k for k in all_keys if start_frame <= k <= end_frame and k not in keep_frames]
            
            if delete_frames:
                cmds.selectKey(self.owner, clear=True)
                for k in delete_frames:
                    cmds.selectKey(self.owner, add=True, time=(k, k))
                cmds.cutKey(animation="keysOrObjects", clear=True)
            
            print(u"[SmartLink] Đã bake tối ưu giữ Grid (bước %d) và giữ nguyên các key cực trị nguồn." % step)
            
        else:
            # Bake thuần túy theo bước nhảy (Step) không thêm key cực trị nguồn nằm ngoài lưới
            cmds.bakeResults(
                self.owner,
                time=(start_frame, end_frame),
                sampleBy=step,
                simulation=True,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                at=attrs
            )
            
            # Xoá các constraints trên owner sau khi Bake
            incoming_constraints = cmds.listConnections(self.owner, source=True, destination=False, type="constraint") or []
            for c in list(set(incoming_constraints)):
                if cmds.objExists(c):
                    try:
                        cmds.delete(c)
                    except Exception:
                        pass
        
        # 4. Xóa các locator thừa
        self.cleanup_locators(loc_parent, loc_child)

    def cleanup_locators(self, loc_parent, loc_child):
        """Xóa locator thừa"""
        if loc_parent and cmds.objExists(loc_parent):
            cmds.delete(loc_parent)
        elif loc_child and cmds.objExists(loc_child):
            cmds.delete(loc_child)


class SpaceSwitcher(object):
    """
    Chuyển đổi không gian dẫn đường (Switch Target) tại frame hiện tại
    mà không thay đổi vị trí trực quan của đối tượng bị dẫn.
    """
    def __init__(self, owner, current_frame):
        self.owner = owner
        self.frame = current_frame

    def switch_to_target(self, new_target):
        """Chuyển đổi constraint của loc_parent sang Target mới"""
        baker = AnimationBaker(self.owner)
        loc_parent, _ = baker.find_locator_names()
        
        if not loc_parent:
            print(u"[SpaceSwitcher] Không tìm thấy loc_parent liên kết với %s" % self.owner)
            return False
            
        # Tìm và xóa constraint cũ trên loc_parent
        old_constraints = cmds.listConnections(loc_parent, type="parentConstraint") or []
        if old_constraints:
            cmds.delete(old_constraints)
            
        old_scale_constraints = cmds.listConnections(loc_parent, type="scaleConstraint") or []
        if old_scale_constraints:
            cmds.delete(old_scale_constraints)
            
        # Thiết lập thời gian hiện tại
        cmds.currentTime(self.frame, edit=True)
        
        # Tạo constraint mới với maintainOffset=True để giữ nguyên toạ độ không bị giật
        cmds.parentConstraint(new_target, loc_parent, maintainOffset=True)
        try:
            cmds.scaleConstraint(new_target, loc_parent, maintainOffset=True)
        except Exception:
            pass
            
        print(u"[SpaceSwitcher] Đã chuyển đổi driver của %s sang %s tại frame %d" % (
            loc_parent, new_target, self.frame))
        return True
