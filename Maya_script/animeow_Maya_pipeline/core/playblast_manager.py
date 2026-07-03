# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import maya.cmds as cmds
import maya.mel as mel

# Danh sách các thành phần Viewport cần ẩn khi làm sạch để Playblast
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
    "textures": False,         # Tắt texture hiển thị để nhẹ nếu cần (tùy chọn)
}

def get_active_model_panel():
    """Lấy tên panel Viewport đang hoạt động"""
    active_panel = cmds.playblast(query=True, activeEditor=True)
    if not active_panel:
        # Fallback lấy panel đang được focus
        focus_panel = cmds.getPanel(withFocus=True)
        if focus_panel and cmds.getPanel(typeOf=focus_panel) == "modelPanel":
            active_panel = focus_panel
        else:
            # Fallback lấy panel đầu tiên tìm thấy
            panels = cmds.getPanel(type="modelPanel")
            if panels:
                active_panel = panels[0]
    return active_panel

def setup_viewport(panel):
    """
    Làm sạch Viewport: Lưu lại trạng thái hiển thị cũ và ẩn các thành phần rig.
    """
    if not panel:
        return {}
        
    original_states = {}
    # Lấy và lưu trạng thái cũ
    for flag in FLAGS_TO_HIDE:
        try:
            original_states[flag] = cmds.modelEditor(panel, query=True, **{flag: True})
        except Exception:
            pass
            
    # Tắt hiển thị các thành phần không cần thiết
    for flag, val in FLAGS_TO_HIDE.items():
        try:
            cmds.modelEditor(panel, edit=True, **{flag: val})
        except Exception:
            pass
            
    # Đảm bảo hiển thị Poly Meshes
    try:
        original_states["polymeshes"] = cmds.modelEditor(panel, query=True, polymeshes=True)
        cmds.modelEditor(panel, edit=True, polymeshes=True)
    except Exception:
        pass
        
    # Thiết lập chế độ tô bóng mượt (Smooth Shaded + Hardware Texturing nếu cần)
    try:
        cmds.modelEditor(panel, edit=True, displayAppearance="smoothShaded")
    except Exception:
        pass
        
    return original_states

def restore_viewport(panel, original_states):
    """Khôi phục lại trạng thái hiển thị ban đầu của Viewport"""
    if not panel or not original_states:
        return
        
    for flag, val in original_states.items():
        try:
            cmds.modelEditor(panel, edit=True, **{flag: val})
        except Exception:
            pass

def get_active_sound():
    """Tìm âm thanh hoạt động trên Time Slider"""
    active_sound = None
    try:
        # Truy vấn thông qua biến toàn cục gPlayBackSlider của Maya
        g_slider = mel.eval("$tmpVar=$gPlayBackSlider")
        if cmds.timeControl(g_slider, exists=True):
            active_sound = cmds.timeControl(g_slider, query=True, sound=True)
    except Exception:
        # Fallback: Lấy âm thanh đầu tiên trong scene nếu có
        sounds = cmds.ls(type="audio")
        if sounds:
            active_sound = sounds[0]
    return active_sound

def get_playblast_path():
    """
    Tự động tính toán đường dẫn video playblast dựa trên file scene hiện tại.
    """
    current_filepath = cmds.file(q=True, sceneName=True)
    if not current_filepath:
        return None, None
        
    dirname = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    filename_no_ext, _ = os.path.splitext(filename)
    
    # Cấu trúc chuẩn: Shots/[Seq]/[Shot]/Anim/Work/File.ma -> Playblast trong Anim/Playblast
    # Ta đi lên 2 cấp thư mục nếu đang ở thư mục Work
    parent_dir = os.path.basename(dirname)
    grandparent_dir = os.path.basename(os.path.dirname(dirname))
    
    if parent_dir.lower() == "work" and grandparent_dir.lower() == "anim":
        playblast_dir = os.path.join(os.path.dirname(dirname), "Playblast")
    else:
        # Fallback: Tạo thư mục Playblast ngay bên cạnh file scene
        playblast_dir = os.path.join(dirname, "Playblast")
        
    if not os.path.exists(playblast_dir):
        os.makedirs(playblast_dir)
        
    return playblast_dir, filename_no_ext

def run_playblast(format_ext="qt", percent=100, width=1920, height=1080):
    """
    Chạy playblast tự động.
    - format_ext: "qt" (QuickTime) hoặc "avi"
    """
    playblast_dir, base_name = get_playblast_path()
    if not playblast_dir:
        cmds.warning("Hãy lưu file trước khi chạy Playblast để tự động xác định thư mục lưu video.")
        return None
        
    # Xác định các định dạng hợp lệ trên hệ thống
    available_formats = cmds.playblast(query=True, format=True)
    
    # Quyết định định dạng và phần mở rộng
    fmt = "qt"
    compression = "H.264"
    ext = ".mov"
    
    if format_ext == "avi":
        if "avi" in available_formats:
            fmt = "avi"
            compression = "none"
            ext = ".avi"
        else:
            cmds.warning("Định dạng AVI không khả dụng trên hệ thống này. Chuyển sang QuickTime.")
    else:
        if "qt" not in available_formats:
            # Fallback nếu không có QuickTime
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
    
    # 1. Chuẩn bị Viewport
    panel = get_active_model_panel()
    original_states = setup_viewport(panel)
    
    # Lấy thông số khung hình
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)
    active_sound = get_active_sound()
    
    # Tham số playblast
    playblast_args = {
        "filename": output_filepath,
        "format": fmt,
        "compression": compression,
        "sequenceTime": False,
        "clearCache": True,
        "viewer": True,             # Mở trình xem video sau khi xong
        "showOrnaments": True,       # Hiển thị HUDs (như thông số camera, frame rate)
        "percent": percent,
        "widthHeight": [width, height],
        "forceOverwrite": True,
        "startTime": start_frame,
        "endTime": end_frame
    }
    
    if active_sound:
        playblast_args["sound"] = active_sound
        
    # 2. Thực thi Playblast
    print("Bắt đầu chạy Playblast: %s" % output_filepath)
    try:
        cmds.playblast(**playblast_args)
    except Exception as e:
        cmds.error("Lỗi khi chạy Playblast: %s" % str(e))
    finally:
        # 3. Khôi phục Viewport
        restore_viewport(panel, original_states)
        
    print("Đã xuất Playblast thành công tại: %s" % output_filepath)
    return output_filepath
