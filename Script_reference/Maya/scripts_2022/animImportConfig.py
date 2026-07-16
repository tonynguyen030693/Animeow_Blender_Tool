from maya import cmds
from collections import OrderedDict
import pickle
import functools

class BOutputJointConfigs():
	def __init__(self):
		self.copyData=None
	def initJointList(self):
		spineList=['Hips','Spine','Spine1', 'Spine2', 'Spine3', 'Spine4','Chest','ChestMid', 'Neck1', 'Neck2', 'Neck3','Head']
		self.addTreeViewItem('',spineList)

		LArmList=['LeftShoulder','LeftArm', 'LeftForeArm', 'LeftHand']
		self.addTreeViewItem('ChestMid',LArmList)

		LTumb=['LeftHandThumbRoot', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'LeftHandThumb4']
		self.addTreeViewItem('LeftHand',LTumb)

		LIndex=['LeftHandIndexRoot', 'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandIndex4' ]
		self.addTreeViewItem('LeftHand',LIndex)

		LMiddle=['LeftHandMiddleRoot', 'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandMiddle4']
		self.addTreeViewItem('LeftHand',LMiddle)

		LRing=['LeftHandRingRoot', 'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4']
		self.addTreeViewItem('LeftHand',LRing)

		LPinky=['LeftHandPinkyRoot', 'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4']
		self.addTreeViewItem('LeftHand',LPinky)

		LLeg=['LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'LeftToeBaseEnd']
		self.addTreeViewItem('Hips',LLeg)

		LArmList=['RightShoulder','RightArm', 'RightForeArm', 'RightHand']
		self.addTreeViewItem('ChestMid',LArmList)

		LTumb=['RightHandThumbRoot', 'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumb4']
		self.addTreeViewItem('RightHand',LTumb)

		LIndex=['RightHandIndexRoot', 'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4' ]
		self.addTreeViewItem('RightHand',LIndex)

		LMiddle=['RightHandMiddleRoot', 'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandMiddle4']
		self.addTreeViewItem('RightHand',LMiddle)

		LRing=['RightHandRingRoot', 'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandRing4']
		self.addTreeViewItem('RightHand',LRing)

		LPinky=['RightHandPinkyRoot', 'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4']
		self.addTreeViewItem('RightHand',LPinky)

		LLeg=['RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase', 'RightToeBaseEnd']
		self.addTreeViewItem('Hips',LLeg)


		self.getDefaultData()
		self.updateInfo()

	def addTreeViewItem(self,pObj,itemList):
		for i in itemList:
			cmds.treeView('ogcListTV_br',e=1,ai=[i,pObj])
			pObj=i
	def getDefaultData(self):
		jntList=cmds.treeView('ogcListTV_br',q=1,ch=1)
		self.outJntData=OrderedDict()
		for i in jntList:
			self.outJntData[i]={'fkCtrl':i}

	def updateInfo(self):
		for i in self.outJntData:
			if(self.outJntData[i]==None):
				cmds.treeView('ogcListTV_br',e=1,dls=[i,''])
			else:
				print i,self.outJntData[i]['fkCtrl']
				fkCtrl=self.outJntData[i]['fkCtrl']
				cmds.treeView('ogcListTV_br',e=1,dls=[i,'  -> %s'%(fkCtrl)])



	def getParentItem(self,item):
		while True:
			pItem=cmds.treeView('ogcListTV_br',q=1,ip=item)
			if(pItem==''):
				return None
			if(self.outJntData[pItem]!=None):
				return self.outJntData[pItem]['fkCtrl']
			item=pItem


	def treeSelectChange(self):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		self.resetOptionUI()
		if(self.outJntData[selI[0]]!=None):
			fkCtrl=self.outJntData[selI[0]]['fkCtrl']
			cmds.textFieldGrp('ogcOutNameTFG_br',e=1,tx=fkCtrl)
		# if(cmds.objExists(selI[0])):
		# 	cmds.select(selI[0])

	def setFromSelect(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		sel=cmds.ls(sl=1)
		if(len(sel)==0):
			return
		self.outJntData[selI[0]]['fkCtrl']=sel[0]
		cmds.textFieldGrp('ogcOutNameTFG_br',e=1,tx=sel[0])
		self.updateInfo()
	def clearData(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		self.resetOptionUI()
		self.outJntData[selI[0]]=None
		self.updateInfo()
	def resetOptionUI(self,*args):
		cmds.textFieldGrp('ogcOutNameTFG_br',e=1,tx='')

	def modifyData(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return

		fkCtrl=cmds.textFieldGrp('ogcOutNameTFG_br',q=1,tx=1)
		if(fkCtrl==''):
			self.outJntData[selI[0]]=None
		else:
			self.outJntData[selI[0]]={'fkCtrl':fkCtrl}
		self.updateInfo()
	def saveFile(self,*args):
		path=cmds.fileDialog2(ff='Joint Mapping Files .jmap(*.jmap)',fm=0)
		if(path==None):return
		filePath=path[0]
		with open(filePath,'w') as fileHandle:
			pickle.dump(self.outJntData.items(),fileHandle)
	def openFile(self,*args):
		path=cmds.fileDialog2(ff='Joint Mapping Files .jmap(*.jmap)',fm=1)
		if(path==None):return
		filePath=path[0]
		with open(filePath,'r') as fileHandle:
			temp=OrderedDict(pickle.load(fileHandle))
		for i in self.outJntData:
			self.outJntData[i]=temp[i]
		self.updateInfo()

	def mirrorData(self,*args):
		prefix=args[0]
		str1=cmds.textField('ogcMirStr1TF_br',q=1,tx=1)
		str2=cmds.textField('ogcMirStr2TF_br',q=1,tx=1)
		for i in self.outJntData:
			if(i[:2]!=prefix):
				continue
			mirI=self.getMirrorName(i)
			if(not self.outJntData.has_key(mirI)):
				continue
			if(self.outJntData[i]==None):
				self.outJntData[mirI]=None
			else:
				fkCtrl=self.outJntData[i]['fkCtrl']
				newName=fkCtrl.replace(str1,str2)
		
				self.outJntData[mirI]={'fkCtrl':newName}
		self.updateInfo()
	def copyDataProc(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		self.copyData=selI[0]
	def pasteDataProc(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		fkCtrl=self.outJntData[self.copyData]['fkCtrl']
		
		for i in selI:
			self.outJntData[i]={'fkCtrl':fkCtrl}
		self.updateInfo()
	def getMirrorName(self,obj):
		L_,R_='Left','Right'
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
	def checkMapAxis(self,jntLoc,ctrlLoc):
		attrList=['tx','ty','tz','rx','ry','rz']
		mapAxisData=[]
		for attr in attrList:
			self.resetTransAttr(jntLoc)
			cmds.setAttr(jntLoc+'.'+attr,1)
			mapAttr,sige=self.getAxis(ctrlLoc)
			mapAxisData.append([attr,mapAttr,sige])
		return mapAxisData

	def getAxis(self,ctrlLoc):
		attrList=['tx','ty','tz','rx','ry','rz']
		for attr in attrList:
			val=cmds.getAttr(ctrlLoc+'.'+attr)
			if(abs(round(val,0))==1):
				sige=1 if(val>0) else -1
				return attr,sige

	def resetTransAttr(self,obj):
		attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
		dValList=[0,0,0,0,0,0,1,1,1]
		for attr,dv in zip(attrList,dValList):
			cmds.setAttr(obj+'.'+attr,dv)

	def outputJoint(self,*args):
		for i in self.outJntData:
			if(self.outJntData[i]==None):
				continue
			jnt=i
			ctrl=self.outJntData[i]['fkCtrl']
			print jnt,ctrl

			jntLoc=cmds.group(em=1,n=jnt+'_loc')
			ctrlLoc=cmds.group(em=1,n=ctrl+'_loc')
			cmds.parent(jntLoc,jnt)
			cmds.parent(ctrlLoc,ctrl)
			self.resetTransAttr(jntLoc)
			self.resetTransAttr(ctrlLoc)

			cmds.parentConstraint(jntLoc,ctrlLoc,mo=1)
			mapList=self.checkMapAxis(jntLoc,ctrlLoc)

			self.outJntData[i]['remap']=mapList


			#cmds.parentConstraint(drJnt,outJnt,mo=1)
			#cmds.scaleConstraint(drJnt,outJnt,mo=1)

	def setDriverType(self,*args):
		val=args[0]
		selI=cmds.treeView('drJointListTV_br',q=1,si=1)
		if(selI==None):
			return
		for i in selI:
			self.drData[i]=val
		self.updateDrInfo()
	def updateDrInfo(self):
		self.updateParent()
		for i in self.drData:
			if(self.drData[i]==None):
				cmds.treeView('drJointListTV_br',e=1,dls=[i,''])
			else:
				cmds.treeView('drJointListTV_br',e=1,dls=[i,'   %s'%self.drData[i]])

	def outputJointConfig(self):
		if(cmds.window('sdd_outputJointConfig_br',q=True,ex=True)):cmds.deleteUI('sdd_outputJointConfig_br')
		cmds.window('sdd_outputJointConfig_br',wh=(630, 560))
		cmds.tabLayout('tabLayout1_br',cr=True)
		cmds.formLayout('ogcMainFL_br')
		cmds.rowLayout('ogcMirrorRL_br',nc=6)
		cmds.textField('ogcMirStr1TF_br',w=150,tx=u'L_')
		cmds.textField('ogcMirStr2TF_br',w=155,tx=u'R_')
		cmds.button(w=80,h=20,l=u'Mirror',c=functools.partial(self.mirrorData,'L_'))
		cmds.text(l=u'')
		cmds.button(w=100,h=20,l=u'Copy Data',c=self.copyDataProc)
		cmds.button(w=100,h=20,l=u'Paste Data',c=self.pasteDataProc)
		cmds.treeView('ogcListTV_br',p='ogcMainFL_br',h=50,scc=self.treeSelectChange)
		cmds.columnLayout('ogcOptionCL_br',p='ogcMainFL_br',adj=True)
		cmds.rowLayout('rowLayout1_br',nc=3,adj=1)
		cmds.columnLayout(adj=True)
		cmds.textFieldGrp('ogcOutNameTFG_br',cw=[[1, 60]],adj=2,l=u'Ctrl Name:',cc=self.modifyData)
		cmds.button(p='rowLayout1_br',w=50,l=u'<',c=self.setFromSelect)
		cmds.button(p='rowLayout1_br',w=80,h=40,l=u'Clear',c=self.clearData)
		cmds.button('ogcOpenB_br',p='ogcMainFL_br',h=30,l=u'Open',c=self.openFile)
		cmds.button('ogcSaveB_br',p='ogcMainFL_br',h=30,l=u'Save',c=self.saveFile)
		cmds.button('ogcExportB_br',p='ogcMainFL_br',h=50,l=u'Create Export Joint',c=self.outputJoint)
		self.initJointList()
		cmds.tabLayout('tabLayout1_br',e=1,tli=[[1, u'Joint Config']])
		cmds.formLayout('ogcMainFL_br',e=1,af=[[u'ogcMirrorRL_br', 'left', 5], [u'ogcMirrorRL_br', 'right', 5], [u'ogcListTV_br', 'left', 5], [u'ogcListTV_br', 'right', 5], [u'ogcOptionCL_br', 'left', 5], [u'ogcOptionCL_br', 'right', 5], [u'ogcOpenB_br', 'top', 5], [u'ogcOpenB_br', 'left', 5], [u'ogcSaveB_br', 'top', 5], [u'ogcSaveB_br', 'right', 5], [u'ogcExportB_br', 'left', 5], [u'ogcExportB_br', 'right', 5], [u'ogcExportB_br', 'bottom', 5]],ac=[[u'ogcMirrorRL_br', 'top', 5, u'ogcOpenB_br'], [u'ogcListTV_br', 'top', 5, u'ogcMirrorRL_br'], [u'ogcListTV_br', 'bottom', 5, u'ogcOptionCL_br'], [u'ogcOptionCL_br', 'bottom', 5, u'ogcExportB_br'], [u'ogcSaveB_br', 'left', 5, u'ogcOpenB_br']],ap=[[u'ogcOpenB_br', 'right', 5, 50]])
		cmds.showWindow('sdd_outputJointConfig_br')

BOutputConfigModule=BOutputJointConfigs()
BOutputConfigModule.outputJointConfig()
self=BOutputConfigModule

