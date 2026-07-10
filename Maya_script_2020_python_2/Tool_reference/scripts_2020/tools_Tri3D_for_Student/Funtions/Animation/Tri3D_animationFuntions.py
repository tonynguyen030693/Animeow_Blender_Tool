import maya.cmds as cmds
import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
import os
import random
from PySide2 import QtGui



################################################################ value
scale_value = 1.0


################################################################ Key
def copyKey(*arg):
    selected_objects = pm.ls(selection=True)
    
    if selected_objects:
        current_time = pm.currentTime(query=True)
        
        for obj in selected_objects:
            pm.copyKey(obj, time=(current_time, current_time), option="curve")

def pasteKey(*arg):
    selected_objects = pm.ls(selection=True)
    
    if selected_objects:
        current_time = pm.currentTime(query=True)
        
        for obj in selected_objects:
            pm.pasteKey(obj, time=(current_time, current_time), option="merge")

def cutKey(*arg):
    selected_objects = pm.ls(selection=True)
    
    if selected_objects:
        current_time = pm.currentTime(query=True)
        
        for obj in selected_objects:
            pm.cutKey(obj, time=(current_time, current_time), clear=True)

def resetKey(*args):
    selected_objects = pm.ls(selection=True)
    
    if selected_objects:
        current_time = pm.currentTime(query=True)
        
        for obj in selected_objects:
            pm.setKeyframe(obj, time=(current_time, current_time), attribute=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'], value=0)

################################################################ graph editor

def TangentsAuto(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)

    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            mel.eval('TangentsAuto;')
            mel.eval('doKeyTangent "-e -itt auto -ott auto" graphEditor1GraphEd "useSmoothness bufferCurve";')
            mel.eval('keyTangent -e -itt auto -ott auto;')
            mel.eval('doUpdateTangentFeedback;')
        else:
            cmds.warning("lam gi co key ma set bro")

def TangentsSpline(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)

    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            mel.eval('TangentsSpline;')
            mel.eval('doKeyTangent "-e -itt spline -ott spline" graphEditor1GraphEd "useSmoothness bufferCurve";')
            mel.eval('keyTangent -e -itt spline -ott spline;')
            mel.eval('doUpdateTangentFeedback;')
        else:
            cmds.warning("lam gi co key ma set bro")
def TangentsClamped(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)

    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            mel.eval('TangentsClamped;')
            mel.eval('doKeyTangent "-e -itt clamped -ott clamped" graphEditor1GraphEd "useSmoothness bufferCurve";')
            mel.eval('keyTangent -e -itt clamped -ott clamped;')
            mel.eval('doUpdateTangentFeedback;')
        else:
            cmds.warning("lam gi co key ma set bro")
def TangentsLinear(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)

    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            mel.eval('TangentsLinear;')
            mel.eval('doKeyTangent "-e -itt linear -ott linear" graphEditor1GraphEd "useSmoothness bufferCurve";')
            mel.eval('keyTangent -e -itt linear -ott linear;')
            mel.eval('doUpdateTangentFeedback;')
        else:
            cmds.warning("lam gi co key ma set bro")
def TangentsFlat(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)

    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            mel.eval('TangentsFlat;')
            mel.eval('doKeyTangent "-e -itt flat -ott flat" graphEditor1GraphEd "useSmoothness bufferCurve";')
            mel.eval('keyTangent -e -itt flat -ott flat;')
            mel.eval('doUpdateTangentFeedback;')
        else:
            cmds.warning("lam gi co key ma set bro")

################################################################ move key pro
def useSEK(*arg):
    qUse= cmds.checkBox('UseSEK', q= 1, v= 1)
    if qUse:
        cmds.textField('startKey', e= 1, ed= 1, tx= int(cmds.currentTime(q= 1)))
        cmds.textField('endKey', e= 1, ed= 1, tx= int(cmds.playbackOptions(q= 1, aet= 1)))
    else:
        cmds.textField('startKey', e= 1, ed= 0, tx= '')
        cmds.textField('endKey', e= 1, ed= 0, tx= '')  

def selectCtrl(*arg):
    getSl= cmds.ls(sl= 1)
    qNameTx= ''
    qSelectAll= cmds.textField('selectAll', q= 1, tx= 1)
    
    if not getSl:
        cmds.textField('selectCtrl', e= 1, tx= '')
    else:
        cmds.textField('selectCtrl', e= 1, tx= '')
        cmds.textField('selectAll', e= 1, tx= '')
        for i in getSl:
            qNameTx= cmds.textField('selectCtrl', q= 1, tx= 1)
            cmds.textField('selectCtrl', e= 1, tx= qNameTx + ' ' + i)

def selectAll(*arg):
    if cmds.textField('selectAll', q= 1, tx= 1):
        cmds.textField('selectAll', e= 1, tx= '')
    else:
        cmds.textField('selectCtrl', e= 1, tx= '')
        getAnicmdsurve= cmds.ls(type= 'anicmdsurve')
        cmds.select(getAnicmdsurve, r= 1)
        cmds.textField('selectAll', e= 1, tx= 'Selected All Anim')
    
def butt_startKey(*arg):
    qUse= cmds.checkBox('UseSEK', q= 1, v= 1)
    if qUse:
        qCTime= cmds.currentTime(q= 1)
        cmds.textField('startKey', e= 1, tx= int(qCTime))

def butt_endKey(*arg):
    qUse= cmds.checkBox('UseSEK', q= 1, v= 1)
    if qUse:
        qCTime= cmds.currentTime(q= 1)
        cmds.textField('endKey', e= 1, tx= int(qCTime))

def butt_moveForward(*arg):
    getSK= cmds.textField('startKey', q= 1, tx= 1)
    getEK= cmds.textField('endKey', q= 1, tx= 1)
    getNK= cmds.intSliderGrp('numbersKey', q= 1, v= 1)
    qUse= cmds.checkBox('UseSEK', q= 1, v= 1)
    
    if not qUse:
        if (cmds.textField('selectAll', q= 1, tx= 1) == '') and (cmds.textField('selectCtrl', q= 1, tx= 1) == '' ):
            raise RuntimeError('You must select Ctrl !!!')
            
        elif cmds.textField('selectAll', q= 1, tx= 1):
            qCTime= cmds.currentTime(q= 1)
            getAnicmdsurve= cmds.ls(type= 'anicmdsurve')
            cmds.select(getAnicmdsurve)
            for i in getAnicmdsurve:
                cmds.keyframe(i, e=1, relative= 1, t= (qCTime,999999), tc= getNK)
        else:
            qCTime= cmds.currentTime(q= 1)
            getName= cmds.textField('selectCtrl', q= 1, tx= 1)
            splitName= getName.split()
        
            for i in splitName:
                cmds.keyframe(i, e=1, relative= 1, t= (qCTime,999999), tc= getNK)
    
    else:
        if (cmds.textField('selectAll', q= 1, tx= 1) == '') and (cmds.textField('selectCtrl', q= 1, tx= 1) == '' ):
            print ('Select Ctrl, please!!!')
        
        elif cmds.textField('selectAll', q= 1, tx= 1):
            print ('elif')
            getAnicmdsurve= cmds.ls(type= 'anicmdsurve')
            cmds.select(getAnicmdsurve)
            for i in getAnicmdsurve:
                cmds.keyframe(i, e=1, relative= 1, t= (getSK,getEK), tc= getNK)
            #cmds.textField('startKey', e= 1, tx= float(getSK) + float(getNK))
            cmds.textField('endKey', e= 1, tx= float(getEK) + float(getNK))
        else:
            qCTime= cmds.currentTime(q= 1)
            getName= cmds.textField('selectCtrl', q= 1, tx= 1)
            splitName= getName.split()
        
            for i in splitName:
                cmds.keyframe(i, e=1, relative= 1, t= (getSK,getEK), tc= getNK)
            #cmds.textField('startKey', e= 1, tx= float(getSK) + float(getNK))
            cmds.textField('endKey', e= 1, tx= float(getEK) + float(getNK))

def butt_moveBackward(*arg):
    getSK= cmds.textField('startKey', q= 1, tx= 1)
    getEK= cmds.textField('endKey', q= 1, tx= 1)
    getNK= cmds.intSliderGrp('numbersKey', q= 1, v= 1)
    qUse= cmds.checkBox('UseSEK', q= 1, v= 1)
    
    if not qUse:
        if (cmds.textField('selectAll', q= 1, tx= 1) == '') and (cmds.textField('selectCtrl', q= 1, tx= 1) == '' ):
            raise RuntimeError('You must select Ctrl !!!')
            
        elif cmds.textField('selectAll', q= 1, tx= 1):
            qCTime= cmds.currentTime(q= 1)
            getAnicmdsurve= cmds.ls(type= 'anicmdsurve')
            cmds.select(getAnicmdsurve)
            for i in getAnicmdsurve:
                cmds.keyframe(i, e=1, relative= 1, t= (qCTime,999999), tc= - getNK)
        else:
            qCTime= cmds.currentTime(q= 1)
            getName= cmds.textField('selectCtrl', q= 1, tx= 1)
            splitName= getName.split()
        
            for i in splitName:
                cmds.keyframe(i, e=1, relative= 1, t= (qCTime,999999), tc= - getNK)
    
    else:
        if (cmds.textField('selectAll', q= 1, tx= 1) == '') and (cmds.textField('selectCtrl', q= 1, tx= 1) == '' ):
            print ('Select Ctrl, please!!!')
            
        elif cmds.textField('selectAll', q= 1, tx= 1):
            getAnicmdsurve= cmds.ls(type= 'anicmdsurve')
            cmds.select(getAnicmdsurve)
            for i in getAnicmdsurve:
                cmds.keyframe(i, e=1, relative= 1, t= (getSK,getEK), tc= - getNK)
            #cmds.textField('startKey', e= 1, tx= float(getSK) - float(getNK))
            cmds.textField('endKey', e= 1, tx= float(getEK) - float(getNK))
        
        else:
            getName= cmds.textField('selectCtrl', q= 1, tx= 1)
            splitName= getName.split()
            for i in splitName:
                print (i)
                cmds.keyframe(i, e=1, relative= 1, t= (getSK,getEK), tc= - getNK)
        
            #cmds.textField('startKey', e= 1, tx= float(getSK) - float(getNK))
            cmds.textField('endKey', e= 1, tx= float(getEK) - float(getNK))


################################################################ move key

def moveKeyF(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)
    time_change = float(cmds.textField('timeChangeField', query=True, text=True))
    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_visibility', add=True, keyframe=True, time=(current_time, current_time))
            cmds.keyframe(edit=True, relative=True, timeChange=time_change)
        else:
            cmds.warning("lam gi co key ma set bro")
def moveKeyB(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)
    time_change = float(cmds.textField('timeChangeField', query=True, text=True))
    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_visibility', add=True, keyframe=True, time=(current_time, current_time))
            cmds.keyframe(edit=True, relative=True, timeChange=time_change * -1)
        else:
            cmds.warning("lam gi co key ma set bro")            
def moveKeyFUi(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)
    time_change = float(cmds.textField('timeChangeField', query=True, text=True))
    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_visibility', add=True, keyframe=True, time=(current_time, current_time))
            cmds.keyframe(edit=True, relative=True, timeChange=time_change)
        else:
            cmds.warning("lam gi co key ma set bro")
def moveKeyBUi(*arg):
    selected_obj = cmds.ls(sl=True)    
    current_time = cmds.currentTime(query=True)
    time_change = float(cmds.textField('timeChangeField', query=True, text=True))
    for obj in selected_obj:  
        selected_keys = cmds.keyframe([obj +'_translateX', obj +'_translateY', obj +'_translateZ',
                                   obj +'_rotateX', obj +'_rotateY', obj +'_rotateZ',
                                   obj +'_scaleX', obj +'_scaleY', obj +'_scaleZ'],
                                  query=True, time=(current_time, current_time))                        
        if selected_keys:
            cmds.selectKey(clear=True)
            cmds.selectKey(obj +'_translateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_translateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_rotateZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleX', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleY', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_scaleZ', add=True, keyframe=True, time=(current_time, current_time))
            cmds.selectKey(obj +'_visibility', add=True, keyframe=True, time=(current_time, current_time))
            cmds.keyframe(edit=True, relative=True, timeChange=time_change * -1)
        else:
            cmds.warning("lam gi co key ma set bro")        


