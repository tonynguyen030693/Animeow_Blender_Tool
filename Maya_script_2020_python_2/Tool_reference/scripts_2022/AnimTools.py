from maya import OpenMaya,OpenMayaAnim
from maya import cmds,mel
import pickle
import functools
import os
import re
import copy
import shutil
from collections import OrderedDict
import math  

class FAnimImportExport():
    def __init__(self,rootPath='E:/myCode/sdd_bodyRigging/'):
        self.rootPath=rootPath
        self.filesPath=self.rootPath+'files/JMap/'
        self.animClipData=None

    def resetTransAttr(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        dValList=[0,0,0,0,0,0,1,1,1]
        for attr,dv in zip(attrList,dValList):
            isKeyable=cmds.getAttr(obj+'.'+attr,k=1)
           
            if(isKeyable):
                cmds.setAttr(obj+'.'+attr,dv)
            else:
                 print obj+'.'+attr

    def importMocapAnim(self,*args):
        filePath=cmds.fileDialog2(ff='.fbx(*.fbx)',fm=1)
        if(filePath==None):return
        fbxPath=filePath[0]
        cmds.textFieldGrp('mocapFbxFileTFG_at',e=1,tx=fbxPath)

        filePath=self.filesPath+'mocapAnimExport.jmap'
        with open(filePath,'r') as fileHandle:
            outJntData=OrderedDict(pickle.load(fileHandle))


        characterNS=cmds.optionMenu('mocapCharacterOM_at',q=1,v=1)
        if(characterNS==None):
            raise RuntimeError,'has not Character exists.'
        importNS='AnimImport'
        cmds.namespace(set=':')
        if(not cmds.namespace(ex=importNS)):
            cmds.namespace(add=importNS)
        cmds.namespace(set=importNS)
        

        for jnt in outJntData:
            if(outJntData[jnt]==None):
                continue
            ctrl=outJntData[jnt]['fkCtrl']
            chJnt=characterNS+jnt
            chCtrl=characterNS+ctrl
            if(cmds.objExists(chJnt) and cmds.objExists(chCtrl)):
                self.resetTransAttr(chCtrl)

        pWorld=True
        newObjMap=OrderedDict()
        for jnt in outJntData:
            if(outJntData[jnt]==None):
                continue
            ctrl=outJntData[jnt]['fkCtrl']
            chJnt=characterNS+jnt
            chCtrl=characterNS+ctrl

            if(cmds.objExists(chJnt) and cmds.objExists(chCtrl)):
                newJnt=cmds.duplicate(chJnt,po=1)[0]
                newCtrl=cmds.group(em=1,n=ctrl)
                newCtrlGrp=cmds.group(newCtrl,n=ctrl+'_zero')
                cmds.parent(newCtrlGrp,chCtrl)
                self.resetTransAttr(newCtrlGrp)
                cmds.parent(newCtrlGrp,w=1)
                con=cmds.parentConstraint(newJnt,newCtrl,mo=1)
                cmds.setAttr(con[0]+'.interpType',0)

                newObjMap[jnt]=[newJnt,newCtrl,characterNS+ctrl]
                if(pWorld):
                    if(cmds.listRelatives(newJnt,p=1)!=None):
                        cmds.parent(newJnt,w=1)
                    if(cmds.listRelatives(newJnt,p=1)!=None):
                        cmds.parent(newCtrlGrp,w=1)
                    pWorld=False
                else:
                    pJnt=cmds.listRelatives(chJnt,p=1)[0]
                    pJnt=pJnt.split(':')[-1]

                    newPJnt=newObjMap[pJnt][0]
                    newPCtrl=newObjMap[pJnt][1]
                    cmds.parent(newJnt,newPJnt)
                    cmds.parent(newCtrlGrp,newPCtrl)
        
        cmds.refresh(f=1)
        cmds.file(fbxPath,pr=1,pmt=0,op='v=0;p=17;f=0',mnc=1,ra=1,typ='FBX',i=1)
        cmds.refresh(f=1)
        rootJnt=newObjMap.items()[0][1][0]
        

        rootAnimCurve=self.findAnimCurveNone(rootJnt)
        minT=rootAnimCurve.time(0).asUnits(OpenMaya.MTime.uiUnit())
        maxT=rootAnimCurve.time(rootAnimCurve.numKeys()-1).asUnits(OpenMaya.MTime.uiUnit())
        cmds.playbackOptions(min=minT,max=maxT)
        keyNum=rootAnimCurve.numKeys()

        cmds.namespace(set=':')



        attrList=['tx','ty','tz','rx','ry','rz']
        keyAnimCurveMap=OrderedDict()
        for i in newObjMap:
            animJnt,newCtrl,chCtrl=newObjMap[i]
            for attr in attrList:
                isKeyable=cmds.getAttr(chCtrl+'.'+attr,k=1)
                if(not isKeyable):
                    continue
                animJntAnim=cmds.findKeyframe(animJnt,c=1,at=attr)
                if(animJntAnim==None):
                    continue
                typ=cmds.objectType(animJntAnim)

                animCurveNodeName=cmds.findKeyframe(chCtrl,c=1,at=attr)
                if(animCurveNodeName==None):
                    animCurveNodeName=cmds.createNode(typ,n=chCtrl+'_'+attr)
                    cmds.connectAttr(animCurveNodeName+'.o',chCtrl+'.'+attr)

                else:
                    animCurveNodeName=animCurveNodeName[0]
                keyAnimCurveMap[newCtrl+'.'+attr]=self.getMFnAnimCurve(animCurveNodeName)

        try:
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
            cmds.progressBar( gMainProgressBar,e=1,bp=1,ii=True,max=keyNum)

            for idx in range(keyNum):
                if cmds.progressBar(gMainProgressBar,q=1,ic=1):
                    break
                cmds.progressBar(gMainProgressBar,e=1,s=1,status='index: %s-%s'%(idx,keyNum))
                curT=rootAnimCurve.time(idx).asUnits(OpenMaya.MTime.uiUnit())
                cmds.currentTime(curT)
                for getAttrStr in keyAnimCurveMap:
                    animCurve=keyAnimCurveMap[getAttrStr]
                    animCurve.name()
                    val=cmds.getAttr(getAttrStr)
                    if(getAttrStr[-2:] in ['rx','ry','rz']):
                        # if(val>0):
                        #     val=val%360
                        # else:
                        #     val=val%-360+360
                        val=math.radians(val)
                    idx=animCurve.addKey(rootAnimCurve.time(idx),val)
                cmds.refresh(f=1)

        finally:
            cmds.progressBar(gMainProgressBar,e=1,ep=1)
        
        cmds.delete(cmds.namespaceInfo(importNS,lod=1))
    def setupUI(self):
        self.refreshNamespace()
        self.refreshFps()


    def refreshFps(self):
        # setfpsStr=['game','film','pal','ntsc','show','palf','ntscf','millisec','sec','min','hour','2fps','3fps','4fps','5fps','6fps','8fps','10fps','12fps','16fps','20fps','40fps','75fps','80fps','100fps','120fps','125fps','150fps','200fps','240fps','250fps','300fps','375fps','400fps','500fps','600fps','750fps','1200fps','1500fps','2000fps','3000fps','6000fps']
        orgStr=['game','film','pal','ntsc','show','palf','ntscf']
        # myStr=['15 fps','24 fps','25 fps','30 fps','48 fps','50 fps','60 fps']
        sel=cmds.currentUnit(q=1,t=1)
        if(sel in orgStr):
            idx=orgStr.index(sel)
            cmds.optionMenu('mocapFpsOM_at',e=1,sl=idx+1)

    def fpsChange(self,*args):
        orgStr=['game','film','pal','ntsc','show','palf','ntscf']
        idx=cmds.optionMenu('mocapFpsOM_at',q=1,sl=1)
        cmds.currentUnit(t=orgStr[idx-1])
        

    def refreshNamespace(self):
        itemList=cmds.optionMenu('mocapCharacterOM_at',q=1,ill=1)
        if(itemList):
            for i in itemList:
                cmds.deleteUI(i)
        self.nsList=self.getExistsNameSpace('Hips')
        for i in self.nsList:
            cmds.menuItem(l=i,p='mocapCharacterOM_at')

    def setNameSpaceFromSelection(self,*args):
        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return
        pref=sel[0].split(':')
        curNS=pref[0]+':' if(len(pref)==2) else ':'
        if(curNS in self.nsList):
            cmds.optionMenu('mocapCharacterOM_at',e=1,v=curNS)


    def getExistsNameSpace(self,obj=None):
        allNS=cmds.namespaceInfo(':',lon=1)
        allNS.append('')
        nsList=[]
        for i in allNS:
            ns=i+':'
            allChild=cmds.namespaceInfo(ns,lod=1)
            if(allChild==None):
                continue
            if(obj and not(cmds.objExists(ns+obj))):
                continue
            nsList.append(ns)
        return nsList

    def nameSpaceSelectChange(self,*args):
        ns=cmds.optionMenu('mocapCharacterOM_at',q=1,v=1)
        ddd=cmds.namespaceInfo(ns,lod=1)
        cmds.select(ddd)



    def getMFnAnimCurve(self,animName):
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(animName)
        animObj = OpenMaya.MObject()
        selection_list.getDependNode(0, animObj)
        return OpenMayaAnim.MFnAnimCurve(animObj)

    def findAnimCurveNone(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz']
        for attr in attrList:
            animCurveNodeName=cmds.findKeyframe(obj,c=1,at=attr)
            if(animCurveNodeName==None):
                continue
            animCurveNodeName=animCurveNodeName[0]
            animCurve=self.getMFnAnimCurve(animCurveNodeName)
            return animCurve
    def TransferAnimationUI(self):
        if(cmds.window('sdd_AnimToolsUI_at',q=True,ex=True)):cmds.deleteUI('sdd_AnimToolsUI_at')
        cmds.window('sdd_AnimToolsUI_at',t=u'Animtion Tools')
        cmds.columnLayout(adj=True)
        cmds.tabLayout('mainTL_at',cr=True)
        cmds.columnLayout('mocapMainCL_at',adj=True)
        cmds.frameLayout('mocapTransferFL_at',cll=False,l=u'Mocap Anim Transfer',mh=3,mw=3)
        cmds.columnLayout('mocapTransferCL_at',adj=True,rs=5)
        cmds.rowLayout('rowLayout5_at',nc=3,adj=2)
        cmds.text(w=60,l=u'Character:',al=u'right')
        cmds.optionMenu('mocapCharacterOM_at',cc=self.nameSpaceSelectChange)
        cmds.menuItem()
        cmds.menuItem()
        cmds.button(p='rowLayout5_at',w=25,h=20,l=u'<',c=self.setNameSpaceFromSelection)
        cmds.rowLayout(p='mocapTransferCL_at',nc=2)
        cmds.text(w=60,l=u'FPS:',al=u'right')
        cmds.optionMenu('mocapFpsOM_at',cc=self.fpsChange)
        cmds.menuItem(l=u'15 fps')
        cmds.menuItem(l=u'24 fps')
        cmds.menuItem(l=u'25 fps')
        cmds.menuItem(l=u'30 fps')
        cmds.menuItem(l=u'48 fps')
        cmds.menuItem(l=u'50 fps')
        cmds.menuItem(l=u'60 fps')
        cmds.textFieldGrp('mocapFbxFileTFG_at',p='mocapTransferCL_at',cw=[[1, 60]],adj=2,l=u'FBX Path:',ed=False)
        cmds.button(p='mocapTransferCL_at',h=30,l=u'Import',c=self.importMocapAnim)
        self.setupUI()
        cmds.tabLayout('mainTL_at',e=1,tli=[[1, u'Mocap Anim']])
        cmds.showWindow('sdd_AnimToolsUI_at')

# if __name__ == '__main__':
#     FAnimModule=FAnimImportExport(rootPath).TransferAnimationUI()
#     FAnimModule.TransferAnimationUI()
#     self=FAnimModule
