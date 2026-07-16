from maya import cmds
from collections import OrderedDict
import pickle
import functools

class BOutputJointConfigs():
	def __init__(self):
		self.copyData=None
	def initJointList(self):
		spineList=['Hips_dr','spine_1_dr', 'spine_2_dr', 'spine_3_dr', 'spine_4_dr', 'spine_5_dr','chest_dr','chect_mid_dr', 'neck_1_dr', 'neck_2_dr', 'neck_3_dr','head_dr', 'head_end_dr']
		self.addTreeViewItem('',spineList)
		LArmList=['L_shoulder_dr','L_arm_dr', 'L_arm_sec1_dr', 'L_arm_sec2_dr', 'L_arm_sec3_dr', 'L_arm_sec4_dr', 'L_arm_sec5_dr','L_lowarm_dr', 'L_lowarm_sec1_dr', 'L_lowarm_sec2_dr', 'L_lowarm_sec3_dr', 'L_lowarm_sec4_dr', 'L_lowarm_sec5_dr','L_hand_dr',]
		self.addTreeViewItem('chect_mid_dr',LArmList)

		LTumb=['L_thumbfinger_dr', 'L_thumbfinger_1_dr', 'L_thumbfinger_2_dr', 'L_thumbfinger_3_dr', 'L_thumbfinger_4_dr']
		self.addTreeViewItem('L_hand_dr',LTumb)

		LIndex=['L_indexfinger_dr','L_indexfinger_1_dr', 'L_indexfinger_2_dr', 'L_indexfinger_3_dr', 'L_indexfinger_4_dr',  ]
		self.addTreeViewItem('L_hand_dr',LIndex)

		LMiddle=['L_middlefinger_dr','L_middlefinger_1_dr', 'L_middlefinger_2_dr', 'L_middlefinger_3_dr', 'L_middlefinger_4_dr' ]
		self.addTreeViewItem('L_hand_dr',LMiddle)

		LRing=['L_ringfinger_dr','L_ringfinger_1_dr', 'L_ringfinger_2_dr', 'L_ringfinger_3_dr', 'L_ringfinger_4_dr']
		self.addTreeViewItem('L_hand_dr',LRing)

		LPinky=['L_pinkyfinger_dr','L_pinkyfinger_1_dr', 'L_pinkyfinger_2_dr', 'L_pinkyfinger_3_dr', 'L_pinkyfinger_4_dr']
		self.addTreeViewItem('L_hand_dr',LPinky)

		LLeg=['L_leg_dr', 'L_leg_sec1_dr', 'L_leg_sec2_dr', 'L_leg_sec3_dr', 'L_leg_sec4_dr', 'L_leg_sec5_dr',  'L_lowleg_dr', 'L_lowleg_sec1_dr', 'L_lowleg_sec2_dr', 'L_lowleg_sec3_dr', 'L_lowleg_sec4_dr', 'L_lowleg_sec5_dr', 'L_foot_dr', 'L_toebase_dr', 'L_toeend_dr']
		self.addTreeViewItem('Hips_dr',LLeg)

		RArmList=['R_shoulder_dr','R_arm_dr', 'R_arm_sec1_dr', 'R_arm_sec2_dr', 'R_arm_sec3_dr', 'R_arm_sec4_dr', 'R_arm_sec5_dr','R_lowarm_dr', 'R_lowarm_sec1_dr', 'R_lowarm_sec2_dr', 'R_lowarm_sec3_dr', 'R_lowarm_sec4_dr', 'R_lowarm_sec5_dr','R_hand_dr',]
		self.addTreeViewItem('chect_mid_dr',RArmList)

		RTumb=['R_thumbfinger_dr', 'R_thumbfinger_1_dr', 'R_thumbfinger_2_dr', 'R_thumbfinger_3_dr', 'R_thumbfinger_4_dr']
		self.addTreeViewItem('R_hand_dr',RTumb)

		RIndex=['R_indexfinger_dr','R_indexfinger_1_dr', 'R_indexfinger_2_dr', 'R_indexfinger_3_dr', 'R_indexfinger_4_dr',  ]
		self.addTreeViewItem('R_hand_dr',RIndex)

		RMiddle=['R_middlefinger_dr','R_middlefinger_1_dr', 'R_middlefinger_2_dr', 'R_middlefinger_3_dr', 'R_middlefinger_4_dr' ]
		self.addTreeViewItem('R_hand_dr',RMiddle)

		RRing=['R_ringfinger_dr','R_ringfinger_1_dr', 'R_ringfinger_2_dr', 'R_ringfinger_3_dr', 'R_ringfinger_4_dr']
		self.addTreeViewItem('R_hand_dr',RRing)

		RPinky=['R_pinkyfinger_dr','R_pinkyfinger_1_dr', 'R_pinkyfinger_2_dr', 'R_pinkyfinger_3_dr', 'R_pinkyfinger_4_dr']
		self.addTreeViewItem('R_hand_dr',RPinky)

		RLeg=['R_leg_dr', 'R_leg_sec1_dr', 'R_leg_sec2_dr', 'R_leg_sec3_dr', 'R_leg_sec4_dr', 'R_leg_sec5_dr',  'R_lowleg_dr', 'R_lowleg_sec1_dr', 'R_lowleg_sec2_dr', 'R_lowleg_sec3_dr', 'R_lowleg_sec4_dr', 'R_lowleg_sec5_dr', 'R_foot_dr', 'R_toebase_dr', 'R_toeend_dr']
		self.addTreeViewItem('Hips_dr',RLeg)
		self.getDefaultData()
		self.updateInfo()

	def addTreeViewItem(self,pObj,itemList):
		for i in itemList:
			cmds.treeView('ogcListTV_br',e=1,ai=[i,pObj])
			cmds.treeView('drJointListTV_br',e=1,ai=[i,pObj])
			pObj=i
	def getDefaultData(self):
		jntList=cmds.treeView('ogcListTV_br',q=1,ch=1)
		self.outJntData=OrderedDict()
		self.drData=OrderedDict()
		for i in jntList:
			self.outJntData[i]={'outName':i[:-3]+'_Jnt','offset':(0,0,0)}
			self.drData[i]=None
	def updateInfo(self):
		self.updateParent()
		for i in self.outJntData:
			if(self.outJntData[i]==None):
				cmds.treeView('ogcListTV_br',e=1,dls=[i,''])
			else:
				outName=self.outJntData[i]['outName']
				offset=self.outJntData[i]['offset']
				cmds.treeView('ogcListTV_br',e=1,dls=[i,'  -> %s    %s,%s,%s'%(outName,int(offset[0]),int(offset[1]),int(offset[2]))])


	def updateParent(self):
		for i in self.outJntData:
			if(self.outJntData[i]==None):
				continue
			self.outJntData[i]['parent']=self.getParentItem(i)
	def getParentItem(self,item):
		while True:
			pItem=cmds.treeView('ogcListTV_br',q=1,ip=item)
			if(pItem==''):
				return None
			if(self.outJntData[pItem]!=None):
				return self.outJntData[pItem]['outName']
			item=pItem


	def treeSelectChange(self):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		self.resetOptionUI()
		if(self.outJntData[selI[0]]!=None):
			outName=self.outJntData[selI[0]]['outName']
			offset=self.outJntData[selI[0]]['offset']
			cmds.textFieldGrp('ogcOutNameTFG_br',e=1,tx=outName)
			cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v1=offset[0])
			cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v2=offset[1])
			cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v3=offset[2])
		if(cmds.objExists(selI[0])):
			cmds.select(selI[0])


	def clearData(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		self.resetOptionUI()
		self.outJntData[selI[0]]=None
		self.updateInfo()
	def resetOptionUI(self,*args):
		cmds.textFieldGrp('ogcOutNameTFG_br',e=1,tx='')
		cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v1=0)
		cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v2=0)
		cmds.floatFieldGrp('ogcOffsetFFG_br',e=1,v3=0)
	def modifyData(self,*args):
		selI=cmds.treeView('ogcListTV_br',q=1,si=1)
		if(selI==None):
			return
		v1=cmds.floatFieldGrp('ogcOffsetFFG_br',q=1,v1=1)
		v2=cmds.floatFieldGrp('ogcOffsetFFG_br',q=1,v2=1)
		v3=cmds.floatFieldGrp('ogcOffsetFFG_br',q=1,v3=1)
		offset=(v1,v2,v3)
		if(len(selI)>1):
			for i in selI:
				if(self.outJntData[i]==None):
					continue
				self.outJntData[i]['offset']=offset
		else:
			outName=cmds.textFieldGrp('ogcOutNameTFG_br',q=1,tx=1)
			if(outName==''):
				self.outJntData[selI[0]]=None
			else:
				self.outJntData[selI[0]]={'outName':outName,'offset':offset}
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
	def saveDrFile(self,*args):
		path=cmds.fileDialog2(ff='Driver Files .drini(*.drini)',fm=0)
		if(path==None):return
		filePath=path[0]
		with open(filePath,'w') as fileHandle:
			pickle.dump(self.drData.items(),fileHandle)

	def openDrFile(self,*args):
		path=cmds.fileDialog2(ff='Driver Files .drini(*.drini)',fm=1)
		if(path==None):return
		filePath=path[0]
		with open(filePath,'r') as fileHandle:
			self.drData=OrderedDict(pickle.load(fileHandle))
		self.updateDrInfo()
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
				outName=self.outJntData[i]['outName']
				newName=outName.replace(str1,str2)
				if(self.outJntData[mirI]!=None):
					offset=self.outJntData[mirI]['offset'][:]
				else:
					offset=self.outJntData[i]['offset'][:]
				self.outJntData[mirI]={'outName':newName,'offset':offset}
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
		outName=self.outJntData[self.copyData]['outName']
		offset=self.outJntData[self.copyData]['offset'][:]
		
		for i in selI:
			self.outJntData[i]={'outName':outName,'offset':offset[:]}
		self.updateInfo()
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
	def outputJoint(self,*args):
		OutputJointGrp=cmds.group(em=1,n='joint_grp')
		for i in self.outJntData:
			if(self.outJntData[i]==None):
				continue
			drJnt=i
			outJnt=self.outJntData[i]['outName']
			offset=self.outJntData[i]['offset']
			pObj=self.outJntData[i]['parent']
			outJnt=cmds.duplicate(drJnt,n=outJnt,rr=1,po=1)[0]
			cmds.parent(outJnt,OutputJointGrp)
			cmds.rotate(offset[0],offset[1],offset[2],outJnt,r=1,os=1,fo=1)
			cmds.makeIdentity(outJnt,a=1,t=1,r=1,s=1,n=0,pn=1)
			if(pObj):
				cmds.parent(outJnt,pObj)
			#cmds.parentConstraint(drJnt,outJnt,mo=1)
			#cmds.scaleConstraint(drJnt,outJnt,mo=1)
		cmds.select(OutputJointGrp)
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
		cmds.rowLayout('rowLayout1_br',nc=2,adj=3)
		cmds.columnLayout(adj=True)
		cmds.textFieldGrp('ogcOutNameTFG_br',cw=[[1, 60]],adj=2,l=u'Out Name:',cc=self.modifyData)
		cmds.floatFieldGrp('ogcOffsetFFG_br',cw=[[1, 60], [2, 152], [3, 152], [4, 152]],l=u'Offset:',nf=3,cc=self.modifyData)
		cmds.button(p='rowLayout1_br',w=80,h=40,l=u'Clear',c=self.clearData)
		cmds.button('ogcOpenB_br',p='ogcMainFL_br',h=30,l=u'Open',c=self.openFile)
		cmds.button('ogcSaveB_br',p='ogcMainFL_br',h=30,l=u'Save',c=self.saveFile)
		cmds.button('ogcExportB_br',p='ogcMainFL_br',h=50,l=u'Create Export Joint',c=self.outputJoint)
		cmds.formLayout('drMainFL_br',p='tabLayout1_br')
		cmds.button('drOpenB_br',h=30,l=u'Open',c=self.openFile)
		cmds.button('drSaveB_br',h=30,l=u'Save',c=self.saveFile)
		cmds.treeView('drJointListTV_br',h=50,scc=self.treeSelectChange)
		cmds.columnLayout('drOptionCL_br',adj=True,rs=5)
		cmds.rowLayout(nc=3)
		cmds.button(w=200,l=u'Direct',c=functools.partial(self.setDriverType,'Direct'))
		cmds.button(w=200,l=u'Angle')
		cmds.button(w=200,l=u'None')
		cmds.button(p='drOptionCL_br',h=50)
		self.initJointList()
		cmds.tabLayout('tabLayout1_br',e=1,sti=2,tli=[[1, u'Joint Config'], [2, u'Driver Config']])
		cmds.formLayout('ogcMainFL_br',e=1,af=[[u'ogcMirrorRL_br', 'left', 5], [u'ogcMirrorRL_br', 'right', 5], [u'ogcListTV_br', 'left', 5], [u'ogcListTV_br', 'right', 5], [u'ogcOptionCL_br', 'left', 5], [u'ogcOptionCL_br', 'right', 5], [u'ogcOpenB_br', 'top', 5], [u'ogcOpenB_br', 'left', 5], [u'ogcSaveB_br', 'top', 5], [u'ogcSaveB_br', 'right', 5], [u'ogcExportB_br', 'left', 5], [u'ogcExportB_br', 'right', 5], [u'ogcExportB_br', 'bottom', 5]],ac=[[u'ogcMirrorRL_br', 'top', 5, u'ogcOpenB_br'], [u'ogcListTV_br', 'top', 5, u'ogcMirrorRL_br'], [u'ogcListTV_br', 'bottom', 5, u'ogcOptionCL_br'], [u'ogcOptionCL_br', 'bottom', 5, u'ogcExportB_br'], [u'ogcSaveB_br', 'left', 5, u'ogcOpenB_br']],ap=[[u'ogcOpenB_br', 'right', 5, 50]])
		cmds.formLayout('drMainFL_br',e=1,af=[[u'drOpenB_br', 'top', 5], [u'drOpenB_br', 'left', 5], [u'drSaveB_br', 'top', 5], [u'drSaveB_br', 'right', 5], [u'drJointListTV_br', 'left', 5], [u'drJointListTV_br', 'right', 5], [u'drOptionCL_br', 'left', 5], [u'drOptionCL_br', 'right', 5], [u'drOptionCL_br', 'bottom', 0]],ac=[[u'drSaveB_br', 'left', 5, u'drOpenB_br'], [u'drJointListTV_br', 'top', 5, u'drOpenB_br'], [u'drJointListTV_br', 'bottom', 5, u'drOptionCL_br']],ap=[[u'drOpenB_br', 'right', 5, 50]])
		cmds.showWindow('sdd_outputJointConfig_br')

BOutputConfigModule=BOutputJointConfigs()
BOutputConfigModule.outputJointConfig()
self=BOutputConfigModule