from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import json
import os
import sys
from maya import mel

try:
    import builtins
    max = builtins.max
    min = builtins.min
except ImportError:
    pass

MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40
BAKE_KEYS_OPTION_VAR = "XformAlignUI_bakeKeys"


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


def is_bake_keys_enabled():
    if cmds.optionVar(exists=BAKE_KEYS_OPTION_VAR):
        return cmds.optionVar(q=BAKE_KEYS_OPTION_VAR) == 1
    return True


def get_xform_json_path():
    anim_tools_folder = os.path.join(os.path.expanduser("~"), "Documents", "animTools")
    return os.path.join(anim_tools_folder, "Xform_Animation_Data.json")


def selectBasedOnJson():
    sel = cmds.ls(sl=True)
    
    if sel == []:
        json_path = get_xform_json_path()
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                data = json.load(file)
            
            object_names = list(data.keys())
            existing_objects = [obj for obj in object_names if cmds.objExists(obj)]
        
            if existing_objects:
                cmds.select(existing_objects, replace=True)
            else:
                cmds.warning("No valid objects from the JSON exist in the scene.")
        else:
            cmds.warning("JSON file not found: {0}".format(json_path))


def get_scale(obj):
    return cmds.xform(obj, query=True, worldSpace=True, scale=True)


def restore_scale(obj, scale_values):
    cmds.xform(obj, worldSpace=True, scale=scale_values)


def apply_matrix_preserve_scale(obj, matrix):
    original_scale = get_scale(obj)
    cmds.xform(obj, worldSpace=True, matrix=matrix)
    restore_scale(obj, original_scale)


def get_object_keyframes(objects, start_frame, end_frame):
    keyframes = set()
    for obj in objects:
        keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
        if keys:
            keyframes.update([int(k) for k in keys])
    return sorted(keyframes)


def get_timeline_range():
    playback_slider = mel.eval('$tmp = $gPlayBackSlider')
    range_array = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(range_array[0])
    end = int(range_array[1]) - 1
    if end > start:
        return start, end
    return None


def paste_xform_range():
    selectBasedOnJson()
    
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.inViewMessage(
            amg='<span style="color:#f58b3a;">Please select objects to paste to</span>',
            pos='botCenter',
            fade=True
        )
        return
    
    json_path = get_xform_json_path()
    
    if not os.path.exists(json_path):
        cmds.inViewMessage(
            amg='<span style="color:#f58b3a;">No data found. Copy first.</span>',
            pos='botCenter',
            fade=True
        )
        return
    
    try:
        with open(json_path, 'r') as json_file:
            transform_data = json.load(json_file)
    except Exception as e:
        cmds.error("Failed to load JSON file: {0}".format(str(e)))
        return
    
    json_objects = list(transform_data.keys())
    
    if not selected_objects:
        target_objects = json_objects
    elif len(json_objects) == 1:
        target_objects = selected_objects
    else:
        target_objects = [obj for obj in selected_objects if obj in transform_data]
        if not target_objects:
            cmds.warning("None of the selected objects are found in the animation data.")
            return
    
    timeline_range = get_timeline_range()
    
    if timeline_range:
        start_frame = timeline_range[0]
        end_frame = timeline_range[1]
    else:
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
    
    bake_keys_mode = is_bake_keys_enabled()
    
    if bake_keys_mode:
        object_keyframes = get_object_keyframes(selected_objects, start_frame, end_frame)
        
        stored_keyframes = set()
        for obj in json_objects:
            if isinstance(transform_data[obj], dict):
                if "keyframes" in transform_data[obj]:
                    for k in transform_data[obj]["keyframes"]:
                        if start_frame <= k <= end_frame:
                            stored_keyframes.add(k)
        stored_keyframes = sorted(stored_keyframes)
        
        if object_keyframes and len(object_keyframes) >= len(stored_keyframes):
            frames_to_process = object_keyframes
        elif stored_keyframes:
            frames_to_process = stored_keyframes
        else:
            frames_to_process = list(range(start_frame, end_frame + 1))
    else:
        frames_to_process = list(range(start_frame, end_frame + 1))
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(frames_to_process[0], frames_to_process[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    current_time = cmds.currentTime(q=True)
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in frames_to_process:
            cmds.currentTime(frame)

            for obj in target_objects:
                if len(json_objects) == 1:
                    source_obj = json_objects[0]
                    frame_str = str(frame)
                    if frame_str in transform_data[source_obj]:
                        data = transform_data[source_obj][frame_str]
                    else:
                        available_frames = [k for k in transform_data[source_obj].keys() if k != "keyframes"]
                        if available_frames:
                            data = transform_data[source_obj][available_frames[0]]
                        else:
                            continue
                else:
                    if obj in transform_data:
                        frame_str = str(frame)
                        if frame_str in transform_data[obj]:
                            data = transform_data[obj][frame_str]
                        else:
                            available_frames = [k for k in transform_data[obj].keys() if k != "keyframes"]
                            if available_frames:
                                data = transform_data[obj][available_frames[0]]
                            else:
                                continue
                    else:
                        continue

                apply_matrix_preserve_scale(obj, data["matrix"])
                cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)
            
    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


paste_xform_range()
