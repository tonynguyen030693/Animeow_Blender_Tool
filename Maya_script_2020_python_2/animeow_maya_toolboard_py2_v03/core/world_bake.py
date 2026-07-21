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
        return "Loi he thong"

def parent_to_animeow_group(node_name):
    """Dam bao node_name duoc dua vao group Animeow_locator"""
    grp = "Animeow_locator"
    if not cmds.objExists(grp):
        grp = cmds.group(em=True, name=grp)
    
    current_parent = cmds.listRelatives(node_name, parent=True)
    if not current_parent or current_parent[0] != grp:
        new_nodes = cmds.parent(node_name, grp)
        return new_nodes[0] if new_nodes else node_name
    return node_name

def clean_empty_animeow_group():
    """Xoa group Animeow_locator neu no trong rong"""
    grp = "Animeow_locator"
    if cmds.objExists(grp):
        children = cmds.listRelatives(grp, children=True) or []
        if not children:
            cmds.delete(grp)


def get_incoming_constraints(obj):
    """Tim tat ca cac constraint node truc tiep hoac gian tiep (qua pairBlend) dang rang buoc obj"""
    if not cmds.objExists(obj):
        return []
        
    found_constraints = []
    
    # 1. Tim cac constraint ket noi truc tiep (source)
    direct_cons = cmds.listConnections(obj, source=True, destination=False, type="constraint") or []
    found_constraints.extend(direct_cons)
    
    # 2. Tim qua pairBlend nodes (du lieu di tu Constraint -> pairBlend -> Object)
    pair_blends = cmds.listConnections(obj, source=True, destination=False, type="pairBlend") or []
    for pb in pair_blends:
        pb_cons = cmds.listConnections(pb, source=True, destination=False, type="constraint") or []
        found_constraints.extend(pb_cons)
        
    return list(set(found_constraints))

def get_pair_blend_nodes(obj):
    """Tim tat ca pairBlend nodes dau vao cua obj"""
    if not cmds.objExists(obj):
        return []
    return cmds.listConnections(obj, source=True, destination=False, type="pairBlend") or []

def get_extreme_frames(curve, tolerance=0.001):
    """Tim cac frame cuc tri (dinh/day) thuc su cua duong cong animation"""
    if not cmds.objExists(curve):
        return []
        
    keys = cmds.keyframe(curve, q=True, timeChange=True) or []
    values = cmds.keyframe(curve, q=True, valueChange=True) or []
    
    if len(keys) <= 2:
        return [int(round(k)) for k in keys]
        
    extreme_frames = []
    extreme_frames.append(int(round(keys[0])))
    extreme_frames.append(int(round(keys[-1])))
    
    for i in range(1, len(keys) - 1):
        prev_val = values[i-1]
        curr_val = values[i]
        next_val = values[i+1]
        
        diff1 = curr_val - prev_val
        diff2 = next_val - curr_val
        
        if diff1 * diff2 < -1e-8:
            if abs(diff1) > tolerance or abs(diff2) > tolerance:
                extreme_frames.append(int(round(keys[i])))
                
    return list(set(extreme_frames))

def smart_bake_object(obj, start_frame, end_frame, step=1, smart_clean=True, channels='both', smart_bake=False, source_obj=None):
    """
    Bake (Bake) chuyen dong cho vat the, ho tro Bake theo luoi Grid,
    bao toan keyframe cuc tri hoac chi Bake tai cac frame co key cua source_obj (Smart Bake).
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

    incoming_constraints = get_incoming_constraints(obj)

    # 1. Khoi tao luoi Grid
    grid_frames = set(range(int(start_frame), int(end_frame) + 1, step))
    
    # 2. Xac dinh cac frame can giu lai (keep_frames)
    keep_frames = set()
    
    if smart_bake and source_obj and cmds.objExists(source_obj):
        # Che do Smart Bake (Key-on-key): Chi lay cac frame co key tu source_obj
        source_keys = cmds.keyframe(source_obj, query=True, timeChange=True) or []
        source_keys = set(int(round(k)) for k in source_keys)
        keep_frames = set(k for k in source_keys if start_frame <= k <= end_frame)
        # Giu lai start & end frame de chan hai dau
        keep_frames.add(int(start_frame))
        keep_frames.add(int(end_frame))
    elif smart_clean:
        # Che do Smart Clean: Grid step + Extreme keys cua driver
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
                        
        keep_frames = grid_frames.union(source_keyframes)

    # 3. Thuc hien Bake tho o buoc nhay 1
    if smart_bake or smart_clean:
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
        
        # 4. Xoa cac constraints va pairBlend dau vao
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try: cmds.delete(c)
                except Exception: pass
        pair_blends = get_pair_blend_nodes(obj)
        for pb in pair_blends:
            if cmds.objExists(pb):
                try: cmds.delete(pb)
                except Exception: pass
                
        # 5. Xoa cac keyframe thua ngoai keep_frames
        all_keys = cmds.keyframe(obj, q=True, timeChange=True) or []
        all_keys = sorted(list(set([int(round(k)) for k in all_keys])))
        for k in all_keys:
            if k < start_frame or k > end_frame:
                continue
            if k not in keep_frames:
                cmds.cutKey(obj, time=(k, k), option="keys", clear=True)
    else:
        # Bake thuan tuy theo buoc nhay (Step)
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
        
        for c in list(set(incoming_constraints)):
            if cmds.objExists(c):
                try: cmds.delete(c)
                except Exception: pass
        pair_blends = get_pair_blend_nodes(obj)
        for pb in pair_blends:
            if cmds.objExists(pb):
                try: cmds.delete(pb)
                except Exception: pass

class WorldBakeManager(object):
    """
    Quan ly Bake chuyen dong sang khong gian the gioi thong qua Locator
    va tra nguoc lai vat the goc, ho tro loc kenh (Translate, Rotate, Both)
    va bao toan keyframe cuc tri / Bake theo key cua doi tuong nguon.
    """
    PREFIX = "Anm_loc_bake_"
    
    def __init__(self):
        pass

    def get_clean_name(self, name):
        short_name = name.split("|")[-1]
        return short_name.replace(":", "_")

    def get_associated_locator(self, obj):
        """Tra ve locator the gioi lien ket voi obj neu da duoc bake truoc do, nguoc lai tra ve None"""
        if not cmds.objExists(obj):
            return None
            
        # 1. Kiem tra qua ket noi message
        connections = cmds.listConnections(obj + ".message", source=False, destination=True) or []
        for conn in connections:
            if self.PREFIX in conn and cmds.attributeQuery('animeow_bakeSource', node=conn, exists=True):
                return conn
                
        # 2. Kiem tra qua ten locator mac dinh
        clean_name = self.get_clean_name(obj)
        locator_name = "%s%s" % (self.PREFIX, clean_name)
        if cmds.objExists(locator_name):
            return locator_name
            
        return None

    def is_already_baked(self, obj):
        """Kiem tra xem vat the da duoc bake sang locator chua"""
        return self.get_associated_locator(obj) is not None

    def bake_to_locator(self, obj, start_frame, end_frame, step=1, smart_clean=True, channels='both', smart_bake=False, custom_name=None, no_constraint=False):
        """Bake vat the sang mot locator o khong gian the gioi"""
        if not cmds.objExists(obj):
            raise RuntimeError("Vat the %s khong ton tai!" % obj)
            
        clean_name = self.get_clean_name(obj)
        locator_name = custom_name if custom_name else ("%s%s" % (self.PREFIX, clean_name))
        
        # Xoa locator trung cu neu co
        old_locs = cmds.ls(locator_name, long=True) or []
        for old in old_locs:
            if cmds.objExists(old):
                try:
                    cmds.delete(old)
                except Exception:
                    pass
                
        # 1. Tao locator moi tai vi tri vat the
        loc = cmds.spaceLocator(name=locator_name)[0]
        cmds.matchTransform(loc, obj, pos=True, rot=True)
        cmds.setAttr(loc + ".rotateOrder", cmds.getAttr(obj + ".rotateOrder"))
        
        for axis in ['X','Y','Z']:
            cmds.setAttr(loc + ".localScale" + axis, 1.5)
            
        # Dua vao group quan ly chung
        loc = parent_to_animeow_group(loc)
        
        # Ghi nhan ket noi
        cmds.addAttr(loc, longName='animeow_bakeSource', attributeType='message')
        cmds.connectAttr(obj + '.message', loc + '.animeow_bakeSource')
        
        # 2. Tao rang buoc tam thoi tu vat the goc sang locator
        temp_con = cmds.parentConstraint(obj, loc, maintainOffset=False)[0]
        
        # 3. Bake animation len locator va toi uu keyframe
        try:
            smart_bake_object(loc, start_frame, end_frame, step, smart_clean, channels, smart_bake=smart_bake, source_obj=obj)
        finally:
            if cmds.objExists(temp_con):
                try:
                    cmds.delete(temp_con)
                except Exception:
                    pass
                    
        # 4. Tao rang buoc nguoc lai tu locator sang vat the goc theo kenh duoc chon
        if not no_constraint:
            if channels == 'translate':
                cmds.pointConstraint(loc, obj, maintainOffset=True)
            elif channels == 'rotate':
                cmds.orientConstraint(loc, obj, maintainOffset=True)
            else: # both
                cmds.parentConstraint(loc, obj, maintainOffset=True)
            
        print("[WorldBake] Da bake thanh cong %s sang locator %s." % (obj, loc))
        return loc

    def bake_from_locator(self, locator_or_obj, start_frame, end_frame, step=1, smart_clean=True, smart_bake=False):
        """Bake chuyen dong tu locator the gioi nguoc lai vat the goc va xoa locator"""
        if not cmds.objExists(locator_or_obj):
            raise RuntimeError("Khong tim thay vat the hoac locator!")
            
        locator = None
        obj = None
        
        if self.PREFIX in locator_or_obj:
            locator = locator_or_obj
            conns = cmds.listConnections(locator + '.animeow_bakeSource', destination=False) or []
            if conns:
                obj = conns[0]
        else:
            obj = locator_or_obj
            clean_name = self.get_clean_name(obj)
            possible_loc = "%s%s" % (self.PREFIX, clean_name)
            if cmds.objExists(possible_loc):
                locator = possible_loc
                
        if not locator or not obj or not cmds.objExists(locator) or not cmds.objExists(obj):
            constraints = get_incoming_constraints(locator_or_obj)
            for con in constraints:
                inputs = cmds.listConnections(con, source=True, destination=False) or []
                for inp in inputs:
                    if self.PREFIX in inp:
                        locator = inp
                        obj = locator_or_obj if locator_or_obj != locator else inp
                        break
                        
        if not locator or not obj:
            raise RuntimeError("Vui long chon Locator hoac vat the goc da duoc World Bake truoc do!")
            
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
            
        # Bake nguoc lai len vat the goc va toi uu
        smart_bake_object(obj, start_frame, end_frame, step, smart_clean, channels, smart_bake=smart_bake, source_obj=locator)
        
        # Xoa locator sau khi hoan thanh
        if cmds.objExists(locator):
            try:
                cmds.delete(locator)
            except Exception:
                pass
        clean_empty_animeow_group()
                
        print("[WorldBake] Da bake nguoc thanh cong tu %s vao %s." % (locator, obj))
        return obj
