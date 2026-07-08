# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

class ArcTracker(object):
    """
    Hệ thống vẽ Arc Tracker (Motion Trail) siêu nhẹ bằng cách trích xuất tọa độ
    từ ma trận thế giới (World Matrix) tại mỗi frame mà không làm thay đổi time slider,
    giúp tối ưu hóa tốc độ và không gây lag viewport trong Maya.
    """
    GROUP_NAME = "Animeow_ArcTracker_Grp"
    
    def __init__(self):
        pass
        
    def get_world_position_at_frame(self, obj, frame):
        """Lấy tọa độ thế giới (X, Y, Z) của đối tượng tại frame cụ thể bằng worldMatrix"""
        try:
            matrix = cmds.getAttr("%s.worldMatrix[0]" % obj, time=frame)
            if matrix and len(matrix) == 16:
                # Tọa độ tịnh tiến X, Y, Z nằm ở vị trí index 12, 13, 14
                return [matrix[12], matrix[13], matrix[14]]
        except Exception:
            pass
            
        # Phương án dự phòng nếu không lấy được worldMatrix
        try:
            curr_time = cmds.currentTime(q=True)
            cmds.currentTime(frame, edit=True)
            pos = cmds.xform(obj, q=True, ws=True, rp=True)
            cmds.currentTime(curr_time, edit=True)
            return pos
        except Exception:
            return [0.0, 0.0, 0.0]

    def clear_all_trails(self):
        """Xóa sạch toàn bộ các Arc Trail hiện có"""
        if cmds.objExists(self.GROUP_NAME):
            try:
                cmds.delete(self.GROUP_NAME)
                print("[ArcTracker] Đã xóa toàn bộ Arc Trails.")
            except Exception as e:
                print("[ArcTracker] Không thể xóa group ArcTracker: %s" % str(e))

    def clear_selected_trails(self, selected_objs):
        """Xóa trail của các vật thể được chọn"""
        if not selected_objs:
            return
            
        for obj in selected_objs:
            clean_name = obj.replace(":", "_").replace("|", "_")
            specific_grp = "%s_%s_Trail" % (self.GROUP_NAME, clean_name)
            if cmds.objExists(specific_grp):
                try:
                    cmds.delete(specific_grp)
                    print("[ArcTracker] Đã xóa trail cho %s" % obj)
                except Exception:
                    pass

    def create_trail(self, obj, start_frame, end_frame, show_ticks=True, show_keys=True, tick_size=0.1):
        """Tạo Arc Trail tĩnh siêu nhẹ cho đối tượng cụ thể"""
        if not cmds.objExists(obj):
            cmds.warning("Đối tượng %s không tồn tại!" % obj)
            return
            
        clean_name = obj.replace(":", "_").replace("|", "_")
        specific_grp = "%s_%s_Trail" % (self.GROUP_NAME, clean_name)
        
        # Xóa trail cũ của vật thể này nếu đã tồn tại
        if cmds.objExists(specific_grp):
            try:
                cmds.delete(specific_grp)
            except Exception:
                pass
                
        # Đảm bảo group tổng tồn tại
        if not cmds.objExists(self.GROUP_NAME):
            cmds.group(em=True, name=self.GROUP_NAME)
            # Khóa các thuộc tính transform của group tổng để tránh di chuyển nhầm
            for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                cmds.setAttr("%s.%s" % (self.GROUP_NAME, attr), lock=True)
                
        # Tạo group riêng cho vật thể này
        obj_trail_grp = cmds.group(em=True, name=specific_grp)
        cmds.parent(obj_trail_grp, self.GROUP_NAME)
        
        # Dò tìm các frame có keyframe của đối tượng để hiển thị đặc biệt
        keyframe_times = []
        try:
            keys = cmds.keyframe(obj, query=True, timeChange=True) or []
            keyframe_times = sorted(list(set([int(k) for k in keys])))
        except Exception:
            pass
            
        points = []
        frames = range(int(start_frame), int(end_frame) + 1)
        
        # Thu thập dữ liệu tọa độ cực nhanh
        for frame in frames:
            pos = self.get_world_position_at_frame(obj, frame)
            points.append(pos)
            
        if len(points) < 2:
            cmds.warning("Không đủ khung hình để tạo trail cho %s!" % obj)
            return
            
        # 1. Tạo đường cong NURBS Curve vẽ đường dẫn (Path)
        curve_name = "%s_Path" % specific_grp
        curve_path = cmds.curve(d=1, p=points, name=curve_name)
        cmds.parent(curve_path, obj_trail_grp)
        
        # Bật hiển thị Override Color cho đường dẫn (màu Cyan nổi bật)
        cmds.setAttr("%s.overrideEnabled" % curve_path, 1)
        cmds.setAttr("%s.overrideColor" % curve_path, 18) # Màu Cyan nhạt trong Maya
        
        # 2. Tạo các điểm Ticks đánh dấu tại mỗi khung hình
        if show_ticks or show_keys:
            ticks_grp = cmds.group(em=True, name="%s_Ticks" % specific_grp)
            cmds.parent(ticks_grp, obj_trail_grp)
            
            for idx, frame in enumerate(frames):
                pos = points[idx]
                is_key = int(frame) in keyframe_times
                
                # Bỏ qua nếu tắt tick thường và frame hiện tại không phải keyframe
                if not is_key and not show_ticks:
                    continue
                # Bỏ qua nếu tắt keyframe tick và frame hiện tại là keyframe
                if is_key and not show_keys:
                    continue
                    
                # Tạo một locator nhỏ làm điểm đánh dấu
                tick_name = "%s_F%d" % (specific_grp, frame)
                loc = cmds.spaceLocator(name=tick_name)[0]
                cmds.parent(loc, ticks_grp)
                cmds.move(pos[0], pos[1], pos[2], loc)
                
                # Điều chỉnh kích thước locator
                cmds.setAttr("%s.scaleX" % loc, tick_size)
                cmds.setAttr("%s.scaleY" % loc, tick_size)
                cmds.setAttr("%s.scaleZ" % loc, tick_size)
                
                # Bật Override Color
                cmds.setAttr("%s.overrideEnabled" % loc, 1)
                
                if is_key:
                    # Nếu là keyframe, tô màu đỏ rực rỡ (màu 13) và phóng to lên một chút
                    cmds.setAttr("%s.overrideColor" % loc, 13)
                    cmds.setAttr("%s.scaleX" % loc, tick_size * 1.5)
                    cmds.setAttr("%s.scaleY" % loc, tick_size * 1.5)
                    cmds.setAttr("%s.scaleZ" % loc, tick_size * 1.5)
                else:
                    # Ticks thường: tô màu vàng ấm áp (màu 17)
                    cmds.setAttr("%s.overrideColor" % loc, 17)
                    
        # Chọn lại đối tượng gốc để animator tiếp tục làm việc
        cmds.select(obj)
        print("[ArcTracker] Đã vẽ Arc Trail thành công cho %s từ frame %d đến %d." % (obj, start_frame, end_frame))
