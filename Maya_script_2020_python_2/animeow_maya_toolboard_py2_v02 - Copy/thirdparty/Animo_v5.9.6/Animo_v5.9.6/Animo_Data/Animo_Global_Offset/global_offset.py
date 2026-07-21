import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import os
import sys

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance

MARK_COLOR = "#3A8A9E"
MARK_OPACITY = 0.40

STORAGE_PREFIX = "_animo_global_offset"


def is_graph_editor_focused():
    try:
        panel = cmds.getPanel(withFocus=True)
        if panel and 'graphEditor' in panel:
            return True
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
    except:
        pass
    return False


def idle_check():
    if not is_enabled():
        return
    
    if get_storage('applying'):
        return
    
    current_time = cmds.currentTime(q=True)
    last_time = get_storage('last_time')
    
    if last_time is not None and abs(current_time - last_time) > 0.001:
        set_storage('last_time', current_time)
        return
    
    if not is_graph_editor_focused():
        return
    
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    current_offsets = get_storage('offsets') or {}
    
    if not original_snapshot or not stored_range:
        return
    
    selected = cmds.ls(selection=True)
    if not selected:
        return
    
    for obj in selected:
        if obj not in original_snapshot:
            continue
        
        for attr, key_data in original_snapshot[obj].items():
            if not key_data:
                continue
            
            attr_full = "{}.{}".format(obj, attr)
            offset_key = "{}:{}".format(obj, attr)
            stored_offset = current_offsets.get(offset_key, 0)
            
            for key_time, original_val in key_data.items():
                try:
                    current_key_vals = cmds.keyframe(attr_full, q=True, time=(key_time, key_time), valueChange=True)
                    if current_key_vals:
                        current_key_val = current_key_vals[0]
                        detected_offset = current_key_val - original_val
                        
                        if abs(detected_offset - stored_offset) > 1e-6:
                            apply_offset_at_frame_graph(key_time, obj, attr, detected_offset)
                            return
                except:
                    continue


def apply_offset_at_frame_graph(frame_time, changed_obj, changed_attr, new_offset):
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    
    if not original_snapshot or not stored_range:
        return
    
    if get_storage('applying'):
        return
    
    set_storage('applying', True)
    
    if changed_obj not in original_snapshot:
        set_storage('applying', False)
        return
    
    if changed_attr not in original_snapshot[changed_obj]:
        set_storage('applying', False)
        return
    
    key_data = original_snapshot[changed_obj][changed_attr]
    if not key_data:
        set_storage('applying', False)
        return
    
    attr_full = "{}.{}".format(changed_obj, changed_attr)
    
    cmds.undoInfo(stateWithoutFlush=False)
    
    try:
        for t, orig_val in key_data.items():
            new_key_val = orig_val + new_offset
            cmds.keyframe(attr_full, edit=True, time=(t, t), valueChange=new_key_val, absolute=True)
        
        current_offsets = get_storage('offsets') or {}
        offset_key = "{}:{}".format(changed_obj, changed_attr)
        current_offsets[offset_key] = new_offset
        set_storage('offsets', current_offsets)
    
    finally:
        cmds.undoInfo(stateWithoutFlush=True)
        set_storage('applying', False)


def clear_timeline_selection():
    app = QtWidgets.QApplication.instance()
    
    widgetStr = mel.eval('$gPlayBackSlider=$gPlayBackSlider')
    ptr = omui.MQtUtil.findControl(widgetStr)
    slider = wrapInstance(int(ptr), QtWidgets.QWidget)
    
    slider_height = slider.size().height()
    
    current_frame = cmds.currentTime(query=True)
    
    click_pos = QtCore.QPoint(-10, int(slider_height / 2.0))
    
    try:
        press_event = QtGui.QMouseEvent(
            QtCore.QEvent.Type.MouseButtonPress,
            click_pos,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        release_event = QtGui.QMouseEvent(
            QtCore.QEvent.Type.MouseButtonRelease,
            click_pos,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
    except AttributeError:
        press_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonPress,
            click_pos,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.NoModifier
        )
        release_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonRelease,
            click_pos,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.NoModifier
        )
    
    app.sendEvent(slider, press_event)
    app.sendEvent(slider, release_event)
    
    app.processEvents()
    
    cmds.currentTime(current_frame)


def get_storage(key):
    name = "{}_{}".format(STORAGE_PREFIX, key)
    if hasattr(cmds, name):
        return getattr(cmds, name)
    return None


def set_storage(key, value):
    name = "{}_{}".format(STORAGE_PREFIX, key)
    setattr(cmds, name, value)


def clear_storage():
    for attr in ['jobs', 'snapshot', 'range', 'callback', 'idle_callback', 'applying', 'last_time', 'offsets']:
        name = "{}_{}".format(STORAGE_PREFIX, attr)
        if hasattr(cmds, name):
            delattr(cmds, name)


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except:
        return "unknown"


def load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(folder)
        marker_folder = os.path.join(parent_folder, "Animo_Keys_Tangent")
    except NameError:
        marker_folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")
    
    v = get_maya_version()
    n = "mark_frame"
    py = os.path.join(marker_folder, n + ".py")
    pyc = os.path.join(marker_folder, "{}_py{}.pyc".format(n, v))
    
    if not os.path.exists(py) and not os.path.exists(pyc):
        return None
    
    if marker_folder not in sys.path:
        sys.path.insert(0, marker_folder)
    
    try:
        import importlib
        if n in sys.modules:
            return sys.modules[n]
        return importlib.import_module(n)
    except:
        return None


def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
    except:
        pass
    return False


def get_graph_editor_key_range():
    if not is_graph_editor_active():
        return None
    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None
    
    min_time = min(selected_keys)
    max_time = max(selected_keys)
    
    # Only use selection if keys span multiple frames
    if abs(max_time - min_time) < 0.001:
        return None  # All keys on same frame, ignore selection
    
    return (min_time, max_time)


def get_timeline_range():
    playback_slider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(time_range[0])
    end = int(time_range[1] - 1)
    if end - start > 0:
        return start, end
    return None


def get_playback_range():
    return int(cmds.playbackOptions(q=True, minTime=True)), int(cmds.playbackOptions(q=True, maxTime=True))


def get_active_range():
    graph_range = get_graph_editor_key_range()
    if graph_range:
        return int(graph_range[0]), int(graph_range[1])
    timeline_range = get_timeline_range()
    if timeline_range:
        return timeline_range
    return get_playback_range()


def get_keyable_attrs(obj):
    attrs = []
    for attr in ['translateX', 'translateY', 'translateZ',
                 'rotateX', 'rotateY', 'rotateZ',
                 'scaleX', 'scaleY', 'scaleZ']:
        try:
            if cmds.getAttr("{}.{}".format(obj, attr), settable=True):
                if cmds.getAttr("{}.{}".format(obj, attr), keyable=True):
                    attrs.append(attr)
        except:
            pass
    
    user_attrs = cmds.listAttr(obj, keyable=True, unlocked=True)
    if user_attrs:
        for attr in user_attrs:
            if attr not in attrs:
                try:
                    if cmds.getAttr("{}.{}".format(obj, attr), settable=True):
                        attrs.append(attr)
                except:
                    pass
    return attrs


def interpolate_value(key_data, target_time):
    if not key_data:
        return None
    
    times = sorted(key_data.keys())
    
    for t in times:
        if abs(t - target_time) < 0.001:
            return key_data[t]
    
    if target_time <= times[0]:
        return key_data[times[0]]
    
    if target_time >= times[-1]:
        return key_data[times[-1]]
    
    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        if t1 <= target_time <= t2:
            v1, v2 = key_data[t1], key_data[t2]
            ratio = (target_time - t1) / (t2 - t1)
            return v1 + ratio * (v2 - v1)
    
    return None


def capture_snapshot(objects, start_time, end_time):
    snapshot = {}
    
    for obj in objects:
        snapshot[obj] = {}
        
        attrs = get_keyable_attrs(obj)
        for attr in attrs:
            attr_full = "{}.{}".format(obj, attr)
            
            key_times = cmds.keyframe(attr_full, q=True, timeChange=True, time=(start_time, end_time))
            if key_times:
                snapshot[obj][attr] = {}
                for t in key_times:
                    try:
                        val = cmds.keyframe(attr_full, q=True, valueChange=True, time=(t, t))[0]
                        snapshot[obj][attr][t] = val
                    except:
                        pass
    
    return snapshot


def apply_offset():
    if get_storage('applying'):
        return
    
    original_snapshot = get_storage('snapshot')
    stored_range = get_storage('range')
    
    if not original_snapshot or not stored_range:
        return
    
    selected = cmds.ls(selection=True)
    if not selected:
        return
    
    current_time = cmds.currentTime(q=True)
    start_time, end_time = stored_range
    
    if current_time < start_time or current_time > end_time:
        return
    
    offsets_to_apply = []
    
    for obj in selected:
        if obj not in original_snapshot:
            continue
        
        for attr, key_data in original_snapshot[obj].items():
            if not key_data:
                continue
            
            attr_full = "{}.{}".format(obj, attr)
            
            try:
                current_val = cmds.getAttr(attr_full)
                if isinstance(current_val, (list, tuple)):
                    current_val = current_val[0]
            except:
                continue
            
            expected_val = interpolate_value(key_data, current_time)
            if expected_val is None:
                continue
            
            offset = current_val - expected_val
            
            if abs(offset) < 1e-9:
                continue
            
            offsets_to_apply.append((obj, attr, offset, key_data))
    
    if not offsets_to_apply:
        return
    
    set_storage('applying', True)
    
    cmds.undoInfo(stateWithoutFlush=False)
    
    try:
        current_offsets = get_storage('offsets') or {}
        
        for obj, attr, offset, key_data in offsets_to_apply:
            attr_full = "{}.{}".format(obj, attr)
            
            for t, original_val in key_data.items():
                new_key_val = original_val + offset
                cmds.keyframe(attr_full, edit=True, time=(t, t), valueChange=new_key_val, absolute=True)
            
            offset_key = "{}:{}".format(obj, attr)
            current_offsets[offset_key] = offset
        
        set_storage('offsets', current_offsets)
        set_storage('last_time', current_time)
    
    finally:
        cmds.undoInfo(stateWithoutFlush=True)
        set_storage('applying', False)


def kill_jobs():
    jobs = get_storage('jobs')
    if jobs:
        for job_id in jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    cmds.scriptJob(kill=job_id, force=True)
            except:
                pass
    set_storage('jobs', [])


def is_enabled():
    jobs = get_storage('jobs')
    if jobs:
        for job_id in jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    return True
            except:
                pass
    return False


def enable():
    kill_jobs()
    
    selected = cmds.ls(selection=True)
    if not selected:
        cmds.warning("Global Offset: Please select objects first")
        return
    
    start_time, end_time = get_active_range()
    
    clear_timeline_selection()
    
    snapshot = capture_snapshot(selected, start_time, end_time)
    
    has_keys = False
    for obj in snapshot:
        for attr in snapshot[obj]:
            if snapshot[obj][attr]:
                has_keys = True
                break
        if has_keys:
            break
    
    if not has_keys:
        cmds.warning("Global Offset: No keys found in range")
        return
    
    set_storage('snapshot', snapshot)
    set_storage('range', (start_time, end_time))
    set_storage('callback', apply_offset)
    set_storage('idle_callback', idle_check)
    set_storage('applying', False)
    set_storage('offsets', {})
    set_storage('last_time', cmds.currentTime(q=True))
    
    callback_func = get_storage('callback')
    idle_callback_func = get_storage('idle_callback')
    
    job1 = cmds.scriptJob(runOnce=False, killWithScene=True, event=["DragRelease", callback_func])
    job2 = cmds.scriptJob(runOnce=False, killWithScene=True, event=["idle", idle_callback_func])
    
    set_storage('jobs', [job1, job2])
    
    marker = load_marker_module()
    if marker:
        marker.mark_range(start_time, end_time, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)


def disable():
    original_snapshot = get_storage('snapshot')
    current_offsets = get_storage('offsets') or {}
    
    has_changes = False
    if original_snapshot and current_offsets:
        for offset_key, offset in current_offsets.items():
            if abs(offset) > 1e-9:
                has_changes = True
                break
    
    if has_changes:
        cmds.undoInfo(stateWithoutFlush=False)
        for obj in original_snapshot:
            for attr, key_data in original_snapshot[obj].items():
                if not key_data:
                    continue
                
                attr_full = "{}.{}".format(obj, attr)
                
                for t, original_val in key_data.items():
                    cmds.keyframe(attr_full, edit=True, time=(t, t), valueChange=original_val, absolute=True)
        cmds.undoInfo(stateWithoutFlush=True)
        
        cmds.undoInfo(openChunk=True, chunkName="Global Offset")
        
        try:
            for obj in original_snapshot:
                for attr, key_data in original_snapshot[obj].items():
                    if not key_data:
                        continue
                    
                    offset_key = "{}:{}".format(obj, attr)
                    offset = current_offsets.get(offset_key, 0)
                    
                    if abs(offset) < 1e-9:
                        continue
                    
                    attr_full = "{}.{}".format(obj, attr)
                    
                    for t, original_val in key_data.items():
                        new_val = original_val + offset
                        cmds.keyframe(attr_full, edit=True, time=(t, t), valueChange=new_val, absolute=True)
        
        finally:
            cmds.undoInfo(closeChunk=True)
        
        current = cmds.currentTime(q=True)
        cmds.currentTime(current, edit=True, update=True)
    
    kill_jobs()
    clear_storage()
    
    marker = load_marker_module()
    if marker:
        marker.trigger_fade(delay=0, fast=True)


def toggle():
    if is_enabled():
        disable()
    else:
        enable()


def run():
    toggle()