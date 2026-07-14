# -*- coding: utf-8 -*-
"""
ANM Hider - Character part visibility manager for Maya.
Re-written in PySide2 (Qt) for high-end modern flat UI/UX.
Integrated into Animeow Toolboard v02.
Original logic by Francisco Cerchiara Montero.
"""

import os
import time
import sys
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

# Version
versionHider = 'ANM_Hider Beta 1.0'

# Global variables
namespaceHider = ''
namespaceHiderForWindow = ''
All_Sets_Hider = ''
Head_Hider = ''
Torso_Hider = ''
Arm_R_Hider = ''
Arm_L_Hider = ''
Leg_R_Hider = ''
Leg_L_Hider = ''
Extra_One_Hider = ''
Extra_Two_Hider = ''
Extra_Three_Hider = ''
ANM_Hider_Settings = ''

allSet = []
polys = []
shapes = []
transformAndShapeSet = []
setHider = ''
shapeMode = 'Off'
choise = ''
setHiderParent = []
setHiderChild = ''
R_Variable = ''
L_Variable = ''

# Annotations for popUp help:
allSets_Ann = 'Left Click:\n - Switch between Show and Hide all sets\n\nRight click:\n- Empty Sets Body\n- Empty Sets Extras\n- Select All Sets'
blueButtons_Ann = 'Left Click:\n - Switch between Show and Hide set\n\nRight click:\n- Add Selection (Transform)\n- Add Selection Shape\n- Remove Selection\n- Select Set\n- Remove Set'
grow_Ann = 'Grow selection'
shrink_Ann = 'Shrink selection'
switchPolyOrNurbsCurves_Ann = 'Left Click:\n- Switch between Poly selection and NurbsCurves\nRight Click:\n- Change poly color selection'

# Output strings
setsExportSucces = 'Sets exported successfully!'
setsLoadSucces = 'Sets loaded successfully!'
setHided = 'Set hidden'
setVisible = 'Set Visible'
allVisMeshSelectable = 'All visible meshes are selectable, and all layerDisplay are unlocked'
allBodySetsRemoved = 'All Body sets removed' 
allExtraSetsRemoved = 'All Extra sets removed'
keepYourSecrets = 'Alright then, keep your secrets' 
allRemoved = 'Everything related to ANM_Hider Removed'
selRemoved = 'Selection removed'

# Warnings
allFacesAreVisible = 'All faces are visible'
hiderSystemWarning = 'There is more than one Hider system, select the character you want to run'
confirmCheckAllSets = 'This may take a while, do you want to check them?'
nothingSel = 'Nothing selected' 
setDontExists = 'Set doesn\'t exist'
nothingSelected = 'Nothing selected'
setDoesntExists = "Set doesn't exist"

# Error
errorLoadSets = 'Error trying to load the set' 
errorExportSets = 'You can only save sets created in the scene'
removeAllConfirm = 'Are you sure you want to delete everything related to the script?'

# ── Helper to resolve icon paths ──
def get_icon_path(icon_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.abspath(os.path.join(current_dir, "..", "icons", "Icons_Hider", icon_name)).replace("\\", "/")
    return icon_path

def get_maya_main_window():
    import maya.OpenMayaUI as mui
    ptr = mui.MQtUtil.mainWindow()
    if ptr:
        return wrapInstance(int(ptr), QtWidgets.QMainWindow)
    return None

# ── Logic methods (Kept module-level for backward compatibility and clean logic) ──

def setup_icons_path():
    """Add package icons directory to Maya's XBMLANGPATH"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_icons_dir = os.path.join(current_dir, "..", "icons")
    package_icons_dir = os.path.abspath(package_icons_dir).replace("\\", "/")
    
    xbm_path = os.environ.get("XBMLANGPATH", "")
    paths = xbm_path.split(";")
    if package_icons_dir not in paths:
        os.environ["XBMLANGPATH"] = package_icons_dir + ";" + xbm_path

def declaringSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, ANM_Hider_Settings
    All_Sets_Hider = ( namespaceHider + 'All_Sets_ANM_Hider' )
    Head_Hider = ( namespaceHider + 'Head_ANM_Hider' )
    Torso_Hider = ( namespaceHider + 'Torso_ANM_Hider' )
    Arm_R_Hider = ( namespaceHider + 'Arm_R_ANM_Hider' )
    Arm_L_Hider = ( namespaceHider + 'Arm_L_ANM_Hider' )
    Leg_R_Hider = ( namespaceHider + 'Leg_R_ANM_Hider' )
    Leg_L_Hider = ( namespaceHider + 'Leg_L_ANM_Hider' )
    Extra_One_Hider = ( namespaceHider + 'Extra_One_ANM_Hider' )
    Extra_Two_Hider = ( namespaceHider + 'Extra_Two_ANM_Hider' )
    Extra_Three_Hider = ( namespaceHider + 'Extra_Three_ANM_Hider' )
    ANM_Hider_Settings = ( namespaceHider + 'ANM_Hider_Settings' )

def createAllSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, ANM_Hider_Settings
    if cmds.objExists('All_Sets_ANM_Hider') == 0: cmds.sets(n='All_Sets_ANM_Hider', em=True)
    if cmds.objExists(Head_Hider) == 0: cmds.sets(n=Head_Hider, em=True)
    if cmds.objExists(Torso_Hider) == 0: cmds.sets(n=Torso_Hider, em=True)
    if cmds.objExists(Arm_R_Hider) == 0: cmds.sets(n=Arm_R_Hider, em=True)
    if cmds.objExists(Arm_L_Hider) == 0: cmds.sets(n=Arm_L_Hider, em=True)
    if cmds.objExists(Leg_R_Hider) == 0: cmds.sets(n=Leg_R_Hider, em=True)
    if cmds.objExists(Leg_L_Hider) == 0: cmds.sets(n=Leg_L_Hider, em=True)
    if cmds.objExists(Extra_One_Hider) == 0: cmds.sets(n=Extra_One_Hider, em=True)
    if cmds.objExists(Extra_Two_Hider) == 0: cmds.sets(n=Extra_Two_Hider, em=True)
    if cmds.objExists(Extra_Three_Hider) == 0: cmds.sets(n=Extra_Three_Hider, em=True)
    cmds.sets (Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider,
    Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, edit=True, fe='All_Sets_ANM_Hider' )

def createSettingsHider():
    if cmds.objExists ('ANM_Hider_Settings') == 0:
        selCurrent = cmds.ls (sl=True)
        cmds.group (em=True, n= 'ANM_Hider_Settings')
        for attr in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz", ".v"]:
            cmds.setAttr (attr, lock=True, keyable=False, channelBox=False )
        # States Attributes
        cmds.addAttr ('ANM_Hider_Settings', ln='All_Sets_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Head_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Torso_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Arm_R_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Arm_L_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Leg_L_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Leg_R_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_One_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_Two_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_Three_Hider_State', at='bool', dv=True, keyable=True)
        # Edit Mode State
        cmds.addAttr ('ANM_Hider_Settings', ln='Edit_Mode_State', at='bool', dv=True, keyable=True)
        cmds.select(selCurrent)

def createHiderInTheScene():
    global namespaceHider, namespaceHiderForWindow
    namespaceHider = ''    
    namespaceHiderForWindow = 'Created in the scene'
    declaringSets()
    createSettingsHider()
    createAllSets()

def declaringNameSpaces():
    global namespaceHider, namespaceHiderForWindow
    currentSel = cmds.ls(sl=True)
    if cmds.objExists('*:ANM_Hider_Settings'):
        cmds.select('*:ANM_Hider_Settings')
        try:
            cmds.select('ANM_Hider_Settings', tgl=True)
        except:
            pass    
        settings = cmds.ls(sl=True)
        if len(settings) >= 1:
            try:
                try:
                    namespaceHiderForWindow = cmds.referenceQuery(currentSel[0], namespace=True, shortName=True)
                    namespaceHider = namespaceHiderForWindow + ":" 
                    declaringSets()
                except:
                    createHiderInTheScene()
            except:
                cmds.warning(hiderSystemWarning)
    else:
        createHiderInTheScene()
    cmds.select(currentSel)

def queryAllSet():
    global allSet, polys, shapes, transformAndShapeSet
    allSet = cmds.sets(setHider, q=True)
    transformAndShapeSet = cmds.ls(allSet, type=['transform','shape'])
    polys = cmds.filterExpand(allSet, sm=34) or []
    try:
        shapes = []
        for poly in polys:
            shape = cmds.listRelatives(poly, s=True, p=True, fullPath=True)
            if shape:
                shapes.append(shape)
        def getUniqueItems(iterable):
            result = []
            for item in iterable:
                if item not in result:
                    result.append(item)
            return result
        shapes = getUniqueItems(shapes)
    except:
        pass

def addSelectionToSet():
    global setHider
    try:
        sel = cmds.ls(sl=True, l=True)
        if len(sel) > 0:
            if cmds.objExists(setHider):
                removeNameSpace()
                if shapeMode == 'On':
                    addNameSpace()
                    shapesCtrl = cmds.listRelatives(sel, s=True, fullPath=True) or []
                    polys_found = cmds.filterExpand(sel, sm=34, fullPath=True) or []
                    if shapesCtrl:
                        cmds.sets (shapesCtrl, edit=True, forceElement=setHider)
                    if polys_found:
                        cmds.sets (polys_found, edit=True, forceElement=setHider)
                if shapeMode == 'Off':
                    addNameSpace()
                    cmds.sets (sel, edit=True, forceElement=setHider)
                queryAllSet()
                hideSet()
                for shape in shapes:
                    cmds.polyOptions (shape, displayInvisibleFaces=1)
                cmds.select(cl=True)
        else:
            cmds.warning(nothingSelected)
    except Exception as e:
        print(f"Error in addSelectionToSet: {e}")
        createSettingsHider()

def hidePolys():
    global setHider, lastPolys, lastPoly
    queryAllSet()
    try:
        cmds.hide(polys)
    except:
        lastPolys = []
        for shape in shapes:
            desgote = cmds.filterExpand(shape[0] +'.f[*]', sm=34, fullPath=True) or []
            if desgote:
                cmds.select(desgote[-1])
                sel = cmds.ls(sl=True)
                lastPolys.append(sel)
        for lastPoly in lastPolys:
            cmds.showHidden(lastPoly)
            for poly in list(polys):
                if poly == lastPoly[0]:
                    polys.remove(poly)        
        cmds.hide(polys)
        for lastPoly in lastPolys:
            cmds.polyHole(lastPoly[0], assignHole = 1)
        for shape in shapes:
            cmds.select(shape)

def showPolys():
    global setHider
    try:
        removeNameSpace()
        if cmds.getAttr(ANM_Hider_Settings + '.' + setHider + '_State') == 0:
            addNameSpace() 
            try:
                cmds.showHidden(polys)
                lastPolys = []
                queryAllSet()
                for shape in shapes:
                    desgote = cmds.filterExpand(shape[0] +'.f[*]', sm=34, fullPath=True) or []
                    if desgote:
                        cmds.select(desgote[-1])
                        sel = cmds.ls(sl=True)
                        lastPolys.append(sel)
                for lastPoly in lastPolys:
                    for poly in list(polys):
                        if poly == lastPoly[0]:
                            polys.remove(poly)
                for lastPoly in lastPolys:
                    cmds.polyHole(lastPoly[0], assignHole = 0)
            except Exception as e:
                print(f"Error in showPolys: {e}")
    except:
        pass

def hideSet():
    global setHider, namespaceHider
    if cmds.objExists(setHider):
        try:
            value = 0  
            currentSel = cmds.ls(sl=True)
            queryAllSet()
            for item in transformAndShapeSet:
                try:
                    cmds.setAttr(item + '.visibility', value)
                except:
                    try:
                        cmds.setAttr(item + '.lodVisibility', value)
                    except:
                        pass
            hidePolys()
            cmds.select (currentSel)
            print (setHided),
        except Exception as e:
            print(f"Error in hideSet: {e}")
            createSettingsHider()
    else:
        cmds.warning("set doesn't exist")
    removeNameSpace()
    cmds.setAttr( ANM_Hider_Settings + '.' + (setHider + '_State'), 0)

def showSet():
    global setHider, namespaceHider
    if cmds.objExists(setHider):
        value = 1  
        currentSel = cmds.ls(sl=True)
        queryAllSet()
        for item in transformAndShapeSet:
            try:
                cmds.setAttr(item + '.visibility', value)
            except:
                try:
                    cmds.setAttr(item + '.lodVisibility', value)
                except:
                    pass
        showPolys()
        cmds.select (currentSel)
        print (setVisible),
    else:
        cmds.warning(setDoesntExists)
    removeNameSpace()
    cmds.setAttr( ANM_Hider_Settings + '.' + (setHider + '_State'), 1)

def showOrHideButton():
    global setHider
    try:
        contentSet = cmds.sets(setHider, q=True)
        if str(contentSet) == 'None':
            cmds.warning('Set empty')
        else:
            removeNameSpace()
            if cmds.getAttr( ANM_Hider_Settings + '.' + (setHider + '_State') ):
                addNameSpace()
                hideSet()
            else:
                addNameSpace()
                showSet()
    except Exception as e:
        print(f"Error in showOrHideButton: {e}")
        createSettingsHider()

def ShowOrHideAllSetsButton():   
    global choise    
    if cmds.getAttr(ANM_Hider_Settings + '.All_Sets_Hider_State'):
        choise = 'hide'; ShowOrHideAllSets()
    else:
        choise = 'show'; ShowOrHideAllSets()

def ShowOrHideAllSets():
    global setHider
    sets_In_AllSetsHider = cmds.sets(All_Sets_Hider, q=True) or []
    result = []    
    for s_name in sets_In_AllSetsHider:
        contentSet = cmds.sets(s_name, q=True)
        result.append(contentSet)
    if result == [None, None, None, None, None, None, None, None, None]:
        cmds.warning('Set empty')
    else:
        for s_name in sets_In_AllSetsHider:
            setHider = s_name
            if choise == 'show':
                showSet()
                cmds.setAttr( ANM_Hider_Settings + '.All_Sets_Hider_State', 1)
            if choise == 'hide':
                hideSet()
                cmds.setAttr( ANM_Hider_Settings + '.All_Sets_Hider_State', 0)

def selectSet():
    if cmds.objExists(setHider):
        cmds.select(setHider)
    else:
        cmds.warning("set doesn't exist")

def showAllHiddenFaces():
    if cmds.objExists('defaultHideFaceDataSet'):
        cmds.showHidden('defaultHideFaceDataSet')
        print(allFacesAreVisible),
    else:
        cmds.warning('No faces hidden')

def unlockAllVismeshes():
    shapesAndShapesOrig = cmds.ls (v=True, type='mesh') or []
    meshes = cmds.filterExpand(shapesAndShapesOrig, sm=12) or []
    groups = cmds.ls(type='transform') or []
    groupsAndMeshes = groups + meshes
    try:
        for item in groupsAndMeshes:
            if cmds.getAttr (item + '.overrideDisplayType') == 2:
                cmds.setAttr (item + '.overrideDisplayType', 0)
    except:
        pass
    try:
        displayLayers = cmds.ls(type='displayLayer', l=True) or []
        for ld in displayLayers:
            cmds.setAttr(ld + '.displayType', 0)     
    except:
        pass
    print (allVisMeshSelectable),

def unlockAllVisible():
    currentSel = cmds.ls(sl=True)
    transform = cmds.ls(type='transform', v=True) or []
    mesh = cmds.ls(type='mesh', v=True) or []
    annotationShapes = cmds.ls(type='annotationShape') or []
    visNurbsShapes = cmds.ls(type='nurbsCurve', v=True) or []
    visNurbsTransform = cmds.ls(cmds.pickWalk (visNurbsShapes, d='up') ) or []
    nodes = annotationShapes + visNurbsTransform + visNurbsShapes + transform + mesh
    for item in nodes:
        try:
            cmds.setAttr(item + '.overrideDisplayType', 0)
            cmds.setAttr(item + '.template', 0)
        except:
            pass
    try:
        displayLayers = cmds.ls(type='displayLayer', l=True) or []
        for ld in displayLayers:
            cmds.setAttr(ld + '.displayType', 0)     
    except:
        pass
    cmds.select(currentSel)
    print ('All selectable'),

def lockSelection():  
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        selShape = cmds.ls(cmds.pickWalk (sel, d='down') ) or []
        nodes = sel + selShape 
        for item in nodes:
            try:
                cmds.setAttr(item + '.overrideDisplayType', 1)
            except:
                pass
        print ('Selection Locked'),
    else:
        cmds.warning(nothingSelected)

def removeAllBodySets():
    global setHider
    currentSel = cmds.ls(sl=True)
    if cmds.objExists(Head_Hider): setHider = Head_Hider; removeSet()
    if cmds.objExists(Torso_Hider): setHider = Torso_Hider; removeSet()
    if cmds.objExists(Arm_R_Hider): setHider = Arm_R_Hider; removeSet()
    if cmds.objExists(Arm_L_Hider): setHider = Arm_L_Hider; removeSet()
    if cmds.objExists(Leg_R_Hider): setHider = Leg_R_Hider; removeSet()
    if cmds.objExists(Leg_L_Hider): setHider = Leg_L_Hider; removeSet()
    cmds.select(currentSel)
    print(allBodySetsRemoved), 

def removeAllExtraSets():
    global setHider
    currentSel = cmds.ls(sl=True)
    if cmds.objExists(Extra_One_Hider): setHider = Extra_One_Hider; removeSet()
    if cmds.objExists(Extra_Two_Hider): setHider = Extra_Two_Hider; removeSet()
    if cmds.objExists(Extra_Three_Hider): setHider = Extra_Three_Hider; removeSet()
    cmds.select(currentSel)
    print(allExtraSetsRemoved), 

def removeSet():
    global setHider
    showSet()
    allSet_q = cmds.sets(setHider, q=True) or []
    if allSet_q:
        cmds.sets(allSet_q, edit=True, rm=setHider)

def removeSelection():
    global setHider
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        if cmds.objExists(setHider):
            value = 1
            transformSel = cmds.ls(sl=True, type='transform') or []
            polysSel = cmds.filterExpand(sel, sm=34, fullPath=True) or []
            shapesSel = cmds.listRelatives(sel, s=True) or []
            if shapesSel:
                cmds.sets (shapesSel, edit=True, rm=setHider)
            cmds.sets (sel, edit=True, rm=setHider)
            try:
                for item in shapesSel:
                    try:
                        cmds.setAttr(item + '.visibility', value)
                    except:
                        cmds.setAttr(item + '.lodVisibility', value)
            except:
                pass
            for item in transformSel:
                try:
                    cmds.setAttr(item + '.visibility', value)
                except:
                    cmds.setAttr(item + '.lodVisibility', value)
            if value == 1:
                value = 0
            if polysSel:
                cmds.showHidden(polysSel)
            try:
                for poly in polysSel:
                    cmds.polyHole (poly, assignHole = value)
            except:
                pass
            print(selRemoved), 
        else:
            cmds.warning(setDontExists) 
    else:
        cmds.warning(nothingSel)

def removeNameSpace():
    global setHider, namespaceHider
    if len(namespaceHider) > 0:
        numberNS = len(namespaceHider)
        setHider = setHider[numberNS:]

def addNameSpace():
    global setHider, namespaceHider
    if len(namespaceHider) > 0:
        setHider = namespaceHider+setHider

def saveSetsHider():
    if namespaceHiderForWindow == 'Created in the scene':
        createAllSets()
        allSets = [Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider,
                   Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider]    
        SourceFile = cmds.fileDialog2(startingDirectory ="/usr/u/bozo/myFiles/", fileFilter="Python File(*.py)")
        if SourceFile:
            SourceFile = ''.join([str(elem) for elem in SourceFile]) 
            fileHandle = open((SourceFile), 'w')
            fileHandle.write("## Remove existent sets\nimport animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeAllBodySets()\nfh.removeAllExtraSets()\n")
            fileHandle.write("## Create all sets\nimport animeow_maya_toolboard_v02.core.anm_hider as fh; fh.createAllSets()\n## Select each set content and create set\n")
            for s_name in allSets:       
                setContent = cmds.sets(s_name, q=True)
                if str(setContent) == 'None' or not setContent:
                    pass
                else:
                    fileHandle.write('cmds.select(')
                    for item in setContent:
                        fileHandle.write('"'+ item+'",')
                    fileHandle.write(')'+'\n')
                    fileHandle.write('cmds.sets( edit=True, fe=fh.' + s_name + ')\n')
            fileHandle.write("## Select clear\n" + "cmds.select(cl=True)\n")
            fileHandle.write("## Check all icons\nimport animeow_maya_toolboard_v02.core.anm_hider as fh; fh.checkAllIconSets()")
            fileHandle.close()
            print(setsExportSucces), 
    else:
        cmds.confirmDialog( title='ANM Hider Warning', message=errorExportSets, button='Ok')

def LoadSetsHider():
    try:
        SourceFile = cmds.fileDialog(m=0)
        if SourceFile:
            with open(SourceFile, 'r') as filehandle:
                filecontent = filehandle.read()
            exec(filecontent)
            print(setsLoadSucces), 
    except Exception as e:
        cmds.error(f"{errorLoadSets}: {e}")

def objectModeHider():
    cmds.selectMode(object=True)
    mel.eval('selectMode -object; selectType -handle 1 -ikHandle 1 -joint 1 -nurbsCurve 1 -cos 1 -stroke 1 -nurbsSurface 1 -polymesh 1 -subdiv 1 -plane 1 -lattice 1 -cluster 1 -sculpt 1 -nonlinear 1 -particleShape 1 -emitter 1 -field 1 -spring 1 -rigidBody 1 -fluid 1 -hairSystem 1 -follicle 1 -nCloth 1 -nRigid 1 -dynamicConstraint 1 -rigidConstraint 1 -collisionModel 1 -light 1 -camera 1 -texture 1 -ikEndEffector 1 -locator 1 -dimension 1;selectType -byName gpuCache 1;')
    mel.eval('selectMode -component; selectType -cv 1 -vertex 1 -subdivMeshPoint 1 -latticePoint 1 -particle 1 -editPoint 0 -curveParameterPoint 0 -surfaceParameterPoint 0 -puv 0 -polymeshEdge 0 -subdivMeshEdge 0 -isoparm 0 -surfaceEdge 0 -surfaceFace 1 -springComponent 0 -facet 0 -subdivMeshFace 1 -hull 0 -rotatePivot 0 -scalePivot 0 -jointPivot 0 -selectHandle 0 -localRotationAxis 0 -imagePlane 0;')
    mel.eval('changeSelectMode -object')

def switchPolyOrNurbsSel(is_faces_mode):
    if not is_faces_mode:
        objectModeHider()
        cmds.selectType(cv=True)
        mel.eval('setObjectPickMask "All" 0;setObjectPickMask "Curve" true')
    else:
        mel.eval('changeSelectMode -component')
        mel.eval('setComponentPickMask "Facet" true; ')
        cmds.selectType(cv=False)

def growSelection():
    cmds.select(cmds.listConnections (t='transform') or [])

def filterOnlyCurves():
    sel = cmds.ls(sl=True)
    onlyCurves = cmds.filterExpand(sel, sm=9, fullPath=True) or []
    cmds.select(onlyCurves)
    print('You have selected: ' + str(onlyCurves)),

def printSelected():
    sel = cmds.ls(sl=True)
    print(str(len(sel))),

def SelectTemplateLineWindow():
    if cmds.window("Select_Template_Line", exists=True):
        cmds.deleteUI("Select_Template_Line")
    selectTemplateLine = cmds.window("Select_Template_Line", title="Select Template Line", s=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(l='Usage: First select pole vector Ctrl\nThen grow selection, Filter and add it to a Set', h=30, fn='boldLabelFont')
    cmds.separator()
    cmds.button(l='1- Grow selection', c='import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.growSelection()')
    cmds.separator()
    cmds.button(l='2- Filter Only Curves', c='import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.filterOnlyCurves()')
    cmds.separator()
    cmds.button(l='3- Print number selected', c='import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.printSelected()')
    cmds.showWindow( selectTemplateLine )
    cmds.window('Select_Template_Line', edit=True, w=300, h=110)

def mirrorCtrlsHider():
    global setHiderParent, setHiderChild, R_Variable, L_Variable
    L_Content = []
    finalContentL = []
    for item in setHiderParent:
        L_item = item.replace(R_Variable, L_Variable)
        if L_item != item:
            L_Content.append(L_item)
            for itemL in L_Content:
                try:
                    cmds.select(itemL)
                    finalContentL.append(itemL)
                    cmds.select(finalContentL)
                    sel = cmds.ls(sl=True)
                    cmds.sets(sel, fe=setHiderChild)
                    cmds.select(cl=True)            
                except:
                    pass

def tryNomenclaturesMirror():
    global R_Variable, L_Variable
    R_Variable = "R_"; L_Variable = "L_"; mirrorCtrlsHider()
    R_Variable = "_R"; L_Variable = "_L"; mirrorCtrlsHider()
    R_Variable = "_R_"; L_Variable = "_L_"; mirrorCtrlsHider()
    R_Variable = "r_"; L_Variable = "l_"; mirrorCtrlsHider()
    R_Variable = "_r"; L_Variable = "_l"; mirrorCtrlsHider()
    R_Variable = "_r_"; L_Variable = "_l_"; mirrorCtrlsHider()
    R_Variable = "Right"; L_Variable = "Left"; mirrorCtrlsHider()
    R_Variable = "right"; L_Variable = "left"; mirrorCtrlsHider()
    R_Variable = "rt"; L_Variable = "lf"; mirrorCtrlsHider()
    R_Variable = "Rt"; L_Variable = "Lf"; mirrorCtrlsHider()
    R_Variable = "RGT"; L_Variable = "LFT"; mirrorCtrlsHider()
    R_Variable = "Rgt"; L_Variable = "Lft"; mirrorCtrlsHider()

def mirrorPolyHider():
    cmds.select(setHiderParent)
    mel.eval('reflectionSetMode objectx')
    mel.eval('reflectionSetMode none')
    cmds.select(setHiderParent, tgl=True)
    cmds.sets(fe=setHiderChild)
    cmds.select(cl=True)

def mirrorHider():
    global setHider, setHiderParent, setHiderChild
    try:
        setHiderParent = cmds.sets(Arm_R_Hider, q=True) or []
        setHiderChild = Arm_L_Hider
        tryNomenclaturesMirror()
        mirrorPolyHider()
        setHider = Arm_L_Hider
        print('Mirror successful'),
    except:
        setHider = Arm_L_Hider

    try:
        setHiderParent = cmds.sets(Leg_R_Hider, q=True) or []
        setHiderChild = Leg_L_Hider
        tryNomenclaturesMirror()
        mirrorPolyHider()
        setHider = Leg_L_Hider
        print('Mirror successful'),
    except:
        setHider = Leg_L_Hider

def waitAndRefresh():
    cmds.refresh(cv=True)
    time.sleep(0.3)
    cmds.refresh(cv=True)

def cycleTurnOnAndOff():
    waitAndRefresh()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()

def checkAllSets():
    global setHider, choise
    response = cmds.confirmDialog(
                    title='Confirm Check all sets',
                    message=confirmCheckAllSets,
                    button=['Yes', 'No'],
                    defaultButton='Yes',
                    cancelButton='Cancel',
                    dismissString='Cancel')
    if response == 'Yes':
        choise = 'show'; ShowOrHideAllSets()
        allSetsCheck = [Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider,
                        Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider]    
        cmds.progressWindow( title='Progress Hider test', isInterruptable=True )                                 
        amount = 0
        for s_name in allSetsCheck:
            cmds.progressWindow( edit=True, progress=amount, status=('Testing: ' + s_name) )
            setHider = s_name
            cycleTurnOnAndOff()
            amount = amount+11
            if cmds.progressWindow( query=True, isCancelled=True ) :
                break
            if cmds.progressWindow( query=True, progress=True ) >= 100 :
                break    
        cmds.progressWindow(endProgress=1)

def cycleTurnOnAndOffIsolate():
    waitAndRefresh()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()

def checkAllSetsIsolate():
    global setHider, choise
    choise = 'hide'; ShowOrHideAllSets()
    allSetsCheck = [Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider,
                    Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider]
    cmds.progressWindow( title='Progress Hider test', isInterruptable=True )                                 
    amount = 0
    for s_name in allSetsCheck:
        cmds.progressWindow( edit=True, progress=amount, status=('Testing: ' + s_name) )
        setHider = s_name
        cycleTurnOnAndOffIsolate()
        amount = amount+11
        if cmds.progressWindow( query=True, isCancelled=True ) :
            break
        if cmds.progressWindow( query=True, progress=True ) >= 100 :
            break    
    cmds.progressWindow(endProgress=1)
    choise = 'show'; ShowOrHideAllSets()

def launchtutorial():
    cmds.launch (web="https://youtu.be/RDHIFQfD12g")

def removeAllHider():
    removeAllBodySets()
    removeAllExtraSets()
    if cmds.objExists('ANM_Hider_Settings'): cmds.delete('ANM_Hider_Settings')
    if cmds.objExists('All_Sets_ANM_Hider'): cmds.delete('All_Sets_ANM_Hider')
    print(allRemoved), 

# ── PySide2 (Qt) High-End UI Implementation ──

class ANMHiderWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(ANMHiderWindow, self).__init__(parent)
        self.setObjectName("ANMHiderWindow")
        self.setWindowTitle("ANM Hider")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.is_edit_mode = True  # Mặc định mở rộng để animator thấy utilities
        self.faces_selection_mode = True  # Mặc định chọn Faces
        self.buttons = {}
        
        self.setup_ui()
        self.apply_stylesheet()
        
        # Load namespaces & settings
        declaringNameSpaces()
        createSettingsHider()
        self.update_namespace_info()
        self.refresh_ui()

    def setup_ui(self):
        # Layout chính của cửa sổ
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(6)
        
        # 1. Menu Bar mỏng
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setFixedHeight(22)
        
        file_menu = self.menu_bar.addMenu("File")
        save_action = file_menu.addAction("Save Sets")
        save_action.triggered.connect(self.on_save_sets)
        load_action = file_menu.addAction("Load Sets")
        load_action.triggered.connect(self.on_load_sets)
        
        help_menu = self.menu_bar.addMenu("Help")
        tut_action = help_menu.addAction("Video Tutorial")
        tut_action.triggered.connect(launchtutorial)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.on_about)
        
        self.main_layout.addWidget(self.menu_bar)
        
        # Tag hiển thị Namespace / Character đang chọn
        self.tag_layout = QtWidgets.QHBoxLayout()
        self.namespace_label = QtWidgets.QLabel("Rig: Created in the scene")
        self.namespace_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00BCD4; padding-left: 2px;")
        self.tag_layout.addWidget(self.namespace_label)
        self.tag_layout.addStretch()
        self.main_layout.addLayout(self.tag_layout)
        
        # 2. Hàng nút ngang (Bộ phận cơ thể & Set điều khiển)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.buttons_layout.setContentsMargins(2, 0, 2, 0)
        
        # Nút Edit Mode (Contract/Expand)
        self.edit_mode_btn = QtWidgets.QPushButton()
        self.edit_mode_btn.setFixedSize(30, 30)
        self.edit_mode_btn.setToolTip("Toggle Edit / Usage Mode")
        self.edit_mode_btn.clicked.connect(self.toggle_edit_mode)
        self.buttons_layout.addWidget(self.edit_mode_btn)
        
        # List định nghĩa các nút bấm Hider chính
        self.hider_defs = [
            ("All_Sets_Hider", All_Sets_Hider, "All Sets", allSets_Ann, self.on_all_sets_click),
            ("Head_Hider", Head_Hider, "Head", blueButtons_Ann, lambda: self.on_part_click(Head_Hider)),
            ("Torso_Hider", Torso_Hider, "Torso", blueButtons_Ann, lambda: self.on_part_click(Torso_Hider)),
            ("Arm_R_Hider", Arm_R_Hider, "Arm R", blueButtons_Ann, lambda: self.on_part_click(Arm_R_Hider)),
            ("Arm_L_Hider", Arm_L_Hider, "Arm L", blueButtons_Ann, lambda: self.on_part_click(Arm_L_Hider)),
            ("Leg_R_Hider", Leg_R_Hider, "Leg R", blueButtons_Ann, lambda: self.on_part_click(Leg_R_Hider)),
            ("Leg_L_Hider", Leg_L_Hider, "Leg L", blueButtons_Ann, lambda: self.on_part_click(Leg_L_Hider)),
            ("Extra_One_Hider", Extra_One_Hider, "Extra 1", blueButtons_Ann, lambda: self.on_part_click(Extra_One_Hider)),
            ("Extra_Two_Hider", Extra_Two_Hider, "Extra 2", blueButtons_Ann, lambda: self.on_part_click(Extra_Two_Hider)),
            ("Extra_Three_Hider", Extra_Three_Hider, "Extra 3", blueButtons_Ann, lambda: self.on_part_click(Extra_Three_Hider)),
        ]
        
        for key_name, var_name, label, tooltip, conn in self.hider_defs:
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(30, 30)
            btn.setToolTip(tooltip)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            # Dùng lambda bọc để tránh mất context
            btn.customContextMenuRequested.connect(lambda pos, k=key_name, v=var_name: self.show_context_menu(pos, k, v))
            btn.clicked.connect(conn)
            self.buttons[key_name] = btn
            self.buttons_layout.addWidget(btn)
            
        self.main_layout.addLayout(self.buttons_layout)
        
        # 3. Widget Utilities (Hàng dưới, có thể thu gọn được)
        self.utility_widget = QtWidgets.QWidget()
        self.utility_layout = QtWidgets.QHBoxLayout(self.utility_widget)
        self.utility_layout.setContentsMargins(2, 4, 2, 2)
        self.utility_layout.setSpacing(4)
        
        # Nút Unlock / Lock options
        self.unlock_btn = QtWidgets.QPushButton()
        self.unlock_btn.setFixedSize(30, 30)
        self.unlock_btn.setToolTip("Lock/Unlock Utilities (Right click for options)")
        self.unlock_btn.setIcon(QtGui.QIcon(get_icon_path("Unlock_Hider.png")))
        self.unlock_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.unlock_btn.customContextMenuRequested.connect(self.show_unlock_context_menu)
        self.unlock_btn.clicked.connect(lambda: cmds.warning("Right click to see unlock/lock options"))
        self.utility_layout.addWidget(self.unlock_btn)
        
        # Nút Object Mode
        self.obj_mode_btn = QtWidgets.QPushButton()
        self.obj_mode_btn.setFixedSize(30, 30)
        self.obj_mode_btn.setToolTip("Object Mode")
        self.obj_mode_btn.setIcon(QtGui.QIcon(get_icon_path("ObjectMode_Hider.png")))
        self.obj_mode_btn.clicked.connect(self.on_object_mode)
        self.utility_layout.addWidget(self.obj_mode_btn)
        
        # Nút Poly / Curves Selection Mode
        self.poly_curve_btn = QtWidgets.QPushButton()
        self.poly_curve_btn.setFixedSize(30, 30)
        self.poly_curve_btn.setToolTip("Switch Poly/Curves Selection (Right click for color)")
        self.poly_curve_btn.setIcon(QtGui.QIcon(get_icon_path("Only_Faces_Hider.png")))
        self.poly_curve_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.poly_curve_btn.customContextMenuRequested.connect(self.show_color_context_menu)
        self.poly_curve_btn.clicked.connect(self.toggle_poly_curve_mode)
        self.utility_layout.addWidget(self.poly_curve_btn)
        
        # Nút Grow Selection
        self.grow_btn = QtWidgets.QPushButton()
        self.grow_btn.setFixedSize(30, 30)
        self.grow_btn.setToolTip(grow_Ann)
        self.grow_btn.setIcon(QtGui.QIcon(get_icon_path("Grow_Hider.png")))
        self.grow_btn.clicked.connect(lambda: cmds.polySelectConstraint(pp=1))
        self.utility_layout.addWidget(self.grow_btn)
        
        # Nút Shrink Selection
        self.shrink_btn = QtWidgets.QPushButton()
        self.shrink_btn.setFixedSize(30, 30)
        self.shrink_btn.setToolTip(shrink_Ann)
        self.shrink_btn.setIcon(QtGui.QIcon(get_icon_path("Shrink_Hider.png")))
        self.shrink_btn.clicked.connect(lambda: cmds.polySelectConstraint(pp=2))
        self.utility_layout.addWidget(self.shrink_btn)
        
        # Nút Template Line Window
        self.template_btn = QtWidgets.QPushButton()
        self.template_btn.setFixedSize(30, 30)
        self.template_btn.setToolTip("Select template lines between elbow and PV")
        self.template_btn.setIcon(QtGui.QIcon(get_icon_path("Template_Line_Hider.png")))
        self.template_btn.clicked.connect(SelectTemplateLineWindow)
        self.utility_layout.addWidget(self.template_btn)
        
        # Nút Mirror
        self.mirror_btn = QtWidgets.QPushButton()
        self.mirror_btn.setFixedSize(30, 30)
        self.mirror_btn.setToolTip("Mirror Right to Left")
        self.mirror_btn.setIcon(QtGui.QIcon(get_icon_path("Mirror_Hider.png")))
        self.mirror_btn.clicked.connect(mirrorHider)
        self.utility_layout.addWidget(self.mirror_btn)
        
        # Nút Check all sets (Eye icon)
        self.check_sets_btn = QtWidgets.QPushButton()
        self.check_sets_btn.setFixedSize(30, 30)
        self.check_sets_btn.setToolTip("Check All Sets (Right click for Isolate Mode)")
        self.check_sets_btn.setIcon(QtGui.QIcon(get_icon_path("Show_All_Hidden_Faces_Hider.png")))
        self.check_sets_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.check_sets_btn.customContextMenuRequested.connect(self.show_check_sets_context_menu)
        self.check_sets_btn.clicked.connect(checkAllSets)
        self.utility_layout.addWidget(self.check_sets_btn)
        
        # Nút Extra Functions (+)
        self.extra_funcs_btn = QtWidgets.QPushButton()
        self.extra_funcs_btn.setFixedSize(30, 30)
        self.extra_funcs_btn.setToolTip("Extra Functions (Right click for options)")
        self.extra_funcs_btn.setIcon(QtGui.QIcon(get_icon_path("Extra_Functions_Hider.png")))
        self.extra_funcs_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.extra_funcs_btn.customContextMenuRequested.connect(self.show_extra_context_menu)
        self.extra_funcs_btn.clicked.connect(lambda: cmds.warning("Right click to see extra functions"))
        self.utility_layout.addWidget(self.extra_funcs_btn)
        
        # Nút Remove All (X)
        self.remove_all_btn = QtWidgets.QPushButton()
        self.remove_all_btn.setFixedSize(30, 30)
        self.remove_all_btn.setToolTip("Delete everything related to ANM Hider")
        self.remove_all_btn.setIcon(QtGui.QIcon(get_icon_path("Remove_All_Hider.png")))
        self.remove_all_btn.clicked.connect(self.on_remove_all_click)
        self.utility_layout.addWidget(self.remove_all_btn)
        
        self.main_layout.addWidget(self.utility_widget)
        
        # Set size ban đầu của window
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def apply_stylesheet(self):
        # CSS phẳng phong cách tối giản màu Cyan cao cấp đồng bộ với Animeow Toolboard v02
        self.setStyleSheet("""
            QDialog {
                background-color: #15181B;
                border: 1px solid #2B2F36;
                border-radius: 6px;
            }
            QMenuBar {
                background-color: #1B1E22;
                color: #A0A5B0;
                font-size: 11px;
                border-bottom: 1px solid #2B2F36;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 2px 8px;
            }
            QMenuBar::item:selected {
                background-color: #00BCD4;
                color: #121212;
                border-radius: 3px;
            }
            QMenu {
                background-color: #1B1E22;
                color: #D5D9E0;
                border: 1px solid #2B2F36;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 4px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #00BCD4;
                color: #121212;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2B2F36;
                margin: 4px 0px;
            }
            QPushButton {
                background-color: #1C2024;
                border: 1px solid #2D3238;
                border-radius: 4px;
                padding: 1px;
            }
            QPushButton:hover {
                background-color: rgba(0, 188, 212, 0.15);
                border: 1px solid rgba(0, 188, 212, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(0, 188, 212, 0.3);
            }
        """)

    def update_namespace_info(self):
        global namespaceHiderForWindow
        self.namespace_label.setText(f"Rig: {namespaceHiderForWindow}")

    def refresh_ui(self):
        # Cập nhật Edit Mode icon
        if self.is_edit_mode:
            self.edit_mode_btn.setIcon(QtGui.QIcon(get_icon_path("Contract_Hider.png")))
            self.utility_widget.show()
        else:
            self.edit_mode_btn.setIcon(QtGui.QIcon(get_icon_path("Expand_Hider.png")))
            self.utility_widget.hide()
            
        # Co dãn kích thước dialog mượt mà
        self.setFixedSize(QtCore.QSize(QtCore.QWIDGETSIZE_MAX, QtCore.QWIDGETSIZE_MAX))
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())
        
        # Cập nhật icon của từng nút bấm theo trạng thái set trong scene
        self.check_all_button_states()

    def check_all_button_states(self):
        # Duyệt qua các nút bộ phận cơ thể để đổi icon
        for key_name, var_name, _, _, _ in self.hider_defs:
            if not cmds.objExists(var_name):
                # Nếu set chưa tồn tại trong scene -> Empty
                icon_file = key_name + "_Empty.png"
            else:
                content = cmds.sets(var_name, q=True)
                if not content or str(content) == "None":
                    icon_file = key_name + "_Empty.png"
                else:
                    # Đọc trạng thái State
                    removeNameSpace()
                    state_attr = ANM_Hider_Settings + "." + key_name + "_State"
                    addNameSpace()
                    
                    if cmds.objExists(state_attr) and cmds.getAttr(state_attr) == 1:
                        icon_file = key_name + ".png"  # Sáng
                    else:
                        icon_file = key_name + "_Off.png"  # Mờ
            
            btn = self.buttons.get(key_name)
            if btn:
                btn.setIcon(QtGui.QIcon(get_icon_path(icon_file)))

    def toggle_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        self.refresh_ui()

    def on_all_sets_click(self):
        # Click All Sets
        global setHider
        setHider = All_Sets_Hider
        ShowOrHideAllSetsButton()
        self.check_all_button_states()

    def on_part_click(self, var_name):
        global setHider
        setHider = var_name
        showOrHideButton()
        self.check_all_button_states()

    def show_context_menu(self, pos, key_name, var_name):
        # Context Menu chuột phải bo góc Cyan phẳng cực đẹp
        menu = QtWidgets.QMenu(self)
        
        add_action = menu.addAction("Add Selection (Transform)")
        add_action.triggered.connect(lambda: self.on_add_sel(var_name, "Off"))
        
        add_shape_action = menu.addAction("Add Selection Shape")
        add_shape_action.triggered.connect(lambda: self.on_add_sel(var_name, "On"))
        
        menu.addSeparator()
        
        rm_sel_action = menu.addAction("Remove Selection")
        rm_sel_action.triggered.connect(lambda: self.on_rm_sel(var_name))
        
        sel_set_action = menu.addAction("Select Set")
        sel_set_action.triggered.connect(lambda: self.on_select_set(var_name))
        
        rm_set_action = menu.addAction("Remove Set")
        rm_set_action.triggered.connect(lambda: self.on_remove_set(var_name))
        
        # Chạy menu
        btn = self.buttons.get(key_name)
        if btn:
            menu.exec_(btn.mapToGlobal(pos))

    def on_add_sel(self, var_name, mode):
        global setHider, shapeMode
        setHider = var_name
        shapeMode = mode
        addSelectionToSet()
        self.check_all_button_states()

    def on_rm_sel(self, var_name):
        global setHider
        setHider = var_name
        removeSelection()
        self.check_all_button_states()

    def on_select_set(self, var_name):
        global setHider
        setHider = var_name
        selectSet()

    def on_remove_set(self, var_name):
        global setHider
        setHider = var_name
        removeSet()
        self.check_all_button_states()

    def show_unlock_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        
        a1 = menu.addAction("Unlock All Visible")
        a1.triggered.connect(unlockAllVisible)
        
        a2 = menu.addAction("Unlock All Visible Meshes")
        a2.triggered.connect(unlockAllVismeshes)
        
        menu.addSeparator()
        
        a3 = menu.addAction("Lock Selection")
        a3.triggered.connect(lockSelection)
        
        menu.exec_(self.unlock_btn.mapToGlobal(pos))

    def show_color_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        
        a1 = menu.addAction("Poly selection color: Red")
        a1.triggered.connect(lambda: cmds.displayColor('polyFace', 13, active=True))
        
        a2 = menu.addAction("Poly selection color: Green")
        a2.triggered.connect(lambda: cmds.displayColor('polyFace', 14, active=True))
        
        a3 = menu.addAction("Poly selection color: Default")
        a3.triggered.connect(lambda: cmds.displayColor('polyFace', 21, active=True))
        
        menu.exec_(self.poly_curve_btn.mapToGlobal(pos))

    def show_check_sets_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        a1 = menu.addAction("Isolate mode (Check and isolate)")
        a1.triggered.connect(checkAllSetsIsolate)
        menu.exec_(self.check_sets_btn.mapToGlobal(pos))

    def show_extra_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        a1 = menu.addAction("Show all hidden faces in the scene")
        a1.triggered.connect(showAllHiddenFaces)
        menu.exec_(self.extra_funcs_btn.mapToGlobal(pos))

    def toggle_poly_curve_mode(self):
        self.faces_selection_mode = not self.faces_selection_mode
        switchPolyOrNurbsSel(self.faces_selection_mode)
        if self.faces_selection_mode:
            self.poly_curve_btn.setIcon(QtGui.QIcon(get_icon_path("Only_Faces_Hider.png")))
        else:
            self.poly_curve_btn.setIcon(QtGui.QIcon(get_icon_path("Only_NurbsCurve_Hider.png")))

    def on_object_mode(self):
        objectModeHider()
        self.faces_selection_mode = False
        self.poly_curve_btn.setIcon(QtGui.QIcon(get_icon_path("Only_NurbsCurve_Hider.png")))

    def on_remove_all_click(self):
        response = cmds.confirmDialog(
            title='ANM Hider Confirm',
            message=removeAllConfirm, 
            button=['Yes', 'No'],
            defaultButton='Yes',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if response == 'Yes':
            removeAllHider()
            self.check_all_button_states()
            self.close()

    def on_save_sets(self):
        saveSetsHider()
        self.check_all_button_states()

    def on_load_sets(self):
        LoadSetsHider()
        self.check_all_button_states()

    def on_about(self):
        QtWidgets.QMessageBox.information(
            self, "About", 
            f"{versionHider}\n\nĐược nâng cấp và thiết kế lại giao diện phẳng PySide2 tối giản cho bộ công cụ Animeow Maya Toolboard.\n\nOriginal tool by Francisco Cerchiara Montero."
        )

# ── Entry Point show_hider ──

_hider_window_instance = None

def show_hider():
    """Hàm khởi chạy chính bằng giao diện PySide2 cao cấp"""
    global _hider_window_instance
    setup_icons_path()
    
    # Đóng cửa sổ cũ nếu có
    if _hider_window_instance is not None:
        try:
            _hider_window_instance.close()
        except:
            pass
        _hider_window_instance = None
        
    _hider_window_instance = ANMHiderWindow()
    _hider_window_instance.show()
