# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import maya.cmds as cmds

def clean_virus():
    """Quet va tieu diet cac node/script doc hai trong scene (vaccine, gene, fuckvirus...)"""
    virus_keywords = ["vaccine", "fuckvirus", "gene", "microvirus", "pyloads", "leukocyte", "antivirus"]
    cleaned_nodes = []
    
    # 1. Tim va diet cac scriptNode chua tu khoa doc hai
    all_scripts = cmds.ls(type="script") or []
    for script in all_scripts:
        script_lower = script.lower()
        # Kiem tra xem ten script co chua tu khoa virus khong
        if any(keyword in script_lower for keyword in virus_keywords):
            try:
                # Truoc khi xoa, tat thuoc tinh locked neu co
                if cmds.objExists(script):
                    cmds.setAttr(script + ".locked", False)
                    cmds.delete(script)
                    cleaned_nodes.append(script)
            except Exception as e:
                print("[AntiVirus] Loi khong the xoa node %s: %s" % (script, str(e)))

    # 2. Quet va diet cac scriptJob doc hai dang chay an
    try:
        jobs = cmds.scriptJob(listJobs=True) or []
        for job in jobs:
            job_lower = job.lower()
            if any(keyword in job_lower for keyword in virus_keywords):
                try:
                    job_id = int(job.split(":")[0])
                    cmds.scriptJob(kill=job_id, force=True)
                    print("[AntiVirus] Da diet scriptJob doc hai an ID: %d" % job_id)
                except Exception:
                    pass
    except Exception as e:
        print("[AntiVirus] Loi quet scriptJob: %s" % str(e))
        
    return cleaned_nodes
