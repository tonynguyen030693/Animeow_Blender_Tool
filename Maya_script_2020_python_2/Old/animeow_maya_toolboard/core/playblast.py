# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
import maya.mel as mel

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

class PlayblastManager(object):
    """
    Quản lý dọn dẹp viewport và xuất video Playblast chất lượng cao tự động.
    """
    FLAGS_TO_HIDE = {
        "nurbsCurves": False,      # Ẩn controls rig
        "joints": False,           # Ẩn xương
        "locators": False,         # Ẩn locators
        "cameras": False,          # Ẩn camera phụ
        "ikHandles": False,        # Ẩn IK handles
        "dimensions": False,       # Ẩn thước đo
        "pivots": False,           # Ẩn tâm xoay
        "handles": False,          # Ẩn handle
        "grid": False,             # Ẩn lưới nền
        "manipulators": False,     # Ẩn bộ điều khiển di chuyển
        "lights": False,           # Ẩn nguồn sáng
        "strokes": False,          # Ẩn nét vẽ Paint Effects
        "textures": False,         # Tắt hiển thị texture
    }

    def __init__(self):
        pass

    def get_active_model_panel(self):
        """Lấy panel viewport đang kích hoạt"""
        active_panel = None
        try:
            active_panel = cmds.playblast(query=True, activeEditor=True)
        except Exception:
            pass
            
        if not active_panel:
            try:
                focus_panel = cmds.getPanel(withFocus=True)
                if focus_panel and cmds.getPanel(typeOf=focus_panel) == "modelPanel":
                    active_panel = focus_panel
            except Exception:
                pass
                
        if not active_panel:
            try:
                panels = cmds.getPanel(type="modelPanel")
                if panels:
                    active_panel = panels[0]
            except Exception:
                pass
        return active_panel

    def setup_viewport(self, panel):
        """Làm sạch viewport để quay playblast đẹp mắt"""
        if not panel:
            return {}
            
        original_states = {}
        for flag in self.FLAGS_TO_HIDE:
            try:
                original_states[flag] = cmds.modelEditor(panel, query=True, **{flag: True})
            except Exception:
                pass
                
        # Ẩn các thành phần phụ trợ
        for flag, val in self.FLAGS_TO_HIDE.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass
                
        # Luôn bật hiển thị Mesh (polymeshes)
        try:
            original_states["polymeshes"] = cmds.modelEditor(panel, query=True, polymeshes=True)
            cmds.modelEditor(panel, edit=True, polymeshes=True)
        except Exception:
            pass
            
        # Chuyển viewport sang chế độ Smooth Shaded
        try:
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded")
        except Exception:
            pass
            
        return original_states

    def restore_viewport(self, panel, original_states):
        """Khôi phục trạng thái viewport ban đầu"""
        if not panel or not original_states:
            return
            
        for flag, val in original_states.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass

    def get_active_sound(self):
        """Tìm tệp âm thanh đang kích hoạt trên timeline"""
        active_sound = None
        try:
            g_slider = mel.eval("$tmpVar=$gPlayBackSlider")
            if cmds.timeControl(g_slider, exists=True):
                active_sound = cmds.timeControl(g_slider, query=True, sound=True)
        except Exception:
            sounds = cmds.ls(type="audio")
            if sounds:
                active_sound = sounds[0]
        return active_sound

    def get_playblast_path(self):
        """Tự động xác định đường dẫn lưu file playblast tương đối theo file maya đang mở"""
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            return None, None
            
        dirname = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        filename_no_ext, _ = os.path.splitext(filename)
        
        # Tạo thư mục mov cùng cấp hoặc cấu trúc cha
        playblast_dir = os.path.join(dirname, "mov")
        if not os.path.exists(playblast_dir):
            try:
                os.makedirs(playblast_dir)
            except Exception:
                pass
                
        return playblast_dir, filename_no_ext

    def is_file_locked(self, filepath):
        """Kiểm tra xem video đầu ra có đang bị chiếm quyền bởi trình phát video không"""
        if not os.path.exists(filepath):
            return False
            
        try:
            f = open(filepath, "a")
            f.close()
            return False
        except IOError:
            return True

    def archive_old_playblast(self, filepath):
        """Sao lưu tệp cũ vào thư mục Old trước khi nướng tệp mới"""
        if not os.path.exists(filepath):
            return
            
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name_no_ext, ext = os.path.splitext(filename)
        
        old_dir = os.path.join(dirname, "Old")
        if not os.path.exists(old_dir):
            os.makedirs(old_dir)
            
        i = 1
        while True:
            dest_filename = "%s_old%d%s" % (name_no_ext, i, ext)
            dest_filepath = os.path.join(old_dir, dest_filename)
            if not os.path.exists(dest_filepath):
                break
            i += 1
            
        try:
            os.rename(filepath, dest_filepath)
            print("[Playblast] Da sao luu video cu sang: %s" % dest_filepath)
        except Exception as e:
            print("[Playblast] Khong the sao luu video cu: %s" % str(e))

    def run_playblast(self, format_ext="qt", percent=100, width=1920, height=1080, camera=None, viewer=True, overwrite=False):
        """Thực thi quay Playblast"""
        playblast_dir, base_name = self.get_playblast_path()
        if not playblast_dir:
            raise RuntimeError("Vui lòng lưu file Maya hiện tại trước khi xuất Playblast!")
            
        available_formats = cmds.playblast(query=True, format=True)
        fmt = "qt"
        ext = ".mov"
        
        if format_ext == "avi":
            if "avi" in available_formats:
                fmt = "avi"
                ext = ".avi"
            else:
                cmds.warning("Định dạng AVI không khả dụng, tự động chuyển sang QuickTime.")
        else:
            if "qt" not in available_formats:
                if "avi" in available_formats:
                    fmt = "avi"
                    ext = ".avi"
                else:
                    fmt = available_formats[0]
                    ext = ".avi"
                    
        if camera:
            clean_camera_name = camera.replace(":", "_").replace("|", "_")
            base_name = "%s_%s" % (base_name, clean_camera_name)
            
        output_filename = base_name + ext
        output_filepath = os.path.normpath(os.path.join(playblast_dir, output_filename))
        
        # Sao lưu nếu không cho phép ghi đè trực tiếp
        if not overwrite and os.path.exists(output_filepath):
            self.archive_old_playblast(output_filepath)
            
        # Kiểm tra khoá file
        if self.is_file_locked(output_filepath):
            raise RuntimeError(
                "Không thể xuất video! Tệp video đầu ra đang được mở hoặc khoá bởi ứng dụng khác:\n%s\n\n"
                "Vui lòng đóng trình phát video (VLC, PotPlayer...) và thử lại." % output_filepath
            )
            
        panel = self.get_active_model_panel()
        original_states = self.setup_viewport(panel)
        
        original_camera = None
        if camera and panel:
            try:
                original_camera = cmds.modelEditor(panel, query=True, camera=True)
                cmds.modelEditor(panel, edit=True, camera=camera)
            except Exception:
                pass
                
        # Lấy âm thanh
        sound_node = self.get_active_sound()
        
        # Tính toán khung hình
        start_time = cmds.playbackOptions(query=True, minTime=True)
        end_time = cmds.playbackOptions(query=True, maxTime=True)
        
        # Lấy danh sách compression khả dụng cho format đã chọn trên hệ thống hiện tại
        available_compressions = []
        try:
            available_compressions = cmds.playblast(query=True, compression=True) or []
        except Exception:
            pass
            
        compression = "none"
        if fmt == "qt":
            # Ưu tiên H.264, sau đó đến các định dạng nén phổ biến, cuối cùng là none
            for opt in ["H.264", "png", "jpeg", "rle", "PNG", "JPEG"]:
                if opt in available_compressions:
                    compression = opt
                    break
            else:
                if available_compressions:
                    compression = available_compressions[0]
        else: # avi
            for opt in ["none", "IYUV codec", "MS-CVC"]:
                if opt in available_compressions:
                    compression = opt
                    break
            else:
                if available_compressions:
                    compression = available_compressions[0]
                    
        playblast_args = {
            "format": fmt,
            "filename": output_filepath,
            "forceOverwrite": True,
            "sequenceTime": False,
            "clearCache": True,
            "viewer": viewer,
            "showOrnaments": True,
            "percent": percent,
            "quality": 70,
            "widthHeight": [width, height],
            "startTime": start_time,
            "endTime": end_time,
        }
        
        if compression and compression != "none":
            playblast_args["compression"] = compression
            
        if sound_node:
            playblast_args["sound"] = sound_node
            
        print("\n[DEBUG PLAYBLAST] --- Thiet lap Playblast ---")
        print("[DEBUG PLAYBLAST] Output Path: %s" % output_filepath)
        print("[DEBUG PLAYBLAST] Format: %s" % fmt)
        print("[DEBUG PLAYBLAST] Compression: %s" % compression)
        print("[DEBUG PLAYBLAST] Available Compressions: %s" % available_compressions)
        print("[DEBUG PLAYBLAST] ----------------------------------------\n")
        
        # Thử chạy playblast với offScreen=True trước
        playblast_args["offScreen"] = True
        
        try:
            cmds.playblast(**playblast_args)
        except Exception as e1:
            print("[Playblast] offScreen=True that bai, dang thu lai voi offScreen=False...")
            playblast_args["offScreen"] = False
            try:
                cmds.playblast(**playblast_args)
            except Exception as e2:
                # Khôi phục trạng thái trước khi ném lỗi
                self.restore_viewport(panel, original_states)
                if original_camera and panel:
                    try:
                        cmds.modelEditor(panel, edit=True, camera=original_camera)
                    except Exception:
                        pass
                raise e2
        finally:
            # Khôi phục viewport và camera ban đầu
            self.restore_viewport(panel, original_states)
            if original_camera and panel:
                try:
                    cmds.modelEditor(panel, edit=True, camera=original_camera)
                except Exception:
                    pass
                    
        return output_filepath
