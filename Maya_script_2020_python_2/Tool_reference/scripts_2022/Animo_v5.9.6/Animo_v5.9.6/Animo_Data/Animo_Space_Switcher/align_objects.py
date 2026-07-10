from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.mel as mel
import os
import sys

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


def get_timeline_range():
    playback_slider = mel.eval('$tmp = $gPlayBackSlider')
    range_array = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(range_array[0])
    end = int(range_array[1]) - 1
    if end > start:
        return start, end
    return None


def align():
    sel = cmds.ls(sl=True)
    
    if len(sel) < 2:
        cmds.inViewMessage(amg='<span style="color:#f58b3a;">Select at least 2 objects</span>', pos="botCenter", fade=True)
        return
    
    target = sel[-1]
    sources = sel[:-1]
    
    timeline_range = get_timeline_range()
    
    if timeline_range:
        align_range(sources, target, timeline_range[0], timeline_range[1])
    else:
        marker = load_mark_frame()
        if marker:
            marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
        
        cmds.matchTransform(sources, target, pos=True, rot=True)
        for src in sources:
            cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])


def align_range(sources, target, start_frame, end_frame):
    current_time = cmds.currentTime(query=True)
    
    keys = cmds.keyframe(target, query=True, time=(start_frame, end_frame))
    
    if not keys:
        marker = load_mark_frame()
        if marker:
            marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
        
        cmds.matchTransform(sources, target, pos=True, rot=True)
        for src in sources:
            cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])
        return
    
    keys = sorted(set([int(k) for k in keys]))
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(keys[0], keys[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    cmds.undoInfo(openChunk=True, chunkName="Align Range")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for key in keys:
            cmds.currentTime(key)
            cmds.matchTransform(sources, target, pos=True, rot=True)
            for src in sources:
                cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])
    finally:
        cmds.currentTime(current_time)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        cmds.undoInfo(closeChunk=True)
