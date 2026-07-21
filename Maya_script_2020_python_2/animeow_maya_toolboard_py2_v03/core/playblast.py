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
        if isinstance(msg, bytes):
            return msg.decode('utf-8', errors='replace')
        return unicode(msg)
    except Exception:
        try:
            val = str(e)
            return val.decode('utf-8', errors='replace')
        except Exception:
            return unicode(e)

class PlayblastManager(object):
    """
    Quan ly don dep viewport va xuat video Playblast chat luong cao tu dong.
    """
    FLAGS_TO_HIDE = {
        "nurbsCurves": False,      # An controls rig
        "joints": False,           # An xuong
        "locators": False,         # An locators
        "cameras": False,          # An camera phu
        "ikHandles": False,        # An IK handles
        "dimensions": False,       # An thuoc do
        "pivots": False,           # An tam xoay
        "handles": False,          # An handle
        "grid": False,             # An luoi nen
        "manipulators": False,     # An bo dieu khien di chuyen
        "lights": False,           # An nguon sang
        "strokes": False,          # An net ve Paint Effects
        "textures": False,         # Tat hien thi texture
    }

    def __init__(self):
        pass

    def get_active_model_panel(self):
        """Lay panel viewport dang kich hoat"""
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
        """Lam sach viewport de quay playblast dep mat"""
        if not panel:
            return {}
            
        original_states = {}
        for flag in self.FLAGS_TO_HIDE:
            try:
                original_states[flag] = cmds.modelEditor(panel, query=True, **{flag: True})
            except Exception:
                pass
                
        # An cac thanh phan phu tro
        for flag, val in self.FLAGS_TO_HIDE.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass
                
        # Luon bat hien thi Mesh (polymeshes)
        try:
            original_states["polymeshes"] = cmds.modelEditor(panel, query=True, polymeshes=True)
            cmds.modelEditor(panel, edit=True, polymeshes=True)
        except Exception:
            pass
            
        # Chuyen viewport sang che do Smooth Shaded
        try:
            cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded")
        except Exception:
            pass
            
        return original_states

    def restore_viewport(self, panel, original_states):
        """Khoi phuc trang thai viewport ban dau"""
        if not panel or not original_states:
            return
            
        for flag, val in original_states.items():
            try:
                cmds.modelEditor(panel, edit=True, **{flag: val})
            except Exception:
                pass

    def get_active_sound(self):
        """Tim tep am thanh dang kich hoat tren timeline"""
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
        """Tu dong xac dinh duong dan luu file playblast tuong doi theo file maya dang mo"""
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            return None, None
            
        dirname = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        filename_no_ext, _ = os.path.splitext(filename)
        
        # Tao thu muc mov cung cap hoac cau truc cha
        playblast_dir = os.path.join(dirname, "mov")
        if not os.path.exists(playblast_dir):
            try:
                os.makedirs(playblast_dir)
            except Exception:
                pass
                
        return playblast_dir, filename_no_ext

    def is_file_locked(self, filepath):
        """Kiem tra xem video dau ra co dang bi chiem quyen boi trinh phat video khong"""
        if not os.path.exists(filepath):
            return False
            
        try:
            f = open(filepath, "a")
            f.close()
            return False
        except IOError:
            return True

    def archive_old_playblast(self, filepath):
        """Sao luu tep cu vao thu muc Old truoc khi nuong tep moi"""
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

    def run_playblast(self, format_ext="qt", percent=100, width=1920, height=1080, camera=None, viewer=True, overwrite=False, custom_dir=None):
        """Thuc thi quay Playblast"""
        if custom_dir and os.path.isdir(custom_dir):
            playblast_dir = custom_dir
            current_filepath = cmds.file(q=True, sceneName=True)
            if current_filepath:
                filename = os.path.basename(current_filepath)
                base_name, _ = os.path.splitext(filename)
            else:
                base_name = "untitled_playblast"
        else:
            playblast_dir, base_name = self.get_playblast_path()
            if not playblast_dir:
                raise RuntimeError("Vui long luu file Maya hien tai hoac chon Thu muc luu tuy chinh truoc khi xuat Playblast!")
            
        available_formats = cmds.playblast(query=True, format=True)
        fmt = "qt"
        ext = ".mov"
        
        if format_ext == "avi":
            if "avi" in available_formats:
                fmt = "avi"
                ext = ".avi"
            else:
                cmds.warning("Dinh dang AVI khong kha dung, tu dong chuyen sang QuickTime.")
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
        
        # Sao luu neu khong cho phep ghi de truc tiep
        if not overwrite and os.path.exists(output_filepath):
            self.archive_old_playblast(output_filepath)
            
        # Kiem tra khoa file
        if self.is_file_locked(output_filepath):
            raise RuntimeError(
                "Khong the xuat video! Tep video dau ra dang duoc mo hoac khoa boi ung dung khac:\n%s\n\n"
                "Vui long dong trinh phat video (VLC, PotPlayer...) va thu lai." % output_filepath
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
                
        # Lay am thanh
        sound_node = self.get_active_sound()
        
        # Tinh toan khung hinh
        start_time = cmds.playbackOptions(query=True, minTime=True)
        end_time = cmds.playbackOptions(query=True, maxTime=True)
        
        # Lay danh sach compression kha dung cho format da chon tren he thong hien tai
        available_compressions = []
        try:
            available_compressions = cmds.playblast(query=True, compression=True) or []
        except Exception:
            pass
            
        compression = "none"
        if fmt == "qt":
            # Uu tien H.264, sau do den cac dinh dang nen pho bien, cuoi cung la none
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
        
        # Thu chay playblast voi offScreen=True truoc
        playblast_args["offScreen"] = True
        
        try:
            cmds.playblast(**playblast_args)
        except Exception as e1:
            print("[Playblast] offScreen=True that bai, dang thu lai voi offScreen=False...")
            playblast_args["offScreen"] = False
            try:
                cmds.playblast(**playblast_args)
            except Exception as e2:
                # Khoi phuc trang thai truoc khi nem loi
                self.restore_viewport(panel, original_states)
                if original_camera and panel:
                    try:
                        cmds.modelEditor(panel, edit=True, camera=original_camera)
                    except Exception:
                        pass
                raise e2
        finally:
            # Khoi phuc viewport va camera ban dau
            self.restore_viewport(panel, original_states)
            if original_camera and panel:
                try:
                    cmds.modelEditor(panel, edit=True, camera=original_camera)
                except Exception:
                    pass
                    
        return output_filepath
