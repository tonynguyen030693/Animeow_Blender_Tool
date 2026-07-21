import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import time

try:
    from . import slider_utils
except ImportError:
    import slider_utils

cascadePushClick = False
cascadeStoredKeyValues = {}
cascadeStoredAnimCurves = []
cascadeStoredKeysSel = []
cascadeMfnCurves = {}


def apply_cascade_keys(t_value):
    global cascadeStoredAnimCurves, cascadeStoredKeysSel, cascadeStoredKeyValues, cascadeMfnCurves
    if not cascadeStoredAnimCurves:
        return
    for n, curve in enumerate(cascadeStoredAnimCurves):
        if not cascadeStoredKeysSel[n] or curve not in cascadeMfnCurves:
            continue
        mfn = cascadeMfnCurves[curve]
        try:
            num_keys = mfn.numKeys
        except:
            continue
        if num_keys == 0:
            continue
        original_values = cascadeStoredKeyValues.get(curve, [])
        if not original_values:
            continue
        all_key_times = slider_utils.get_all_key_times(mfn)
        for selected_time in cascadeStoredKeysSel[n]:
            selected_idx = None
            for i, key_time in enumerate(all_key_times):
                if abs(key_time - selected_time) < 0.001:
                    selected_idx = i
                    break
            if selected_idx is None or selected_idx >= len(original_values):
                continue
            selected_original_value = original_values[selected_idx]
            left_neighbor_value = None
            right_neighbor_value = None
            if selected_idx > 0:
                left_neighbor_value = original_values[selected_idx - 1]
            if selected_idx < len(original_values) - 1:
                right_neighbor_value = original_values[selected_idx + 1]
            if left_neighbor_value is None and right_neighbor_value is None:
                continue
            if left_neighbor_value is None:
                left_neighbor_value = selected_original_value
            if right_neighbor_value is None:
                right_neighbor_value = selected_original_value
            keys_to_move = []
            target_value = selected_original_value
            if t_value < 1.0:
                blend_factor = 1.0 - t_value
                target_value = selected_original_value + (left_neighbor_value - selected_original_value) * blend_factor
                keys_to_move = list(range(selected_idx, len(original_values)))
            else:
                blend_factor = t_value - 1.0
                target_value = selected_original_value + (right_neighbor_value - selected_original_value) * blend_factor
                keys_to_move = list(range(0, selected_idx + 1))
            movement_offset = target_value - selected_original_value
            for key_idx in keys_to_move:
                if key_idx >= len(original_values) or key_idx >= num_keys:
                    continue
                new_value = original_values[key_idx] + movement_offset
                slider_utils.set_key_value(curve, key_idx, new_value)


def slider_logic(value, mouse_pressed, last_update_time, update_throttle_ms):
    global cascadePushClick, cascadeStoredAnimCurves, cascadeStoredKeysSel, cascadeStoredKeyValues, cascadeMfnCurves
    t_value = value / 100.0
    show_value = abs(round((t_value - 1.0) * 100.0, 2))
    if show_value >= 1 or show_value == 0:
        show_value = int(round(show_value))
    status = "Cascade: {0}%".format(show_value)
    if not mouse_pressed:
        return last_update_time, status
    current_time = time.time() * 1000
    time_since_last = current_time - last_update_time
    if time_since_last < update_throttle_ms and cascadePushClick:
        return last_update_time, status
    last_update_time = current_time
    if not cascadePushClick:
        cascadePushClick = True
        slider_utils.safe_undo_chunk_open("Cascade Keys")
        getCurves = slider_utils.get_anim_curves()
        cascadeStoredAnimCurves = getCurves[0]
        getFrom = getCurves[1]
        if not cascadeStoredAnimCurves:
            return last_update_time, status
        cascadeStoredKeysSel = slider_utils.get_keys_sel(cascadeStoredAnimCurves, getFrom)
        cascadeStoredKeyValues = {}
        cascadeMfnCurves = {}
        for n, curve in enumerate(cascadeStoredAnimCurves):
            if not cascadeStoredKeysSel[n]:
                continue
            mfn = slider_utils.get_mfn_anim_curve(curve)
            if mfn is None:
                continue
            cascadeMfnCurves[curve] = mfn
            all_key_values = slider_utils.get_all_key_values(mfn)
            if all_key_values:
                cascadeStoredKeyValues[curve] = list(all_key_values)
    apply_cascade_keys(t_value)
    return last_update_time, status


def reset_slider(slider_widget):
    global cascadePushClick, cascadeStoredKeyValues, cascadeStoredAnimCurves, cascadeStoredKeysSel, cascadeMfnCurves
    final_value = slider_widget.value()
    if final_value != 100 and cascadePushClick:
        t_value = final_value / 100.0
        apply_cascade_keys(t_value)
    slider_widget.blockSignals(True)
    slider_widget.setValue(100)
    slider_widget.blockSignals(False)
    if cascadePushClick:
        slider_utils.safe_undo_chunk_close()
        cascadePushClick = False
        cascadeStoredKeyValues = {}
        cascadeStoredAnimCurves = []
        cascadeStoredKeysSel = []
        cascadeMfnCurves = {}
