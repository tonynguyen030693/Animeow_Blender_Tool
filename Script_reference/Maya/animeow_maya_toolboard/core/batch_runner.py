# -*- coding: utf-8 -*-
"""
Script chạy ngầm trong mayapy standalone để ghép nối chuyển động.
"""
from __future__ import print_function, absolute_import, division

import os
import sys
import json

def run_batch():
    # 1. Kiểm tra tham số cấu hình
    if len(sys.argv) < 2:
        print("STANDALONE_ERROR: Thiếu đường dẫn file cấu hình JSON.")
        sys.exit(1)
        
    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print("STANDALONE_ERROR: File cấu hình không tồn tại: %s" % config_path)
        sys.exit(1)
        
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print("STANDALONE_ERROR: Lỗi đọc file JSON: %s" % str(e))
        sys.exit(1)
        
    # 2. Khởi tạo Maya Standalone
    print("STANDALONE_STATUS: Đang khởi tạo Maya Standalone (ẩn)...")
    try:
        import maya.standalone
        maya.standalone.initialize(name="python")
    except Exception as e:
        print("STANDALONE_ERROR: Không thể khởi tạo Maya Standalone: %s" % str(e))
        sys.exit(1)
        
    # 3. Import các thư viện Maya cần thiết
    import maya.cmds as cmds
    
    # 4. Đưa package vào sys.path để import đúng cách
    core_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(core_dir)
    package_parent = os.path.dirname(parent_dir) # Thư mục chứa animeow_maya_toolboard
    
    if package_parent not in sys.path:
        sys.path.insert(0, package_parent)
        
    from animeow_maya_toolboard.core.anim_combiner import AnimationCombiner
    
    # 5. Chạy trình gộp file
    print("STANDALONE_STATUS: Bắt đầu xử lý gộp Animation...")
    try:
        combiner = AnimationCombiner(
            shot_files=config["shot_files"],
            master_scene_path=config["master_scene_path"],
            output_path=config["output_path"],
            time_mode=config["time_mode"],
            master_start_frame=config["master_start_frame"]
        )
        
        success = combiner.run()
        
        if success:
            print("STANDALONE_SUCCESS: Ghép nối chuyển động hoàn thành thành công!")
            exit_code = 0
        else:
            print("STANDALONE_ERROR: Tiến trình AnimationCombiner báo thất bại.")
            exit_code = 1
            
    except Exception as e:
        print("STANDALONE_ERROR: Lỗi phát sinh trong tiến trình chạy combiner: %s" % str(e))
        exit_code = 1
    finally:
        # 6. Giải phóng Maya Standalone
        try:
            maya.standalone.uninitialize()
        except:
            pass
            
    sys.exit(exit_code)

if __name__ == "__main__":
    run_batch()
