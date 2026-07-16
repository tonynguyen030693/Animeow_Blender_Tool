# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import tempfile
import shutil
import sys
import traceback
import maya.cmds as cmds


class AnimationCombiner(object):
    """
    Class xử lý ghép nối chuyển động từ nhiều file shot con vào một file master.
    """
    def __init__(self, shot_files, master_scene_path, output_path, time_mode="sequential", master_start_frame=1):
        self.shot_files = shot_files
        self.master_scene_path = master_scene_path
        self.output_path = output_path
        self.time_mode = time_mode
        self.master_start_frame = master_start_frame
        
        self.temp_dir = None
        self.shot_data_list = []

    def load_atom_plugin(self):
        """Đảm bảo plugin ATOM đã được nạp trong Maya"""
        if not cmds.pluginInfo("atomImportExport", query=True, loaded=True):
            try:
                cmds.loadPlugin("atomImportExport")
                print("STATUS_MSG: Đã nạp plugin atomImportExport.")
            except Exception as e:
                print("STATUS_ERROR: Không thể nạp plugin atomImportExport: %s" % str(e), file=sys.stderr)
                raise e

    def get_animated_transforms(self):
        """Tìm tất cả các node transform có chứa keyframe animation trong scene hiện tại"""
        anim_curves = cmds.ls(type="animCurve")
        if not anim_curves:
            return []
        
        nodes = cmds.listConnections(anim_curves, source=False, destination=True)
        if not nodes:
            return []
            
        animated_transforms = cmds.ls(nodes, type="transform")
        return list(set(animated_transforms))

    def extract_animations(self):
        """Mở lần lượt các file con và xuất file ATOM tạm thời"""
        self.temp_dir = tempfile.mkdtemp(prefix="animeow_combiner_")
        self.shot_data_list = []
        total_shots = len(self.shot_files)
        
        for idx, shot_file in enumerate(self.shot_files):
            shot_basename = os.path.basename(shot_file)
            print("PROGRESS_UPDATE: %d/%d | Đang trích xuất: %s" % (idx + 1, total_shots * 2, shot_basename))
            
            if not os.path.exists(shot_file):
                print("STATUS_WARNING: File không tồn tại, bỏ qua: %s" % shot_file)
                continue
                
            # Mở file shot con
            cmds.file(shot_file, open=True, force=True)
            
            # Lấy thông số thời gian của shot
            start_frame = cmds.playbackOptions(query=True, minTime=True)
            end_frame = cmds.playbackOptions(query=True, maxTime=True)
            duration = end_frame - start_frame + 1
            
            # Tìm danh sách control có key
            animated_nodes = self.get_animated_transforms()
            if not animated_nodes:
                print("STATUS_WARNING: Không tìm thấy animation trong file: %s" % shot_basename)
                continue
                
            # Tên file atom tạm
            shot_name = os.path.splitext(shot_basename)[0]
            atom_filename = "shot_%03d_%s.atom" % (idx, shot_name)
            atom_path = os.path.join(self.temp_dir, atom_filename)
            
            # Bake Kết Quả Anim trước khi xuất (giúp giữ constraints, expressions...)
            # Vì file mở không lưu nên việc bake này cực kỳ an toàn
            print("STATUS_MSG: Đang Bake Results để bảo toàn chuyển động (Constraint/Expression)...")
            try:
                cmds.bakeResults(
                    animated_nodes,
                    time=(start_frame, end_frame),
                    simulation=True,
                    minimizeRotation=True,
                    disableImplicitControl=True
                )
            except Exception as bake_err:
                print("STATUS_WARNING: Không thể Bake Results (tiếp tục xuất thô): %s" % str(bake_err))
            
            # Chọn các node và xuất
            cmds.select(animated_nodes, replace=True)
            print("STATUS_MSG: Đang xuất file ATOM cho %d nodes (Frame %d -> %d)..." % (len(animated_nodes), start_frame, end_frame))
            
            cmds.atomExport(
                selected=True,
                file=atom_path,
                time=(start_frame, end_frame),
                hierarchy="none",
                controlPoints=True,
                shapes=True,
                attributes="",
                sdk=True,
                constraint=False,
                staticValues=False
            )
            
            self.shot_data_list.append({
                "shot_name": shot_name,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "duration": duration,
                "atom_path": atom_path,
                "nodes": animated_nodes
            })
            
        return len(self.shot_data_list) > 0

    def merge_animations(self):
        """Mở file master và dán tuần tự anim từ các file ATOM tạm vào"""
        if not self.shot_data_list:
            return False
            
        # Mở file Master mẫu
        print("STATUS_MSG: Đang mở file Master: %s" % os.path.basename(self.master_scene_path))
        cmds.file(self.master_scene_path, open=True, force=True)
        
        current_time_cursor = self.master_start_frame
        min_global_frame = None
        max_global_frame = None
        total_shots = len(self.shot_data_list)
        
        for idx, data in enumerate(self.shot_data_list):
            # Tính toán tiến trình từ 50% -> 100%
            progress_idx = len(self.shot_files) + idx + 1
            print("PROGRESS_UPDATE: %d/%d | Đang gộp chuyển động: %s" % (progress_idx, len(self.shot_files) * 2, data["shot_name"]))
            
            # Chọn các node tồn tại thực tế trên master
            existing_nodes = [node for node in data["nodes"] if cmds.objExists(node)]
            if not existing_nodes:
                print("STATUS_WARNING: Không tìm thấy đối tượng tương ứng nào trên Master cho shot %s." % data["shot_name"])
                continue
                
            cmds.select(existing_nodes, replace=True)
            
            # Tính toán offset
            if self.time_mode == "sequential":
                offset = current_time_cursor - data["start_frame"]
                shot_master_start = current_time_cursor
                shot_master_end = current_time_cursor + data["duration"] - 1
                current_time_cursor = shot_master_end + 1
            else:
                offset = 0
                shot_master_start = data["start_frame"]
                shot_master_end = data["end_frame"]
                
            if min_global_frame is None or shot_master_start < min_global_frame:
                min_global_frame = shot_master_start
            if max_global_frame is None or shot_master_end > max_global_frame:
                max_global_frame = shot_master_end
                
            # Import ATOM đè lên
            cmds.atomImport(
                file=data["atom_path"],
                type="anim",
                selected=True,
                search="*",
                replace="*",
                timeMap="none",
                timeMapStart=1,
                timeOffset=offset
            )
            print("STATUS_MSG: Đã dán anim cho %s tại [%d -> %d] (Offset: %d)" % 
                  (data["shot_name"], shot_master_start, shot_master_end, offset))
                  
        # Dọn dẹp animation curves mồ côi
        try:
            all_curves = cmds.ls(type="animCurve")
            unused_curves = [c for c in all_curves if not cmds.listConnections(c, source=False, destination=True)]
            if unused_curves:
                cmds.delete(unused_curves)
                print("STATUS_MSG: Đã dọn dẹp %d animation curves rác." % len(unused_curves))
        except Exception as clean_err:
            print("STATUS_WARNING: Lỗi dọn dẹp curves: %s" % str(clean_err))

        # Cấu hình Timeline
        if min_global_frame is not None and max_global_frame is not None:
            cmds.playbackOptions(edit=True, minTime=min_global_frame, maxTime=max_global_frame)
            cmds.playbackOptions(edit=True, animationStartTime=min_global_frame, animationEndTime=max_global_frame)
            cmds.currentTime(min_global_frame)
            
        # Lưu file mới
        cmds.file(rename=self.output_path)
        cmds.file(save=True, type="mayaAscii")
        print("STATUS_SUCCESS: Đã lưu file Master ghép nối thành công tại: %s" % self.output_path)
        return True

    def run(self):
        """Thực thi toàn bộ tiến trình ghép nối"""
        if not self.shot_files:
            print("STATUS_ERROR: Danh sách file shot lẻ trống.", file=sys.stderr)
            return False
            
        if not self.master_scene_path or not os.path.exists(self.master_scene_path):
            print("STATUS_ERROR: File Master không tồn tại: %s" % self.master_scene_path, file=sys.stderr)
            return False

        try:
            self.load_atom_plugin()
        except Exception:
            return False
        
        success = False
        try:
            # 1. Trích xuất
            if self.extract_animations():
                # 2. Ghép nối
                success = self.merge_animations()
        except Exception as e:
            traceback.print_exc()
            print("STATUS_ERROR: Lỗi khi ghép nối chuyển động: %s" % str(e), file=sys.stderr)
            success = False
        finally:
            # Dọn dẹp thư mục tạm
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("STATUS_MSG: Đã dọn dẹp thư mục tạm thời.")
                
        return success

