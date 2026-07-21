import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import os
import json

FRAME_RANGE = 18
POINT_SIZE = 5.0
LINE_WIDTH = 4.0
FRAMES_PER_UPDATE = 3
GROUP_NAME = "Tracify"
COLORS = [(0.85, 0.12, 0.11), (1.0, 0.4, 0.7), (1.0, 0.9, 0.15), (0.7, 0.3, 0.9), (0.3, 0.6, 1.0)]
KEY_COLOR = (0.95, 0.45, 0.45)

_colorIndex = 0
_trackers = {}
_cache = {}
_jobs = []
_attrJobs = []
_idleJob = False
_checkJob = None
_dirtyQueue = []
_lastFrame = -999999


def _loadPlugin():
    pluginName = "tracify_node.py"
    try:
        if cmds.pluginInfo(pluginName, query=True, loaded=True):
            return True
    except:
        pass
    thisDir = os.path.dirname(os.path.abspath(__file__))
    pluginPath = os.path.join(thisDir, pluginName)
    if not os.path.exists(pluginPath):
        cmds.error("Tracify: Cannot find " + pluginPath)
        return False
    try:
        cmds.loadPlugin(pluginPath)
        return True
    except Exception as e:
        cmds.error("Tracify: Failed to load plugin - " + str(e))
        return False


def _isPluginLoaded():
    try:
        return cmds.pluginInfo("tracify_node.py", query=True, loaded=True)
    except:
        return False


def _getNextColor():
    global _colorIndex
    color = COLORS[_colorIndex % len(COLORS)]
    _colorIndex += 1
    return color


def _getAnimRange():
    return int(oma2.MAnimControl.animationStartTime().value), int(oma2.MAnimControl.animationEndTime().value)


def _getPlaybackRange():
    return int(oma2.MAnimControl.minTime().value), int(oma2.MAnimControl.maxTime().value)


def _getCurrentFrame():
    return int(oma2.MAnimControl.currentTime().value)


def _getWorldPos(objName, frame=None):
    sel = om2.MSelectionList()
    try:
        sel.add(objName)
        dagPath = sel.getDagPath(0)
        fnDag = om2.MFnDagNode(dagPath)
        plug = fnDag.findPlug("worldMatrix", False).elementByLogicalIndex(0)
        if frame is not None:
            ctx = om2.MDGContext(om2.MTime(frame, om2.MTime.uiUnit()))
            matObj = plug.asMObject(ctx)
        else:
            matObj = plug.asMObject()
        mat = om2.MFnMatrixData(matObj).matrix()
        return [mat[12], mat[13], mat[14]]
    except:
        return None


def _getWorldPosRange(objName, startFrame, endFrame):
    positions = {}
    sel = om2.MSelectionList()
    try:
        sel.add(objName)
        dagPath = sel.getDagPath(0)
        fnDag = om2.MFnDagNode(dagPath)
        plug = fnDag.findPlug("worldMatrix", False).elementByLogicalIndex(0)
        timeUnit = om2.MTime.uiUnit()
        for f in range(startFrame, endFrame + 1):
            ctx = om2.MDGContext(om2.MTime(f, timeUnit))
            matObj = plug.asMObject(ctx)
            mat = om2.MFnMatrixData(matObj).matrix()
            positions[str(f)] = [mat[12], mat[13], mat[14]]
    except:
        pass
    return positions


def _getKeyframes(objName, start, end):
    keyframes = set()
    sel = om2.MSelectionList()
    try:
        sel.add(objName)
        dagPath = sel.getDagPath(0)
        node = dagPath.node()
        itDG = om2.MItDependencyGraph(node, om2.MFn.kAnimCurve, om2.MItDependencyGraph.kUpstream, om2.MItDependencyGraph.kDepthFirst, om2.MItDependencyGraph.kNodeLevel)
        while not itDG.isDone():
            curve = oma2.MFnAnimCurve(itDG.currentNode())
            for i in range(curve.numKeys):
                f = int(curve.input(i).value)
                if start <= f <= end:
                    keyframes.add(f)
            itDG.next()
    except:
        pass
    return list(keyframes)


def _createTrackerGrp(obj):
    shortName = obj.split("|")[-1].replace(":", "_")
    grpName = "tracify_grp_" + shortName
    if cmds.objExists(grpName):
        cmds.delete(grpName)
    grp = cmds.createNode("transform", name=grpName, skipSelect=True)
    cmds.parent(grp, obj)
    fullPath = cmds.ls(grp, long=True)[0]
    cmds.setAttr(fullPath + ".tx", 0)
    cmds.setAttr(fullPath + ".ty", 0)
    cmds.setAttr(fullPath + ".tz", 0)
    cmds.setAttr(fullPath + ".rx", 0)
    cmds.setAttr(fullPath + ".ry", 0)
    cmds.setAttr(fullPath + ".rz", 0)
    animStart, animEnd = _getAnimRange()
    numFrames = animEnd - animStart + 1
    timeUnit = om2.MTime.uiUnit()
    mSel = om2.MSelectionList()
    mSel.add(fullPath)
    grpNode = mSel.getDagPath(0).node()
    fnDep = om2.MFnDependencyNode(grpNode)
    times = om2.MTimeArray(numFrames, om2.MTime())
    vals = om2.MDoubleArray(numFrames, 0.0)
    for i in range(numFrames):
        times[i] = om2.MTime(animStart + i, timeUnit)
    for attr in ["translateX", "translateY", "translateZ"]:
        plug = fnDep.findPlug(attr, False)
        curveFn = oma2.MFnAnimCurve()
        curveFn.create(plug, oma2.MFnAnimCurve.kAnimCurveTL)
        curveFn.addKeys(times, vals, oma2.MFnAnimCurve.kTangentAuto, oma2.MFnAnimCurve.kTangentAuto)
    for attr in ["rx", "ry", "rz", "sx", "sy", "sz", "v"]:
        cmds.setAttr(fullPath + "." + attr, lock=True, keyable=False, channelBox=False)
    return fullPath


def _buildFullCache(nodeName, trackerGrp):
    global _cache
    playStart, playEnd = _getPlaybackRange()
    positions = _getWorldPosRange(trackerGrp, playStart, playEnd)
    keyframes = _getKeyframes(trackerGrp, playStart, playEnd)
    _cache[nodeName] = {
        "positions": positions,
        "keyframes": keyframes,
        "start": playStart,
        "end": playEnd
    }
    _syncCache(nodeName)


def _syncCache(nodeName):
    if nodeName in _cache and cmds.objExists(nodeName):
        undoState = cmds.undoInfo(q=True, state=True)
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            cmds.setAttr(nodeName + ".cacheData", json.dumps(_cache[nodeName], separators=(',', ':')), type="string")
        except:
            pass
        cmds.undoInfo(stateWithoutFlush=undoState)


def _onTimeChange():
    global _lastFrame, _trackers, _cache
    currentFrame = _getCurrentFrame()
    if currentFrame == _lastFrame:
        return
    _lastFrame = currentFrame
    if not _trackers:
        return
    for nodeName, trackerGrp in list(_trackers.items()):
        if not cmds.objExists(nodeName) or not cmds.objExists(trackerGrp):
            continue
        pos = _getWorldPos(trackerGrp)
        if pos and nodeName in _cache:
            _cache[nodeName]["positions"][str(currentFrame)] = pos
            _syncCache(nodeName)



def _startIdleProcess():
    global _idleJob
    if _idleJob:
        return
    if not _dirtyQueue:
        return
    _idleJob = True
    cmds.evalDeferred(_processNextFrame, lowestPriority=False)


def _processNextFrame():
    global _idleJob, _dirtyQueue, _cache
    _idleJob = False
    if not _dirtyQueue:
        return
    # Sort queue by distance from current frame (closest first)
    currentFrame = _getCurrentFrame()
    _dirtyQueue.sort(key=lambda x: abs(x[2] - currentFrame))
    nodesToSync = set()
    for _ in range(FRAMES_PER_UPDATE):
        if not _dirtyQueue:
            break
        nodeName, trackerGrp, frame = _dirtyQueue.pop(0)
        if cmds.objExists(trackerGrp) and nodeName in _cache:
            pos = _getWorldPos(trackerGrp, frame)
            if pos:
                _cache[nodeName]["positions"][str(frame)] = pos
                nodesToSync.add(nodeName)
    for nodeName in nodesToSync:
        _syncCache(nodeName)
    if nodesToSync:
        cmds.refresh()
    # Always reschedule immediately if more work
    if _dirtyQueue:
        cmds.evalDeferred(_processNextFrame, lowestPriority=False)


def _checkPositions():
    global _checkJob, _trackers, _cache, _dirtyQueue
    _checkJob = None
    if not _trackers:
        _scheduleCheck()
        return
    currentFrame = _getCurrentFrame()
    needsUpdate = False
    for nodeName, trackerGrp in list(_trackers.items()):
        if not cmds.objExists(nodeName) or not cmds.objExists(trackerGrp):
            continue
        if nodeName not in _cache:
            continue
        cache = _cache[nodeName]
        currentPos = _getWorldPos(trackerGrp)
        if not currentPos:
            continue
        cachedPos = cache["positions"].get(str(currentFrame))
        if cachedPos:
            dx = abs(currentPos[0] - cachedPos[0])
            dy = abs(currentPos[1] - cachedPos[1])
            dz = abs(currentPos[2] - cachedPos[2])
            if dx < 0.0001 and dy < 0.0001 and dz < 0.0001:
                continue
        cache["positions"][str(currentFrame)] = currentPos
        _syncCache(nodeName)
        needsUpdate = True
        # Queue ALL frames in cache, expanding outward from current
        start = cache.get("start", 0)
        end = cache.get("end", 9999)
        maxOffset = max(currentFrame - start, end - currentFrame)
        for offset in range(1, maxOffset + 1):
            for f in [currentFrame - offset, currentFrame + offset]:
                if start <= f <= end:
                    item = (nodeName, trackerGrp, f)
                    if item not in _dirtyQueue:
                        _dirtyQueue.append(item)
    if needsUpdate:
        _startIdleProcess()
    _scheduleCheck()


def _onGraphEditorChanged():
    global _trackers, _cache, _dirtyQueue
    if not _trackers:
        return
    currentFrame = _getCurrentFrame()
    for nodeName, trackerGrp in list(_trackers.items()):
        if not cmds.objExists(nodeName) or not cmds.objExists(trackerGrp):
            continue
        if nodeName not in _cache:
            continue
        cache = _cache[nodeName]
        currentPos = _getWorldPos(trackerGrp)
        if currentPos:
            cache["positions"][str(currentFrame)] = currentPos
            _syncCache(nodeName)
        # Queue ALL frames in cache, expanding outward from current
        start = cache.get("start", 0)
        end = cache.get("end", 9999)
        maxOffset = max(currentFrame - start, end - currentFrame)
        for offset in range(1, maxOffset + 1):
            for f in [currentFrame - offset, currentFrame + offset]:
                if start <= f <= end:
                    item = (nodeName, trackerGrp, f)
                    if item not in _dirtyQueue:
                        _dirtyQueue.append(item)
    _startIdleProcess()


def _scheduleCheck():
    global _checkJob
    if _checkJob is None:
        _checkJob = cmds.scriptJob(event=["idle", _checkPositions], runOnce=True)


def _setupJobs():
    global _jobs
    _clearJobs()
    _jobs.append(cmds.scriptJob(event=["timeChanged", _onTimeChange], protected=True))
    _jobs.append(cmds.scriptJob(event=["DragRelease", _checkPositions], protected=True))
    _jobs.append(cmds.scriptJob(event=["graphEditorChanged", _onGraphEditorChanged], protected=True))
    _jobs.append(cmds.scriptJob(event=["SceneOpened", clear], protected=True))
    _jobs.append(cmds.scriptJob(event=["NewSceneOpened", clear], protected=True))
    _setupAttrJobs()
    _scheduleCheck()


def _setupAttrJobs():
    global _attrJobs, _trackers
    _clearAttrJobs()
    for trackerGrp in _trackers.values():
        if cmds.objExists(trackerGrp):
            for attr in [".tx", ".ty", ".tz"]:
                job = cmds.scriptJob(attributeChange=[trackerGrp + attr, _checkPositions], protected=True)
                _attrJobs.append(job)


def _clearAttrJobs():
    global _attrJobs
    for j in _attrJobs:
        try:
            if cmds.scriptJob(exists=j):
                cmds.scriptJob(kill=j, force=True)
        except:
            pass
    _attrJobs = []


def _clearJobs():
    global _jobs, _idleJob, _checkJob, _dirtyQueue
    _clearAttrJobs()
    for j in _jobs:
        try:
            if cmds.scriptJob(exists=j):
                cmds.scriptJob(kill=j, force=True)
        except:
            pass
    _jobs = []
    _idleJob = False
    if _checkJob is not None:
        try:
            if cmds.scriptJob(exists=_checkJob):
                cmds.scriptJob(kill=_checkJob, force=True)
        except:
            pass
        _checkJob = None
    _dirtyQueue = []


def create(objects=None):
    global _colorIndex, _trackers, _cache
    if not _loadPlugin():
        return
    if objects is None:
        objects = cmds.ls(sl=True, long=True)
    if not objects:
        cmds.warning("Tracify: Select at least one object")
        return
    _colorIndex = 0
    cmds.waitCursor(state=True)
    try:
        if not cmds.objExists(GROUP_NAME):
            cmds.createNode("transform", name=GROUP_NAME, skipSelect=True)
            cmds.setAttr(GROUP_NAME + ".useOutlinerColor", True)
            cmds.setAttr(GROUP_NAME + ".outlinerColor", 1.0, 0.4, 0.7)
            cmds.setAttr(GROUP_NAME + ".hiddenInOutliner", True)
            for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
                cmds.setAttr(GROUP_NAME + "." + attr, lock=True, keyable=False, channelBox=False)
        for obj in objects:
            trackerGrp = _createTrackerGrp(obj)
            shortName = obj.split("|")[-1].replace(":", "_")
            nodeName = "tracify_" + shortName
            if cmds.objExists(nodeName):
                cmds.delete(nodeName)
            node = cmds.createNode("tracifyNode", name=nodeName, parent=GROUP_NAME, skipSelect=True)
            cmds.setAttr(node + ".useOutlinerColor", True)
            cmds.setAttr(node + ".outlinerColor", 1.0, 0.4, 0.7)
            cmds.connectAttr("time1.outTime", node + ".timeInput", force=True)
            cmds.connectAttr(trackerGrp + ".worldMatrix[0]", node + ".sourceWorldMatrix", force=True)
            color = _getNextColor()
            cmds.setAttr(node + ".frameRange", FRAME_RANGE)
            cmds.setAttr(node + ".pointSize", POINT_SIZE)
            cmds.setAttr(node + ".lineWidth", LINE_WIDTH)
            cmds.setAttr(node + ".lineColorR", color[0])
            cmds.setAttr(node + ".lineColorG", color[1])
            cmds.setAttr(node + ".lineColorB", color[2])
            cmds.setAttr(node + ".keyColorR", KEY_COLOR[0])
            cmds.setAttr(node + ".keyColorG", KEY_COLOR[1])
            cmds.setAttr(node + ".keyColorB", KEY_COLOR[2])
            _trackers[nodeName] = trackerGrp
        _setupJobs()
        for panel in cmds.getPanel(type="modelPanel") or []:
            try:
                cmds.modelEditor(panel, edit=True, locators=True)
            except:
                pass
        cmds.select(objects)
        _initTrackers()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        cmds.waitCursor(state=False)


def _initTrackers():
    for trackerGrp in _trackers.values():
        if cmds.objExists(trackerGrp):
            cmds.setAttr(trackerGrp + ".tx", 1)
            cmds.setAttr(trackerGrp + ".tx", 0)
    for nodeName, trackerGrp in list(_trackers.items()):
        if cmds.objExists(nodeName) and cmds.objExists(trackerGrp):
            _buildFullCache(nodeName, trackerGrp)
    cmds.refresh()


def clear():
    global _trackers, _cache
    cmds.waitCursor(state=True)
    try:
        _clearJobs()
        _trackers = {}
        _cache = {}
        for grp in cmds.ls("tracify_grp_*", type="transform") or []:
            if cmds.objExists(grp):
                try:
                    cmds.delete(grp)
                except:
                    pass
        if cmds.objExists(GROUP_NAME):
            cmds.delete(GROUP_NAME)
        if _isPluginLoaded():
            for node in cmds.ls(type="tracifyNode") or []:
                if cmds.objExists(node):
                    cmds.delete(node)
        cmds.refresh()
    finally:
        cmds.waitCursor(state=False)


def toggle(objects=None):
    cmds.undoInfo(openChunk=True, chunkName="Tracify")
    try:
        if cmds.objExists(GROUP_NAME) or (cmds.ls(type="tracifyNode") if _isPluginLoaded() else False):
            clear()
        else:
            create(objects)
    finally:
        cmds.undoInfo(closeChunk=True)


def refresh():
    global _trackers, _cache
    if not _isPluginLoaded():
        return
    _trackers = {}
    _cache = {}
    for nodeName in cmds.ls(type="tracifyNode") or []:
        if not cmds.objExists(nodeName):
            continue
        conns = cmds.listConnections(nodeName + ".sourceWorldMatrix", source=True, destination=False) or []
        if conns:
            trackerGrp = cmds.ls(conns[0], long=True)
            if trackerGrp and cmds.objExists(trackerGrp[0]):
                _trackers[nodeName] = trackerGrp[0]
                _buildFullCache(nodeName, trackerGrp[0])
    if _trackers:
        if not _jobs:
            _setupJobs()
        else:
            _setupAttrJobs()
    cmds.refresh()


def reinit():
    refresh()


def setRange(value):
    global FRAME_RANGE
    FRAME_RANGE = value
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".frameRange", value)
    cmds.refresh()


def setPointSize(value):
    global POINT_SIZE
    POINT_SIZE = value
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".pointSize", value)
    cmds.refresh()


def setLineWidth(value):
    global LINE_WIDTH
    LINE_WIDTH = value
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".lineWidth", value)
    cmds.refresh()


def setColorMode(mode):
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".colorMode", mode)
    cmds.refresh()


def setRainbowMode(enabled):
    setColorMode(1 if enabled else 0)


r = refresh
t = toggle