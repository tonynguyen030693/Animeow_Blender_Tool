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
        if isinstance(msg, unicode):
            return msg
        return msg.decode('utf-8', errors='replace')
    except Exception:
        try:
            return str(e).decode('utf-8', errors='replace')
        except Exception:
            return u"Lỗi ngoại lệ hệ thống"

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

    def is_file_locked(self, filepath):
        """Kiểm tra xem file có bị khóa bởi ứng dụng khác không"""
        if not os.path.exists(filepath):
            return False
        
        import sys
        fs_path = filepath
        if isinstance(filepath, unicode):
            try:
                fs_path = filepath.encode(sys.getfilesystemencoding())
            except Exception:
                try:
                    fs_path = filepath.encode("utf-8")
                except Exception:
                    pass
        try:
            # Thử mở file ở chế độ ghi/append để kiểm tra lock
            f = open(fs_path, "a")
            f.close()
            return False
        except IOError:
            return True

    def run_playblast(self, format_ext="qt", percent=100, width=1920, height=1080, custom_path=None, camera=None, viewer=True):
        """Chạy playblast tự động (hỗ trợ lưu nháp hoặc publish tùy chọn, hỗ trợ chọn camera và cấu hình viewer)"""
        if custom_path:
            playblast_dir = os.path.dirname(custom_path)
            output_filepath = custom_path
            if not os.path.exists(playblast_dir):
                os.makedirs(playblast_dir)
        else:
            playblast_dir, base_name = self.get_playblast_path()
            if not playblast_dir:
                cmds.warning("Please save the file before running Playblast to automatically determine the output folder.")
                return None
                
            available_formats = cmds.playblast(query=True, format=True)
            
            fmt = "qt"
            ext = ".mov"
            
            if format_ext == "avi":
                if "avi" in available_formats:
                    fmt = "avi"
                    ext = ".avi"
                else:
                    cmds.warning("AVI format is not available. Switching to QuickTime.")
            else:
                if "qt" not in available_formats:
                    if "avi" in available_formats:
                        fmt = "avi"
                        ext = ".avi"
                    else:
                        fmt = available_formats[0]
                        ext = ".avi"
            
            # Bổ sung hậu tố tên camera nếu có chỉ định camera cụ thể
            if camera:
                clean_camera_name = camera.replace(":", "_").replace("|", "_")
                base_name = "%s_%s" % (base_name, clean_camera_name)
                        
            output_filename = base_name + ext
            output_filepath = os.path.normpath(os.path.join(playblast_dir, output_filename))
        
        # Kiểm tra file video đầu ra có bị khóa bởi trình phát video không
        if self.is_file_locked(output_filepath):
            raise RuntimeError(
                u"Cannot export video! The output video file is currently open or locked by another application:\n%s\n\n"
                u"Please close your video player (VLC, PotPlayer, Windows Media Player...) and try again." 
                % os.path.normpath(output_filepath)
            )
            
        # Kiểm tra quyền ghi/tạo file tại đường dẫn đích (đặc biệt hữu ích khi dùng ổ đĩa mạng)
        try:
            if not os.path.exists(output_filepath):
                with open(output_filepath, "w") as f:
                    f.write("")
                os.remove(output_filepath)
            else:
                with open(output_filepath, "r+") as f:
                    pass
        except Exception as we:
            raise RuntimeError(
                u"No permission to create or overwrite file in the Playblast output folder.\n"
                u"The LAN network drive may be disconnected or the folder has restricted write access:\n%s\n\n"
                u"System details: %s" % (os.path.normpath(output_filepath), exception_to_unicode(we))
            )

        panel = self.get_active_model_panel()
        original_states = self.setup_viewport(panel)
        
        # Nếu chỉ định camera, chuyển đổi camera của viewport
        original_camera = None
        if camera and panel:
            try:
                original_camera = cmds.modelEditor(panel, query=True, camera=True)
                if cmds.objExists(camera):
                    cmds.modelEditor(panel, edit=True, camera=camera)
                else:
                    cmds.warning("Camera does not exist: %s. Using the current camera." % camera)
                    camera = None
            except Exception as e:
                cmds.warning("Cannot switch camera to %s: %s" % (camera, str(e)))
                camera = None
        
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        active_sound = self.get_active_sound()
        
        # Xác định format dựa trên phần mở rộng của file
        available_formats = cmds.playblast(query=True, format=True)
        fmt = "qt"
        
        if output_filepath.lower().endswith(".avi"):
            fmt = "avi"
        else:
            if "qt" not in available_formats:
                fmt = "avi" if "avi" in available_formats else available_formats[0]
                # Đổi đuôi file
                base, _ = os.path.splitext(output_filepath)
                output_filepath = base + (".avi" if fmt == "avi" else ".mov")
                
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
            "filename": output_filepath,
            "format": fmt,
            "sequenceTime": False,
            "clearCache": True,
            "viewer": viewer,
            "showOrnaments": True,
            "percent": percent,
            "widthHeight": [width, height],
            "forceOverwrite": True,
            "startTime": start_frame,
            "endTime": end_frame
        }
        
        # Chỉ sử dụng compression nếu nó khác "none" và có giá trị hợp lệ
        if compression and compression != "none":
            playblast_args["compression"] = compression
            
        if active_sound:
            playblast_args["sound"] = active_sound
            
        # In thông tin cấu hình Playblast chi tiết phục vụ chẩn đoán lỗi
        print("\n[DEBUG PLAYBLAST] --- Playblast Configuration Details ---")
        print("[DEBUG PLAYBLAST] Output Path: %s" % output_filepath)
        print("[DEBUG PLAYBLAST] Format: %s" % fmt)
        print("[DEBUG PLAYBLAST] Compression: %s" % compression)
        print("[DEBUG PLAYBLAST] Viewer: %s" % viewer)
        print("[DEBUG PLAYBLAST] Resolution: %s x %s" % (width, height))
        print("[DEBUG PLAYBLAST] Frame range: %s -> %s" % (start_frame, end_frame))
        print("[DEBUG PLAYBLAST] Active Model Panel: %s" % panel)
        print("[DEBUG PLAYBLAST] Specified Camera: %s" % camera)
        print("[DEBUG PLAYBLAST] Active Sound: %s" % active_sound)
        print("[DEBUG PLAYBLAST] Available Formats: %s" % available_formats)
        print("[DEBUG PLAYBLAST] Available Compressions: %s" % available_compressions)
        print("[DEBUG PLAYBLAST] ----------------------------------------\n")
            
        # Thử chạy playblast với offScreen=True trước để tăng tốc độ và tránh lỗi kích thước viewport
        playblast_args["offScreen"] = True
        
        try:
            cmds.playblast(**playblast_args)
        except Exception as e1:
            err1_str = exception_to_unicode(e1)
            print("[DEBUG PLAYBLAST] offScreen=True failed. Details: %s" % err1_str)
            import traceback
            traceback.print_exc()
            
            # Thử lại với offScreen=False (chụp viewport trực tiếp)
            playblast_args["offScreen"] = False
            print("[DEBUG PLAYBLAST] Retrying with offScreen=False...")
            try:
                cmds.playblast(**playblast_args)
            except Exception as e2:
                import traceback
                error_trace = traceback.format_exc()
                err2_str = exception_to_unicode(e2)
                
                print("[DEBUG PLAYBLAST] offScreen=False failed as well!")
                print(error_trace)
                
                # Ném lỗi kèm theo traceback cụ thể để hiển thị lên hộp thoại UI
                raise RuntimeError(
                    "Maya Playblast Error!\n"
                    "Details: %s\n\n"
                    "System Traceback:\n%s" % (err2_str, error_trace)
                )
        finally:
            if panel:
                self.restore_viewport(panel, original_states)
                if original_camera:
                    try:
                        cmds.modelEditor(panel, edit=True, camera=original_camera)
                    except Exception:
                        pass
            
        print("Playblast exported successfully at: %s" % output_filepath)
        return output_filepath
