# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import maya.cmds as cmds

def clean_virus():
    """Quét và tiêu diệt các node/script độc hại trong scene (vaccine, gene, fuckvirus...)"""
    virus_keywords = ["vaccine", "fuckvirus", "gene", "microvirus", "pyloads", "leukocyte", "antivirus"]
    cleaned_nodes = []
    
    # 1. Tìm và diệt các scriptNode chứa từ khóa độc hại
    all_scripts = cmds.ls(type="script") or []
    for script in all_scripts:
        script_lower = script.lower()
        # Kiểm tra xem tên script có chứa từ khóa virus không
        if any(keyword in script_lower for keyword in virus_keywords):
            try:
                # Trước khi xóa, tắt thuộc tính locked nếu có
                if cmds.objExists(script):
                    cmds.setAttr(script + ".locked", False)
                    cmds.delete(script)
                    cleaned_nodes.append(script)
            except Exception as e:
                print("[AntiVirus] Lỗi không thể xóa node %s: %s" % (script, str(e)))

    # 2. Quét và diệt các scriptJob độc hại đang chạy ẩn
    try:
        jobs = cmds.scriptJob(listJobs=True) or []
        for job in jobs:
            job_lower = job.lower()
            if any(keyword in job_lower for keyword in virus_keywords):
                try:
                    job_id = int(job.split(":")[0])
                    cmds.scriptJob(kill=job_id, force=True)
                    print("[AntiVirus] Đã diệt scriptJob độc hại ẩn ID: %d" % job_id)
                except Exception:
                    pass
    except Exception as e:
        print("[AntiVirus] Lỗi quét scriptJob: %s" % str(e))
        
    return cleaned_nodes
