# -*- coding: utf-8 -*-
from __future__ import print_function, division

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
            return u"Loi ngoai le he thong"

class FileManager(object):
    """
    Class quan ly cac thao tac mo, luu file va quan ly cau truc du an.
    Ho tro cau truc phang: Project -> Episode (ten day du) -> WorkingFile -> Layout/Anim (chua truc tiep file .ma)
    """
    # Pattern phan tich file nhap: vi du KS_ESS_V2_Shot_01-30_Lay_v01.ma hoac KS_ESS_V2_Shot_01_Anim_v01.ma
    SCENE_NAME_PATTERN = re.compile(
        r"^(?P<prefix>.*?)_(?P<task>Lay|Anim)_v(?P<ver>\d+)(?:_\d+)?(?P<ext>\.m[ab])$", 
        re.IGNORECASE
    )

    def __init__(self, project_root="Z:\\Animeow_Production"):
        self.project_root = project_root

    def clean_shot_code(self, ep_abbrev, shot_input):
        """Lam sach shot input de tranh trung lap tien to va hau to task (vi du LL_BGOTL_V01_Shot_01_Anim -> 01 hoac 03-10)"""
        if not shot_input:
            return ""
        s = str(shot_input).strip()
        if ep_abbrev and s.lower().startswith(ep_abbrev.lower()):
            s = s[len(ep_abbrev):].lstrip("_")
        if "Shot_" in s:
            s = s.split("Shot_")[-1]
        elif "shot_" in s.lower():
            idx = s.lower().find("shot_")
            s = s[idx + 5:]
        s = re.sub(r'_(Anim|Lay|anim|lay).*$', '', s)
        
        # Chuan hoa dai shot neu nhap dang 3-10 hoac 03_10 -> 03-10
        range_match = re.match(r'^(\d+)\s*[\-\_]\s*(\d+)$', s)
        if range_match:
            s1 = int(range_match.group(1))
            s2 = int(range_match.group(2))
            return "%02d-%02d" % (s1, s2)
            
        # Chuan hoa so shot don neu nhap dang 3 -> 03
        if s.isdigit():
            return "%02d" % int(s)
            
        return s

    def parse_scene_name(self, filename):
        """Phan tich ten file lay prefix, task, version va extension"""
        match = self.SCENE_NAME_PATTERN.match(filename)
        if match:
            prefix = match.group("prefix")
            task = match.group("task")
            ver_str = match.group("ver")
            ext = match.group("ext")
            # Loai bo hau to task bi trung lap trong prefix neu co (vi du: LL_BGOTL_V01_Shot_01_Anim -> LL_BGOTL_V01_Shot_01)
            clean_prefix = re.sub(r'_(Lay|Anim)$', '', prefix, flags=re.IGNORECASE)
            return clean_prefix, task, int(ver_str), len(ver_str), ext

        # Fallback neu file bi dinh them ky tu o cuoi ten (vi du LL_BGOTL_V01_Shot_01_Anim_v01_1.ma)
        fallback_match = re.search(r"^(?P<prefix>.*?)_(?P<task>Lay|Anim)", filename, re.IGNORECASE)
        if fallback_match:
            prefix = fallback_match.group("prefix")
            task = fallback_match.group("task")
            clean_prefix = re.sub(r'_(Lay|Anim)$', '', prefix, flags=re.IGNORECASE)
            
            ver_match = re.search(r"[vV](?P<ver>\d+)", filename)
            ver_num = int(ver_match.group("ver")) if ver_match else 1
            ext = os.path.splitext(filename)[1]
            return clean_prefix, task, ver_num, 2, ext

        return None

    def get_project_prefix(self, project):
        """Lay tien to du an (KS, LL, EL, v.v.)"""
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
        Chuan hoa ten tap phim thanh dang PascalCase kem tien to du an,
        cach nhau bang dau gach duoi (vi du: KS_Elevator_Safety_Song_V02).
        """
        if not episode_name:
            return ""
            
        proj_prefix = self.get_project_prefix(project)
        words = re.split(r'[\s_\-]+', episode_name)
        
        # Bo qua tu dau tien neu trung voi tien to du an (tranh bi lap lai KS_KS_...)
        if words and words[0].upper() == proj_prefix.upper():
            words = words[1:]
            
        processed_words = []
        for word in words:
            if not word:
                continue
            # Chuan hoa version (vi du V2 -> V02)
            ver_match = re.match(r'^[vV](?P<num>\d+)$', word)
            if ver_match:
                processed_words.append("V%02d" % int(ver_match.group("num")))
                continue
            # Chuan hoa so tap (vi du 5 -> 05)
            num_match = re.match(r'^\d+$', word)
            if num_match:
                num_str = "%02d" % int(word) if len(word) == 1 else word
                processed_words.append(num_str)
                continue
            # Viet hoa chu cai dau, cac chu sau viet thuong (vi du: elevator -> Elevator)
            # Giu nguyen viet hoa neu tu ngan <= 3 ky tu (vi du AAA)
            if word.isupper() and len(word) <= 3:
                processed_words.append(word)
            else:
                processed_words.append(word.capitalize())
                
        folder_body = "_".join(processed_words)
        if proj_prefix:
            return "%s_%s" % (proj_prefix, folder_body)
        return folder_body

    def get_episode_abbreviation(self, project, episode_folder_name):
        """Tinh toan ma viet tat chu cai dau tu file metadata.json (neu co) hoac tu dong tinh tu ten thu muc"""
        if not project or not episode_folder_name:
            return ""
            
        # 1. Thu doc ma viet tat tu file metadata.json cua tap phim tren server
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
                
        # 2. Thuat toan tu dong du phong (Fallback) neu chua co metadata.json
        proj_prefix = self.get_project_prefix(project)
                
        # 2.2 Rut gon ten tap phim (ho tro ca dau gach duoi, gach ngang va khoang trang)
        words = re.split(r'[\s_\-]+', episode_folder_name)
        
        # Bo qua tu dau tien neu trung voi tien to du an (tranh bi lap lai trong ma viet tat, e.g. KS_KSAAA_25 -> KS_AAA_25)
        if words and words[0].upper() == proj_prefix.upper():
            words = words[1:]
            
        ep_parts = []
        version_part = ""
        
        for word in words:
            if not word:
                continue
            # Neu la ky hieu version (V02, V12, V01...)
            ver_match = re.match(r'^[vV](?P<num>\d+)$', word)
            if ver_match:
                version_part = "V%02d" % int(ver_match.group("num"))
            # Neu la so tap phim (25, 01...)
            elif re.match(r'^\d+$', word):
                version_part = "%02d" % int(word) if len(word) == 1 else word
            # Neu la tu viet hoa ngan (<= 3 ky tu) nhu AAA, EP, v.v.
            elif word.isupper() and len(word) <= 3:
                ep_parts.append(word)
            else:
                # Mac dinh lay chu cai dau
                ep_parts.append(word[0].upper())
                
        ep_code = "".join(ep_parts)
        if version_part:
            ep_code = "%s_%s" % (ep_code, version_part)
            
        return "%s_%s" % (proj_prefix, ep_code)

    def rename_episode_folder(self, project, old_ep_name, new_ep_name):
        """Doi ten thu muc tap phim tren Server"""
        if not self.project_root or not project or not old_ep_name or not new_ep_name:
            return False
            
        old_path = os.path.normpath(os.path.join(self.project_root, project, old_ep_name))
        new_path = os.path.normpath(os.path.join(self.project_root, project, new_ep_name))
        
        if not os.path.exists(old_path):
            cmds.warning(u"Thu muc nguon khong ton tai: %s" % old_path)
            return False
            
        if os.path.exists(new_path):
            cmds.warning(u"Thu muc dich da ton tai: %s" % new_path)
            return False
            
        try:
            # O Windows, neu co file dang mo/khoa, os.rename se bao loi PermissionError
            os.rename(old_path, new_path)
            print("Doi ten thu muc tap phim thanh cong tu %s thanh %s" % (old_ep_name, new_ep_name))
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            cmds.warning(u"Khong the doi ten thu muc tap phim: %s" % str(e))
            return False

    def get_projects(self):
        """Lay danh sach cac du an trong project_root"""
        if not self.project_root or not os.path.exists(self.project_root):
            return []
        projects = []
        for item in os.listdir(self.project_root):
            item_path = os.path.join(self.project_root, item)
            if os.path.isdir(item_path) and not item.startswith("."):
                projects.append(item)
        return sorted(projects)

    def get_episodes(self, project):
        """Lay danh sach cac tap phim trong du an"""
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
        """Quet thu muc WorkingFile/[Task] (va cac thu muc con doi voi Layout) va tra ve danh sach file nhap"""
        if not self.project_root or not project or not episode or not task:
            return []
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        if not os.path.exists(work_dir):
            return []
        
        files_to_scan = []
        
        # 1. Quet cac file nam truc tiep o thu muc cha (Layout va Anim)
        for filename in os.listdir(work_dir):
            filepath = os.path.join(work_dir, filename)
            if os.path.isfile(filepath):
                files_to_scan.append((filename, filepath))
                
        # 2. Quet them cac file nam trong cac thu muc con (dat theo ten shot)
        if task_dir_name in ["Layout", "Anim"]:
            for item in os.listdir(work_dir):
                shot_dir_path = os.path.join(work_dir, item)
                if os.path.isdir(shot_dir_path) and not item.startswith("."):
                    # Quet trong folder con "file"
                    file_dir_path = os.path.join(shot_dir_path, "file")
                    if os.path.exists(file_dir_path) and os.path.isdir(file_dir_path):
                        for filename in os.listdir(file_dir_path):
                            filepath = os.path.join(file_dir_path, filename)
                            if os.path.isfile(filepath):
                                files_to_scan.append((filename, filepath))
                                
                    # Quet du phong truc tiep trong thu muc shot de tuong thich nguoc
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
        """Tao cau truc thu muc chuan cho tap phim moi va ghi metadata.json neu co custom abbreviation"""
        if not self.project_root or not project or not episode_name:
            cmds.warning("Vui long dien day du thong tin Project va Ten tap phim.")
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
                print("Loi khi tao metadata.json: %s" % str(e))
                
        print("Da tao tap phim moi tai: %s" % ep_dir)
        return ep_dir

    def create_new_work_file(self, project, episode, task, shot_range_or_num):
        """Tao file nhap moi truc tiep trong thu muc WorkingFile/[Task]/"""
        if not self.project_root or not project or not episode or not task or not shot_range_or_num:
            cmds.warning("Vui long nhap day du thong tin.")
            return None
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        ep_abbrev = self.get_episode_abbreviation(project, episode)
        shot_code_str = self.clean_shot_code(ep_abbrev, shot_range_or_num)
        
        # Dam bao so shot le dang 2 chu so (doi voi Animation)
        if task_short == "Anim":
            try:
                shot_num_int = int(shot_code_str)
                shot_code_str = "%02d" % shot_num_int
            except ValueError:
                pass
            
        file_prefix = "%s_Shot_%s" % (ep_abbrev, shot_code_str)
        
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        # Luu tat ca file nhap (ca Layout va Anim) vao thu muc con dat ten theo shot -> thu muc 'file'
        work_dir = os.path.join(work_dir, file_prefix, "file")
            
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        filename = "%s_%s_v01.ma" % (file_prefix, task_short)
        filepath = os.path.normpath(os.path.join(work_dir, filename))
        
        if os.path.exists(filepath):
            cmds.warning("File da ton tai: %s" % filename)
            return filepath
            
        cmds.file(new=True, force=True)
        cmds.file(rename=to_sys_path(filepath))
        cmds.file(save=True, type="mayaAscii")
        
        cmds.workspace(to_sys_path(self.project_root), openWorkspace=True)
        print(u"Khoi tao file nhap moi thanh cong: %s" % filepath)
        return filepath

    def save_current_scene_to_pipeline(self, project, episode, task, shot_range_or_num):
        """Luu file Maya dang mo hien tai vao Pipeline theo khau va shot chi dinh"""
        if not self.project_root or not project or not episode or not task or not shot_range_or_num:
            cmds.warning("Vui long nhap day du thong tin (Project, Episode, Task, Shot).")
            return None
            
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        ep_abbrev = self.get_episode_abbreviation(project, episode)
        shot_code_str = self.clean_shot_code(ep_abbrev, shot_range_or_num)
        
        if task_short == "Anim":
            try:
                shot_num_int = int(shot_code_str)
                shot_code_str = "%02d" % shot_num_int
            except ValueError:
                pass
            
        file_prefix = "%s_Shot_%s" % (ep_abbrev, shot_code_str)
        
        work_dir = os.path.join(self.project_root, project, episode, "WorkingFile", task_dir_name)
        # Luu tat ca file nhap (ca Layout va Anim) vao thu muc con dat ten theo shot -> thu muc 'file'
        work_dir = os.path.join(work_dir, file_prefix, "file")
            
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        # Tim version lon nhat hien co trong thu muc dich de tu dong tang +1 (hoac bat dau v01)
        max_ver = 0
        if os.path.exists(work_dir):
            pattern = re.compile(r"^" + re.escape(file_prefix) + r"_" + re.escape(task_short) + r"_v(?P<ver>\d+)\.m[ab]$", re.IGNORECASE)
            for f in os.listdir(work_dir):
                m = pattern.match(f)
                if m:
                    v = int(m.group("ver"))
                    if v > max_ver:
                        max_ver = v
                        
        next_ver = max_ver + 1
        filename = "%s_%s_v%02d.ma" % (file_prefix, task_short, next_ver)
        filepath = os.path.normpath(os.path.join(work_dir, filename))
        
        cmds.file(rename=to_sys_path(filepath))
        cmds.file(save=True, type="mayaAscii")
        
        cmds.workspace(to_sys_path(self.project_root), openWorkspace=True)
        print(u"Da luu canh hien tai vao Pipeline thanh cong: %s" % filepath)
        return filepath

    def increment_save(self, task):
        """Luu file hien tai thanh mot phien ban nhap moi (+1)"""
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            cmds.warning("File chua duoc luu lan nao! Hay tao file nhap moi truoc.")
            return None
            
        dirname = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        
        parsed = self.parse_scene_name(filename)
        if not parsed:
            cmds.warning("Ten file hien tai khong dung quy chuan (vi du: KS_ESS_V2_Shot_01_Lay_v01.ma).")
            return None
            
        prefix, file_task, ver_num, padding, ext = parsed
        task_short = "Lay" if task.lower() in ["layout", "lay"] else "Anim"
        
        new_ver_num = ver_num + 1
        format_str = "%s_%s_v%0" + str(padding) + "d%s"
        new_filename = format_str % (prefix, task_short, new_ver_num, ext)
        
        # Luu tai cung thu muc chua file hien tai
        new_filepath = os.path.normpath(os.path.join(dirname, new_filename))
        
        cmds.file(rename=to_sys_path(new_filepath))
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
        cmds.file(save=True, type=file_type)
        
        print(u"Da luu phien ban nhap moi thanh cong: %s" % new_filepath)
        return new_filepath

    def publish_file(self, project, episode, task):
        """Luu file hien tai va publish file sach vao thu muc Published tuong ung"""
        if not self.project_root or not project or not episode or not task:
            cmds.warning("Vui long chon day du thong tin de Publish.")
            return None
            
        current_filepath = cmds.file(q=True, sceneName=True)
        if not current_filepath:
            cmds.warning("Hay luu file nhap cua ban truoc khi Publish.")
            return None
            
        cmds.file(save=True)
        
        filename = os.path.basename(current_filepath)
        parsed = self.parse_scene_name(filename)
        if not parsed:
            cmds.warning("Ten file hien tai khong dung quy chuan. Khong the Publish.")
            return None
            
        prefix, file_task, ver, padding, ext = parsed
        
        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        published_dir = os.path.join(self.project_root, project, episode, "Published", task_dir_name)
        # Publish vao thu muc con dat ten theo shot
        published_dir = os.path.join(published_dir, prefix)
            
        if not os.path.exists(published_dir):
            os.makedirs(published_dir)
            
        published_filename = "%s_%s_pub%s" % (prefix, task_short, ext)
        published_filepath = os.path.normpath(os.path.join(published_dir, published_filename))
        
        try:
            cmds.file(rename=to_sys_path(published_filepath))
            print(u"Dang don dep file cho Publish...")
            try:
                import maya.mel as mel
                mel.eval("MLdeleteUnused;")
            except Exception as e:
                print(u"Loi khi xoa unused nodes: %s" % exception_to_unicode(e))
                
            cmds.file(save=True, type="mayaAscii" if ext.lower() == ".ma" else "mayaBinary")
            print(u"Da luu file publish sach tai: %s" % published_filepath)
            
            return published_filepath
        except Exception as e:
            cmds.error(u"Loi trong qua trinh Publish file: %s" % exception_to_unicode(e))
            return None
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(to_sys_path(current_filepath), open=True, force=True)

    def check_episode_filenames_naming(self, project, episode):
        """Quet toan bo file trong WorkingFile\Layout va WorkingFile\Anim (bao gom thu muc con) de tim file sai quy chuan hoac sai thu muc"""
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
                
            # Regex kiem tra file dung quy chuan thuc te (ap dung cho ca Layout va Anim, ho tro dai shot 01-10)
            valid_pattern = re.compile(
                r"^" + re.escape(ep_abbrev) + r"_Shot_(?P<shot>\d+(-\d+)?)_" + re.escape(task_short) + r"_v(?P<ver>\d+)(?P<ext>\.m[ab])$", 
                re.IGNORECASE
            )
                
            # Thu thap cac file can kiem tra
            files_to_check = []
            seen_files = set()
            for filename in os.listdir(work_dir):
                filepath = os.path.join(work_dir, filename)
                if os.path.isfile(filepath):
                    files_to_check.append((filename, filepath, work_dir))
                    seen_files.add(os.path.normpath(filepath).lower())
                    
            if t_dir in ["Layout", "Anim"]:
                for item in os.listdir(work_dir):
                    shot_dir_path = os.path.join(work_dir, item)
                    if os.path.isdir(shot_dir_path) and not item.startswith("."):
                        file_dir_path = os.path.join(shot_dir_path, "file")
                        if os.path.exists(file_dir_path) and os.path.isdir(file_dir_path):
                            for filename in os.listdir(file_dir_path):
                                filepath = os.path.join(file_dir_path, filename)
                                if os.path.isfile(filepath) and os.path.normpath(filepath).lower() not in seen_files:
                                    files_to_check.append((filename, filepath, file_dir_path))
                                    seen_files.add(os.path.normpath(filepath).lower())
                                    
                        for filename in os.listdir(shot_dir_path):
                            filepath = os.path.join(shot_dir_path, filename)
                            if os.path.isfile(filepath) and os.path.normpath(filepath).lower() not in seen_files:
                                files_to_check.append((filename, filepath, shot_dir_path))
                                seen_files.add(os.path.normpath(filepath).lower())
                
            # Max version cho moi shot
            max_ver_by_shot = {}
            for filename, _, _ in files_to_check:
                m = valid_pattern.match(filename)
                if m:
                    shot_val = m.group("shot")
                    v = int(m.group("ver"))
                    if v > max_ver_by_shot.get(shot_val, 0):
                        max_ver_by_shot[shot_val] = v
                        
            for filename, filepath, current_dir in files_to_check:
                if not (filename.lower().endswith(".ma") or filename.lower().endswith(".mb")):
                    continue
                    
                match = valid_pattern.match(filename)
                is_correct_location = True
                
                if match:
                    shot_val = match.group("shot")
                    proposed_prefix = "%s_Shot_%s" % (ep_abbrev, shot_val)
                    expected_dir = os.path.normpath(os.path.join(work_dir, proposed_prefix, "file"))
                    if os.path.normpath(current_dir).lower() != expected_dir.lower():
                        is_correct_location = False
                        
                if not match or not is_correct_location:
                    ext = os.path.splitext(filename)[1].lower()
                    
                    shot_match = re.search(r"Shot_(?P<shot>\d+(-\d+)?)", filename, re.IGNORECASE)
                    if shot_match:
                        proposed_shot = shot_match.group("shot")
                    else:
                        proposed_shot = self.clean_shot_code(ep_abbrev, filename)
                        if not proposed_shot:
                            proposed_shot = "01"
                            
                    if not match:
                        current_max = max_ver_by_shot.get(proposed_shot, 0)
                        proposed_ver = current_max + 1
                        max_ver_by_shot[proposed_shot] = proposed_ver
                        
                        proposed_filename = "%s_Shot_%s_%s_v%02d%s" % (
                            ep_abbrev, proposed_shot, task_short, proposed_ver, ext
                        )
                    else:
                        proposed_filename = filename
                        shot_val = match.group("shot")
                        proposed_shot = shot_val
                    
                    proposed_prefix = "%s_Shot_%s" % (ep_abbrev, proposed_shot)
                    proposed_dir = os.path.join(work_dir, proposed_prefix, "file")
                    
                    incorrect_files.append({
                        "task_dir": t_dir,
                        "old_filename": filename,
                        "old_filepath": filepath,
                        "new_filename": proposed_filename,
                        "new_filepath": os.path.join(proposed_dir, proposed_filename)
                    })
        return incorrect_files

    def rename_work_files(self, incorrect_files):
        """Doi ten hang loat cac file lam viec sai quy chuan sau khi xac nhan"""
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
                
            if os.path.exists(new_path) and old_path.lower() != new_path.lower():
                ver_match = re.search(r"_v(?P<ver>\d+)\.m[ab]$", new_path, re.IGNORECASE)
                if ver_match:
                    v = int(ver_match.group("ver"))
                    ext = os.path.splitext(new_path)[1]
                    while os.path.exists(new_path) and old_path.lower() != new_path.lower():
                        v += 1
                        new_path = re.sub(r"_v\d+\.m[ab]$", "_v%02d%s" % (v, ext), new_path, flags=re.IGNORECASE)
                else:
                    base, ext = os.path.splitext(new_path)
                    v = 1
                    while os.path.exists("%s_v%02d%s" % (base, v, ext)) and old_path.lower() != new_path.lower():
                        v += 1
                    new_path = "%s_v%02d%s" % (base, v, ext)
                
            try:
                dest_dir = os.path.dirname(new_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                    
                is_current_open = (current_filepath and current_filepath == old_path)
                if is_current_open:
                    cmds.file(save=True)
                    cmds.file(rename=to_sys_path(new_path))
                    cmds.file(save=True, type="mayaAscii" if new_path.lower().endswith(".ma") else "mayaBinary")
                    if os.path.exists(old_path) and old_path.lower() != new_path.lower():
                        os.remove(old_path)
                    current_filepath = new_path
                else:
                    os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                cmds.warning(u"Loi khi doi ten file %s: %s" % (file_info["old_filename"], exception_to_unicode(e)))
                
        return success_count > 0

    def debug_open_file(self, filepath):
        """
        Mo file o che do debug:
        1. Do thoi gian nap file goc (khong load reference).
        2. Quet danh sach reference va nap tung file mot, do thoi gian nap cua moi reference.
        3. Quet danh sach script node trong scene.
        Tra ve dictionary bao cao chi tiet.
        """
        import time
        
        report = {
            "base_scene_time": 0.0,
            "references": [],
            "script_nodes": [],
            "total_time": 0.0
        }
        
        start_total = time.time()
        
        # Buoc 1: Mo file khong nap reference
        t0 = time.time()
        cmds.file(to_sys_path(filepath), open=True, force=True, loadReferenceDepth="none")
        report["base_scene_time"] = time.time() - t0
        
        # Buoc 2: Quet cac reference va nap tung cai mot
        ref_files = cmds.file(q=True, reference=True) or []
        
        for ref_file in ref_files:
            try:
                ref_node = cmds.referenceQuery(ref_file, referenceNode=True)
            except Exception:
                ref_node = None
                
            t_ref_start = time.time()
            try:
                # Nap reference
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
            
        # Buoc 3: Kiem tra cac Script Nodes trong scene
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
    # Ho tro quy trinh Tach / Gop Shot (Split & Combine)
    # ================================================================

    def get_combine_file_dir(self, project, episode):
        """Tra ve duong dan thu muc luu file gop canh tong: Published/Combine_File/"""
        if not self.project_root or not project or not episode:
            return None
        combine_dir = os.path.join(self.project_root, project, episode, "Published", "Combine_File")
        return os.path.normpath(combine_dir)

    def get_project_studiolibrary_dir(self, project=None):
        """Lay duong dan Thu vien Studio Library tong (Z:\\Animeow_Production\\Enjo_Library) dung chung cho tat ca du an"""
        library_root = os.path.join(os.path.dirname(self.project_root), "Enjo_Library")
        if not os.path.exists(library_root):
            library_root = os.path.join(self.project_root, "Enjo_Library")
            
        lib_dir = os.path.normpath(library_root)
        if not os.path.exists(lib_dir):
            try:
                os.makedirs(lib_dir)
            except Exception:
                pass
        return lib_dir

    def get_studiolibrary_dir(self, project, episode):
        """Tra ve duong dan thu muc Studio Library cua tap phim: Published/StudioLibrary/"""
        if not self.project_root or not project or not episode:
            return None
        sl_dir = os.path.join(self.project_root, project, episode, "Published", "StudioLibrary")
        return os.path.normpath(sl_dir)

    def build_studiolibrary_shot_dir(self, project, episode, shot_code_or_num):
        """
        Xay dung duong dan thu muc Studio Library cho mot Shot cu the.
        Vi du: shot_code_or_num = 5 hoac "05" -> .../Published/StudioLibrary/Shot_05/
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
        Tim file Animation le da publish cua mot shot cu the.
        Quet thu muc Published/Anim/ va tim file khop Shot_{num:02d}_Anim_pub.
        Tra ve duong dan file neu tim thay, None neu khong.
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
        Xay dung duong dan luu file shot le khi tach.
        Tra ve tuple (filepath, shot_dir) hoac (None, None).

        Vi du: bookmark_num = 5 -> file: KS_ELV02_Shot_05_Lay_v01.ma
               thu muc: WorkingFile/Layout/KS_ELV02_Shot_05/file/
        """
        if not self.project_root or not project or not episode:
            return None, None

        ep_abbrev = self.get_episode_abbreviation(project, episode)
        shot_code = "%02d" % int(bookmark_num)

        task_dir_name = "Layout" if task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"

        file_prefix = "%s_Shot_%s" % (ep_abbrev, shot_code)

        work_dir = os.path.join(
            self.project_root, project, episode,
            "WorkingFile", task_dir_name
        )
        shot_dir = os.path.join(work_dir, file_prefix, "file")

        filename = "%s_%s_v01.ma" % (file_prefix, task_short)
        filepath = os.path.normpath(os.path.join(shot_dir, filename))
        shot_dir = os.path.normpath(shot_dir)
        return filepath, shot_dir

    def build_combine_file_path(self, project, episode, start_shot, end_shot):
        """
        Xay dung duong dan file gop canh tong.
        Vi du: start_shot=1, end_shot=30 -> KS_ELV02_Shot_01-30.ma
               Luu tai Published/Combine_File/
        """
        if not self.project_root or not project or not episode:
            return None

        ep_abbrev = self.get_episode_abbreviation(project, episode)
        combine_dir = self.get_combine_file_dir(project, episode)
        if not combine_dir:
            return None

        filename = "%s_Shot_%02d-%02d.ma" % (ep_abbrev, int(start_shot), int(end_shot))
        return os.path.normpath(os.path.join(combine_dir, filename))

    def organize_studio_library(self, project=None):
        """Tu dong don dep, chuyen nhan vat chinh ve 01_Characters va danh so toan bo Studio Library"""
        lib_dir = self.get_project_studiolibrary_dir()
        if not lib_dir or not os.path.exists(lib_dir):
            return False, u"Thu muc Studio Library khong ton tai: %s" % lib_dir

        import shutil
        import re

        def safe_move(src, dst):
            if not os.path.exists(src):
                return False
            if os.path.normpath(src).lower() == os.path.normpath(dst).lower():
                if src != dst:
                    temp_path = src + "_tmp_rename"
                    os.rename(src, temp_path)
                    os.rename(temp_path, dst)
                    return True
                return True

            dst_dir = os.path.dirname(dst)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            if os.path.exists(dst):
                if os.path.isdir(src) and os.path.isdir(dst):
                    for item in os.listdir(src):
                        safe_move(os.path.join(src, item), os.path.join(dst, item))
                    try:
                        os.rmdir(src)
                    except Exception:
                        pass
                    return True
                return False

            try:
                shutil.move(src, dst)
                return True
            except Exception:
                return False

        def clean_name(name):
            cleaned = re.sub(r'^\d+[\._\-\s]*', '', name).strip()
            custom_fixes = {
                "conheo": "Con_Heo", "conbo": "Con_Bo", "conca": "Con_Ca",
                "conchim": "Con_Chim", "concoc": "Con_Coc", "concuu": "Con_Cuu",
                "conech": "Con_Ech", "conga": "Con_Ga", "conho": "Con_Ho",
                "conkien": "Con_Kien", "conmuoi": "Con_Muoi", "conngua": "Con_Ngua",
                "consau": "Con_Sau", "contho": "Con_Tho", "conchuot": "Con_Chuot",
                "conmeo": "Con_Meo", "convit": "Con_Vit", "canhcut": "Canh_Cut",
                "khunglong": "Khung_Long", "babyleo": "Baby_Leo", "lillybunny": "Lilly_Bunny",
                "sammybear": "Sammy_Bear", "tobymonkey": "Toby_Monkey", "woofinwolf": "Woofin_Wolf",
                "animalsother": "Animals_Other"
            }
            key = cleaned.lower().replace("_", "").replace(" ", "")
            if key in custom_fixes:
                return custom_fixes[key]

            s = re.sub(r'([a-z])([A-Z])', r'\1_\2', cleaned)
            words = [w.capitalize() for w in re.split(r'[\s_\-]+', s) if w]
            return "_".join(words)

        def number_subfolders(parent):
            if not os.path.exists(parent):
                return
            subdirs = [
                d for d in os.listdir(parent)
                if not d.startswith('.') and not d.startswith('_')
                and os.path.isdir(os.path.join(parent, d))
                and not d.endswith(('.anim', '.pose', '.mirror', '.selection'))
            ]
            subdirs.sort(key=lambda s: clean_name(s).lower())
            for idx, old_name in enumerate(subdirs, 1):
                c_name = clean_name(old_name)
                new_name = "%02d_%s" % (idx, c_name)
                safe_move(os.path.join(parent, old_name), os.path.join(parent, new_name))

        # Direct main characters from 02_Animals to 01_Characters
        main_char_targets = ["Sammy_Bear", "Toby_Monkey", "Woofin", "Woofin_Wolf", "Lilly_Bunny"]
        anim_dir = os.path.join(lib_dir, "02_Animals")
        char_dir = os.path.join(lib_dir, "01_Characters")

        if os.path.exists(anim_dir):
            for item in os.listdir(anim_dir):
                cn = clean_name(item)
                if cn in main_char_targets:
                    safe_move(os.path.join(anim_dir, item), os.path.join(char_dir, cn))

        for cat in ["01_Characters", "02_Animals", "03_Props_Vehicles", "04_Common_Library", "05_User_Scratch", "99_Archive_Trash"]:
            number_subfolders(os.path.join(lib_dir, cat))

        return True, u"Da tu dong chuyen cac Nhan vat chinh ve 01_Characters va danh so lai toan bo Studio Library!"

