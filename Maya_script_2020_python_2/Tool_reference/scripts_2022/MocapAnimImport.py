from maya import OpenMayaUI
from maya import OpenMayaAnim
from maya import cmds
from PySide import QtCore,QtGui
import shiboken
import pickle
import functools
import os
import re
import copy
import shutil
from collections import OrderedDict

        if(not cmds.formLayout('poseMainFL_ps',q=1,ex=1)):
            return
        old=cmds.textField('nameSpaceTF_ps',q=1,tx=1)
        itemList=cmds.popupMenu('nameSpacePM_ps',q=1,ia=1)
        if(itemList):
            for i in itemList:
                cmds.deleteUI(i)

        self.nsList=self.getExistsNameSpace()
        for i in self.nsList:
            cmds.menuItem(l=i,p='nameSpacePM_ps',c=functools.partial(self.setCurrentNameSpace,i))
class FAnimImportExport():
    def __init__(self,rootPath='E:/myCode/sdd_bodyRigging/'):
        self.rootPath=rootPath
        self.filesPath=self.rootPath+'files/JMap/'
        self.animClipData=None
        
    def setupUI(self):
        self.rangeTypeChange()        

    def openMocapFbx(self,*args):
        filePath=cmds.fileDialog2(ff='.fbx(*.fbx)',fm=1)
        if(filePath==None):return
        fbxPath=filePath[0]
        cmds.textFieldGrp('mocapFbxFileTFG_at',e=1,tx=fbxPath)

        basePath=os.path.dirname(fbxPath)
        fileName=os.path.basename(fbxPath)
        saveName,saveExt=os.path.splitext(fileName)
        animPath=os.path.join(basePath,saveName+'.sanim')
        if(os.path.exists(animPath)):
            cmds.button('saveMocapeAnimB_at',e=1,l='ReSave')
            cmds.button('importMocapAnimB_at',e=1,en=1)
            cmds.textFieldGrp('mocapAnimFileTFG_at',e=1,tx=animPath)
            with open(animPath,'r') as fileHandle:
                self.animClipData=pickle.load(fileHandle)
            
        else:
            self.animClipData=None
            cmds.file(filePath,f=1,ignoreVersion=1,typ='FBX',o=1)
            cmds.button('saveMocapeAnimB_at',e=1,l='Save')
            cmds.button('importMocapAnimB_at',e=1,en=0)
            cmds.textFieldGrp('mocapAnimFileTFG_at',e=1,tx='')

        self.updateMocapAnimKeyNum()
            
    def updateMocapAnimKeyNum(self,*args):
        num=0
        if(self.animClipData!=None):
            num=self.animClipData['endTime']-self.animClipData['startTime']
        cmds.intField('mocapAnimKeyNum_at',e=1,v=num)

    def refreshNamespace(self):
        itemList=cmds.popupMenu('nameSpacePM_ps',q=1,ia=1)
        if(itemList):
            for i in itemList:
                cmds.deleteUI(i)

        self.nsList=self.getExistsNameSpace()
        for i in self.nsList:
            cmds.menuItem(l=i,p='nameSpacePM_ps',c=functools.partial(self.setCurrentNameSpace,i))

    
    def rangeTypeChange(self,*args):
        typ=cmds.radioButtonGrp('exportRangeTypeRBG_at',q=1,sl=1)
        if(typ==1):
            maxT=cmds.playbackOptions(q=1,max=1)
            minT=cmds.playbackOptions(q=1,min=1)
            cmds.intFieldGrp('exportStartEndIFG_at',e=1,v1=minT,v2=maxT,en1=0,en2=0)
        elif(typ==2):
            cmds.intFieldGrp('exportStartEndIFG_at',e=1,v1=0,v2=0,en1=0,en2=0)
        else:
            maxT=cmds.playbackOptions(q=1,max=1)
            minT=cmds.playbackOptions(q=1,min=1)
            cmds.intFieldGrp('exportStartEndIFG_at',e=1,v1=minT,v2=maxT,en1=1,en2=1)

    def loadSelectionToList(self,*args):
        cmds.textScrollList('animCtrlListTSL_at',e=1,ra=1)
        sel=cmds.ls(sl=1)
        for i in sel:
            cmds.textScrollList('animCtrlListTSL_at',e=1,a=i)
        self.updateExportCtrlNum()
    def addSelectionToList(self,*args):
        allI=cmds.textScrollList('animCtrlListTSL_at',q=1,ai=1)
        sel=cmds.ls(sl=1)
        for i in sel:
            if(allI==None or i not in allI ):
                cmds.textScrollList('animCtrlListTSL_at',e=1,a=i)
        self.updateExportCtrlNum()
    def removeCtrlFromList(self,*args):
        allI=cmds.textScrollList('animCtrlListTSL_at',q=1,ai=1)
        selI=cmds.textScrollList('animCtrlListTSL_at',q=1,si=1)
        if(selI==None or allI==None):
            return
        cmds.textScrollList('animCtrlListTSL_at',e=1,ra=1)    
        for i in allI:
            if(i not in selI):
                cmds.textScrollList('animCtrlListTSL_at',e=1,a=i)
        self.updateExportCtrlNum()
    def updateExportCtrlNum(self,*args):
        allI=cmds.textScrollList('animCtrlListTSL_at',q=1,ai=1)
        if(allI==None):
            num=0
        else:
            num=len(allI)
        cmds.text('ceCtrlNumT_at',e=1,l='%s'%num)


    def getMFnAnimCurve(self,animName):
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(animName)
        animObj = OpenMaya.MObject()
        selection_list.getDependNode(0, animObj)
        return OpenMayaAnim.MFnAnimCurve(animObj)

    def getAnimCurveData(self,animCurveNodeName,sign):
        animCurveData={}
        animCurveData['nodeType']=cmds.objectType(animCurveNodeName)
        animCurveData['preInfinity']=cmds.getAttr(animCurveNodeName+'.preInfinity')
        animCurveData['postInfinity']=cmds.getAttr(animCurveNodeName+'.postInfinity')
        util=OpenMaya.MScriptUtil()
        util.createFromDouble(0.0)
        
        # animCurveNodeName='Hips_translateY'
        animCurve=self.getMFnAnimCurve(animCurveNodeName)
        keyList=[]
        for i in range(animCurve.numKeys()):
            keyTime=animCurve.time(i).value()
            keyValue=animCurve.value(i)*sign
            keyInTangentType=animCurve.inTangentType(i)
            keyOutTangentType=animCurve.outTangentType(i)
            keyTangentsLocked=animCurve.tangentsLocked(i)
            keyWeightsLocked=animCurve.weightsLocked(i)
            keyIsBreakdown=animCurve.isBreakdown(i)
            keyInAngle=OpenMaya.MAngle()
            keyInWeight=util.asDoublePtr()
            animCurve.getTangent(i, keyInAngle, keyInWeight, True)
            keyInAngle=keyInAngle.value()*sign
            keyInWeight=util.getDouble(keyInWeight)

            keyOutAngle=OpenMaya.MAngle()
            keyOutWeight=util.asDoublePtr()
            animCurve.getTangent(i, keyOutAngle, keyOutWeight, False)

            keyOutAngle=keyOutAngle.value()*sign
            keyOutWeight=util.getDouble(keyOutWeight)

            curKey=(keyTime,keyValue,keyInTangentType,keyOutTangentType,keyTangentsLocked,keyWeightsLocked,keyIsBreakdown,keyInAngle,keyInWeight,keyOutAngle,keyOutWeight)
            keyList.append(curKey)

    
        animCurveData['keys']=keyList
        return animCurveData

    def getAnimTimeRange(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz']
        for attr in attrList:
            animCurveNodeName=cmds.findKeyframe(obj,c=1,at=attr)
            if(animCurveNodeName==None):
                continue
            animCurveNodeName=animCurveNodeName[0]
            animCurve=self.getMFnAnimCurve(animCurveNodeName)
            minT=animCurve.time(0).value()
            maxT=animCurve.time(animCurve.numKeys()-1).value()
            return minT,maxT



    def saveMocapAnimToFile(self,*args):
        filePath=self.filesPath+'mocapAnimExport.jmap'
        with open(filePath,'r') as fileHandle:
            outJntData=OrderedDict(pickle.load(fileHandle))
        

        hipJnt=outJntData.keys()[0]
        print hipJnt
        if(not cmds.objExists(hipJnt)):
            raise
        minT,maxT=self.getAnimTimeRange(hipJnt)

        hipTmepJnt=cmds.rename(hipJnt,hipJnt+'_temp')

        hipHelpLoc=cmds.group(em=1,n=hipJnt)
        hipHelpLocGrp=cmds.group(hipHelpLoc,n=hipJnt+'_grp')
        cmds.delete(cmds.parentConstraint('Spine',hipHelpLocGrp))
        con=cmds.parentConstraint(hipTmepJnt,hipHelpLoc,mo=1)
        cmds.bakeResults(hipHelpLoc,at=['tx','ty','tz','rx','ry','rz'],t=(minT,maxT),sb=1,pok=1)
        cmds.delete(con)

        self.animClipData={}
        self.animClipData['startTime']=minT
        self.animClipData['endTime']=maxT

        animData={}
        for jnt in outJntData:
            if(outJntData[jnt]==None):
                continue
            ctrl=outJntData[jnt]['fkCtrl']
            remapList=outJntData[jnt]['remap']
            if(not cmds.objExists(jnt)):
                raise

            attrListData={}
            for attr,mapAttr,sign in remapList:
                isLock=cmds.getAttr(jnt+'.'+attr,l=1)
                if(isLock):
                    continue
                animCurveNodeName=cmds.findKeyframe(jnt,c=1,at=attr)
                if(animCurveNodeName==None):
                    continue
                attrListData[mapAttr]=self.getAnimCurveData(animCurveNodeName[0],sign)
            animData[ctrl]=attrListData

        self.animClipData['animData']=animData

        fbxPath=cmds.textFieldGrp('mocapFbxFileTFG_at',q=1,tx=1)
        if(fbxPath==''):
            fbxPath=cmds.file(q=1,exn=1)

        basePath=os.path.dirname(fbxPath)
        fileName=os.path.basename(fbxPath)
        saveName,saveExt=os.path.splitext(fileName)
        fullPath=os.path.join(basePath,saveName+'.sanim')

        with open(fullPath,'w') as fileHandle:
            pickle.dump(self.animClipData,fileHandle)
        cmds.textFieldGrp('mocapAnimFileTFG_at',e=1,tx=fullPath)
        self.updateMocapAnimKeyNum()

    def importMocapAnim(self,*args):
        animData=self.animClipData['animData']
        for ctrl in animData:
            attrListData=animData[ctrl]
            for attr in attrListData:
                if(not cmds.objExists(ctrl)):
                    continue
                isKeyable=cmds.getAttr(ctrl+'.'+attr,k=1)
                if(not isKeyable):
                    continue
                animCurveData=attrListData[attr]
                self.setAnimCurveData(ctrl,attr,animCurveData)


    def openAnimFile(self,*args):
        path=cmds.fileDialog2(ff='Animation File .sanim(*.sanim)',fm=1)
        if(path==None):return
        filePath=path[0]
        cmds.textFieldButtonGrp('animFileTFBG_at',e=1,tx=filePath)
        filePath=cmds.textFieldButtonGrp('animFileTFBG_at',q=1,tx=1)
        with open(filePath,'r') as fileHandle:
            self.animClipData=pickle.load(fileHandle)

    def importAnim(self,*args):
        animData=self.animClipData['animData']
        for ctrl in animData:
            attrListData=animData[ctrl]
            for attr in attrListData:
                if(not cmds.objExists(ctrl)):
                    continue
                isKeyable=cmds.getAttr(ctrl+'.'+attr,k=1)
                if(not isKeyable):
                    continue
                animCurveData=attrListData[attr]
                self.setAnimCurveData(ctrl,attr,animCurveData)


    def setAnimCurveData(self,ctrl,attr,animCurveData):
        animCurveNodeName=cmds.findKeyframe(ctrl,c=1,at=attr)
        if(animCurveNodeName==None):
            animCurveNodeName=cmds.createNode(animCurveData['nodeType'],n=ctrl+'_'+attr)
            cmds.connectAttr(animCurveNodeName+'.o',ctrl+'.'+attr)
        else:
            animCurveNodeName=animCurveNodeName[0]

        cmds.setAttr(animCurveNodeName+'.preInfinity',animCurveData['preInfinity'])
        cmds.setAttr(animCurveNodeName+'.postInfinity',animCurveData['postInfinity'])

        animCurve=self.getMFnAnimCurve(animCurveNodeName)
        keyList=animCurveData['keys']
        for i in range(len(keyList)):
            curKey=keyList[i]
            keyTime,keyValue,keyInTangentType,keyOutTangentType,keyTangentsLocked,keyWeightsLocked,keyIsBreakdown,keyInAngle,keyInWeight,keyOutAngle,keyOutWeight=curKey
            idx=animCurve.addKey(OpenMaya.MTime(keyTime),keyValue,keyInTangentType,keyOutTangentType)
            animCurve.setTangentsLocked(idx,keyTangentsLocked)
            animCurve.setWeightsLocked(idx,keyWeightsLocked)
            animCurve.setIsBreakdown(idx,keyIsBreakdown)
            animCurve.setTangent(idx,OpenMaya.MAngle(keyInAngle),keyInWeight,True)
            animCurve.setTangent(idx,OpenMaya.MAngle(keyOutAngle),keyOutWeight,False)


    def saveAnimToFile(self):
        allCtrl=cmds.ls(sl=1)
        animData={}
        for jnt in allCtrl:
            exportAttrList=cmds.listAttr('Hips',k=1)
            for attr in exportAttrList:
                isLock=cmds.getAttr(jnt+'.'+attr,l=1)
                if(isLock):
                    continue
                animCurveNodeName=cmds.findKeyframe(jnt,c=1,at=attr)
                if(animCurveNodeName==None):
                    continue
            animData[attr]=self.getAnimCurveData(animCurveNodeName)
FAnimModule=FAnimImportExport()
self=FAnimModule
