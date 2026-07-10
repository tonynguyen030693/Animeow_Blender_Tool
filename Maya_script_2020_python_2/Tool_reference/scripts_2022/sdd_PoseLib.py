from maya import OpenMayaUI
from maya import cmds
from PySide import QtCore,QtGui
import shiboken
import pickle
import functools
import os
import re
import copy
import shutil
class PIconButton(QtGui.QWidget):
    click=QtCore.Signal()
    doubleClick=QtCore.Signal()
    def __init__(self,parent=None,image='E:/tt.jpg',name='test'):
        QtGui.QWidget.__init__(self,parent)
        self.poseName=name

        self.iconLabel=QtGui.QLabel(self)
        self.iconLabel.setPixmap(QtGui.QPixmap(image))
        self.iconLabel.setScaledContents(True)
        self.textLabel=QtGui.QLabel(self.poseName,self)
        self.textLabel.setFixedHeight(22)
        self.textLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        self.setAutoFillBackground(True)

        self.bgColor=QtGui.QColor(50,50,50)
        self.setBgColor(self.bgColor)
        self.setIconSize(60)
        self.isSelected=False
    def setPoseName(self,name):
        self.poseName=name
        self.textLabel.setText(self.poseName)
    def setBgColor(self,col):
        palette=self.palette()
        palette.setColor(palette.Background,col)
        self.setPalette(palette)
    def setSelect(self,isSel):
        self.isSelected=isSel
        if(self.isSelected):
            self.setBgColor(self.bgColor.lighter(200))
        else:
            self.setBgColor(self.bgColor)
    def setIconSize(self,size):
        self.setFixedSize(size+4,size+22+4)
        self.iconLabel.setGeometry(2,2,size,size)
        self.textLabel.setGeometry(2,2+size,size,22)
    def setHighLighter(self):
        self.setBgColor(self.bgColor.lighter(255))
    # def mouseDoubleClickEvent(self,event):
    #     if(event.button()==QtCore.Qt.MouseButton.LeftButton):
    #         self.doubleClick.emit()
    #         self.setBgColor(self.bgColor.lighter(255))
    #         event.accept()

    # def mousePressEvent(self,event):
    #     if(event.button()==QtCore.Qt.MouseButton.LeftButton):
    #         self.click.emit()
    #         self.setBgColor(self.bgColor.lighter(255))
    #         # event.accept()

    #     QtGui.QWidget.mousePressEvent(self,event)

    # def mouseReleaseEvent(self,event):
    #     if(event.button()==QtCore.Qt.MouseButton.LeftButton):
    #         self.setBgColor(self.bgColor)
    #         event.accept()
    #     else:
    #         QtGui.QWidget.mouseReleaseEvent(self,event)
    # def enterEvent(self,event):
    #     self.setBgColor(self.bgColor.lighter(160))
    # def leaveEvent(self,event):
    #     self.setBgColor(self.bgColor)

class PFlowLayout(QtGui.QLayout):
    resizeHeight=QtCore.Signal(int)
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(PFlowLayout, self).__init__(parent)
        self.margin=margin

        self.setSpacing(spacing)

        self.itemList = []
        self.layoutHeight=0

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        width=width if(self.layoutHeight<width) else self.layoutHeight
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        self.resizeHeight.emit(height)
        return height

    def setGeometry(self, rect):
        super(PFlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
        self.layoutHeight=rect.width()

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin, 2 * self.margin)
        return size
    def setItemSize(self,size):
        for item in self.itemList:
            item.widget().setIconSize(size)
        height=self.doLayout(self.geometry(), False)
        self.resizeHeight.emit(height)

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            space= self.spacing() if(item.widget().isVisible()) else 0
            nextX = x + item.sizeHint().width() + space
            if nextX - space > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + space*5
                nextX = x + item.sizeHint().width() + space
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())


        return y + lineHeight - rect.y()

class PFlowWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.mainLayout=PFlowLayout(spacing=2)
        self.setLayout(self.mainLayout)
        self.mainLayout.resizeHeight.connect(self.setFixedHeight)
    def setFixedHeight(self,height):
        QtGui.QWidget.setFixedHeight(self,height)
    def resizeEvent(self,event):
        QtGui.QWidget.resizeEvent(self,event)
        self.mainLayout.setGeometry(self.geometry())




class PScrollWeiget(QtGui.QScrollArea):
    deleteSelection=QtCore.Signal(list)
    selectChanged=QtCore.Signal(list)
    itemDClick=QtCore.Signal(str)
    mixturePose=QtCore.Signal(str)
    renameItem=QtCore.Signal(str)
    copyItem=QtCore.Signal(list)
    pasteItem=QtCore.Signal()
    openItem=QtCore.Signal(str)
    keyPose=QtCore.Signal(str)


    def __init__(self,parent=None):
        QtGui.QScrollArea.__init__(self,parent)
        self.mainWidget=PFlowWidget()
        self.setWidget(self.mainWidget)
        self.defulatSize=60
        self.minSize=20
        self.maxSize=300
        self.curSize=self.defulatSize
        self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.ControlModifier=False
        self.ShiftModifier=False

    def setIconSizeHint(self,size):
        self.minSize,self.maxSize,self.defulatSize=size
        self.curSize=self.defulatSize
        self.mainWidget.mainLayout.setItemSize(self.curSize)

    def getAllItem(self):
        return self.mainWidget.mainLayout.itemList

    def resizeEvent(self,event):
        QtGui.QScrollArea.resizeEvent(self,event)
        self.mainWidget.setFixedWidth(self.width()-16) 
    def addWidget(self,widget):
        self.mainWidget.mainLayout.addWidget(widget)
        widget.setIconSize(self.curSize)
        self.rubberBand.show()
        self.rubberBand.hide()
    def removeWidget(self,widget):
        self.mainWidget.mainLayout.removeWidget(widget)


        # self.rubberBand.show()
        # self.rubberBand.hide()
    def wheelEvent(self,event):
        if(event.modifiers()==QtCore.Qt.Modifier.CTRL):
            dt=event.delta()/abs(event.delta())*5
            self.curSize=max(self.minSize,min(self.curSize+dt,self.maxSize))
            self.mainWidget.mainLayout.setItemSize(self.curSize)
            event.accept()

    def keyPressEvent(self,event):
        if(event.key()==QtCore.Qt.Key_C):
            if(self.ControlModifier):
                self.copyItemProc()
        if(event.key()==QtCore.Qt.Key_V):
            if(self.ControlModifier):
                self.pasteItemProc()

        if(event.key()==QtCore.Qt.Key_F):
            self.curSize=self.defulatSize
            self.mainWidget.mainLayout.setItemSize(self.curSize)
        if(event.key()==QtCore.Qt.Key_Delete):
            self.deleteSelectionItem()
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

    def getSelectWidget(self):
        sel=[]
        for item in self.getAllItem():
            widget=item.widget()
            if(widget.isSelected):
                sel.append(widget.poseName)
        return sel

    def getMapPos(self,pos):
        posx=self.horizontalScrollBar().value()+pos.x()
        posy=self.verticalScrollBar().value()+pos.y()
        return QtCore.QPoint(posx,posy)

    def mousePressEvent(self,event):
        if(event.button()==QtCore.Qt.MouseButton.LeftButton):
            self.origin = event.pos()
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
            self.rubberBand.show()
            hitWidegt=self.getHitItem(event.pos())
            if(hitWidegt):
                hitWidegt.setSelect(True)
            event.accept()
        elif(event.button()==QtCore.Qt.MouseButton.RightButton):
            hitWidegt=self.getHitItem(event.pos())
            if(hitWidegt):
                self.clearSeletion()
                hitWidegt.setSelect(True)
                self.rightItemMenuShow(hitWidegt.poseName)
            else:
                self.rightMenuShow()

    def mouseDoubleClickEvent(self,event):
        if(event.button()==QtCore.Qt.MouseButton.LeftButton):
            hitWidegt=self.getHitItem(event.pos())
            if(hitWidegt):
                hitWidegt.setHighLighter()
                self.itemDClick.emit(hitWidegt.poseName)
            event.accept()


    def getHitItem(self,pos):
        print pos
        pos=self.getMapPos(pos)
        print pos
        hitWidegt=None
        for item in self.getAllItem():
            widget=item.widget()
            itemRect=widget.geometry()
            if(itemRect.contains(pos)):
                hitWidegt=widget
                break
        return hitWidegt

    def mouseMoveEvent(self,event):
        if(self.rubberBand.isVisible()):
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            event.accept()
    def mouseReleaseEvent(self,event):
        if(event.button()==QtCore.Qt.MouseButton.LeftButton):
            self.rubberBand.hide()
            SelRect=QtCore.QRect(self.getMapPos(self.origin), self.getMapPos(event.pos())).normalized()
            selList=[]
            for item in self.getAllItem():
                widget=item.widget()
                isContaint=self.rectIntersectContains(widget.geometry(),SelRect)
                if(isContaint):
                    selList.append(item)
            self.setSelect(selList)
            event.accept()

    def setSelect(self,selList):
        if(self.ControlModifier==False and self.ShiftModifier==False):
            self.clearSeletion()
        exSelList=[]
        for item in selList:
            widget=item.widget()
            if(self.ControlModifier==True and self.ShiftModifier==False):
                widget.setSelect(False)
            else:
                widget.setSelect(True)
        sel=self.getSelectWidget()
        self.selectChanged.emit(sel)

    def rectIntersectContains(self,widgetRect,selRect):
        if(widgetRect.isEmpty()):
            return False
        iRect=selRect.intersected(widgetRect)
        if(not iRect.isEmpty()):
            return True
        if(selRect.contains(widgetRect)):
            return True
        return False

    def clearSeletion(self):
        for wi in self.getAllItem():
            wi.widget().setSelect(False)

    def sizeHint(self):
        return QtCore.QSize(500,400)
        # self.selectCtrl(selList)
    def rightMenuShow(self):
        rightMenu=QtGui.QMenu(self)
        copyAction = QtGui.QAction('Copy Selection', self,shortcut='Ctrl+C', triggered=self.copyItemProc) 
        rightMenu.addAction(copyAction)
        pasteAction = QtGui.QAction('Paste Selection', self,shortcut='Ctrl+V', triggered=self.pasteItemProc) 
        rightMenu.addAction(pasteAction)

        rightMenu.addSeparator()

        deleteAction = QtGui.QAction('Delete Selection', self,shortcut='Delete', triggered=self.deleteSelectionItem) 
        rightMenu.addAction(deleteAction)
        resetAction = QtGui.QAction('Reset View', self,shortcut='F', triggered=self.resetView) 
        rightMenu.addAction(resetAction)

        rightMenu.addSeparator()
        openAction = QtGui.QAction('Open in Explorer', self, triggered=functools.partial(self.openItem.emit,'')) 
        rightMenu.addAction(openAction)

        rightMenu.exec_(QtGui.QCursor.pos())
    def rightItemMenuShow(self,poseName):
        rightItemMenu=QtGui.QMenu(self)
        keyAction = QtGui.QAction('Key', self, triggered=functools.partial(self.keyPose.emit,poseName)) 
        rightItemMenu.addAction(keyAction)

        rightItemMenu.addSeparator()

        mixtureAction = QtGui.QAction('Mixture Pose', self, triggered=functools.partial(self.mixturePose.emit,poseName)) 
        rightItemMenu.addAction(mixtureAction)

        rightItemMenu.addSeparator()

        openAction = QtGui.QAction('Open in Explorer', self, triggered=functools.partial(self.openItem.emit,poseName)) 
        rightItemMenu.addAction(openAction)

        rightItemMenu.addSeparator()

        renameAction = QtGui.QAction('Rename', self, triggered=functools.partial(self.renameItem.emit,poseName)) 
        rightItemMenu.addAction(renameAction)

        rightItemMenu.exec_(QtGui.QCursor.pos())
    def copyItemProc(self):
        sel=self.getSelectWidget()
        if(len(sel)>0):
            self.copyItem.emit(sel)
    def pasteItemProc(self):
        self.pasteItem.emit()

    def deleteSelectionItem(self):
        sel=self.getSelectWidget()
        if(len(sel)>0):
            self.deleteSelection.emit(sel)


    def resetView(self):
        self.curSize=self.defulatSize
        self.mainWidget.mainLayout.setItemSize(self.curSize)

    def printss(self):
        print '---------------'

class PoseLibraryModule():
    def __init__(self):
        self.getSettingData()
        self.npShowType=[1,0,0,0]
        self.allGroupData={}
        self.nameRegex=re.compile('^[\w][\w]*$')
        self.copyDataList=[]
    def TimeCompare(self,x, y):
        stat_x = os.stat(x)
        stat_y = os.stat(y)

        if stat_x.st_ctime < stat_y.st_ctime:
            return -1
        elif stat_x.st_ctime > stat_y.st_ctime:
            return 1
        else:
            return 0
    def createScriptJob(self,winName=None):
        self.selectChangedJob=cmds.scriptJob(e=['SelectionChanged',self.refreshNamespace],p='poseMainFL_ps')

    def setupUI(self):
        self.allGroupData={}
        oldList=cmds.tabLayout('poseMainTL_ps',q=1,ca=1)
        if(oldList):
            cmds.deleteUI(oldList)
        for projectPath in self.settingData['projectPathList']:
            subList=os.listdir(projectPath)
            poseGroupList=[]
            for sub in subList:
                subPath=projectPath+sub
                if(os.path.isdir(subPath)):
                    poseGroupList.append(subPath)
            poseGroupList.sort(self.TimeCompare)
            for i in poseGroupList:
                self.addPScrollWeiget(i)
        cmds.rowLayout('mixturePoseRL_ps',e=1,vis=0)
        self.refreshNamespace()
        self.createScriptJob()
        self.tabSelectChange()

    def addPScrollWeiget(self,path):
        groupName=os.path.basename(path)
        ctrlName='%sPSW_ps'%groupName
        plLayout=cmds.paneLayout(p='poseMainTL_ps',ann=groupName)
        cmds.tabLayout('poseMainTL_ps',e=1,tl=[plLayout,groupName])
        ctrl=PScrollWeiget()
        ctrl.setObjectName(ctrlName)
        cmds.control(ctrlName,e=1,p=plLayout)
        ctrl.deleteSelection.connect(self.deleteSelectionItem)
        ctrl.itemDClick.connect(self.assignPose)
        ctrl.mixturePose.connect(self.mixturePose)
        ctrl.selectChanged.connect(self.selectChanged)
        ctrl.renameItem.connect(self.renamePose)
        ctrl.copyItem.connect(self.copyPose)
        ctrl.pasteItem.connect(self.pastePose)
        ctrl.openItem.connect(self.openInExplorer)
        ctrl.keyPose.connect(self.keyPose)

        ctrl.setIconSizeHint(self.settingData['iconSize'])
        self.allGroupData[groupName]={'ctrl':ctrl,'path':path,'isLoad':False,'poseListData':{}}

    def show(self):
        self.PoseLibWin()

    def PoseLibWin(self):
        if(cmds.window('sdd_poseLibWin_ps',q=True,ex=True)):cmds.deleteUI('sdd_poseLibWin_ps')
        cmds.window('sdd_poseLibWin_ps',t=u'poseLib',wh=(500, 600))
        cmds.formLayout('poseMainFL_ps',w=420,h=350)
        cmds.columnLayout('toolBarCL_ps',adj=True)
        cmds.rowLayout('mixturePoseRL_ps',vis=False,nc=2,adj=2)
        cmds.text('mpPoseNameT_ps',l=u'')
        cmds.floatSliderGrp('mpWeightFSG_ps',f=True,min=0.0,max=1.0,pre=2,cc=self.mixturePoseWeightChange,dc=self.mixturePoseWeightDrag)
        cmds.rowLayout('toolBarRL_ps',p='toolBarCL_ps',nc=4,adj=2)
        cmds.button('addPoseB_ps',w=50,h=18,l=u'+',c=self.newPose)
        cmds.optionMenu('nameSpaceOM_ps')
        cmds.menuItem(l=':')
        cmds.checkBox('nsLockCB_ps',p='toolBarRL_ps',l=u'Auto',v=True)
        cmds.iconTextButton('settingITB_ps',p='toolBarRL_ps',w=18,h=18,i=u'hotkeySetSettings.png',c=self.PoseLibSettingWin)
        cmds.tabLayout('poseMainTL_ps',p='poseMainFL_ps',cr=True,cc=self.tabSelectChange)
        cmds.formLayout('poseMainFL_ps',e=1,af=[[u'toolBarCL_ps', 'left', 0], [u'toolBarCL_ps', 'right', 0], [u'toolBarCL_ps', 'bottom', 0], [u'poseMainTL_ps', 'top', 0], [u'poseMainTL_ps', 'left', 0], [u'poseMainTL_ps', 'right', 0]],ac=[[u'poseMainTL_ps', 'bottom', 0, u'toolBarCL_ps']])
        if(cmds.dockControl('sdd_poseLibWin_ps_dock',q=1,ex=1)):cmds.deleteUI('sdd_poseLibWin_ps_dock')
        cmds.dockControl('sdd_poseLibWin_ps_dock',l='PoseLib',con='sdd_poseLibWin_ps',a='right',fl=1,aa=['top', 'bottom', 'left', 'right'],w=500,h=600)

        self.setupUI()
    def openInExplorer(self,poseName):
        print poseName
        groupData=self.getCurrentGroupData()
        os.startfile(groupData['path'])

    def tabSelectChange(self,*args):
        groupData=self.getCurrentGroupData()
        if(not groupData['isLoad']):
            self.loadPoseLibs(groupData['path'])
            groupData['isLoad']=True

        
    def copyPose(self,poseList):
        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']
        self.copyDataList=[]
        for poseName in poseList:
            if(poseListData.has_key(poseName)):
                poseItemData=copy.deepcopy(poseListData[poseName]['orientData']) 
                self.copyDataList.append(poseItemData)

    def pastePose(self):
        if(not self.copyDataList or len(self.copyDataList)==0):
            return
        groupData=self.getCurrentGroupData()
        for poseItemData in self.copyDataList:
            poseName=self.getTempPoseName()
            filePath=groupData['path']+'/%s.pose'%poseName
            with open(filePath,'w') as fileHandle:
                pickle.dump(poseItemData,fileHandle)
            self.addPoseToView(filePath)

    def addPoseToView(self,filePath):
        baseName=os.path.basename(filePath)
        poseName=os.path.splitext(baseName)[0]
        with open(filePath,'r') as fileHandle:
            poseItemData=pickle.load(fileHandle)
        iconBtn=PIconButton(image=self.hexStrToImage(poseItemData['image']),name=poseName)
        iconBtn.click.connect(functools.partial(self.poseButtonClickProc,baseName))

        groupData=self.getCurrentGroupData(filePath)
        groupData['ctrl'].addWidget(iconBtn)
        poseData={'filePath':filePath,'btn':iconBtn,'orientData':poseItemData}
        groupData['poseListData'][poseName]=poseData

    def loadPoseLibs(self,path):
        allList=os.listdir(path)
        poseList=[]
        for i in allList:
            tt,ext=os.path.splitext(i)
            if(ext=='.pose'):
                poseList.append(os.path.join(path,i))
        poseList.sort(self.TimeCompare)
        for i in poseList:
            self.addPoseToView(i)

    def selectChanged(self,sel):
        cmds.rowLayout('mixturePoseRL_ps',e=1,vis=0)
        if(len(sel)==0):
            return
        ctrlSet=set()
        for poseName in sel:
            groupData=self.getCurrentGroupData()
            poseListData=groupData['poseListData']
            poseCtrlData=poseListData[poseName]['orientData']['data']
            currentSet=set(poseCtrlData.keys())
            ctrlSet=ctrlSet|currentSet
        ctrlList=[]
        ns=self.getCurrentNameSpace()
        for i in ctrlSet:
            ctrl=ns+i
            if(cmds.objExists(ctrl)):
                ctrlList.append(ctrl)
        print ctrlList
        if(len(ctrlList)>0):
            try:
                cmds.undoInfo(swf=0)
                cmds.select(ctrlList)
            finally:
                cmds.undoInfo(swf=1)


    def renamePose(self,oldName):
        result=cmds.promptDialog(t='Rename Pose',m='Enter Name:',tx=oldName,b=['OK', 'Cancel'],db='OK',cb='Cancel',ds='Cancel')
        if result != 'OK':
            return
        newName = cmds.promptDialog(q=True, tx=True)
        if(not self.nameRegex.match(newName)):
            raise RuntimeError,'The name is not in conformity with the rules!'
        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']
        if(poseListData.has_key(newName)):
            raise RuntimeError,'The name is repeated!'

        posItem=self.getPoseItem(oldName)
        oldPath=posItem['filePath']
        basePath=os.path.dirname(oldPath)
        newPath=os.path.join(basePath,newName+'.pose')
        try:
            os.rename(oldPath,newPath)
        except:
            pass
        else:
            poseListData[newName]=posItem
            del poseListData[oldName]
            posItem['btn'].setPoseName(newName)
            posItem['filePath']=newPath


    def getPoseItem(self,poseName):
        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']
        if(not poseListData.has_key(poseName)):
            raise RuntimeError,'%s is not exists.'%poseName
        poseItem=poseListData[poseName]
        return poseItem

    def mixturePose(self,poseName):
        cmds.floatSliderGrp('mpWeightFSG_ps',e=1,v=0)
        posItem=self.getPoseItem(poseName)
        poseCtrlData=posItem['orientData']['data']
        ns=self.getCurrentNameSpace()

        self.mixtureCtrlList=[]
        for ctrl in poseCtrlData:
            ctrlName=ns+ctrl
            if(not cmds.objExists(ctrlName)):
                continue
            poseAttrList=poseCtrlData[ctrl]
            for attr,newVal in poseAttrList:
                oldVal=cmds.getAttr(ctrlName+'.'+attr)
                if(round(oldVal,4)!=round(newVal,4)):
                    self.mixtureCtrlList.append([ctrlName+'.'+attr,oldVal,newVal])
        cmds.text('mpPoseNameT_ps',e=1,l=poseName)
        cmds.rowLayout('mixturePoseRL_ps',e=1,vis=1)



    def mixturePoseWeightChange(self,val=None):
        if(not val):
            cmds.floatSliderGrp('mpWeightFSG_ps',q=1,v=1)

        try:
            cmds.undoInfo(ock=1)
            self.mixturePoseSetValue(val)
        finally:
            cmds.undoInfo(cck=1)


    def mixturePoseWeightDrag(self,val=None):
        if(not val):
            cmds.floatSliderGrp('mpWeightFSG_ps',q=1,v=1)
        try:
            cmds.undoInfo(swf=0)
            self.mixturePoseSetValue(val)
        finally:
            cmds.undoInfo(swf=1)

    def mixturePoseSetValue(self,weight):
        for attr,oldVal,newVal in self.mixtureCtrlList:
            finallyVal=oldVal*(1-weight)+newVal*weight
            try:
                cmds.setAttr(attr,finallyVal)
            except:
                pass

    def keyPose(self,poseName):
        posItem=self.getPoseItem(poseName)
        poseCtrlData=posItem['orientData']['data']
        ns=self.getCurrentNameSpace()
        try:
            cmds.undoInfo(ock=1)
            for ctrl in poseCtrlData:
                ctrlName=ns+ctrl
                if(not cmds.objExists(ctrlName)):
                    continue
                poseAttrList=poseCtrlData[ctrl]
                for attr,newVal in poseAttrList:
                    oldVal=cmds.getAttr(ctrlName+'.'+attr)
                    if(round(oldVal,4)!=round(newVal,4)):
                        try:
                            cmds.setKeyframe(ctrlName,at=attr)
                        except:
                            pass
        finally:
            cmds.undoInfo(cck=1)
    def assignPose(self,poseName):
        posItem=self.getPoseItem(poseName)
        poseCtrlData=posItem['orientData']['data']
        ns=self.getCurrentNameSpace()
        try:
            cmds.undoInfo(ock=1)
            for ctrl in poseCtrlData:
                ctrlName=ns+ctrl
                if(not cmds.objExists(ctrlName)):
                    continue
                poseAttrList=poseCtrlData[ctrl]
                for attr,newVal in poseAttrList:
                    oldVal=cmds.getAttr(ctrlName+'.'+attr)
                    if(round(oldVal,4)!=round(newVal,4)):
                        try:
                            cmds.setAttr(ctrlName+'.'+attr,newVal)
                        except:
                            pass
        finally:
            cmds.undoInfo(cck=1)


    def getExistsNameSpace(self,obj=None):
        allNS=cmds.namespaceInfo(':',lon=1)
        nsList=[]
        for i in allNS:
            ns=i+':'
            allChild=cmds.namespaceInfo(ns,lod=1)
            if(allChild==None):
                continue
            if(obj and not(cmds.objExists(ns+obj))):
                continue
            nsList.append(ns)
        nsList.append(':')
        return nsList

    def refreshNamespace(self):
        if(not cmds.formLayout('poseMainFL_ps',q=1,ex=1)):
            return
        old=cmds.optionMenu('nameSpaceOM_ps',q=1,v=1)

        itemList=cmds.optionMenu('nameSpaceOM_ps',q=1,ils=1)
        if(itemList):
            for i in itemList:
                cmds.deleteUI(i)

        self.nsList=self.getExistsNameSpace()
        for i in self.nsList:
            cmds.menuItem(l=i,p='nameSpaceOM_ps')

        if(old in self.nsList):
            cmds.optionMenu('nameSpaceOM_ps',e=1,v=old)

        if(cmds.checkBox('nsLockCB_ps',q=1,v=1)):
            self.setNameSpaceFromSelection()


    def setNameSpaceFromSelection(self,*args):
        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return

        pref=sel[0].split(':')
        curNS=pref[0]+':' if(len(pref)==2) else ':'
        
        if(curNS in self.nsList):
            cmds.optionMenu('nameSpaceOM_ps',e=1,v=curNS)


    def getCurrentNameSpace(self):
        return cmds.optionMenu('nameSpaceOM_ps',q=1,v=1)


    def getCurrentGroupData(self,path=''):
        if(path==''):
            selTab=cmds.tabLayout('poseMainTL_ps',q=1,st=1)
            groupName=cmds.paneLayout(selTab,q=1,ann=1)
        else:
            groupName=os.path.basename(os.path.dirname(path))
            print groupName
        return self.allGroupData[groupName]

    def poseButtonClickProc(self,poseName):
        print poseName
        # self.ctrl.clearSeletion()
        # 
    def getSettingData(self):
        docDir = cmds.internalVar(userAppDir=True)
        self.poseLibsPath=docDir+'PoseLibs/'
        if(not os.path.exists(self.poseLibsPath)):
            os.makedirs(self.poseLibsPath)
        self.defaultGroupPath=self.poseLibsPath+'/Default'
        if(not os.path.exists(self.defaultGroupPath)):
            os.makedirs(self.defaultGroupPath)

        self.settingData={'projectPathList':[self.poseLibsPath],'iconSize':[20,300,60]}

        self.settingFile=self.poseLibsPath+'/setting.ini'
        if(not os.path.exists(self.settingFile)):
            with open(self.settingFile,'w') as fileHandle:
                pickle.dump(self.settingData,fileHandle)
        else:
            with open(self.settingFile,'r') as fileHandle:
                self.settingData=pickle.load(fileHandle)

    def setupSettingUI(self):
        cmds.treeView('libPathListTV_pls',e=1,ra=1)
        for i in self.settingData['projectPathList']:
            cmds.treeView('libPathListTV_pls',e=1,ai=[i,''])
        iconSize=self.settingData['iconSize']

        cmds.intField('iconMinIF_pls',e=1,v=iconSize[0])
        cmds.intField('iconMaxIF_pls',e=1,v=iconSize[1])
        cmds.intField('iconDefaultIF_pls',e=1,v=iconSize[2])
    def addLibPath(self,*args):
        path=cmds.fileDialog2(fm=3,okc='Set',cap='Choose Lib Path')
        if(path==None):return
        newPath=path[0]+'/'
        if(newPath not in self.settingData['projectPathList']):
            cmds.treeView('libPathListTV_pls',e=1,ai=[newPath,''])
    def removeLibPath(self,*args):
        selI=cmds.treeView('libPathListTV_pls',q=1,si=1)
        cmds.treeView('libPathListTV_pls',e=1,ra=1)
        for i in self.settingData['projectPathList']:
            if(i not in selI):
                cmds.treeView('libPathListTV_pls',e=1,ai=[i,''])

    def pathTVSelectionChange(self,*args):
        selI=cmds.treeView('libPathListTV_pls',q=1,si=1)
        cmds.columnLayout('libGroupCL_pls',e=1,vis=(selI!=None))
        cmds.treeView('libGroupListTV_pls',e=1,ra=1)
        if(not selI):
            return
        projectPath=selI[0]
        subList=os.listdir(projectPath)
        poseGroupList=[]
        for sub in subList:
            subPath=projectPath+sub
            if(os.path.isdir(subPath)):
                poseGroupList.append(subPath)
        poseGroupList.sort(self.TimeCompare)
        for i in poseGroupList:
            name=os.path.basename(i)
            cmds.treeView('libGroupListTV_pls',e=1,ai=[name,''])
    def newLibGroup(self,*args):
        selI=cmds.treeView('libPathListTV_pls',q=1,si=1)
        if(not selI):
            return
        projectPath=selI[0]
        result=cmds.promptDialog(t='New Group',m='Enter Name:',b=['OK', 'Cancel'],db='OK',cb='Cancel',ds='Cancel')
        if result != 'OK':
            return
        newName = cmds.promptDialog(q=True, tx=True)
        if(not self.nameRegex.match(newName)):
            raise RuntimeError,'The name is not in conformity with the rules!'
        os.makedirs(os.path.join(projectPath,newName))
        self.pathTVSelectionChange()

    def removeLibGroup(self,*args):
        selI=cmds.treeView('libPathListTV_pls',q=1,si=1)
        if(not selI):
            return
        projectPath=selI[0]
        groupSelI=cmds.treeView('libGroupListTV_pls',q=1,si=1)
        if(not groupSelI):
            return
        for groupName in groupSelI:
            shutil.rmtree(os.path.join(projectPath,groupName))
        self.pathTVSelectionChange()

    def saveSettingData(self,*args):
        allI=cmds.treeView('libPathListTV_pls',q=1,ch=1)
        if(allI==None):
            allI=[]
        self.settingData['projectPathList']=allI

        minV=cmds.intField('iconMinIF_pls',q=1,v=1)
        maxV=cmds.intField('iconMaxIF_pls',q=1,v=1)
        defualtV=cmds.intField('iconDefaultIF_pls',q=1,v=1)
        self.settingData['iconSize']=[minV,maxV,defualtV]

        with open(self.settingFile,'w') as fileHandle:
            pickle.dump(self.settingData,fileHandle)

        self.PoseLibWin()
        if(cmds.window('sdd_PoseLibSettingWin_pls',q=True,ex=True)):cmds.deleteUI('sdd_PoseLibSettingWin_pls')

    def cancelSetting(self,*args):
        if(cmds.window('sdd_PoseLibSettingWin_pls',q=True,ex=True)):cmds.deleteUI('sdd_PoseLibSettingWin_pls')
    def PoseLibSettingWin(self):
        if(cmds.window('sdd_PoseLibSettingWin_pls',q=True,ex=True)):cmds.deleteUI('sdd_PoseLibSettingWin_pls')
        cmds.window('sdd_PoseLibSettingWin_pls',t=u'PoseLib Setting',s=False,wh=(400, 280))
        cmds.columnLayout('mainCL_pls',adj=True,rs=5)
        cmds.frameLayout('projectMainFL_pls',cll=True,l=u'Project Setting')
        cmds.paneLayout('projectMainPL_pls',cn=u'vertical2',ps=[[1, 65L, 65L], [2, 35L, 35L]])
        cmds.columnLayout('libPathCL_pls',adj=True,rs=5)
        cmds.rowLayout('libPathRL_pls',nc=4,adj=2)
        cmds.text(l=u'Libs Path List:')
        cmds.text(l=u'')
        cmds.iconTextButton('addPathITB_pls',i=u'addClip.png',c=self.addLibPath)
        cmds.iconTextButton('delPathITB_pls',i=u'removeRenderable.png',c=self.removeLibPath)
        cmds.treeView('libPathListTV_pls',p='libPathCL_pls',h=120,scc=self.pathTVSelectionChange)
        cmds.columnLayout('libGroupCL_pls',p='projectMainPL_pls',vis=False,adj=True,rs=5)
        cmds.rowLayout('groupRL_pls',nc=4,adj=2)
        cmds.text(l=u'Group List:')
        cmds.text(l=u'')
        cmds.iconTextButton('addGroupITB_pls',i=u'addClip.png',c=self.newLibGroup)
        cmds.iconTextButton('delGroupITB_pls',i=u'removeRenderable.png',c=self.removeLibGroup)
        cmds.treeView('libGroupListTV_pls',p='libGroupCL_pls',h=120)
        cmds.frameLayout('uiSettingMainFL_pls',p='mainCL_pls',cll=True,l=u'UI Setting')
        cmds.columnLayout('uiSettingMainCL_pls',adj=True,rs=5)
        cmds.rowLayout('iconSizeRL_pls',nc=7)
        cmds.text(w=70,l=u'Icon Size:',al=u'left')
        cmds.text(w=50,l=u'Min',al=u'right')
        cmds.intField('iconMinIF_pls',w=40,v=20,min=0)
        cmds.text(w=50,l=u'Max',al=u'right')
        cmds.intField('iconMaxIF_pls',w=40,v=300,min=0)
        cmds.text(w=50,l=u'Default',al=u'right')
        cmds.intField('iconDefaultIF_pls',w=40,v=60,min=0)
        cmds.separator(p='mainCL_pls')
        cmds.rowLayout(p='mainCL_pls',nc=2)
        cmds.button(w=200,l=u'Save',c=self.saveSettingData)
        cmds.button(w=200,l=u'Cancel',c=self.cancelSetting)
        cmds.showWindow('sdd_PoseLibSettingWin_pls')

        self.setupSettingUI()


    def deleteSelectionItem(self,sel):
        ret=cmds.confirmDialog( t='Confirm', m='delete %s pose ?'%(len(sel)), b=['Yes','No'], db='Yes', cb='No', ds='No' )
        if(ret!='Yes'):
            return
        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']
        for i in sel:
            iconBtn=poseListData[i]['btn']
            os.remove(poseListData[i]['filePath'])
            del poseListData[i]
            groupData['ctrl'].removeWidget(iconBtn)
            iconBtn.setParent(None)

    def hexStrToImage(self,hexStr):
        img=QtGui.QImage()
        img.loadFromData(QtCore.QByteArray.fromBase64(hexStr),'jpg')
        return img
    def newPose(self,*args):
        self.selectCtrl=cmds.ls(sl=1)
        if(len(self.selectCtrl)==0):
            return
        self.NewPoseWin()
        cmds.textField('poseNameTF_psn',e=1,tx=self.getTempPoseName())

    def getTempPoseName(self):
        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']
        startIdx=1
        while True:
            poseName='pose%03d'%(startIdx)
            if(not poseListData.has_key(poseName)):
                break
            startIdx+=1
        return poseName



    def createPose(self,*args):
        assert cmds.formLayout('poseMainFL_ps',q=True,ex=True)
        poseName=cmds.textField('poseNameTF_psn',q=1,tx=1)
        if(not self.nameRegex.match(poseName)):
            raise RuntimeError,'The name is not in conformity with the rules!'

        groupData=self.getCurrentGroupData()
        poseListData=groupData['poseListData']

        if(poseListData.has_key(poseName)):
            raise RuntimeError,'The name is repeated!'

        poseItemData={}
        poseItemData['data']=self.getSelectPoseData()
        poseItemData['image']=self.grabControlImageStr('modelEditor1_psn')

        filePath=groupData['path']+'/%s.pose'%poseName
        print filePath
        with open(filePath,'w') as fileHandle:
            pickle.dump(poseItemData,fileHandle)

        self.addPoseToView(filePath)

        if(cmds.window('sdd_newPoseWin_psn',q=True,ex=True)):cmds.deleteUI('sdd_newPoseWin_psn')

    def grabControlImageStr(self,ctrlId):
        ptr=OpenMayaUI.MQtUtil.findControl(ctrlId)
        assert ptr
        widget=shiboken.wrapInstance(long(ptr), QtGui.QWidget)
        pp=QtGui.QPixmap.grabWindow(widget.winId(),0,0,-1,-1)
        buf = QtCore.QBuffer()
        pp.save(buf,'jpg')
        return buf.buffer().toBase64().data()

    def getSelectPoseData(self,*args):
        poseCtrlData={}
        for ctrl in self.selectCtrl:
            poseAttrList=[]
            attrList=cmds.listAttr(ctrl,k=1)
            if(attrList==None):
                continue
            for attr in attrList:
                val=cmds.getAttr(ctrl+'.'+attr)
                poseAttrList.append([attr,val])
            noNSCtrl=ctrl.split(':')[-1]
            poseCtrlData[noNSCtrl]=poseAttrList
        return poseCtrlData

    def initNewPoseUI(self):
        print self.npShowType
        cmds.checkBoxGrp('showObjTypeCBG_psn',e=1,va4=self.npShowType)
        cmds.modelEditor('modelEditor1_psn',e=1,pm=self.npShowType[0],nc=self.npShowType[1],j=self.npShowType[2],ns=self.npShowType[3])

    def NewPoseWin(self):
        if(cmds.window('sdd_newPoseWin_psn',q=True,ex=True)):cmds.deleteUI('sdd_newPoseWin_psn')
        cmds.window('sdd_newPoseWin_psn',t=u'NewPose',s=False,mnb=False,mxb=False,wh=[312, 401])
        cmds.frameLayout(cll=True,lv=False,mh=5,mw=5)
        cmds.columnLayout('mainCL_psn',adj=True,rs=5)
        cmds.formLayout('formLayout1_psn',w=300,h=300)
        cmds.modelEditor('modelEditor1_psn')
        cmds.checkBoxGrp('showObjTypeCBG_psn',p='mainCL_psn',cw=[[1, 70], [2, 70], [3, 70], [4, 70]],ncb=4,l1=u'Mesh',l2=u'Curve',l3=u'Joint',l4=u'Nurbs',v1=True,cc=self.showTypeChange)
        cmds.textField('poseNameTF_psn',p='mainCL_psn',h=25,tx=u'pose01')
        cmds.button('createB_psn',p='mainCL_psn',w=150,h=30,l=u'Create',c=self.createPose)
        cmds.formLayout('formLayout1_psn',e=1,af=[[u'modelEditor1_psn', 'top', 0], [u'modelEditor1_psn', 'left', 0], [u'modelEditor1_psn', 'right', 0], [u'modelEditor1_psn', 'bottom', 0]])
        cmds.modelEditor('modelEditor1_psn',e=1,da=u'smoothShaded',hud=False,sel=False,pm=True,gr=False,m=False,alo=False,jx=True)
        cmds.showWindow('sdd_newPoseWin_psn')

        self.initNewPoseUI()

    def showTypeChange(self,*args):
        self.npShowType=cmds.checkBoxGrp('showObjTypeCBG_psn',q=1,va4=1)
        cmds.modelEditor('modelEditor1_psn',e=1,pm=self.npShowType[0],nc=self.npShowType[1],j=self.npShowType[2],ns=self.npShowType[3])

def PosLibUI():
    global PosLibModule
    PosLibModule=PoseLibraryModule()
    # self=PosLibModule
    PosLibModule.show()


