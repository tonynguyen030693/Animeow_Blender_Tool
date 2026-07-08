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


def get_object_keyframes(objects, start_frame, end_frame):
    keyframes = set()
    for obj in objects:
        keys = cmds.keyframe(obj, query=True, time=(start_frame, end_frame))
        if keys:
            keyframes.update([int(k) for k in keys])
    return sorted(keyframes)


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


def get_timeline_range():
    playBackSlider = mel.eval('$tmp=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    start = int(timeRange[0])
    end = int(timeRange[1]) - 1
    if end > start:
        return start, end
    return None


def paste_transforms():
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
    
    timeline_range = get_timeline_range()
    
    if timeline_range:
        start_frame = timeline_range[0]
        end_frame = timeline_range[1]
        
        bake_keys_mode = is_bake_keys_enabled()
        
        if bake_keys_mode:
            paste_at_keyframes(selected_objects, transform_data, start_frame, end_frame)
        else:
            paste_animation_range(selected_objects, transform_data, start_frame, end_frame)
    else:
        paste_single_frame_data(selected_objects, transform_data)


def paste_at_keyframes(selected_objects, transform_data, start_frame, end_frame):
    json_objects = list(transform_data.keys())
    
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
        keyframes = object_keyframes
    elif stored_keyframes:
        keyframes = stored_keyframes
    else:
        json_keyframes = set()
        for obj in json_objects:
            if isinstance(transform_data[obj], dict):
                for key in transform_data[obj].keys():
                    if key != "keyframes" and (key.isdigit() or (key.startswith('-') and key[1:].isdigit())):
                        k = int(key)
                        if start_frame <= k <= end_frame:
                            json_keyframes.add(k)
        keyframes = sorted(json_keyframes)
    
    if not keyframes:
        cmds.warning("No keyframes found.")
        return
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(keyframes[0], keyframes[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    current_time = cmds.currentTime(q=True)
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform At Keys")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in keyframes:
            cmds.currentTime(frame)
            
            if len(json_objects) == 1:
                source_obj = json_objects[0]
                frame_str = str(frame)
                if frame_str in transform_data[source_obj]:
                    data = transform_data[source_obj][frame_str]
                else:
                    available_frames = [k for k in transform_data[source_obj].keys() if k != "keyframes"]
                    if available_frames:
                        first_frame = available_frames[0]
                        data = transform_data[source_obj][first_frame]
                    else:
                        continue
                
                for obj in selected_objects:
                    apply_matrix_preserve_scale(obj, data["matrix"])
                    cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)
            else:
                for obj in selected_objects:
                    if obj in transform_data:
                        frame_str = str(frame)
                        if frame_str in transform_data[obj]:
                            data = transform_data[obj][frame_str]
                        else:
                            available_frames = [k for k in transform_data[obj].keys() if k != "keyframes"]
                            if available_frames:
                                first_frame = available_frames[0]
                                data = transform_data[obj][first_frame]
                            else:
                                continue
                        
                        apply_matrix_preserve_scale(obj, data["matrix"])
                        cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)
    
    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


def paste_single_frame_data(selected_objects, transform_data):
    marker = load_mark_frame()
    if marker:
        marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    json_objects = list(transform_data.keys())
    json_object_count = len(json_objects)
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Single Frame")
    
    try:
        if json_object_count == 1:
            single_obj = json_objects[0]
            available_frames = [k for k in transform_data[single_obj].keys() if k != "keyframes"]
            if not available_frames:
                return
            frame_data = available_frames[0]
            matrix = transform_data[single_obj][frame_data]["matrix"]
            
            for obj in selected_objects:
                try:
                    apply_matrix_preserve_scale(obj, matrix)
                    cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"))
                except Exception as e:
                    cmds.warning("Failed to apply transforms to {0}: {1}".format(obj, str(e)))
        else:
            for obj in selected_objects:
                try:
                    if obj in transform_data:
                        available_frames = [k for k in transform_data[obj].keys() if k != "keyframes"]
                        if not available_frames:
                            continue
                        frame_data = available_frames[0]
                        matrix = transform_data[obj][frame_data]["matrix"]
                        apply_matrix_preserve_scale(obj, matrix)
                        cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"))
                except Exception as e:
                    cmds.warning("Failed to apply transforms to {0}: {1}".format(obj, str(e)))
                    
    finally:
        cmds.undoInfo(closeChunk=True)


def paste_single_frame_across_range(selected_objects, transform_data, start_frame, end_frame):
    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    json_objects = list(transform_data.keys())
    json_object_count = len(json_objects)
    
    current_time = cmds.currentTime(q=True)
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame)
            
            if json_object_count == 1:
                single_obj = json_objects[0]
                frame_data = list(transform_data[single_obj].keys())[0]
                matrix = transform_data[single_obj][frame_data]["matrix"]
                
                for obj in selected_objects:
                    try:
                        apply_matrix_preserve_scale(obj, matrix)
                        cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)
                    except Exception as e:
                        cmds.warning("Failed to apply transforms to {0}: {1}".format(obj, str(e)))
            else:
                for obj in selected_objects:
                    try:
                        if obj in transform_data:
                            frame_data = list(transform_data[obj].keys())[0]
                            matrix = transform_data[obj][frame_data]["matrix"]
                            apply_matrix_preserve_scale(obj, matrix)
                            cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)
                    except Exception as e:
                        cmds.warning("Failed to apply transforms to {0}: {1}".format(obj, str(e)))
                            
    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


def paste_animation_full_timeline(selected_objects, transform_data, available_frames):
    start_frame = int(cmds.playbackOptions(q=True, min=True))
    end_frame = int(cmds.playbackOptions(q=True, max=True))
    paste_animation_range(selected_objects, transform_data, start_frame, end_frame)


def paste_animation_range(selected_objects, transform_data, start_frame, end_frame):
    marker = load_mark_frame()
    if marker:
        marker.mark_range(start_frame, end_frame, auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
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
    
    current_time = cmds.currentTime(q=True)
    
    cmds.undoInfo(openChunk=True, chunkName="Paste Xform Animation Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in range(start_frame, end_frame + 1):
            cmds.currentTime(frame)

            for obj in target_objects:
                if len(json_objects) == 1:
                    source_obj = json_objects[0]
                    if str(frame) in transform_data[source_obj]:
                        data = transform_data[source_obj][str(frame)]
                    else:
                        continue
                else:
                    if obj in transform_data and str(frame) in transform_data[obj]:
                        data = transform_data[obj][str(frame)]
                    else:
                        continue

                apply_matrix_preserve_scale(obj, data["matrix"])
                cmds.setKeyframe(obj, attribute=("tx", "ty", "tz", "rx", "ry", "rz"), time=frame)

        if not selected_objects:
            cmds.select(target_objects, replace=True)
            
    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)


paste_transforms()
