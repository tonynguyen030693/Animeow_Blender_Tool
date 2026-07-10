import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import time

try:
    from . import slider_utils
except ImportError:
    import slider_utils

IS_MACOS = slider_utils.IS_MACOS

_dragging = False
_current_mode = None
_original_values = {}
_pivot_values = {}
_stored_keys_sel = []
_stored_anim_curves = []
_stored_key_indexes = {}
_mfn_curves = {}
_get_from = "graphEditor"


def cache_original_values(mode):
    global _original_values, _pivot_values, _stored_keys_sel, _stored_anim_curves
    global _stored_key_indexes, _mfn_curves, _current_mode, _get_from
    _original_values = {}
    _pivot_values = {}
    _stored_key_indexes = {}
    _mfn_curves = {}
    _current_mode = mode
    get_curves = slider_utils.get_anim_curves()
    _stored_anim_curves = get_curves[0]
    _get_from = get_curves[1]
    if not _stored_anim_curves:
        return
    _stored_keys_sel = slider_utils.get_keys_sel(_stored_anim_curves, _get_from)
    has_selected_keys = any(key_list for key_list in _stored_keys_sel if key_list)
    if not has_selected_keys:
        current_time = cmds.currentTime(query=True)
        for curve in _stored_anim_curves:
            if cmds.objExists(curve):
                existing_keys = cmds.keyframe(curve, query=True, timeChange=True)
                key_exists = existing_keys and current_time in existing_keys
                cmds.setKeyframe(curve, time=current_time, insert=True)
                if not key_exists:
                    prev_key = cmds.findKeyframe(curve, time=(current_time, current_time), which="previous")
                    next_key = cmds.findKeyframe(curve, time=(current_time, current_time), which="next")
                    out_tangent_type = "auto"
                    if prev_key is not None:
                        try:
                            prev_out_tangent = cmds.keyTangent(curve, time=(prev_key, prev_key), query=True, outTangentType=True)[0]
                            if prev_out_tangent == "step":
                                out_tangent_type = "step"
                        except:
                            pass
                    if out_tangent_type != "step" and next_key is not None:
                        try:
                            next_out_tangent = cmds.keyTangent(curve, time=(next_key, next_key), query=True, outTangentType=True)[0]
                            if next_out_tangent == "step":
                                out_tangent_type = "step"
                        except:
                            pass
                    cmds.keyTangent(curve, time=(current_time, current_time), inTangentType="auto", outTangentType=out_tangent_type)
        _stored_keys_sel = []
        for curve in _stored_anim_curves:
            if cmds.objExists(curve):
                _stored_keys_sel.append([current_time])
            else:
                _stored_keys_sel.append([])
    for n, curve in enumerate(_stored_anim_curves):
        if not _stored_keys_sel[n]:
            continue
        mfn = slider_utils.get_mfn_anim_curve(curve)
        if mfn is None:
            continue
        _mfn_curves[curve] = mfn
        sel_times = _stored_keys_sel[n]
        num_keys = mfn.numKeys
        indexes = []
        original_pairs = []
        for time_val in sel_times:
            idx = slider_utils.get_key_index_at_time(mfn, time_val)
            if idx >= 0:
                indexes.append(idx)
                # Always use cmds.keyframe for consistent UI units (works for both translate and rotate)
                val_list = cmds.keyframe(curve, index=(idx, idx), query=True, valueChange=True)
                val = val_list[0] if val_list else 0.0
                original_pairs.append((time_val, val))
        if not original_pairs:
            continue
        _stored_key_indexes[curve] = indexes
        _original_values[curve] = original_pairs
        if mode == "left":
            first_idx = indexes[0]
            if first_idx > 0:
                val_list = cmds.keyframe(curve, index=(first_idx - 1, first_idx - 1), query=True, valueChange=True)
                pivot_val = val_list[0] if val_list else 0.0
            else:
                pivot_val = original_pairs[0][1]
        elif mode == "right":
            last_idx = indexes[-1]
            if last_idx < num_keys - 1:
                val_list = cmds.keyframe(curve, index=(last_idx + 1, last_idx + 1), query=True, valueChange=True)
                pivot_val = val_list[0] if val_list else 0.0
            else:
                pivot_val = original_pairs[-1][1]
        else:
            values = [v for _, v in original_pairs]
            if len(values) == 1:
                single_idx = indexes[0]
                neighbor_values = []
                if single_idx > 0:
                    val_list = cmds.keyframe(curve, index=(single_idx - 1, single_idx - 1), query=True, valueChange=True)
                    if val_list:
                        neighbor_values.append(val_list[0])
                if single_idx < num_keys - 1:
                    val_list = cmds.keyframe(curve, index=(single_idx + 1, single_idx + 1), query=True, valueChange=True)
                    if val_list:
                        neighbor_values.append(val_list[0])
                if neighbor_values:
                    pivot_val = sum(neighbor_values) / len(neighbor_values)
                else:
                    pivot_val = 0.0
            else:
                min_val, max_val = min(values), max(values)
                pivot_val = (min_val + max_val) / 2.0
        _pivot_values[curve] = pivot_val


def scale_keys(slider_val):
    global _original_values, _pivot_values, _stored_key_indexes, _mfn_curves
    if not _original_values:
        return
    if slider_val >= 0:
        scale_factor = 1 + slider_val
    else:
        scale_factor = 1 + slider_val * 2
    for curve in _original_values:
        if curve not in _mfn_curves:
            continue
        pivot_val = _pivot_values[curve]
        key_indexes = _stored_key_indexes.get(curve, [])
        original_pairs = _original_values[curve]
        for i, key_index in enumerate(key_indexes):
            if i >= len(original_pairs):
                continue
            try:
                original_val = original_pairs[i][1]
                new_val = pivot_val + (original_val - pivot_val) * scale_factor
                # Use cmds.keyframe for setting values - consistent UI units
                cmds.keyframe(curve, index=(key_index, key_index), valueChange=new_val)
            except:
                continue


def scale_left_logic(value, last_update_time, update_throttle_ms):
    global _dragging
    slider_val = value / 100.0
    current_time = time.time() * 1000
    time_since_last = current_time - last_update_time
    if not _dragging:
        _dragging = True
        last_update_time = current_time
        slider_utils.safe_undo_chunk_open("Scale Left")
        cache_original_values("left")
        scale_keys(slider_val)
    else:
        if time_since_last >= update_throttle_ms:
            last_update_time = current_time
            scale_keys(slider_val)
    return last_update_time, "Scale Left: {0}".format(value)


def scale_right_logic(value, last_update_time, update_throttle_ms):
    global _dragging
    slider_val = value / 100.0
    current_time = time.time() * 1000
    time_since_last = current_time - last_update_time
    if not _dragging:
        _dragging = True
        last_update_time = current_time
        slider_utils.safe_undo_chunk_open("Scale Right")
        cache_original_values("right")
        scale_keys(slider_val)
    else:
        if time_since_last >= update_throttle_ms:
            last_update_time = current_time
            scale_keys(slider_val)
    return last_update_time, "Scale Right: {0}".format(value)


def scale_avg_logic(value, last_update_time, update_throttle_ms):
    global _dragging
    slider_val = value / 100.0
    current_time = time.time() * 1000
    time_since_last = current_time - last_update_time
    if not _dragging:
        _dragging = True
        last_update_time = current_time
        slider_utils.safe_undo_chunk_open("Scale Average")
        cache_original_values("avg")
        scale_keys(slider_val)
    else:
        if time_since_last >= update_throttle_ms:
            last_update_time = current_time
            scale_keys(slider_val)
    return last_update_time, "Scale Average: {0}".format(value)


def slider_logic(value, mouse_pressed, last_update_time, update_throttle_ms, shift_pressed, ctrl_pressed):
    if not mouse_pressed:
        return last_update_time, "Scale Left: {0}".format(value)
    if ctrl_pressed:
        return scale_avg_logic(value, last_update_time, update_throttle_ms)
    elif shift_pressed:
        return scale_right_logic(value, last_update_time, update_throttle_ms)
    else:
        return scale_left_logic(value, last_update_time, update_throttle_ms)


def reset_slider(slider_widget):
    global _dragging, _original_values, _pivot_values, _stored_keys_sel, _stored_anim_curves
    global _stored_key_indexes, _mfn_curves, _current_mode
    slider_widget.blockSignals(True)
    slider_widget.setValue(0)
    slider_widget.blockSignals(False)
    if _dragging:
        slider_utils.safe_undo_chunk_close()
        _dragging = False
    _original_values = {}
    _pivot_values = {}
    _stored_keys_sel = []
    _stored_anim_curves = []
    _stored_key_indexes = {}
    _mfn_curves = {}
    _current_mode = None
