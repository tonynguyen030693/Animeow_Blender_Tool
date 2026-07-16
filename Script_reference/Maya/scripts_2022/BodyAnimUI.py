from maya import OpenMayaUI
from maya import cmds
from PySide import QtCore,QtGui
import shiboken
import pickle
import functools

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
    def mouseDoubleClickEvent(self,event):
        print event.ignore()


class BPickWidget(QtGui.QWidget):
    def __init__(self,parent=None,rootPath=''):
        self.rootPath+'icons/'
        self.iconPath=iconPath
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
        self.namespaceCB = QtGui.QComboBox(self)
        self.namespaceCB.setGeometry(QtCore.QRect(14, 6, 425, 22))
        self.namespaceCB.setObjectName("namespace_cb")

        self.ikfkSeamlessCB = QtGui.QCheckBox('IkFk seamless switch',self)
        self.ikfkSeamlessCB.setGeometry(QtCore.QRect(16, 30, 150, 22))
        self.ikfkSeamlessCB.setObjectName("ikfkSeamless_CB")
        self.ikfkSeamlessCB.setChecked(True)


        self.selScriptJob=cmds.scriptJob(e=['SelectionChanged',self.updateUIState])

        filePath='E:/myCode/sdd_bodyRig/files/BodyUIData.uidata'
        with open(filePath,'r') as fileHandle:
            BodyUIData=pickle.load(fileHandle)

        self.ikfkMatchData={}
        self.ikfkMatchData['L_arm_switch_ctrl']={'fk':['L_arm_fk_ctrl','L_lowarm_fk_ctrl','L_hand_fk_ctrl'],'ik':['L_arm_ik_ctrl','L_arm_ik_pole_ctrl']}
        self.ikfkMatchData['R_arm_switch_ctrl']={'fk':['R_arm_fk_ctrl','R_lowarm_fk_ctrl','R_hand_fk_ctrl'],'ik':['R_arm_ik_ctrl','R_arm_ik_pole_ctrl']}
        self.ikfkMatchData['L_leg_switch_ctrl']={'fk':['L_leg_fk_ctrl','L_lowleg_fk_ctrl','L_foot_fk_ctrl','L_toebase_fk_ctrl'],'ik':['L_foot_ik_ctrl','L_heel_ik_ctrl','L_leg_ik_ctrl','L_leg_ik_pole_ctrl','L_toebase_ik_ctrl']}
        self.ikfkMatchData['R_leg_switch_ctrl']={'fk':['R_leg_fk_ctrl','R_lowleg_fk_ctrl','R_foot_fk_ctrl','R_toebase_fk_ctrl'],'ik':['R_foot_ik_ctrl','R_heel_ik_ctrl','R_leg_ik_ctrl','R_leg_ik_pole_ctrl','R_toebase_ik_ctrl']}

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
        self.updateUIState()
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

    def showEvent(self,event):
        if(not cmds.scriptJob(ex=self.selScriptJob)):
            self.selScriptJob=cmds.scriptJob(e=['SelectionChanged',self.updateUIState])
        QtGui.QWidget.showEvent(self,event)

    def hideEvent(self,event):
        if(cmds.scriptJob(ex=self.selScriptJob)):
            cmds.scriptJob(k=self.selScriptJob,f=1)
        QtGui.QWidget.hideEvent(self,event)

    def refreshNamespace(self):
        old=self.namespaceCB.currentText()
        self.namespaceCB.clear()
        allCtrl='all_ctrl'
        nsList=cmds.namespaceInfo(lon=1)
        nsList=['']+nsList
        for ns in nsList:
            nsl=ns+':'
            if(cmds.objExists(nsl+allCtrl)):
                self.namespaceCB.addItem(nsl,ns)
        oldIdx=self.namespaceCB.findText(old)
        if(oldIdx>=0):
            self.namespaceCB.setCurrentIndex(oldIdx)

        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return
        pref=sel[0].split(':')
        curNS=pref[0] if(len(pref)==2) else ''
        for i in range(self.namespaceCB.count()):
            if(self.namespaceCB.itemData(i)==curNS):
                self.namespaceCB.setCurrentIndex(i)
                break
    def ikfkSwitch(self,ctrlId):
        try:
            cmds.undoInfo(ock=1)
            switchCtrl=self.getNameSpaceCtrl(ctrlId)
            ikfk=cmds.getAttr(switchCtrl+'.ikfk')
            if(self.ikfkSeamlessCB.isChecked()):
                matchList=self.ikfkMatchData[ctrlId]['fk' if ikfk==0 else 'ik']
                self.matchCtrlPose(matchList)

            cmds.setAttr(switchCtrl+'.ikfk',1-ikfk)
            self.selectCtrl([switchCtrl])
        finally:
            cmds.undoInfo(cck=1)
   
    def getNameSpaceCtrl(self,ctrl):
        namespace=self.namespaceCB.currentText()
        return namespace+ctrl

    def matchCtrlPose(self,matchList):
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
    def __init__(self,rootPath='E:/myCode/sdd_bodyRig/'):
        self.rootPath=rootPath

    def showUI(self):
        if(cmds.window('sdd_BodyAnimUIWin_bui',q=True,ex=True)):cmds.deleteUI('sdd_BodyAnimUIWin_bui')
        cmds.window('sdd_BodyAnimUIWin_bui',s=False)
        cmds.columnLayout(adj=True)
        self.bodyAnimPickGrp('bodyAnimPickGrp1_bui')
        if(cmds.dockControl('sdd_BodyAnimUIWin_bui_dock',q=1,ex=1)):cmds.deleteUI('sdd_BodyAnimUIWin_bui_dock')
        cmds.dockControl('sdd_BodyAnimUIWin_bui_dock',con='sdd_BodyAnimUIWin_bui',a='right',fl=1,aa=['top', 'bottom', 'left', 'right'])

    def bodyAnimPickGrp(self,name):
        self.ctrl=BPickWidget(None,rootPath=self.rootPath)
        self.ctrl.setObjectName(name)
        cmds.control(name,e=1,p=cmds.setParent(q=1))

def BBodyAnimUI(rootPath):

    BodyUIModuel=BBodyAnimUIModule(rootPath)
    BodyUIModuel.showUI()

if __name__ == '__main__':
    BBodyAnimUI('E:/myCode/sdd_bodyRig/')