from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim
from collections import OrderedDict
import pickle
import functools
import math
from maya import mel as mm
class GeneralUtility():
    @staticmethod
    def findNodeShape(objName,getAll=False):
        shapes = cmds.listRelatives(objName, s=True, pa=True)
        if not shapes:
            raise RuntimeError, '%s has no shape'%objName
        retList=[]
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject'%shape)
            if (not is_intermediate):
                retList.append(shape)
        if(len(retList)>0):
            if(getAll):
                return retList
            else:
                return retList[0]
        else:
            raise RuntimeError('Could not find shape on node {0}'.format(objName))
    @staticmethod
    def findNodeIntermediateShape(objName):
        shapes = cmds.listRelatives(objName, s=True, pa=True)
        if not shapes:
            raise RuntimeError, '%s has no shape'%objName
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject'%shape)
            if (is_intermediate and cmds.listConnections('%s.worldMesh' % shape,source=False)):
                return shape
        raise RuntimeError('Could not find shape on node {0}'.format(objName))
    @staticmethod
    def getComponentCenter(compList):
        center=[0,0,0]
        for comp in compList:
            pos=cmds.xform(comp,q=1,ws=1,t=1)
            center[0]+=pos[0]
            center[1]+=pos[1]
            center[2]+=pos[2]
        center[0]/=len(compList)
        center[1]/=len(compList)
        center[2]/=len(compList)
        return center
    @staticmethod
    def getObjectMatrix(obj):
        matList=cmds.xform(obj,q=1,ws=1,m=1)
        util=maya.OpenMaya.MScriptUtil()
        mat=OpenMaya.MMatrix()
        util.createMatrixFromList(matList,mat)
        return mat
    @staticmethod
    def transformationMatrix(mat,translate=None,rotate=None,space=OpenMaya.MSpace.kTransform):
        tranMat=OpenMaya.MTransformationMatrix(mat)
        if(translate):
            tranMat.translateBy(OpenMaya.MVector(translate[0],translate[1],translate[2]),space)
        if(rotate):
            tranMat.rotateBy(OpenMaya.MEulerRotation(rotate[0],rotate[1],rotate[2]),space)
        return tranMat.asMatrix()
    @staticmethod
    def getDistance(obj1,obj2): 
        t1=cmds.xform(obj1,q=1,ws=1,t=1)
        t2=cmds.xform(obj2,q=1,ws=1,t=1)
        p1=OpenMaya.MPoint(t1[0],t1[1],t1[2])
        p2=OpenMaya.MPoint(t2[0],t2[1],t2[2])
        return p1.distanceTo(p2)
    @staticmethod
    def getVector(obj1,obj2):
        if(not isinstance(obj1,OpenMaya.MPoint)):
            t1=cmds.xform(obj1,q=1,ws=1,t=1)
            p1=OpenMaya.MPoint(t1[0],t1[1],t1[2])
        else:
            p1=obj1
        if(not isinstance(obj2,OpenMaya.MPoint)):
            t2=cmds.xform(obj2,q=1,ws=1,t=1)
            p2=OpenMaya.MPoint(t2[0],t2[1],t2[2])
        else:
            p2=obj2
        return p2-p1
    @staticmethod
    def getPerpendicularVector(vec1,vec2):
        vec1=OpenMaya.MVector(vec1)
        vec2=OpenMaya.MVector(vec2)
        len2=vec1*vec2/vec2.length()
        vec2.normalize()
        pVec=vec2*len2
        return pVec-vec1
    @staticmethod
    def getPoleMoveVector(obj1,obj2,obj3,typ='first'):
        # obj1='L_arm'
        # obj2='L_lowarm'
        # obj3='L_hand'

        vec1=GeneralUtility.getVector(obj1,obj2)
        vec2=GeneralUtility.getVector(obj1,obj3)
        if(typ=='first'):
            pVec=GeneralUtility.getPerpendicularVector(vec2,vec1)
        else:
            pVec=GeneralUtility.getPerpendicularVector(vec1,vec2)
            pVec*=-1
        pVec.normalize()
        moveVec=pVec*vec1.length()
        return  moveVec

    @staticmethod
    def getWorldSpaceFront(obj,offsetRatate=[0,0,0]):
        mat=GeneralUtility.getObjectMatrix(obj)
        mat=GeneralUtility.transformationMatrix(mat,rotate=[math.radians(offsetRatate[0]),math.radians(offsetRatate[1]),math.radians(offsetRatate[2])])
        vec=OpenMaya.MVector(1,0,0)
        return vec*mat.inverse()
    @staticmethod
    def getWorldSpaceDirection(obj,Direct=[1,0,0]):
        mat=GeneralUtility.getObjectMatrix(obj)
        vec=OpenMaya.MVector(Direct[0],Direct[1],Direct[2])
        return vec*mat.inverse()
    @staticmethod
    def getJointChain(rootJnt):
        jntList=[rootJnt]
        loopNum=0
        while True:
            chList=cmds.listRelatives(rootJnt,c=1,typ='joint',ad=0)
            if(chList==None):
                break
            jntList.append(chList[0])
            rootJnt=chList[0]
            if(loopNum>1000):
                raise RuntimeError,'Loop Limit!'
            loopNum+=1
        return jntList
    @staticmethod
    def connectAllShapeAttr(ctrl,cAttr,sAttr):
        shapeList=GeneralUtility.findNodeShape(ctrl,getAll=True)
        for shape in shapeList:
                cmds.connectAttr(cAttr,shape+'.'+sAttr)
    @staticmethod
    def createSdkGrp(ctrl):
        sdkGrp=ctrl+'_sdk'
        if(cmds.objExists(sdkGrp)):
            return sdkGrp
        sdkGrp=cmds.group(em=1,n=sdkGrp)
        cmds.parent(sdkGrp,ctrl)
        GeneralUtility.resetTransformAttr(sdkGrp)
        pObj=cmds.listRelatives(ctrl,p=1)
        if(pObj):
            cmds.parent(sdkGrp,pObj[0])
        else:
            cmds.parent(sdkGrp,w=1)
        cmds.parent(ctrl,sdkGrp)
        return sdkGrp
    @staticmethod
    def createAimGrp(ctrl):
        aimGrp=ctrl+'_aim'
        if(cmds.objExists(aimGrp)):
            return aimGrp
        aimGrp=cmds.group(em=1,n=aimGrp)
        cmds.parent(aimGrp,ctrl)
        GeneralUtility.resetTransformAttr(aimGrp)
        pObj=cmds.listRelatives(ctrl,p=1)
        if(pObj):
            cmds.parent(aimGrp,pObj[0])
        else:
            cmds.parent(aimGrp,w=1)
        cmds.parent(ctrl,aimGrp)
        return aimGrp
    @staticmethod
    def transferSdkValueToCtrl(ctrl):
        pos=cmds.xform(ctrl,q=1,ws=1,t=1)
        rot=cmds.xform(ctrl,q=1,ws=1,ro=1)
        sdkGrp=GeneralUtility.createSdkGrp(ctrl)
        GeneralUtility.resetTransformAttr(sdkGrp)
        cmds.xform(ctrl,ws=1,t=pos)
        cmds.xform(ctrl,ws=1,ro=rot)
    @staticmethod
    def resetTransformAttr(obj):
        attrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        valList=[0,0,0,0,0,0,1,1,1]
        for attr,dv in zip(attrList,valList):
            isLock=cmds.getAttr(obj+'.'+attr,l=1)
            if(isLock):
                continue
            cmds.setAttr(obj+'.'+attr,dv)


# curve,zeroGrp=ControlUtility.createControl('sss')
# ControlUtility.scaleCV(curve,2)
class ControlUtility():
    GlobalScale=1
    @staticmethod
    def createControl(cName,cType='Circle',Mirror=True,T=True,R=True,S=False):
        curve=ControlUtility.createCurve(cName,cType)
        cmds.rename(curve,cName)
        ControlUtility.scaleCV(curve,ControlUtility.GlobalScale,typ='ObjectCenter')
        cmds.setAttr(curve+'.v',l=1,k=0)
        ControlUtility.lockTranslate(curve,x=not T,y=not T,z=not T)
        ControlUtility.lockRotate(curve,x=not R,y=not R,z=not R)
        ControlUtility.lockScale(curve,x=not S,y=not S,z=not S)
        zeroGrp=ControlUtility.createZeroGrp(curve,Mirror)
        return zeroGrp
    @staticmethod
    def createZeroGrp(curve,Mirror):
        zeroGrp=cmds.group(em=1,n=curve+'_zero')
        cmds.delete(cmds.parentConstraint(curve,zeroGrp))
        pObj=cmds.listRelatives(curve,p=1)
        if(pObj):
            cmds.parent(zeroGrp,pObj[0])
        if(Mirror):
            mirGrp=cmds.group(em=1,n=curve+'_mir')
            cmds.delete(cmds.parentConstraint(zeroGrp,mirGrp))
            cmds.parent(mirGrp,zeroGrp)
            cmds.parent(curve,mirGrp)
            if(curve[:2]=='R_'):
                cmds.setAttr(mirGrp+'.sx',-1)
                cmds.setAttr(mirGrp+'.sy',-1)
                cmds.setAttr(mirGrp+'.sz',-1)
        else:
            cmds.parent(curve,zeroGrp)
        return zeroGrp

    @staticmethod
    def createParentGrp(curve,suf):
        pGrp=cmds.duplicate(curve,po=1,n=curve+suf)[0]
        cmds.parent(curve,pGrp)
        return pGrp
    @staticmethod
    def createInverseGrp(curve):
        invGrp=cmds.duplicate(curve,po=1,n=curve+'_inv')[0]
        cmds.parent(curve,invGrp)
        invMulNode=cmds.createNode('multiplyDivide',n=invGrp+'_mulNode')
        cmds.setAttr(invMulNode+'.i2',-1,-1,-1,typ='float3')
        cmds.connectAttr(curve+'.r',invMulNode+'.i1')
        cmds.connectAttr(invMulNode+'.o',invGrp+'.r')
        return invGrp
    @staticmethod
    def lockTranslate(curve,x=1,y=1,z=1):
        cmds.setAttr(curve+'.tx',l=x,k=not x)
        cmds.setAttr(curve+'.ty',l=y,k=not y)
        cmds.setAttr(curve+'.tz',l=z,k=not z)
    @staticmethod
    def lockRotate(curve,x=1,y=1,z=1):
        cmds.setAttr(curve+'.rx',l=x,k=not x)
        cmds.setAttr(curve+'.ry',l=y,k=not y)
        cmds.setAttr(curve+'.rz',l=z,k=not z)
    @staticmethod
    def lockScale(curve,x=1,y=1,z=1):
        cmds.setAttr(curve+'.sx',l=x,k=not x)
        cmds.setAttr(curve+'.sy',l=y,k=not y)
        cmds.setAttr(curve+'.sz',l=z,k=not z)

    @staticmethod
    def scaleCV(curve,size,typ='ShapeCenter'):
        if(isinstance(size,list)):
            sx,sy,sz=size
        else:
            sx,sy,sz=size,size,size
        if(typ=='ObjectCenter' or typ==1):
            center=cmds.xform(curve,q=1,ws=1,t=1)
            cmds.scale(sx,sy,sz,cmds.ls(curve+'.cv[*]'),r=1,ocp=1,p=center)
        elif(typ=='WorldCenter' or typ==2):
            center=(0,0,0)
            cmds.scale(sx,sy,sz,cmds.ls(curve+'.cv[*]'),r=1,ocp=1,p=center)
        elif(typ=='ShapeCenter' or typ==3):
            shapes=GeneralUtility.findNodeShape(curve,getAll=True)
            for shape in shapes:
                cvList=cmds.ls(shape+'.cv[*]',fl=1)
                center=GeneralUtility.getComponentCenter(cvList)
                cmds.scale(sx,sy,sz,cvList,r=1,ocp=1,p=center)
    @staticmethod
    def moveCV(curve,vec,space='world'):
        shapes=GeneralUtility.findNodeShape(curve,getAll=True)
        for shape in shapes:
            cvList=cmds.ls(shape+'.cv[*]',fl=1)
            if(space=='world'):
                cmds.move(vec.x,vec.y,vec.z,cvList,r=1)
            else:
                cmds.move(vec.x,vec.y,vec.z,cvList,wd=1,r=1,os=1)

    @staticmethod
    def createCurve(cName,cType):
        if(cType=='Root'):
            cName=cmds.circle(n=cName,r=1.3,nr=[0,1,0],ch=0)
            return cName[0]
        if(cType=='Circle'):
            cName=cmds.circle(n=cName,r=1.3,nr=[1,0,0],ch=0)
            return cName[0]
        if(cType=='Circle_Arrow'):
            cName=cmds.curve(n=cName,d=1,p=[(0.0,0.991,-0.125),(0.0,1.113,0.0),(0.0,0.991,0.126),(0.0,0.969,0.249),(0.0,0.93,0.369),(0.0,0.875,0.482),(0.0,0.811,0.59),(0.0,0.729,0.685),(0.0,0.639,0.772),(0.0,0.536,0.846),(0.0,0.426,0.905),(0.0,0.309,0.953),(0.0,0.187,0.983),(0.0,0.063,1.0),(-0.0,-0.063,1.0),(-0.0,-0.187,0.983),(-0.0,-0.309,0.953),(-0.0,-0.426,0.905),(-0.0,-0.536,0.846),(-0.0,-0.639,0.772),(-0.0,-0.729,0.685),(-0.0,-0.811,0.59),(-0.0,-0.875,0.482),(-0.0,-0.93,0.369),(-0.0,-0.97,0.249),(-0.0,-0.99,0.126),(-0.0,-1.0,0.0),(-0.0,-0.988,-0.125),(-0.0,-0.97,-0.249),(-0.0,-0.928,-0.368),(-0.0,-0.874,-0.481),(-0.0,-0.811,-0.59),(-0.0,-0.729,-0.686),(-0.0,-0.638,-0.772),(-0.0,-0.536,-0.846),(-0.0,-0.425,-0.905),(-0.0,-0.309,-0.953),(-0.0,-0.187,-0.983),(-0.0,-0.063,-1.0),(0.0,0.064,-1.0),(0.0,0.187,-0.983),(0.0,0.31,-0.953),(0.0,0.426,-0.904),(0.0,0.536,-0.846),(0.0,0.639,-0.772),(0.0,0.729,-0.685),(0.0,0.811,-0.589),(0.0,0.875,-0.481),(0.0,0.93,-0.369),(0.0,0.969,-0.248),(0.0,0.991,-0.125),(0.0,1.002,0.0),(0.0,0.991,0.126)])
            return cName
        if(cType=='Sphere'):
            cName=cmds.curve(n=cName,d=1,p=[(0.504214,0,0),(0.491572,0.112198,0),(0.454281,0.21877,0),(0.394211,0.314372,0),(0.314372,0.394211,0),(0.21877,0.454281,0),(0.112198,0.491572,0),(0,0.504214,0),(-0.112198,0.491572,0),(-0.21877,0.454281,0),(-0.314372,0.394211,0),(-0.394211,0.314372,0),(-0.454281,0.21877,0),(-0.491572,0.112198,0),(-0.504214,0,0),(-0.491572,-0.112198,0),(-0.454281,-0.21877,0),(-0.394211,-0.314372,0),(-0.314372,-0.394211,0),(-0.21877,-0.454281,0),(-0.112198,-0.491572,0),(0,-0.504214,0),(0.112198,-0.491572,0),(0.21877,-0.454281,0),(0.314372,-0.394211,0),(0.394211,-0.314372,0),(0.454281,-0.21877,0),(0.491572,-0.112198,0),(0.504214,0,0),(0.491572,0,-0.112198),(0.454281,0,-0.21877),(0.394211,0,-0.314372),(0.314372,0,-0.394211),(0.21877,0,-0.454281),(0.112198,0,-0.491572),(0,0,-0.504214),(-0.112198,0,-0.491572),(-0.21877,0,-0.454281),(-0.314372,0,-0.394211),(-0.394211,0,-0.314372),(-0.454281,0,-0.21877),(-0.491572,0,-0.112198),(-0.504214,0,0),(-0.491572,0,0.112198),(-0.454281,0,0.21877),(-0.394211,0,0.314372),(-0.314372,0,0.394211),(-0.21877,0,0.454281),(-0.112198,0,0.491572),(0,0,0.504214),(0,0.112198,0.491572),(0,0.21877,0.454281),(0,0.314372,0.394211),(0,0.394211,0.314372),(0,0.454281,0.21877),(0,0.491572,0.112198),(0,0.504214,0),(0,0.491572,-0.112198),(0,0.454281,-0.21877),(0,0.394211,-0.314372),(0,0.314372,-0.394211),(0,0.21877,-0.454281),(0,0.112198,-0.491572),(0,0,-0.504214),(0,-0.112198,-0.491572),(0,-0.21877,-0.454281),(0,-0.314372,-0.394211),(0,-0.394211,-0.314372),(0,-0.454281,-0.21877),(0,-0.491572,-0.112198),(0,-0.504214,0),(0,-0.491572,0.112198),(0,-0.454281,0.21877),(0,-0.394211,0.314372),(0,-0.314372,0.394211),(0,-0.21877,0.454281),(0,-0.112198,0.491572),(0,0,0.504214),(0.112198,0,0.491572),(0.21877,0,0.454281),(0.314372,0,0.394211),(0.394211,0,0.314372),(0.454281,0,0.21877),(0.491572,0,0.112198),(0.504214,0,0)])
            return cName
        if(cType=='Triangle'):
            cName=cmds.curve(d=1,n=cName,p=[(0,0,0.25),(0,0.05,0.1),(0,-0.05,0.1),(0,0,0.25)])
            return cName
        if(cType=='Rect'):
            cName=cmds.curve(d=1,n=cName,p=[(0,-2,2),(0,-2,-2),(0,2,-2),(0,2,2),(0,-2,2)])
            return cName
        if(cType=='Cube'):
            cName=cmds.curve(d=1,n=cName,p=[(0.1,0.1,-0.1),(-0.1,0.1,-0.1),(-0.1,0.1,0.1),(0.1,0.1,0.1),(0.1,0.1,-0.1),(0.1,-0.1,-0.1),(0.1,-0.1,0.1),(0.1,0.1,0.1),(-0.1,0.1,0.1),(-0.1,-0.1,0.1),(0.1,-0.1,0.1),(0.1,-0.1,-0.1),(-0.1,-0.1,-0.1),(-0.1,-0.1,0.1),(-0.1,0.1,0.1),(-0.1,0.1,-0.1),(-0.1,-0.1,-0.1)])
            return cName
        if(cType=='Cross'):
            cName=cmds.curve(n=cName,d=1,p=[(-1,0,-1),(0 ,0 ,-1),(0,0,-2),(1,0,-2),(1,0,-1),(2,0,-1),(2,0,0),(1,0,0),(1,0,1),(0,0,1),(0,0,0),(-1,0,0),(-1,0,-1)])
            return cName
        if(cType=='Circle_Line'):
            cName=cmds.curve(n=cName,d=3,p=[(0,0,0),(0,1.3,0),(0,1.3,0),(0,1.3,0),(0,1.388,-0.213),(0,1.6,-0.3),(0,1.81,-0.213),(0,1.9,0),(0,1.815,0.213),(0,1.597,0.3),(0,1.388,0.213),(0,1.3,0),(0,1.3,0),(0,1.3,0)])
            return cName
        if(cType=='Heel'):
            cName=cmds.curve(n=cName,d=3,p=[(9.8,0,-4),(9.8,0,-4),(9.8,0,-4),(-2.59,0,-4.15),(-4.59,0,-3),(-5.59,0,0),(-4.59,0,3),(-2.59,0,4.15),(9.8,0,3),(9.8,0,3),(9.8,0,3),(9.8,0,-4)])
            return cName
        if(cType=='Toe'):
            cName=cmds.curve(n=cName,d=3,p=[(1.4,0,-4),(1.4,0,-4),(1.4,0,-4),(8.324,0,-4),(10.973,0,-3),(12.297,0,0),(10.973,0,3),(8.324,0,4),(1.4,0,3),(1.4,0,3),(1.4,0,3),(1.4,0,-4)])
            return cName
        if(cType=='None'):
            cName=cmds.group(n=cName,em=1)
            return cName
# attrStrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
# sel=cmds.listRelatives('move_Ctrl',c=1,typ='joint',ad=1)
# lockInfo={}
# for i in sel:
#     lockList=[]
#     for attr in attrStrList:
#         isLock=cmds.getAttr(i+'.'+attr,l=1)
#         lockList.append(isLock)
#     lockInfo[i]=lockList
# for i in lockInfo:
#     for attr,isLock in zip(attrStrList,lockInfo[i]):
#         cmds.setAttr(i+'.'+attr,l=isLock)
#  
class CorrectBSModule():
    def __init__(self):
        self.skinName=None
        self.skinMesh=None
        self.bsNode=None
        self.mirrorData=None
        self.modifyMesh=None
        self.sdkHandleCallback=None
        self.sdkScriptJob=None

        self.sdkHandle='body_sdk_handle'
        self.SkinMeshTFG='bsSkinMeshTFG_br'
        self.bsDriverListTV='bsDriverAttrList_br'
        self.bsDriverShowTypeRBG='bsDriverShowTypeRBG_br'
        self.bsDriverValueFSG='bsDriverValueFSG_br'

        self.bsDrivenListTV='bsDrivenBsList_br'
        self.bsDrivenShowTypeRBG='bsDrivenShowTypeRBG_br'
        self.bsDrivenValueFSG='bsDrivenValueFSG_br'

        self.bsEnterModifyB='bsEnterModifyB_br'

        self.bsIgnoreTFG='bsIgnoreDisTFG_br'
        self.bsMirrorAxisRBG='bsMirrorAxisRBG_br'

        self.bsNewBsB='bsNewBlendShapeB_br'
    def driverListSelectChange(self):
        cmds.floatSliderGrp(self.bsDriverValueFSG,e=1,en=0)
        cmds.button(self.bsEnterModifyB,e=1,en=0)
        selI=cmds.treeView(self.bsDriverListTV,q=1,si=1)
        if(selI==None):return
        val=cmds.getAttr(self.sdkHandle+'.'+selI[0])
        maxVal=self.getAttrMax(self.sdkHandle,selI[0])
        minVal=self.getAttrMin(self.sdkHandle,selI[0])
        cmds.floatSliderGrp(self.bsDriverValueFSG,e=1,v=val,en=1,max=maxVal,min=minVal)
        cmds.button(self.bsEnterModifyB,e=1,en=(self.skinMesh!=None and len(selI)==1))
        self.updateDriverList()
        self.updateDrivenListInfo()

    def getAttrMax(self,obj,attr):
        if(cmds.attributeQuery(attr,node=obj,mxe=1)):
            return cmds.attributeQuery(attr,node=obj,max=1)[0]
        return 100
    def getAttrMin(self,obj,attr):
        if(cmds.attributeQuery(attr,node=obj,mne=1)):
            return cmds.attributeQuery(attr,node=obj,min=1)[0]
        return -100

    def dirverValueDrag(self,value):
        cmds.undoInfo(swf=0)
        self.infValueChange(value)
        cmds.undoInfo(swf=1)
        
    def dirverValueChange(self,value):
        selI=cmds.treeView(self.bsDriverListTV,q=1,si=1)
        if(selI==None):return
        
        for i in selI:
            subList=i.split('__')
            if(len(subList)>1):
                mainAttr,mainVal=subList[0],int(subList[1])
                self.forceSetAttr(self.sdkHandle+'.'+mainAttr,mainVal*0.01)
            self.forceSetAttr(self.sdkHandle+'.'+i,value)
            cmds.treeView(self.bsDriverListTV,e=1,dls=[i,'    '+str(value)])
        cmds.button(self.bsEnterModifyB,e=1,en=(self.skinMesh!=None and value==1))

    def forceSetAttr(self,objAttr,val):
        if(cmds.getAttr(objAttr,l=1)):
            print('%s is Locked!'%objAttr)
            return
        inputList=cmds.listConnections(objAttr,p=1,s=1,d=0)
        if(inputList):
            assert(len(inputList)==1)
            objAttr=inputList[0]
        cmds.setAttr(objAttr,val)

    def createSDKListScriptJob(self,winName):
        sdkList=cmds.listAttr(self.sdkHandle,ud=1)
        for sdkAttr in sdkList:
            cmds.scriptJob(ac=[self.sdkHandle+'.%s'%sdkAttr,functools.partial(self.sdkHandleAttrChange,sdkAttr)],p=winName)

    def sdkHandleAttrChange(self,sdkAttr):
        val=cmds.getAttr(self.sdkHandle+'.'+sdkAttr)
        val=round(val,3)
        cmds.treeView(self.bsDriverListTV,e=1,dls=[sdkAttr,'    '+str(val)])
        if(cmds.radioButtonGrp(self.bsDriverShowTypeRBG,q=1,sl=1)==2):
            cmds.treeView(self.bsDriverListTV,e=1,iv=[sdkAttr,val>0])

    def loadDriverToUI(self):
        attrList=cmds.listAttr(self.sdkHandle,ud=1)
        if(attrList==None):
            return
        for attr in attrList:
            cmds.treeView(self.bsDriverListTV,e=1,ai=[attr,''])
        return attrList

    def updateDriverList(self,*args):
        allI=cmds.treeView(self.bsDriverListTV,q=1,ch=1)
        if(allI==None):
            allI=self.loadDriverToUI()
        print allI
        for attr in allI:
            val=cmds.getAttr(self.sdkHandle+'.'+attr)
            cmds.treeView(self.bsDriverListTV,e=1,dls=[attr,' %s'%val])
            vis=cmds.radioButtonGrp(self.bsDriverShowTypeRBG,q=1,sl=1)==1 or round(val,3)>0
            cmds.treeView(self.bsDriverListTV,e=1,iv=[attr,vis])


    def enterModifyMode(self,*args):
        selI=cmds.treeView(self.bsDriverListTV,q=1,si=1)
        assert selI
        drAttr=selI[0]
        bsTargetMesh=self.getBSTragetMesh(drAttr)
        self.targetMesh=bsTargetMesh
        self.modifyMesh=bsTargetMesh+'_modify'
        if(not cmds.objExists(self.modifyMesh)):
            self.modifyMesh=cmds.duplicate(self.skinMesh,n=self.modifyMesh,rr=1)[0]
            self.parentToWorld(self.modifyMesh)
            self.deleteIntermediateShape(self.modifyMesh)

        cmds.select(self.modifyMesh)
        self.setSkinShapeVisiable(0)
        self.createSlideHUD()
        self.updateDrivenListInfo(Reload=True)


    def createSlideHUD(self,*args):
        self.deleteSlideHUD()
        cmds.headsUpDisplay(rp=[2,1])
        cmds.hudButton('HUDSlideComponentsB',s=2,b=1,vis=1,l='Enable Slide Components',ba='center',bw=160,pc=self.enableSlideComponents)
    def deleteSlideHUD(self,*args):
        if(cmds.headsUpDisplay('HUDSlideComponentsB',q=1,ex=1)):
            cmds.headsUpDisplay('HUDSlideComponentsB',e=1,rem=1)
    def enableSlideComponents(self):
        lab=cmds.hudButton('HUDSlideComponentsB',q=1,l=1)
        enLab='Enable Slide Components'
        disLab='Disable Slide Components'
        cmds.delete(self.modifyMesh,ch=1)
        if(lab==enLab):
            cmds.transferAttributes(self.skinMesh,self.modifyMesh,pos=1,nml=0,uvs=0,col=0,spa=1,sm=0)
            cmds.hudButton('HUDSlideComponentsB',e=1,l=disLab)
        else:
            cmds.hudButton('HUDSlideComponentsB',e=1,l=enLab)

    def parentToWorld(self,obj):
        pObj=cmds.listRelatives(obj,p=1)
        if(pObj!=None):
            cmds.parent(obj,w=1)

    def setSkinShapeVisiable(self,vis):
        skinShape=self.findNodeShape(self.skinMesh)
        cmds.setAttr(skinShape+'.v',vis)

    def exitModifyMode(self,*args):
        self.deleteSlideHUD()
        try:
            cmds.undoInfo(swf=0)
            bsNode=self.getBsNode()
            try:
                cmds.setAttr(bsNode+'.en',0)
                skin_points = self.getMeshPoints(self.skinMesh)
                interShape = self.findNodeIntermediateShape(self.skinMesh)
                inter_points = self.getMeshPoints(interShape)
                x_points = OpenMaya.MPointArray(inter_points)
                y_points = OpenMaya.MPointArray(inter_points)
                z_points = OpenMaya.MPointArray(inter_points)

                for i in range(skin_points.length()):
                    x_points[i].x += 1.0
                    y_points[i].y += 1.0
                    z_points[i].z += 1.0
                try:
                    self.setMeshPoints(interShape, x_points)
                    x_points = self.getMeshPoints(self.skinMesh)
                    self.setMeshPoints(interShape, y_points)
                    y_points = self.getMeshPoints(self.skinMesh)
                    self.setMeshPoints(interShape, z_points)
                    z_points = self.getMeshPoints(self.skinMesh)
                finally:
                    self.setMeshPoints(interShape, inter_points)

                modify_points = self.getMeshPoints(self.modifyMesh)
                __matrices=[]
                for i in range(skin_points.length()):
                    matrix = OpenMaya.MMatrix()
                    self.set_matrix_row(matrix, x_points[i] - skin_points[i], 0)
                    self.set_matrix_row(matrix, y_points[i] - skin_points[i], 1)
                    self.set_matrix_row(matrix, z_points[i] - skin_points[i], 2)
                    self.set_matrix_row(matrix, modify_points[i], 3)
                    matrix = matrix.inverse()
                    __matrices.append(matrix)
            finally:
                cmds.setAttr(bsNode+'.en',1)

            outMesh=self.targetMesh

            self.forceSetAttr(self.getBSWeightAttr(outMesh),0)
            skin_points = self.getMeshPoints(self.skinMesh)
            self.forceSetAttr(self.getBSWeightAttr(outMesh),1)
                
            out_points = self.getSkinOrigPoints()
            # old_points = self.getMeshPoints(outMesh)
            # fix_points = OpenMaya.MPointArray()
            # fix_points.setLength(old_points.length())

            ignoreDis=self.getMirrorThreshold()
            for i in range(out_points.length()):
                delta = modify_points[i] - skin_points[i]
                if (math.fabs(delta.x) < ignoreDis and math.fabs(delta.y) < ignoreDis and math.fabs(delta.z) < ignoreDis):
                    continue
                offset = delta * __matrices[i]
                out_points[i].x+=offset.x
                out_points[i].y+=offset.y
                out_points[i].z+=offset.z
                # fix_points[i].x=old_points[i].x-out_points[i].x
                # fix_points[i].y=old_points[i].y-out_points[i].y
                # fix_points[i].z=old_points[i].z-out_points[i].z
            self.setMeshPoints(outMesh, out_points)

            # #fix overlay bs
            # dnAttr=self.getMeshBsSdkList(outMesh)
            # if(len(dnAttr)==1):
            #     dnAttr=dnAttr[0]
            #     bsList=self.getAllBsList()
            #     for bsMesh in bsList:
            #         sdkList,valList=self.getMeshBsSdkList(bsMesh)
            #         if(dnAttr in sdkList):

        finally:
            cmds.undoInfo(swf=1)
            if(cmds.objExists(self.modifyMesh)):
                cmds.delete(self.modifyMesh)
            self.setSkinShapeVisiable(1)

    def getAllBsList(self):
        bsGrp=self.getBSGrp()
        bsList=cmds.listRelatives(bsGrp,c=1,pa=1)
        if(not bsList):
            return
        return bsList


    def repairBSAndSdk(self,drAttr):
        allI=cmds.treeView(self.bsDrivenListTV,q=1,ch=1)
        if(allI==None):
            return
        drValue=cmds.getAttr(self.sdkHandle+'.'+drAttr)
        dnValue=0
        for i in allI:
            if(i.startswith(drAttr)):
                cValue=int(i.split('__')[-1])
                if(cValue>drValue):
                    continue
                if(cValue>dnValue):
                    dnValue=cValue

    def getBSWeightAttr(self,outMesh):
        bsNode=self.getBsNode()
        cnn=cmds.listConnections(outMesh+'.worldMesh[0]',p=1)
        idx=cnn[0].split('.')[2][len('inputTargetGroup'):]
        return bsNode+'.w'+idx

    def loadDrivenToUI(self,*args):
        bsNode=self.getBsNode()
        if(not cmds.objExists(bsNode)):
            return
        cmds.treeView(self.bsDrivenListTV,e=1,ra=1)
        idxList=cmds.getAttr(bsNode+'.w',mi=1)
        if(not idxList):
            return
        allI=[]
        for idx in idxList:
            cwAttr=bsNode+'.w[%s]'%idx
            lab=cmds.aliasAttr(cwAttr,q=1)
            if(lab==''):
                lab='w[%s]'%idx
            val=cmds.getAttr(cwAttr)
            val=round(val,3)
            cmds.treeView(self.bsDrivenListTV,e=1,ai=[lab,''])
            allI.append(lab)
        return allI

    def updateDrivenListInfo(self,Reload=False):
        bsNode=self.getBsNode()
        if(not cmds.objExists(bsNode)):
            return
        allI=cmds.treeView(self.bsDrivenListTV,q=1,ch=1)
        if(allI==None or Reload):
            allI=self.loadDrivenToUI()
            if(allI==None):
                return

        for attr in allI:
            val=cmds.getAttr(bsNode+'.'+attr)
            cmds.treeView(self.bsDrivenListTV,e=1,dls=[attr,'    '+str(val)])
            vis=self.checkDrivenBSVis(attr)
            cmds.treeView(self.bsDrivenListTV,e=1,iv=[attr,vis])

    def checkDrivenBSVis(self,bsName):
        if(cmds.radioButtonGrp('bsDrivenShowTypeRBG_br',q=1,sl=1)==1):
            return True
        selAttrI=cmds.treeView(self.bsDriverListTV,q=1,si=1)
        if(selAttrI==None):
            return False
        for i in selAttrI:
            if(bsName.startswith(i)):
                return True
        return False

    def drivenListSelectChange(self,*args):
        selI=cmds.treeView(self.bsDrivenListTV,q=1,si=1)
        cmds.floatSliderGrp(self.bsDrivenValueFSG,e=1,en=(selI!=None))
        if(selI==None):return
        bsNode=self.getBsNode()

        val=cmds.getAttr(bsNode+'.'+selI[0])
        cmds.floatSliderGrp(self.bsDrivenValueFSG,e=1,v=val,en=1)

        self.selectBlendShapeMesh()

    def drivenValueDrag(self,value):
        cmds.undoInfo(swf=0)
        self.drivenValueChange(value)
        cmds.undoInfo(swf=1)
        
    def drivenValueChange(self,value):
        value=cmds.floatSliderGrp('bsDrivenValueFSG_br',q=1,v=1)
        value=round(value,3)
        selI=cmds.treeView(self.bsDrivenListTV,q=1,si=1)
        if(selI==None):return
        bsNode=self.getBsNode()
        for i in selI:
            self.forceSetAttr(bsNode+'.'+i,value)
        self.updateDrivenListInfo()




    def sculptMode(self,*args):
        cmds.selectMode(o=1)
        cmds.SculptGeometryTool()

    def vertexMode(self,*args):
        cmds.selectMode(co=1)
        cmds.selectPriority(jp=1)
        cmds.selectType(jp=0,sp=0,rp=0,cv=1,pv=1,smp=1,lp=1,pr=1)

#=====================================================================================================
    def checkMirrorInfo(self,space=OpenMaya.MSpace.kObject):
        mfnOrigMesh=self.getSkinOrigMesh()
        origPoints = OpenMaya.MPointArray()
        mfnOrigMesh.getPoints(origPoints, space)

        axis=self.getMirrorAxis()

        self.mirrorData=[]
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        idPtr= util.asIntPtr()
        clostPoint=OpenMaya.MPoint()
        cmds.progressWindow(t='',pr=0,st='Check Mirror Info...',max=origPoints.length())
        try:
            oldSel=cmds.ls(sl=1)
            for i in range(origPoints.length()):
                cmds.progressWindow(e=1,s=1)

                mirrorPoint=OpenMaya.MPoint(origPoints[i][0]*axis[0],origPoints[i][1]*axis[1],origPoints[i][2]*axis[2])
                mfnOrigMesh.getClosestPoint(mirrorPoint,clostPoint,space,idPtr)
                idx = OpenMaya.MScriptUtil(idPtr).asInt()
                nearestIdxList=OpenMaya.MIntArray()
                mfnOrigMesh.getPolygonVertices(idx,nearestIdxList)
            
                closetIdx=nearestIdxList[0]
                for idx in range(1,nearestIdxList.length()):
                    dis1=mirrorPoint.distanceTo(origPoints[nearestIdxList[idx]])
                    dis2=mirrorPoint.distanceTo(origPoints[closetIdx])
                    if(dis1<dis2):
                        closetIdx=nearestIdxList[idx]
                dis=mirrorPoint.distanceTo(origPoints[closetIdx])
                self.mirrorData.append(closetIdx)
        finally:
            cmds.progressWindow(e=1,ep=1)
        cmds.select(cl=1)
        cmds.select(oldSel)


    def getMirrorThreshold(self,*args):
        return cmds.floatFieldGrp(self.bsIgnoreTFG,q=1,v1=1)

    def getMirrorValue(self,*args):
        return cmds.radioButtonGrp(self.bsMirrorAxisRBG,q=1,sl=1)

    def getBSGrp(self):
        bsGrp='body_bs_grp'
        if(not cmds.objExists(bsGrp)):
            bsGrp=cmds.group(n=bsGrp,em=1)
            cmds.setAttr(bsGrp+'.v',0)
        skinMeshBsGrp='%s_bs_grp'%self.skinMesh
        if(not cmds.objExists(skinMeshBsGrp)):
            skinMeshBsGrp=cmds.group(n=skinMeshBsGrp,em=1)
            cmds.parent(skinMeshBsGrp,bsGrp)
        return skinMeshBsGrp

    def setSkinMesh(self,*args):
        sel=cmds.ls(sl=1)
        if(sel==None):
            return
        mesh=sel[0]
        shapes=cmds.listRelatives(mesh,s=1)
        if(not shapes and cmds.objectType(shapes[0])!='mesh'):
            raise RuntimeError,'Please select Mesh to set!'
        self.skinName=self.findSkinclusterNode(mesh)
        self.skinMesh=mesh
        self.bsNode=self.findBlendShapeNode(self.skinMesh)
        cmds.textFieldButtonGrp(self.SkinMeshTFG,e=1,tx=self.skinMesh)
        self.mirrorData=None
        self.updateDriverList()
        
        

    def findBlendShapeNode(self,skinMesh):
        skinShape=self.findNodeShape(skinMesh)
        bsList=cmds.ls(typ='blendShape')
        retList=[]
        for i in bsList:
            geo=cmds.blendShape(i,q=1,g=1)
            if(geo and skinShape==geo[0]):
                retList.append(i)
        if len(retList)==0:
            return
        return retList[0]

    def findNodeShape(self,meshName):
        shapes = cmds.listRelatives(meshName, s=True, pa=True)
        if not shapes:
            raise RuntimeError, '%s has no shape'%meshName
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject'%shape)
            if (not is_intermediate):
                return shape
        raise RuntimeError('Could not find shape on node {0}'.format(meshName))

    def findNodeIntermediateShape(self,meshName):
        shapes = cmds.listRelatives(meshName, s=True, pa=True)
        if not shapes:
            raise RuntimeError, '%s has no shape'%meshName
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject'%shape)
            if (is_intermediate and cmds.listConnections('%s.worldMesh' % shape,source=False)):
                return shape
        raise RuntimeError('Could not find shape on node {0}'.format(meshName))

    def deleteIntermediateShape(self,meshName):
        shapes = cmds.listRelatives(meshName, s=True, pa=True)
        if not shapes:
            raise RuntimeError, '%s has no shape'%meshName
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject'%shape)
            if is_intermediate:
                cmds.delete(shape)

    def findSkinclusterNode(self,meshName):
        skinNode=mm.eval('findRelatedSkinCluster "%s"'%meshName)
        if not skinNode:
            raise RuntimeError, '%s has no skin'%meshName
        return skinNode

    def getSkinMesh(self):
        if(self.skinMesh==None):
            cmds.confirmDialog(t='Confirm',m='Please set the Options !',b=['Yes'],db='Yes')
            raise RuntimeError,'SkinMesh is not set!'
        return self.skinMesh

    def getBsTragetName(self,drAttr):
        val=cmds.getAttr(self.sdkHandle+'.'+drAttr)
        bsAttr=drAttr+'__%s'%int(val)
        return bsAttr

    def getBSTragetMesh(self,drAttr):
        bsAttr=self.getBsTragetName(drAttr)
        bsTargetMesh=self.skinMesh+'_'+bsAttr
        if(cmds.objExists(bsTargetMesh)):
            return bsTargetMesh
        else:
            try:
                cmds.undoInfo(swf=0)
                bsGrp=self.getBSGrp()
                bsTargetMesh=cmds.duplicate(self.skinMesh,n=bsTargetMesh,rr=1)[0]
                self.addSdkListEnumAttr(bsTargetMesh,[bsAttr])
                self.deleteIntermediateShape(bsTargetMesh)
                self.setToOrigPoints(bsTargetMesh)
                cmds.parent(bsTargetMesh,bsGrp)
                bsNode,index=self.blendShapeToSkinMesh(bsTargetMesh,bsAttr)
                self.connectSdkToBsAttr(bsAttr)
            finally:
                cmds.undoInfo(swf=1)
            return bsTargetMesh

    def connectSdkToBsAttr(self,bsAttr):
        bsNode=self.getBsNode()

        dnAttr=bsNode+'.'+bsAttr
        drAttr=bsAttr.split('__')[0]
        drVal=int(bsAttr.split('__')[-1])

        startValue,fixBsAttr=self.getDrivenStartEndValue(drAttr,drVal)
        drAttr=self.sdkHandle+'.'+drAttr
        cmds.setDrivenKeyframe(dnAttr,cd=drAttr,v=0,dv=startValue,itt='linear',ott='linear')
        cmds.setDrivenKeyframe(dnAttr,cd=drAttr,v=1,dv=drVal,itt='linear',ott='linear')
        if(fixBsAttr):
            sdkAnimNode=cmds.keyframe(bsNode,at=fixBsAttr,q=1,n=1)
            if(sdkAnimNode==None):
                return
            cmds.keyframe(sdkAnimNode[0],o='over',index=(0,0),a=1,fc=drVal)
    def fixBSDriverAttr(self,*args):
        selI=cmds.treeView(self.bsDrivenListTV,q=1,si=1)
        if(selI==None):
            return
        for i in selI:
            self.connectSdkToBsAttr(i)

    def getDrivenStartEndValue(self,drAttr,drVal):
        startValue=0
        endValue=190
        fixBsAttr=None
        allI=cmds.treeView(self.bsDrivenListTV,q=1,ch=1)
        if(allI==None):
            return startValue,fixBsAttr

        for i in allI:
            if(i.startswith(drAttr)):
                val=int(i.split('__')[-1])
                if(val<drVal):
                    if(val>startValue):
                        startValue=val
                else:
                    if(val<endValue):
                        endValue=val
                        fixBsAttr=i
        return startValue,fixBsAttr


    def createMinimumOutput(self,input1,input2,bsAttr):
        condNode=cmds.createNode('condition')
        cmds.connectAttr(input1,condNode+'.ft')
        cmds.connectAttr(input2,condNode+'.st')
        cmds.setAttr(condNode+'.op',4)
        cmds.connectAttr(input1,condNode+'.ctr')
        cmds.connectAttr(input2,condNode+'.cfr')
        cmds.connectAttr(condNode+'.ocr',bsAttr,f=1)
        return condNode+'.ocr'


    def addSdkListEnumAttr(self,meshName,selAttrI):
        attrList=cmds.listAttr(meshName)
        if('SdkList' in attrList):
            cmds.addAttr(meshName+'.SdkList',e=1,en=':'.join(selAttrI))
        else:
            cmds.addAttr(meshName,ln='SdkList',at='enum',en=':'.join(selAttrI))

    def getMeshBsSdkList(self,meshName,combin=False):
        enumStr=cmds.addAttr(meshName+'.SdkList',q=1,en=1)
        sdkValList=enumStr.split(':')
        return sdkValList
        sdkList=[]
        valList=[]
        for i in sdkValList:
            sdk=i.split('__')[0]
            val=int(i.split('__')[-1])
            sdkList.append(sdk)
            valList.append(val)
        return sdkList,valList

    def getBsListLable(self,meshName):
        assert self.skinMesh
        assert len(meshName)>len(self.skinMesh)
        if(meshName[:len(self.skinMesh)]==self.skinMesh):
            return meshName[len(self.skinMesh)+1:]
        raise RuntimeError,'%s does not match the name rules.'%meshName

    def deleteBlendShape(self,*args):
        bsList=self.getBsListSelectMesh()
        if(len(bsList)==0):
            return
        bsNode=self.getBsNode()
        idxList=cmds.getAttr(bsNode+'.w',mi=1)
        for i in bsList:
            cnn=cmds.listConnections(i+'.worldMesh[0]',p=1)
            idx=cnn[0].split('.')[2][len('inputTargetGroup'):]
            idx=int(idx[1:-1])
            cmds.blendShape(bsNode,e=1,tc=0,rm=1,t=(self.skinMesh,idx,i,1))
            cmds.delete(i)
        self.updateDrivenListInfo(Reload=True)
        
        
    def getBsNode(self):
        assert self.skinMesh
        bsNode=self.skinMesh+'_blendShape'
        # assert cmds.objExists(bsNode)
        return bsNode

    def blendShapeToSkinMesh(self,bsTargetMesh,bsAttr):
        bsNode=self.getBsNode()
        if(cmds.objExists(bsNode)):
            cnnShape=cmds.blendShape(bsNode,q=1,g=1)[0]
            cnnMesh=cmds.listRelatives(cnnShape,pa=1,p=1)[0]
            if(self.skinMesh!=cnnMesh):
                cmds.delete(bsNode)
        index=0
        if not(cmds.objExists(bsNode)):
            cmds.blendShape(bsTargetMesh,self.skinMesh,foc=1,n=bsNode)
        else:
            exIdList=cmds.getAttr(bsNode+'.inputTarget[0].inputTargetGroup',mi=1)
            if(exIdList):
                index=exIdList[-1]+1
            cmds.blendShape(bsNode,e=1,t=(self.skinMesh,index,bsTargetMesh,1))
        cmds.aliasAttr(bsAttr,bsNode+'.w[%s]'%index)
        return bsNode,index


    def getSkinOrigMesh(self):
        assert self.skinName
        mfnSkin=self.getMFnSkinCluster(self.skinName)
        origObj=mfnSkin.inputShapeAtIndex(0)
        mfnOrigMesh=OpenMaya.MFnMesh(origObj)
        return mfnOrigMesh
    def getSkinOrigPoints(self,space=OpenMaya.MSpace.kObject):
        mfnOrigMesh=self.getSkinOrigMesh()
        origPoints = OpenMaya.MPointArray()
        mfnOrigMesh.getPoints(origPoints, space)
        return origPoints
    def setToOrigPoints(self,meshName,space=OpenMaya.MSpace.kObject):
        mfnOrigMesh=self.getSkinOrigMesh()
        origPoints = OpenMaya.MPointArray()
        mfnOrigMesh.getPoints(origPoints, space)
        self.setMeshPoints(meshName,origPoints)

    def getMFnSkinCluster(self,skinName):
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(skinName)
        skinObj = OpenMaya.MObject()
        selection_list.getDependNode(0, skinObj)
        return OpenMayaAnim.MFnSkinCluster(skinObj)


    def getMfnMesh(self,meshName):
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(meshName)
        dagPath = OpenMaya.MDagPath()
        selection_list.getDagPath(0, dagPath)
        return OpenMaya.MFnMesh(dagPath)

    def getNodeMObject(self,objName):
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(objName)
        retObj = OpenMaya.MObject()
        selection_list.getDependNode(0, retObj)
        return retObj

    def getMeshPoints(self,meshName, space=OpenMaya.MSpace.kObject):
        mfnMesh=self.getMfnMesh(meshName)
        points = OpenMaya.MPointArray()
        mfnMesh.getPoints(points, space)
        return points

    def setMeshPoints(self,meshName, points, space=OpenMaya.MSpace.kObject):
        mfnMesh=self.getMfnMesh(meshName)
        mfnMesh.setPoints(points, space)



    def selectBlendShapeMesh(self,*args):
        bsList=self.getBsListSelectMesh()
        if(len(bsList)==0):
            return
        cmds.select(bsList)

    def getBsListSelectMesh(self):
        assert self.skinMesh
        selI=cmds.treeView(self.bsDrivenListTV,q=1,si=1)
        selBsList=[]
        if(selI):
            for i in selI:
                selBsList.append(self.skinMesh+'_'+i)
        return selBsList


    def set_matrix_row(self,matrix, new_vector, row):
        self.set_matrix_cell(matrix, new_vector.x, row, 0)
        self.set_matrix_cell(matrix, new_vector.y, row, 1)
        self.set_matrix_cell(matrix, new_vector.z, row, 2)
    def set_matrix_cell(self,matrix, value, row, column):
        OpenMaya.MScriptUtil.setDoubleArray(matrix[row], column, value)


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

    def getMirrorData(self):
        if(not self.mirrorData):
            self.checkMirrorInfo()
        return self.mirrorData

    def getMirrorAxis(self):
        mirrorAxis=self.getMirrorValue()
        if(mirrorAxis==1):
            axis=[-1,1,1]
        elif(mirrorAxis==2):
            axis=[1,-1,1]
        else:
            axis=[1,1,-1]
        return axis



    def mirrorBlendShape(self,*args):

        selI=cmds.treeView(self.bsDrivenListTV,q=1,si=1)
        if(not selI):
            return
        selectBS=selI

        bsGrp=self.getBSGrp()
        axis=self.getMirrorAxis()
        try:
            cmds.undoInfo(swf=0)

            mirBsMeshList=[]
            for bsAttr in selectBS:
                bsMesh=self.skinMesh+'_'+bsAttr
                mirBsAttr=self.getMirrorName(bsAttr)

                mirBsTargetMesh=self.skinMesh+'_'+mirBsAttr
                if(not cmds.objExists(mirBsTargetMesh)):
                    mirBsTargetMesh=cmds.duplicate(self.skinMesh,n=mirBsTargetMesh,rr=1)[0]

                    self.addSdkListEnumAttr(mirBsTargetMesh,[mirBsAttr])
                    self.deleteIntermediateShape(mirBsTargetMesh)
                    self.setToOrigPoints(mirBsTargetMesh)
                    cmds.parent(mirBsTargetMesh,bsGrp)
                    bsNode,index=self.blendShapeToSkinMesh(mirBsTargetMesh,mirBsAttr)
                    self.connectSdkToBsAttr(mirBsAttr)

                mirIdxList=self.getMirrorData()
                bsPoint=self.getMeshPoints(bsMesh)
                mirBsPoint=self.getMeshPoints(mirBsTargetMesh)
                origPoints=self.getSkinOrigPoints()

                ignoreDis=self.getMirrorThreshold()
                for i in range(origPoints.length()):
                    if(bsPoint[i].distanceTo(origPoints[i])>ignoreDis):

                        mirBsPoint[mirIdxList[i]].x=bsPoint[i].x*axis[0]
                        mirBsPoint[mirIdxList[i]].y=bsPoint[i].y*axis[1]
                        mirBsPoint[mirIdxList[i]].z=bsPoint[i].z*axis[2]

                self.setMeshPoints(mirBsTargetMesh,mirBsPoint)
                mirBsMeshList.append(mirBsTargetMesh)


            self.updateDrivenListInfo(Reload=True)
        finally:
            cmds.undoInfo(swf=1)    
class BBodyRigging():
    def __init__(self,rootPath='E:/myCode/sdd_bodyRigging/'):
        self.rootPath=rootPath
        self.filesPath=self.rootPath+'files/'
        self.CrtModule=CorrectBSModule()
    def importJointTemplate(self,*args):
        JointTemplatePath=self.filesPath+'Template/BaseJoint.ma'
        fullPath=unicode(JointTemplatePath,'gbk')
        cmds.file(fullPath,i=1,type="mayaAscii")
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
    def mirrorJoint(self,*args):
        prefix=args[0]
        jntCtrl='Temp_Ctrl'
        if(not cmds.objExists(jntCtrl)):
            raise RuntimeError,'%s is not exists!'%jntCtrl
            return
        if(prefix=='select'):
            sel=cmds.ls(sl=1)
            if len(sel)==0:
                return
            allJoint=sel
        else:
            allJoint=cmds.listRelatives(jntCtrl,c=1,typ='joint',ad=1)
        attrStrList=('tx','ty','tz','rx','ry','rz')
        
        for jnt in allJoint:
            if(prefix!='select' and jnt[:2]!=prefix):
                continue
            mirJnt=self.getMirrorName(jnt)
            pObj=cmds.listRelatives(jnt,p=1,typ='joint')
            if(mirJnt==jnt):
                mirValueList=(1,-1,1,1,1,-1)
            elif(pObj==None):
                mirValueList=(-1,1,1,1,1,1)
            else:
                mirValueList=(-1,-1,-1,1,1,1)
            for attr,mirVal in zip(attrStrList,mirValueList):
                isLock=cmds.getAttr(mirJnt+'.'+attr,l=1)
                if(isLock):
                    continue
                val=cmds.getAttr(jnt+'.'+attr)
                cmds.setAttr(mirJnt+'.'+attr,mirVal*val)

    def armRig(self,shoulderJnt,uparmJnt,lowarmJnt,handJnt):
        armRigGrp=uparmJnt+'_rig_grp'
        armRigGrp=cmds.group(em=1,n=armRigGrp)
        cmds.delete(cmds.parentConstraint(uparmJnt,armRigGrp))
        allCtrl='all_ctrl'
        cmds.parent(armRigGrp,allCtrl)
        # shoulder rig
        shoulderRigGrp=shoulderJnt+'_rig_grp'
        shoulderRigGrp=cmds.group(em=1,n=shoulderRigGrp)
        cmds.delete(cmds.parentConstraint(shoulderJnt,shoulderRigGrp))

        shoulderIkGrp=shoulderJnt+'_ik_grp'
        shoulderIkGrp=cmds.group(em=1,n=shoulderIkGrp)
        cmds.delete(cmds.parentConstraint(shoulderRigGrp,shoulderIkGrp))
        cmds.parent(shoulderIkGrp,shoulderRigGrp)
        cmds.setAttr(shoulderIkGrp+'.visibility',0)

        shoulderIk=cmds.duplicate(shoulderJnt,po=1,rr=1,n=shoulderJnt+'_ik')[0]
        cmds.parent(shoulderIk,shoulderIkGrp)
        shoulderIkEnd=cmds.duplicate(uparmJnt,po=1,rr=1,n=shoulderJnt+'_ik_end')[0]
        cmds.parent(shoulderIkEnd,shoulderIk)


        shoulderIkCtrlGrp=shoulderJnt+'_ik_ctrl_grp'
        shoulderIkCtrlGrp=cmds.group(em=1,n=shoulderIkCtrlGrp)
        cmds.delete(cmds.parentConstraint(shoulderRigGrp,shoulderIkCtrlGrp))
        cmds.parent(shoulderIkCtrlGrp,shoulderRigGrp)

        shoulderCtrl=shoulderJnt+'_ctrl'
        shoulderCtrlZero=ControlUtility.createControl(shoulderCtrl,'Sphere')
        cmds.delete(cmds.parentConstraint(shoulderJnt,shoulderCtrlZero))
        cmds.parent(shoulderCtrlZero,shoulderIkCtrlGrp)
        dis=GeneralUtility.getDistance(shoulderIk,shoulderIkEnd)
        vec=OpenMaya.MVector(1,0,0)+OpenMaya.MVector(0,0,-0.8)
        ControlUtility.moveCV(shoulderCtrl,vec*dis,space='object')
        ControlUtility.scaleCV(shoulderCtrl,2)

        shoulderIkHandle=shoulderJnt+'_ikHandle'
        shoulderIkHandle=cmds.ikHandle(sj=shoulderIk,ee=shoulderIkEnd,n=shoulderIkHandle,sol='ikRPsolver')[0]
        cmds.parent(shoulderIkHandle,shoulderCtrl)
        cmds.setAttr(shoulderIkHandle+'.v',0)

        cmds.parent(shoulderRigGrp,armRigGrp)

        # and follow grp
        shoulderFollowGrp=shoulderJnt+'_follow_grp'
        self.addFollowGrp(shoulderFollowGrp,shoulderIk)

        # ik rig
        armIkRigGrp=uparmJnt+'_ik_rig_grp'
        armIkRigGrp=cmds.group(em=1,n=armIkRigGrp)
        cmds.delete(cmds.parentConstraint(uparmJnt,armIkRigGrp))
        cmds.parent(armIkRigGrp,armRigGrp)

        armIkGrp=uparmJnt+'_ik_jnt_grp'
        armIkGrp=cmds.duplicate(armIkRigGrp,po=1,rr=1,n=armIkGrp)[0]
        cmds.setAttr(armIkGrp+'.visibility',0)
        cmds.parent(armIkGrp,armIkRigGrp)

        uparmIk=cmds.duplicate(uparmJnt,po=1,rr=1,n=uparmJnt+'_ik')[0]
        cmds.parent(uparmIk,armIkGrp)

        lowarmIk=cmds.duplicate(lowarmJnt,po=1,rr=1,n=lowarmJnt+'_ik')[0]
        cmds.parent(lowarmIk,uparmIk)

        handIk=cmds.duplicate(handJnt,po=1,rr=1,n=handJnt+'_ik')[0]
        cmds.parent(handIk,lowarmIk)


        armIkCtrlGrp=uparmJnt+'_ik_ctrl_grp'
        armIkCtrlGrp=cmds.duplicate(armIkRigGrp,po=1,rr=1,n=armIkCtrlGrp)[0]
        cmds.parent(armIkCtrlGrp,armIkRigGrp)

        armIkRootCtrl=uparmIk+'_root_ctrl'
        armIkRootCtrlZero=ControlUtility.createControl(armIkRootCtrl,'Sphere')
        cmds.delete(cmds.parentConstraint(uparmIk,armIkRootCtrlZero))
        cmds.parent(armIkRootCtrlZero,armIkCtrlGrp)
        cmds.parentConstraint(armIkRootCtrl,armIkGrp,mo=1)


        armIkCtrl=uparmIk+'_ctrl'
        armIkCtrlZero=ControlUtility.createControl(armIkCtrl,'Cube')
        cmds.delete(cmds.parentConstraint(handIk,armIkCtrlZero))
        cmds.parent(armIkCtrlZero,armIkCtrlGrp)
        ControlUtility.scaleCV(armIkCtrl,[5,30,30])

        
        armIkPoleCtrl=uparmIk+'_pole_ctrl'
        armIkPoleCtrlZero=ControlUtility.createControl(armIkPoleCtrl,'Sphere',R=False)
        cmds.delete(cmds.parentConstraint(uparmIk,armIkPoleCtrlZero))
        cmds.delete(cmds.pointConstraint(lowarmIk,armIkPoleCtrlZero))
        cmds.parent(armIkPoleCtrlZero,armIkCtrlGrp)
        vec=GeneralUtility.getPoleMoveVector(uparmIk,lowarmIk,handIk)
        cmds.move(vec.x,vec.y,vec.z,armIkPoleCtrlZero,r=1)


        armIkHandle=uparmJnt+'_ikHandle'
        armIkHandle=cmds.ikHandle(sj=uparmIk,ee=handIk,n=armIkHandle,sol='ikRPsolver')[0]
        cmds.parent(armIkHandle,armIkCtrl)
        cmds.poleVectorConstraint(armIkPoleCtrl,armIkHandle)
        cmds.orientConstraint(armIkCtrl,handIk)
        cmds.setAttr(armIkHandle+'.v',0)


        armIkLocGrp=uparmJnt+'_ik_loc_grp'
        armIkLocGrp=cmds.duplicate(armIkRigGrp,po=1,rr=1,n=armIkLocGrp)[0]
        cmds.parent(armIkLocGrp,armIkRigGrp)
        cmds.setAttr(armIkLocGrp+'.v',0)
        cmds.parentConstraint(armIkRootCtrl,armIkLocGrp,mo=1)

        uparmIkLoc=uparmIk+'_loc'
        uparmIkLoc=cmds.spaceLocator(n=uparmIkLoc)[0]
        cmds.delete(cmds.pointConstraint(uparmIk,uparmIkLoc))
        cmds.parent(uparmIkLoc,armIkLocGrp)

        uparmIkPoleLoc=armIkPoleCtrl+'_loc'
        uparmIkPoleLoc=cmds.spaceLocator(n=uparmIkPoleLoc)[0]
        cmds.pointConstraint(armIkPoleCtrl,uparmIkPoleLoc)
        cmds.parent(uparmIkPoleLoc,armIkLocGrp)

        handIkCtrlLoc=armIkCtrl+'_loc'
        handIkCtrlLoc=cmds.spaceLocator(n=handIkCtrlLoc)[0]
        cmds.pointConstraint(armIkHandle,handIkCtrlLoc)
        cmds.parent(handIkCtrlLoc,armIkLocGrp)

        # root vis
        cmds.addAttr(armIkCtrl,ln='rootVis',at='long',k=1,dv=0,max=1,min=0)
        GeneralUtility.connectAllShapeAttr(armIkRootCtrl,armIkCtrl+'.rootVis','visibility')

        # ik stretch
        upLen=cmds.getAttr(lowarmJnt+'.tx')
        dnLen=cmds.getAttr(handJnt+'.tx')

        cmds.addAttr(armIkCtrl,ln='stretch',at='float',max=1,min=0,k=1)
        cmds.addAttr(armIkCtrl,ln='upLength',at='float',k=1)
        cmds.addAttr(armIkCtrl,ln='dnLength',at='float',k=1)



        upIkStretchAdd=uparmIk+'_stretch_addNode'
        upIkStretchAdd=cmds.createNode('plusMinusAverage',n=upIkStretchAdd)
        cmds.setAttr(upIkStretchAdd+'.i1[0]',abs(upLen))
        cmds.connectAttr(armIkCtrl+'.upLength',upIkStretchAdd+'.i1[1]')

        lowIkStretchAdd=lowarmIk+'_stretch_addNode'
        lowIkStretchAdd=cmds.createNode('plusMinusAverage',n=lowIkStretchAdd)
        cmds.setAttr(lowIkStretchAdd+'.i1[0]',abs(dnLen))
        cmds.connectAttr(armIkCtrl+'.dnLength',lowIkStretchAdd+'.i1[1]',f=1)

        handIkStretchAdd=handIk+'_stretch_addNode'
        handIkStretchAdd=cmds.createNode('plusMinusAverage',n=handIkStretchAdd)
        cmds.connectAttr(lowIkStretchAdd+'.o1',handIkStretchAdd+'.i1[0]')
        cmds.connectAttr(upIkStretchAdd+'.o1',handIkStretchAdd+'.i1[1]')

        handIkStretchLenMul=handIk+'_stretch_len_mulNode'
        handIkStretchLenMul=cmds.createNode('multiplyDivide',n=handIkStretchLenMul)
        cmds.setAttr(handIkStretchLenMul+'.i1x',1 if upLen>0 else -1)
        cmds.setAttr(handIkStretchLenMul+'.i1y',1 if upLen>0 else -1)
        cmds.connectAttr(upIkStretchAdd+'.o1',handIkStretchLenMul+'.i2x')
        cmds.connectAttr(lowIkStretchAdd+'.o1',handIkStretchLenMul+'.i2y')

        handIkStretchDis=handIk+'_stretch_disNode'
        handIkStretchDis=cmds.createNode('distanceBetween',n=handIkStretchDis)
        cmds.connectAttr(uparmIkLoc+'.t',handIkStretchDis+'.p1')
        cmds.connectAttr(handIkCtrlLoc+'.t',handIkStretchDis+'.p2')

        handIkStretchDiv=handIk+'_stretch_divNode'
        handIkStretchDiv=cmds.createNode('multiplyDivide',n=handIkStretchDiv)
        cmds.setAttr(handIkStretchDiv+'.op',2)
        cmds.connectAttr(handIkStretchDis+'.d',handIkStretchDiv+'.i1x')
        cmds.connectAttr(handIkStretchAdd+'.o1',handIkStretchDiv+'.i2x')

        handIkStretchCon=handIk+'_stretch_conNode'
        handIkStretchCon=cmds.createNode('condition',n=handIkStretchCon)
        cmds.connectAttr(handIkStretchDiv+'.ox',handIkStretchCon+'.ft')
        cmds.connectAttr(handIkStretchDiv+'.ox',handIkStretchCon+'.ctr')
        cmds.setAttr(handIkStretchCon+'.st',1)
        cmds.setAttr(handIkStretchCon+'.op',2)
        cmds.setAttr(handIkStretchCon+'.cfr',1)

        handIkStretchBlend=handIk+'_stretch_blendNode'
        handIkStretchBlend=cmds.createNode('blendTwoAttr',n=handIkStretchBlend)

        cmds.setAttr(handIkStretchBlend+'.i[0]',1)
        cmds.connectAttr(handIkStretchCon+'.ocr',handIkStretchBlend+'.i[1]')
        cmds.connectAttr(armIkCtrl+'.stretch',handIkStretchBlend+'.ab')

        handIkStretchMul=handIk+'_mulNode'
        handIkStretchMul=cmds.createNode('multiplyDivide',n=handIkStretchMul)
        cmds.connectAttr(handIkStretchBlend+'.o',handIkStretchMul+'.i1x')
        cmds.connectAttr(handIkStretchBlend+'.o',handIkStretchMul+'.i1y')
        cmds.connectAttr(handIkStretchLenMul+'.ox',handIkStretchMul+'.i2x')
        cmds.connectAttr(handIkStretchLenMul+'.oy',handIkStretchMul+'.i2y')

        # cmds.connectAttr(handIkMul+'.ox',lowarmIk+'.tx')
        # cmds.connectAttr(handIkMul+'.oy',handIk+'.tx')
    
        # pole help line
        self.adddHelpLine(armIkPoleCtrl,lowarmIk,armIkCtrlGrp)
        # ik lock
        
        cmds.addAttr(armIkPoleCtrl,ln='lock',at='float',max=1,min=0,k=1)
        uparmIkDis=uparmIk+'_disNode'
        uparmIkDis=cmds.createNode('distanceBetween',n=uparmIkDis)
        cmds.connectAttr(uparmIkLoc+'.t',uparmIkDis+'.p1')
        cmds.connectAttr(uparmIkPoleLoc+'.t',uparmIkDis+'.p2')

        lowarmIkDis=lowarmIk+'_disNode'
        lowarmIkDis=cmds.createNode('distanceBetween',n=lowarmIkDis)
        cmds.connectAttr(uparmIkPoleLoc+'.t',lowarmIkDis+'.p1')
        cmds.connectAttr(handIkCtrlLoc+'.t',lowarmIkDis+'.p2')

        uparmIkLockDiv=uparmIk+'_lock_divNode'
        uparmIkLockDiv=cmds.createNode('multiplyDivide',n=uparmIkLockDiv)
        cmds.connectAttr(uparmIkDis+'.d',uparmIkLockDiv+'.i1x')
        cmds.setAttr(uparmIkLockDiv+'.i2x',abs(upLen))
        cmds.connectAttr(lowarmIkDis+'.d',uparmIkLockDiv+'.i1y')
        cmds.setAttr(uparmIkLockDiv+'.i2y',abs(dnLen))
        cmds.setAttr(uparmIkLockDiv+'.op',2)

        uparmIkLockMul=uparmIk+'_lock_mulNode'
        uparmIkLockMul=cmds.createNode('multiplyDivide',n=uparmIkLockMul)
        cmds.connectAttr(uparmIkLockDiv+'.ox',uparmIkLockMul+'.i1x')
        cmds.setAttr(uparmIkLockMul+'.i2x',upLen)
        cmds.connectAttr(uparmIkLockDiv+'.oy',uparmIkLockMul+'.i1y')
        cmds.setAttr(uparmIkLockMul+'.i2y',dnLen)

        
        # blend ik stretch and lock
        uparmIkLockBlend=uparmIk+'_stretch_lock_blendNode'
        uparmIkLockBlend=cmds.createNode('blendColors',n=uparmIkLockBlend)
        cmds.connectAttr(uparmIkLockMul+'.ox',uparmIkLockBlend+'.c1r',f=1)
        cmds.connectAttr(uparmIkLockMul+'.oy',uparmIkLockBlend+'.c1g',f=1)
        cmds.connectAttr(handIkStretchMul+'.ox',uparmIkLockBlend+'.c2r',f=1)
        cmds.connectAttr(handIkStretchMul+'.oy',uparmIkLockBlend+'.c2g',f=1)
        cmds.connectAttr(armIkPoleCtrl+'.lock',uparmIkLockBlend+'.b')


        cmds.connectAttr(uparmIkLockBlend+'.opr',lowarmIk+'.tx')
        cmds.connectAttr(uparmIkLockBlend+'.opg',handIk+'.tx')


        # fk rig
        armFkRigGrp=uparmJnt+'_fk_rig_grp'
        armFkRigGrp=cmds.group(em=1,n=armFkRigGrp)
        cmds.delete(cmds.parentConstraint(uparmJnt,armFkRigGrp))
        cmds.parent(armFkRigGrp,armRigGrp)

        armFkJntGrp=uparmJnt+'_fk_jnt_grp'
        armFkJntGrp=cmds.duplicate(armFkRigGrp,po=1,rr=1,n=armFkJntGrp)[0]
        cmds.parent(armFkJntGrp,armFkRigGrp)
        cmds.setAttr(armFkJntGrp+'.visibility',0)

        uparmFk=cmds.duplicate(uparmJnt,po=1,rr=1,n=uparmJnt+'_fk')[0]
        cmds.parent(uparmFk,armFkJntGrp)

        lowarmFk=cmds.duplicate(lowarmJnt,po=1,rr=1,n=lowarmJnt+'_fk')[0]
        cmds.parent(lowarmFk,uparmFk)

        handFk=cmds.duplicate(handJnt,po=1,rr=1,n=handJnt+'_fk')[0]
        cmds.parent(handFk,lowarmFk)

        armFkCtrlGrp=uparmJnt+'_fk_Ctrl_grp'
        armFkCtrlGrp=cmds.duplicate(armFkRigGrp,po=1,rr=1,n=armFkCtrlGrp)[0]
        cmds.parent(armFkCtrlGrp,armFkRigGrp)


        uparmFkCtrl=uparmFk+'_ctrl'
        uparmFkCtrlZero=ControlUtility.createControl(uparmFkCtrl,'Circle',T=False)
        uparmFkRootCtrl=uparmFk+'_root_ctrl'
        uparmFkRootCtrl=cmds.duplicate(uparmFkCtrl,n=uparmFkRootCtrl,rr=1)[0]
        cmds.parent(uparmFkCtrl,uparmFkRootCtrl)
        cmds.addAttr(uparmFkCtrl,ln='rootVis',at='long',k=1,max=0,min=1,dv=0)
        ControlUtility.scaleCV(uparmFkRootCtrl,5)
        GeneralUtility.connectAllShapeAttr(uparmFkRootCtrl,uparmFkCtrl+'.rootVis','visibility')

        cmds.delete(cmds.parentConstraint(uparmFk,uparmFkCtrlZero))
        cmds.parentConstraint(uparmFkCtrl,uparmFk,mo=1)
        cmds.parent(uparmFkCtrlZero,armFkCtrlGrp)
        ControlUtility.scaleCV(uparmFkCtrl,4)


        lowarmFkCtrl=lowarmFk+'_ctrl'
        lowarmFkCtrlZero=ControlUtility.createControl(lowarmFkCtrl,'Circle',T=False)
        # ControlUtility.lockRotate(lowarmFkCtrl,z=0)
        cmds.delete(cmds.parentConstraint(lowarmFk,lowarmFkCtrlZero))
        cmds.parentConstraint(lowarmFkCtrl,lowarmFk,mo=1)
        cmds.parent(lowarmFkCtrlZero,uparmFkCtrl)
        ControlUtility.scaleCV(lowarmFkCtrl,4)


        handFkCtrl=handFk+'_ctrl'
        handFkCtrlZero=ControlUtility.createControl(handFkCtrl,'Circle',T=False)
        cmds.delete(cmds.parentConstraint(handFk,handFkCtrlZero))
        cmds.parentConstraint(handFkCtrl,handFk,mo=1)
        cmds.parent(handFkCtrlZero,lowarmFkCtrl)
        ControlUtility.scaleCV(handFkCtrl,4)



        # fk stretch
        cmds.addAttr(uparmFkCtrl,ln='upLength',at='float',k=1)

        uparmFkAdd=uparmFk+'_stretch_addNode'
        uparmFkAdd=cmds.createNode('plusMinusAverage',n=uparmFkAdd)
        cmds.connectAttr(uparmFkCtrl+'.upLength',uparmFkAdd+'.i1[0]')
        cmds.setAttr(uparmFkAdd+'.i1[1]',cmds.getAttr(lowarmFkCtrlZero+'.tx'))
        cmds.connectAttr(uparmFkAdd+'.o1',lowarmFkCtrlZero+'.tx')

        cmds.addAttr(lowarmFkCtrl,ln='dnLength',at='float',k=1)
        lowarmFkAdd=lowarmFk+'_stretch_addNode'
        lowarmFkAdd=cmds.createNode('plusMinusAverage',n=lowarmFkAdd)
        cmds.connectAttr(lowarmFkCtrl+'.dnLength',lowarmFkAdd+'.i1[0]')
        cmds.setAttr(lowarmFkAdd+'.i1[1]',cmds.getAttr(handFkCtrlZero+'.tx'))
        cmds.connectAttr(lowarmFkAdd+'.o1',handFkCtrlZero+'.tx')



        # dri jnt
        armDrJntGrp=uparmJnt+'_dr_jnt_grp'
        armDrJntGrp=cmds.group(em=1,n=armDrJntGrp)
        cmds.delete(cmds.parentConstraint(shoulderJnt,armDrJntGrp))
        cmds.parent(armDrJntGrp,armRigGrp)
        cmds.setAttr(armDrJntGrp+'.visibility',0)

        shoulderDr=cmds.duplicate(shoulderJnt,po=1,rr=1,n=shoulderJnt+'_dr')[0]
        cmds.parent(shoulderDr,armDrJntGrp)


        uparmDr=cmds.duplicate(uparmJnt,po=1,rr=1,n=uparmJnt+'_dr')[0]
        cmds.parent(uparmDr,shoulderDr)

        lowarmDr=cmds.duplicate(lowarmJnt,po=1,rr=1,n=lowarmJnt+'_dr')[0]
        cmds.parent(lowarmDr,uparmDr)

        handDr=cmds.duplicate(handJnt,po=1,rr=1,n=handJnt+'_dr')[0]
        cmds.parent(handDr,lowarmDr)

        armSwitchCtrl=uparmJnt+'_switch_ctrl'
        armSwitchCtrlZero=ControlUtility.createControl(armSwitchCtrl,'Cross',T=False,R=False)
        cmds.parentConstraint(handDr,armSwitchCtrlZero)
        cmds.parent(armSwitchCtrlZero,armRigGrp)
        dis=GeneralUtility.getDistance(lowarmJnt,handJnt)
        vec=OpenMaya.MVector(0,0,-1)
        ControlUtility.moveCV(armSwitchCtrl,vec*dis*0.3,space='object')


        cmds.parentConstraint(shoulderIk,shoulderDr,mo=1)
        # ik fk switch
        cmds.addAttr(armSwitchCtrl,ln='ikfk',at='long',k=1,dv=0,max=1,min=0)

        armSwitchRev=armSwitchCtrl+'_ikfk_revNode'
        armSwitchRev=cmds.createNode('reverse',n=armSwitchRev)
        cmds.connectAttr(armSwitchCtrl+'.ikfk',armSwitchRev+'.ix')



        ikfkAttr=armSwitchCtrl+'.ikfk'
        ikfkInvAttr=armSwitchRev+'.ox'
        uparmCon=cmds.parentConstraint(uparmIk,uparmFk,uparmDr)[0]
        cmds.connectAttr(ikfkInvAttr,uparmCon+'.w0')
        cmds.connectAttr(ikfkAttr,uparmCon+'.w1')

        lowarmCon=cmds.parentConstraint(lowarmIk,lowarmFk,lowarmDr)[0]
        cmds.connectAttr(ikfkInvAttr,lowarmCon+'.w0')
        cmds.connectAttr(ikfkAttr,lowarmCon+'.w1')

        handCon=cmds.parentConstraint(handIk,handFk,handDr)[0]
        cmds.connectAttr(ikfkInvAttr,handCon+'.w0')
        cmds.connectAttr(ikfkAttr,handCon+'.w1')

        cmds.connectAttr(ikfkInvAttr,armIkRigGrp+'.v')
        cmds.connectAttr(ikfkAttr,armFkRigGrp+'.v')


        # twist second
        cmds.addAttr(armSwitchCtrl,ln='secVis',at='long',k=1,max=0,min=1,dv=0)
        switchAttr=armSwitchCtrl+'.secVis'
        eZero=self.addSceondRig(uparmJnt,uparmDr,lowarmDr,armRigGrp,switchAttr,typ='up')
        sCtrl=self.addSceondRig(lowarmJnt,lowarmDr,handDr,armRigGrp,switchAttr,typ='low')
        cmds.delete(cmds.pointConstraint(eZero,q=1,n=1))
        cmds.pointConstraint(sCtrl,eZero)
        cmds.setAttr(eZero+'.v',0)

        # dr jnt grp follow
        armDrJntFollowChest=armDrJntGrp+'_follow_chest'
        self.addFollowToGrp(armDrJntFollowChest,armDrJntGrp,'Chest')
        cmds.parentConstraint(armDrJntFollowChest,armDrJntGrp)

        # shoulder follow
        shoulderFollowChest=shoulderRigGrp+'_follow_chest'
        self.addFollowToGrp(shoulderFollowChest,shoulderRigGrp,'Chest')
        cmds.parentConstraint(shoulderFollowChest,shoulderRigGrp)
        # arm ik follow
        armIkFollowShoulder=armIkRootCtrlZero+'_follow_Shoulder'
        self.addFollowToGrp(armIkFollowShoulder,armIkRootCtrlZero,shoulderFollowGrp)
        cmds.parentConstraint(armIkFollowShoulder,armIkRootCtrlZero)

        # ik pole follow
        cmds.addAttr(armIkPoleCtrl,ln='follow',at='enum',en='hand:shoulder:world',k=1)

        armPoleFollowShoulder=armIkPoleCtrlZero+'_follow_shoulder'
        self.addFollowToGrp(armPoleFollowShoulder,uparmIk,shoulderFollowGrp)
        tx=cmds.getAttr(lowarmJnt+'.tx')
        direction=tx/abs(tx)
        cmds.aimConstraint(armIkCtrl,armPoleFollowShoulder,mo=1,aim=(direction,0,0),u=(0,0,1),wut="objectrotation",wu=(0,0,1),wuo=armIkCtrl)
        armIkPoleFollowRot=cmds.duplicate(armPoleFollowShoulder,n=uparmIk+'_pole_follow_rot',po=1,rr=1)[0]
        cmds.parent(armIkPoleFollowRot,armPoleFollowShoulder)
        armIkPoleFollowCon=cmds.duplicate(armPoleFollowShoulder,n=uparmIk+'_pole_follow_con',po=1,rr=1)[0]
        cmds.delete(cmds.parentConstraint(armIkPoleCtrl,armIkPoleFollowCon))
        cmds.parent(armIkPoleFollowCon,armIkPoleFollowRot)

        driverAttr=handIkStretchDis+'.d'
        drivenAttr=armIkPoleFollowRot+'.rz'
        driverValue=cmds.getAttr(driverAttr)
        cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=0,dv=driverValue,itt='linear',ott='linear')
        cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=-45,dv=0,itt='linear',ott='linear')

        armPoleFollowShoulderNorol=armIkPoleCtrlZero+'_follow_shoulder_norol'
        self.addFollowToGrp(armPoleFollowShoulderNorol,armIkPoleCtrlZero,shoulderFollowGrp)

        armPoleFollowWrold=armIkPoleCtrlZero+'_follow_world'
        self.addFollowToGrp(armPoleFollowWrold,armIkPoleCtrlZero,'World')

        followList=[armIkPoleFollowCon,armPoleFollowShoulderNorol,armPoleFollowWrold]
        followAttr=armIkPoleCtrl+'.follow'
        self.addConstraintByFollowList(followList,armIkPoleCtrlZero,followAttr)


        # hand ik follow
        cmds.addAttr(armIkCtrl,ln='follow',at='enum',en='world:body:hip:chest:head:shoulder',k=1)

        armIkFollowWorld=armIkCtrlZero+'_follow_world'
        self.addFollowToGrp(armIkFollowWorld,armIkCtrlZero,'World')

        armIkFollowBody=armIkCtrlZero+'_follow_body'
        self.addFollowToGrp(armIkFollowBody,armIkCtrlZero,'Body')

        armIkFollowHip=armIkCtrlZero+'_follow_hip'
        self.addFollowToGrp(armIkFollowHip,armIkCtrlZero,'Hip')

        armIkFollowChest=armIkCtrlZero+'_follow_chest'
        self.addFollowToGrp(armIkFollowChest,armIkCtrlZero,'Chest')

        armIkFollowHead=armIkCtrlZero+'_follow_head'
        self.addFollowToGrp(armIkFollowHead,armIkCtrlZero,'Head')

        armIkFollowShoulder=armIkCtrlZero+'_follow_shoulder'
        self.addFollowToGrp(armIkFollowShoulder,armIkCtrlZero,shoulderFollowGrp)

        followList=[armIkFollowWorld,armIkFollowBody,armIkFollowHip,armIkFollowChest,armIkFollowHead,armIkFollowShoulder]
        followAttr=armIkCtrl+'.follow'
        self.addConstraintByFollowList(followList,armIkCtrlZero,followAttr)



        # arm fk follow

        cmds.addAttr(uparmFkCtrl,ln='follow',at='long',k=1,max=0,min=1,dv=1)
        followInv=cmds.createNode('reverse',n=uparmFkCtrl+'_follow_invNode')
        cmds.connectAttr(uparmFkCtrl+'.follow',followInv+'.ix')

        armFkFollowShoulder=armFkCtrlGrp+'_follow_shoulder'
        self.addFollowToGrp(armFkFollowShoulder,armFkCtrlGrp,shoulderFollowGrp)

        armFkFollowWorld=armFkCtrlGrp+'_follow_world'
        self.addFollowToGrp(armFkFollowWorld,armFkCtrlGrp,'World')

        cmds.pointConstraint(armFkFollowShoulder,armFkCtrlGrp)
        con=cmds.orientConstraint(armFkFollowShoulder,armFkFollowWorld,armFkCtrlGrp)[0]
        cmds.connectAttr(uparmFkCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')

        self.fingerRig(handJnt,handDr,armSwitchCtrl)

        # ikfk Match
        ctrlList=[uparmFkCtrl,lowarmFkCtrl,handFkCtrl,armIkPoleCtrl,armIkCtrl]
        drList=[uparmDr,lowarmDr,handDr,[uparmDr,lowarmDr],handDr]
        for ctrl,drJnt in zip(ctrlList,drList):
            self.addIkfkMathGroup(ctrl,drJnt)

    def addIkfkMathGroup(self,ctrl,drJnt):
        matchGrp=ctrl+'_match'
        matchGrp=cmds.group(em=1,n=matchGrp)
        cmds.parent(matchGrp,ctrl)
        GeneralUtility.resetTransformAttr(matchGrp)
        pObj=cmds.listRelatives(ctrl,p=1)[0]
        cmds.parent(matchGrp,pObj)
        cmds.parentConstraint(drJnt,matchGrp,mo=1)

    def adddHelpLine(self,sObj,eObj,rigGrp):
        grp=sObj+'_helpline_grp'
        grp=cmds.group(em=1,n=grp)
        cmds.parent(grp,rigGrp)
        cmds.setAttr(grp+'.it',0)
        curve=cmds.curve(n=sObj+'_helpline',d=1,p=[(0,0,0),(1,0,0)])
        cmds.setAttr(curve+'.overrideEnabled',1)
        cmds.setAttr(curve+'.overrideDisplayType',2)
        cmds.parent(curve,grp)
        loc1=cmds.spaceLocator(n=curve+'_loc1')[0]
        cmds.connectAttr(loc1+'.worldPosition',curve+'.cv[0]')
        cmds.pointConstraint(sObj,loc1)
        cmds.setAttr(loc1+'.visibility',0)
        cmds.parent(loc1,grp)
        loc2=cmds.spaceLocator(n=curve+'_loc2')[0]
        cmds.connectAttr(loc2+'.worldPosition',curve+'.cv[1]')
        cmds.setAttr(loc2+'.visibility',0)
        cmds.parent(loc2,grp)
        cmds.pointConstraint(eObj,loc2)
        
    def addConstraintByFollowList(self,followList,conObj,followAttr):
        for idx,followGrp in enumerate(followList):
            con=cmds.parentConstraint(followGrp,conObj)
            if(isinstance(con,list)):
                con=con[0]
            followCond=cmds.createNode('condition',n=followGrp+'_condNode')
            cmds.connectAttr(followAttr,followCond+'.ft')
            cmds.setAttr(followCond+'.st',idx)
            cmds.setAttr(followCond+'.ctr',1)
            cmds.setAttr(followCond+'.cfr',0)
            cmds.setAttr(followCond+'.op',0)
            cmds.connectAttr(followCond+'.ocr',con+'.w%s'%idx)

    def addSceondRig(self,upJnt,upDr,lowDr,RigGrp,switchAttr,typ='up'):
        jLen=cmds.getAttr(lowDr+'.tx')
        upjntTwistGrp=upJnt+'_twist_grp'
        upjntTwistGrp=cmds.group(em=1,n=upjntTwistGrp)
        cmds.delete(cmds.parentConstraint(upDr,upjntTwistGrp))
        cmds.parent(upjntTwistGrp,upDr if typ=='up' else lowDr)
        cmds.setAttr(upjntTwistGrp+'.v',0)

        upjntNonRoll=upJnt+'_nonroll'
        upjntNonRoll=cmds.duplicate(upDr if typ=='up' else lowDr,po=1,rr=1,n=upjntNonRoll)[0]
        cmds.parent(upjntNonRoll,upjntTwistGrp)


        upjntNonRollEnd=upJnt+'_nonroll_end'
        upjntNonRollEnd=cmds.duplicate(upDr if typ=='up' else lowDr,po=1,rr=1,n=upjntNonRollEnd)[0]
        cmds.parent(upjntNonRollEnd,upjntNonRoll)

        cmds.setAttr(upjntNonRollEnd+'.ty',l=1)
        cmds.setAttr(upjntNonRollEnd+'.tz',l=1)
        vec=GeneralUtility.getVector(upDr,lowDr)
        vec.normalize()
        cmds.move(vec.x,vec.y,vec.z,upjntNonRollEnd,r=1)

        upjntNonRollIkHandle=upjntNonRoll+'_ikHandle'
        upjntNonRollIkHandle=cmds.ikHandle(sj=upjntNonRoll,ee=upjntNonRollEnd,n=upjntNonRollIkHandle,sol='ikSCsolver')[0]
        pObj=cmds.listRelatives(upDr if typ=='up' else lowDr,p=1)[0]
        cmds.parent(upjntNonRollIkHandle,pObj)
        upjntNonRollIkHandleZero=ControlUtility.createZeroGrp(upjntNonRollIkHandle,Mirror=False)
        cmds.setAttr(upjntNonRollIkHandleZero+'.v',0)

        followjntLoc=upjntNonRoll+'_follow_jnt_loc'
        followjntLoc=cmds.spaceLocator(n=followjntLoc)[0]
        cmds.delete(cmds.parentConstraint(upjntNonRollEnd,followjntLoc))
        cmds.parent(followjntLoc,upjntTwistGrp)
        cmds.pointConstraint(followjntLoc,upjntNonRollIkHandle)

        upjntTwist=upJnt+'_twist'
        upjntTwist=cmds.duplicate(upjntNonRoll,po=1,rr=1,n=upjntTwist)[0]
        cmds.parent(upjntTwist,upjntNonRoll)

        upjntTwistEnd=upJnt+'_twist_end'
        upjntTwistEnd=cmds.duplicate(upjntNonRollEnd,po=1,rr=1,n=upjntTwistEnd)[0]
        cmds.parent(upjntTwistEnd,upjntTwist)

        followTwistAimLoc=upjntTwist+'_aim_loc'
        followTwistAimLoc=cmds.spaceLocator(n=followTwistAimLoc)[0]
        cmds.delete(cmds.parentConstraint(upjntTwistEnd,followTwistAimLoc))
        cmds.parent(followTwistAimLoc,upjntTwistGrp)

        followTwistUpLoc=upjntTwist+'_up_loc'
        followTwistUpLoc=cmds.spaceLocator(n=followTwistUpLoc)[0]
        cmds.delete(cmds.parentConstraint(upjntTwist,followTwistUpLoc))
        cmds.parent(followTwistUpLoc,upjntTwistGrp)
        cmds.aimConstraint(followTwistAimLoc,upjntTwist,aim=(jLen/abs(jLen),0,0),u=(0,0,1),wut="objectrotation",wu=(0,0,1),wuo=followTwistUpLoc)


        secondeRigGrp=upJnt+'_second_rig_grp'
        secondeRigGrp=cmds.group(em=1,n=secondeRigGrp)
        cmds.delete(cmds.parentConstraint(upDr,secondeRigGrp))
        cmds.parent(secondeRigGrp,RigGrp)

        secondeRotGrp=upJnt+'_second_rotation_grp'
        secondeRotGrp=cmds.duplicate(secondeRigGrp,po=1,rr=1,n=secondeRotGrp)[0]
        cmds.parent(secondeRotGrp,secondeRigGrp)
        cmds.parentConstraint(upDr,secondeRotGrp)

        
        secondeRotList=[]
        for i in range(5):
            secondeRot=upJnt+'_sec%s_rotation'%(i+1)
            secondeRot=cmds.duplicate(secondeRotGrp,po=1,rr=1,n=secondeRot)[0]
            cmds.setAttr(secondeRot+'.tx',i*(jLen/4))
            cmds.parent(secondeRot,secondeRotGrp)
            secondeRotMul=cmds.createNode('multiplyDivide',n=secondeRot+'_mulNode')
            cmds.connectAttr(upjntTwist+'.rx',secondeRotMul+'.i1x')
            if(typ=='up'):
                cmds.setAttr(secondeRotMul+'.i2x',(1-i*0.25)*-1)
            else:
                cmds.setAttr(secondeRotMul+'.i2x',i*0.25)

            cmds.connectAttr(secondeRotMul+'.ox',secondeRot+'.rx')
            secondeRotList.append(secondeRot)

        sPos=cmds.xform(upDr,q=1,ws=1,t=1)
        ePos=cmds.xform(lowDr,q=1,ws=1,t=1)
        mPos=[(sPos[0]+ePos[0])*0.5,(sPos[1]+ePos[1])*0.5,(sPos[2]+ePos[2])*0.5]

        secondCurve=upJnt+'_second_curve'
        secondCurve=cmds.curve(n=secondCurve,d=2,p=[sPos,mPos,ePos])
        cmds.setAttr(secondCurve+'.it',0)
        secondCurveZero=ControlUtility.createZeroGrp(secondCurve,Mirror=False)
        cmds.parent(secondCurveZero,secondeRigGrp)
        cmds.setAttr(secondCurveZero+'.visibility',0)


        secondeCtrlGrp=upJnt+'_second_ctrl_grp'
        secondeCtrlGrp=cmds.duplicate(secondeRigGrp,po=1,rr=1,n=secondeCtrlGrp)[0]
        cmds.parent(secondeCtrlGrp,secondeRigGrp)
        cmds.parentConstraint(upDr,secondeCtrlGrp)
        cmds.connectAttr(switchAttr,secondeCtrlGrp+'.v')


        secondSCtrl=upJnt+'_second_01_ctrl'
        secondSCtrlZero=ControlUtility.createControl(secondSCtrl,'Rect')
        secondSCtrlLoc=cmds.spaceLocator(n=secondSCtrl+'_loc')[0]
        cmds.setAttr(secondSCtrlLoc+'.visibility',0)
        cmds.parent(secondSCtrlLoc,secondSCtrl)
        cmds.delete(cmds.parentConstraint(upDr,secondSCtrlZero))
        cmds.parent(secondSCtrlZero,secondeCtrlGrp)
        cmds.connectAttr(secondSCtrlLoc+'.worldPosition',secondCurve+'.cv[0]')

        secondECtrl=upJnt+'_second_03_ctrl'
        secondECtrlZero=ControlUtility.createControl(secondECtrl,'Rect')
        secondECtrlLoc=cmds.spaceLocator(n=secondECtrl+'_loc')[0]
        cmds.setAttr(secondECtrlLoc+'.visibility',0)
        cmds.parent(secondECtrlLoc,secondECtrl)
        cmds.delete(cmds.parentConstraint(lowDr,secondECtrlZero))
        cmds.parent(secondECtrlZero,secondeCtrlGrp)
        cmds.connectAttr(secondECtrlLoc+'.worldPosition',secondCurve+'.cv[2]')
        cmds.pointConstraint(lowDr,secondECtrlZero)

        secondMCtrl=upJnt+'_second_02_ctrl'
        secondMCtrlZero=ControlUtility.createControl(secondMCtrl,'Rect')
        secondMCtrlLoc=cmds.spaceLocator(n=secondMCtrl+'_loc')[0]
        cmds.setAttr(secondMCtrlLoc+'.visibility',0)
        cmds.parent(secondMCtrlLoc,secondMCtrl)
        cmds.pointConstraint(secondSCtrl,secondECtrl,secondMCtrlZero)
        cmds.parent(secondMCtrlZero,secondeCtrlGrp)
        cmds.connectAttr(secondMCtrlLoc+'.worldPosition',secondCurve+'.cv[1]')

        cmds.aimConstraint(secondECtrl,secondMCtrlZero,aim=(jLen/abs(jLen),0,0),u=(0,0,1),wut="objectrotation",wu=(0,0,1),wuo=secondeRotList[2])


        secondePosGrp=upJnt+'_second_position_grp'
        secondePosGrp=cmds.group(em=1,n=secondePosGrp)
        cmds.parent(secondePosGrp,secondeRigGrp)

        secondePosOff=upJnt+'_second_position_off'
        secondePosOff=cmds.group(em=1,n=secondePosOff)
        cmds.parent(secondePosOff,secondePosGrp)
        cmds.setAttr(secondePosOff+'.it',0)

        secondePosList=[]
        for i in range(5):
            secondePos=upJnt+'_sec%s_position'%(i+1)
            secondePos=cmds.group(n=secondePos,em=1)
            cmds.parent(secondePos,secondePosOff)
            secondePosInfo=cmds.createNode('pointOnCurveInfo',n=secondePos+'_infoNode')
            cmds.connectAttr(secondCurve+'.worldSpace',secondePosInfo+'.ic')
            cmds.connectAttr(secondePosInfo+'.p',secondePos+'.t')
            cmds.setAttr(secondePosInfo+'.pr',i*0.25)
            secondePosList.append(secondePos)

        secondeDrGrp=upJnt+'_second_dr_grp'
        secondeDrGrp=cmds.duplicate(secondeRigGrp,po=1,rr=1,n=secondeDrGrp)[0]
        cmds.parent(secondeDrGrp,secondeRigGrp)
        cmds.parentConstraint(upDr,secondeDrGrp)
        cmds.setAttr(secondeDrGrp+'.visibility',0)

        secondeDrList=[]
        for i in range(5):
            secondeDr=upJnt+'_sec%s_dr'%(i+1)
            secondeDr=cmds.duplicate(upDr,n=secondeDr,po=1,rr=1)[0]
            cmds.parent(secondeDr,secondeDrGrp)
            cmds.pointConstraint(secondePosList[i],secondeDr)
            cmds.tangentConstraint(secondCurve,secondeDr,aim=(jLen/abs(jLen),0,0),u=(0,0,1),wut="objectrotation",wu=(0,0,1),wuo=secondeRotList[i])
            # cmds.setAttr(secondeDr+'.displayLocalAxis',1)

        return secondECtrlZero if(typ=='up')else secondSCtrl

    def fingerRig(self,handJnt,handDr,armSwitchCtrl):
        #     pass
        # handJnt='L_hand'
        # handDr=handJnt+'_dr'
        # armSwitchCtrl='L_arm_switch_ctrl'
        cmds.addAttr(armSwitchCtrl,ln='fingerRootVis',at='long',k=1,dv=0,max=1,min=0)
        cmds.addAttr(armSwitchCtrl,ln='thumb',at='float',k=1,dv=0,max=10,min=-2)
        cmds.addAttr(armSwitchCtrl,ln='index',at='float',k=1,dv=0,max=10,min=-2)
        cmds.addAttr(armSwitchCtrl,ln='middle',at='float',k=1,dv=0,max=10,min=-2)
        cmds.addAttr(armSwitchCtrl,ln='ring',at='float',k=1,dv=0,max=10,min=-2)
        cmds.addAttr(armSwitchCtrl,ln='pinky',at='float',k=1,dv=0,max=10,min=-2)


        fingerAllRigGrp=handJnt+'_finger_rig_grp'
        fingerAllRigGrp=cmds.group(em=1,n=fingerAllRigGrp)
        cmds.parentConstraint(handDr,fingerAllRigGrp)
        allCtrl='all_ctrl'
        cmds.parent(fingerAllRigGrp,allCtrl)

        rootJntList=cmds.listRelatives(handJnt,c=1,typ='joint',ad=0)
        for rootJnt in rootJntList:
            fingerRigGrp=rootJnt+'_rig_grp'
            fingerRigGrp=cmds.group(em=1,n=fingerRigGrp)
            cmds.delete(cmds.parentConstraint(rootJnt,fingerRigGrp))
            cmds.parent(fingerRigGrp,fingerAllRigGrp)

            fingerJntList=GeneralUtility.getJointChain(rootJnt)
            # duplicate driver joint
            fingerDrJntGrp=cmds.duplicate(fingerRigGrp,n=rootJnt+'_dr_jnt_grp',po=1,rr=1)[0]
            cmds.parent(fingerDrJntGrp,fingerRigGrp)
            cmds.setAttr(fingerDrJntGrp+'.visibility',0)
            fingerDrList=[]
            for fingerJnt in fingerJntList:
                fingerDr=cmds.duplicate(fingerJnt,po=1,rr=1,n=fingerJnt+'_dr')[0]
                cmds.parent(fingerDr,fingerDrJntGrp)
                fingerDrList.append(fingerDr)
                
            for idx in range(1,len(fingerDrList)):
                cmds.parent(fingerDrList[idx],fingerDrList[idx-1])
            # crate control
            fingerCtrlGrp=cmds.duplicate(fingerRigGrp,n=rootJnt+'_ctrl_grp',po=1,rr=1)[0]
            cmds.parent(fingerCtrlGrp,fingerRigGrp)
            fingerCtrlList=[]
            for idx,fingerJnt in enumerate(fingerJntList[:-1]) :
                fingerCtrl=fingerJnt+'_ctrl'
                if(idx==0):
                    fingerCtrlZero=ControlUtility.createControl(fingerCtrl,'Circle_Line')
                    GeneralUtility.connectAllShapeAttr(fingerCtrl,armSwitchCtrl+'.fingerRootVis','visibility')
                else:
                    fingerCtrlZero=ControlUtility.createControl(fingerCtrl,'Circle_Arrow',T=False)

                ControlUtility.scaleCV(fingerCtrl,0.8,typ='ObjectCenter')
                cmds.delete(cmds.parentConstraint(fingerJnt,fingerCtrlZero))
                cmds.parent(fingerCtrlZero,fingerCtrlGrp)
                cmds.parentConstraint(fingerCtrl,fingerDrList[idx],mo=1)
                fingerCtrlList.append([fingerCtrl,fingerCtrlZero])
            for idx in range(1,len(fingerCtrlList)):
                cmds.parent(fingerCtrlList[idx][1],fingerCtrlList[idx-1][0])
            # curl control
            fingerCurlCtrlGrp=cmds.duplicate(fingerRigGrp,n=rootJnt+'_curl_ctrl_grp',po=1,rr=1)[0]
            cmds.parent(fingerCurlCtrlGrp,fingerRigGrp)
            cmds.parentConstraint(fingerCtrlList[0][0],fingerCurlCtrlGrp)

            fingerCurlCtrl=rootJnt+'_curl_ctrl'
            fingerCurlCtrlZero=ControlUtility.createControl(fingerCurlCtrl,'Root')
            cmds.delete(cmds.parentConstraint(fingerJntList[1],fingerCurlCtrlZero))
            ControlUtility.scaleCV(fingerCurlCtrl,0.05,typ='ObjectCenter')
            vec=GeneralUtility.getVector(fingerJntList[1],fingerJntList[2])
            vec.normalize()
            dis=GeneralUtility.getDistance(fingerJntList[1],fingerJntList[-1])
            vec*=dis*1.5
            cmds.move(vec.x,vec.y,vec.z,fingerCurlCtrlZero,r=1)
            cmds.transformLimits(fingerCurlCtrl,tx=[-1,1],etx=[1,1])#,ty=[-1,1],ety=[1,1],tz=[-1,1],etz=[1,1])

            cmds.setAttr(fingerCurlCtrlZero+'.s',ControlUtility.GlobalScale*5,ControlUtility.GlobalScale*5,ControlUtility.GlobalScale*5,typ='float3')
            
            aimGrp=GeneralUtility.createAimGrp(fingerCtrlList[1][0])

            cmds.aimConstraint(fingerCurlCtrl,aimGrp,aim=(1,0,0),u=(0,1,0),wut="objectrotation",wu=(0,1,0),wuo=fingerCurlCtrl)
            cmds.parent(fingerCurlCtrlZero,fingerCurlCtrlGrp)
            self.adddHelpLine(fingerCurlCtrl,fingerCtrlList[1][0],fingerCurlCtrlGrp)

            for ctrl,ctrlZero in fingerCtrlList[1:]:
                self.createFingerSdk(fingerCurlCtrl,ctrl)

    def createFingerSdk(self,fingerCurlCtrl,ctrl):
        sdkPrefData={
                    'L_thumbfinger_1_ctrl':[(1,15),(-1,-30)],
                    'L_thumbfinger_2_ctrl':[(1,15),(-1,-90)],
                    'L_thumbfinger_3_ctrl':[(1,15),(-1,-90)],
                    'L_indexfinger_1_ctrl':[(1,15),(-1,-90)],
                    'L_indexfinger_2_ctrl':[(1,15),(-1,-90)],
                    'L_indexfinger_3_ctrl':[(1,15),(-1,-90)],
                    'L_middlefinger_1_ctrl':[(1,15),(-1,-90)],
                    'L_middlefinger_2_ctrl':[(1,15),(-1,-90)],
                    'L_middlefinger_3_ctrl':[(1,15),(-1,-90)],
                    'L_ringfinger_1_ctrl':[(1,15),(-1,-90)],
                    'L_ringfinger_2_ctrl':[(1,15),(-1,-90)],
                    'L_ringfinger_3_ctrl':[(1,15),(-1,-90)],
                    'L_pinkyfinger_1_ctrl':[(1,15),(-1,-90)],
                    'L_pinkyfinger_2_ctrl':[(1,15),(-1,-90)],
                    'L_pinkyfinger_3_ctrl':[(1,15),(-1,-90)],

                    'R_thumbfinger_1_ctrl':[(1,15),(-1,-30)],
                    'R_thumbfinger_2_ctrl':[(1,15),(-1,-90)],
                    'R_thumbfinger_3_ctrl':[(1,15),(-1,-90)],
                    'R_indexfinger_1_ctrl':[(1,15),(-1,-90)],
                    'R_indexfinger_2_ctrl':[(1,15),(-1,-90)],
                    'R_indexfinger_3_ctrl':[(1,15),(-1,-90)],
                    'R_middlefinger_1_ctrl':[(1,15),(-1,-90)],
                    'R_middlefinger_2_ctrl':[(1,15),(-1,-90)],
                    'R_middlefinger_3_ctrl':[(1,15),(-1,-90)],
                    'R_ringfinger_1_ctrl':[(1,15),(-1,-90)],
                    'R_ringfinger_2_ctrl':[(1,15),(-1,-90)],
                    'R_ringfinger_3_ctrl':[(1,15),(-1,-90)],
                    'R_pinkyfinger_1_ctrl':[(1,15),(-1,-90)],
                    'R_pinkyfinger_2_ctrl':[(1,15),(-1,-90)],
                    'R_pinkyfinger_3_ctrl':[(1,15),(-1,-90)]
                    }

        sdkGrp=GeneralUtility.createSdkGrp(ctrl)
        driverAttr=fingerCurlCtrl+'.tx'
        drivenAttr=sdkGrp+'.rz'
        cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=0,dv=0,itt='linear',ott='linear')
        print ctrl,sdkPrefData.has_key(ctrl)
        if(sdkPrefData.has_key(ctrl)):
            keyData=sdkPrefData[ctrl]
            for dv,cv in keyData:
                cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=cv,dv=dv,itt='linear',ott='linear')
        else:
            cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=15,dv=1,itt='linear',ott='linear')
            cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=-90,dv=-1,itt='linear',ott='linear')


    def legRig(self,uplegJnt,lowlegJnt,footJnt,toebaseJnt,toeendJnt,toeinJnt,toeoutJnt,heelJnt):
        legRigGrp=uplegJnt+'_rig_grp'
        legRigGrp=cmds.group(em=1,n=legRigGrp)
        cmds.delete(cmds.parentConstraint(uplegJnt,legRigGrp))
        allCtrl='all_ctrl'
        cmds.parent(legRigGrp,allCtrl)
        # cmds.parentConstraint()

        # ik rig
        legIkRigGrp=uplegJnt+'_ik_rig_grp'
        legIkRigGrp=cmds.group(em=1,n=legIkRigGrp)
        cmds.delete(cmds.parentConstraint(uplegJnt,legIkRigGrp))
        cmds.parent(legIkRigGrp,legRigGrp)

        legIkJntGrp=uplegJnt+'_ik_jnt_grp'
        legIkJntGrp=cmds.duplicate(legIkRigGrp,po=1,rr=1,n=legIkJntGrp)[0]
        cmds.parent(legIkJntGrp,legIkRigGrp)
        cmds.setAttr(legIkJntGrp+'.visibility',0)

        uplegIk=cmds.duplicate(uplegJnt,po=1,rr=1,n=uplegJnt+'_ik')[0]
        cmds.parent(uplegIk,legIkJntGrp)

        lowlegIk=cmds.duplicate(lowlegJnt,po=1,rr=1,n=lowlegJnt+'_ik')[0]
        cmds.parent(lowlegIk,uplegIk)

        footIk=cmds.duplicate(footJnt,po=1,rr=1,n=footJnt+'_ik')[0]
        cmds.parent(footIk,lowlegIk)

        toebaseIk=cmds.duplicate(toebaseJnt,po=1,rr=1,n=toebaseJnt+'_ik')[0]
        cmds.parent(toebaseIk,footIk)

        toeendIk=cmds.duplicate(toeendJnt,po=1,rr=1,n=toeendJnt+'_ik')[0]
        cmds.parent(toeendIk,toebaseIk)


        legIkCtrlGrp=uplegJnt+'_ik_ctrl_grp'
        legIkCtrlGrp=cmds.duplicate(legIkRigGrp,po=1,rr=1,n=legIkCtrlGrp)[0]
        cmds.parent(legIkCtrlGrp,legIkRigGrp)

        legIkRootCtrl=uplegIk+'_root_ctrl'
        legIkRootCtrlZero=ControlUtility.createControl(legIkRootCtrl,'Sphere')
        cmds.delete(cmds.parentConstraint(uplegIk,legIkRootCtrlZero))
        cmds.parent(legIkRootCtrlZero,legIkCtrlGrp)
        cmds.parentConstraint(legIkRootCtrl,legIkJntGrp,mo=1)


        legIkCtrl=uplegIk+'_ctrl'
        legIkCtrlZero=ControlUtility.createControl(legIkCtrl,'Heel')
        cmds.delete(cmds.parentConstraint(footIk,legIkCtrlZero))
        cmds.rotate(0,0,90,legIkCtrlZero,r=1,os=1,fo=1)
        cmds.parent(legIkCtrlZero,legIkCtrlGrp)
        vec1=GeneralUtility.getVector(heelJnt,footJnt)
        vec2=GeneralUtility.getVector(heelJnt,toeendJnt)
        pVec=GeneralUtility.getPerpendicularVector(vec1,vec2)
        ControlUtility.moveCV(legIkCtrl,pVec)

        legIkPoleCtrl=uplegIk+'_pole_ctrl'
        legIkPoleCtrlZero=ControlUtility.createControl(legIkPoleCtrl,'Sphere',R=False)
        cmds.delete(cmds.parentConstraint(uplegIk,legIkPoleCtrlZero))
        cmds.delete(cmds.pointConstraint(lowlegIk,legIkPoleCtrlZero))
        cmds.parent(legIkPoleCtrlZero,legIkCtrlGrp)
        vec=GeneralUtility.getPoleMoveVector(uplegIk,lowlegIk,footIk)
        cmds.move(vec.x,vec.y,vec.z,legIkPoleCtrlZero,r=1)


        toebaseIkCtrl=toebaseIk+'_ctrl'
        toebaseIkCtrlZero=ControlUtility.createControl(toebaseIkCtrl,'Toe',T=False)
        cmds.delete(cmds.parentConstraint(toebaseIk,toebaseIkCtrlZero))
        vec1=GeneralUtility.getVector(toeendJnt,toebaseJnt)
        vec2=GeneralUtility.getVector(toeendJnt,heelJnt)
        pVec=GeneralUtility.getPerpendicularVector(vec1,vec2)
        ControlUtility.moveCV(toebaseIkCtrl,pVec)


        toeendIkRot=toeendIk+'_rot'
        toeendIkRotZero=ControlUtility.createControl(toeendIkRot,'None',T=False)
        cmds.delete(cmds.parentConstraint(toeendIk,toeendIkRotZero))

        heelIkRot=heelJnt+'_ik_rot'
        heelIkRotZero=ControlUtility.createControl(heelIkRot,'None',T=False)
        cmds.delete(cmds.parentConstraint(heelJnt,heelIkRotZero))

        toeIkRot=toebaseIk+'_rot'
        toeIkRotZero=ControlUtility.createControl(toeIkRot,'None')
        cmds.delete(cmds.parentConstraint(toebaseIk,toeIkRotZero))

        toeinIkRot=toeinJnt+'_ik_rot'
        toeinIkRotZero=ControlUtility.createControl(toeinIkRot,'None')
        cmds.delete(cmds.parentConstraint(toeinJnt,toeinIkRotZero))

        toeoutIkRot=toeoutJnt+'_ik_rot'
        toeoutIkRotZero=ControlUtility.createControl(toeoutIkRot,'None')
        cmds.delete(cmds.parentConstraint(toeoutJnt,toeoutIkRotZero))


        legIkHandle=uplegJnt+'_ikHandle'
        legIkHandle=cmds.ikHandle(sj=uplegIk,ee=footIk,n=legIkHandle,sol='ikRPsolver')[0]
        cmds.setAttr(legIkHandle+'.v',0)
        footIkHandle=footJnt+'_ikHandle'
        footIkHandle=cmds.ikHandle(sj=footIk,ee=toebaseIk,n=footIkHandle,sol='ikRPsolver')[0]
        cmds.setAttr(footIkHandle+'.v',0)
        toeIkHandle=toebaseJnt+'_ikHandle'
        toeIkHandle=cmds.ikHandle(sj=toebaseIk,ee=toeendIk,n=toeIkHandle,sol='ikRPsolver')[0]
        cmds.setAttr(toeIkHandle+'.v',0)

        cmds.parent(legIkHandle,toeIkRot)
        cmds.parent(footIkHandle,toeIkRot)
        cmds.parent(toeIkHandle,toebaseIkCtrl)
        cmds.parent(toeIkRotZero,toebaseIkCtrlZero,toeoutIkRot)
        cmds.parent(toeoutIkRotZero,toeinIkRot)
        cmds.parent(toeinIkRotZero,heelIkRot)
        cmds.parent(heelIkRotZero,toeendIkRot)
        cmds.parent(toeendIkRotZero,legIkCtrl)

        cmds.poleVectorConstraint(legIkPoleCtrl,legIkHandle)

        # footIkCtrl=footIk+'_ctrl'
        # footIkCtrlZero=ControlUtility.createControl(footIkCtrl,'Sphere',T=False)
        # ControlUtility.createInverseGrp(footIkCtrl)
        # cmds.delete(cmds.parentConstraint(toebaseIk,footIkCtrlZero))
        # cmds.parentConstraint(footIk,footIkCtrlZero,mo=1)
        # cmds.parent(footIkCtrlZero,legIkCtrlGrp)
        # vec1=GeneralUtility.getVector(toeendJnt,heelJnt)
        # vec2=GeneralUtility.getVector(toeendJnt,footJnt)
        # pVec=GeneralUtility.getPerpendicularVector(vec1,vec2)
        # ControlUtility.moveCV(footIkCtrl,pVec*0.5)

        # cmds.transformLimits(footIkCtrl,rz=[0,0],erz=[0,1])

        # footIk='L_foot_ik'
        # footIkCtrl='L_foot_ik_ctrl'
        cmds.addAttr(legIkCtrl,ln='footRoll',at='float',k=1,dv=0)
        cmds.addAttr(legIkCtrl,ln='rotateHeel',at='float',k=1,dv=0)
        cmds.addAttr(legIkCtrl,ln='pinHeel',at='float',k=1,dv=0)
        cmds.addAttr(legIkCtrl,ln='pinToe',at='float',k=1,dv=0)
        cmds.addAttr(legIkCtrl,ln='liftToe',at='float',k=1,dv=0)
        cmds.addAttr(legIkCtrl,ln='side',at='float',k=1,dv=0)

        cmds.addAttr(legIkCtrl,ln='footLift',at='float',k=1,dv=30)
        cmds.addAttr(legIkCtrl,ln='footStraight',at='float',k=1,dv=60)

        #footRoll


        rang1=cmds.createNode('setRange',n=footIk+'_footLift_rangNode')
        cmds.connectAttr(legIkCtrl+'.footRoll',rang1+'.vx')
        cmds.setAttr(rang1+'.nx',0)
        cmds.setAttr(rang1+'.mx',1)
        cmds.connectAttr(legIkCtrl+'.footLift',rang1+'.omx')

        rang2=cmds.createNode('setRange',n=footIk+'_footStraight_rangNode')
        cmds.connectAttr(legIkCtrl+'.footRoll',rang2+'.vx')
        cmds.setAttr(rang2+'.nx',0)
        cmds.setAttr(rang2+'.mx',1)
        cmds.connectAttr(legIkCtrl+'.footLift',rang2+'.onx')
        cmds.connectAttr(legIkCtrl+'.footStraight',rang2+'.omx')

        addNode=cmds.createNode('plusMinusAverage',n=footIk+'_addNode')
        cmds.connectAttr(rang1+'.ox',addNode+'.i1[0]')
        cmds.connectAttr(rang2+'.ox',addNode+'.i1[1]')
        cmds.setAttr(addNode+'.op',2)


        mulNode=cmds.createNode('multiplyDivide',n=footIk+'_mulNode')
        cmds.connectAttr(addNode+'.o1',mulNode+'.i1x')
        cmds.connectAttr(legIkCtrl+'.footRoll',mulNode+'.i2x')

        invRotMul=cmds.createNode('multiplyDivide',n=toeIkRot+'_rzInv_mulNode')
        cmds.setAttr(invRotMul+'.i2x',-1)
        cmds.connectAttr(mulNode+'.ox',invRotMul+'.i1x')
        cmds.connectAttr(invRotMul+'.ox',toeIkRot+'.rz')


        cmds.connectAttr(rang2+'.ox',mulNode+'.i1y')
        cmds.connectAttr(legIkCtrl+'.footRoll',mulNode+'.i2y')
        #### # lift toe
        toeendIkRotAdd=cmds.createNode('plusMinusAverage',n=toeendIkRot+'_addNode')
        cmds.connectAttr(legIkCtrl+'.liftToe',toeendIkRotAdd+'.i1[0]')
        cmds.connectAttr(mulNode+'.oy',toeendIkRotAdd+'.i1[1]')

        cmds.setAttr(invRotMul+'.i2y',-1)
        cmds.connectAttr(toeendIkRotAdd+'.o1',invRotMul+'.i1y')

        cmds.connectAttr(invRotMul+'.oy',toeendIkRot+'.rz')

        heelIkRotCond=cmds.createNode('condition',n=heelIkRot+'_rz_cond')
        cmds.connectAttr(legIkCtrl+'.footRoll',heelIkRotCond+'.ft')
        cmds.setAttr(heelIkRotCond+'.op',4)
        cmds.setAttr(heelIkRotCond+'.cfr',0)
        cmds.connectAttr(legIkCtrl+'.footRoll',heelIkRotCond+'.ctr')
        cmds.setAttr(invRotMul+'.i2z',-1)
        cmds.connectAttr(heelIkRotCond+'.ocr',invRotMul+'.i1z')
        cmds.connectAttr(invRotMul+'.oz',heelIkRot+'.rz')


        # rotate heel
        cmds.connectAttr(legIkCtrl+'.rotateHeel',toeIkRot+'.ry')

        # pin heel
        cmds.connectAttr(legIkCtrl+'.pinHeel',heelIkRot+'.ry')
        # pin toe
        cmds.connectAttr(legIkCtrl+'.pinToe',toeendIkRot+'.ry')
        # side 
        toeinIkRotCond=cmds.createNode('condition',n=toeinIkRot+'_rx_cond')
        cmds.connectAttr(legIkCtrl+'.side',toeinIkRotCond+'.ft')
        cmds.connectAttr(legIkCtrl+'.side',toeinIkRotCond+'.ctr')

        cmds.setAttr(toeinIkRotCond+'.op',2)
        cmds.setAttr(toeinIkRotCond+'.cfr',0)
        cmds.connectAttr(toeinIkRotCond+'.ocr',toeinIkRot+'.rx')

        toeoutIkRotCond=cmds.createNode('condition',n=toeoutIkRot+'_rx_cond')
        cmds.connectAttr(legIkCtrl+'.side',toeoutIkRotCond+'.ft')
        cmds.connectAttr(legIkCtrl+'.side',toeoutIkRotCond+'.ctr')

        cmds.setAttr(toeoutIkRotCond+'.op',4)
        cmds.setAttr(toeoutIkRotCond+'.cfr',0)
        cmds.connectAttr(toeoutIkRotCond+'.ocr',toeoutIkRot+'.rx')


        # footEndIkHandle=footEndIk+'_ikHandle'
        # footEndIkHandle=cmds.ikHandle(sj=footIk,ee=footEndIk,n=footEndIkHandle,sol='ikSCsolver')[0]
        # cmds.parent(footEndIkHandle,footIkCtrl)
        # cmds.setAttr(footEndIkHandle+'.v',0)

        legIkLocGrp=uplegJnt+'_ik_loc_grp'
        legIkLocGrp=cmds.duplicate(legIkRigGrp,po=1,rr=1,n=legIkLocGrp)[0]
        cmds.parent(legIkLocGrp,legIkRigGrp)
        cmds.setAttr(legIkLocGrp+'.v',0)
        cmds.parentConstraint(legIkRootCtrl,legIkLocGrp,mo=1)

        uplegIkLoc=uplegIk+'_loc'
        uplegIkLoc=cmds.spaceLocator(n=uplegIkLoc)[0]
        cmds.delete(cmds.pointConstraint(uplegIk,uplegIkLoc))
        cmds.parent(uplegIkLoc,legIkLocGrp)

        lowlegIkCtrlLoc=legIkPoleCtrl+'_loc'
        lowlegIkCtrlLoc=cmds.spaceLocator(n=lowlegIkCtrlLoc)[0]
        cmds.pointConstraint(legIkPoleCtrl,lowlegIkCtrlLoc)
        cmds.parent(lowlegIkCtrlLoc,legIkLocGrp)

        footIkCtrlLoc=legIkCtrl+'_loc'
        footIkCtrlLoc=cmds.spaceLocator(n=footIkCtrlLoc)[0]
        cmds.pointConstraint(legIkHandle,footIkCtrlLoc)
        cmds.parent(footIkCtrlLoc,legIkLocGrp)

        # root vis
        cmds.addAttr(legIkCtrl,ln='rootVis',at='long',k=1,dv=0,max=1,min=0)
        GeneralUtility.connectAllShapeAttr(legIkRootCtrl,legIkCtrl+'.rootVis','visibility')

        # ik stretch
        upLen=cmds.getAttr(lowlegJnt+'.tx')
        dnLen=cmds.getAttr(footJnt+'.tx')

        cmds.addAttr(legIkCtrl,ln='stretch',at='float',max=1,min=0,k=1)
        cmds.addAttr(legIkCtrl,ln='upLength',at='float',k=1)
        cmds.addAttr(legIkCtrl,ln='dnLength',at='float',k=1)

        upIkStretchAdd=uplegIk+'_stretch_addNode'
        upIkStretchAdd=cmds.createNode('plusMinusAverage',n=upIkStretchAdd)
        cmds.setAttr(upIkStretchAdd+'.i1[0]',abs(upLen))
        cmds.connectAttr(legIkCtrl+'.upLength',upIkStretchAdd+'.i1[1]')

        lowIkStretchAdd=lowlegIk+'_stretch_addNode'
        lowIkStretchAdd=cmds.createNode('plusMinusAverage',n=lowIkStretchAdd)
        cmds.setAttr(lowIkStretchAdd+'.i1[0]',abs(dnLen))
        cmds.connectAttr(legIkCtrl+'.dnLength',lowIkStretchAdd+'.i1[1]',f=1)

        footIkStretchAdd=footIk+'_stretch_addNode'
        footIkStretchAdd=cmds.createNode('plusMinusAverage',n=footIkStretchAdd)
        cmds.connectAttr(lowIkStretchAdd+'.o1',footIkStretchAdd+'.i1[0]')
        cmds.connectAttr(upIkStretchAdd+'.o1',footIkStretchAdd+'.i1[1]')

        footIkStretchLenMul=footIk+'_stretch_len_mulNode'
        footIkStretchLenMul=cmds.createNode('multiplyDivide',n=footIkStretchLenMul)
        cmds.setAttr(footIkStretchLenMul+'.i1x',1 if upLen>0 else -1)
        cmds.setAttr(footIkStretchLenMul+'.i1y',1 if upLen>0 else -1)
        cmds.connectAttr(upIkStretchAdd+'.o1',footIkStretchLenMul+'.i2x')
        cmds.connectAttr(lowIkStretchAdd+'.o1',footIkStretchLenMul+'.i2y')

        footIkStretchDis=footIk+'_stretch_disNode'
        footIkStretchDis=cmds.createNode('distanceBetween',n=footIkStretchDis)
        cmds.connectAttr(uplegIkLoc+'.t',footIkStretchDis+'.p1')
        cmds.connectAttr(footIkCtrlLoc+'.t',footIkStretchDis+'.p2')

        footIkStretchDiv=footIk+'_stretch_divNode'
        footIkStretchDiv=cmds.createNode('multiplyDivide',n=footIkStretchDiv)
        cmds.setAttr(footIkStretchDiv+'.op',2)
        cmds.connectAttr(footIkStretchDis+'.d',footIkStretchDiv+'.i1x')
        cmds.connectAttr(footIkStretchAdd+'.o1',footIkStretchDiv+'.i2x')

        footIkStretchCon=footIk+'_stretch_conNode'
        footIkStretchCon=cmds.createNode('condition',n=footIkStretchCon)
        cmds.connectAttr(footIkStretchDiv+'.ox',footIkStretchCon+'.ft')
        cmds.connectAttr(footIkStretchDiv+'.ox',footIkStretchCon+'.ctr')
        cmds.setAttr(footIkStretchCon+'.st',1)
        cmds.setAttr(footIkStretchCon+'.op',2)
        cmds.setAttr(footIkStretchCon+'.cfr',1)

        footIkStretchBlend=footIk+'_stretch_blendNode'
        footIkStretchBlend=cmds.createNode('blendTwoAttr',n=footIkStretchBlend)

        cmds.setAttr(footIkStretchBlend+'.i[0]',1)
        cmds.connectAttr(footIkStretchCon+'.ocr',footIkStretchBlend+'.i[1]')
        cmds.connectAttr(legIkCtrl+'.stretch',footIkStretchBlend+'.ab')

        footIkStretchMul=footIk+'_mulNode'
        footIkStretchMul=cmds.createNode('multiplyDivide',n=footIkStretchMul)
        cmds.connectAttr(footIkStretchBlend+'.o',footIkStretchMul+'.i1x')
        cmds.connectAttr(footIkStretchBlend+'.o',footIkStretchMul+'.i1y')
        cmds.connectAttr(footIkStretchLenMul+'.ox',footIkStretchMul+'.i2x')
        cmds.connectAttr(footIkStretchLenMul+'.oy',footIkStretchMul+'.i2y')

        # cmds.connectAttr(footIkMul+'.ox',lowlegIk+'.tx')
        # cmds.connectAttr(footIkMul+'.oy',footIk+'.tx')
        # pole help line
        self.adddHelpLine(legIkPoleCtrl,lowlegIk,legIkCtrlGrp)
        # ik lock
        cmds.addAttr(legIkPoleCtrl,ln='lock',at='float',max=1,min=0,k=1)
        uplegIkDis=uplegIk+'_disNode'
        uplegIkDis=cmds.createNode('distanceBetween',n=uplegIkDis)
        cmds.connectAttr(uplegIkLoc+'.t',uplegIkDis+'.p1')
        cmds.connectAttr(lowlegIkCtrlLoc+'.t',uplegIkDis+'.p2')

        lowlegIkDis=lowlegIk+'_disNode'
        lowlegIkDis=cmds.createNode('distanceBetween',n=lowlegIkDis)
        cmds.connectAttr(lowlegIkCtrlLoc+'.t',lowlegIkDis+'.p1')
        cmds.connectAttr(footIkCtrlLoc+'.t',lowlegIkDis+'.p2')

        uplegIkLockDiv=uplegIk+'_lock_divNode'
        uplegIkLockDiv=cmds.createNode('multiplyDivide',n=uplegIkLockDiv)
        cmds.connectAttr(uplegIkDis+'.d',uplegIkLockDiv+'.i1x')
        cmds.setAttr(uplegIkLockDiv+'.i2x',abs(upLen))
        cmds.connectAttr(lowlegIkDis+'.d',uplegIkLockDiv+'.i1y')
        cmds.setAttr(uplegIkLockDiv+'.i2y',abs(dnLen))
        cmds.setAttr(uplegIkLockDiv+'.op',2)

        uplegIkLockMul=uplegIk+'_lock_mulNode'
        uplegIkLockMul=cmds.createNode('multiplyDivide',n=uplegIkLockMul)
        cmds.connectAttr(uplegIkLockDiv+'.ox',uplegIkLockMul+'.i1x')
        cmds.setAttr(uplegIkLockMul+'.i2x',upLen)
        cmds.connectAttr(uplegIkLockDiv+'.oy',uplegIkLockMul+'.i1y')
        cmds.setAttr(uplegIkLockMul+'.i2y',dnLen)



        # blend ik stretch and lock
        uplegIkLockBlend=uplegIk+'_stretch_lock_blendNode'
        uplegIkLockBlend=cmds.createNode('blendColors',n=uplegIkLockBlend)
        cmds.connectAttr(uplegIkLockMul+'.ox',uplegIkLockBlend+'.c1r',f=1)
        cmds.connectAttr(uplegIkLockMul+'.oy',uplegIkLockBlend+'.c1g',f=1)
        cmds.connectAttr(footIkStretchMul+'.ox',uplegIkLockBlend+'.c2r',f=1)
        cmds.connectAttr(footIkStretchMul+'.oy',uplegIkLockBlend+'.c2g',f=1)
        cmds.connectAttr(legIkPoleCtrl+'.lock',uplegIkLockBlend+'.b')


        cmds.connectAttr(uplegIkLockBlend+'.opr',lowlegIk+'.tx')
        cmds.connectAttr(uplegIkLockBlend+'.opg',footIk+'.tx')

        # fk rig
        legFkRigGrp=uplegJnt+'_fk_rig_grp'
        legFkRigGrp=cmds.group(em=1,n=legFkRigGrp)
        cmds.delete(cmds.parentConstraint(uplegJnt,legFkRigGrp))
        cmds.parent(legFkRigGrp,legRigGrp)

        legFkJntGrp=uplegJnt+'_fk_jnt_grp'
        legFkJntGrp=cmds.duplicate(legFkRigGrp,po=1,rr=1,n=legFkJntGrp)[0]
        cmds.parent(legFkJntGrp,legFkRigGrp)
        cmds.setAttr(legFkJntGrp+'.visibility',0)

        uplegFk=cmds.duplicate(uplegJnt,po=1,rr=1,n=uplegJnt+'_fk')[0]
        cmds.parent(uplegFk,legFkJntGrp)

        lowlegFk=cmds.duplicate(lowlegJnt,po=1,rr=1,n=lowlegJnt+'_fk')[0]
        cmds.parent(lowlegFk,uplegFk)

        footFk=cmds.duplicate(footJnt,po=1,rr=1,n=footJnt+'_fk')[0]
        cmds.parent(footFk,lowlegFk)

        toebaseFk=cmds.duplicate(toebaseJnt,po=1,rr=1,n=toebaseJnt+'_fk')[0]
        cmds.parent(toebaseFk,footFk)


        legFkCtrlGrp=uplegJnt+'_fk_Ctrl_grp'
        legFkCtrlGrp=cmds.duplicate(legFkRigGrp,po=1,rr=1,n=legFkCtrlGrp)[0]
        cmds.parent(legFkCtrlGrp,legFkRigGrp)


        uplegFkCtrl=uplegFk+'_ctrl'
        uplegFkCtrlZero=ControlUtility.createControl(uplegFkCtrl,'Circle',T=False)
        uplegFkRootCtrl=uplegFk+'_root_ctrl'
        uplegFkRootCtrl=cmds.duplicate(uplegFkCtrl,n=uplegFkRootCtrl,rr=1)[0]
        cmds.parent(uplegFkCtrl,uplegFkRootCtrl)
        cmds.addAttr(uplegFkCtrl,ln='rootVis',at='long',k=1,max=0,min=1,dv=0)
        ControlUtility.scaleCV(uplegFkRootCtrl,5)
        GeneralUtility.connectAllShapeAttr(uplegFkRootCtrl,uplegFkCtrl+'.rootVis','visibility')

        cmds.delete(cmds.parentConstraint(uplegFk,uplegFkCtrlZero))
        cmds.parentConstraint(uplegFkCtrl,uplegFk,mo=1)
        cmds.parent(uplegFkCtrlZero,legFkCtrlGrp)
        ControlUtility.scaleCV(uplegFkCtrl,4)


        lowlegFkCtrl=lowlegFk+'_ctrl'
        lowlegFkCtrlZero=ControlUtility.createControl(lowlegFkCtrl,'Circle',T=False)
        # ControlUtility.lockRotate(lowlegFkCtrl,z=0)
        cmds.delete(cmds.parentConstraint(lowlegFk,lowlegFkCtrlZero))
        cmds.parentConstraint(lowlegFkCtrl,lowlegFk,mo=1)
        cmds.parent(lowlegFkCtrlZero,uplegFkCtrl)
        ControlUtility.scaleCV(lowlegFkCtrl,4)


        footFkCtrl=footFk+'_ctrl'
        footFkCtrlZero=ControlUtility.createControl(footFkCtrl,'Circle',T=False)
        cmds.delete(cmds.parentConstraint(footFk,footFkCtrlZero))
        cmds.parentConstraint(footFkCtrl,footFk,mo=1)
        cmds.parent(footFkCtrlZero,lowlegFkCtrl)
        ControlUtility.scaleCV(footFkCtrl,4)

        toebaseFkCtrl=toebaseFk+'_ctrl'
        toebaseFkCtrlZero=ControlUtility.createControl(toebaseFkCtrl,'Circle',T=False)
        cmds.delete(cmds.parentConstraint(toebaseFk,toebaseFkCtrlZero))
        cmds.parentConstraint(toebaseFkCtrl,toebaseFk,mo=1)
        cmds.parent(toebaseFkCtrlZero,footFkCtrl)
        ControlUtility.scaleCV(toebaseFkCtrl,4)


        # fk stretch
        cmds.addAttr(uplegFkCtrl,ln='upLength',at='float',k=1)

        uplegFkAdd=uplegFk+'_stretch_addNode'
        uplegFkAdd=cmds.createNode('plusMinusAverage',n=uplegFkAdd)
        cmds.connectAttr(uplegFkCtrl+'.upLength',uplegFkAdd+'.i1[0]')
        cmds.setAttr(uplegFkAdd+'.i1[1]',cmds.getAttr(lowlegFkCtrlZero+'.tx'))
        cmds.connectAttr(uplegFkAdd+'.o1',lowlegFkCtrlZero+'.tx')

        cmds.addAttr(lowlegFkCtrl,ln='dnLength',at='float',k=1)
        lowlegFkAdd=lowlegFk+'_stretch_addNode'
        lowlegFkAdd=cmds.createNode('plusMinusAverage',n=lowlegFkAdd)
        cmds.connectAttr(lowlegFkCtrl+'.dnLength',lowlegFkAdd+'.i1[0]')
        cmds.setAttr(lowlegFkAdd+'.i1[1]',cmds.getAttr(footFkCtrlZero+'.tx'))
        cmds.connectAttr(lowlegFkAdd+'.o1',footFkCtrlZero+'.tx')



        # dri jnt
        legDrJntGrp=uplegJnt+'_dr_jnt_grp'
        legDrJntGrp=cmds.group(em=1,n=legDrJntGrp)
        cmds.delete(cmds.parentConstraint(uplegJnt,legDrJntGrp))
        cmds.parent(legDrJntGrp,legRigGrp)
        cmds.setAttr(legDrJntGrp+'.visibility',0)

        uplegDr=cmds.duplicate(uplegJnt,po=1,rr=1,n=uplegJnt+'_dr')[0]
        cmds.parent(uplegDr,legDrJntGrp)

        lowlegDr=cmds.duplicate(lowlegJnt,po=1,rr=1,n=lowlegJnt+'_dr')[0]
        cmds.parent(lowlegDr,uplegDr)

        footDr=cmds.duplicate(footJnt,po=1,rr=1,n=footJnt+'_dr')[0]
        cmds.parent(footDr,lowlegDr)

        toebaseDr=cmds.duplicate(toebaseJnt,po=1,rr=1,n=toebaseJnt+'_dr')[0]
        cmds.parent(toebaseDr,footDr)

        toeendDr=cmds.duplicate(toeendJnt,po=1,rr=1,n=toeendJnt+'_dr')[0]
        cmds.parent(toeendDr,toebaseDr)

        legSwitchCtrl=uplegJnt+'_switch_ctrl'
        legSwitchCtrlZero=ControlUtility.createControl(legSwitchCtrl,'Cross',T=False,R=False)
        cmds.parentConstraint(footDr,legSwitchCtrlZero)
        cmds.parent(legSwitchCtrlZero,legRigGrp)

        vec=GeneralUtility.getVector(toeinJnt,toeoutJnt)
        ControlUtility.moveCV(legSwitchCtrl,vec)



        # ik fk switch
        cmds.addAttr(legSwitchCtrl,ln='ikfk',at='long',k=1,dv=0,max=1,min=0)

        legSwitchRev=legSwitchCtrl+'_ikfk_revNode'
        legSwitchRev=cmds.createNode('reverse',n=legSwitchRev)
        cmds.connectAttr(legSwitchCtrl+'.ikfk',legSwitchRev+'.ix')



        ikfkAttr=legSwitchCtrl+'.ikfk'
        ikfkInvAttr=legSwitchRev+'.ox'
        uplegCon=cmds.parentConstraint(uplegIk,uplegFk,uplegDr)[0]
        cmds.connectAttr(ikfkInvAttr,uplegCon+'.w0')
        cmds.connectAttr(ikfkAttr,uplegCon+'.w1')

        lowlegCon=cmds.parentConstraint(lowlegIk,lowlegFk,lowlegDr)[0]
        cmds.connectAttr(ikfkInvAttr,lowlegCon+'.w0')
        cmds.connectAttr(ikfkAttr,lowlegCon+'.w1')

        footCon=cmds.parentConstraint(footIk,footFk,footDr)[0]
        cmds.connectAttr(ikfkInvAttr,footCon+'.w0')
        cmds.connectAttr(ikfkAttr,footCon+'.w1')

        toebaseCon=cmds.parentConstraint(toebaseIk,toebaseFk,toebaseDr)[0]
        cmds.connectAttr(ikfkInvAttr,toebaseCon+'.w0')
        cmds.connectAttr(ikfkAttr,toebaseCon+'.w1')

        cmds.connectAttr(ikfkInvAttr,legIkRigGrp+'.v')
        cmds.connectAttr(ikfkAttr,legFkRigGrp+'.v')

        # twist second
        cmds.addAttr(legSwitchCtrl,ln='secVis',at='long',k=1,max=0,min=1,dv=0)
        switchAttr=legSwitchCtrl+'.secVis'
        eZero=self.addSceondRig(uplegJnt,uplegDr,lowlegDr,legRigGrp,switchAttr,typ='up')
        sCtrl=self.addSceondRig(lowlegJnt,lowlegDr,footDr,legRigGrp,switchAttr,typ='low')
        cmds.delete(cmds.pointConstraint(eZero,q=1,n=1))
        cmds.pointConstraint(sCtrl,eZero)
        cmds.setAttr(eZero+'.v',0)


        # dr jnt grp follow
        legDrJntFollowChest=legDrJntGrp+'_follow_hip'
        self.addFollowToGrp(legDrJntFollowChest,legDrJntGrp,'Hip')
        cmds.parentConstraint(legDrJntFollowChest,legDrJntGrp)

        # leg ik follow
        legIkFollowHip=legIkRootCtrlZero+'_follow_hip'
        self.addFollowToGrp(legIkFollowHip,legIkRootCtrlZero,'Hip')
        cmds.parentConstraint(legIkFollowHip,legIkRootCtrlZero)


        # ik pole follow
        cmds.addAttr(legIkPoleCtrl,ln='follow',at='enum',en='foot:hip:world',k=1)
        legPoleFollowHip=legIkPoleCtrlZero+'_follow_hip'
        self.addFollowToGrp(legPoleFollowHip,uplegIk,'Hip')
        tx=cmds.getAttr(lowlegJnt+'.tx')
        direction=tx/abs(tx)
        cmds.aimConstraint(legIkCtrl,legPoleFollowHip,mo=1,aim=(direction,0,0),u=(0,0,1),wut="objectrotation",wu=(0,0,1),wuo=legIkCtrl)
        legIkPoleFollowRot=cmds.duplicate(legPoleFollowHip,n=uplegJnt+'_pole_follow_rot',po=1,rr=1)[0]
        cmds.parent(legIkPoleFollowRot,legPoleFollowHip)
        legIkPoleFollowCon=cmds.duplicate(legPoleFollowHip,n=uplegJnt+'_pole_follow_con',po=1,rr=1)[0]
        cmds.delete(cmds.parentConstraint(legIkPoleCtrl,legIkPoleFollowCon))
        cmds.parent(legIkPoleFollowCon,legIkPoleFollowRot)

        driverAttr=footIkStretchDis+'.d'
        drivenAttr=legIkPoleFollowRot+'.rz'
        driverValue=cmds.getAttr(driverAttr)
        cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=0,dv=driverValue,itt='linear',ott='linear')
        cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=45,dv=0,itt='linear',ott='linear')

        legPoleFollowHipNorol=legIkPoleCtrlZero+'_follow_hip_norol'
        self.addFollowToGrp(legPoleFollowHipNorol,legIkPoleCtrlZero,'Hip')

        legPoleFollowWorld=legIkPoleCtrlZero+'_follow_world'
        self.addFollowToGrp(legPoleFollowWorld,legIkPoleCtrlZero,'World')

        followList=[legIkPoleFollowCon,legPoleFollowHipNorol,legPoleFollowWorld]
        followAttr=legIkPoleCtrl+'.follow'
        self.addConstraintByFollowList(followList,legIkPoleCtrlZero,followAttr)


        # leg ik follow
        cmds.addAttr(legIkCtrl,ln='follow',at='enum',en='world:body:hip',k=1)

        legIkFollowWorld=legIkCtrlZero+'_follow_world'
        self.addFollowToGrp(legIkFollowWorld,legIkCtrlZero,'World')

        legIkFollowBody=legIkCtrlZero+'_follow_body'
        self.addFollowToGrp(legIkFollowBody,legIkCtrlZero,'Body')

        legIkFollowHip=legIkCtrlZero+'_follow_hip'
        self.addFollowToGrp(legIkFollowHip,legIkCtrlZero,'Hip')


        followList=[legIkFollowWorld,legIkFollowBody,legIkFollowHip]
        followAttr=legIkCtrl+'.follow'
        self.addConstraintByFollowList(followList,legIkCtrlZero,followAttr)

        # leg fk follow
        cmds.addAttr(uplegFkCtrl,ln='follow',at='long',k=1,max=0,min=1,dv=1)
        followInv=cmds.createNode('reverse',n=uplegFkCtrl+'_follow_invNode')
        cmds.connectAttr(uplegFkCtrl+'.follow',followInv+'.ix')

        legFkFollowHip=legFkCtrlGrp+'_follow_hip'
        self.addFollowToGrp(legFkFollowHip,legFkCtrlGrp,'Hip')

        legFkFollowWorld=legFkCtrlGrp+'_follow_world'
        self.addFollowToGrp(legFkFollowWorld,legFkCtrlGrp,'World')


        cmds.pointConstraint(legFkFollowHip,legFkCtrlGrp)
        con=cmds.orientConstraint(legFkFollowHip,legFkFollowWorld,legFkCtrlGrp)[0]
        cmds.connectAttr(uplegFkCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')

        # leg dr follow
        
        legDrJntGrpFollowHip=legDrJntGrp+'_follow_hip'
        self.addFollowToGrp(legDrJntGrpFollowHip,legDrJntGrp,'Hip')
        cmds.parentConstraint(legDrJntGrpFollowHip,legDrJntGrp)


        # ikfk Match
        ctrlList=[uplegFkCtrl,lowlegFkCtrl,footFkCtrl,toebaseFkCtrl,legIkPoleCtrl,legIkCtrl,toebaseIkCtrl]
        drList=[uplegDr,lowlegDr,footDr,toebaseDr,[uplegDr,lowlegDr],footDr,toebaseDr]
        for ctrl,drJnt in zip(ctrlList,drList):
            self.addIkfkMathGroup(ctrl,drJnt)

    def splieIkRig(self,endJnt,jntList,rigGrp,baseName='',curRad=5,ctrlType='mocap',endParent=True,attrCtrl=None):

        # endJnt,jntList,rigGrp,baseName,curRad,ctrlType,endParent,attrCtrl=('head', ['neck_1', 'neck_2', 'neck_3'], u'neck_rig_grp', 'neck', 5, 'mocap', False, None)

        ikJntGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_ik_jnt_grp')[0]
        cmds.parent(ikJntGrp,rigGrp)
        cmds.setAttr(ikJntGrp+'.visibility',0)
        # ik joint
        ikJntList=[]
        for jnt in jntList:
            ikJnt=cmds.duplicate(jnt,po=1,rr=1,n=jnt+'_ik')[0]
            cmds.parent(ikJnt,ikJntGrp)
            ikJntList.append(ikJnt)

        for idx in range(1,len(ikJntList)):
            cmds.parent(ikJntList[idx],ikJntList[idx-1])

        # ik end
        ikJnt=cmds.duplicate(endJnt,po=1,rr=1,n=baseName+'_end_ik')[0]
        cmds.parent(ikJnt,ikJntList[-1])
        ikJntList.append(ikJnt)
        # ik curve 

        cvList=[]
        for ikJnt in ikJntList:
            pos=cmds.xform(ikJnt,q=1,ws=1,t=1)
            cvList.append(pos)

        splineCurve=baseName+'_ik_curve'
        splineCurve=cmds.curve(n=splineCurve,d=2,p=cvList)
        cmds.setAttr(splineCurve+'.it',0)
        splineCurveGrp=cmds.group(splineCurve,n=baseName+'_curve_grp')
        cmds.parent(splineCurveGrp,rigGrp)


        splineScaleCurve=baseName+'_globalscale_curve'
        splineScaleCurve=cmds.curve(n=splineScaleCurve,d=1,p=[(0,0,0),(1,0,0)])
        cmds.delete(cmds.parentConstraint(rigGrp,splineScaleCurve))
        cmds.parent(splineScaleCurve,splineCurveGrp)

        cmds.setAttr(splineCurveGrp+'.visibility',0)

        # ik control
        ikCtrlGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_ik_ctrl_grp')[0]
        cmds.parent(ikCtrlGrp,rigGrp)
        

        ikCtrlList=[]
        for idx,ikJnt in enumerate(ikJntList):
            ikCtrl=ikJnt+'_ctrl'
            ikCtrlZero=ControlUtility.createControl(ikCtrl,'Rect',Mirror=False,R=False)
            cmds.delete(cmds.parentConstraint(ikJnt,ikCtrlZero))
            ikCtrlLoc=cmds.spaceLocator(n=ikCtrl+'_loc')[0]
            cmds.setAttr(ikCtrlLoc+'.visibility',0)
            cmds.delete(cmds.parentConstraint(ikCtrl,ikCtrlLoc))
            cmds.parent(ikCtrlLoc,ikCtrl)
            cmds.connectAttr(ikCtrlLoc+'.worldPosition',splineCurve+'.cv[%s]'%idx)
            cmds.parent(ikCtrlZero,ikCtrlGrp)
            ikCtrlList.append([ikCtrl,ikCtrlZero])

        # fk control
        fkCtrlGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_fk_ctrl_grp')[0]
        cmds.parent(fkCtrlGrp,rigGrp)
        
        fkCtrlList=[]
        for fkJnt in jntList+[endJnt]:
            fkCtrl=fkJnt+'_ctrl'
            fkCtrlZero=ControlUtility.createControl(fkCtrl,'Circle',Mirror=False)
            ControlUtility.scaleCV(fkCtrl,curRad)
            cmds.delete(cmds.parentConstraint(fkJnt,fkCtrlZero))
            # cmds.rotate(0,180,-90,fkCtrlZero,r=1,os=1,fo=1)
            cmds.parent(fkCtrlZero,fkCtrlGrp)
            fkCtrlList.append([fkCtrl,fkCtrlZero])
        endNum=len(fkCtrlList)
        if(not endParent):
            endNum-=1
        for idx in range(1,endNum):
            cmds.parent(fkCtrlList[idx][1],fkCtrlList[idx-1][0])

        for fkCtrl,ikCtrl in zip(fkCtrlList,ikCtrlList):
            cmds.parentConstraint(fkCtrl[0],ikCtrl[1],mo=1)

        if(attrCtrl==None):
            attrCtrl=fkCtrlList[0][0]
        cmds.addAttr(attrCtrl,ln='ikVis',at='long',k=1,dv=0,max=1,min=0)
        cmds.addAttr(attrCtrl,ln='stretch',at='float',k=1,max=0,min=1)

        # spline ik
        ikHandle=baseName+'_ikHandle'
        ikHandle=cmds.ikHandle(sj=ikJntList[0],ee=ikJntList[-1],c=splineCurve,n=ikHandle,ccv=0,pcv=0,sol='ikSplineSolver')[0]

        cmds.setAttr(ikHandle+'.dTwistControlEnable',1)
        cmds.setAttr(ikHandle+'.dTwistControlEnable',1)
        cmds.setAttr(ikHandle+'.dWorldUpType',4)
        cmds.setAttr(ikHandle+'.dForwardAxis',0)
        cmds.setAttr(ikHandle+'.dWorldUpAxis',3)
        cmds.setAttr(ikHandle+'.dWorldUpVector',0,0,1,typ='float3')
        cmds.setAttr(ikHandle+'.dWorldUpVectorEnd',0,0,1,typ='float3')
        cmds.connectAttr(ikCtrlList[0][0]+'.worldMatrix',ikHandle+'.dWorldUpMatrix')
        cmds.connectAttr(ikCtrlList[-1][0]+'.worldMatrix',ikHandle+'.dWorldUpMatrixEnd')
        cmds.setAttr(ikHandle+'.v',0)

        ikHandleZero=cmds.group(ikHandle,n=ikHandle+'_zero')
        cmds.parent(ikHandleZero,rigGrp)

        # ik stretch
        splineCurveInfo=splineCurve+'_infoNode'
        splineCurveInfo=cmds.createNode('curveInfo',n=splineCurveInfo)
        cmds.connectAttr(splineCurve+'.worldSpace',splineCurveInfo+'.inputCurve')

        splineScaleInfo=splineScaleCurve+'_infoNode'
        splineScaleInfo=cmds.createNode('curveInfo',n=splineScaleInfo)
        cmds.connectAttr(splineScaleCurve+'.worldSpace',splineScaleInfo+'.inputCurve')

        splineCurveMul=splineCurve+'_mulNode'
        splineCurveMul=cmds.createNode('multiplyDivide',n=splineCurveMul)
        cmds.connectAttr(splineScaleInfo+'.al',splineCurveMul+'.i1x')
        oldLen=cmds.getAttr(splineCurveInfo+'.al')
        cmds.setAttr(splineCurveMul+'.i2x',oldLen)

        splineCurveDiv=splineCurve+'_divNode'
        splineCurveDiv=cmds.createNode('multiplyDivide',n=splineCurveDiv)
        cmds.setAttr(splineCurveDiv+'.op',2)
        cmds.connectAttr(splineCurveInfo+'.al',splineCurveDiv+'.i1x')
        cmds.connectAttr(splineCurveMul+'.ox',splineCurveDiv+'.i2x')

        splineStretchBlend=baseName+'_stretch_blendNode'
        splineStretchBlend=cmds.createNode('blendTwoAttr',n=splineStretchBlend)
        cmds.connectAttr(attrCtrl+'.stretch',splineStretchBlend+'.ab')
        cmds.setAttr(splineStretchBlend+'.i[0]',1)
        cmds.connectAttr(splineCurveDiv+'.ox',splineStretchBlend+'.i[1]')

        for ikJnt in ikJntList[1:]:
            ikJntMul=ikJnt+'_mulNode'
            ikJntMul=cmds.createNode('multiplyDivide',n=ikJntMul)
            oldTx=cmds.getAttr(ikJnt+'.tx')
            cmds.setAttr(ikJntMul+'.i1x',oldTx)
            cmds.connectAttr(splineStretchBlend+'.o',ikJntMul+'.i2x')
            cmds.connectAttr(ikJntMul+'.ox',ikJnt+'.tx')


        # vis
        cmds.connectAttr(attrCtrl+'.ikVis',ikCtrlGrp+'.v')
        return fkCtrlList,ikJntList,fkCtrlGrp

    def secIkRig(self,endJnt,jntList,rigGrp,baseName='',curRad=5,ctrlType='mocap',endParent=True,attrCtrl=None):


        ikJntGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_ik_jnt_grp')[0]
        cmds.parent(ikJntGrp,rigGrp)
        cmds.setAttr(ikJntGrp+'.visibility',0)
        # ik joint
        ikJntList=[]
        for jnt in jntList:
            ikJnt=cmds.duplicate(jnt,po=1,rr=1,n=jnt+'_ik')[0]
            cmds.parent(ikJnt,ikJntGrp)
            ikJntList.append(ikJnt)

        for idx in range(1,len(ikJntList)):
            cmds.parent(ikJntList[idx],ikJntList[idx-1])

        # ik end
        ikJnt=cmds.duplicate(endJnt,po=1,rr=1,n=endJnt+'_ik')[0]
        cmds.parent(ikJnt,ikJntList[-1])
        ikJntList.append(ikJnt)

        # ik control
        ikCtrlGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_ik_ctrl_grp')[0]
        cmds.parent(ikCtrlGrp,rigGrp)
        cmds.connectAttr(attrCtrl+'.ikVis',ikCtrlGrp+'.v')

        ikCtrlList=[]
        for idx,ikJnt in enumerate(ikJntList):
            ikCtrl=ikJnt+'_ctrl'
            ikCtrlZero=ControlUtility.createControl(ikCtrl,'Rect',Mirror=False)
            cmds.delete(cmds.parentConstraint(ikJnt,ikCtrlZero))
            cmds.parent(ikCtrlZero,ikCtrlGrp)
            cmds.parentConstraint(ikCtrl,ikJnt)
            ikCtrlList.append([ikCtrl,ikCtrlZero])

        # fk control
        fkCtrlGrp=cmds.duplicate(rigGrp,po=1,rr=1,n=baseName+'_fk_ctrl_grp')[0]
        cmds.parent(fkCtrlGrp,rigGrp)
        
        fkCtrlList=[]
        for fkJnt in jntList+[endJnt]:
            fkCtrl=fkJnt+'_ctrl'
            fkCtrlZero=ControlUtility.createControl(fkCtrl,'Circle',Mirror=False)
            ControlUtility.scaleCV(fkCtrl,curRad)
            cmds.delete(cmds.parentConstraint(fkJnt,fkCtrlZero))
            # cmds.rotate(0,180,-90,fkCtrlZero,r=1,os=1,fo=1)
            cmds.parent(fkCtrlZero,fkCtrlGrp)
            fkCtrlList.append([fkCtrl,fkCtrlZero])
        endNum=len(fkCtrlList)
        if(not endParent):
            endNum-=1
        for idx in range(1,endNum):
            cmds.parent(fkCtrlList[idx][1],fkCtrlList[idx-1][0])

        for fkCtrl,ikCtrl in zip(fkCtrlList,ikCtrlList):
            cmds.parentConstraint(fkCtrl[0],ikCtrl[1],mo=1)

        if(attrCtrl==None):
            attrCtrl=fkCtrlList[0][0]
        

        return fkCtrlList,ikJntList,fkCtrlGrp


    def spineRig(self,spineJntList,chestJnt,chestMidJnt,hipJnt):
        cmds.delete(cmds.parentConstraint(spineJntList[0],hipJnt))

        bodyCtrl='body_ctrl'
        bodyCtrlZero=ControlUtility.createControl(bodyCtrl,'Root',Mirror=False)
        cmds.delete(cmds.parentConstraint(spineJntList[0],bodyCtrlZero))
        cmds.rotate(0,180,-90,bodyCtrlZero,r=1,os=1,fo=1)
        ControlUtility.scaleCV(bodyCtrl,15)
        cmds.addAttr(bodyCtrl,ln='ikVis',at='long',k=1,dv=0,max=1,min=0)
        cmds.addAttr(bodyCtrl,ln='fkVis',at='long',k=1,dv=0,max=1,min=0)



        allCtrl='all_ctrl'
        cmds.parent(bodyCtrlZero,allCtrl)


        spineRigGrp=cmds.group(em=1,n='spine_rig_grp')
        cmds.delete(cmds.parentConstraint(spineJntList[0],spineRigGrp))
        cmds.parent(spineRigGrp,bodyCtrl)

        # spline ik rig

        fkCtrlList,ikJntList,fkCtrlGrp=self.secIkRig(chestJnt,spineJntList,spineRigGrp,baseName='spine',curRad=12,ctrlType='mocap',endParent=True,attrCtrl=bodyCtrl)
        
        GeneralUtility.connectAllShapeAttr(fkCtrlList[0][0],bodyCtrl+'.fkVis','visibility')
        for i in range(2,len(fkCtrlList),2):
            GeneralUtility.connectAllShapeAttr(fkCtrlList[i][0],bodyCtrl+'.fkVis','visibility')

        # driver joint
        spineDrJntGrp=cmds.duplicate(spineRigGrp,po=1,rr=1,n='spine_dr_jnt_grp')[0]
        cmds.parent(spineDrJntGrp,spineRigGrp)
        cmds.setAttr(spineDrJntGrp+'.visibility',0)
        spineDrList=[]
        for spineJnt in spineJntList:
            spineDr=cmds.duplicate(spineJnt,po=1,rr=1,n=spineJnt+'_dr')[0]
            cmds.parent(spineDr,spineDrJntGrp)
            spineDrList.append(spineDr)

        for idx in range(1,len(spineDrList)):
            cmds.parent(spineDrList[idx],spineDrList[idx-1])

        for spineDr,spineIkJnt in zip(spineDrList,ikJntList[:-1]):
            cmds.parentConstraint(spineIkJnt,spineDr)

        chestDr=cmds.duplicate(chestJnt,po=1,rr=1,n=chestJnt+'_dr')[0]
        cmds.parent(chestDr,spineDrList[-1])
        cmds.parentConstraint(ikJntList[-1],chestDr)
    

        chestMidDr=cmds.duplicate(chestMidJnt,po=1,rr=1,n=chestMidJnt+'_dr')[0]
        cmds.parent(chestMidDr,chestDr)
        chestMidCtrl=chestMidJnt+'_ctrl'
        chestMidCtrlZero=ControlUtility.createControl(chestMidCtrl,'Circle',Mirror=False)
        cmds.delete(cmds.parentConstraint(chestMidJnt,chestMidCtrlZero))
        cmds.parentConstraint(chestMidCtrl,chestMidDr)
        ControlUtility.scaleCV(chestMidCtrl,12)
        cmds.parent(chestMidCtrlZero,fkCtrlList[-1][0])

        GeneralUtility.connectAllShapeAttr(chestMidCtrl,bodyCtrl+'.fkVis','visibility')



        hipDr=cmds.duplicate(hipJnt,po=1,rr=1,n=hipJnt+'_dr')[0]
        cmds.parent(hipDr,spineDrJntGrp)
        hipCtrl=hipJnt+'_ctrl'
        hipCtrlZero=ControlUtility.createControl(hipCtrl,'Circle',Mirror=False)
        cmds.delete(cmds.parentConstraint(spineJntList[0],hipCtrlZero))
        # cmds.rotate(0,180,-90,hipCtrlZero,r=1,os=1,fo=1)

        cmds.parentConstraint(hipCtrl,hipDr,mo=1)

        vec=GeneralUtility.getVector(spineJntList[0],hipJnt)

        ControlUtility.moveCV(hipCtrl,vec)
        ControlUtility.scaleCV(hipCtrl,12)
        cmds.parent(hipCtrlZero,bodyCtrl)


        # follow grp
        bodyFollowGrp='body_follow_grp'
        self.addFollowGrp(bodyFollowGrp,bodyCtrl)

        chestFollowGrp='chest_follow_grp'
        self.addFollowGrp(chestFollowGrp,chestMidCtrl)

        hipFollowGrp='hip_follow_grp'
        self.addFollowGrp(hipFollowGrp,hipCtrl)

        # 
        cmds.addAttr(bodyCtrl,ln='TCHour',at='long',k=1,dv=0)
        cmds.addAttr(bodyCtrl,ln='TCMinute',at='long',k=1,dv=0)
        cmds.addAttr(bodyCtrl,ln='TCSecond',at='long',k=1,dv=0)
        cmds.addAttr(bodyCtrl,ln='TCFrame',at='long',k=1,dv=0)

    def neckRig(self,neckJntList,headJnt,headEndJnt):
        neckRigGrp=cmds.group(em=1,n='neck_rig_grp')
        cmds.delete(cmds.parentConstraint(neckJntList[0],neckRigGrp))
        allCtrl='all_ctrl'
        cmds.parent(neckRigGrp,allCtrl)


        # spline ik rig
        fkCtrlList,ikJntList,fkCtrlGrp=self.splieIkRig(headJnt,neckJntList,neckRigGrp,baseName='neck',curRad=5,ctrlType='mocap',endParent=False,attrCtrl=None)


        neckDrJntGrp=cmds.duplicate(neckRigGrp,po=1,rr=1,n='neck_dr_jnt_grp')[0]
        cmds.parent(neckDrJntGrp,neckRigGrp)
        cmds.setAttr(neckDrJntGrp+'.visibility',0)
        neckDrList=[]
        for neckJnt in neckJntList:
            neckDr=cmds.duplicate(neckJnt,po=1,rr=1,n=neckJnt+'_dr')[0]
            cmds.parent(neckDr,neckDrJntGrp)
            neckDrList.append(neckDr)

        for idx in range(1,len(neckDrList)):
            cmds.parent(neckDrList[idx],neckDrList[idx-1])

        for ikJnt,neckDr in zip(ikJntList[:-1],neckDrList):
            cmds.parentConstraint(ikJnt,neckDr)


        # head rig

        headDrJntGrp=cmds.group(em=1,n='head_dr_jnt_grp')
        cmds.delete(cmds.parentConstraint(headJnt,headDrJntGrp))
        cmds.parent(headDrJntGrp,neckRigGrp)
        cmds.setAttr(headDrJntGrp+'.visibility',0)

        headDr=cmds.duplicate(headJnt,po=1,rr=1,n=headJnt+'_dr')[0]
        cmds.parent(headDr,headDrJntGrp)

        headEndDr=cmds.duplicate(headEndJnt,po=1,rr=1,n=headEndJnt+'_dr')[0]
        cmds.parent(headEndDr,headDr)



        headFkCtrl,headFkCtrlZero=fkCtrlList[-1]
        cmds.parentConstraint(headFkCtrl,headDr)



        headAimRotGrp=cmds.group(em=1,n='head_aim_rot_grp')
        headFkCtrlGrp=cmds.group(headAimRotGrp,n='head_fk_ctrl_grp')
        cmds.delete(cmds.parentConstraint(headJnt,headFkCtrlGrp))
        cmds.parent(headFkCtrlGrp,neckRigGrp)
        cmds.parent(headFkCtrlZero,headAimRotGrp)

        headAimUpLoc=cmds.duplicate(headAimRotGrp,po=1,rr=1,n='head_aim_up_loc')[0]
        cmds.setAttr(headAimUpLoc+'.tx',1)

        dis=GeneralUtility.getDistance(headJnt,headEndJnt)


        headAimCtrl='head_aim_ctrl'
        headAimCtrlZero=ControlUtility.createControl(headAimCtrl,'Sphere',Mirror=False,R=False)
        cmds.delete(cmds.parentConstraint(headAimRotGrp,headAimCtrlZero))
        cmds.parent(headAimCtrlZero,headAimRotGrp)
        cmds.setAttr(headAimCtrlZero+'.tz',-dis*3)
        cmds.parent(headAimCtrlZero,neckRigGrp)
        cmds.aimConstraint(headAimCtrl,headAimRotGrp,mo=1,aim=(0,0,-1),u=(1,0,0),wut="objectrotation",wu=(1,0,0),wuo=headAimUpLoc)


        cmds.addAttr(headFkCtrl,ln='aimVis',at='float',k=1,max=0,min=1,dv=0)
        cmds.connectAttr(headFkCtrl+'.aimVis',headAimCtrlZero+'.v')

        # pole help line
        self.adddHelpLine(headAimCtrl,headFkCtrl,headAimCtrlZero)

        # follow grp
        neckFollowGrp='neck_follow_grp'
        self.addFollowGrp(neckFollowGrp,fkCtrlList[-2][0])

        headFollowGrp='head_follow_grp'
        self.addFollowGrp(headFollowGrp,headFkCtrl)

        # neck follow
        neckRootCtrl=fkCtrlList[0][0]
        cmds.addAttr(neckRootCtrl,ln='follow',at='float',k=1,max=0,min=1,dv=1)
        followInv=cmds.createNode('reverse',n=neckRootCtrl+'_follow_invNode')
        cmds.connectAttr(neckRootCtrl+'.follow',followInv+'.ix')

        neckFollwChest=fkCtrlGrp+'_follow_chest'
        self.addFollowToGrp(neckFollwChest,fkCtrlGrp,'Chest')

        neckFollowWorld=fkCtrlGrp+'_follow_world'
        self.addFollowToGrp(neckFollowWorld,fkCtrlGrp,'World')

        cmds.pointConstraint(neckFollwChest,fkCtrlGrp)
        con=cmds.orientConstraint(neckFollwChest,neckFollowWorld,fkCtrlGrp)[0]
        cmds.connectAttr(neckRootCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')




        # head follow

        cmds.addAttr(headFkCtrl,ln='follow',at='float',k=1,max=0,min=1,dv=1)
        followInv=cmds.createNode('reverse',n=headFkCtrl+'_follow_invNode')
        cmds.connectAttr(headFkCtrl+'.follow',followInv+'.ix')

        headFollwChest=headFkCtrlGrp+'_follow_neck'
        self.addFollowToGrp(headFollwChest,headFkCtrlGrp,'Neck')

        headFollowWorld=headFkCtrlGrp+'_follow_world'
        self.addFollowToGrp(headFollowWorld,headFkCtrlGrp,'World')

        cmds.pointConstraint(headFollwChest,headFkCtrlGrp)
        con=cmds.orientConstraint(headFollwChest,headFollowWorld,headFkCtrlGrp)[0]
        cmds.connectAttr(headFkCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')


        headAimUpFollwChest=headAimUpLoc+'_follow_neck'
        self.addFollowToGrp(headAimUpFollwChest,headAimUpLoc,'Neck')

        headAimUpFollwWorld=headAimUpLoc+'_follow_world'
        self.addFollowToGrp(headAimUpFollwWorld,headAimUpLoc,'World')
        con=cmds.parentConstraint(headAimUpFollwChest,headAimUpFollwWorld,headAimUpLoc)[0]
        cmds.connectAttr(headFkCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')

        # head aim follow

        cmds.addAttr(headAimCtrl,ln='follow',at='float',k=1,max=0,min=1,dv=1)
        followInv=cmds.createNode('reverse',n=headAimCtrl+'_follow_invNode')
        cmds.connectAttr(headAimCtrl+'.follow',followInv+'.ix')

        headAimFollwChest=headAimCtrlZero+'_follow_neck'
        self.addFollowToGrp(headAimFollwChest,headAimCtrlZero,'Neck')

        headAimFollowWorld=headAimCtrlZero+'_follow_world'
        self.addFollowToGrp(headAimFollowWorld,headAimCtrlZero,'World')


        con=cmds.parentConstraint(headAimFollwChest,headAimFollowWorld,headAimCtrlZero)[0]
        cmds.connectAttr(headAimCtrl+'.follow',con+'.w0')
        cmds.connectAttr(followInv+'.ox',con+'.w1')



    # def neckRig(self,neckJntList,headJnt,headEndJnt):
    #     neckRigGrp=cmds.group(em=1,n='neck_rig_grp')
    #     cmds.delete(cmds.parentConstraint(neckJntList[0],neckRigGrp))
    #     allCtrl='all_ctrl'
    #     cmds.parent(neckRigGrp,allCtrl)

    #     neckDrJntGrp=cmds.duplicate(neckRigGrp,po=1,rr=1,n='neck_dr_jnt_grp')[0]
    #     cmds.parent(neckDrJntGrp,neckRigGrp)
    #     cmds.setAttr(neckDrJntGrp+'.visibility',0)
    #     neckDrList=[]
    #     for neckJnt in neckJntList:
    #         neckDr=cmds.duplicate(neckJnt,po=1,rr=1,n=neckJnt+'_dr')[0]
    #         cmds.parent(neckDr,neckDrJntGrp)
    #         neckDrList.append(neckDr)

    #     for idx in range(1,len(neckDrList)):
    #         cmds.parent(neckDrList[idx],neckDrList[idx-1])

    #     neckFkCtrlGrp=cmds.duplicate(neckRigGrp,po=1,rr=1,n='neck_fk_ctrl_grp')[0]
    #     cmds.parent(neckFkCtrlGrp,neckRigGrp)

    #     neckFkCtrlList=[]
    #     for neckFkJnt in neckJntList:
    #         neckFkCtrl=neckFkJnt+'_ctrl'
    #         neckFkCtrlZero=ControlUtility.createControl(neckFkCtrl,'Circle',Mirror=False)
    #         ControlUtility.scaleCV(neckFkCtrl,5)
    #         cmds.delete(cmds.parentConstraint(neckFkJnt,neckFkCtrlZero))
    #         cmds.parent(neckFkCtrlZero,neckFkCtrlGrp)
    #         neckFkCtrlList.append([neckFkCtrl,neckFkCtrlZero])


    #     # ik joint list
    #     neckIkJntGrp=cmds.duplicate(neckRigGrp,po=1,rr=1,n='neck_ik_jnt_grp')[0]
    #     cmds.parent(neckIkJntGrp,neckRigGrp)
    #     # cmds.setAttr(neckDrJntGrp+'.visibility',0)
    #     neckIkList=[]
    #     for neckJnt in neckJntList:
    #         neckIk=cmds.duplicate(neckJnt,po=1,rr=1,n=neckJnt+'_ik')[0]
    #         cmds.parent(neckIk,neckIkJntGrp)
    #         neckIkList.append(neckIk)

    #     for idx in range(1,len(neckIkList)):
    #         cmds.parent(neckIkList[idx],neckIkList[idx-1])
        
    #     neckIkEnd=cmds.duplicate(headJnt,po=1,rr=1,n=neckJnt+'_ikEnd')[0]
    #     cmds.parent(neckIkEnd,neckIkList[-1])
    #     neckIkList.append(neckIkEnd)


    #     neckIkCtrlGrp=cmds.duplicate(neckRigGrp,po=1,rr=1,n='neck_ik_ctrl_grp')[0]
    #     cmds.parent(neckIkCtrlGrp,neckRigGrp)


    #     neckIkCtrlList=[]
    #     for neckIk in neckIkList:
    #         neckIkCtrl=neckIk+'_ctrl'
    #         neckIkCtrlZero=ControlUtility.createControl(neckIkCtrl,'Circle',Mirror=False)
    #         ControlUtility.scaleCV(neckIkCtrl,5)
    #         cmds.delete(cmds.parentConstraint(neckIk,neckIkCtrlZero))
    #         cmds.parent(neckIkCtrlZero,neckIkCtrlGrp)
    #         neckIkCtrlList.append([neckIkCtrl,neckIkCtrlZero])


    #     for idx in range(1,len(neckFkCtrlList)):
    #         cmds.parent(neckFkCtrlList[idx][1],neckFkCtrlList[idx-1][0])

    #     for neckFkCtrl,neckDr in zip(neckFkCtrlList,neckDrList):
    #         cmds.parentConstraint(neckFkCtrl[0],neckDr)


    #     # head rig

    #     headDrJntGrp=cmds.group(em=1,n='head_dr_jnt_grp')
    #     cmds.delete(cmds.parentConstraint(headJnt,headDrJntGrp))
    #     cmds.parent(headDrJntGrp,neckRigGrp)
    #     cmds.setAttr(headDrJntGrp+'.visibility',0)

    #     headDr=cmds.duplicate(headJnt,po=1,rr=1,n=headJnt+'_dr')[0]
    #     cmds.parent(headDr,headDrJntGrp)

    #     headEndDr=cmds.duplicate(headEndJnt,po=1,rr=1,n=headEndJnt+'_dr')[0]
    #     cmds.parent(headEndDr,headDr)


    #     headFkCtrlGrp=cmds.group(em=1,n='head_fk_ctrl_grp')
    #     cmds.delete(cmds.parentConstraint(headJnt,headFkCtrlGrp))
    #     cmds.parent(headFkCtrlGrp,neckRigGrp)


    #     headFkCtrl=headJnt+'_ctrl'
    #     headFkCtrlZero=ControlUtility.createControl(headFkCtrl,'Circle',Mirror=False)
    #     cmds.delete(cmds.parentConstraint(headJnt,headFkCtrlZero))
    #     ControlUtility.scaleCV(headFkCtrl,6)
    #     cmds.parentConstraint(headFkCtrl,headDr)
    #     cmds.parent(headFkCtrlZero,headFkCtrlGrp)


    #     # follow grp
    #     neckFollowGrp='neck_follow_grp'
    #     self.addFollowGrp(neckFollowGrp,neckFkCtrlList[-1][0])

    #     headFollowGrp='head_follow_grp'
    #     self.addFollowGrp(headFollowGrp,headFkCtrl)

    #     # neck follow
    #     neckRootCtrl=neckFkCtrlList[0][0]
    #     cmds.addAttr(neckRootCtrl,ln='follow',at='float',k=1,max=0,min=1,dv=1)
    #     followInv=cmds.createNode('reverse',n=neckRootCtrl+'_follow_invNode')
    #     cmds.connectAttr(neckRootCtrl+'.follow',followInv+'.ix')

    #     neckFollwChest=neckFkCtrlGrp+'_follow_chest'
    #     self.addFollowToGrp(neckFollwChest,neckFkCtrlGrp,'Chest')

    #     neckFollowWorld=neckFkCtrlGrp+'_follow_world'
    #     self.addFollowToGrp(neckFollowWorld,neckFkCtrlGrp,'World')

    #     cmds.pointConstraint(neckFollwChest,neckFkCtrlGrp)
    #     con=cmds.orientConstraint(neckFollwChest,neckFollowWorld,neckFkCtrlGrp)[0]
    #     cmds.connectAttr(neckRootCtrl+'.follow',con+'.w0')
    #     cmds.connectAttr(followInv+'.ox',con+'.w1')

    #     # head follow

    #     cmds.addAttr(headFkCtrl,ln='follow',at='float',k=1,max=0,min=1,dv=1)
    #     followInv=cmds.createNode('reverse',n=headFkCtrl+'_follow_invNode')
    #     cmds.connectAttr(headFkCtrl+'.follow',followInv+'.ix')

    #     headFollwChest=headFkCtrlGrp+'_follow_neck'
    #     self.addFollowToGrp(headFollwChest,headFkCtrlGrp,'Neck')

    #     headFollowWorld=headFkCtrlGrp+'_follow_world'
    #     self.addFollowToGrp(headFollowWorld,headFkCtrlGrp,'World')

    #     cmds.pointConstraint(headFollwChest,headFkCtrlGrp)
    #     con=cmds.orientConstraint(headFollwChest,headFollowWorld,headFkCtrlGrp)[0]
    #     cmds.connectAttr(headFkCtrl+'.follow',con+'.w0')
    #     cmds.connectAttr(followInv+'.ox',con+'.w1')
 
    def addFollowGrp(self,grpName,ctrlName):
        grpName=cmds.group(em=1,n=grpName)
        cmds.delete(cmds.parentConstraint(ctrlName,grpName))
        cmds.parent(grpName,ctrlName)
    def addFollowToGrp(self,grpName,conName,folName):
        findDict={'World':'world_follow_grp','Body':'body_follow_grp','Hip':'hip_follow_grp','Chest':'chest_follow_grp','Neck':'neck_follow_grp','Head':'head_follow_grp'}
        folName=findDict.get(folName,folName)

        grpName=cmds.group(em=1,n=grpName)
        cmds.delete(cmds.parentConstraint(conName,grpName))
        cmds.parent(grpName,folName)

    def createBsSdkHandle(self):
        drConfigFile=self.filesPath+'Template/DriverConfig.drini'
        with open(drConfigFile,'r') as fileHandle:
            drData=OrderedDict(pickle.load(fileHandle))
        sdkHandle='body_sdk_handle'
        if(not cmds.objExists(sdkHandle)):
            allCtrl='all_ctrl'
            sdkHandle=cmds.group(em=1,n=sdkHandle)
            cmds.parent(sdkHandle,allCtrl)
        for i in drData:
            if(drData[i]==None):
                continue
            drJnt=i
            typ=drData[i]
            if(typ=='Direct'):
                self.directDriverSystem(drJnt,sdkHandle)
            else:
                self.angleDirverSystem(drJnt,sdkHandle)
    def directDriverSystem(self,drObj,sdkHandle):
        subAttr=[('U','ry',180),('D','ry',-180),('F','rz',180),('B','rz',-180)]
        for Dir,Attr,Dv in subAttr:
            cAttr=drObj+'_'+Dir
            cmds.addAttr(sdkHandle,ln=cAttr,at='float',k=1,min=0,max=180)
            driverAttr=drObj+'.'+Attr
            drivenAttr=sdkHandle+'.'+cAttr
            cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=0,dv=0,itt='linear',ott='linear')
            cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=180,dv=Dv,itt='linear',ott='linear')


    def angleDirverSystem(self,attachObj,sdkHandle):
        if(not cmds.objExists(attachObj)):
            raise RuntimeError,'%s is not exists!'%attachObj
        baseADName=attachObj+'_angleDriver'
        handle=cmds.group(n=baseADName+'_handle',em=1)
        cmds.setAttr(handle+'.v',0)
        followLoc=baseADName+'_follow_loc'
        followLoc=cmds.spaceLocator(n=followLoc)[0]
        cmds.setAttr(followLoc+'.tx',1)

        cmds.parent(followLoc,handle)
        centerLoc=baseADName+'_center_loc'
        centerLoc=cmds.spaceLocator(n=centerLoc)[0]
        cmds.transformLimits(centerLoc,tx=[0,0],etx=[True,True])
        cmds.parent(centerLoc,handle)
        cmds.pointConstraint(followLoc,centerLoc)

        mainAngle=cmds.createNode('angleBetween',n=baseADName+'_AB')
        cmds.connectAttr(followLoc+'.t',mainAngle+'.v1')
        val=cmds.getAttr(mainAngle+'.v1')[0]
        cmds.setAttr(mainAngle+'.v2',val[0],val[1],val[2],typ='float3')

        mainAngleAttr=mainAngle+'.axisAngle.angle'
        tmList=[
            ('U',(0,1,0),90),
            ('D',(0,-1,0),90),
            ('F',(0,0,1),90),
            ('B',(0,0,-1),90),
            ('UF',(0,1,1),45),
            ('UB',(0,1,-1),45),
            ('DF',(0,-1,1),45),
            ('DB',(0,-1,-1),45)]
        for i in tmList:
            dAttr,dPos,dLimit=i
            cmds.addAttr(handle,ln=dAttr,at='float',k=1,max=180,min=0)
            cmds.addAttr(sdkHandle,ln=attachObj+'_'+dAttr,at='float',k=1,max=180,min=0)
            cmds.connectAttr(handle+'.'+dAttr,sdkHandle+'.'+attachObj+'_'+dAttr)
            
            dAngle=cmds.createNode('angleBetween',n=baseADName+'_%s_ABw'%dAttr)
            cmds.connectAttr(centerLoc+'.t',dAngle+'.v1')
            cmds.setAttr(dAngle+'.v2',dPos[0],dPos[1],dPos[2],typ='float3')
            dClamp=cmds.createNode('clamp',n=baseADName+'_%s_CP'%dAttr)
            cmds.setAttr(dClamp+'.mxr',dLimit)
            cmds.connectAttr(dAngle+'.axisAngle.angle',dClamp+'.ipr')
            dDivide=cmds.createNode('multiplyDivide',n=baseADName+'_%s_MD'%dAttr)
            cmds.setAttr(dDivide+'.op',2)
            cmds.connectAttr(dClamp+'.opr',dDivide+'.i1x')
            cmds.setAttr(dDivide+'.i2x',dLimit)
            dReverse=cmds.createNode('reverse',n=baseADName+'_%s_RV'%dAttr)
            cmds.connectAttr(dDivide+'.ox',dReverse+'.ix')
            outMul=cmds.createNode('multiplyDivide',n=baseADName+'_%s_out_MD'%dAttr)
            cmds.connectAttr(dReverse+'.ox',outMul+'.i1x')
            cmds.connectAttr(mainAngleAttr,outMul+'.i2x')
            cmds.connectAttr(outMul+'.ox',handle+'.'+dAttr)


        cmds.delete(cmds.parentConstraint(attachObj,handle))
        cmds.pointConstraint(attachObj,handle)
        cmds.parentConstraint(attachObj,followLoc,mo=1)
        pObj=cmds.listRelatives(attachObj,p=1)
        if(pObj):
            cmds.parent(handle,pObj)
        return handle
    def buildRigging(self,*args):
        # unlock
        jntCtrl='Temp_Ctrl'
        if(not cmds.objExists(jntCtrl)):
            return
        gls=cmds.getAttr(jntCtrl+'.sx')
        attrStrList=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        sel=cmds.listRelatives(jntCtrl,c=1,typ='joint',ad=1)
        for i in sel:
            for attr in attrStrList:
                cmds.setAttr(i+'.'+attr,l=0)
        cmds.makeIdentity(jntCtrl,a=1,t=1,r=1,s=1,n=0,pn=1)
        # root rig 
        rigGrp=cmds.group(em=1,n='rig_grp')
        cmds.addAttr(rigGrp,ln='TempScale',at='float',k=1,dv=gls)
        ControlUtility.GlobalScale=gls

        globalCtrl='global_ctrl'
        globalCtrlZero=ControlUtility.createControl(globalCtrl,'Root',Mirror=False)
        ControlUtility.scaleCV(globalCtrl,50)
        cmds.parent(globalCtrlZero,rigGrp)
 

        allCtrl='all_ctrl'
        allCtrlZero=ControlUtility.createControl(allCtrl,'Root',S=True,Mirror=False)
        ControlUtility.scaleCV(allCtrl,40)
        cmds.parent(allCtrlZero,globalCtrl)
        cmds.connectAttr(allCtrl+'.sx',allCtrl+'.sy')
        cmds.connectAttr(allCtrl+'.sx',allCtrl+'.sz')
        cmds.setAttr(allCtrl+'.sy',k=0)
        cmds.setAttr(allCtrl+'.sz',k=0)
        cmds.aliasAttr('globalScale',allCtrl+'.sx')
        cmds.setAttr(allCtrl+'.v',k=0)

        worldFollowGrp='world_follow_grp'
        followWorldGrp=cmds.group(em=1,n=worldFollowGrp)
        cmds.parent(followWorldGrp,allCtrl)

        chestJnt='chest'
        chestMidJnt='chect_mid'
        hipJnt='Hips'
        spineJntList=['spine_1','spine_2','spine_3','spine_4','spine_5']
        self.spineRig(spineJntList,chestJnt,chestMidJnt,hipJnt)

        neckJntList=['neck_1','neck_2','neck_3']
        headJnt='head'
        headEndJnt='head_end'
        self.neckRig(neckJntList,headJnt,headEndJnt)

        shoulderJnt='L_shoulder'
        uparmJnt='L_arm'
        lowarmJnt='L_lowarm'
        handJnt='L_hand'
        self.armRig(shoulderJnt,uparmJnt,lowarmJnt,handJnt)

        shoulderJnt='R_shoulder'
        uparmJnt='R_arm'
        lowarmJnt='R_lowarm'
        handJnt='R_hand'
        self.armRig(shoulderJnt,uparmJnt,lowarmJnt,handJnt)

        uplegJnt='L_leg'
        lowlegJnt='L_lowleg'
        footJnt='L_foot'
        toebaseJnt='L_toebase'
        toeendJnt='L_toeend'
        toeinJnt='L_toein'
        toeoutJnt='L_toeout'
        heelJnt='L_heel'
        self.legRig(uplegJnt,lowlegJnt,footJnt,toebaseJnt,toeendJnt,toeinJnt,toeoutJnt,heelJnt)

        uplegJnt='R_leg'
        lowlegJnt='R_lowleg'
        footJnt='R_foot'
        toebaseJnt='R_toebase'
        toeendJnt='R_toeend'
        toeinJnt='R_toein'
        toeoutJnt='R_toeout'
        heelJnt='R_heel'
        self.legRig(uplegJnt,lowlegJnt,footJnt,toebaseJnt,toeendJnt,toeinJnt,toeoutJnt,heelJnt)
        self.createBsSdkHandle()

        cmds.delete(jntCtrl)
        allFKcon=cmds.select('body_ctrl','R_shoulder_ctrl','L_shoulder_ctrl','spine_1_ctrl','Hips_ctrl','spine_2_ctrl','spine_3_ctrl','spine_4_ctrl','spine_5_ctrl','chest_ctrl','chect_mid_ctrl','R_arm_fk_ctrl','R_lowarm_fk_ctrl','R_hand_fk_ctrl','L_indexfinger_1_ctrl','L_indexfinger_2_ctrl','L_indexfinger_3_ctrl','head_ctrl','neck_1_ctrl','neck_2_ctrl','neck_3_ctrl','R_indexfinger_1_ctrl','R_indexfinger_2_ctrl','R_indexfinger_3_ctrl','L_pinkyfinger_1_ctrl','L_pinkyfinger_2_ctrl','L_pinkyfinger_3_ctrl','L_middlefinger_1_ctrl','L_ringfinger_1_ctrl','L_ringfinger_2_ctrl','L_ringfinger_3_ctrl','L_middlefinger_2_ctrl','L_middlefinger_3_ctrl','L_leg_fk_ctrl','L_lowleg_fk_ctrl','L_foot_fk_ctrl','L_toebase_fk_ctrl','R_thumbfinger_1_ctrl','R_thumbfinger_2_ctrl','R_thumbfinger_3_ctrl','L_arm_fk_ctrl','L_lowarm_fk_ctrl','L_hand_fk_ctrl','R_leg_fk_ctrl','R_lowleg_fk_ctrl','R_foot_fk_ctrl','R_toebase_fk_ctrl','L_thumbfinger_1_ctrl','L_thumbfinger_2_ctrl','L_thumbfinger_3_ctrl','R_middlefinger_1_ctrl','R_middlefinger_2_ctrl','R_middlefinger_3_ctrl','R_pinkyfinger_1_ctrl','R_pinkyfinger_2_ctrl','R_pinkyfinger_3_ctrl','R_ringfinger_1_ctrl','R_ringfinger_2_ctrl','R_ringfinger_3_ctrl' )
        selFK=cmds.ls(sl=1)
        for ii in selFK:
            fkShapeList=cmds.listRelatives(selFK,s=1,f=1)
            for oo in fkShapeList:
                cmds.setAttr(oo+'.overrideEnabled',1)
                cmds.setAttr(oo+'.overrideColor',6)
        
        allIkcon=cmds.select('spine_4_ik_ctrl','spine_1_ik_ctrl','spine_3_ik_ctrl','spine_5_ik_ctrl','spine_2_ik_ctrl','R_arm_ik_ctrl','R_arm_ik_pole_ctrl','L_arm_ik_pole_ctrl','L_arm_ik_ctrl','R_leg_ik_pole_ctrl','R_leg_ik_ctrl','R_toebase_ik_ctrl','L_leg_ik_ctrl','L_leg_ik_pole_ctrl','L_toebase_ik_ctrl')
        selIK=cmds.ls(sl=1)
        for iii in selIK:
            IKShapeList=cmds.listRelatives(selIK,s=1,f=1)
            for ooo in IKShapeList:
                cmds.setAttr(ooo+'.overrideEnabled',1)
                cmds.setAttr(ooo+'.overrideColor',13)
        allMedcon=cmds.select( 'all_ctrl','global_ctrl','L_leg_switch_ctrl','L_indexfinger_curl_ctrl','L_ringfinger_curl_ctrl','L_thumbfinger_curl_ctrl','L_middlefinger_curl_ctrl','L_pinkyfinger_curl_ctrl','R_indexfinger_curl_ctrl','R_middlefinger_curl_ctrl','R_pinkyfinger_curl_ctrl','R_arm_switch_ctrl','R_leg_switch_ctrl','L_arm_switch_ctrl','R_ringfinger_curl_ctrl','R_thumbfinger_curl_ctrl')
        selMed=cmds.ls(sl=1)
        for iiii in selMed:
            MedShapeList=cmds.listRelatives(selMed,s=1,f=1)
            for oooo in MedShapeList:
                cmds.setAttr(oooo+'.overrideEnabled',1)
                cmds.setAttr(oooo+'.overrideColor',17)
        allSeccon=cmds.select( 'R_leg_second_02_ctrl','R_lowleg_second_01_ctrl','R_lowleg_second_03_ctrl','R_lowleg_second_02_ctrl','L_leg_second_01_ctrl','L_leg_second_02_ctrl','L_lowarm_second_03_ctrl','L_lowarm_second_01_ctrl','L_lowarm_second_02_ctrl','R_lowarm_second_01_ctrl','R_lowarm_second_03_ctrl','R_lowarm_second_02_ctrl','R_arm_second_01_ctrl','R_arm_second_02_ctrl','R_leg_second_01_ctrl','L_arm_second_02_ctrl','L_arm_second_01_ctrl','L_lowleg_second_01_ctrl','L_lowleg_second_03_ctrl','L_lowleg_second_02_ctrl')
        selSec=cmds.ls(sl=1)
        for iiiii in selSec:
            SecShapeList=cmds.listRelatives(selSec,s=1,f=1)
            for ooooo in SecShapeList:
                cmds.setAttr(ooooo+'.overrideEnabled',1)
                cmds.setAttr(ooooo+'.overrideColor',24)
    def outputJoint(self,*args):
        typIdx=cmds.radioButtonGrp('outTypeRBG_br',q=1,sl=1)
        jmap1=self.filesPath+'JMap/normal.jmap'
        jmap2=self.filesPath+'JMap/mocap.jmap'
        jmap3=self.filesPath+'JMap/mocap_sec1.jmap'
        jmap4=self.filesPath+'JMap/mocap_sec4.jmap'
        jmapList=[jmap1,jmap2,jmap3,jmap4]
        filePath=jmapList[typIdx-1]
        with open(filePath,'r') as fileHandle:
            outJntData=OrderedDict(pickle.load(fileHandle))
        
        # OutputJointGrp='joint_grp'
        # if(not cmds.objExists(OutputJointGrp)):
        #     OutputJointGrp=cmds.group(em=1,n='joint_grp') 
        jointList=[]
        for i in outJntData:
            if(outJntData[i]==None):
                continue
            drJnt=i
            outJnt=outJntData[i]['outName']
            offset=outJntData[i]['offset']
            pObj=outJntData[i]['parent']

            if(not cmds.objExists(outJnt)):
                outJnt=cmds.duplicate(drJnt,n=outJnt,rr=1,po=1)[0]
                cmds.parent(outJnt,w=1)
                cmds.rotate(offset[0],offset[1],offset[2],outJnt,r=1,os=1,fo=1)
                cmds.makeIdentity(outJnt,a=1,t=1,r=1,s=1,n=0,pn=1)
                if(pObj):
                    cmds.parent(outJnt,pObj)
            else:
                pcon=cmds.parentConstraint(outJnt,q=1,n=1)
                scon=cmds.scaleConstraint(outJnt,q=1,n=1)
                if(pcon):
                    cmds.delete(pcon)
                if(scon):
                    cmds.delete(scon)
            jointList.append(outJnt)



            cmds.parentConstraint(drJnt,outJnt,mo=1)
            cmds.scaleConstraint(drJnt,outJnt,mo=1)
        cmds.select(jointList[0])
    # sdk====================================================
    def loadDriverCtrl(self,*args):
        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return
        cmds.textField('sdkDriverCtrlTF_br',e=1,tx=sel[0])
        self.loadDirverAttr()
    def loadDrivenCtrl(self,*args):
        typ=args[0]
        sel=cmds.ls(sl=1)
        if(len(sel)==0):
            return
        if(typ=='Load'):
            cmds.textScrollList('sdkDrivenListTSL_br',e=1,ra=1)
        for i in sel:
            cmds.textScrollList('sdkDrivenListTSL_br',e=1,a=i)
        self.checkDrivenListSdkGrp()
    def clearDrivenList(self,*args):
        cmds.textScrollList('sdkDrivenListTSL_br',e=1,ra=1)
    def checkDrivenListSdkGrp(self,*args):
        allI=cmds.textScrollList('sdkDrivenListTSL_br',q=1,ai=1)
        if(allI==None):
            return
        for i in allI:
            GeneralUtility.createSdkGrp(i)
    def resetDrivenListToZero(self,*args):
        allI=cmds.textScrollList('sdkDrivenListTSL_br',q=1,ai=1)
        if(allI==None):
            return
        for i in allI:
            sdkGrp=GeneralUtility.createSdkGrp(i)

            GeneralUtility.resetTransformAttr(sdkGrp)
            GeneralUtility.resetTransformAttr(i)

    def loadLRingerPref(self,*args):
        cmds.textField('sdkDriverCtrlTF_br',e=1,tx='L_arm_switch_ctrl')
        cmds.textScrollList('sdkDrivenListTSL_br',e=1,ra=1)
        dnList=['L_thumbfinger_1_ctrl', 'L_thumbfinger_2_ctrl', 'L_thumbfinger_3_ctrl', 'L_indexfinger_1_ctrl', 'L_indexfinger_2_ctrl', 'L_indexfinger_3_ctrl', 'L_middlefinger_1_ctrl', 'L_middlefinger_2_ctrl', 'L_middlefinger_3_ctrl', 'L_ringfinger_1_ctrl', 'L_ringfinger_2_ctrl', 'L_ringfinger_3_ctrl', 'L_pinkyfinger_1_ctrl', 'L_pinkyfinger_2_ctrl', 'L_pinkyfinger_3_ctrl']
        for i in dnList:
            cmds.textScrollList('sdkDrivenListTSL_br',e=1,a=i)
        self.loadDirverAttr()
        self.checkDrivenListSdkGrp()
    def loadRRingerPref(self,*args):
        cmds.textField('sdkDriverCtrlTF_br',e=1,tx='R_arm_switch_ctrl')
        cmds.textScrollList('sdkDrivenListTSL_br',e=1,ra=1)
        dnList=['R_thumbfinger_1_ctrl', 'R_thumbfinger_2_ctrl', 'R_thumbfinger_3_ctrl', 'R_indexfinger_1_ctrl', 'R_indexfinger_2_ctrl', 'R_indexfinger_3_ctrl', 'R_middlefinger_1_ctrl', 'R_middlefinger_2_ctrl', 'R_middlefinger_3_ctrl', 'R_ringfinger_1_ctrl', 'R_ringfinger_2_ctrl', 'R_ringfinger_3_ctrl', 'R_pinkyfinger_1_ctrl', 'R_pinkyfinger_2_ctrl', 'R_pinkyfinger_3_ctrl']
        for i in dnList:
            cmds.textScrollList('sdkDrivenListTSL_br',e=1,a=i)
        self.loadDirverAttr()
        self.checkDrivenListSdkGrp()
    def drivenListSelectChange(self,*args):
        sel=cmds.textScrollList('sdkDrivenListTSL_br',q=1,si=1)
        if(sel==None):
            return
        cmds.select(sel)
    def loadDirverAttr(self,*args):
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        if(not cmds.objExists(drCtrl)):
            return
        showType=cmds.radioButtonGrp('sdkShowTypeRBG_br',q=1,sl=1)

        if(showType==1):
            attrList=cmds.listAttr(drCtrl,k=1)
        else:
            attrList=cmds.listAttr(drCtrl,k=1,ud=1)
        isOnlyFloat=cmds.checkBox('sdkShowTypeCB_br',q=1,v=1)

        cmds.treeView('sdkDriverAttrListTV_br',e=1,ra=1)
        if(attrList==None):
            return
        for i in attrList:
            drAttr=drCtrl+'.'+i
            typ=cmds.getAttr(drAttr,type=1)
            if(isOnlyFloat):
                if not(typ in ['float','double','doubleAngle','doubleLinear']):
                    continue
            cmds.treeView('sdkDriverAttrListTV_br',e=1,ai=[i,''])
            val=cmds.getAttr(drAttr)
            cmds.treeView('sdkDriverAttrListTV_br',e=1,dls=[i,' %s'%val])
    def driverAttrSelectChange(self,*args):
        selI=cmds.treeView('sdkDriverAttrListTV_br',q=1,si=1)
        if(selI==None):
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        drAttr=drCtrl+'.'+selI[0]
        maxV=self.getAttrMax(drCtrl,selI[0])
        minV=self.getAttrMin(drCtrl,selI[0])
        val=cmds.getAttr(drAttr)
        cmds.floatSliderGrp('sdkDriverAttrValFSG_br',e=1,max=maxV,min=minV,v=val,pre=1 if(maxV>1) else 2)
        cmds.button('sdkDefineB_br',e=1,en=len(selI)==1)

    def getAttrMax(self,obj,attr):
        if(cmds.attributeQuery(attr,node=obj,mxe=1)):
            return cmds.attributeQuery(attr,node=obj,max=1)[0]
        print attr
        return 100
    def getAttrMin(self,obj,attr):
        if(cmds.attributeQuery(attr,node=obj,mne=1)):
            return cmds.attributeQuery(attr,node=obj,min=1)[0]
        return -100

    def driverValueSelectChange(self,*args):
        val=cmds.floatSliderGrp('sdkDriverAttrValFSG_br',q=1,v=1)
        selI=cmds.treeView('sdkDriverAttrListTV_br',q=1,si=1)
        if(selI==None):
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        for i in selI:
            drAttr=drCtrl+'.'+i
            try:
                cmds.undoInfo(swf=0)
                cmds.setAttr(drAttr,val)
                cmds.treeView('sdkDriverAttrListTV_br',e=1,dls=[i,' %s'%val])
            finally:
                cmds.undoInfo(swf=1)

    def resetDriverListToZero(self,*args):
        selI=cmds.treeView('sdkDriverAttrListTV_br',q=1,ch=1)
        if(selI==None):
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        for i in selI:
            drAttr=drCtrl+'.'+i
            try:
                cmds.undoInfo(swf=0)
                cmds.setAttr(drAttr,0)
                cmds.treeView('sdkDriverAttrListTV_br',e=1,dls=[i,' %s'%0.0])
            finally:
                cmds.undoInfo(swf=1)
        self.resetDrivenListToZero()
    def deleteDriverAttr(self,*args):
        selI=cmds.treeView('sdkDriverAttrListTV_br',q=1,si=1)
        if(selI==None):
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        drAttr=drCtrl+'.'+selI[0]
        ret=cmds.confirmDialog( t='Confirm', m='Are you sure Delete This?', b=['Yes','No'], db='No', cb='No', ds='No' )
        if(ret!='Yes'):
            return
        cmds.deleteAttr(drAttr)
        self.loadDirverAttr()

    def newDriverAttr(self,*args):
        cmds.layoutDialog(ui=self.newDriverAttrUI)
        
    def newDriverAttrUI(self):
        form = cmds.setParent(q=True)
        cmds.columnLayout('nDrAttrMainCL_br',adj=True)
        cmds.textFieldGrp('nAttrNameTFG_br',cw=[[1, 50]],adj=2,l=u'Name:')
        cmds.rowLayout(nc=4)
        cmds.text(w=50,l=u'Mininum:',al=u'right')
        cmds.floatField('nMinValFF_br',w=93,v=-10.0,pre=2)
        cmds.text(w=50,l=u'Maxinum:',al=u'right')
        cmds.floatField('nMaxValFF_br',w=93,v=10.0,pre=2)
        cmds.button('nCreateB_br',p=form,l=u'New',c=self.newButtonProc)
        cmds.button('nCancelB_br',p=form,l=u'Cancel',c=self.cancelButtonProc)
        cmds.formLayout(form,e=1,af=[[u'nDrAttrMainCL_br', 'top', 5], [u'nDrAttrMainCL_br', 'left', 5], [u'nDrAttrMainCL_br', 'right', 5], [u'nCreateB_br', 'left', 5], [u'nCreateB_br', 'bottom', 5], [u'nCancelB_br', 'right', 5], [u'nCancelB_br', 'bottom', 5]],ac=[[u'nCancelB_br', 'left', 5, u'nCreateB_br']],ap=[[u'nCreateB_br', 'right', 5, 50]])
    def newButtonProc(self,*args):
        newName=cmds.textFieldGrp('nAttrNameTFG_br',q=1,tx=1)
        maxV=cmds.floatField('nMinValFF_br',q=1,v=1)
        minV=cmds.floatField('nMaxValFF_br',q=1,v=1)
        nameRegex=re.compile('^[\w][\w]*$')
        if(not nameRegex.match(newName)):
            cmds.textFieldGrp('nAttrNameTFG_br',e=1,tx='')
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        if(not cmds.objExists(drCtrl)):
            return
        cmds.addAttr(drCtrl,ln=newName,at='float',k=1,max=maxV,min=minV)
        self.loadDirverAttr()
        cmds.layoutDialog(dis='OK')
    def cancelButtonProc(self,*args):
        cmds.layoutDialog(dis='Cancel')

    def redefineSdk(self,*args):
        selI=cmds.treeView('sdkDriverAttrListTV_br',q=1,si=1)
        if(selI==None):
            return
        drCtrl=cmds.textField('sdkDriverCtrlTF_br',q=1,tx=1)
        if(not cmds.objExists(drCtrl)):
            return
        dnCtrlList=cmds.textScrollList('sdkDrivenListTSL_br',q=1,ai=1)
        if(dnCtrlList==None):
            return
        driverValue=cmds.floatSliderGrp('sdkDriverAttrValFSG_br',q=1,v=1)
        if(driverValue==0):
            return
        isMirror=cmds.checkBox('sdkMirrorCB_br',q=1,v=1)
        driverAttr=drCtrl+'.'+selI[0]

        mirDrCtrl=self.getMirrorName(drCtrl)
        if(mirDrCtrl==drCtrl):
            isMirror=False
        mirDriverAttr=mirDrCtrl+'.'+selI[0]

        for dnCtrl in dnCtrlList:
            GeneralUtility.transferSdkValueToCtrl(dnCtrl)

        attrStrList=['tx','ty','tz','rx','ry','rz']
        for dnCtrl in dnCtrlList:
            sdkGrp=GeneralUtility.createSdkGrp(dnCtrl)
            mirDnCtrl=self.getMirrorName(dnCtrl)
            mirSdkGrp=GeneralUtility.createSdkGrp(mirDnCtrl)
            
            for attr in attrStrList:
                isLock=cmds.getAttr(dnCtrl+'.'+attr,l=1)
                if(isLock):
                    continue
                drivenValue=cmds.getAttr(dnCtrl+'.'+attr)
                if(round(drivenValue,3)==0):
                    continue

                drivenAttr=sdkGrp+'.'+attr
                cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=0,dv=0,itt='linear',ott='linear')
                cmds.setDrivenKeyframe(drivenAttr,cd=driverAttr,v=drivenValue,dv=driverValue,itt='linear',ott='linear')
                
                if(not isMirror):
                    continue
                mirDrivenAttr=mirSdkGrp+'.'+attr
                cmds.setDrivenKeyframe(mirDrivenAttr,cd=mirDriverAttr,v=0,dv=0,itt='linear',ott='linear')
                cmds.setDrivenKeyframe(mirDrivenAttr,cd=mirDriverAttr,v=drivenValue,dv=driverValue,itt='linear',ott='linear')
            
        for dnCtrl in dnCtrlList:
            GeneralUtility.resetTransformAttr(dnCtrl)
        cmds.setAttr(driverAttr,0)

    def transferSdk(self,*args):
        dnCtrlList=cmds.textScrollList('sdkDrivenListTSL_br',q=1,ai=1)
        if(dnCtrlList==None):
            return
        for dnCtrl in dnCtrlList:
            GeneralUtility.transferSdkValueToCtrl(dnCtrl)
    # correct blendshape
    def enterModifyMode(self,*args):
        self.CrtModule.enterModifyMode()
        cmds.button('bsEnterModifyB_br',e=1,vis=0)
        cmds.button('bsExistsModifyB_br',e=1,vis=0)
        cmds.button('bsExistsModifyB_br',e=1,vis=1)
    def exitModifyMode(self,*args):
        self.CrtModule.exitModifyMode()
        cmds.button('bsEnterModifyB_br',e=1,vis=0)
        cmds.button('bsExistsModifyB_br',e=1,vis=0)
        cmds.button('bsEnterModifyB_br',e=1,vis=1)

def add_character_name():
    txName=cmds.textFieldButtonGrp('character_name',q=1,tx=1)
    crateN=cmds.textCurves(n='cName',ch=1,f='Times New Roman|h-500|w2000|c0',t=txName)
    selShapeAll=cmds.listRelatives(crateN,c=1)
    sel=cmds.listRelatives(selShapeAll,c=1)
    for i in sel[1:]:
        selShape=cmds.listRelatives(i,s=1,f=1)
        for s in selShape:
            newShape=cmds.rename(s,sel[0].split('|')[-1]+'Shape')
            cmds.parent(i,sel[0])
            cmds.makeIdentity(i,apply=1,t=1,r=1,s=1,n=0)
            cmds.parent(i,w=1)
            cmds.parent(newShape,sel[0],r=1,s=1)
        cmds.delete(i)
    
    for a in range(1,len(selShapeAll)):
        selShapeTall=selShapeAll[a]
        cmds.delete(selShapeTall)
    cmds.setAttr(sel[0]+'.overrideEnabled',1)
    cmds.setAttr(sel[0]+'.overrideColor',17)
    cmds.setAttr(sel[0]+'.scaleX',20)
    cmds.setAttr(sel[0]+'.scaleY',20)
    cmds.setAttr(sel[0]+'.scaleZ',20)
    cmds.xform(crateN,cpc=1)
    cmds.pointConstraint('head_ctrl',crateN,w=1,e=0)
    cmds.delete(crateN[0]+'_pointConstraint1')
    cmds.parent(crateN[0],'head_ctrl')
    cmds.makeIdentity(crateN[0],apply=1,t=1,r=1,s=1,n=0)
    cmds.setAttr(crateN[0]+'.tx',30)
    cmds.delete(sel[0],ch=1)
    cmds.disconnectAttr(crateN[1]+'.position[0]',selShapeAll[0]+'.translate')
    cmds.rename(sel[0],txName+'_ctrl')

def BodyRigging(self):
    if(cmds.window('sdd_BodyRigging_br',q=True,ex=True)):cmds.deleteUI('sdd_BodyRigging_br')
    cmds.window('sdd_BodyRigging_br',mb=False)
    cmds.tabLayout('mainTL_br',cr=True)
    cmds.columnLayout('riggingMainCL_br',adj=True)
    cmds.frameLayout('tempFRL_br',cll=False,l=u'Joint Template',mh=2,mw=2)
    cmds.columnLayout(adj=True)
    cmds.button(h=45,l=u'Import',c=self.importJointTemplate)
    cmds.frameLayout('mirrorFRL_br',p='riggingMainCL_br',cll=False,l=u'Mirror',mh=2,mw=2)
    cmds.columnLayout('mirrorCL_br',adj=True,rs=2)
    cmds.rowLayout(nc=3,adj=2)
    cmds.button(w=153,l=u'R>>L',c=functools.partial(self.mirrorJoint,'R_'))
    cmds.text(l=u'======')
    cmds.button(w=153,l=u'R<<L',c=functools.partial(self.mirrorJoint,'L_'))
    cmds.rowLayout(p='mirrorCL_br',nc=1,adj=1)
    cmds.button(l=u'Mirror Selection',c=functools.partial(self.mirrorJoint,'select'))
    cmds.frameLayout('buildFRL_br',p='riggingMainCL_br',cll=False,l=u'Build',mh=2,mw=2)
    cmds.columnLayout(adj=True)
    cmds.button(h=45,l=u'Rigging',c=self.buildRigging)
    cmds.textFieldButtonGrp('character_name', label='Character name', text='', buttonLabel='add' ,bc='add_character_name()')
    cmds.frameLayout('exportFRL_br',p='riggingMainCL_br',cll=False,l=u'Export',mh=2,mw=2)
    cmds.columnLayout(adj=True,rs=5)
    cmds.radioButtonGrp('outTypeRBG_br',cw=[[1, 80], [2, 80], [3, 90], [4, 90]],nrb=4,sl=2,l1=u'Normal',l2=u'Mocap',l3=u'Mocap+SEC1',l4=u'Mocap+SEC4')
    cmds.button(h=45,l=u'Create Output Joints',c=self.outputJoint)
    cmds.frameLayout('extendFRL_br',p='riggingMainCL_br',cl=True,cll=True,l=u'Extend Rig *')
    cmds.columnLayout('columnLayout9_br',adj=True)
    cmds.frameLayout('armrigFRL_br',cl=True,cll=True,l=u'Arm Rig')
    cmds.columnLayout(adj=True)
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'Shoulder:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'UpArm:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'LowArm:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'Hand:',ed=False,bl=u'Load')
    cmds.button(l=u'Rigging')
    cmds.frameLayout('legrigFRL_br',p='columnLayout9_br',cl=True,cll=True,l=u'Leg Rig')
    cmds.columnLayout(adj=True)
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'UpLeg:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'LowLeg:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'Foot:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'ToeBase:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'ToeEnd:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'ToeIn:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'ToeOut:',ed=False,bl=u'Load')
    cmds.textFieldButtonGrp(cw=[[1, 55]],adj=2,l=u'Heel:',ed=False,bl=u'Load')
    cmds.button(l=u'Rigging')
    cmds.columnLayout('sdkMainCL_br',p='mainTL_br',adj=True)
    cmds.frameLayout(cll=False,l=u'Driver',mh=2,mw=2)
    cmds.rowLayout(nc=2,adj=1)
    cmds.textField('sdkDriverCtrlTF_br',ed=False)
    cmds.popupMenu(p='sdkDriverCtrlTF_br',b=1)
    cmds.menuItem(l=u'L Finger Pref',c=self.loadLRingerPref)
    cmds.menuItem(l=u'R Finger Pref',c=self.loadRRingerPref)
    cmds.columnLayout(adj=True)
    cmds.button('sdkLoadDriver_br',w=80,h=20,l=u'Load',c=self.loadDriverCtrl)
    cmds.frameLayout(p='sdkMainCL_br',cll=False,l=u'Driven',mh=2,mw=2)
    cmds.rowLayout(nc=2,adj=1)
    cmds.textScrollList('sdkDrivenListTSL_br',h=90,ams=True,sc=self.drivenListSelectChange)
    cmds.columnLayout(h=92,adj=True,rs=2)
    cmds.button(w=80,h=20,l=u'Load',c=functools.partial(self.loadDrivenCtrl,'Load'))
    cmds.button(w=80,h=20,l=u'Add',c=functools.partial(self.loadDrivenCtrl,'Add'))
    cmds.button(w=80,h=20,l=u'Clear All',c=self.clearDrivenList)
    cmds.frameLayout(p='sdkMainCL_br',cll=False,l=u'SDK Define',mh=2,mw=2)
    cmds.columnLayout('sdkDefineCL_br',adj=True,rs=2)
    cmds.rowLayout(nc=3)
    cmds.radioButtonGrp('sdkShowTypeRBG_br',cw=[[1, 40]],nrb=2,sl=2,l1=u'All',l2=u'User',cc=self.loadDirverAttr)
    cmds.checkBox('sdkShowTypeCB_br',w=100,l=u'Only Float',v=True)
    cmds.checkBox('sdkMirrorCB_br',l=u'Mirror SDK',v=True)
    cmds.rowLayout('sdkDefineRL_br',p='sdkDefineCL_br',nc=2,adj=1)
    cmds.columnLayout(adj=True)
    cmds.treeView('sdkDriverAttrListTV_br',h=115,scc=self.driverAttrSelectChange)
    cmds.columnLayout(p='sdkDefineRL_br',h=117,adj=True,rs=2)
    cmds.button(w=80,h=20,l=u'New',c=self.newDriverAttr)
    cmds.button(w=80,h=20,l=u'Delete',c=self.deleteDriverAttr)
    cmds.button(w=80,h=20,l=u'Transfer',c=self.transferSdk)
    cmds.rowLayout(p='sdkDefineCL_br',nc=2,adj=1)
    cmds.floatSliderGrp('sdkDriverAttrValFSG_br',cw=[[1, 60]],adj=2,f=True,max=1.0,pre=2,cc=self.driverValueSelectChange,dc=self.driverValueSelectChange)
    cmds.columnLayout(adj=True)
    cmds.button(w=80,h=20,l=u'Reset All',c=self.resetDriverListToZero)
    cmds.button('sdkDefineB_br',p='sdkDefineCL_br',h=30,l=u'Redefine',c=self.redefineSdk)
    cmds.columnLayout('bsMainCL_br',p='mainTL_br',adj=True)
    cmds.frameLayout('bsOptionFRL_br',cll=False,l=u'Mesh Info',mh=2,mw=2)
    cmds.columnLayout(adj=True)
    cmds.floatFieldGrp('bsIgnoreDisTFG_br',cw=[[1, 70]],l=u'Ignore Dis:',nf=1,pre=4,v1=0.01)
    cmds.radioButtonGrp('bsMirrorAxisRBG_br',cw=[[1, 70], [2, 70], [3, 70], [4, 70]],nrb=3,sl=1,l=u'Mirror Axis:',l1=u'X',l2=u'Y',l3=u'Z')
    cmds.textFieldButtonGrp('bsSkinMeshTFG_br',cw=[[1, 70]],adj=2,l=u'Skin Mesh:',ed=False,bl=u'Load',bc=self.CrtModule.setSkinMesh)
    cmds.frameLayout('bsDriverFRL_br',p='bsMainCL_br',cll=False,l=u'Driver Info List',mh=2,mw=2)
    cmds.columnLayout('bsDriverCL_br',adj=True,rs=2)
    cmds.paneLayout('paneLayout1_br',cn=u'vertical2')
    cmds.columnLayout(adj=True,rs=2)
    cmds.radioButtonGrp('bsDriverShowTypeRBG_br',cw=[[1, 40], [2, 40]],nrb=2,sl=2,l1=u'All',l2=u'Influence',cc=self.CrtModule.updateDriverList)
    cmds.treeView('bsDriverAttrList_br',h=180,scc=self.CrtModule.driverListSelectChange,cmc=self.CrtModule.updateDriverList)
    cmds.floatSliderGrp('bsDriverValueFSG_br',en=False,w=50,vis=False,cw=[[1, 50]],adj=2,f=True)
    cmds.columnLayout(p='paneLayout1_br',adj=True,rs=2)
    cmds.radioButtonGrp('bsDrivenShowTypeRBG_br',cw=[[1, 40], [2, 40]],nrb=2,sl=2,l1=u'All',l2=u'Influence',cc=self.CrtModule.loadDrivenToUI)
    cmds.treeView('bsDrivenBsList_br',h=180,scc=self.CrtModule.drivenListSelectChange)
    cmds.popupMenu(p='bsDrivenBsList_br')
    cmds.menuItem(l=u'Fix SDK',c=self.CrtModule.fixBSDriverAttr)
    cmds.menuItem(d=True)
    cmds.menuItem(l=u'Mirror BlendShape',c=self.CrtModule.mirrorBlendShape)
    cmds.menuItem(d=True)
    cmds.menuItem(l=u'Delete BlendShape',c=self.CrtModule.deleteBlendShape)
    cmds.floatSliderGrp('bsDrivenValueFSG_br',w=50,cw=[[1, 50]],adj=2,f=True,min=0.0,max=1.0,pre=3,cc=self.CrtModule.drivenValueChange,dc=self.CrtModule.drivenValueDrag)
    cmds.button('bsEnterModifyB_br',p='bsDriverCL_br',en=False,h=50,l=u'Enter Modify Mode',c=self.enterModifyMode)
    cmds.button('bsExistsModifyB_br',p='bsDriverCL_br',h=50,vis=False,l=u'Finally Modify',c=self.exitModifyMode)
    cmds.columnLayout('toolsMainCL_br',p='mainTL_br',adj=True)
    cmds.tabLayout('mainTL_br',e=1,tli=[[1, u'Rigging'], [2, u'SDK'], [3, u'CorrectBS'], [4, u'Tools']])
    cmds.showWindow('sdd_BodyRigging_br')


def BodyRiggingUI(rootPath):
    global BodyRiggingModule
    BodyRiggingModule=BBodyRigging(rootPath)
    BodyRigging(BodyRiggingModule)


BodyRiggingModule=BBodyRigging('C:/Users/Administrator/Desktop/sdd_bodyRigging/')
BodyRigging(BodyRiggingModule)
self=BodyRiggingModule
self.buildRigging
