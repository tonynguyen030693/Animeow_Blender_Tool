###############################################################################
#
# Copyright (c) 1988-2013 CGCG Inc.
# All Rights Reserved.
#
# This file contains unpublished confidential and proprietary
# information of CGCG Inc.  The contents of this file
# may not be copied or duplicated, in whole or in part, by any
# means, electronic or hardcopy, without the express prior
# written permission of CGCG Inc.
#
#    $HeadURL: Reticle.py $
#    $Revision: 0ce5627ec9f1 $
#    $Author: indigo $
#    $Date: 2017/01/19 07:34:32 $
#
###############################################################################

import maya.cmds as mc
import maya.mel as mel
import os
import datetime
import json
from xml.dom.minidom import *
from ast import literal_eval

class Reticle():
    def __init__(self):
        ''''''
        self.reticleName = 'Slate'
        self.reticleShapeName = 'SlateShape'
        self.displaySafeAction = 0
        self.displaySafeTitle = 0
        self.currentProject = 'CGCG'
        self.currentStage = 'blocking'
        self.reset = 1
        self.textScale = 0
        
        self.gAttr = ['textScale']
        
        self.baseAttr = ['visibility', 'drawingEnabled', 'template', 'enableTextDrawing',
                         'enableOrtho', 'focalLengthFloating', 'framePadding', 'maximumDistance', 'dateFormat']
        
        self.filmBackAttr = ['displayFilmGate', 
                             'horizontalFilmAperture', 'verticalFilmAperture',
                             'horizontalSafeAction', 'verticalSafeAction',
                             'horizontalSafeTitle', 'verticalSafeTitle',
                             'filmGateColor', 'filmGateTrans', 
                             'displaySafeAction', 'displaySafeTitle']
        
        self.projGateAttr = ['displayProjGate', 
                             'horizontalProjectionGate', 'verticalProjectionGate',
                             'projGateColor', 'projGateTrans']
        
        self.panScanAttr = ['panScanDisplayMode', 'panScanAspectRatio',
                            'panScanRatio', 'panScanOffset', 
                            'panScanMaskColor', 'panScanMaskTrans', 
                            'panScanLineColor', 'panScanLineTrans',
                            'panScanDisplaySafeAction', 'panScanDisplaySafeTitle']
        
        self.padAttr = ['usePad', 'padAmountX', 'padAmountY', 'padDisplayMode', 
                        'padMaskColor', 'padMaskTrans',
                        'padLineColor', 'padLineTrans']
        
        self.optionAttr = ['miscTextColor', 'miscTextTrans',
                           'lineColor', 'lineTrans', 
                           'displayLineH', 'displayLineV', 
                           'displayThirdsH', 'displayThirdsV', 
                           'displayCrosshair', 'hideLocator',
                           'useSpReticle', 'useOverscan', 
                           'driveCameraAperture', 'maximumDistance']
        
        self.aspectRatioAttr = ['displayMode', 'aspectRatio', 'aspectDisplaySafeAction', 'aspectDisplaySafeTitle', 'aspectLineColor', 'aspectMaskTrans', 'aspectLineTrans']
        
        self.textAttr = ['textFont', 'textType', 'textStr', 'textVAlign', 'textAlign', 'textPos', 'textPosRel', 'textLevel', 'textARLevel', 'textColor', 'textTrans', 'textSize', 'textScale', 'textLabel', 'textLabelStr']               
        
    def getAppDir(self):
        return os.path.split(__file__)[0].replace('/python', '')
        
    def getProject(self):
        #return 'TEST'
        if 'CG_PROJECT' in os.environ.keys():
            return os.environ['CG_PROJECT']
        else:
            return 'CGCG'
    
    def createReticle(self, project='CGCG'):
        self.setEnv()
        self.project = project
        if not mc.objExists(self.reticleName):
            mc.createNode('transform', n=self.reticleName)
            if not mc.objExists(self.reticleShapeName):
                mc.createNode('CgSlate', n=self.reticleShapeName, p=self.reticleName)
                
    def setEnv(self):
        #Frame Range
        os.environ['FS'] = '%d'%mc.playbackOptions(q=True, min=True)
        os.environ['FE'] = '%d'%mc.playbackOptions(q=True, max=True)
        os.environ['FPAD'] = '%d'%0
        os.environ['ORTHO_EN'] = '%d'%1
        
        #Shot Name
        fileName = mc.file(q=True, ns=True)
        os.environ['SHOT'] = fileName
        
    def removeReticle(self):
        if mc.objExists(self.reticleName):
            mc.delete(self.reticleName)
                
    def setDefault(self, customXML=None):
        #self.setEnv()
        mc.setAttr('%s.tx'%self.reticleName, lock=True, keyable=False, channelBox=False)
        mc.setAttr('%s.ty'%self.reticleName, lock=True, keyable=False, channelBox=False)
        mc.setAttr('%s.tz'%self.reticleName, lock=True, keyable=False, channelBox=False)
        
        mc.setAttr('%s.drawingEnabled'%self.reticleShapeName, 1)
        mc.setAttr('%s.displaySafeAction'%self.reticleShapeName, self.displaySafeAction)
        mc.setAttr('%s.displaySafeTitle'%self.reticleShapeName, self.displaySafeTitle)
        
        if mc.objExists(self.reticleName):
            self.reset = 1
            if mel.eval('attributeExists "allowReset" "%s"'%self.reticleShapeName):
                self.reset = mc.getAttr('%s.allowReset'%self.reticleShapeName)
                
            if self.reset:
                # Set first aspect ratio
                mc.setAttr('%s.aspectRatios[0].aspectRatio'%self.reticleShapeName, 1.7777778)
                mc.setAttr('%s.aspectRatios[0].displayMode'%self.reticleShapeName, 0)
                
                #self.setAttr('%s.aspectRatios[0].aspectRatio'%self.reticleShapeName, 1.7777778)
                #self.setAttr('%s.aspectRatios[0].displayMode'%self.reticleShapeName, 0)
                
                #Set reticle to template mode
                mc.setAttr('%s.template'%self.reticleShapeName, 1)
                
                hfa = 0.961;        # red
                vfa = 0.539;        # red
                
                # safe multipliers
                hsa = hfa * 0.6747;
                vsa = vfa * 0.8991;
                hst = hfa * 0.5990;
                vst = vfa * 0.8012;
                
                # filmback attributes
                
                mc.setAttr('%s.horizontalFilmAperture'%self.reticleShapeName, hfa)
                mc.setAttr('%s.verticalFilmAperture'%self.reticleShapeName, vfa)
                mc.setAttr('%s.horizontalSafeAction'%self.reticleShapeName, hsa)
                mc.setAttr('%s.verticalSafeAction'%self.reticleShapeName, vsa)
                mc.setAttr('%s.horizontalSafeTitle'%self.reticleShapeName, hst)
                mc.setAttr('%s.verticalSafeTitle'%self.reticleShapeName, vst)
                
                if mel.eval('attributeExists "%s" %s'%('filmGateTrans',self.reticleShapeName)):
                    mc.setAttr('%s.filmGateTrans'%self.reticleShapeName, 0.7)
                    
                mc.setAttr('%s.displaySafeAction'%self.reticleShapeName, 0)
                #mc.setAttr('%s.displaySafeTitle'%self.reticleShapeName, 0)
                
                # projection gate attributes
                
                mc.setAttr('%s.displayProjGate'%self.reticleShapeName, 0)        # hide          
                mc.setAttr('%s.horizontalProjectionGate'%self.reticleShapeName, hfa)
                mc.setAttr('%s.verticalProjectionGate'%self.reticleShapeName, vfa)
                
                # pan and scan attributes
                
                mc.setAttr('%s.panScanDisplayMode'%self.reticleShapeName, 0)      #None
                mc.setAttr('%s.panScanRatio'%self.reticleShapeName, 1.33333)      
                mc.setAttr('%s.panScanDisplaySafeAction'%self.reticleShapeName, 0)
                mc.setAttr('%s.panScanDisplaySafeTitle'%self.reticleShapeName, 0)
                
                self.setChannelBox()
                self.cleanLabels()
                self.createLabel(customXML)

    def cleanLabels(self):
        idxList = mc.getAttr('%s.text'%self.reticleShapeName, mi=True)
        if idxList:
            idxList.reverse()
            for idx in idxList:   
                mc.removeMultiInstance('%s.text[%s]'%(self.reticleShapeName, idx))
        
    def setChannelBox(self):
        mc.setAttr('%s.localPositionX'%self.reticleShapeName, cb=0)
        mc.setAttr('%s.localPositionY'%self.reticleShapeName, cb=0)
        mc.setAttr('%s.localPositionZ'%self.reticleShapeName, cb=0)
        mc.setAttr('%s.localScaleX'%self.reticleShapeName, cb=0)
        mc.setAttr('%s.localScaleY'%self.reticleShapeName, cb=0)
        mc.setAttr('%s.localScaleZ'%self.reticleShapeName, cb=0)
        
        mc.setAttr('%s.drawingEnabled'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displaySafeAction'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displaySafeTitle'%self.reticleShapeName, k=1)
        mc.setAttr('%s.filmGateTrans'%self.reticleShapeName, k=1)
        
        mc.setAttr('%s.panScanOffset'%self.reticleShapeName, k=0)
        mc.setAttr('%s.panScanRatio'%self.reticleShapeName, k=0)
        mc.setAttr('%s.panScanDisplayMode'%self.reticleShapeName, k=1)
        mc.setAttr('%s.panScanMaskTrans'%self.reticleShapeName, k=1)
        
        mc.setAttr('%s.displayCrosshair'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displayLineH'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displayLineV'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displayThirdsH'%self.reticleShapeName, k=1)
        mc.setAttr('%s.displayThirdsV'%self.reticleShapeName, k=1)
    
    def setAttr(self, attr, value=None, string=False):
        attr_type = mc.getAttr('%s' % attr, type=True)
        _value = value
        
        if value.startswith('@'):
            _value = value[1:]
            print _value
            _value = _value.format(fs=mc.playbackOptions(q=True, min=True),
                                   fe=mc.playbackOptions(q=True, max=True))
            
        elif value:
            # print type(value), attr_type, attr
            if attr_type in ['string']:
                _value = str(value)
            else:
                _value = literal_eval(value) 
            #print attr, value, type(value), _value
            
        emptyStr = False
        
        cmd = 'if(`objExists \\"%s\\"`)setAttr \\"%s\\" '%(self.reticleShapeName, attr)
        if type(_value).__name__ in ['str', 'unicode']:
            cmd += '-type \\"string\\" \\"%s\\";'%_value
            if len(_value) == 0:
               emptyStr = True
               
        elif type(_value) == list:
            
            if len(_value) == 3:
                #double3
                cmd += '-type \\"double3\\" %s %s %s;'%(_value[0], _value[1], _value[2])
            elif len(_value) == 2:
                
                cmd += '%s %s;'%(_value[0], _value[1])
        else:
            
            cmd += '%s;'%(_value)
            
        if not emptyStr:
            mel.eval('eval "%s"'%cmd)
        
    def createLabel(self, customXML=None):
        self.openXML(customXML)
    
    def openXML(self, customXml=None):
        self.currentProject = self.getProject()
        self.currentSettingFileName = '%s/config/%s.xml'%(self.getAppDir(), self.project)
        #if not os.path.exists(self.currentSettingFileName):
        #    self.currentSettingFileName = '%s/config/%s.xml'%(self.getAppDir(), 'CGCG')
        print '--> Load Reticle Settings :: (%s) %s'%(self.currentProject, self.currentSettingFileName)
        if customXml:
            self.currentSettingFileName = customXml
        dom = parse(self.currentSettingFileName)
        self.handleReticle(dom)
        
    def handleReticle(self, dom):
        reticle = dom.getElementsByTagName('CgReticle')[0]
        
        if 'textScale' in reticle.attributes.keys():
            self.textScale = reticle.attributes['textScale'].value
            
        #handle base attr
        for attr in self.baseAttr:
            if attr in reticle.attributes.keys():
                attrValue = reticle.attributes[attr].value
                if mel.eval('attributeExists "%s" %s'%(attr,self.reticleShapeName)):
                    self.setAttr("%s.%s"%(self.reticleShapeName, attr), attrValue)
                    
        for attr in self.panScanAttr:
            if attr in reticle.attributes.keys():
                attrValue = reticle.attributes[attr].value
                if mel.eval('attributeExists "%s" %s'%(attr,self.reticleShapeName)):
                    self.setAttr("%s.%s"%(self.reticleShapeName, attr), attrValue)
                    
        for attr in self.filmBackAttr:
            if attr in reticle.attributes.keys():
                attrValue = reticle.attributes[attr].value
                if mel.eval('attributeExists "%s" %s'%(attr,self.reticleShapeName)):
                    self.setAttr("%s.%s"%(self.reticleShapeName, attr), attrValue)
        
        self.handleAspects(reticle.getElementsByTagName('AspectRatio'))
        
        self.handleLabels(reticle.getElementsByTagName('Label'))
        
    def handleAspects(self, aspects):
        idx = 0
        for aspect in aspects:
            for attr in self.aspectRatioAttr:
                if attr in aspect.attributes.keys():
                    #print attr
                    attrValue = aspect.attributes[attr].value
                    if attrValue == 'False' or attrValue == '0':
                        attrValue = '0'
                    if attrValue == 'True' or attrValue == '1':
                        attrValue = '1'
                    #print attr, attrValue
                    self.setAttr('%s.aspectRatios[%s].%s'%(self.reticleShapeName, idx, attr), attrValue)
                    #mel.eval('setAttr "%s.aspectRatios[%s].%s" %s'%(self.reticleShapeName, idx, attr, attrValue))    
            idx += 1
            
    def formatValue(self, attrValue):
        show_name = ''
        stage = ''
        
        #Depend on project 
        #if self.currentProject == 'DRAGON':
        
        if len(attrValue):  
            #Custom Frame Range Format
            if '%%FRAMERANGE%%' in attrValue:
                fMin = int(mc.playbackOptions(q=True, min=True))
                fMax = int(mc.playbackOptions(q=True, max=True))
                return attrValue.replace('%%FRAMERANGE%%', '%s-%s'%(fMin, fMax))
            
            # Use @{fs}-{fe} format to format the static string
            if attrValue.startswith('@'):
                return attrValue[1:].format(fs=int(mc.playbackOptions(q=True, min=True)),
                                            fe=int(mc.playbackOptions(q=True, max=True)),
                                            total=(int(mc.playbackOptions(q=True, max=True))-int(mc.playbackOptions(q=True, min=True)) + 1))
                                            
            if '{basename}' in attrValue:
                return attrValue.format(basename=mc.file(q=True, ns=True))
                
            attrValueMap = {}
            if '%(show_name)' in attrValue:
                show_name = '_'.join(mc.file(q=True, ns=True).split('.')[0].split('_')[:4])
                attrValueMap['show_name'] = show_name
                
            if '%(stage_name)' in attrValue:
                fileBase = mc.file(q=True, ns=True).split('.')[0]
                if len(fileBase.split('_')) > 4:
                    stage_name = mc.file(q=True, ns=True).split('.')[0].split('_')[4]
                    attrValueMap['stage_name'] = stage_name
                else:
                    attrValueMap['stage_name'] = ''
            
            if '%(macro)' in attrValue:
                macroFunc = attrValue.split(':')[-1]
                mel.eval('python("import macro.%s");' % macroFunc.split('.')[0])
                return mel.eval('python("macro.%s");' % macroFunc)
                
            #attrValue = attrValue%{'show_name':'%s'%show_name}
            attrValue = attrValue%attrValueMap
            
            # RenderGlobals shot data as json
            if attrValue.startswith('shot_data'):
                render_globals = 'defaultRenderGlobals'
                shot_data_attr = attrValue.split(':')[-1]
                attrValue = ''
                if mc.objExists(render_globals):
                    if mel.eval('attributeExists "shotData" %s'%render_globals):
                        shot_data_str = mc.getAttr('%s.shotData'%render_globals)
                        shot_data = json.loads(shot_data_str)
                        if shot_data_attr in shot_data.keys():
                            attrValue = shot_data[shot_data_attr]
                    
            return attrValue
        else:
            return attrValue
        
    def handleLabels(self, labels):
        idx = 0
        for label in labels:
            textType = label.attributes['textType'].value
            for attr in self.textAttr:
            
                if attr in label.attributes.keys():
                
                    attrValue = '%s'%label.attributes[attr].value
                    attrType = mc.getAttr('%s.text[%s].%s'%(self.reticleShapeName, idx, attr), type=True)
                    
                    if attrType == 'string':
                        #0 : String, 32 : Pass
                        if textType == '0' or textType == '32':
                            #Formating String'
                            attrValue = self.formatValue(attrValue)
                            #attrValue = '\'%s\''%attrValue                           
                        
                    self.setAttr('%s.text[%s].%s'%(self.reticleShapeName, idx, attr) , attrValue)
                    
                    # set default text size for vp2
                    if mel.eval('getApplicationVersionAsFloat') == 2015:
                        self.setAttr('%s.text[%s].textSize'%(self.reticleShapeName, idx) , '18')
                        
            if self.textScale:
                if 'textScale' in mc.listAttr('%s.text'%self.reticleShapeName, leaf=True):
                    mc.setAttr('%s.text[%s].textScale'%(self.reticleShapeName, idx), 1)
                    
            idx += 1
                
    def strToSeq(self, o):
        mel.eval('python("list_obj = %s")' % o)
        o = mel.eval('python("list_obj")')
        return o
        
    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)    
    
    def saveXML(self):
        doc = Document()
        reticle = doc.createElement("CgReticle")
        
        displaySafeAction = 0
        displaySafeTitle = 0
        aspectRatios_displayMode = 0
        aspectRatios_aspectMaskTrans = 0.750
        aspectRatios_aspectLineTrans = 0.000
        enableOrtho = 0
        
        if mel.eval('attributeExists "displaySafeAction" %s'%self.reticleShapeName):    
            if mc.getAttr('%s.displaySafeAction'%self.reticleShapeName):
                displaySafeAction = 1
        reticle.setAttribute('displaySafeAction', '%s'%displaySafeAction)
            
        if mel.eval('attributeExists "displaySafeTitle" %s'%self.reticleShapeName):
            if mc.getAttr('%s.displaySafeTitle'%self.reticleShapeName):
                displaySafeTitle = 1
        reticle.setAttribute('displaySafeTitle', '%s'%displaySafeTitle)
        
        if mel.eval('attributeExists "enableOrtho" %s'%self.reticleShapeName):
            if mc.getAttr('%s.enableOrtho'%self.reticleShapeName):
                enableOrtho = 1
        reticle.setAttribute('enableOrtho', '%s'%enableOrtho)
        
        doc.appendChild(reticle)
        
        idxList = mc.getAttr('%s.aspectRatios'%self.reticleShapeName, mi=True)
        if idxList:
            for idx in idxList:
                attrList = mc.listAttr('%s.aspectRatios[%s]'%(self.reticleShapeName, idx), lf=True, m=True)
                aspectRatio = doc.createElement('AspectRatio')
                aspectRatio.setAttribute('id', '%s'%idx)
                for attr in attrList:
                    if attrList.index(attr) > 0:
                        attrType = mc.getAttr('%s.aspectRatios[%s].%s'%(self.reticleShapeName, idx, attr), type=True)
                        attrValue = mc.getAttr('%s.aspectRatios[%s].%s'%(self.reticleShapeName, idx, attr))
                        
                        if attrType == 'float2' or attrType == 'float3':
                            aspectRatio.setAttribute(attr,'%s'%list(attrValue[0]))
                        else:
                            aspectRatio.setAttribute(attr,'%s'%attrValue)
                            
                        reticle.appendChild(aspectRatio)
        
        idxList = mc.getAttr('%s.text'%self.reticleShapeName, mi=True)
        if idxList:
            
            for idx in idxList:
                attrList = mc.listAttr('%s.text[%s]'%(self.reticleShapeName, idx), lf=True, m=True)
                label = doc.createElement('Label')
                for attr in attrList:
                    
                    if attrList.index(attr) > 0:
                        
                        attrType = mc.getAttr('%s.text[%s].%s'%(self.reticleShapeName, idx, attr), type=True)
                        attrValue = mc.getAttr('%s.text[%s].%s'%(self.reticleShapeName, idx, attr))
                                                
                        if attrType == 'string':
                            label.setAttribute(attr,'%s'%attrValue)
                            
                        elif attrType == 'float2' or attrType == 'float3':
                            
                            label.setAttribute(attr,'%s'%list(attrValue[0]))
                        else:
                            
                            label.setAttribute(attr,'%s'%attrValue)
                            
                        reticle.appendChild(label)
            print doc.toprettyxml(indent="  ")
        
if __name__ == '__main__':
    ret = Reticle()
    #ret.createReticle()
    #ret.setDefault()
    #ret.openXML()
    #ret.saveXML()