import maya.cmds as cmds
import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
import os
################################################################ import os
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'Icons')

import tools_Tri3D_for_Student.Funtions.Animation.Tri3D_animationFuntions as Funcanim
import tools_Tri3D_for_Student.Funtions.Tri3D_functions as func
import tools_Tri3D_for_Student.Funtions.Rigging.Tri3D_rigFunctions as Rig

############################################################################################### UI
def wdMK(*arg):                                                                                                                          
    if cmds.window("windowMK", exists=True):
        cmds.deleteUI("windowMK")
    windowMK = cmds.window("windowMK", title="moveKey pro", sizeable=False, resizeToFitChildren=True, w=300)
    cmds.windowPref("windowMK", remove=True) 

    cmds.columnLayout("MK", w=300, adj= 1)
    cmds.setParent("MK")
    cmds.rowColumnLayout("Move_Pro", w=300, nc=4)
    cmds.button(l= 'Select', c= Funcanim.selectCtrl, w=50)
    cmds.textField('selectCtrl', w= 250, ed= 0, placeholderText="Select_Controller")
    cmds.button(l= 'Select', c= Funcanim.selectAll, w=50)
    cmds.textField('selectAll', w= 100, ed= 0, placeholderText="Select_Ctrl")

    cmds.setParent("MK")
    cmds.checkBox('UseSEK', l= 'On_Start_End', v= 0, cc= Funcanim.useSEK)
    cmds.rowColumnLayout("Button2", w=300, nc=4)
    cmds.button(l= 'Start Key', c= Funcanim.butt_startKey, w=50)
    cmds.textField('startKey', w= 100, ed= 0, tx= '')
    cmds.button(l= 'End Key', c= Funcanim.butt_endKey, w=50)
    cmds.textField('endKey', w= 100, ed= 0, tx= '')

    cmds.setParent("MK")
    cmds.intSliderGrp('numbersKey', f= 1, min= 1, v= 1, max= 999999)

    cmds.setParent("MK")
    cmds.rowColumnLayout("button select", w=300, nc=2)
    cmds.button('moveBackward', l= '<<< Move Back', c= Funcanim.butt_moveBackward, w=150)
    cmds.button('moveForward', l= 'Move Go >>>', c= Funcanim.butt_moveForward, w=150)    
    cmds.showWindow(windowMK)