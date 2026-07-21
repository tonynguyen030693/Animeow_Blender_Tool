import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import time

try:
    from . import slider_utils
except ImportError:
    import slider_utils

IS_MACOS = slider_utils.IS_MACOS

blendPushClick = False
blendStoredKeyValues = {}
blendStoredKeyTimes = {}
blendStoredIndexes = {}
blendStoredAnimCurves = []
blendStoredKeysSel = []
blendStoredMfnCurves = {}
blendLastValue = 0
blendScaleValue = 1
blendGetFrom = "graphEditor"


def setup_blend_key_transform_data():
    global blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes, blendStoredMfnCurves, blendGetFrom
    blendStoredKeyValues = {}
    blendStoredKeyTimes = {}
    blendStoredIndexes = {}
    blendStoredMfnCurves = {}
    for n, curve in enumerate(blendStoredAnimCurves):
        if not blendStoredKeysSel[n]:
            continue
        mfn = slider_utils.get_mfn_anim_curve(curve)
        if mfn is None:
            continue
        blendStoredMfnCurves[curve] = mfn
        # Always use cmds.keyframe for consistent UI units (works for both translate and rotate)
        keyValues = cmds.keyframe(curve, query=True, valueChange=True)
        if not keyValues:
            keyValues = []
        keyTimes = slider_utils.get_all_key_times(mfn)
        if not keyValues or not keyTimes:
            continue
        if len(keyTimes) == 1:
            inOffsetTime = 1
            inOffsetVal = 0
            outOffsetTime = 1
            outOffsetVal = 0
        else:
            inOffsetTime = keyTimes[1] - keyTimes[0]
            inOffsetVal = keyValues[1] - keyValues[0]
            outOffsetTime = keyTimes[-1] - keyTimes[-2]
            outOffsetVal = keyValues[-1] - keyValues[-2]
        keyValues.insert(0, keyValues[0] - inOffsetVal)
        keyTimes.insert(0, keyTimes[0] - inOffsetTime)
        keyValues.insert(0, keyValues[0] - inOffsetVal)
        keyTimes.insert(0, keyTimes[0] - inOffsetTime)
        keyValues.append(keyValues[-1] + outOffsetVal)
        keyTimes.append(keyTimes[-1] + outOffsetTime)
        keyValues.append(keyValues[-1] + outOffsetVal)
        keyTimes.append(keyTimes[-1] + outOffsetTime)
        blendStoredKeyValues[curve] = keyValues
        blendStoredKeyTimes[curve] = keyTimes
        indexes = []
        keysSelTemp = list(blendStoredKeysSel[n])
        firstTime = True
        for i, keyTime in enumerate(keyTimes):
            for j, selTime in enumerate(keysSelTemp):
                if abs(selTime - keyTime) < 0.001:
                    if firstTime:
                        indexes.append([])
                        firstTime = False
                    indexes[-1].append(i)
                    keysSelTemp.pop(j)
                    break
            else:
                firstTime = True
        for i, segment in enumerate(indexes):
            indexes[i].insert(0, segment[0] - 1)
            indexes[i].append(segment[-1] + 1)
        blendStoredIndexes[curve] = indexes


def execute_blend_key_transform(slider_val):
    global blendLastValue, blendScaleValue, blendStoredMfnCurves
    if not blendStoredAnimCurves:
        return
    tValue = (slider_val + 100) / 100.0
    if tValue <= 1:
        p = tValue
    else:
        p = 2 - tValue
    if p == 0:
        p = 0.0000001
    if blendPushClick and blendLastValue != 0:
        blendScaleValue = (1.0 / blendLastValue) * p
    else:
        blendScaleValue = p
    for n, curve in enumerate(blendStoredAnimCurves):
        if curve not in blendStoredIndexes or curve not in blendStoredMfnCurves:
            continue
        mfn = blendStoredMfnCurves[curve]
        try:
            num_keys = mfn.numKeys
        except:
            continue
        keyValues = blendStoredKeyValues[curve]
        segments = blendStoredIndexes[curve]
        for s, segment in enumerate(segments):
            fv = keyValues[segment[0]]
            lv = keyValues[segment[-1]]
            has_real_left_neighbor = segment[0] > 1
            has_real_right_neighbor = segment[-1] < len(keyValues) - 2
            if not has_real_left_neighbor and not has_real_right_neighbor:
                selected_keys_in_segment = segment[1:-1]
                if len(selected_keys_in_segment) >= 2:
                    fv = keyValues[selected_keys_in_segment[0]]
                    lv = keyValues[selected_keys_in_segment[-1]]
            elif not has_real_left_neighbor and len(segment) > 3:
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    fv = keyValues[selected_keys_in_segment[0]]
            elif not has_real_right_neighbor and len(segment) > 3:
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    lv = keyValues[selected_keys_in_segment[-1]]
            if tValue <= 1:
                pivot = fv
            else:
                pivot = lv
            for i, keyIndex in enumerate(segment):
                if 1 <= i <= len(segment) - 2:
                    realIndex = keyIndex - 2
                    if 0 <= realIndex < num_keys:
                        try:
                            cmds.scaleKey(curve, index=(realIndex, realIndex), 
                                         valuePivot=pivot, valueScale=blendScaleValue)
                        except:
                            continue
    blendLastValue = p


def slider_logic(value, mouse_pressed, last_update_time, update_throttle_ms):
    global blendPushClick, blendStoredAnimCurves, blendStoredKeysSel, blendGetFrom
    status = "Blend: {0}".format(value)
    if not mouse_pressed:
        return last_update_time, status
    current_time = time.time() * 1000
    time_since_last = current_time - last_update_time
    if time_since_last < update_throttle_ms and blendPushClick:
        return last_update_time, status
    last_update_time = current_time
    selected = cmds.ls(selection=True)
    if selected:
        if not blendPushClick:
            blendPushClick = True
            slider_utils.safe_undo_chunk_open("Blend to Neighbors")
            getCurves = slider_utils.get_anim_curves()
            blendStoredAnimCurves = getCurves[0]
            blendGetFrom = getCurves[1]
            if not blendStoredAnimCurves:
                return last_update_time, status
            blendStoredKeysSel = slider_utils.get_keys_sel(blendStoredAnimCurves, blendGetFrom)
            hasSelectedKeys = any(keyList for keyList in blendStoredKeysSel if keyList)
            if not hasSelectedKeys:
                currentTime = cmds.currentTime(query=True)
                for curve in blendStoredAnimCurves:
                    if cmds.objExists(curve):
                        existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                        keyExists = existingKeys and currentTime in existingKeys
                        cmds.setKeyframe(curve, time=currentTime, insert=True)
                        if not keyExists:
                            prev_key = cmds.findKeyframe(curve, time=(currentTime,currentTime), which="previous")
                            next_key = cmds.findKeyframe(curve, time=(currentTime,currentTime), which="next")
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
                            cmds.keyTangent(curve, time=(currentTime, currentTime), inTangentType="auto", outTangentType=out_tangent_type)
                blendStoredKeysSel = []
                for curve in blendStoredAnimCurves:
                    if cmds.objExists(curve):
                        blendStoredKeysSel.append([currentTime])
                    else:
                        blendStoredKeysSel.append([])
            setup_blend_key_transform_data()
        execute_blend_key_transform(value)
    return last_update_time, status


def reset_slider(slider_widget):
    global blendPushClick, blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
    global blendStoredAnimCurves, blendStoredKeysSel, blendLastValue, blendScaleValue, blendStoredMfnCurves
    slider_widget.blockSignals(True)
    slider_widget.setValue(0)
    slider_widget.blockSignals(False)
    if blendPushClick:
        slider_utils.safe_undo_chunk_close()
    blendPushClick = False
    blendStoredKeyValues = {}
    blendStoredKeyTimes = {}
    blendStoredIndexes = {}
    blendStoredAnimCurves = []
    blendStoredKeysSel = []
    blendStoredMfnCurves = {}
    blendLastValue = 0
    blendScaleValue = 1
