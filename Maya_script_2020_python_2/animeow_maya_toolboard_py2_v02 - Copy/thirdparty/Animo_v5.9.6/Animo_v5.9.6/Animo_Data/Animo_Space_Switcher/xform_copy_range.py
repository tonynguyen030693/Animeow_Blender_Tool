from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import json
import os
import sys
from maya import mel

MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40


def load_mark_frame():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Space_Switcher")
    
    if folder not in sys.path:
        sys.path.insert(0, folder)
    
    try:
        import mark_frame
        return mark_frame
    except ImportError:
        return None


def get_xform_json_path():
    anim_tools_folder = os.path.join(os.path.expanduser("~"), "Documents", "animTools")
    
    if not os.path.exists(anim_tools_folder):
        os.makedirs(anim_tools_folder)
    
    return os.path.join(anim_tools_folder, "Xform_Animation_Data.json")


def get_object_keyframes(obj, start_frame, end_frame):
    keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
    if keys:
        return sorted(set([int(k) for k in keys]))
    return []


def copy_xform_range():
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        cmds.inViewMessage(
            amg='<span style="color:#f58b3a;">Please select objects to copy</span>',
            pos='botCenter',
            fade=True
        )
        return
    
    start_frame = int(cmds.playbackOptions(query=True, minTime=True))
    end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    animation_data = {}
    current_time = cmds.currentTime(q=True)

    cmds.undoInfo(openChunk=True, chunkName="Copy Xform Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)

    try:
        for obj in selection:
            animation_data[obj] = {
                "keyframes": get_object_keyframes(obj, start_frame, end_frame)
            }
        
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame)

            for obj in selection:
                matrix = cmds.xform(obj, q=True, ws=True, m=True)

                animation_data[obj][str(frame)] = {
                    "matrix": [round(m, 6) for m in matrix]
                }

        json_path = get_xform_json_path()
        
        with open(json_path, 'w') as outfile:
            json.dump(animation_data, outfile, indent=4)
        
        cmds.inViewMessage(
            amg='<span style="color:#4ca6e6;">Xform Range Copied</span>',
            pos='botCenter',
            fade=True
        )

    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


copy_xform_range()
