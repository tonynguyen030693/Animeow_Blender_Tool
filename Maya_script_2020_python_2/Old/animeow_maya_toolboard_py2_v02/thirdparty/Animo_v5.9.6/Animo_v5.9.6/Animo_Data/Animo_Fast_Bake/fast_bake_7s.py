import maya.cmds as cmds
import maya.mel as mel
import os
import sys

MARK_COLOR = "#32CD32"
MARK_OPACITY = 0.25


def get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except Exception:
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
    
    if n in sys.modules:
        del sys.modules[n]
    
    try:
        import importlib
        return importlib.import_module(n)
    except Exception:
        return None


def get_graph_editor_key_range():
    """Get range from selected keys in graph editor"""
    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None
    
    min_selected_time = min(selected_keys)
    max_selected_time = max(selected_keys)
    
    return (int(min_selected_time), int(max_selected_time))


def get_timeline_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    range_visible = cmds.timeControl(playback_slider, query=True, rangeVisible=True)
    if range_visible:
        time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        start_range = int(time_range[0])
        end_range = int(time_range[1] - 1)
        if end_range > start_range:
            return start_range, end_range
    return 0, 0


def get_playback_range():
    min_time = cmds.playbackOptions(q=True, min=True)
    max_time = cmds.playbackOptions(q=True, max=True)
    return int(min_time), int(max_time)


def get_marker_range(pnl):
    """Determine which range to mark based on cursor location"""
    # Only use graph editor key range if cursor is IN the graph editor
    if pnl == 'graphEditor1':
        graph_range = get_graph_editor_key_range()
        if graph_range:
            return graph_range
    
    # Check timeline range selection
    start_range, end_range = get_timeline_range()
    if (end_range - start_range) > 0:
        return start_range, end_range
    
    # Fall back to full playback range
    return get_playback_range()


def fast_bake():
    Min = cmds.playbackOptions(q=True, min=True)
    Max = cmds.playbackOptions(q=True, max=True)
    pnl = cmds.getPanel(up=True)
    selCurve = cmds.keyframe(q=True, selected=True)
    
    if pnl == 'graphEditor1':
        if selCurve:
            mel.eval('bakeResults -sampleBy 1 -oversamplingRate 1 -preserveOutsideKeys 1 -sparseAnimCurveBake 0;')
    
    else:
        if selCurve:
            cmds.selectKey(cl=True)
        
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        StartRange = int(timeRange[0])
        EndRange = int(timeRange[1] - 1)
        selection = cmds.ls(sl=True)
        
        if selection:
            cmds.waitCursor(state=True)
            cmds.refresh(suspend=True)
            cmds.evaluationManager(mode="off")
            CBsel = cmds.channelBox("mainChannelBox", q=True, sma=True)
            
            if CBsel:
                if EndRange - StartRange == 0:
                    cmds.bakeResults(sm=True, pok=True, t=(Min, Max), at=CBsel, sb="7")
                else:
                    cmds.bakeResults(sm=True, pok=True, t=(StartRange, EndRange), at=CBsel, sb="7")
            else:
                if EndRange - StartRange == 0:
                    cmds.bakeResults(sm=True, pok=True, t=(Min, Max), sb="7")
                else:
                    cmds.bakeResults(sm=True, pok=True, t=(StartRange, EndRange), sb="7")
            
            cmds.waitCursor(state=False)
            cmds.refresh(suspend=False)
            cmds.evaluationManager(mode="parallel")
            mel.eval("paneLayout -e -manage true $gMainPane")


def run():
    marker_module = load_marker_module()
    
    selection = cmds.ls(sl=True)
    pnl = cmds.getPanel(up=True)
    selCurve = cmds.keyframe(q=True, selected=True)
    
    if marker_module and (selection or (pnl == 'graphEditor1' and selCurve)):
        marker_start, marker_end = get_marker_range(pnl)
        marker_module.mark_range(marker_start, marker_end, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
        cmds.refresh(force=True)
    
    fast_bake()
    
    if marker_module:
        marker_module.trigger_fade(delay=500)


if __name__ == "__main__":
    run()
