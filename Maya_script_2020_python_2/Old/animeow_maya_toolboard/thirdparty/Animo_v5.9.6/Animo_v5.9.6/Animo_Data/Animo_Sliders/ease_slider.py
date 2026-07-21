## Created by Ehsan Bayat, 2025
## Ease Slider Module for Animo
## This module provides tween/ease functionality when Ctrl is held on the TW slider

import maya.cmds as cmds
from maya import mel
import maya.utils
import platform
import time

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass

IS_MACOS = platform.system() == "Darwin"

# Global state variables for tween operations
pushClick = False
openChunk = True
originalValues = {}
storedSelection = []
storedAnimCurves = []
storedKeysSel = []

# Blend to neighbors state
blendPushClick = False
blendOpenChunk = True
blendStoredKeyValues = {}
blendStoredKeyTimes = {}
blendStoredIndexes = {}
blendStoredAnimCurves = []
blendStoredKeysSel = []
blendLastValue = 0
blendScaleValue = 1

# Throttle tracking
last_update_time = 0
update_throttle_ms = 1


def safe_undo_chunk_close():
    """Safely close an undo chunk with Mac compatibility"""
    try:
        if IS_MACOS:
            cmds.refresh()
            maya.utils.processIdleEvents()
        cmds.undoInfo(closeChunk=True)
    except:
        pass


def safe_undo_chunk_open(chunk_name="Ease Operation"):
    """Safely open an undo chunk with Mac compatibility"""
    try:
        cmds.undoInfo(openChunk=True, chunkName=chunk_name)
        if IS_MACOS:
            maya.utils.processIdleEvents()
    except:
        pass


def get_anim_curves():
    """Get animation curves from graph editor or timeline selection"""
    anim_curves = cmds.keyframe(query=True, name=True, selected=True)
    get_from = "graphEditor"
    
    if not anim_curves:
        get_from = "timeline"
        play_back_slider = mel.eval('$temp=$gPlayBackSlider')
        anim_curves = cmds.timeControl(play_back_slider, query=True, animCurveNames=True)
    
    return [anim_curves, get_from]


def get_timeline_range():
    """Get the current timeline range selection"""
    play_back_slider = mel.eval('$temp_playBackSlider=$gPlayBackSlider')
    time_range = cmds.timeControl(play_back_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return [start_range, end_range]


def get_keys_sel(anim_curves, get_from):
    """Get selected keys for each animation curve"""
    if not anim_curves:
        return []
    
    keys_sel = []
    if get_from == "graphEditor":
        for node in anim_curves:
            keys = cmds.keyframe(node, selected=True, query=True, timeChange=True)
            keys_sel.append(keys if keys else [])
    else:
        range_val = get_timeline_range()
        for node in anim_curves:
            if not cmds.objExists(node):
                keys_sel.append([])
                continue
                
            all_keys = cmds.keyframe(node, query=True, timeChange=True)
            if all_keys:
                range_keys = [k for k in all_keys if range_val[0] <= k < range_val[1]]
                keys_sel.append(range_keys)
            else:
                keys_sel.append([])
    return keys_sel


def get_key_indexes(curve, key_times):
    """Get key indexes for given key times on a curve"""
    if not cmds.objExists(curve) or not key_times:
        return []
    
    all_key_times = cmds.keyframe(curve, query=True, timeChange=True)
    if not all_key_times:
        return []
    
    indexes = []
    for key_time in key_times:
        for i, curve_time in enumerate(all_key_times):
            if abs(key_time - curve_time) < 0.001:  # Float comparison tolerance
                indexes.append(i)
                break
    return indexes


def set_key_tangents_smart(curves_and_times):
    """Set key tangents intelligently based on neighboring keys"""
    if not curves_and_times:
        return
    
    step_count = 0
    checked_count = 0
    max_check_threshold = 30
    
    for curve, key_times in curves_and_times.items():
        if checked_count >= max_check_threshold:
            break
            
        try:
            all_keys = cmds.keyframe(curve, query=True, timeChange=True)
            if not all_keys or len(all_keys) < 2:
                continue
            
            for key_time in key_times:
                current_key_index = None
                for i, kt in enumerate(all_keys):
                    if abs(kt - key_time) < 0.001:
                        current_key_index = i
                        break
                
                if current_key_index is None:
                    continue
                
                checked_count += 1
                
                if current_key_index > 0:
                    prev_out_tangent = cmds.keyTangent(curve, index=(current_key_index-1,), 
                                                     query=True, outTangentType=True)
                    if prev_out_tangent and prev_out_tangent[0] == 'step':
                        step_count += 1
                
                if current_key_index < len(all_keys) - 1:
                    next_in_tangent = cmds.keyTangent(curve, index=(current_key_index+1,), 
                                                    query=True, inTangentType=True)
                    if next_in_tangent and next_in_tangent[0] == 'step':
                        step_count += 1
                
                if checked_count >= max_check_threshold:
                    break
        except:
            continue
    
    if step_count >= max_check_threshold:
        for curve, key_times in curves_and_times.items():
            try:
                all_keys = cmds.keyframe(curve, query=True, timeChange=True)
                if not all_keys:
                    continue
                
                for key_time in key_times:
                    current_key_index = None
                    for i, kt in enumerate(all_keys):
                        if abs(kt - key_time) < 0.001:
                            current_key_index = i
                            break
                    
                    if current_key_index is not None:
                        cmds.keyTangent(curve, index=(current_key_index,), 
                                      outTangentType='step')
            except:
                continue
    else:
        for curve, key_times in curves_and_times.items():
            try:
                all_keys = cmds.keyframe(curve, query=True, timeChange=True)
                if not all_keys or len(all_keys) < 2:
                    continue
                
                for key_time in key_times:
                    current_key_index = None
                    for i, kt in enumerate(all_keys):
                        if abs(kt - key_time) < 0.001:
                            current_key_index = i
                            break
                    
                    if current_key_index is None:
                        continue
                        
                    prev_is_step = False
                    next_is_step = False
                    
                    if current_key_index > 0:
                        prev_out_tangent = cmds.keyTangent(curve, index=(current_key_index-1,), 
                                                         query=True, outTangentType=True)
                        if prev_out_tangent and prev_out_tangent[0] == 'step':
                            prev_is_step = True
                    
                    if current_key_index < len(all_keys) - 1:
                        next_in_tangent = cmds.keyTangent(curve, index=(current_key_index+1,), 
                                                        query=True, inTangentType=True)
                        if next_in_tangent and next_in_tangent[0] == 'step':
                            next_is_step = True
                    
                    if prev_is_step and next_is_step:
                        cmds.keyTangent(curve, index=(current_key_index,), 
                                      outTangentType='step')
                    elif prev_is_step:
                        pass
                    elif next_is_step:
                        cmds.keyTangent(curve, index=(current_key_index,), outTangentType='step')
            except:
                continue


def initialize_tween():
    """Initialize tween operation - open undo chunk and cache original values"""
    global originalValues, storedAnimCurves, storedKeysSel, openChunk
    
    safe_undo_chunk_open("Ease Tween")
    originalValues = {}
    
    getCurves = get_anim_curves()
    storedAnimCurves = getCurves[0]
    getFrom = getCurves[1]
    
    if not storedAnimCurves:
        openChunk = False
        return False
        
    storedKeysSel = get_keys_sel(storedAnimCurves, getFrom)
    
    hasSelectedKeys = any(keyList for keyList in storedKeysSel if keyList)
    
    if not hasSelectedKeys:
        current_time = cmds.currentTime(query=True)
        for curve in storedAnimCurves:
            if cmds.objExists(curve):
                existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                keyExists = existingKeys and current_time in existingKeys
                
                cmds.setKeyframe(curve, time=current_time, insert=True)
                
                if not keyExists:
                    prev_key = cmds.findKeyframe(curve, time=(current_time, current_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(current_time, current_time), which="next")
                    
                    in_tangent_type = "auto"
                    out_tangent_type = "auto"
                    
                    step_detected = False
                    
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key), 
                                                             query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                step_detected = True
                                in_tangent_type = "auto"
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    if not step_detected and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key), 
                                                             query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                step_detected = True
                                in_tangent_type = "auto"
                                out_tangent_type = "step"
                        except:
                            pass
                    
                    cmds.keyTangent(curve, time=(current_time, current_time),
                                  inTangentType=in_tangent_type, outTangentType=out_tangent_type)
        
        storedKeysSel = []
        for curve in storedAnimCurves:
            if cmds.objExists(curve):
                storedKeysSel.append([current_time])
            else:
                storedKeysSel.append([])
    
    for n, curve in enumerate(storedAnimCurves):
        if not cmds.objExists(curve) or not storedKeysSel[n]:
            continue
            
        originalValues[curve] = {}
        for key_time in storedKeysSel[n]:
            try:
                original_val = cmds.keyframe(curve, query=True, time=(key_time, key_time), 
                                           valueChange=True)[0]
                originalValues[curve][key_time] = original_val
            except:
                continue
    
    return True


def execute_tween(bias):
    """Execute the tween operation with given bias value (0.0 to 1.0)"""
    global originalValues, storedAnimCurves, storedKeysSel
    
    if not storedAnimCurves:
        return
    
    for n, curve in enumerate(storedAnimCurves):
        if not cmds.objExists(curve) or not storedKeysSel[n]:
            continue
        
        for key_time in storedKeysSel[n]:
            if curve not in originalValues or key_time not in originalValues[curve]:
                continue
                
            original_val = originalValues[curve][key_time]
            
            all_keys = cmds.keyframe(curve, query=True, timeChange=True)
            if not all_keys:
                continue
            
            all_keys = sorted(all_keys)
            
            prev_time = None
            next_time = None
            
            for k in all_keys:
                if k < key_time:
                    prev_time = k
                elif k > key_time:
                    next_time = k
                    break
            
            prev_value = None
            next_value = None
            
            if prev_time is not None:
                try:
                    prev_value = cmds.keyframe(curve, query=True, time=(prev_time,), valueChange=True)[0]
                except:
                    prev_value = None
            
            if next_time is not None:
                try:
                    next_value = cmds.keyframe(curve, query=True, time=(next_time,), valueChange=True)[0]
                except:
                    next_value = None
            
            tweened_value = original_val
            
            if prev_value is not None and next_value is not None:
                tweened_value = prev_value + (next_value - prev_value) * bias
                
            elif prev_value is not None:
                if bias < 0.5:
                    blend_factor = (0.5 - bias) * 2  # 0.5->0.0 becomes 0.0->1.0
                    tweened_value = original_val + (prev_value - original_val) * blend_factor
                    
            elif next_value is not None:
                if bias > 0.5:
                    blend_factor = (bias - 0.5) * 2  # 0.5->1.0 becomes 0.0->1.0
                    tweened_value = original_val + (next_value - original_val) * blend_factor
            
            try:
                cmds.keyframe(curve, edit=True, time=(key_time, key_time), valueChange=tweened_value)
            except:
                continue


def reset_tween():
    """Reset the tween state and close undo chunk"""
    global pushClick, openChunk, originalValues, storedSelection, storedAnimCurves, storedKeysSel
    
    if pushClick and openChunk:
        try:
            safe_undo_chunk_close()
        except:
            pass
        openChunk = False
    
    pushClick = False
    originalValues = {}
    storedSelection = []
    storedAnimCurves = []
    storedKeysSel = []


def setup_blend_key_transform_data():
    """Setup data structures for blend to neighbors operation"""
    global blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
    
    blendStoredKeyValues = {}
    blendStoredKeyTimes = {}
    blendStoredIndexes = {}
    
    for n, curve in enumerate(blendStoredAnimCurves):
        if not cmds.objExists(curve) or not blendStoredKeysSel[n]:
            continue
            
        keyValues = cmds.keyframe(curve, query=True, valueChange=True)
        keyTimes = cmds.keyframe(curve, query=True, timeChange=True)
        
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
                if abs(selTime - keyTime) < 0.001:  # Float comparison
                    if firstTime:
                        indexes.append([])
                        firstTime = False
                    indexes[-1].append(i)
                    keysSelTemp.pop(j)
                    break
            else:
                firstTime = True
        
        for i, segment in enumerate(indexes):
            indexes[i].insert(0, segment[0] - 1)  # Add head
            indexes[i].append(segment[-1] + 1)    # Add tail
        
        blendStoredIndexes[curve] = indexes


def execute_blend_key_transform(slider_val):
    """Execute blend to neighbors operation"""
    global blendLastValue, blendScaleValue
    
    if not blendStoredAnimCurves:
        return
    
    tValue = (slider_val + 100) / 100.0  # Convert to 0-2 range
    
    if tValue <= 1: 
        p = tValue
    else:          
        p = 2 - tValue
    
    if p == 0:
        p = 0.0000001  # Avoid division by zero
    
    if blendPushClick and blendLastValue != 0:
        blendScaleValue = (1.0 / blendLastValue) * p
    else:
        blendScaleValue = p
    
    for n, curve in enumerate(blendStoredAnimCurves):
        if curve not in blendStoredIndexes or not cmds.objExists(curve):
            continue
            
        keyValues = blendStoredKeyValues[curve]
        keyTimes = blendStoredKeyTimes[curve]
        segments = blendStoredIndexes[curve]
        
        for s, segment in enumerate(segments):
            fv = keyValues[segment[0]]   # First value (left neighbor)
            lv = keyValues[segment[-1]]  # Last value (right neighbor)
            
            has_real_left_neighbor = segment[0] > 1  # More than just head keys
            has_real_right_neighbor = segment[-1] < len(keyValues) - 2  # More than just tail keys
            
            if not has_real_left_neighbor and not has_real_right_neighbor:
                selected_keys_in_segment = segment[1:-1]  # Exclude head/tail
                if len(selected_keys_in_segment) >= 2:
                    fv = keyValues[selected_keys_in_segment[0]]   # First selected
                    lv = keyValues[selected_keys_in_segment[-1]]  # Last selected
            elif not has_real_left_neighbor and len(segment) > 3:  # No left, but has right
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    fv = keyValues[selected_keys_in_segment[0]]
            elif not has_real_right_neighbor and len(segment) > 3:  # No right, but has left  
                selected_keys_in_segment = segment[1:-1]
                if selected_keys_in_segment:
                    lv = keyValues[selected_keys_in_segment[-1]]
            
            if tValue <= 1:
                pivot = fv  # Blend toward left neighbor
            else:
                pivot = lv  # Blend toward right neighbor
            
            for i, keyIndex in enumerate(segment):
                if 1 <= i <= len(segment) - 2:  # Skip head and tail
                    realIndex = keyIndex - 2  # Adjust for head keys offset
                    
                    if 0 <= realIndex < len(cmds.keyframe(curve, query=True, timeChange=True) or []):
                        try:
                            cmds.scaleKey(curve, index=(realIndex, realIndex), 
                                        valuePivot=pivot, valueScale=blendScaleValue)
                        except:
                            try:
                                currentVal = cmds.keyframe(curve, index=(realIndex, realIndex), 
                                                         query=True, valueChange=True)[0]
                                newValue = pivot + (currentVal - pivot) * blendScaleValue
                                cmds.keyframe(curve, edit=True, index=(realIndex, realIndex), 
                                            valueChange=newValue)
                            except:
                                continue
    
    blendLastValue = p


def initialize_blend():
    """Initialize blend to neighbors operation"""
    global blendStoredAnimCurves, blendStoredKeysSel, blendOpenChunk
    
    safe_undo_chunk_open("Blend to Neighbors")
    
    getCurves = get_anim_curves()
    blendStoredAnimCurves = getCurves[0]
    getFrom = getCurves[1]
    
    if not blendStoredAnimCurves:
        blendOpenChunk = False
        return False
        
    blendStoredKeysSel = get_keys_sel(blendStoredAnimCurves, getFrom)
    
    hasSelectedKeys = any(keyList for keyList in blendStoredKeysSel if keyList)
    
    if not hasSelectedKeys:
        currentTime = cmds.currentTime(query=True)
        curves_with_new_keys = {}
        for curve in blendStoredAnimCurves:
            if cmds.objExists(curve):
                existingKeys = cmds.keyframe(curve, query=True, timeChange=True)
                keyExists = existingKeys and currentTime in existingKeys
                
                cmds.setKeyframe(curve, time=currentTime, insert=True)
                
                if not keyExists:
                    curves_with_new_keys[curve] = [currentTime]
        
        if curves_with_new_keys:
            for curve, times in curves_with_new_keys.items():
                for key_time in times:
                    cmds.keyTangent(curve, time=(key_time, key_time), 
                                   inTangentType='auto', outTangentType='auto')
        
        blendStoredKeysSel = []
        for curve in blendStoredAnimCurves:
            if cmds.objExists(curve):
                blendStoredKeysSel.append([currentTime])
            else:
                blendStoredKeysSel.append([])
    
    setup_blend_key_transform_data()
    return True


def reset_blend():
    """Reset blend state and close undo chunk"""
    global blendPushClick, blendOpenChunk, blendStoredKeyValues, blendStoredKeyTimes, blendStoredIndexes
    global blendStoredAnimCurves, blendStoredKeysSel, blendLastValue, blendScaleValue
    
    if blendPushClick and blendOpenChunk:
        try:
            safe_undo_chunk_close()
        except:
            pass
        blendOpenChunk = False
    
    blendPushClick = False
    blendStoredKeyValues = {}
    blendStoredKeyTimes = {}
    blendStoredIndexes = {}
    blendStoredAnimCurves = []
    blendStoredKeysSel = []
    blendLastValue = 0
    blendScaleValue = 1


# High-level API functions for Animo integration

class EaseSlider:
    """
    High-level ease slider controller for Animo integration.
    Usage:
        slider = EaseSlider()
        slider.start()           # Call when slider drag starts
        slider.update(value)     # Call during drag (-100 to 100)
        slider.finish()          # Call when slider drag ends
    """
    
    def __init__(self):
        self.is_active = False
        self.last_update_time = 0
        self.update_throttle_ms = 1
    
    def start(self):
        """Initialize the ease operation when slider drag starts"""
        global pushClick, openChunk
        
        if self.is_active:
            return
        
        self.is_active = True
        pushClick = True
        openChunk = True
        
        if IS_MACOS:
            # Slight delay for Mac compatibility
            import maya.utils
            maya.utils.executeDeferred(initialize_tween)
        else:
            initialize_tween()
    
    def update(self, value):
        """
        Update the ease operation with new slider value.
        
        Args:
            value: Slider value from -100 to 100
                   -100 = fully toward previous key
                   0 = original position
                   100 = fully toward next key
        """
        global pushClick, openChunk, last_update_time
        
        if not self.is_active:
            self.start()
        
        current_time = time.time() * 1000
        time_since_last = current_time - self.last_update_time
        
        if time_since_last < self.update_throttle_ms and pushClick:
            return
        
        self.last_update_time = current_time
        
        # Convert slider value (-100 to 100) to bias (0.0 to 1.0)
        bias = (value + 100) / 200.0
        execute_tween(bias)
    
    def finish(self):
        """Complete the ease operation when slider is released"""
        global pushClick, openChunk
        
        if not self.is_active:
            return
        
        self.is_active = False
        reset_tween()
    
    def cancel(self):
        """Cancel the ease operation (same as finish but can be extended)"""
        self.finish()


# Singleton instance for easy access
_ease_slider_instance = None

def get_ease_slider():
    """Get the singleton EaseSlider instance"""
    global _ease_slider_instance
    if _ease_slider_instance is None:
        _ease_slider_instance = EaseSlider()
    return _ease_slider_instance


# Convenience functions for direct use

def start_ease():
    """Start an ease operation"""
    get_ease_slider().start()


def update_ease(value):
    """Update ease with slider value (-100 to 100)"""
    get_ease_slider().update(value)


def finish_ease():
    """Finish the ease operation"""
    get_ease_slider().finish()


def ease_value(value):
    """
    One-shot ease operation - start, apply, and finish.
    Useful for button clicks with preset values.
    
    Args:
        value: -100 to 100
    """
    slider = get_ease_slider()
    slider.start()
    slider.update(value)
    slider.finish()
