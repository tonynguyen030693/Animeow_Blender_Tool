# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import re
import getpass
import time
import maya.cmds as cmds

# Regex chuẩn hoá để phân tích tên file dạng: Seq01_Shot010_Anim_v001.ma hoặc .mb
SCENE_NAME_PATTERN = re.compile(r"^(?P<prefix>.*)_v(?P<ver>\d+)(?P<ext>\.m[ab])$", re.IGNORECASE)

def parse_scene_name(filename):
    """
    Phân tích tên file để lấy prefix, chỉ số version (int) và extension.
    Trả về (prefix, version_int, ext) nếu khớp, ngược lại trả về None.
    """
    match = SCENE_NAME_PATTERN.match(filename)
    if match:
        prefix = match.group("prefix")
        ver_str = match.group("ver")
        ext = match.group("ext")
        return prefix, int(ver_str), len(ver_str), ext
    return None

def get_sequences(project_root):
    """Lấy danh sách các Sequence (phân đoạn) trong thư mục dự án"""
    if not project_root or not os.path.exists(project_root):
        return []
    shots_dir = os.path.join(project_root, "Shots")
    if not os.path.exists(shots_dir):
        return []
    
    sequences = []
    for item in os.listdir(shots_dir):
        item_path = os.path.join(shots_dir, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            sequences.append(item)
    return sorted(sequences)

def get_shots(project_root, sequence):
    """Lấy danh sách các Shot trong Sequence được chọn"""
    if not project_root or not sequence:
        return []
    seq_dir = os.path.join(project_root, "Shots", sequence)
    if not os.path.exists(seq_dir):
        return []
    
    shots = []
    for item in os.listdir(seq_dir):
        item_path = os.path.join(seq_dir, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            shots.append(item)
    return sorted(shots)

def get_work_dir(project_root, sequence, shot):
    """Lấy đường dẫn thư mục làm việc của Shot"""
    return os.path.join(project_root, "Shots", sequence, shot, "Anim", "Work")

def get_playblast_dir(project_root, sequence, shot):
    """Lấy đường dẫn thư mục chứa video playblast"""
    return os.path.join(project_root, "Shots", sequence, shot, "Anim", "Playblast")

def get_work_files(project_root, sequence, shot):
    """
    Quét thư mục Work và trả về danh sách các file làm việc (.ma, .mb) kèm thông tin chi tiết.
    """
    work_dir = get_work_dir(project_root, sequence, shot)
    if not os.path.exists(work_dir):
        return []
    
    files_info = []
    for filename in os.listdir(work_dir):
        if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
            continue
        
        filepath = os.path.join(work_dir, filename)
        if not os.path.isfile(filepath):
            continue
        
        # Lấy thông tin thời gian và dung lượng
        mtime = os.path.getmtime(filepath)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        size_mb = os.path.getsize(filepath) / (1024.0 * 1024.0)
        
        # Parse version để hiển thị và sắp xếp
        parsed = parse_scene_name(filename)
        ver_num = parsed[1] if parsed else 0
        
        files_info.append({
            "filename": filename,
            "filepath": filepath,
            "version": ver_num,
            "time": time_str,
            "mtime": mtime,
            "size": "{:.2f} MB".format(size_mb)
        })
        
    # Sắp xếp file theo phiên bản giảm dần (mới nhất lên đầu)
    return sorted(files_info, key=lambda x: x["version"], reverse=True)

def increment_save():
    """
    Lưu file hiện tại thành một phiên bản mới (+1 version).
    Trả về đường dẫn file mới hoặc None nếu thất bại.
    """
    # Lấy đường dẫn file hiện tại đang mở trong Maya
    current_filepath = cmds.file(q=True, sceneName=True)
    if not current_filepath:
        cmds.warning("File chưa được lưu lần nào! Hãy lưu file hoặc dùng chức năng Tạo Shot mới.")
        return None
        
    dirname = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    
    parsed = parse_scene_name(filename)
    if not parsed:
        cmds.warning("Tên file hiện tại không đúng quy chuẩn (ví dụ: ShotName_v001.ma). Không thể tự động tăng version.")
        return None
        
    prefix, ver_num, padding, ext = parsed
    new_ver_num = ver_num + 1
    
    # Định dạng lại tên file mới với padding tương ứng (mặc định 3 số)
    format_str = "%s_v%0" + str(padding) + "d%s"
    new_filename = format_str % (prefix, new_ver_num, ext)
    new_filepath = os.path.join(dirname, new_filename)
    
    # Tạo thư mục nếu chưa tồn tại (đề phòng)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
    # Đổi tên file trong Maya và lưu lại
    cmds.file(rename=new_filepath)
    
    file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
    cmds.file(save=True, type=file_type)
    
    print("Đã lưu phiên bản mới thành công: %s" % new_filepath)
    return new_filepath

def create_new_shot(project_root, sequence, shot):
    """
    Tạo mới một file shot diễn hoạt v001.ma và cấu trúc thư mục liên quan.
    """
    if not project_root or not sequence or not shot:
        cmds.warning("Vui lòng nhập đầy đủ thông tin Project, Sequence và Shot.")
        return None
        
    work_dir = get_work_dir(project_root, sequence, shot)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
        
    # Đặt tên file đầu tiên theo quy chuẩn: Seq_Shot_Anim_v001.ma
    filename = "%s_%s_Anim_v001.ma" % (sequence, shot)
    filepath = os.path.join(work_dir, filename)
    
    if os.path.exists(filepath):
        cmds.warning("File đã tồn tại: %s. Vui lòng mở file thay vì tạo mới." % filename)
        return filepath
        
    # Tạo mới scene trắng trong Maya và lưu lại
    cmds.file(new=True, force=True)
    cmds.file(rename=filepath)
    cmds.file(save=True, type="mayaAscii")
    
    # Thiết lập Project Directory của Maya về project_root
    cmds.workspace(project_root, openWorkspace=True)
    
    # Tạo sẵn các thư mục phụ trợ như Playblast
    playblast_dir = get_playblast_dir(project_root, sequence, shot)
    if not os.path.exists(playblast_dir):
        os.makedirs(playblast_dir)
        
    print("Khởi tạo Shot mới thành công: %s" % filepath)
    return filepath
