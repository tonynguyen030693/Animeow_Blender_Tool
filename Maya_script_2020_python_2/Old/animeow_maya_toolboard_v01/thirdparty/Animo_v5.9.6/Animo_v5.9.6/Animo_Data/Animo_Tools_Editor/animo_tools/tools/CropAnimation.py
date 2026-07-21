import maya.cmds as cmds
import maya.mel as mel

def crop_animation():
    try:
        playBackSlider = mel.eval('$tmp=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, q=True, rangeArray=True)
    except:
        timeRange = None
    
    if timeRange is None:
        return
        
    startRange = int(timeRange[0])
    endRange = int(timeRange[1]) - 1
    
    if endRange - startRange > 0:
        ct = cmds.currentTime(q=True)
        
        cmds.waitCursor(state=True)
        cmds.evaluationManager(mode="off")
        cmds.refresh(suspend=True)
        
        try:
            cmds.selectKey(clear=True)
        except:
            pass
        
        cmds.currentTime(startRange)
        cmds.setKeyframe(insert=True)
        cmds.currentTime(endRange)
        cmds.setKeyframe(insert=True)
        
        cmds.cutKey(time=(-999999, startRange-1))
        cmds.cutKey(time=(endRange+1, 999999))
        
        cmds.currentTime(ct)
        
        cmds.waitCursor(state=False)
        cmds.evaluationManager(mode="parallel")
        cmds.refresh(suspend=False)

crop_animation()
