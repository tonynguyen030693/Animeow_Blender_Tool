import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import time

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore

try:
    from . import slider_utils
except ImportError:
    import slider_utils

IS_MACOS = slider_utils.IS_MACOS

pushClick = False
originalValues = {}
storedAnimCurves = []
storedKeysSel = []
storedMfnCurves = {}
storedKeyIndexes = {}
storedBoundaryValues = {}  # Store left/right boundary values per curve
storedGetFrom = "graphEditor"


def initialize_tween_undo():
    global originalValues, storedAnimCurves, storedKeysSel, storedMfnCurves, storedKeyIndexes, storedBoundaryValues, storedGetFrom
    slider_utils.safe_undo_chunk_open("Tween")
    originalValues = {}
    storedMfnCurves = {}
    storedKeyIndexes = {}
    storedBoundaryValues = {}
    getCurves = slider_utils.get_anim_curves()
    storedAnimCurves = getCurves[0]
    storedGetFrom = getCurves[1]
    if not storedAnimCurves:
        return
    storedKeysSel = slider_utils.get_keys_sel(storedAnimCurves, storedGetFrom)
    hasSelectedKeys = any(keyList for keyList in storedKeysSel if keyList)
    if not hasSelectedKeys:
        current_time = cmds.currentTime(query=True)
        for curve in storedAnimCurves:
            if cmds.objExists(curve):
                existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                keyExists = existingKeys and current_time in existingKeys
                cmds.setKeyframe(curve, time=current_time, insert=True)
                if not keyExists:
                    prev_key = cmds.findKeyframe(curve, time=(current_time,current_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(current_time,current_time), which="next")
                    out_tangent_type = "auto"
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key,prev_key), query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                out_tangent_type = "step"
                        except:
                            pass
                    if out_tangent_type != "step" and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key,next_key), query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                out_tangent_type = "step"
                        except:
                            pass
                    cmds.keyTangent(curve, time=(current_time, current_time), inTangentType="auto", outTangentType=out_tangent_type)
        storedKeysSel = []
        for curve in storedAnimCurves:
            if cmds.objExists(curve):
                storedKeysSel.append([current_time])
            else:
                storedKeysSel.append([])
    
    for n, curve in enumerate(storedAnimCurves):
        if not storedKeysSel[n]:
            continue
        mfn = slider_utils.get_mfn_anim_curve(curve)
        if mfn is None:
            continue
        storedMfnCurves[curve] = mfn
        originalValues[curve] = {}
        storedKeyIndexes[curve] = {}
        
        num_keys = mfn.numKeys
        
        # Get all selected key indexes for this curve
        selected_indexes = []
        for key_time in storedKeysSel[n]:
            idx = slider_utils.get_key_index_at_time(mfn, key_time)
            if idx >= 0:
                val = cmds.keyframe(curve, index=(idx, idx), query=True, valueChange=True)
                originalValues[curve][key_time] = val[0] if val else 0.0
                storedKeyIndexes[curve][key_time] = idx
                selected_indexes.append(idx)
        
        if not selected_indexes:
            continue
        
        # Find boundary neighbors (unselected keys before first and after last selected)
        first_selected_idx = min(selected_indexes)
        last_selected_idx = max(selected_indexes)
        
        left_value = None
        right_value = None
        
        # Left boundary: key before the first selected key
        if first_selected_idx > 0:
            val = cmds.keyframe(curve, index=(first_selected_idx - 1, first_selected_idx - 1), query=True, valueChange=True)
            left_value = val[0] if val else None
        
        # Right boundary: key after the last selected key
        if last_selected_idx < num_keys - 1:
            val = cmds.keyframe(curve, index=(last_selected_idx + 1, last_selected_idx + 1), query=True, valueChange=True)
            right_value = val[0] if val else None
        
        storedBoundaryValues[curve] = (left_value, right_value)


def execute_tween_on_curves(bias):
    global originalValues, storedAnimCurves, storedKeysSel, storedMfnCurves, storedKeyIndexes, storedBoundaryValues
    if not storedAnimCurves:
        return
    for n, curve in enumerate(storedAnimCurves):
        if not storedKeysSel[n] or curve not in storedMfnCurves:
            continue
        if curve not in storedBoundaryValues:
            continue
        
        left_value, right_value = storedBoundaryValues[curve]
        
        for key_time in storedKeysSel[n]:
            if curve not in originalValues or key_time not in originalValues[curve]:
                continue
            original_val = originalValues[curve][key_time]
            key_idx = storedKeyIndexes[curve].get(key_time, -1)
            if key_idx < 0:
                continue
            
            tweened_value = original_val
            if left_value is not None and right_value is not None:
                tweened_value = left_value + (right_value - left_value) * bias
            elif left_value is not None:
                if bias < 0.5:
                    blend_factor = (0.5 - bias) * 2
                    tweened_value = original_val + (left_value - original_val) * blend_factor
            elif right_value is not None:
                if bias > 0.5:
                    blend_factor = (bias - 0.5) * 2
                    tweened_value = original_val + (right_value - original_val) * blend_factor
            cmds.keyframe(curve, index=(key_idx, key_idx), valueChange=tweened_value)


def slider_logic(value, mouse_pressed, last_update_time, update_throttle_ms):
    global pushClick
    status = "Tween: {0}".format(value)
    if not mouse_pressed:
        return last_update_time, status
    current_time = time.time() * 1000
    last_update_time = current_time
    selected = cmds.ls(selection=True)
    if selected:
        if not pushClick:
            pushClick = True
            if IS_MACOS:
                QtCore.QTimer.singleShot(20, initialize_tween_undo)
            else:
                initialize_tween_undo()
        bias = (value + 100) / 200.0
        execute_tween_on_curves(bias)
    return last_update_time, status


def reset_slider(slider_widget):
    global pushClick, originalValues, storedAnimCurves, storedKeysSel, storedMfnCurves, storedKeyIndexes, storedBoundaryValues
    final_value = slider_widget.value()
    if pushClick:
        bias = (final_value + 100) / 200.0
        execute_tween_on_curves(bias)
    slider_widget.blockSignals(True)
    slider_widget.setValue(0)
    slider_widget.blockSignals(False)
    if pushClick:
        slider_utils.safe_undo_chunk_close()
    pushClick = False
    originalValues = {}
    storedAnimCurves = []
    storedKeysSel = []
    storedMfnCurves = {}
    storedKeyIndexes = {}
    storedBoundaryValues = {}