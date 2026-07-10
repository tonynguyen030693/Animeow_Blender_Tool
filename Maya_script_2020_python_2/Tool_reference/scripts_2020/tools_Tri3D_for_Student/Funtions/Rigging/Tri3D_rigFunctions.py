import pymel.core as pm
import maya.cmds as cmds
import os
ctrlColor = 'ctrlColor'
########################################################################
########################################################################

################################################################

 
def createJoint(*arg):
    selected_obj = cmds.ls(sl=True)
    for obj in selected_obj:
        pivot_position = cmds.xform(selected_obj, ws=True, query=True, rotatePivot=True)

        Joint = cmds.joint(name= obj + "_jnt")
        cmds.xform(Joint, ws=True, translation=pivot_position)
        cmds.setParent(Joint, obj)


def scalePoCurve(*arg):
    selected_curve = pm.selected()[0]
    pivot_point = selected_curve.getPivots(worldSpace=True)[0]
    scale_factor = 1.3  
    for cv in selected_curve.cv:
        vertex_position = pm.xform(cv, query=True, translation=True, worldSpace=True)
        scaled_position = [
            pivot_point[0] + (vertex_position[0] - pivot_point[0]) * scale_factor,
            pivot_point[1] + (vertex_position[1] - pivot_point[1]) * scale_factor,
            pivot_point[2] + (vertex_position[2] - pivot_point[2]) * scale_factor,
        ]
        pm.xform(cv, translation=scaled_position, worldSpace=True)
def scaleNeCurve(*arg):
    selected_curve = pm.selected()[0]
    pivot_point = selected_curve.getPivots(worldSpace=True)[0]
    scale_factor = -1.3  
    for obj in selected_curve.cv:
        vertex_position = pm.xform(obj, query=True, translation=True, worldSpace=True)
        scaled_position = [
            pivot_point[0] + (vertex_position[0] - pivot_point[0]) / scale_factor,
            pivot_point[1] + (vertex_position[1] - pivot_point[1]) / scale_factor,
            pivot_point[2] + (vertex_position[2] - pivot_point[2]) / scale_factor,
        ]
        pm.xform(obj, translation=scaled_position, worldSpace=True)


################################################################ set color
def setColor():
    selColor = cmds.colorIndexSliderGrp(ctrlColor, query = 1, value = 1)
    selCtrl = cmds.ls(selection = 1)
    for ctrl in selCtrl:
        cmds.setAttr(ctrl + ".overrideEnabled", 1)
        cmds.setAttr(ctrl + ".overrideColor", (selColor - 1))  

def hideManipulator():
    selPanel = cmds.getPanel(withFocus = 1)
    cmds. modelEditor(selPanel, edit = 1,  selectionHiliteDisplay = 0, manipulators = 0)
    setColor() 

def showManipulator():
    selPanel = cmds.getPanel(withFocus = 1)
    cmds.modelEditor(selPanel, edit = 1,  selectionHiliteDisplay = 1, manipulators = 1)         
