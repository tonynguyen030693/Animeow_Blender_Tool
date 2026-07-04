# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import maya.cmds as cmds
import maya.mel as mel

class PlayblastManager(object):
    """
    Class quản lý làm sạch viewport và tự động xuất playblast.
    Hỗ trợ xuất video nháp và video publish.
    """
    FLAGS_TO_HIDE = {
        "nurbsCurves": False,      # Ẩn controls
        "joints": False,           # Ẩn xương
        "locators": False,         # Ẩn locators
        "cameras": False,          # Ẩn camera phụ
        "ikHandles": False,        # Ẩn IK handles
        "dimensions": False,       # Ẩn thước đo
        "pivots": False,           # Ẩn tâm
        "handles": False,          # Ẩn tay cầm
        "grid": False,             # Ẩn lưới nền
        "manipulators": False,     # Ẩn bộ điều khiển di chuyển
        "lights": False,           # Ẩn đèn
        "strokes": False,          # Ẩn nét vẽ Paint Effects
        "textures": False,         # Tắt hiển thị texture
    }

    def __init__(self):
        pass

    def get_active_model_panel(self):
        """Lấy tên panel Viewport đang hoạt động"""
        active_panel = cmds.playblast(query=True, activeEditor=True)
        if not active_panel:
            focus_panel = cmds.getPanel(withFocus=True)
            if focus_panel and cmds.getPanel(typeOf=focus_panel) == "modelPanel":
                active_panel = focus_panel
            else:
                panels = cmds.getPanel(type="modelPanel")
                if panels:
                    active_panel = panels[0]
        return active_panel

    def setup_viewport(self, panel):
        """Làm sạch Viewport: Lưu trạng thái cũ và ẩn các rig controls"""
        if not panel:
            return {}
            
        original_states = {}
        for flag in self.FLAGS_TO_HIDE:
            try:
                original_states[flag] = cmds.modelEditor(panel, query=True, **{flag: True})
            except Exception:
                pass
                
        for flag, val in self.FLAGS_TO_HIDE.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass
                
        try:
            original_states["polymeshes"] = cmds.modelEditor(panel, query=True, polymeshes=True)
            cmds.modelEditor(panel, edit=True, polymeshes=True)
        except Exception:
            pass
            
        try:
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded")
        except Exception:
            pass
            
        return original_states

    def restore_viewport(self, panel, original_states):
        """Khôi phục lại trạng thái hiển thị ban đầu"""
        if not panel or not original_states:
            return
            
        for flag, val in original_states.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass

    def get_active_sound(self):
        """Tìm âm thanh hoạt động trên Time Slider"""
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
        """Tự động tính toán đường dẫn lưu video playblast nháp hàng ngày"""
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            return None, None
            
        dirname = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        filename_no_ext, _ = os.path.splitext(filename)
        
        parent_dir = os.path.basename(dirname) # "Layout" hoặc "Anim"
        grandparent_dir = os.path.basename(os.path.dirname(dirname)) # "WorkingFile"
        
        if parent_dir.lower() in ["layout", "anim"] and grandparent_dir.lower() == "workingfile":
            # Đi ngược 3 cấp để lấy thư mục tập phim
            ep_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_filepath)))
            task_dir_name = "Layout" if parent_dir.lower() == "layout" else "Anim"
            playblast_dir = os.path.join(ep_dir, "mov", task_dir_name)
        else:
            playblast_dir = os.path.join(dirname, "mov")
            
        if not os.path.exists(playblast_dir):
            os.makedirs(playblast_dir)
            
        return playblast_dir, filename_no_ext

    def run_playblast(self, format_ext="qt", percent=100, width=1920, height=1080, custom_path=None):
        """Chạy playblast tự động (hỗ trợ lưu nháp hoặc publish tùy chọn)"""
        if custom_path:
            playblast_dir = os.path.dirname(custom_path)
            output_filepath = custom_path
            if not os.path.exists(playblast_dir):
                os.makedirs(playblast_dir)
        else:
            playblast_dir, base_name = self.get_playblast_path()
            if not playblast_dir:
                cmds.warning("Hãy lưu file trước khi chạy Playblast để tự động xác định thư mục.")
                return None
                
            available_formats = cmds.playblast(query=True, format=True)
            
            fmt = "qt"
            compression = "H.264"
            ext = ".mov"
            
            if format_ext == "avi":
                if "avi" in available_formats:
                    fmt = "avi"
                    compression = "none"
                    ext = ".avi"
                else:
                    cmds.warning("Định dạng AVI không khả dụng. Chuyển sang QuickTime.")
            else:
                if "qt" not in available_formats:
                    if "avi" in available_formats:
                        fmt = "avi"
                        compression = "none"
                        ext = ".avi"
                    else:
                        fmt = available_formats[0]
                        compression = "none"
                        ext = ".avi"
                        
            output_filename = base_name + ext
            output_filepath = os.path.join(playblast_dir, output_filename)
        
        panel = self.get_active_model_panel()
        original_states = self.setup_viewport(panel)
        
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        active_sound = self.get_active_sound()
        
        # Xác định format dựa trên phần mở rộng của file
        available_formats = cmds.playblast(query=True, format=True)
        fmt = "qt"
        compression = "H.264"
        
        if output_filepath.lower().endswith(".avi"):
            fmt = "avi"
            compression = "none"
        else:
            if "qt" not in available_formats:
                fmt = "avi" if "avi" in available_formats else available_formats[0]
                compression = "none"
                # Đổi đuôi file
                base, _ = os.path.splitext(output_filepath)
                output_filepath = base + (".avi" if fmt == "avi" else ".mov")
                
        playblast_args = {
            "filename": output_filepath,
            "format": fmt,
            "compression": compression,
            "sequenceTime": False,
            "clearCache": True,
            "viewer": True,
            "showOrnaments": True,
            "percent": percent,
            "widthHeight": [width, height],
            "forceOverwrite": True,
            "startTime": start_frame,
            "endTime": end_frame
        }
        
        if active_sound:
            playblast_args["sound"] = active_sound
            
        print("Bắt đầu chạy Playblast: %s" % output_filepath)
        try:
            cmds.playblast(**playblast_args)
        except Exception as e:
            cmds.error("Lỗi khi chạy Playblast: %s" % str(e))
        finally:
            self.restore_viewport(panel, original_states)
            
        print("Đã xuất Playblast thành công tại: %s" % output_filepath)
        return output_filepath
