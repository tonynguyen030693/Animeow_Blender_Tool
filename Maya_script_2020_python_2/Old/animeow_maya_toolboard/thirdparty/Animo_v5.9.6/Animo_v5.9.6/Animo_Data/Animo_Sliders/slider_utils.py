import maya.cmds as cmds
from maya import mel
import maya.utils
import platform
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import math

IS_MACOS = platform.system() == "Darwin"

_undo_chunk_open = False


def safe_undo_chunk_open(chunk_name="Slider Operation"):
    global _undo_chunk_open
    if _undo_chunk_open:
        return
    try:
        cmds.undoInfo(openChunk=True, chunkName=chunk_name)
        _undo_chunk_open = True
        if IS_MACOS:
            maya.utils.processIdleEvents()
    except:
        pass


def safe_undo_chunk_close():
    global _undo_chunk_open
    if not _undo_chunk_open:
        return
    try:
        if IS_MACOS:
            cmds.refresh()
            maya.utils.processIdleEvents()
        cmds.undoInfo(closeChunk=True)
        _undo_chunk_open = False
    except:
        pass


def get_mobject(node_name):
    try:
        sel = om2.MSelectionList()
        sel.add(node_name)
        return sel.getDependNode(0)
    except:
        return None


def get_mfn_anim_curve(node_name):
    mobj = get_mobject(node_name)
    if mobj is None:
        return None
    try:
        return oma2.MFnAnimCurve(mobj)
    except:
        return None


def is_angle_curve(mfn):
    """Check if the anim curve is for a rotation/angle attribute (returns radians)"""
    try:
        return mfn.animCurveType == oma2.MFnAnimCurve.kAnimCurveTA
    except:
        return False


def get_key_value(mfn, index):
    """Get key value, converting radians to degrees for rotation curves"""
    value = mfn.value(index)
    if is_angle_curve(mfn):
        value = math.degrees(value)
    return value


def get_anim_curves():
    anim_curves = cmds.keyframe(query=True, name=True, selected=True)
    get_from = "graphEditor"
    if not anim_curves:
        get_from = "channelBox"
        selected_objects = cmds.ls(selection=True)
        if selected_objects:
            channel_box = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
            selected_attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True)
            if selected_attrs:
                anim_curves = []
                for obj in selected_objects:
                    for attr in selected_attrs:
                        connections = cmds.listConnections(
                            '{}.{}'.format(obj, attr),
                            source=True,
                            destination=False,
                            type='animCurve'
                        )
                        if connections:
                            anim_curves.extend(connections)
                if anim_curves:
                    anim_curves = list(set(anim_curves))
    if not anim_curves:
        get_from = "timeline"
        play_back_slider = mel.eval('$temp=$gPlayBackSlider')
        anim_curves = cmds.timeControl(play_back_slider, query=True, animCurveNames=True)
    return [anim_curves, get_from]


def get_timeline_range():
    play_back_slider = mel.eval('$temp_playBackSlider=$gPlayBackSlider')
    time_range = cmds.timeControl(play_back_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return [start_range, end_range]


def get_keys_sel(anim_curves, get_from):
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
            mfn = get_mfn_anim_curve(node)
            if mfn is None:
                keys_sel.append([])
                continue
            num_keys = mfn.numKeys
            if num_keys == 0:
                keys_sel.append([])
                continue
            range_keys = []
            for i in range(num_keys):
                key_time = mfn.input(i).value
                if range_val[0] <= key_time < range_val[1]:
                    range_keys.append(key_time)
            keys_sel.append(range_keys)
    return keys_sel


def get_key_index_at_time(mfn, time_val):
    num_keys = mfn.numKeys
    for i in range(num_keys):
        if abs(mfn.input(i).value - time_val) < 0.001:
            return i
    return -1


def get_key_indexes(curve, key_times):
    if not key_times:
        return []
    mfn = get_mfn_anim_curve(curve)
    if mfn is None:
        return []
    indexes = []
    for key_time in key_times:
        idx = get_key_index_at_time(mfn, key_time)
        if idx >= 0:
            indexes.append(idx)
    return indexes


def get_all_key_times(mfn):
    num_keys = mfn.numKeys
    return [mfn.input(i).value for i in range(num_keys)]


def get_all_key_values(mfn):
    """Get all key values, converting radians to degrees for rotation curves"""
    num_keys = mfn.numKeys
    if is_angle_curve(mfn):
        return [math.degrees(mfn.value(i)) for i in range(num_keys)]
    return [mfn.value(i) for i in range(num_keys)]


def set_key_value(curve, index, value):
    cmds.keyframe(curve, index=(index, index), valueChange=value, absolute=True)
