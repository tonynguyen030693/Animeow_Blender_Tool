# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import os
import io
import maya.cmds as cmds

def clean_virus():
    """
    Quet va tieu diet cac node/script doc hai trong scene va trong thu muc Maya user scripts.
    Tuong thich voi Python 2.7 (Maya 2020) va Python 3 (Maya 2022+).
    """
    virus_keywords = [
        "vaccine", "fuckvirus", "gene", "microvirus", "pyloads",
        "leukocyte", "antivirus", "breed", "cortex", "mayascanner",
        "vrmf_control", "usersetup", "auto_save"
    ]
    cleaned_items = []

    # 1. Tim va diet cac scriptNode chua tu khoa doc hai hoac ma doc
    all_scripts = cmds.ls(type="script") or []
    for script in all_scripts:
        script_lower = script.lower()
        is_suspicious = False

        # Kiểm tra theo tên node
        if any(keyword in script_lower for keyword in virus_keywords):
            is_suspicious = True

        # Kiểm tra nội dung mã script bên trong node nếu chưa khớp tên
        if not is_suspicious:
            try:
                body = ""
                if cmds.attributeQuery("script", node=script, exists=True):
                    body += str(cmds.getAttr(script + ".script") or "")
                if cmds.attributeQuery("beforeScript", node=script, exists=True):
                    body += str(cmds.getAttr(script + ".beforeScript") or "")
                if cmds.attributeQuery("afterScript", node=script, exists=True):
                    body += str(cmds.getAttr(script + ".afterScript") or "")

                body_lower = body.lower()
                if any(keyword in body_lower for keyword in virus_keywords):
                    is_suspicious = True
            except Exception:
                pass

        if is_suspicious:
            try:
                if cmds.objExists(script):
                    # Tắt thuộc tính locked nếu node bị khóa
                    try:
                        cmds.setAttr(script + ".locked", False)
                    except Exception:
                        pass
                    cmds.delete(script)
                    cleaned_items.append("scriptNode: " + script)
                    print("[AntiVirus] Da xoa scriptNode doc hai: %s" % script)
            except Exception as e:
                print("[AntiVirus] Loi khong the xoa scriptNode %s: %s" % (script, str(e)))

    # 2. Quet va diet cac scriptJob doc hai dang chay an trong bo nho Maya
    try:
        jobs = cmds.scriptJob(listJobs=True) or []
        for job in jobs:
            job_lower = job.lower()
            if any(keyword in job_lower for keyword in virus_keywords):
                try:
                    job_id = int(job.split(":")[0])
                    cmds.scriptJob(kill=job_id, force=True)
                    cleaned_items.append("scriptJob ID: %d" % job_id)
                    print("[AntiVirus] Da diet scriptJob doc hai ID: %d" % job_id)
                except Exception:
                    pass
    except Exception as e:
        print("[AntiVirus] Loi quet scriptJob: %s" % str(e))

    # 3. Quet va lam sach file userSetup.py / userSetup.mel trong thu muc scripts cua User
    try:
        user_script_dir = cmds.internalVar(userScriptDir=True)
        if user_script_dir and os.path.exists(user_script_dir):
            for setup_file in ["userSetup.py", "userSetup.mel"]:
                setup_path = os.path.join(user_script_dir, setup_file)
                if os.path.isfile(setup_path):
                    try:
                        with io.open(setup_path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                        
                        clean_lines = []
                        file_modified = False
                        for line in lines:
                            line_lower = line.lower()
                            if any(keyword in line_lower for keyword in virus_keywords):
                                file_modified = True
                            else:
                                clean_lines.append(line)
                        
                        if file_modified:
                            with io.open(setup_path, "w", encoding="utf-8") as f:
                                f.writelines(clean_lines)
                            cleaned_items.append("File system script: %s" % setup_file)
                            print("[AntiVirus] Da lam sach file doc hai: %s" % setup_path)
                    except Exception as fe:
                        print("[AntiVirus] Loi khi xu ly file %s: %s" % (setup_path, str(fe)))
    except Exception as e:
        print("[AntiVirus] Loi quet thu muc userScriptDir: %s" % str(e))

    return cleaned_items

