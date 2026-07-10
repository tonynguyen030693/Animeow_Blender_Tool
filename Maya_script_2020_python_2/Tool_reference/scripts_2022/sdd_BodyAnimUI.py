from maya import OpenMayaUI,OpenMaya,OpenMayaAnim
from maya import cmds,mel
from PySide import QtCore,QtGui
import shiboken
import pickle
import functools
from collections import OrderedDict
import math  


def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)

class BPickButton(QtGui.QPushButton):
    def __init__(self,parent=None):
        super(BPickButton, self).__init__(parent)
        self.isSelected=False
        self.updateBtnColor()
    def updateBtnColor(self):
        if(self.isSelected):
            self.setStyleSheet("background-color: rgba(255, 155,0 ,255);")
        else:
            self.setStyleSheet("background-color: rgba(0, 155, 255,230);")
    def setSelect(self,isSel):
        self.isSelected=isSel
        self.updateBtnColor()
    # def mouseDoubleClickEvent(self,event):
    #     print event.ignore()


class BPickWidget(QtGui.QWidget):
    def __init__(self,parent=None,rootPath=''):
        self.iconPath=rootPath+'icons/'
        self.rootPath=rootPath
        QtGui.QWidget.__init__(self,parent)
        self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.ShiftModifier=False
        self.ControlModifier=False
        self.setFixedSize(454,604)
        self.setObjectName('BPickWidget')

        self.bgLab = QtGui.QLabel(self)
        self.bgLab.setGeometry(QtCore.QRect(2, 2, 450, 600))
        self.bgLab.setText("")
        self.bgLab.setTextFormat(QtCore.Qt.PlainText)
        self.bgLab.setPixmap(QtGui.QPixmap(self.iconPath+"bodyBG.jpg"))
        self.bgLab.setObjectName("label")


        self.namesCB = QtGui.QComboBox(self)
        self.namesCB.setGeometry(QtCore.QRect(14, 6, 425, 22))
        self.namesCB.setObjectName("namespace_cb")
        


        self.aotunamesCB = QtGui.QCheckBox('Auto NameSpace',self)
        self.aotunamesCB.setGeometry(QtCore.QRect(16, 30, 150, 22))
        self.aotunamesCB.setObjectName("aotuNamespace_CB")
        self.aotunamesCB.setChecked(True)

        self.ikfkSeamlessCB = QtGui.QCheckBox('IkFk seamless switch',self)
        self.ikfkSeamlessCB.setGeometry(QtCore.QRect(16, 50, 150, 22))
        self.ikfkSeamlessCB.setObjectName("ikfkSeamless_CB")
        self.ikfkSeamlessCB.setChecked(True)


        filePath=self.rootPath+'/files/BodyUIData.uidata'
        with open(filePath,'r') as fileHandle:
            BodyUIData=pickle.load(fileHandle)

        filePath=self.rootPath+'/files/JMap/mocapAnimExport.jmap'
        with open(filePath,'r') as fileHandle:
            self.outJntData=OrderedDict(pickle.load(fileHandle))

        self.ikfkMatchData={}

        LLegIkResetList=['L_leg_ik_ctrl.footRoll','L_leg_ik_ctrl.rotateHeel','L_leg_ik_ctrl.rotateHeel','L_leg_ik_ctrl.pinHeel','L_leg_ik_ctrl.pinToe','L_leg_ik_ctrl.liftToe','L_leg_ik_ctrl.side']
        RLegIkResetList=['R_leg_ik_ctrl.footRoll','R_leg_ik_ctrl.rotateHeel','R_leg_ik_ctrl.rotateHeel','R_leg_ik_ctrl.pinHeel','R_leg_ik_ctrl.pinToe','R_leg_ik_ctrl.liftToe','R_leg_ik_ctrl.side']

        self.ikfkMatchData['L_arm_switch_ctrl']={'fk':['L_arm_fk_ctrl','L_lowarm_fk_ctrl','L_hand_fk_ctrl'],'ik':['L_arm_ik_ctrl','L_arm_ik_pole_ctrl'],'fkReset':[],'ikReset':[]}
        self.ikfkMatchData['R_arm_switch_ctrl']={'fk':['R_arm_fk_ctrl','R_lowarm_fk_ctrl','R_hand_fk_ctrl'],'ik':['R_arm_ik_ctrl','R_arm_ik_pole_ctrl'],'fkReset':[],'ikReset':[]}
        self.ikfkMatchData['L_leg_switch_ctrl']={'fk':['L_leg_fk_ctrl','L_lowleg_fk_ctrl','L_foot_fk_ctrl','L_toebase_fk_ctrl'],'ik':['L_leg_ik_ctrl','L_leg_ik_pole_ctrl','L_toebase_ik_ctrl'],'fkReset':[],'ikReset':LLegIkResetList}
        self.ikfkMatchData['R_leg_switch_ctrl']={'fk':['R_leg_fk_ctrl','R_lowleg_fk_ctrl','R_foot_fk_ctrl','R_toebase_fk_ctrl'],'ik':['R_leg_ik_ctrl','R_leg_ik_pole_ctrl','R_toebase_ik_ctrl'],'fkReset':[],'ikReset':RLegIkResetList}

        self.PickBtnData={}
        self.FuncBtnData={}
        self.VisGrpData={'L_arm_fk':[],'L_arm_ik':[],'R_arm_fk':[],'R_arm_ik':[],'L_leg_fk':[],'L_leg_ik':[],'R_leg_fk':[],'R_leg_ik':[]}


        for ctrl in BodyUIData:
            rect=BodyUIData[ctrl]['rect']
            lab=BodyUIData[ctrl]['label']
            if(ctrl.endswith('_btn')):
                btn= QtGui.QPushButton(self)
                btn.setGeometry(QtCore.QRect(rect[0], rect[1], rect[2], rect[3]))
                btn.setText(lab)
                btn.setObjectName(ctrl)
                self.FuncBtnData[ctrl]=btn
            else:
                btn= BPickButton(self)
                btn.setGeometry(QtCore.QRect(rect[0], rect[1], rect[2], rect[3]))
                btn.setText(lab)
                chList=BodyUIData[ctrl]['ChildList']
                btn.setProperty("ChildList",chList)
                btn.setObjectName(ctrl)

                self.PickBtnData[ctrl]=btn
            visGrp=BodyUIData[ctrl]['VisGrp']
            if(self.VisGrpData.has_key(visGrp)):
                self.VisGrpData[visGrp].append(btn)

            clickProc=BodyUIData[ctrl]['ClickProc']
            if(clickProc=='Pick'):
                btn.clicked.connect(functools.partial(self.selectCtrl,[ctrl]))
            elif(clickProc=='IkFkSwitch'):
                btn.clicked.connect(functools.partial(self.ikfkSwitch,ctrl))
            elif(clickProc=='SelectAll'):
                btn.clicked.connect(self.selectAll)
            elif(clickProc=='Reset'):
                btn.clicked.connect(self.resetProc)
            elif(clickProc=='Keyframe'):
                btn.clicked.connect(self.keyframeProc)
            elif(clickProc=='MirrorL'):
                btn.clicked.connect(functools.partial(self.mirrorProc,'L_'))
            elif(clickProc=='MirrorR'):
                btn.clicked.connect(functools.partial(self.mirrorProc,'R_'))
            elif(clickProc=='IkFkBake'):
                btn.clicked.connect(functools.partial(self.ikfkBake,ctrl[:-len('_btn')]))
            elif(clickProc=='ImportAnim'):
                btn.clicked.connect(self.importAnim)
        self.updateUIState()



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

    def resetTransAttr(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        dValList=[0,0,0,0,0,0,1,1,1]
        for attr,dv in zip(attrList,dValList):
            isKeyable=cmds.getAttr(obj+'.'+attr,k=1)
            if(isKeyable):
                cmds.setAttr(obj+'.'+attr,dv)
            else:
                 print obj+'.'+attr
    def importAnim(self):
        importNS='AnimImport'
        if(not cmds.namespace(ex=importNS)):
            cmds.namespace(add=importNS)
        try:
            cmds.namespace(set=importNS)
            self.importAnimProc(importNS)
        finally:
            cmds.namespace(set=':')
            cmds.delete(cmds.namespaceInfo(importNS,lod=1))
            cmds.namespace(rm=importNS)

    def importAnimProc(self,importNS):

        filePath=cmds.fileDialog2(ff='.fbx(*.fbx)',fm=1)
        if(filePath==None):return
        fbxPath=filePath[0]


        characterNS=self.namesCB.currentText()
        if(characterNS==None):
            raise RuntimeError,'has not Character exists.'
        switchCtrlList=['L_arm_switch_ctrl','R_arm_switch_ctrl','L_leg_switch_ctrl','R_leg_switch_ctrl']
        for i in switchCtrlList:
            ctrl=characterNS+i
            cmds.setAttr(ctrl+'.ikfk',1)
        
        for jnt in self.outJntData:
            if(self.outJntData[jnt]==None):
                continue
            ctrl=self.outJntData[jnt]['fkCtrl']
            chJnt=characterNS+jnt
            chCtrl=characterNS+ctrl
            print ctrl
            if(cmds.objExists(chJnt) and cmds.objExists(chCtrl)):
                self.resetTransAttr(chCtrl)

        timeInfoAttrList=['TCHour','TCMinute','TCSecond','TCFrame']
        pWorld=True
        newObjMap=OrderedDict()
        for jnt in self.outJntData:
            if(self.outJntData[jnt]==None):
                continue
            ctrl=self.outJntData[jnt]['fkCtrl']
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

                exAttrList=cmds.listAttr(newJnt)
                if(jnt=='Hips'):
                    for attr in timeInfoAttrList:
                        if( attr not in exAttrList):
                            cmds.addAttr(newJnt,ln=attr,at='long',k=1,dv=0)
                exAttrList=cmds.listAttr(newCtrl)
                if(ctrl=='body_ctrl'):
                    for attr in timeInfoAttrList:
                        if( attr not in exAttrList):
                            cmds.addAttr(newCtrl,ln=attr,at='long',k=1,dv=0)

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



        attrList=['tx','ty','tz','rx','ry','rz']+timeInfoAttrList
        keyAnimCurveMap=OrderedDict()
        for i in newObjMap:

            animJnt,newCtrl,chCtrl=newObjMap[i]
            for attr in attrList:
                allAttrList=cmds.listAttr(chCtrl,k=1,sn=1)
                if(attr not in allAttrList):
                    continue
                # isKeyable=cmds.getAttr(chCtrl+'.'+attr,k=1)
                # if(not isKeyable):
                #     continue

                    
                animJntAnim=cmds.findKeyframe(animJnt,c=1,at=attr)

                if(animJntAnim==None):
                    continue
                typ=cmds.objectType(animJntAnim)

                if(attr in timeInfoAttrList):
                    self.copyAnimCurve(animJnt,attr,chCtrl,attr,1)
                else:
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

    def copyAnimCurve(self,animObj,animAttr,pasteObj,pasteAttr,sign):
        isKeyable=cmds.getAttr(pasteObj+'.'+pasteAttr,k=1)
        if(not isKeyable):
            return
        animKName=cmds.findKeyframe(animObj,c=1,at=animAttr)
        if(animKName==None):
            return
        pasteKName=cmds.findKeyframe(pasteObj,c=1,at=pasteAttr)
        if(pasteKName==None):
            pasteKName=cmds.duplicate(animKName,n=pasteObj+'_'+pasteAttr)[0]
            cmds.connectAttr(pasteKName+'.o',pasteObj+'.'+pasteAttr)
            return


        util=OpenMaya.MScriptUtil()
        util.createFromDouble(0.0)
        

        animCurve=self.getMFnAnimCurve(animKName[0])
        pasteCurve=self.getMFnAnimCurve(pasteKName[0])

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

            idx=pasteCurve.addKey(OpenMaya.MTime(keyTime),keyValue,keyInTangentType,keyOutTangentType)
            pasteCurve.setTangentsLocked(idx,keyTangentsLocked)
            pasteCurve.setWeightsLocked(idx,keyWeightsLocked)
            pasteCurve.setIsBreakdown(idx,keyIsBreakdown)
            pasteCurve.setTangent(idx,OpenMaya.MAngle(keyInAngle),keyInWeight,True)
            pasteCurve.setTangent(idx,OpenMaya.MAngle(keyOutAngle),keyOutWeight,False)


    def mirrorProc(self,typ='L_'):
        try:
            cmds.undoInfo(ock=1)
            sel=cmds.ls(sl=1)

            if(len(sel)==0):
                sel=self.PickBtnData.keys()
            selCtrlList=[]
            for i in sel:
                noNSI=i.split(':')[-1]
                if(noNSI.startswith(typ)):
                    selCtrlList.append(noNSI)

            for ctrl in selCtrlList:
                mirCtrl=self.getMirrorName(ctrl)
                if(ctrl==mirCtrl):
                    continue
                ctrl=self.getNameSpaceCtrl(ctrl)
                mirCtrl=self.getNameSpaceCtrl(mirCtrl)

                keyAttrList=cmds.listAttr(ctrl,k=1)
                mirKeyAttrList=cmds.listAttr(mirCtrl,k=1)
                for attr in keyAttrList:
                    if(attr not in mirKeyAttrList):
                        continue
                    ctrlAttr= ctrl+'.'+attr
                    mirCtrlAttr= mirCtrl+'.'+attr
                    isLock=cmds.getAttr(ctrlAttr,l=1)
                    if(isLock):
                        continue
                    isLock=cmds.getAttr(mirCtrlAttr,l=1)
                    if(isLock):
                        continue
                    val=cmds.getAttr(ctrlAttr)
                    cmds.setAttr(mirCtrlAttr,val)

        finally:
            cmds.undoInfo(cck=1)
    def getMirrorName(self,obj):
        L_,R_='L_','R_'
        _L,_R='_L','_R'
        if(obj[:len(L_)]==L_):
            mirObj=R_+obj[len(L_):]
            return mirObj
        elif(obj[:len(R_)]==R_):
            mirObj=L_+obj[len(R_):]
            return mirObj
        elif(obj[-len(_L):]==_L):
            mirObj=obj[:-len(_L)]+_R
            return mirObj
        elif(obj[-len(_R):]==_R):
            mirObj=obj[:-len(_R)]+_L
            return mirObj
        else:
            return obj

    def keyframeProc(self):
        try:
            cmds.undoInfo(ock=1)
            sel=cmds.ls(sl=1)
            if(len(sel)==0):
                self.selectAll()
            cmds.setKeyframe()
        finally:
            cmds.undoInfo(cck=1)

    def resetProc(self):
        try:
            cmds.undoInfo(ock=1)
            sel=cmds.ls(sl=1)
            if(len(sel)==0):
                self.selectAll()
            sel=cmds.ls(sl=1)
            if(len(sel)==0):
                return
            for i in sel:
                keyAttrList=cmds.listAttr(i,k=1)
                for attr in keyAttrList:
                    isLock=cmds.getAttr(i+'.'+attr,l=1)
                    if(isLock):
                        continue
                    if attr in ['ikfk','follow','lock','upLength','dnLength','stretch','globalScale'] or attr.endswith('Vis'):
                        continue
                    try:
                        cmds.setAttr(i+'.'+attr,0)
                    except:
                        print i+'.'+attr
        finally:
            cmds.undoInfo(cck=1)

    def selectAll(self):
        self.selectCtrl(self.PickBtnData.keys())

    def getExistsNameSpace(self):
        exList=cmds.ls('*Hips',r=1)
        nsList=[]
        for jnt in exList:
            spList=jnt.split(':')
            if(len(spList)==1):
                ns=':'
            else:
                ns=jnt[:-len('Hips')]

            nsList.append(ns)
        return nsList

    def refreshNamespace(self):
        old=self.namesCB.currentText()
        self.namesCB.clear()
        self.nsList=self.getExistsNameSpace()
        for i in self.nsList:
            self.namesCB.addItem(i)

        oldIdx=self.namesCB.findText(old) 
        if(oldIdx>=0):
            self.namesCB.setCurrentIndex(oldIdx)

        if(self.aotunamesCB.isChecked()):
            self.setNameSpaceFromSelection()


    def setNameSpaceFromSelection(self,*args):
        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return

        pref=sel[0].split(':')
        curNS=pref[0]+':' if(len(pref)==2) else ':'
        idx=self.namesCB.findText(curNS)
        if(idx!=-1):
            self.namesCB.setCurrentIndex(idx)



    def IkFkBakeUI(self,typ):
        form = cmds.setParent(q=True)
        cmds.frameLayout('mainFL_ifb',p=form,cll=False,lv=False,mh=5,mw=5)
        cmds.columnLayout('mainCL_ifb',adj=True,rs=3)
        cmds.radioButtonGrp('bakeTypeRBG_ifb',cw=[[1, 60], [2, 70]],nrb=2,sl=1,l='Bake Type:',l1='IK > FK',l2='FK > IK')
        cmds.checkBoxGrp('partArmCB_ifb',cw=[[1, 60], [2, 80]],ncb=2,l='part:',l1='R_Arm',l2='L_Arm')
        cmds.checkBoxGrp('partLegCB_ifb',cw=[[1, 60], [2, 80]],ncb=2,l='',l1='R_Leg',l2='L_Leg')

        cmds.intFieldGrp('tiemSE_ifb',cw=[[1, 60]],l='Start/End:',nf=2)
        cmds.button(l='Bake Anim',c=self.IkFkBakeWinComfirm)
        cmds.formLayout(form,e=1,af=[['mainFL_ifb', 'top', 0], ['mainFL_ifb', 'left', 0], ['mainFL_ifb', 'right', 0], ['mainFL_ifb', 'bottom', 0]])


        switchCtrl=self.getNameSpaceCtrl(typ)
        if(cmds.objExists(switchCtrl)):
            ikfk=cmds.getAttr(switchCtrl+'.ikfk')
            cmds.radioButtonGrp('bakeTypeRBG_ifb',e=1,sl= 1 if(ikfk==0) else 2)

        cmds.checkBoxGrp('partArmCB_ifb',e=1,v1=0,v2=0)
        cmds.checkBoxGrp('partLegCB_ifb',e=1,v1=0,v2=0)
        if(typ=='R_arm_switch_ctrl'):
            cmds.checkBoxGrp('partArmCB_ifb',e=1,v1=1)
        elif(typ=='L_arm_switch_ctrl'):
            cmds.checkBoxGrp('partArmCB_ifb',e=1,v2=1)
        elif(typ=='R_leg_switch_ctrl'):
            cmds.checkBoxGrp('partLegCB_ifb',e=1,v1=1)
        else:
            cmds.checkBoxGrp('partLegCB_ifb',e=1,v2=1)

        minT=cmds.playbackOptions(q=1,min=1)
        maxT=cmds.playbackOptions(q=1,max=1)
        cmds.intFieldGrp('tiemSE_ifb',e=1,v1=minT,v2=maxT)

    def IkFkBakeWinComfirm(self,*args):
        bakeType=cmds.radioButtonGrp('bakeTypeRBG_ifb',q=1,sl=1)

        minT=cmds.intFieldGrp('tiemSE_ifb',q=1,v1=1)
        maxT=cmds.intFieldGrp('tiemSE_ifb',q=1,v2=1)
        bakeCtrlList=[]
        if(cmds.checkBoxGrp('partArmCB_ifb',q=1,v1=0)):
            bakeCtrlList.append('R_arm_switch_ctrl')
        if(cmds.checkBoxGrp('partArmCB_ifb',q=1,v2=0)):
            bakeCtrlList.append('L_arm_switch_ctrl')    
        if(cmds.checkBoxGrp('partLegCB_ifb',q=1,v1=0)):
            bakeCtrlList.append('R_leg_switch_ctrl')
        if(cmds.checkBoxGrp('partLegCB_ifb',q=1,v2=0)):
            bakeCtrlList.append('L_leg_switch_ctrl')   

        self.ikfkBakeData=[bakeType,minT,maxT,bakeCtrlList]

        cmds.layoutDialog(dis='OK')

    def ikfkBake(self,typ):
        ret=cmds.layoutDialog(ui=functools.partial(self.IkFkBakeUI,typ))
        if(ret!='OK'):
            return
        bakeType,minT,maxT,bakeCtrlList=self.ikfkBakeData
        # bakeType,minT,maxT,bakeCtrlList=2,1,70,['L_leg_switch_ctrl']

        try:
            cmds.undoInfo(ock=1)
            for T in range(minT,maxT+1):
                cmds.currentTime(T)
                
                for ctrlId in bakeCtrlList:
                    switchCtrl=self.getNameSpaceCtrl(ctrlId)
                    if(not cmds.objExists(switchCtrl)):
                        continue
                    matchList=self.ikfkMatchData[ctrlId]['fk' if bakeType==1 else 'ik']
                    resetList=self.ikfkMatchData[ctrlId]['fkReset' if bakeType==1 else 'ikReset']
                    self.matchCtrlPose(matchList,resetList,isKey=True)


            for ctrlId in bakeCtrlList:
                switchCtrl=self.getNameSpaceCtrl(ctrlId)
                if(not cmds.objExists(switchCtrl)):
                    continue
                cmds.setAttr(switchCtrl+'.ikfk',1 if bakeType==1 else 0)
        finally:
            cmds.undoInfo(cck=1)

    def ikfkSwitch(self,ctrlId):
        try:
            cmds.undoInfo(ock=1)
            switchCtrl=self.getNameSpaceCtrl(ctrlId)
            ikfk=cmds.getAttr(switchCtrl+'.ikfk')
            if(self.ikfkSeamlessCB.isChecked()):
                matchList=self.ikfkMatchData[ctrlId]['fk' if ikfk==0 else 'ik']
                resetList=self.ikfkMatchData[ctrlId]['fkReset' if ikfk==0 else 'ikReset']
                self.matchCtrlPose(matchList,resetList)

            cmds.setAttr(switchCtrl+'.ikfk',1-ikfk)
            self.selectCtrl([switchCtrl])
        finally:
            cmds.undoInfo(cck=1)
   
    def getNameSpaceCtrl(self,ctrl):
        namespace=self.namesCB.currentText()
        return namespace+ctrl

    def matchCtrlPose(self,matchList,resetList,isKey=False):
        for ctrl in matchList:
            ctrl=self.getNameSpaceCtrl(ctrl)
            matchGrp=ctrl+'_match'
            if(not cmds.objExists(matchGrp)):
                self.resetTransformAttr(ctrl)
            else:
                pos=cmds.xform(matchGrp,ws=1,q=1,t=1)
                rot=cmds.xform(matchGrp,ws=1,q=1,ro=1)
                cmds.xform(ctrl,ws=1,t=pos)
                cmds.xform(ctrl,ws=1,ro=rot)
            if(isKey):
                self.keyTransformAttr(ctrl)
        for i in resetList:
            i=self.getNameSpaceCtrl(i)
            cmds.setAttr(i,0)

    def keyTransformAttr(self,ctrl):
        attrList=['tx','ty','tz','rx','ry','rz']
        for attr in attrList:
            isKeyable=cmds.getAttr(ctrl+'.'+attr,k=1)
            if(isKeyable):
                cmds.setKeyframe(ctrl,at=attr)


    def resetTransformAttr(self,obj):
        attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        valList=[0,0,0,0,0,0,1,1,1]
        for attr,dv in zip(attrList,valList):
            isLock=cmds.getAttr(obj+'.'+attr,l=1)
            if(isLock):
                continue
            cmds.setAttr(obj+'.'+attr,dv)
    def updateIkFKBtnState(self):
        LArmSwitchCtrl='L_arm_switch_ctrl'
        self.switchBtnIkFkState(LArmSwitchCtrl,'L_arm_fk','L_arm_ik')
        RArmSwitchCtrl='R_arm_switch_ctrl'
        self.switchBtnIkFkState(RArmSwitchCtrl,'R_arm_fk','R_arm_ik')
        LLegSwitchCtrl='L_leg_switch_ctrl'
        self.switchBtnIkFkState(LLegSwitchCtrl,'L_leg_fk','L_leg_ik')
        RLegSwitchCtrl='R_leg_switch_ctrl'
        self.switchBtnIkFkState(RLegSwitchCtrl,'R_leg_fk','R_leg_ik')

    def switchBtnIkFkState(self,ctrlId,fkKey,ikKey):
        ctrl=self.getNameSpaceCtrl(ctrlId)
        ikfk=1
        exList=cmds.listAttr(ctrl,ud=1)
        if(exList==None or 'ikfk' not in exList):
            return
        if(cmds.objExists(ctrl)):
            ikfk=cmds.getAttr(ctrl+'.ikfk')
        for btn in self.VisGrpData[fkKey]:
            btn.setVisible(ikfk)
        for btn in self.VisGrpData[ikKey]:
            btn.setVisible(not ikfk)
        self.PickBtnData[ctrlId].setText('IK' if ikfk==0 else 'FK')

    def keyPressEvent(self,event):
        if(event.key()==QtCore.Qt.Key_Control):
            self.ControlModifier=True
        if(event.key()==QtCore.Qt.Key_Shift):
            self.ShiftModifier=True
        event.accept()
        self.setFocus()
    def keyReleaseEvent(self,event):
        if(event.key()==QtCore.Qt.Key_Control):
            self.ControlModifier=False
        if(event.key()==QtCore.Qt.Key_Shift):
            self.ShiftModifier=False
        event.accept()
        self.setFocus()

    def mousePressEvent(self,event):
        if(event.button()==QtCore.Qt.MouseButton.LeftButton):
            self.origin = event.pos()
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
            self.rubberBand.show()
            event.accept()
    def mouseMoveEvent(self,event):
        if(self.rubberBand.isVisible()):
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            event.accept()
    def mouseReleaseEvent(self,event):
        if(event.button()==QtCore.Qt.MouseButton.LeftButton):
            self.rubberBand.hide()
            SelRect=QtCore.QRect(self.origin, event.pos()).normalized()
            selList=[]
            for i in self.PickBtnData:
                btn=self.PickBtnData[i]
                if(not btn.isVisible()):
                    continue
                iRect=SelRect.intersected(btn.geometry())
                if(SelRect.contains(btn.geometry()) or not iRect.isEmpty()):
                    selList.append(i)
            self.selectCtrl(selList)
            event.accept()
    
    def selectCtrl(self,selList):
        exSelList=[]
        for i in selList:
            i=self.getNameSpaceCtrl(i)
            if(cmds.objExists(i)):
                exSelList.append(i)
        if(self.ControlModifier==True and self.ShiftModifier==False):
            cmds.select(exSelList,d=1)
        elif(self.ShiftModifier==True):
            cmds.select(exSelList,add=1)
        else:
            cmds.select(cl=1)
            cmds.select(exSelList,add=1)
        self.updateUIState()


    def updateUIState(self):
        self.refreshNamespace()
        self.updateIkFKBtnState()
        sel=cmds.ls(sl=1)
        activeList=[i.split(':')[-1] for i in sel]
        for i in self.PickBtnData:
            btn=self.PickBtnData[i]
            btn.setSelect(bool(i in activeList))

    def focusOutEvent(self,event):
        self.ControlModifier=False
        self.ShiftModifier=False



class BBodyAnimUIModule():
    def __init__(self,rootPath='E:/myCode/sdd_bodyRigging/'):
        self.rootPath=rootPath
        self.ctrl=None

    def selectChangeJobProc(self):
        self.ctrl.updateUIState()


    def showUI(self):
        if(cmds.window('sdd_bodyPickerUI_bp',q=True,ex=True)):
            cmds.deleteUI('sdd_bodyPickerUI_bp')

        cmds.window('sdd_bodyPickerUI_bp',rtf=1,s=0)
        cmds.columnLayout('MainCL_bp',adj=True)

        self.ctrl=BPickWidget(None,rootPath=self.rootPath)
        self.ctrl.setObjectName('bodyAnimPickGrp1_bp')

        print self.ctrl.namesCB
        cmds.control('bodyAnimPickGrp1_bp',e=1,p=cmds.setParent(q=1))
        cmds.showWindow('sdd_bodyPickerUI_bp')
        # if(cmds.dockControl('sdd_bodyPickerUI_bp_dock',q=1,ex=1)):cmds.deleteUI('sdd_bodyPickerUI_bp_dock')
        # cmds.dockControl('sdd_bodyPickerUI_bp_dock',l='Body Picker',con='sdd_bodyPickerUI_bp',a='right',fl=1,aa=['top', 'bottom', 'left', 'right'],w=640,h=480)

        cmds.scriptJob(e=['SelectionChanged',self.selectChangeJobProc],p='sdd_bodyPickerUI_bp')

        global TPickWidget
        TPickWidget=self.ctrl




def BBodyAnimUI(rootPath):
    global BodyUIModuel
    BodyUIModuel=BBodyAnimUIModule(rootPath)
    BodyUIModuel.showUI()
# if __name__ == '__main__':
#     BodyUIModuel=BBodyAnimUIModule()
#     BodyUIModuel.showUI()
#     self=BodyUIModuel.ctrl