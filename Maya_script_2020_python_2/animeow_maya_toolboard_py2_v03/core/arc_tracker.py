# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

class ArcTracker(object):
    """
    He thong ve Arc Tracker (Motion Trail) sieu nhe bang cach trich xuat toa do
    tu ma tran the gioi (World Matrix) tai moi frame ma khong lam thay doi time slider,
    giup toi uu hoa toc do va khong gay lag viewport trong Maya.
    """
    GROUP_NAME = "Animeow_ArcTracker_Grp"
    
    def __init__(self):
        pass
        
    def get_world_position_at_frame(self, obj, frame):
        """Lay toa do the gioi (X, Y, Z) cua doi tuong tai frame cu the bang worldMatrix"""
        is_component = '.' in obj
        if not is_component:
            try:
                matrix = cmds.getAttr("%s.worldMatrix[0]" % obj, time=frame)
                if matrix and len(matrix) == 16:
                    # Toa do tinh tien X, Y, Z nam o vi tri index 12, 13, 14
                    return [matrix[12], matrix[13], matrix[14]]
            except Exception:
                pass
                
        # Phuong an du phong neu khong lay duoc worldMatrix hoac danh cho component
        try:
            curr_time = cmds.currentTime(q=True)
            cmds.currentTime(frame, edit=True)
            if is_component:
                pos = cmds.xform(obj, q=True, ws=True, translation=True)
            else:
                pos = cmds.xform(obj, q=True, ws=True, rp=True)
            cmds.currentTime(curr_time, edit=True)
            return pos
        except Exception:
            return [0.0, 0.0, 0.0]

    def clear_all_trails(self):
        """Xoa sach toan bo cac Arc Trail hien co"""
        if cmds.objExists(self.GROUP_NAME):
            try:
                cmds.delete(self.GROUP_NAME)
                print("[ArcTracker] Da xoa toan bo Arc Trails.")
            except Exception as e:
                print("[ArcTracker] Khong the xoa group ArcTracker: %s" % str(e))

    def clear_selected_trails(self, selected_objs):
        """Xoa trail cua cac vat the duoc chon"""
        if not selected_objs:
            return
            
        for obj in selected_objs:
            clean_name = obj.replace(":", "_").replace("|", "_")
            specific_grp = "%s_%s_Trail" % (self.GROUP_NAME, clean_name)
            if cmds.objExists(specific_grp):
                try:
                    cmds.delete(specific_grp)
                    print("[ArcTracker] Da xoa trail cho %s" % obj)
                except Exception:
                    pass

    def create_trail(self, obj, start_frame, end_frame, show_ticks=True, show_keys=True, tick_size=0.1):
        """Tao Arc Trail tinh sieu nhe cho doi tuong cu the"""
        if not cmds.objExists(obj):
            cmds.warning("Doi tuong %s khong ton tai!" % obj)
            return
            
        is_component = '.' in obj
        if is_component:
            node_name = obj.split('.')[0]
            component_suffix = "." + ".".join(obj.split('.')[1:])
            # Thay the ky tu dac biet de dat ten group hop le trong Maya
            clean_name = obj.replace(":", "_").replace("|", "_").replace(".", "_").replace("[", "_").replace("]", "_")
        else:
            node_name = obj
            component_suffix = ""
            clean_name = obj.replace(":", "_").replace("|", "_")
            
        specific_grp = "%s_%s_Trail" % (self.GROUP_NAME, clean_name)
        
        # Xoa trail cu cua vat the nay neu da ton tai
        if cmds.objExists(specific_grp):
            try:
                cmds.delete(specific_grp)
            except Exception:
                pass
                
        # Dam bao group tong ton tai
        if not cmds.objExists(self.GROUP_NAME):
            cmds.group(em=True, name=self.GROUP_NAME)
            # Khoa cac thuoc tinh transform cua group tong de tranh di chuyen nham
            for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                cmds.setAttr("%s.%s" % (self.GROUP_NAME, attr), lock=True)
                
        # Tao group rieng cho vat the nay
        obj_trail_grp = cmds.group(em=True, name=specific_grp)
        cmds.parent(obj_trail_grp, self.GROUP_NAME)
        
        # Luu thong tin vat the goc bang message connection
        cmds.addAttr(obj_trail_grp, longName='animeow_sourceObj', attributeType='message')
        cmds.connectAttr(node_name + '.message', obj_trail_grp + '.animeow_sourceObj')
        
        # Luu hau to component (neu co) vao thuoc tinh chuoi
        if is_component:
            cmds.addAttr(obj_trail_grp, longName='animeow_component', dataType='string')
            cmds.setAttr(obj_trail_grp + '.animeow_component', component_suffix, type='string')
        
        # Do tim cac frame co keyframe cua doi tuong de hien thi dac biet
        keyframe_times = []
        try:
            target_node = node_name if is_component else obj
            keys = cmds.keyframe(target_node, query=True, timeChange=True) or []
            keyframe_times = sorted(list(set([int(k) for k in keys])))
        except Exception:
            pass
            
        points = []
        frames = range(int(start_frame), int(end_frame) + 1)
        
        # Thu thap du lieu toa do chinh xac bang cach duyet qua cac khung hinh tuan tu
        # Su dung suspend=True de tranh giat lag viewport va dam bao Parallel Evaluation danh gia dung vi tri
        cmds.refresh(suspend=True)
        curr_time = cmds.currentTime(q=True)
        try:
            for frame in frames:
                cmds.currentTime(frame, edit=True)
                if is_component:
                    pos = cmds.xform(obj, q=True, ws=True, translation=True)
                else:
                    pos = cmds.xform(obj, q=True, ws=True, rp=True)
                points.append(pos)
        finally:
            cmds.currentTime(curr_time, edit=True)
            cmds.refresh(suspend=False)
            
        if len(points) < 2:
            cmds.warning("Khong du khung hinh de tao trail cho %s!" % obj)
            return
            
        # 1. Tao duong cong NURBS Curve ve duong dan (Path)
        curve_name = "%s_Path" % specific_grp
        curve_path = cmds.curve(d=1, p=points, name=curve_name)
        cmds.parent(curve_path, obj_trail_grp)
        
        # Bat hien thi Override Color cho duong dan (mau Cyan noi bat)
        cmds.setAttr("%s.overrideEnabled" % curve_path, 1)
        cmds.setAttr("%s.overrideColor" % curve_path, 18) # Mau Cyan nhat trong Maya
        
        # 2. Tao cac diem Ticks danh dau tai moi khung hinh
        if show_ticks or show_keys:
            ticks_grp = cmds.group(em=True, name="%s_Ticks" % specific_grp)
            cmds.parent(ticks_grp, obj_trail_grp)
            
            for idx, frame in enumerate(frames):
                pos = points[idx]
                is_key = int(frame) in keyframe_times
                
                # Bo qua neu tat tick thuong va frame hien tai khong phai keyframe
                if not is_key and not show_ticks:
                    continue
                # Bo qua neu tat keyframe tick va frame hien tai la keyframe
                if is_key and not show_keys:
                    continue
                    
                # Tao mot locator nho lam diem danh dau
                tick_name = "%s_F%d" % (specific_grp, frame)
                loc = cmds.spaceLocator(name=tick_name)[0]
                cmds.parent(loc, ticks_grp)
                cmds.move(pos[0], pos[1], pos[2], loc)
                
                # Dieu chinh kich thuoc locator
                cmds.setAttr("%s.scaleX" % loc, tick_size)
                cmds.setAttr("%s.scaleY" % loc, tick_size)
                cmds.setAttr("%s.scaleZ" % loc, tick_size)
                
                # Bat Override Color
                cmds.setAttr("%s.overrideEnabled" % loc, 1)
                
                if is_key:
                    # Neu la keyframe, to mau do ruc ro (mau 13) va phong to len mot chut
                    cmds.setAttr("%s.overrideColor" % loc, 13)
                    cmds.setAttr("%s.scaleX" % loc, tick_size * 2.0)
                    cmds.setAttr("%s.scaleY" % loc, tick_size * 2.0)
                    cmds.setAttr("%s.scaleZ" % loc, tick_size * 2.0)
                else:
                    # Ticks thuong: to mau vang am ap (mau 17)
                    cmds.setAttr("%s.overrideColor" % loc, 17)
                    
        # Chon lai doi tuong goc de animator tiep tuc lam viec
        cmds.select(obj)
        print("[ArcTracker] Da ve Arc Trail thanh cong cho %s tu frame %d den %d." % (obj, start_frame, end_frame))

    def update_trails(self, selected_objs=None, show_ticks=True, show_keys=True, tick_size=0.1):
        """
        Cap nhat cac trail. 
        Neu selected_objs khong trong: cap nhat/ve trail cho cac doi tuong duoc chon.
        Neu selected_objs trong: tu dong quet group tong va cap nhat tat ca trail dang hien thi trong canh.
        """
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        objects_to_update = []
        
        # 1. Neu co chon vat the cu the
        if selected_objs:
            objects_to_update = selected_objs
        # 2. Neu khong chon gi, tu dong quet tim tat ca cac trail hien huu trong canh
        else:
            if cmds.objExists(self.GROUP_NAME):
                children = cmds.listRelatives(self.GROUP_NAME, children=True, type="transform") or []
                for child in children:
                    attr_path = "%s.animeow_sourceObj" % child
                    if cmds.objExists(attr_path):
                        conns = cmds.listConnections(attr_path, destination=False) or []
                        if conns:
                            # Kiem tra xem co luu hau to component khong
                            comp_attr = "%s.animeow_component" % child
                            if cmds.objExists(comp_attr):
                                comp_suffix = cmds.getAttr(comp_attr) or ""
                                objects_to_update.append(conns[0] + comp_suffix)
                            else:
                                objects_to_update.append(conns[0])
                            
        # Loai bo cac doi tuong trung lap va thuc hien ve lai
        updated_count = 0
        for obj in list(set(objects_to_update)):
            if cmds.objExists(obj):
                self.create_trail(
                    obj=obj,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    show_ticks=show_ticks,
                    show_keys=show_keys,
                    tick_size=tick_size
                )
                updated_count += 1
                
        return updated_count
