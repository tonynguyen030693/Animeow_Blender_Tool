# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import re
import getpass
import time
import maya.cmds as cmds

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

    def get_episode_folder_name(self, episode_name):
        """Chuẩn hoá tên tập phim thành dạng PascalCase cách nhau bằng dấu gạch dưới (Elevator_Safety_Song_V02)"""
        if not episode_name:
            return ""
        words = re.split(r'[\s_\-]+', episode_name)
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
        return "_".join(processed_words)

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
        # 2.1 Tiền tố dự án
        proj_lower = project.lower()
        if "kidsong" in proj_lower:
            proj_prefix = "KS"
        elif "lolo" in proj_lower:
            proj_prefix = "LL"
        elif "elementies" in proj_lower:
            proj_prefix = "EL"
        else:
            proj_prefix = "".join([c for c in project if c.isupper()])
            if not proj_prefix:
                proj_prefix = project[:2].upper()
            else:
                proj_prefix = proj_prefix[:2]
                
        # 2.2 Rút gọn tên tập phim
        words = episode_folder_name.split("_")
        ep_parts = []
        version_part = ""
        
        for word in words:
            if not word:
                continue
            # Nếu là ký hiệu version (V02, V12, V01...)
            if re.match(r'^[vV]\d+$', word):
                version_part = word.upper()
            # Nếu là số tập phim (25, 01...)
            elif re.match(r'^\d+$', word):
                version_part = word
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
        """Quét trực tiếp thư mục WorkingFile/[Task] và trả về danh sách file nháp"""
        if not self.project_root or not project or not episode or not task:
            return []
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        if not os.path.exists(work_dir):
            return []
        
        files_info = []
        for filename in os.listdir(work_dir):
            if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                continue
            
            filepath = os.path.join(work_dir, filename)
            if not os.path.isfile(filepath):
                continue
            
            mtime = os.path.getmtime(filepath)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            size_mb = os.path.getsize(filepath) / (1024.0 * 1024.0)
            
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
            
        ep_dir_name = self.get_episode_folder_name(episode_name)
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
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        filename = "%s_%s_v01.ma" % (file_prefix, task_short)
        filepath = os.path.normpath(os.path.join(work_dir, filename))
        
        if os.path.exists(filepath):
            cmds.warning("File đã tồn tại: %s" % filename)
            return filepath
            
        cmds.file(new=True, force=True)
        cmds.file(rename=filepath)
        cmds.file(save=True, type="mayaAscii")
        
        cmds.workspace(self.project_root, openWorkspace=True)
        print("Khởi tạo file nháp mới thành công: %s" % filepath)
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
        
        cmds.file(rename=new_filepath)
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
        cmds.file(save=True, type=file_type)
        
        print("Đã lưu phiên bản nháp mới thành công: %s" % new_filepath)
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
        if not os.path.exists(published_dir):
            os.makedirs(published_dir)
            
        published_filename = "%s_%s_pub%s" % (prefix, task_short, ext)
        published_filepath = os.path.normpath(os.path.join(published_dir, published_filename))
        
        try:
            cmds.file(rename=published_filepath)
            print("Đang dọn dẹp file cho Publish...")
            try:
                import maya.mel as mel
                mel.eval("MLdeleteUnused;")
            except Exception as e:
                print("Lỗi khi xóa unused nodes: %s" % str(e))
                
            cmds.file(save=True, type="mayaAscii" if ext.lower() == ".ma" else "mayaBinary")
            print("Đã lưu file publish sạch tại: %s" % published_filepath)
            return published_filepath
        except Exception as e:
            cmds.error("Lỗi trong quá trình Publish file: %s" % str(e))
            return None
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(current_filepath, open=True, force=True)

    def check_episode_filenames_naming(self, project, episode):
        """Quét toàn bộ file trong WorkingFile\Layout và WorkingFile\Anim để tìm file sai quy chuẩn"""
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
                
            max_ver = 0
            for f in os.listdir(work_dir):
                m = valid_pattern.match(f)
                if m:
                    v = int(m.group("ver"))
                    if v > max_ver:
                        max_ver = v
                        
            for filename in os.listdir(work_dir):
                if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                    continue
                filepath = os.path.join(work_dir, filename)
                if not os.path.isfile(filepath):
                    continue
                    
                match = valid_pattern.match(filename)
                if not match:
                    # File sai quy chuẩn! Đề xuất tên chuẩn mới
                    ext = os.path.splitext(filename)[1].lower()
                    
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
                    
                    incorrect_files.append({
                        "task_dir": t_dir,
                        "old_filename": filename,
                        "old_filepath": filepath,
                        "new_filename": proposed_filename,
                        "new_filepath": os.path.join(work_dir, proposed_filename)
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
                is_current_open = (current_filepath and current_filepath == old_path)
                if is_current_open:
                    cmds.file(save=True)
                    cmds.file(rename=new_path)
                    cmds.file(save=True, type="mayaAscii" if new_path.lower().endswith(".ma") else "mayaBinary")
                    os.remove(old_path)
                    current_filepath = new_path
                else:
                    os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                cmds.warning("Loi khi doi ten file %s: %s" % (file_info["old_filename"], str(e)))
                
        return success_count > 0
