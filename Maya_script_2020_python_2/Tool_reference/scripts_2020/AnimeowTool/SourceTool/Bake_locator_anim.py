import maya.cmds as cmds
import maya.mel as mel
from functools import wraps


# -----------------------------------------------------------------------------
# Decorators
# -----------------------------------------------------------------------------
def viewportOff( func ):
    """
    Decorator - turn off Maya display while func is running.
    if func will fail, the error will be raised after.
    """
    @wraps(func)
    def wrap( *args, **kwargs ):


        # Turn $gMainPane Off:
        mel.eval("paneLayout -e -manage false $gMainPane")


        # Decorator will try/except running the function.
        # But it will always turn on the viewport at the end.
        # In case the function failed, it will prevent leaving maya viewport off.
        try:
            return func( *args, **kwargs )
        except Exception:
            cmds.warning('Done!')#raise # will raise original error
        finally:
            mel.eval("paneLayout -e -manage true $gMainPane")


    return wrap


#returns a list with the NOT selected attributes in the channel box
def selectedAttrs():
    gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
    selChannels = cmds.channelBox(gChannelBoxName, query=True, sma=True)


    trans = []
    rot = []
    scale = []


    if(selChannels!=None):
        trans = ["tx","ty","tz"]
        rot = ["rx","ry","rz"]
        scale = ["sx","sy","sz"]
        for i in range(len(selChannels)):
            if(selChannels[i] in trans):
                trans.remove(selChannels[i])
            elif(selChannels[i] in rot):
                rot.remove(selChannels[i])
            elif(selChannels[i] in scale):
                scale.remove(selChannels[i])


        trans = [s.replace('t', '') for s in trans]
        rot = [s.replace('r', '') for s in rot]
        scale = [s.replace('s', '') for s in scale]


    return (trans, rot, scale)


#returns the highlighted frame range in the time slider
def frameRange():
    aPlayBackSliderPython = maya.mel.eval('$tmpVar=$gPlayBackSlider')
    highlightRange = cmds.timeControl(aPlayBackSliderPython, query=True, rangeArray=True)


    if((highlightRange[1]-highlightRange[0])>1):
        minTime = highlightRange[0]
        maxTime = highlightRange[1]
    else:
        minTime = cmds.playbackOptions(minTime=True, query=True)
        maxTime = cmds.playbackOptions(maxTime=True, query=True)
    return(minTime, maxTime)


@viewportOff
def createLocatorAtSelectionAndBakeAnim(*args):
    framesSelected = frameRange()
    channels = selectedAttrs()


    sel = cmds.ls(selection = True)
    sel_verts = cmds.filterExpand(sm=31)
    locList = []
    constList = []
    suffix = '_LOC' # or '_LOC#' if we want to add a number at the end in the firt locator too.


    if (len(sel) == 0):
        loc = cmds.spaceLocator()
    elif (sel_verts != None):
        locName = sel_verts[0].split('.')[0] + suffix
        bb = cmds.exactWorldBoundingBox(sel_verts)
        pos = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
        newLoc = cmds.spaceLocator(name=locName)
        cmds.move(pos[0], pos[1], pos[2], newLoc)
    else:
        for i in range(len(sel)):
            locName = sel[i] + suffix
            loc = cmds.spaceLocator(name= locName)
            locList.append(loc)


            #No attributes selected on the channel box
            if(channels==None):
                tempConst = cmds.parentConstraint(sel[i], loc, mo=False)
                tempScaleConst = cmds.scaleConstraint(sel[i], loc, mo=False)
            #Some attributes selected on the channel box
            else:
                print('attrs selected!')
                tempConst = cmds.parentConstraint(sel[i], loc, st=channels[0], sr=channels[1], mo=False)
                tempScaleConst = cmds.scaleConstraint(sel[i], loc, sk=channels[2], mo=False)
            constList.append(tempConst)
            constList.append(tempScaleConst)


    cmds.select(clear=True)
    for i in range(len(locList)):
        cmds.select(locList[i],add=True)
    locators = cmds.ls(selection=True)
    cmds.bakeResults(locators, t=(framesSelected[0],framesSelected[1]), bol=False, preserveOutsideKeys = True, simulation=True)
    cmds.select(clear=True)
    for i in range(len(constList)):
        cmds.delete(constList[i])


    #create an error
    #raise RuntimeError("raise an error in line 48")


# createLocatorAtSelectionAndBakeAnim()