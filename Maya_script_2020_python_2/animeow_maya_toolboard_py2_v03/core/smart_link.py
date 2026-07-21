# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import re

def exception_to_unicode(e):
    try:
        msg = e.message if hasattr(e, 'message') and e.message else ""
        if not msg and e.args:
            msg = e.args[0]
        if isinstance(msg, unicode):
            return msg
        if isinstance(msg, bytes):
            return msg.decode('utf-8', errors='replace')
        return unicode(msg)
    except Exception:
        try:
            val = str(e)
            return val.decode('utf-8', errors='replace')
        except Exception:
            return unicode(e)

def get_extreme_frames(curve, tolerance=0.001):
    """Tim cac frame cuc tri (dinh/day) thuc su cua duong cong animation"""
    if not cmds.objExists(curve):
        return []
        
    keys = cmds.keyframe(curve, q=True, timeChange=True) or []
    values = cmds.keyframe(curve, q=True, valueChange=True) or []
    
    if len(keys) <= 2:
        return [int(round(k)) for k in keys]
        
    extreme_frames = []
    # Luon giu key dau va key cuoi
    extreme_frames.append(int(round(keys[0])))
    extreme_frames.append(int(round(keys[-1])))
    
    for i in range(1, len(keys) - 1):
        prev_val = values[i-1]
        curr_val = values[i]
        next_val = values[i+1]
        
        diff1 = curr_val - prev_val
        diff2 = next_val - curr_val
        
        # Neu doi chieu do doc (doi dau nhan) va su thay doi lon hon sai so tolerance
        if diff1 * diff2 < -1e-8:
            if abs(diff1) > tolerance or abs(diff2) > tolerance:
                extreme_frames.append(int(round(keys[i])))
                
    return list(set(extreme_frames))


def parent_to_animeow_group(node_name):
    """Dam bao node_name duoc dua vao group Animeow_locator"""
    grp = "Animeow_locator"
    if not cmds.objExists(grp):
        grp = cmds.group(em=True, name=grp)
    
    current_parent = cmds.listRelatives(node_name, parent=True)
    if not current_parent or current_parent[0] != grp:
        new_nodes = cmds.parent(node_name, grp)
        if new_nodes:
            return new_nodes[0]
    return node_name

def clean_empty_animeow_group():
    """Xoa group Animeow_locator neu no trong rong"""
    grp = "Animeow_locator"
    if cmds.objExists(grp):
        children = cmds.listRelatives(grp, children=True) or []
        if not children:
            cmds.delete(grp)


class SmartLinkManager(object):
    """
    Quan ly vong doi cap Locator (Hook & Offset) va chuyen doi Animation trong Maya.
    Hook (Parent Locator) theo duoi Target (vat dan).
    Offset (Child Locator) chua khoang cach tuong doi va nhan keyframe.
    """
    def __init__(self, owner, target):
        self.owner = owner
        self.target = target
        self.loc_parent = None
        self.loc_child = None

    def detect_existing_animation(self):
        """Kiem tra xem owner co san animation (keyframe) hay khong"""
        anim_curves = cmds.keyframe(self.owner, query=True, name=True)
        return bool(anim_curves)

    def record_world_animation(self, start_frame, end_frame):
        """Ghi hinh chuyen dong the gioi cua owner sang mot locator tam thoi bang Constraint & Bake"""
        # Tao locator tam
        loc_temp = cmds.spaceLocator(name="Anm_loc_temp_" + self.owner)[0]
        parent_to_animeow_group(loc_temp)
        
        # Tao parentConstraint tam thoi tu owner sang loc_temp
        const = cmds.parentConstraint(self.owner, loc_temp, maintainOffset=False)[0]
        scale_const = None
        try:
            scale_const = cmds.scaleConstraint(self.owner, loc_temp, maintainOffset=False)[0]
        except Exception:
            pass
            
        # Bake ket qua bang engine cuc nhanh cua Maya
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
        
        # Xoa constraint tam thoi
        cmds.delete(const)
        if scale_const and cmds.objExists(scale_const):
            cmds.delete(scale_const)
            
        return loc_temp

    def clear_owner_keyframes(self):
        """Xoa toan bo keyframe cu tren owner de giai phong toa do"""
        cmds.cutKey(self.owner, clear=True)

    def create_locator_pair(self):
        """Tao cap Locator Parent (Hook) va Child (Offset) tai vi tri the gioi cua owner hien tai"""
        # 1. Tao Parent (Hook)
        self.loc_parent = cmds.spaceLocator(name="Anm_loc_link_parent_" + self.owner)[0]
        cmds.matchTransform(self.loc_parent, self.owner, pos=True, rot=True)
        
        # 2. Tao Child (Offset)
        self.loc_child = cmds.spaceLocator(name="Anm_loc_link_child_" + self.owner)[0]
        cmds.matchTransform(self.loc_child, self.owner, pos=True, rot=True)
        
        # Thiet lap ty le hien thi cho de nhin trong viewport
        for axis in ['X', 'Y', 'Z']:
            cmds.setAttr(self.loc_parent + ".localScale" + axis, 2.0)
            cmds.setAttr(self.loc_child + ".localScale" + axis, 1.2)
            
        # 3. Long lam cha con
        cmds.parent(self.loc_child, self.loc_parent)
        
        # Dua vao group quan ly chung
        parent_to_animeow_group(self.loc_parent)
        
        return self.loc_parent, self.loc_child

    def apply_constraint_to_target(self):
        """Gan parentConstraint & scaleConstraint tu target (vat dan) toi loc_parent"""
        if self.target.lower() == "world":
            print("[SmartLink] Dang lien ket %s vao Khong gian the gioi (World Space)." % self.owner)
            return
            
        cmds.parentConstraint(self.target, self.loc_parent, maintainOffset=True)
        try:
            cmds.scaleConstraint(self.target, self.loc_parent, maintainOffset=True)
        except Exception:
            pass

    def apply_constraint_to_owner(self):
        """Gan parentConstraint & scaleConstraint tu loc_child toi owner (vat bi dan)"""
        cmds.parentConstraint(self.loc_child, self.owner, maintainOffset=True)
        try:
            cmds.scaleConstraint(self.loc_child, self.owner, maintainOffset=True)
        except Exception:
            pass

    def match_animation_to_child(self, loc_temp, start_frame, end_frame):
        """Khop chuyen dong tu loc_temp sang loc_child bang parentConstraint va bakeResults"""
        # Tao constraint tam thoi tu loc_temp sang loc_child
        const = cmds.parentConstraint(loc_temp, self.loc_child, maintainOffset=False)[0]
        scale_const = None
        try:
            scale_const = cmds.scaleConstraint(loc_temp, self.loc_child, maintainOffset=False)[0]
        except Exception:
            pass
            
        # Bake ket qua truc tiep sang loc_child (Maya tu dong tinh toan toa do cuc bo duoi loc_parent)
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
        
        # Xoa constraint tam thoi
        cmds.delete(const)
        if scale_const and cmds.objExists(scale_const):
            cmds.delete(scale_const)

    def reset_owner_transforms(self):
        """Dua toa do cuc bo cua owner ve mac dinh (0 cho dich chuyen/xoay, 1 cho scale)"""
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
        """Xoa locator tam"""
        if loc_temp and cmds.objExists(loc_temp):
            cmds.delete(loc_temp)
        clean_empty_animeow_group()


class AnimationBaker(object):
    """
    Chiu trach nhiem Bake (Bake) chuyen dong tu locator sang keyframe thuc tren vat the
    va don dep sach se cac constraints/locator thua.
    """
    def __init__(self, owner):
        self.owner = owner

    def find_locator_names(self):
        """Tim cap Locator dang lien ket voi owner"""
        loc_parent = "Anm_loc_link_parent_" + self.owner
        loc_child = "Anm_loc_link_child_" + self.owner
        
        # Neu khong tim thay truc tiep theo ten, quet nguoc qua cac constraint
        if not cmds.objExists(loc_child):
            constraints = cmds.listConnections(self.owner, type="parentConstraint") or []
            for con in constraints:
                targets = cmds.parentConstraint(con, query=True, targetList=True) or []
                for target in targets:
                    if "Anm_loc_link_child_" in target or "loc_child_" in target:
                        loc_child = target
                        parents = cmds.listRelatives(loc_child, parent=True) or []
                        if parents and ("Anm_loc_link_parent_" in parents[0] or "loc_parent_" in parents[0]):
                            loc_parent = parents[0]
                        break
        
        return (loc_parent if cmds.objExists(loc_parent) else None,
                loc_child if cmds.objExists(loc_child) else None)

    def bake(self, start_frame, end_frame, step=1, smart_clean=True, clean_threshold=0.05):
        """Bake chuyen dong va don dep"""
        # 1. Dinh vi locators
        loc_parent, loc_child = self.find_locator_names()
        
        # Tu dong toi uu hoa khoang bake dua tren pham vi keyframe thuc te cua locator
        # de tranh bi mat animation truoc/sau timeline hien thi khi xoa constraint
        if loc_child and cmds.objExists(loc_child):
            all_loc_keys = cmds.keyframe(loc_child, q=True, timeChange=True) or []
            if all_loc_keys:
                loc_min = min(all_loc_keys)
                loc_max = max(all_loc_keys)
                start_frame = min(start_frame, loc_min)
                end_frame = max(end_frame, loc_max)
        
        # Quet them keyframe tren target (vat dan goc cua loc_parent) de mo rong thoi gian
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
            # Thu thap cac frame theo luoi Grid Step (vi du step=2: 1, 3, 5, 7...)
            grid_frames = set(range(int(start_frame), int(end_frame) + 1, step))
            
            # Thu thap cac keyframe nguon tu locator hoac cac vat dan cua constraint
            source_keyframes = set()
            targets_to_scan = []
            if loc_child and cmds.objExists(loc_child):
                targets_to_scan.append(loc_child)
            else:
                for con in incoming_constraints:
                    # Lay cac ket noi dau vao (drivers) cua constraint
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
            
            # Tap hop cac frame can giu lai (Hop cua luoi Grid va Keyframe nguon)
            keep_frames = grid_frames.union(source_keyframes)
            
            # Bake voi step = 1 de ghi nhan day du chuyen dong chinh xac nhat
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
            
            # Xoa cac constraints tren owner sau khi Bake
            for c in list(set(incoming_constraints)):
                if cmds.objExists(c):
                    try:
                        cmds.delete(c)
                    except Exception:
                        pass
            
            # Loc bo cac keyframe tho khong nam trong danh sach keep_frames
            all_keys = cmds.keyframe(self.owner, q=True, timeChange=True) or []
            all_keys = sorted(list(set([int(round(k)) for k in all_keys])))
            delete_frames = [k for k in all_keys if start_frame <= k <= end_frame and k not in keep_frames]
            
            if delete_frames:
                cmds.selectKey(self.owner, clear=True)
                for k in delete_frames:
                    cmds.selectKey(self.owner, add=True, time=(k, k))
                cmds.cutKey(animation="keysOrObjects", clear=True)
            
            print("[SmartLink] Da bake toi uu giu Grid (buoc %d) va giu nguyen cac key cuc tri nguon." % step)
            
        else:
            # Bake thuan tuy theo buoc nhay (Step) khong them key cuc tri nguon nam ngoai luoi
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
            
            # Xoa cac constraints tren owner sau khi Bake
            incoming_constraints = cmds.listConnections(self.owner, source=True, destination=False, type="constraint") or []
            for c in list(set(incoming_constraints)):
                if cmds.objExists(c):
                    try:
                        cmds.delete(c)
                    except Exception:
                        pass
        
        # 4. Xoa cac locator thua
        self.cleanup_locators(loc_parent, loc_child)

    def cleanup_locators(self, loc_parent, loc_child):
        """Xoa locator thua"""
        if loc_parent and cmds.objExists(loc_parent):
            cmds.delete(loc_parent)
        elif loc_child and cmds.objExists(loc_child):
            cmds.delete(loc_child)
        clean_empty_animeow_group()


class SpaceSwitcher(object):
    """
    Chuyen doi khong gian dan duong (Switch Target) tai frame hien tai
    ma khong thay doi vi tri truc quan cua doi tuong bi dan.
    """
    def __init__(self, owner, current_frame):
        self.owner = owner
        self.frame = current_frame

    def switch_to_target(self, new_target):
        """Chuyen doi constraint cua loc_parent sang Target moi"""
        baker = AnimationBaker(self.owner)
        loc_parent, _ = baker.find_locator_names()
        
        if not loc_parent:
            print("[SpaceSwitcher] Khong tim thay loc_parent lien ket voi %s" % self.owner)
            return False
            
        # Tim va xoa constraint cu tren loc_parent
        old_constraints = cmds.listConnections(loc_parent, type="parentConstraint") or []
        if old_constraints:
            cmds.delete(old_constraints)
            
        old_scale_constraints = cmds.listConnections(loc_parent, type="scaleConstraint") or []
        if old_scale_constraints:
            cmds.delete(old_scale_constraints)
            
        # Thiet lap thoi gian hien tai
        cmds.currentTime(self.frame, edit=True)
        
        # Tao constraint moi voi maintainOffset=True de giu nguyen toa do khong bi giat
        cmds.parentConstraint(new_target, loc_parent, maintainOffset=True)
        try:
            cmds.scaleConstraint(new_target, loc_parent, maintainOffset=True)
        except Exception:
            pass
            
        print("[SpaceSwitcher] Da chuyen doi driver cua %s sang %s tai frame %d" % (
            loc_parent, new_target, self.frame))
        return True
