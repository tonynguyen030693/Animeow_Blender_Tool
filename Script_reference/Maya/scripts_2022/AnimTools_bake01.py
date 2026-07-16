from maya import OpenMaya,OpenMayaAnim
from maya import cmds
import pickle
import functools
import os
import re
import copy
import shutil
from collections import OrderedDict

class FAnimImportExport():
    def __init__(self,rootPath='E:/myCode/sdd_bodyRigging/'):
        self.rootPath=rootPath
        self.filesPath=self.rootPath+'files/JMap/'
        self.animClipData=None

    def resetTransAttr(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        dValList=[0,0,0,0,0,0,1,1,1]
        for attr,dv in zip(attrList,dValList):
            cmds.setAttr(obj+'.'+attr,dv)

    def importMocapAnim(self,*args):
        tt=''
        filePath=cmds.fileDialog2(ff='.fbx(*.fbx)',fm=1)
        if(filePath==None):return
        fbxPath=filePath[0]
        cmds.textFieldGrp('mocapFbxFileTFG_at',e=1,tx=fbxPath)
        self.refreshNamespace()

        filePath=self.filesPath+'mocapAnimExport.jmap'
        with open(filePath,'r') as fileHandle:
            outJntData=OrderedDict(pickle.load(fileHandle))

        characterNS=':'
        importNS='AnimImport'
        cmds.namespace(set=':')
        if(not cmds.namespace(ex=importNS)):
            cmds.namespace(add=importNS)
        cmds.namespace(set=importNS)
        pWorld=True

        newObjMap=OrderedDict()
        for jnt in outJntData:
            if(outJntData[jnt]==None):
                continue
            ctrl=outJntData[jnt]['fkCtrl']

            if(cmds.objExists(characterNS+jnt) and cmds.objExists(characterNS+ctrl)):
                newJnt=cmds.duplicate(characterNS+jnt,po=1)[0]
                newCtrl=cmds.group(em=1,n=ctrl)
                newCtrlGrp=cmds.group(newCtrl,n=ctrl+'_zero')
                cmds.parent(newCtrlGrp,characterNS+ctrl)
                self.resetTransAttr(newCtrlGrp)
                cmds.parent(newCtrlGrp,w=1)
                con=cmds.parentConstraint(newJnt,newCtrl,mo=1)
                cmds.setAttr(con[0]+'.interpType',0)

                newObjMap[jnt]=[newJnt,newCtrl,newCtrlGrp,characterNS+ctrl]
                if(pWorld):
                    if(cmds.listRelatives(newJnt,p=1)!=None):
                        cmds.parent(newJnt,w=1)
                    if(cmds.listRelatives(newJnt,p=1)!=None):
                        cmds.parent(newCtrlGrp,w=1)
                    pWorld=False
                else:
                    pJnt=cmds.listRelatives(newJnt,p=1)[0]
                    newPJnt=newObjMap[pJnt][0]
                    newPCtrl=newObjMap[pJnt][1]
                    cmds.parent(newJnt,newPJnt)
                    cmds.parent(newCtrlGrp,newPCtrl)

        cmds.file(fbxPath,pr=1,op='v=0;p=17;f=0',mnc=0,ra=1,typ='FBX',i=1)
        
        rootJnt=newObjMap.items()[0][1][0]
        

        rootAnimCurve=self.findAnimCurveNone(rootJnt)
        minT=rootAnimCurve.time(0).value()
        maxT=rootAnimCurve.time(rootAnimCurve.numKeys()-1).value()
        cmds.playbackOptions(min=minT,max=maxT)
        keyNum=rootAnimCurve.numKeys()

        cmds.namespace(set=':')

        import time
        st=time.time()
        attrList=['tx','ty','tz','rx','ry','rz']
        for idx in range(keyNum):
            curT=animCurve.time(idx).value()
            cmds.currentTime(curT)
            for jnt in newObjMap:
                newJnt,newCtrl,newCtrlGrp,chCtrl=newObjMap[jnt]
                for attr in attrList:
                    isKeyable=cmds.getAttr(chCtrl+'.'+attr,k=1)
                    if(not isKeyable):
                        continue
                    val=cmds.getAttr(newCtrl+'.'+attr)
                    cmds.setAttr(chCtrl+'.'+attr,val)
                    cmds.setKeyframe(chCtrl+'.'+attr)
            cmds.refresh(f=1)
        print '----------------',time.time()-st
        cmds.delete(cmds.namespaceInfo(importNS,lod=1))

        attrList=['tx','ty','tz','rx','ry','rz']
        keyAnimCurveMap=OrderedDict()
        for jnt in newObjMap:
            newJnt,newCtrl,newCtrlGrp,chCtrl=newObjMap[jnt]
            for attr in attrList:
                isKeyable=cmds.getAttr(chCtrl+'.'+attr,k=1)
                if(not isKeyable):
                    continue
                newJntAnim=cmds.findKeyframe(newJnt,c=1,at=attr)
                if(newJntAnim==None):
                    continue
                typ=cmds.objectType(newJntAnim)

                animCurveNodeName=cmds.findKeyframe(chCtrl,c=1,at=attr)
                if(animCurveNodeName==None):
                    animCurveNodeName=cmds.createNode(typ,n=chCtrl+'_'+attr)
                    cmds.connectAttr(animCurveNodeName+'.o',chCtrl+'.'+attr)

                else:
                    animCurveNodeName=animCurveNodeName[0]
                keyAnimCurveMap[newCtrl+'.'+attr]=self.getMFnAnimCurve(animCurveNodeName)



        
        for idx in range(keyNum):
            curT=rootAnimCurve.time(idx).value()
            cmds.currentTime(curT)
            for getAttrStr in keyAnimCurveMap:
                animCurve=keyAnimCurveMap[getAttrStr]
                val=cmds.getAttr(getAttrStr)
                idx=animCurve.addKey(OpenMaya.MTime(curT),1)
                dv=animCurve.value(idx)
                animCurve.setValue(idx,val)

            cmds.refresh(f=1)
        



    def refreshNamespace(self):
        itemList=cmds.optionMenu('mocapCharacterOM_at',q=1,ill=1)
        if(itemList):
            for i in itemList:
                cmds.deleteUI(i)
        self.nsList=self.getExistsNameSpace()
        for i in self.nsList:
            cmds.menuItem(l=i,p='mocapCharacterOM_at')
            

    def getExistsNameSpace(self):
        allNS=cmds.namespaceInfo(lon=1)
        nsList=[]
        for i in allNS:
            if(cmds.namespaceInfo(i,lod=1)):
                nsList.append(i+':')
        nsList.insert(0,':')
        return nsList

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

    def findAnimCurveNone(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz']
        for attr in attrList:
            animCurveNodeName=cmds.findKeyframe(obj,c=1,at=attr)
            if(animCurveNodeName==None):
                continue
            animCurveNodeName=animCurveNodeName[0]
            animCurve=self.getMFnAnimCurve(animCurveNodeName)
            return animCurve

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
