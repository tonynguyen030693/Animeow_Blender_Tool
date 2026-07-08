# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import re
import getpass
import time
import sys
import maya.cmds as cmds

def to_sys_path(path):
    if not path:
        return path
    if isinstance(path, unicode):
        try:
            return path.encode(sys.getfilesystemencoding())
        except Exception:
            return path.encode("utf-8")
    return path

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

class FileManager(object):
    """
    Class quản lý các thao tác mở, lưu file và quản lý cấu trúc dự án.
    Hỗ trợ cấu trúc phẳng: Project -> Episode (tên đầy đủ) -> WorkingFile -> Layout/Anim (chứa trực tiếp file .ma)
    """
    # Pattern phân tích file nháp: ví dụ KS_ESS_V2_Shot_01-30_Lay_v01.ma hoặc KS_ESS_V2_Shot_01_Anim_v01.ma
    SCENE_NAME_PATTERN = re.compile(
        r"^(?P<prefix>.*?)_(?P<task>Lay|Anim)_v(?P<ver>\d+)(?P<ext>\.m[ab])$", 
        re.IGNORECASE
    )

    def __init__(self, project_root="Z:\\Animeow_Production"):
        self.project_root = project_root

    def parse_scene_name(self, filename):
        """Phân tích tên file lấy prefix, task, version và extension"""
        match = self.SCENE_NAME_PATTERN.match(filename)
        if match:
            prefix = match.group("prefix")
            task = match.group("task")
            ver_str = match.group("ver")
            ext = match.group("ext")
            return prefix, task, int(ver_str), len(ver_str), ext
        return None

    def get_project_prefix(self, project):
        """Lấy tiền tố dự án (KS, LL, EL, v.v.)"""
        if not project:
            return ""
        proj_lower = project.lower()
        if "kidsong" in proj_lower:
            return "KS"
        elif "lolo" in proj_lower:
            return "LL"
        elif "elementies" in proj_lower:
            return "EL"
        else:
            proj_prefix = "".join([c for c in project if c.isupper()])
            if not proj_prefix:
                return project[:2].upper()
            else:
                return proj_prefix[:2]

    def get_episode_folder_name(self, project, episode_name):
        """
        Chuẩn hoá tên tập phim thành dạng PascalCase kèm tiền tố dự án,
        cách nhau bằng dấu gạch dưới (ví dụ: KS_Elevator_Safety_Song_V02).
        """
        if not episode_name:
            return ""
            
        proj_prefix = self.get_project_prefix(project)
        words = re.split(r'[\s_\-]+', episode_name)
        
        # Bỏ qua từ đầu tiên nếu trùng với tiền tố dự án (tránh bị lặp lại KS_KS_...)
        if words and words[0].upper() == proj_prefix.upper():
            words = words[1:]
            
        processed_words = []
        for word in words:
            if not word:
                continue
            # Chuẩn hoá version (ví dụ V2 -> V02)
            ver_match = re.match(r'^[vV](?P<num>\d+)$', word)
            if ver_match:
                processed_words.append("V%02d" % int(ver_match.group("num")))
                continue
            # Chuẩn hoá số tập (ví dụ 5 -> 05)
            num_match = re.match(r'^\d+$', word)
            if num_match:
                num_str = "%02d" % int(word) if len(word) == 1 else word
                processed_words.append(num_str)
                continue
            # Viết hoa chữ cái đầu, các chữ sau viết thường (ví dụ: elevator -> Elevator)
            # Giữ nguyên viết hoa nếu từ ngắn <= 3 ký tự (ví dụ AAA)
            if word.isupper() and len(word) <= 3:
                processed_words.append(word)
            else:
                processed_words.append(word.capitalize())
                
        folder_body = "_".join(processed_words)
        if proj_prefix:
            return "%s_%s" % (proj_prefix, folder_body)
        return folder_body

    def get_episode_abbreviation(self, project, episode_folder_name):
        """Tính toán mã viết tắt chữ cái đầu từ file metadata.json (nếu có) hoặc tự động tính từ tên thư mục"""
        if not project or not episode_folder_name:
            return ""
            
        # 1. Thử đọc mã viết tắt từ file metadata.json của tập phim trên server
        metadata_path = os.path.join(self.project_root, project, episode_folder_name, "metadata.json")
        if os.path.exists(metadata_path):
            import json
            try:
                with open(metadata_path, "r") as f:
                    data = json.load(f)
                    val = data.get("abbreviation")
                    if val:
                        return val
            except Exception:
                pass
                
        # 2. Thuật toán tự động dự phòng (Fallback) nếu chưa có metadata.json
        proj_prefix = self.get_project_prefix(project)
                
        # 2.2 Rút gọn tên tập phim (hỗ trợ cả dấu gạch dưới, gạch ngang và khoảng trắng)
        words = re.split(r'[\s_\-]+', episode_folder_name)
        
        # Bỏ qua từ đầu tiên nếu trùng với tiền tố dự án (tránh bị lặp lại trong mã viết tắt, e.g. KS_KSAAA_25 -> KS_AAA_25)
        if words and words[0].upper() == proj_prefix.upper():
            words = words[1:]
            
        ep_parts = []
        version_part = ""
        
        for word in words:
            if not word:
                continue
            # Nếu là ký hiệu version (V02, V12, V01...)
            ver_match = re.match(r'^[vV](?P<num>\d+)$', word)
            if ver_match:
                version_part = "V%02d" % int(ver_match.group("num"))
            # Nếu là số tập phim (25, 01...)
            elif re.match(r'^\d+$', word):
                version_part = "%02d" % int(word) if len(word) == 1 else word
            # Nếu là từ viết hoa ngắn (<= 3 ký tự) như AAA, EP, v.v.
            elif word.isupper() and len(word) <= 3:
                ep_parts.append(word)
            else:
                # Mặc định lấy chữ cái đầu
                ep_parts.append(word[0].upper())
                
        ep_code = "".join(ep_parts)
        if version_part:
            ep_code = "%s_%s" % (ep_code, version_part)
            
        return "%s_%s" % (proj_prefix, ep_code)

    def rename_episode_folder(self, project, old_ep_name, new_ep_name):
        """Đổi tên thư mục tập phim trên Server"""
        if not self.project_root or not project or not old_ep_name or not new_ep_name:
            return False
            
        old_path = os.path.normpath(os.path.join(self.project_root, project, old_ep_name))
        new_path = os.path.normpath(os.path.join(self.project_root, project, new_ep_name))
        
        if not os.path.exists(old_path):
            cmds.warning(u"Thư mục nguồn không tồn tại: %s" % old_path)
            return False
            
        if os.path.exists(new_path):
            cmds.warning(u"Thư mục đích đã tồn tại: %s" % new_path)
            return False
            
        try:
            # Ở Windows, nếu có file đang mở/khóa, os.rename sẽ báo lỗi PermissionError
            os.rename(old_path, new_path)
            print("Đổi tên thư mục tập phim thành công từ %s thành %s" % (old_ep_name, new_ep_name))
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            cmds.warning(u"Không thể đổi tên thư mục tập phim: %s" % str(e))
            return False

    def get_projects(self):
        """Lấy danh sách các dự án trong project_root"""
        if not self.project_root or not os.path.exists(self.project_root):
            return []
        projects = []
        for item in os.listdir(self.project_root):
            item_path = os.path.join(self.project_root, item)
            if os.path.isdir(item_path) and not item.startswith("."):
                projects.append(item)
        return sorted(projects)

    def get_episodes(self, project):
        """Lấy danh sách các tập phim trong dự án"""
        if not self.project_root or not project:
            return []
        proj_dir = os.path.join(self.project_root, project)
        if not os.path.exists(proj_dir):
            return []
        
        episodes = []
        for item in os.listdir(proj_dir):
            item_path = os.path.join(proj_dir, item)
            if os.path.isdir(item_path) and not item.startswith("."):
                episodes.append(item)
        return sorted(episodes)

    def get_work_files(self, project, episode, task):
        """Quét thư mục WorkingFile/[Task] (và các thư mục con đối với Layout) và trả về danh sách file nháp"""
        if not self.project_root or not project or not episode or not task:
            return []
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        if not os.path.exists(work_dir):
            return []
        
        files_to_scan = []
        
        # 1. Quét các file nằm trực tiếp ở thư mục cha (Layout và Anim)
        for filename in os.listdir(work_dir):
            filepath = os.path.join(work_dir, filename)
            if os.path.isfile(filepath):
                files_to_scan.append((filename, filepath))
                
        # 2. Quét thêm các file nằm trong các thư mục con (đặt theo tên shot)
        if task_dir_name in ["Layout", "Anim"]:
            for item in os.listdir(work_dir):
                shot_dir_path = os.path.join(work_dir, item)
                if os.path.isdir(shot_dir_path) and not item.startswith("."):
                    # Quét trong folder con "file"
                    file_dir_path = os.path.join(shot_dir_path, "file")
                    if os.path.exists(file_dir_path) and os.path.isdir(file_dir_path):
                        for filename in os.listdir(file_dir_path):
                            filepath = os.path.join(file_dir_path, filename)
                            if os.path.isfile(filepath):
                                files_to_scan.append((filename, filepath))
                                
                    # Quét dự phòng trực tiếp trong thư mục shot để tương thích ngược
                    for filename in os.listdir(shot_dir_path):
                        filepath = os.path.join(shot_dir_path, filename)
                        if os.path.isfile(filepath):
                            files_to_scan.append((filename, filepath))
        
        files_info = []
        seen_filepaths = set()
        
        for filename, filepath in files_to_scan:
            if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                continue
            
            filepath_norm = os.path.normpath(filepath).lower()
            if filepath_norm in seen_filepaths:
                continue
            seen_filepaths.add(filepath_norm)
            
            try:
                mtime = os.path.getmtime(filepath)
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                size_mb = os.path.getsize(filepath) / (1024.0 * 1024.0)
            except Exception:
                continue
            
            parsed = self.parse_scene_name(filename)
            ver_num = parsed[2] if parsed else 0
            
            files_info.append({
                "filename": filename,
                "filepath": filepath,
                "version": ver_num,
                "time": time_str,
                "mtime": mtime,
                "size": "{:.2f} MB".format(size_mb)
            })
            
        return sorted(files_info, key=lambda x: x["filename"])

    def create_new_episode(self, project, episode_name, custom_abbrev=None):
        """Tạo cấu trúc thư mục chuẩn cho tập phim mới và ghi metadata.json nếu có custom abbreviation"""
        if not self.project_root or not project or not episode_name:
            cmds.warning("Vui lòng điền đầy đủ thông tin Project và Tên tập phim.")
            return None
            
        ep_dir_name = self.get_episode_folder_name(project, episode_name)
        ep_dir = os.path.join(self.project_root, project, ep_dir_name)
        
        sub_dirs = [
            os.path.join(ep_dir, "Published", "Layout"),
            os.path.join(ep_dir, "Published", "Anim"),
            os.path.join(ep_dir, "Published", "Combine_File"),
            os.path.join(ep_dir, "WorkingFile", "Layout"),
            os.path.join(ep_dir, "WorkingFile", "Anim"),
            os.path.join(ep_dir, "mov", "Layout"),
            os.path.join(ep_dir, "mov", "Anim"),
        ]
        
        for d in sub_dirs:
            if not os.path.exists(d):
                os.makedirs(d)
                
        if custom_abbrev:
            import json
            metadata_path = os.path.normpath(os.path.join(ep_dir, "metadata.json"))
            try:
                with open(metadata_path, "w") as f:
                    json.dump({"abbreviation": custom_abbrev}, f)
            except Exception as e:
                print("Lỗi khi tạo metadata.json: %s" % str(e))
                
        print("Đã tạo tập phim mới tại: %s" % ep_dir)
        return ep_dir

    def create_new_work_file(self, project, episode, task, shot_range_or_num):
        """Tạo file nháp mới trực tiếp trong thư mục WorkingFile/[Task]/"""
        if not self.project_root or not project or not episode or not task or not shot_range_or_num:
            cmds.warning("Vui lòng nhập đầy đủ thông tin.")
            return None
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        # Đảm bảo số shot lẻ dạng 2 chữ số (đối với Animation)
        if task_short == "Anim":
            try:
                shot_num_int = int(shot_range_or_num)
                shot_code_str = "%02d" % shot_num_int
            except ValueError:
                shot_code_str = shot_range_or_num
        else:
            shot_code_str = shot_range_or_num
            
        ep_abbrev = self.get_episode_abbreviation(project, episode)
        file_prefix = "%s_Shot_%s" % (ep_abbrev, shot_code_str)
        
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        if task_short == "Lay":
            # Layout: lưu vào thư mục con đặt tên theo shot -> tiếp tục lưu vào folder 'file'
            work_dir = os.path.join(work_dir, file_prefix, "file")
            
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        filename = "%s_%s_v01.ma" % (file_prefix, task_short)
        filepath = os.path.normpath(os.path.join(work_dir, filename))
        
        if os.path.exists(filepath):
            cmds.warning("File đã tồn tại: %s" % filename)
            return filepath
            
        cmds.file(new=True, force=True)
        cmds.file(rename=to_sys_path(filepath))
        cmds.file(save=True, type="mayaAscii")
        
        cmds.workspace(to_sys_path(self.project_root), openWorkspace=True)
        print(u"Khởi tạo file nháp mới thành công: %s" % filepath)
        return filepath

    def increment_save(self, task):
        """Lưu file hiện tại thành một phiên bản nháp mới (+1)"""
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            cmds.warning("File chưa được lưu lần nào! Hãy tạo file nháp mới trước.")
            return None
            
        dirname = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        
        parsed = self.parse_scene_name(filename)
        if not parsed:
            cmds.warning("Tên file hiện tại không đúng quy chuẩn (ví dụ: KS_ESS_V2_Shot_01_Lay_v01.ma).")
            return None
            
        prefix, file_task, ver_num, padding, ext = parsed
        task_short = "Lay" if task.lower() in ["layout", "lay"] else "Anim"
        
        new_ver_num = ver_num + 1
        format_str = "%s_%s_v%0" + str(padding) + "d%s"
        new_filename = format_str % (prefix, task_short, new_ver_num, ext)
        
        # Lưu tại cùng thư mục chứa file hiện tại
        new_filepath = os.path.normpath(os.path.join(dirname, new_filename))
        
        cmds.file(rename=to_sys_path(new_filepath))
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
        cmds.file(save=True, type=file_type)
        
        print(u"Đã lưu phiên bản nháp mới thành công: %s" % new_filepath)
        return new_filepath

    def publish_file(self, project, episode, task):
        """Lưu file hiện tại và publish file sạch vào thư mục Published tương ứng"""
        if not self.project_root or not project or not episode or not task:
            cmds.warning("Vui lòng chọn đầy đủ thông tin để Publish.")
            return None
            
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            cmds.warning("Hãy lưu file nháp của bạn trước khi Publish.")
            return None
            
        cmds.file(save=True)
        
        filename = os.path.basename(current_filepath)
        parsed = self.parse_scene_name(filename)
        if not parsed:
            cmds.warning("Tên file hiện tại không đúng quy chuẩn. Không thể Publish.")
            return None
            
        prefix, file_task, ver, padding, ext = parsed
        
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        published_dir = os.path.join(self.project_root, project, episode, "Published", task_dir_name)
        if task_short == "Lay":
            # Layout: publish vào thư mục con đặt tên theo shot
            published_dir = os.path.join(published_dir, prefix)
            
        if not os.path.exists(published_dir):
            os.makedirs(published_dir)
            
        published_filename = "%s_%s_pub%s" % (prefix, task_short, ext)
        published_filepath = os.path.normpath(os.path.join(published_dir, published_filename))
        
        try:
            cmds.file(rename=to_sys_path(published_filepath))
            print(u"Đang dọn dẹp file cho Publish...")
            try:
                import maya.mel as mel
                mel.eval("MLdeleteUnused;")
            except Exception as e:
                print(u"Lỗi khi xóa unused nodes: %s" % exception_to_unicode(e))
                
            cmds.file(save=True, type="mayaAscii" if ext.lower() == ".ma" else "mayaBinary")
            print(u"Đã lưu file publish sạch tại: %s" % published_filepath)
            
            return published_filepath
        except Exception as e:
            cmds.error(u"Lỗi trong quá trình Publish file: %s" % exception_to_unicode(e))
            return None
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(to_sys_path(current_filepath), open=True, force=True)

    def check_episode_filenames_naming(self, project, episode):
        """Quét toàn bộ file trong WorkingFile\Layout (kể cả thư mục con) và WorkingFile\Anim để tìm file sai quy chuẩn"""
        if not self.project_root or not project or not episode:
            return []
            
        ep_abbrev = self.get_episode_abbreviation(project, episode)
        task_dirs = ["Layout", "Anim"]
        incorrect_files = []
        
        for t_dir in task_dirs:
            task_short = "Lay" if t_dir == "Layout" else "Anim"
            work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", t_dir)
            if not os.path.exists(work_dir):
                continue
                
            # Regex kiểm tra file đúng quy chuẩn thực tế
            if t_dir == "Layout":
                # Layout hỗ trợ dải số (ví dụ 01-30) hoặc số đơn lẻ
                valid_pattern = re.compile(
                    r"^" + re.escape(ep_abbrev) + r"_Shot_(?P<shot>\d+(-\d+)?)_" + re.escape(task_short) + r"_v(?P<ver>\d+)(?P<ext>\.m[ab])$", 
                    re.IGNORECASE
                )
            else:
                # Anim chỉ hỗ trợ số đơn lẻ
                valid_pattern = re.compile(
                    r"^" + re.escape(ep_abbrev) + r"_Shot_(?P<shot>\d+)_" + re.escape(task_short) + r"_v(?P<ver>\d+)(?P<ext>\.m[ab])$", 
                    re.IGNORECASE
                )
                
            # Thu thập các file cần kiểm tra
            files_to_check = []
            for filename in os.listdir(work_dir):
                filepath = os.path.join(work_dir, filename)
                if os.path.isfile(filepath):
                    files_to_check.append((filename, filepath, work_dir))
                    
            if t_dir in ["Layout", "Anim"]:
                for item in os.listdir(work_dir):
                    shot_dir_path = os.path.join(work_dir, item)
                    if os.path.isdir(shot_dir_path) and not item.startswith("."):
                        # Quét trong shot_dir_path/file/
                        file_dir_path = os.path.join(shot_dir_path, "file")
                        if os.path.exists(file_dir_path) and os.path.isdir(file_dir_path):
                            for filename in os.listdir(file_dir_path):
                                filepath = os.path.join(file_dir_path, filename)
                                if os.path.isfile(filepath):
                                    files_to_check.append((filename, filepath, file_dir_path))
                                    
                        # Quét dự phòng trực tiếp trong shot_dir_path (cho các file cũ)
                        for filename in os.listdir(shot_dir_path):
                            filepath = os.path.join(shot_dir_path, filename)
                            if os.path.isfile(filepath):
                                files_to_check.append((filename, filepath, shot_dir_path))
                
            max_ver = 0
            for filename, _, _ in files_to_check:
                m = valid_pattern.match(filename)
                if m:
                    v = int(m.group("ver"))
                    if v > max_ver:
                        max_ver = v
                        
            for filename, filepath, current_dir in files_to_check:
                if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                    continue
                    
                match = valid_pattern.match(filename)
                is_correct_location = True
                
                # Nếu là Layout, kiểm tra xem nó có nằm đúng thư mục con theo shot hay không
                if match and t_dir == "Layout":
                    shot_val = match.group("shot")
                    proposed_prefix = "%s_Shot_%s" % (ep_abbrev, shot_val)
                    expected_dir = os.path.normpath(os.path.join(work_dir, proposed_prefix, "file"))
                    if os.path.normpath(current_dir).lower() != expected_dir.lower():
                        is_correct_location = False
                        
                if not match or not is_correct_location:
                    # File sai quy chuẩn tên hoặc sai vị trí lưu trữ!
                    ext = os.path.splitext(filename)[1].lower()
                    
                    if not match:
                        # Sai tên -> Đề xuất tên mới
                        shot_match = re.search(r"Shot_(?P<shot>\d+(-\d+)?)", filename, re.IGNORECASE)
                        if shot_match:
                            proposed_shot = shot_match.group("shot")
                        else:
                            proposed_shot = "01" if t_dir == "Anim" else "01-10"
                            
                        ver_match = re.search(r"[vV](?P<ver>\d+)", filename)
                        if not ver_match:
                            ver_match = re.search(r"(?P<ver>\d+)\.m[ab]$", filename, re.IGNORECASE)
                            
                        if ver_match:
                            proposed_ver = int(ver_match.group("ver"))
                        else:
                            proposed_ver = max_ver + 1
                            max_ver += 1
                            
                        proposed_filename = "%s_Shot_%s_%s_v%02d%s" % (
                            ep_abbrev, proposed_shot, task_short, proposed_ver, ext
                        )
                    else:
                        # Đúng tên nhưng sai vị trí -> giữ nguyên tên, đề xuất vị trí mới
                        proposed_filename = filename
                        shot_val = match.group("shot")
                        proposed_shot = shot_val
                    
                    # Xác định thư mục đích
                    if t_dir == "Layout":
                        proposed_prefix = "%s_Shot_%s" % (ep_abbrev, proposed_shot)
                        proposed_dir = os.path.join(work_dir, proposed_prefix, "file")
                    else:
                        proposed_dir = work_dir
                    
                    incorrect_files.append({
                        "task_dir": t_dir,
                        "old_filename": filename,
                        "old_filepath": filepath,
                        "new_filename": proposed_filename,
                        "new_filepath": os.path.normpath(os.path.join(proposed_dir, proposed_filename))
                    })
                    
        return incorrect_files

    def rename_work_files(self, incorrect_files):
        """Đổi tên hàng loạt các file làm việc sai quy chuẩn sau khi xác nhận"""
        if not incorrect_files:
            return False
            
        current_filepath = cmds.file(q=True, sceneName=True)
        if current_filepath:
            current_filepath = os.path.normpath(current_filepath)
            
        success_count = 0
        for file_info in incorrect_files:
            old_path = os.path.normpath(file_info["old_filepath"])
            new_path = os.path.normpath(file_info["new_filepath"])
            
            if not os.path.exists(old_path):
                continue
                
            if os.path.exists(new_path):
                base, ext = os.path.splitext(new_path)
                i = 1
                while os.path.exists("%s_%d%s" % (base, i, ext)):
                    i += 1
                new_path = "%s_%d%s" % (base, i, ext)
                
            try:
                # Tạo thư mục con đích nếu chưa tồn tại
                dest_dir = os.path.dirname(new_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                    
                is_current_open = (current_filepath and current_filepath == old_path)
                if is_current_open:
                    cmds.file(save=True)
                    cmds.file(rename=to_sys_path(new_path))
                    cmds.file(save=True, type="mayaAscii" if new_path.lower().endswith(".ma") else "mayaBinary")
                    os.remove(old_path)
                    current_filepath = new_path
                else:
                    os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                cmds.warning(u"Lỗi khi đổi tên file %s: %s" % (file_info["old_filename"], exception_to_unicode(e)))
                
        return success_count > 0

    def debug_open_file(self, filepath):
        """
        Mở file ở chế độ debug:
        1. Đo thời gian nạp file gốc (không load reference).
        2. Quét danh sách reference và nạp từng file một, đo thời gian nạp của mỗi reference.
        3. Quét danh sách script node trong scene.
        Trả về dictionary báo cáo chi tiết.
        """
        import time
        
        report = {
            "base_scene_time": 0.0,
            "references": [],
            "script_nodes": [],
            "total_time": 0.0
        }
        
        start_total = time.time()
        
        # Bước 1: Mở file không nạp reference
        t0 = time.time()
        cmds.file(to_sys_path(filepath), open=True, force=True, loadReferenceDepth="none")
        report["base_scene_time"] = time.time() - t0
        
        # Bước 2: Quét các reference và nạp từng cái một
        ref_files = cmds.file(q=True, reference=True) or []
        
        for ref_file in ref_files:
            try:
                ref_node = cmds.referenceQuery(ref_file, referenceNode=True)
            except Exception:
                ref_node = None
                
            t_ref_start = time.time()
            try:
                # Nạp reference
                cmds.file(ref_file, loadReference=True)
                ref_time = time.time() - t_ref_start
                status = "Success"
            except Exception as ref_err:
                ref_time = time.time() - t_ref_start
                status = "Failed: %s" % exception_to_unicode(ref_err)
                
            report["references"].append({
                "filepath": ref_file,
                "node": ref_node,
                "time": ref_time,
                "status": status
            })
            
        # Bước 3: Kiểm tra các Script Nodes trong scene
        script_nodes = cmds.ls(type="script") or []
        for node in script_nodes:
            try:
                script_type = cmds.getAttr(node + ".scriptType")
                script_val = cmds.getAttr(node + ".before") or ""
                if not script_val:
                    script_val = cmds.getAttr(node + ".after") or ""
                
                script_preview = script_val[:100] + "..." if len(script_val) > 100 else script_val
                
                report["script_nodes"].append({
                    "name": node,
                    "type": script_type,
                    "preview": script_preview.strip()
                })
            except Exception:
                pass
                
        report["total_time"] = time.time() - start_total
        return report

    # ================================================================
    # Hỗ trợ quy trình Tách / Gộp Shot (Split & Combine)
    # ================================================================

    def get_combine_file_dir(self, project, episode):
        """Trả về đường dẫn thư mục lưu file gộp cảnh tổng: Published/Combine_File/"""
        if not self.project_root or not project or not episode:
            return None
        combine_dir = os.path.join(self.project_root, project, episode, "Published", "Combine_File")
        return os.path.normpath(combine_dir)

    def get_studiolibrary_dir(self, project, episode):
        """Trả về đường dẫn thư mục Studio Library của tập phim: Published/StudioLibrary/"""
        if not self.project_root or not project or not episode:
            return None
        sl_dir = os.path.join(self.project_root, project, episode, "Published", "StudioLibrary")
        return os.path.normpath(sl_dir)

    def build_studiolibrary_shot_dir(self, project, episode, shot_code_or_num):
        """
        Xây dựng đường dẫn thư mục Studio Library cho một Shot cụ thể.
        Ví dụ: shot_code_or_num = 5 hoặc "05" -> .../Published/StudioLibrary/Shot_05/
        """
        st_dir = self.get_studiolibrary_dir(project, episode)
        if not st_dir:
            return None
            
        try:
            shot_num = int(shot_code_or_num)
            shot_folder = "Shot_%02d" % shot_num
        except ValueError:
            shot_folder = "Shot_%s" % shot_code_or_num
            
        return os.path.normpath(os.path.join(st_dir, shot_folder))

    def get_published_anim_file(self, project, episode, shot_num):
        """
        Tìm file Animation lẻ đã publish của một shot cụ thể.
        Quét thư mục Published/Anim/ và tìm file khớp Shot_{num:02d}_Anim_pub.
        Trả về đường dẫn file nếu tìm thấy, None nếu không.
        """
        if not self.project_root or not project or not episode:
            return None
        pub_anim_dir = os.path.join(self.project_root, project, episode, "Published", "Anim")
        if not os.path.exists(pub_anim_dir):
            return None

        shot_code = "Shot_%02d" % int(shot_num)
        for filename in os.listdir(pub_anim_dir):
            if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                continue
            if shot_code in filename and "_Anim" in filename:
                return os.path.normpath(os.path.join(pub_anim_dir, filename))
        return None

    def build_split_shot_path(self, project, episode, bookmark_num, task="Layout"):
        """
        Xây dựng đường dẫn lưu file shot lẻ khi tách.
        Trả về tuple (filepath, shot_dir) hoặc (None, None).

        Ví dụ: bookmark_num = 5 -> file: KS_ELV02_Shot_05_Lay_v01.ma
               thư mục: WorkingFile/Layout/KS_ELV02_Shot_05/file/
        """
        if not self.project_root or not project or not episode:
            return None, None

        ep_abbrev = self.get_episode_abbreviation(project, episode)
        shot_code = "%02d" % int(bookmark_num)

        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"

        file_prefix = "%s_Shot_%s" % (ep_abbrev, shot_code)

        shot_dir = os.path.join(
            self.project_root, project, episode,
            "WorkingFile", task_dir_name, file_prefix, "file"
        )

        filename = "%s_%s_v01.ma" % (file_prefix, task_short)
        filepath = os.path.normpath(os.path.join(shot_dir, filename))
        shot_dir = os.path.normpath(shot_dir)
        return filepath, shot_dir

    def build_combine_file_path(self, project, episode, start_shot, end_shot):
        """
        Xây dựng đường dẫn file gộp cảnh tổng.
        Ví dụ: start_shot=1, end_shot=30 -> KS_ELV02_Shot_01-30.ma
               Lưu tại Published/Combine_File/
        """
        if not self.project_root or not project or not episode:
            return None

        ep_abbrev = self.get_episode_abbreviation(project, episode)
        combine_dir = self.get_combine_file_dir(project, episode)
        if not combine_dir:
            return None

        filename = "%s_Shot_%02d-%02d.ma" % (ep_abbrev, int(start_shot), int(end_shot))
        return os.path.normpath(os.path.join(combine_dir, filename))
