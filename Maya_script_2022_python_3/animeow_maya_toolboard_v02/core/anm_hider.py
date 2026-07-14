# -*- coding: utf-8 -*-
"""
ANM Hider v2.2 - Character part visibility manager for Maya.
Converted and integrated into Animeow Toolboard v02.
Original tool by Francisco Cerchiara Montero.
"""

import os
import time
import subprocess
import maya.cmds as cmds
import maya.mel as mel

# Version
versionHider = 'ANM_Hider Beta 2.2'

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
commandButton = ''
popUpButton = ''
choise = ''
setHiderParent = []
setHiderChild = ''
R_Variable = ''
L_Variable = ''

# Window Size
highWindow = 20
widthWindow = 388

# Annotations for popUp help:
allSets_Ann = 'Left Click:\n -Switch between Show and Hide set\n\nRight click options:\n- Remove all the Body sets\n- Select all content of the set\n- Remove all the Extra sets'
blueButtons_Ann = 'Left Click:\n -Switch between Show and Hide set\n\nRight click options:\n- Add your current selection to the current set\n- Remove your current selection from the current set\n- Select all content of the set\n- Remove all content from the current set'
templateLine_Ann = 'This button allows you to select the usual line between the elbow control and the pole vector control that is mostly unselectable'
editMode_Ann = 'Toggle between Usage and Edit mode'
addSel_Ann = 'Add your current selection to the current set'
addSelExtra_Ann = 'Add your current selection to the current set (Only shapes and polygons)'
grow_Ann = 'Grow selection'
shrink_Ann = 'Shrink selection'
switchPolyOrNurbsCurves_Ann = 'Left Click:\n-Switch between Poly selection and NurbsCurves\nRight Click:\n-Change poly color selection'
objectMode_Ann = 'Object Mode'
deleteAll_Ann = 'Delete everything related to the script'
help_Ann = 'Open help window'
showAllHiddenFaces_Ann = 'Show all hidden faces in the scene'
checkAllSets_Ann = 'Turn OFF and ON two times each set to check the overall setup'
mirrorButtons_Ann = 'Mirror right Arm and Leg content to the left ones'
unlockAllVisMeshes_Ann = 'Make selectable all visible meshes and unlock all layer display on the scene'
unlockAllVis_Ann = 'Make selectable all: mesh shape, nurbsCurve shape, transform, annotation shape of the scene'
lockSelection_Ann = 'Make all the items selected unselectables'
rightClickToSeeButtons_Ann = 'Right click to see the buttons'

# Prints
setsExportSucces = 'Sets exported succesfully!'
setsLoadSucces = 'Sets loaded succesfully!'
setHided = 'Set hidden'
setVisible = 'Set Visible'
allVisMeshSelectable = 'All visible meshes are selectable, and all layerDisplay are unlocked'
allBodySetsRemoved = 'All Body sets removed' 
allExtraSetsRemoved = 'All Extra sets removed'
keepYourSecrets = 'Alright then, keep your secrets' 
allRemoved = 'everything related to ANM_Hider Removed'
selRemoved = 'Selection removed'

# Warnings
allFacesAreVisible = 'All faces are visible'
setDoesntExistsSet = 'Set doesn\'t exists'
hiderSystemWarning = 'There is more than one Hider system, select the character you want to run'
confirmCheckAllSets = 'This may take a while, do you want to check them?'
nothingSel = 'Nothing selected' 
setDontExists = 'Set doesn\'t exist'
couldntUnlockAllMeshes = "Couldn't unlock all the meshes because they are in a layerDisplay, check if you can unlock them trough layer display"
couldntUnlockAllLayerDisplay = "Couldn't unlock all layerDisplay"
nothingSelected = 'Nothing selected'
setDoesntExists = "Set doesn't exist"

# Error
errorLoadSets = 'Error trying to load the set, Try to set the namespace the same than when you export the file' 
errorExportSets = 'You can only save sets created in the scene'

# PromptWindows
removeAllConfirm = 'Are you sure you want to delete everything related to the script?'

def setup_icons_path():
    """Tự động thêm thư mục chứa Icons_Hider của package vào XBMLANGPATH của Maya"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_icons_dir = os.path.join(current_dir, "..", "icons")
    package_icons_dir = os.path.abspath(package_icons_dir).replace("\\", "/")
    
    xbm_path = os.environ.get("XBMLANGPATH", "")
    paths = xbm_path.split(";")
    if package_icons_dir not in paths:
        os.environ["XBMLANGPATH"] = package_icons_dir + ";" + xbm_path

def declaringSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, ANM_Hider_Settings
    All_Sets_Hider = ( namespaceHider + 'All_Sets_Hider' )
    Head_Hider = ( namespaceHider + 'Head_Hider' )
    Torso_Hider = ( namespaceHider + 'Torso_Hider' )
    Arm_R_Hider = ( namespaceHider + 'Arm_R_Hider' )
    Arm_L_Hider = ( namespaceHider + 'Arm_L_Hider' )
    Leg_R_Hider = ( namespaceHider + 'Leg_R_Hider' )
    Leg_L_Hider = ( namespaceHider + 'Leg_L_Hider' )
    Extra_One_Hider = ( namespaceHider + 'Extra_One_Hider' )
    Extra_Two_Hider = ( namespaceHider + 'Extra_Two_Hider' )
    Extra_Three_Hider = ( namespaceHider + 'Extra_Three_Hider' )
    ANM_Hider_Settings = ( namespaceHider + 'ANM_Hider_Settings' )

def createAllSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, ANM_Hider_Settings
    if cmds.objExists('All_Sets_Hider') == 0: cmds.sets(n='All_Sets_Hider', em=True)
    if cmds.objExists(Head_Hider) == 0: cmds.sets(n=Head_Hider, em=True)
    if cmds.objExists(Torso_Hider) == 0: cmds.sets(n=Torso_Hider, em=True)
    if cmds.objExists(Arm_R_Hider) == 0: cmds.sets(n=Arm_R_Hider, em=True)
    if cmds.objExists(Arm_L_Hider) == 0: cmds.sets(n=Arm_L_Hider, em=True)
    if cmds.objExists(Leg_R_Hider) == 0: cmds.sets(n=Leg_R_Hider, em=True)
    if cmds.objExists(Leg_L_Hider) == 0: cmds.sets(n=Leg_L_Hider, em=True)
    if cmds.objExists(Extra_One_Hider) == 0: cmds.sets(n=Extra_One_Hider, em=True)
    if cmds.objExists(Extra_Two_Hider) == 0: cmds.sets(n=Extra_Two_Hider, em=True)
    if cmds.objExists(Extra_Three_Hider) == 0: cmds.sets(n=Extra_Three_Hider, em=True)
    # parent all sets to All_Sets_Hider
    cmds.sets (Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider,
    Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, edit=True, fe='All_Sets_Hider' )

def createSettingsHider():
    if cmds.objExists ('ANM_Hider_Settings') == 0:
        selCurrent = cmds.ls (sl=True)
        cmds.group (em=True, n= 'ANM_Hider_Settings')
        cmds.setAttr (".tx", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".ty", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".tz", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".rx", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".ry", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".rz", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".sx", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".sy", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".sz", lock=True, keyable=False, channelBox=False )
        cmds.setAttr (".v", lock=True, keyable=False, channelBox=False )
        # Create Attr States
        cmds.addAttr ('ANM_Hider_Settings', ln='All_Sets_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Head_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Torso_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Arm_R_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Arm_L_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Leg_L_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Leg_R_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_One_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_Two_Hider_State',at='bool', dv=True, keyable=True)
        cmds.addAttr ('ANM_Hider_Settings', ln='Extra_Three_Hider_State',at='bool', dv=True, keyable=True)
        # Create Attr Edit Mode
        cmds.addAttr ('ANM_Hider_Settings', ln='Edit_Mode_State',at='bool', dv=True, keyable=True)
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
            cmds.select('ANM_Hider_Settings',tgl=True)
        except:
            pass    
        settings = cmds.ls(sl=True)
        
        if len(settings) >= 1:
            try:
                try:
                    namespaceHiderForWindow = cmds.referenceQuery( currentSel[0], namespace=True, shortName=True )
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
        cmds.warning("set doesn't exists")
    
    removeNameSpace()
    cmds.setAttr( ANM_Hider_Settings + '.' + (setHider + '_State'), 0)
    checkStateIcon()

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
    checkStateIcon()

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
        checkAllIconSets()

def ShowOrHideAllSetsButton():   
    global choise    
    if cmds.getAttr(ANM_Hider_Settings + '.All_Sets_Hider_State'):
        choise = 'hide'; ShowOrHideAllSets()
    else:
        choise = 'show'; ShowOrHideAllSets()

def checkStateIcon():
    global setHider, namespaceHider
    try:
        addNameSpace()
        contentSet = cmds.sets(setHider, q=True)
        if str(contentSet) == 'None':
            removeNameSpace()
            cmds.iconTextButton ( (setHider + "button"), e=True, image=("Icons_Hider/" + setHider + "_Empty" + ".png") )
        else:
            removeNameSpace()
            if cmds.getAttr( ANM_Hider_Settings + '.' + (setHider + '_State') ):
                cmds.iconTextButton ( (setHider + "button"), e=True, image=("Icons_Hider/" + setHider + ".png") )
            else:
                cmds.iconTextButton ( (setHider + "button"), e=True, image=("Icons_Hider/" + setHider + "_Off" + ".png") )
    except:
        pass

def checkAllIconSets():
    global setHider
    setHider = Head_Hider; removeNameSpace(); checkStateIcon()
    setHider = Torso_Hider; removeNameSpace(); checkStateIcon()
    setHider = Arm_R_Hider; removeNameSpace(); checkStateIcon()
    setHider = Arm_L_Hider; removeNameSpace(); checkStateIcon()
    setHider = Leg_R_Hider; removeNameSpace(); checkStateIcon()
    setHider = Leg_L_Hider; removeNameSpace(); checkStateIcon()
    setHider = Extra_One_Hider; removeNameSpace(); checkStateIcon()
    setHider = Extra_Two_Hider; removeNameSpace(); checkStateIcon()
    setHider = Extra_Three_Hider; removeNameSpace(); checkStateIcon()

def ShowOrHideAllSets():
    global setHider
    sets_In_AllSetsHider = cmds.sets(All_Sets_Hider,q=True) or []
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
        checkStateIcon()

def selectSet():
    if cmds.objExists(setHider):
        cmds.select(setHider)
    else:
        cmds.warning("set doesn't exists")

def showAllHiddenFaces():
    if cmds.objExists('defaultHideFaceDataSet'):
        cmds.showHidden('defaultHideFaceDataSet')
        print(allFacesAreVisible),
    else:
        cmds.warning('No faces hidded')

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

def removeAllHider():
    removeAllBodySets()
    removeAllExtraSets()
    if cmds.objExists(ANM_Hider_Settings): cmds.delete(ANM_Hider_Settings)
    if cmds.objExists('All_Sets_Hider'): cmds.delete('All_Sets_Hider')
    if cmds.window ("windowHider", exists=True):
        cmds.deleteUI ("windowHider")
    print(allRemoved), 

def confirmRemoveAllHider():
    response = cmds.confirmDialog(
                    title='Confirm Window',
                    message=removeAllConfirm, 
                    button=['Yes', 'No'],
                    defaultButton='Yes',
                    cancelButton='Cancel',
                    dismissString='Cancel')
    if response == 'Yes':
        removeAllHider()
    if response == 'No':    
        print(keepYourSecrets), 

def removeSet():
    global setHider
    showSet()
    allSet_q = cmds.sets(setHider, q=True) or []
    if allSet_q:
        cmds.sets(allSet_q, edit=True, rm=setHider)
    checkStateIcon()

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
            checkStateIcon()
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
        allSets = [Head_Hider,Torso_Hider,Arm_R_Hider,Arm_L_Hider,
        Leg_R_Hider,Leg_L_Hider, Extra_One_Hider,Extra_Two_Hider,Extra_Three_Hider]    
        SourceFile = cmds.fileDialog2(startingDirectory ="/usr/u/bozo/myFiles/", fileFilter="Python File(*.py)")
        if SourceFile:
            SourceFile = ''.join([str(elem) for elem in SourceFile]) 
            fileHandle = open((SourceFile), 'w')
            fileHandle.write("## Remove existent sets\n" + "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeAllBodySets()\nfh.removeAllExtraSets()\n")
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

def inViewMessageHider():
    global messageHider
    cmds.inViewMessage (amg="<span style=\"color:#82C99A;\"> "+messageHider+" </span> ", 
    dragKill=True, pos='topCenter',fade=True)

def toggleEditMode():
    if cmds.window ('windowHider',q=True, h=True) == (36 + highWindow) :
        cmds.iconTextButton ('Edit_Modebutton', e=True, image1="Icons_Hider/Contract_Hider.png")
        cmds.window ('windowHider', edit=True, w=widthWindow, h=(74 + highWindow))
        cmds.setAttr (ANM_Hider_Settings +'.Edit_Mode_State', 1)
    else:
        cmds.iconTextButton ('Edit_Modebutton', e=True, image1="Icons_Hider/Expand_Hider.png")
        cmds.window ('windowHider', edit=True, w=widthWindow, h=(36 + highWindow))
        cmds.setAttr (ANM_Hider_Settings+'.Edit_Mode_State', 0)

def checkEditMode():
    if cmds.getAttr( ANM_Hider_Settings + '.Edit_Mode_State' ):
        cmds.iconTextButton ('Edit_Modebutton', e=True, image1="Icons_Hider/Contract_Hider.png")
        cmds.window ('windowHider', edit=True, w=widthWindow, h=(74 + highWindow) )
    else:
        cmds.iconTextButton ('Edit_Modebutton', e=True, image1="Icons_Hider/Expand_Hider.png")
        cmds.window ('windowHider', edit=True, w=widthWindow, h=(36 + highWindow))

def objectModeHider():
    global messageHider
    cmds.selectMode(object=True)
    mel.eval('selectMode -object; selectType -handle 1 -ikHandle 1 -joint 1 -nurbsCurve 1 -cos 1 -stroke 1 -nurbsSurface 1 -polymesh 1 -subdiv 1 -plane 1 -lattice 1 -cluster 1 -sculpt 1 -nonlinear 1 -particleShape 1 -emitter 1 -field 1 -spring 1 -rigidBody 1 -fluid 1 -hairSystem 1 -follicle 1 -nCloth 1 -nRigid 1 -dynamicConstraint 1 -rigidConstraint 1 -collisionModel 1 -light 1 -camera 1 -texture 1 -ikEndEffector 1 -locator 1 -dimension 1;selectType -byName gpuCache 1;')
    mel.eval('selectMode -component; selectType -cv 1 -vertex 1 -subdivMeshPoint 1 -latticePoint 1 -particle 1 -editPoint 0 -curveParameterPoint 0 -surfaceParameterPoint 0 -puv 0 -polymeshEdge 0 -subdivMeshEdge 0 -isoparm 0 -surfaceEdge 0 -surfaceFace 1 -springComponent 0 -facet 0 -subdivMeshFace 1 -hull 0 -rotatePivot 0 -scalePivot 0 -jointPivot 0 -selectHandle 0 -localRotationAxis 0 -imagePlane 0;')
    mel.eval('changeSelectMode -object')
    messageHider = 'Object Mode'; inViewMessageHider()

def switchPolyOrNurbsSel():
    global messageHider
    if cmds.iconTextButton('toggleFacesNurbsCurve', q=True, i=True) == "Icons_Hider/Only_Faces_Hider.png":
        objectModeHider()
        cmds.selectType (cv=True)
        mel.eval('setObjectPickMask "All" 0;setObjectPickMask "Curve" true')
        messageHider = 'NurbsCurve selection Mode'; inViewMessageHider()
        cmds.iconTextButton ('toggleFacesNurbsCurve', e=True, i="Icons_Hider/Only_NurbsCurve_Hider.png")
    else:
        mel.eval('changeSelectMode -component')
        mel.eval('setComponentPickMask "Facet" true; ')
        cmds.selectType (cv=False)
        messageHider = 'Poly Faces selection Mode'; inViewMessageHider()
        cmds.iconTextButton ('toggleFacesNurbsCurve', e=True, i="Icons_Hider/Only_Faces_Hider.png")

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
    print('Select Template Line Window'),

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
        checkStateIcon()
        print('Mirror successful'),
    except:
        setHider = Arm_L_Hider
        checkStateIcon()

    try:
        setHiderParent = cmds.sets(Leg_R_Hider, q=True) or []
        setHiderChild = Leg_L_Hider
        tryNomenclaturesMirror()
        mirrorPolyHider()
        setHider = Leg_L_Hider
        checkStateIcon()
        print('Mirror successful'),
    except:
        setHider = Leg_L_Hider
        checkStateIcon()

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
        allSetsCheck = [Head_Hider,Torso_Hider,Arm_R_Hider,Arm_L_Hider,
        Leg_R_Hider,Leg_L_Hider, Extra_One_Hider,Extra_Two_Hider,Extra_Three_Hider]    
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
    allSetsCheck = [Head_Hider,Torso_Hider,Arm_R_Hider,Arm_L_Hider,
    Leg_R_Hider,Leg_L_Hider, Extra_One_Hider,Extra_Two_Hider,Extra_Three_Hider]
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

def toggleImageHelpWindow():
    if cmds.image("helpwindowimage", q=True, image=True) == "Icons_Hider/Help_2_On_Hider.png":
        cmds.image ("helpwindowimage", e=True, image="Icons_Hider/Help_2_Off_Hider.png")
    else:
        cmds.image ("helpwindowimage", e=True, image="Icons_Hider/Help_2_On_Hider.png")
    
def helpWindow():
    if cmds.window ('HelpWindowHider', exists=True):
        cmds.deleteUI ("HelpWindowHider")
    helpWindowHider = cmds.window('HelpWindowHider',  s=False, h=680, w=656, title="Help Window Hider")
    scrollLayout = cmds.scrollLayout(horizontalScrollBarThickness=20, verticalScrollBarThickness=16)

    cmds.image(i="Icons_Hider/Help_1_Hider.png")
    form = cmds.formLayout()
    object = cmds.button (l="", w=200, h=28, c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.toggleImageHelpWindow()", backgroundColor=[0.72,0.15,0.16])
    cmds.formLayout (form, edit=True, attachForm= [[object, "top", 5], [object, "left", 215]])
    object = cmds.text(l='Press here repeatedly to see ', font='boldLabelFont')
    cmds.formLayout (form, edit=True, attachForm= [[object, "top", 12], [object, "left", 240]])

    cmds.setParent('..')
    cmds.image('helpwindowimage',i="Icons_Hider/Help_2_On_Hider.png")
    
    form = cmds.formLayout()
    object = cmds.text (l="By Francisco Cerchiara Montero", font='boldLabelFont')
    cmds.formLayout (form, edit=True, attachForm= [[object, "top", 5], [object, "left", 470]])
    object = cmds.button (l="Link to online tutorial", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.launchtutorial()", backgroundColor=[0.72,0.15,0.16])
    cmds.formLayout (form, edit=True, attachForm= [[object, "top", 0], [object, "left", 10]])
    
    cmds.setParent('..')
    cmds.showWindow (helpWindowHider)

def contactWindow():
    if cmds.window ("ANM_Contact", exists=True ):
        cmds.deleteUI ("ANM_Contact")
    ANMContact = cmds.window ("ANM_Contact", title="Contact", s=False)
    
    cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)] )
    cmds.text( label='Name:  ' )
    name = cmds.textField(text='Francisco Cerchiara Montero', editable=True)
    cmds.text( label='Email:  ' )
    address = cmds.textField(text='FranCM127@hotmail.com', editable=True)
    cmds.text( label='Facebook:  ' )
    phoneNumber = cmds.textField(text='www.facebook.com/Fran127', editable=True)
    cmds.text( label='Linked-In:  ' )
    email = cmds.textField(text='www.linkedin.com/in/francm3danimator/', editable=True)
    
    cmds.textField( name, edit=True, enterCommand=('cmds.setFocus(\"' + address + '\")') )
    cmds.textField( address, edit=True, enterCommand=('cmds.setFocus(\"' + phoneNumber + '\")') )
    cmds.textField( phoneNumber, edit=True, enterCommand=('cmds.setFocus(\"' + email + '\")') )
    cmds.textField( email, edit=True, enterCommand=('cmds.setFocus(\"' + name + '\")') )
    
    cmds.showWindow( ANMContact )

def buttonWindowHider():
    global shapeMode
    removeNameSpace()
    cmds.iconTextButton ( (setHider + "button"), style="iconOnly",
    ann=blueButtons_Ann, commandRepeatable=True, i=("Icons_Hider/" + setHider + ".png"),
    c=commandButton ) 
    cmds.popupMenu(postMenuCommand = popUpButton)
    cmds.menuItem (i="Icons_Hider/PopUp_Add_Hider.png", l="Add Selection", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.shapeMode = 'Off'; fh.addSelectionToSet()")
    cmds.menuItem (i="Icons_Hider/PopUp_Add_Hider.png", l="Add Selection Shape", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.shapeMode = 'On'; fh.addSelectionToSet()")
    cmds.menuItem (divider=True)
    cmds.menuItem (i="Icons_Hider/PopUp_Remove_Hider.png", l="Remove Selection", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeSelection()")
    cmds.menuItem (i="Icons_Hider/PopUp_SelectSet_Hider.png", l="Select Set", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.selectSet()")
    cmds.menuItem (i="Icons_Hider/PopUp_RemoveSet_Hider.png", l="Remove Set", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeSet()")

def HiderUI():    
    global blueButtons_Ann, commandButton, popUpButton, setHider
    
    declaringNameSpaces()
    createSettingsHider()

    if cmds.window ('windowHider', exists=True):
        cmds.deleteUI ("windowHider")
    windowHider = cmds.window ("windowHider", s=False, title= ("ANM_Hider: " + namespaceHiderForWindow), menuBar=True)
    
    cmds.menu('FileMenu', label='File')
    cmds.menuItem(l="Save Sets", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.saveSetsHider()")
    cmds.menuItem(l="Load Sets", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.LoadSetsHider()")    
    cmds.menu('HelpMenu', label='Help' )
    cmds.menuItem( l='Video Tutorial', c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.launchtutorial()")
    cmds.menuItem( l='Contact', c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.contactWindow()")
    cmds.menuItem( l='About version', c="import animeow_maya_toolboard_v02.core.anm_hider as fh; print(fh.versionHider),")

    cmds.rowColumnLayout (numberOfColumns = 11)
    
    cmds.iconTextButton ('Edit_Modebutton', i="Icons_Hider/Contract_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.toggleEditMode()", ann=editMode_Ann)
    
    setHider = All_Sets_Hider
    removeNameSpace()
    cmds.iconTextButton ( (setHider + "button"),
    ann=allSets_Ann, commandRepeatable=True, i=("Icons_Hider/" + setHider + ".png"),
    c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.ShowOrHideAllSetsButton()") 
    cmds.popupMenu(postMenuCommand = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.All_Sets_Hider")
    cmds.menuItem (i="Icons_Hider/PopUp_RemoveSet_Hider.png", l="Empty Sets Body", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeAllBodySets()")
    cmds.menuItem (i="Icons_Hider/PopUp_RemoveSet_Hider.png", l="Empty Sets Extras", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.removeAllExtraSets()")
    cmds.menuItem (i="Icons_Hider/PopUp_SelectSet_Hider.png", l="Select All Sets", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; cmds.select(fh.All_Sets_Hider)")
    
    setHider = Head_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Head_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Head_Hider"
    buttonWindowHider()
    
    setHider = Torso_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Torso_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Torso_Hider"
    buttonWindowHider()
    
    setHider = Arm_R_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Arm_R_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Arm_R_Hider"
    buttonWindowHider()
    
    setHider = Arm_L_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Arm_L_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Arm_L_Hider"
    buttonWindowHider()
    
    setHider = Leg_R_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Leg_R_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Leg_R_Hider"
    buttonWindowHider()
    
    setHider = Leg_L_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Leg_L_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Leg_L_Hider"
    buttonWindowHider()
    
    setHider = Extra_One_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_One_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_One_Hider"
    buttonWindowHider()
       
    setHider = Extra_Two_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_Two_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_Two_Hider"
    buttonWindowHider()
    
    setHider = Extra_Three_Hider
    commandButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_Three_Hider; fh.showOrHideButton()"
    popUpButton = "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.setHider = fh.Extra_Three_Hider"
    buttonWindowHider()
    
    # Utilities
    cmds.iconTextButton (i="Icons_Hider/Unlock_Hider.png", c='import animeow_maya_toolboard_v02.core.anm_hider as fh; cmds.warning(fh.rightClickToSeeButtons_Ann),', ann=rightClickToSeeButtons_Ann)
    cmds.popupMenu()
    cmds.menuItem(i="Icons_Hider/Unlock_Hider.png", l="Unlock All Visible", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.unlockAllVisible()", ann=unlockAllVis_Ann)
    cmds.menuItem(i="Icons_Hider/Unlock_Hider.png", l="Unlock All Visible Meshes", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.unlockAllVismeshes()", ann=unlockAllVisMeshes_Ann)
    cmds.menuItem(i="Icons_Hider/Lock_Hider.png", l="Lock Selection", c= "import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.lockSelection()", ann=lockSelection_Ann)

    cmds.iconTextButton (i="Icons_Hider/ObjectMode_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.objectModeHider()", ann=objectMode_Ann)
    cmds.iconTextButton ('toggleFacesNurbsCurve', i="Icons_Hider/Only_Faces_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.switchPolyOrNurbsSel()",ann=switchPolyOrNurbsCurves_Ann)
    cmds.popupMenu()
    cmds.menuItem(i="Icons_Hider/PolyColorSel_Red_Hider.png",l="Poly color selection Red", c= "cmds.displayColor ('polyFace', 13, active= True)")
    cmds.menuItem(i="Icons_Hider/PolyColorSel_Green_Hider.png", l="Poly color selection Green", c="cmds.displayColor ('polyFace', 14, active= True)")
    cmds.menuItem(i="Icons_Hider/PolyColorSel_Default_Hider.png", l="Poly color selection default", c="cmds.displayColor ('polyFace', 21, active= True)")
    
    cmds.iconTextButton (i="Icons_Hider/Grow_Hider.png", c="cmds.polySelectConstraint (pp=1)", commandRepeatable=True, ann=grow_Ann)
    cmds.iconTextButton (i="Icons_Hider/Shrink_Hider.png", c="cmds.polySelectConstraint (pp=2)", commandRepeatable=True, ann=shrink_Ann)
    cmds.iconTextButton (i="Icons_Hider/Template_Line_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.SelectTemplateLineWindow()", ann=templateLine_Ann)
    cmds.iconTextButton (i="Icons_Hider/Mirror_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.mirrorHider()", ann=mirrorButtons_Ann)
    
    cmds.iconTextButton (i="Icons_Hider/Show_All_Hidden_Faces_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.checkAllSets()", ann=checkAllSets_Ann)
    cmds.popupMenu()
    cmds.menuItem(l="Isolate mode", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.checkAllSetsIsolate()", ann= ( checkAllSets_Ann + ' but isolating every set') )
    
    cmds.iconTextButton (i="Icons_Hider/Extra_Functions_Hider.png",  c='import animeow_maya_toolboard_v02.core.anm_hider as fh; cmds.warning(fh.rightClickToSeeButtons_Ann),', ann=rightClickToSeeButtons_Ann)
    cmds.popupMenu('extraFunctions')
    cmds.menuItem(l="Show all hidden faces in the scene", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.showAllHiddenFaces()")
    
    cmds.iconTextButton (i="Icons_Hider/Remove_All_Hider.png", c="import animeow_maya_toolboard_v02.core.anm_hider as fh; fh.confirmRemoveAllHider()",ann=deleteAll_Ann)

    cmds.setParent('..')
    cmds.showWindow( windowHider )    
    checkEditMode()
    checkAllIconSets()

def show_hider():
    """Hàm khởi chạy chính từ Animeow Toolboard"""
    setup_icons_path()
    HiderUI()
