# Embedded file name: D:\PycharmProjects\maya\MG_PreviewTool.py
"""

import MG_PreviewTool
reload(MG_PreviewTool)
MG_PreviewTool.run()

"""
import pymel.core as pm
import os
import subprocess
from time import gmtime, strftime
SET_TIME_UNIT = 'ntsc'
LIST_TIME_UNIT = ['NTSC(30 fps)','Film(24 fps)', 'PAL(25 fps)' ]
TEMP_PREVIEW = 'D:/tempPreview/'

class PreviewTool():

    def __init__(self):
        self.winName = 'previewTool'

    def buildUI(self):
        try:
            pm.deleteUI(self.winName)
        except:
            pass

        with pm.window(self.winName, title='PreView Tool'):
            with pm.frameLayout(label=u'HUD', cll=0, bgc=(0.5, 0.5, 0.5)):
                pm.separator(style='none', h=2)
                with pm.columnLayout(adj=True, rs=5, cat=('both', 5)):
                    self.labelIndexSG = pm.colorIndexSliderGrp(label='Label color:', cw=[(1, 60), (2, 30)], min=1, max=20, value=18, dc=self.setHUDLabelColor)
                    self.fontIndexSG = pm.colorIndexSliderGrp(label='Font color:', cw=[(1, 60), (2, 30)], min=1, max=20, value=18, dc=self.setHUDFondColor)
                pm.separator(style='in', h=2)
                with pm.columnLayout(adj=True, rs=2, cat=('both', 5)):
                    with pm.rowColumnLayout(nc=2, cw=[(1, 75), (2, 170)], cat=[(1, 'both', 2), (2, 'both', 2)]):
                        pm.text(label='Artist Name:')
                        self.artistNameTF = pm.textField(text='')
                    with pm.horizontalLayout():
                        pm.button(label='On', h=30, command=self.onHUD)
                        pm.button(label='Off', h=30, command=self.offHUD)
            with pm.frameLayout(label='Playblast', cll=0, bgc=(0.5, 0.5, 0.5)):
                pm.separator(style='none', h=2)
                with pm.columnLayout(adj=True, rs=2, cat=('both', 5)):
                    with pm.rowColumnLayout(nc=2, cw=[(1, 40), (2, 140)], cat=[(1, 'both', 2), (2, 'both', 2)]):
                        pm.text(label='Time:')
                        self.timeOM = pm.optionMenu(label='', width=70, cc=self.changeTimeSelect)
                        for f in LIST_TIME_UNIT:
                            pm.menuItem('%sItem' % f, label=f, p=self.timeOM)

                pm.separator(style='in', h=2)
                '''
                with pm.columnLayout(adj=True, cat=('both', 5)):
                    self.safeActionCB = pm.checkBox(label='Safe Action', value=1, onc=pm.Callback(self.safeActionVisible, 1), ofc=pm.Callback(self.safeActionVisible, 0))
                    self.ResolutionCB = pm.checkBox(label='Resolution Gate', value=0, onc=pm.Callback(self.setResolutionGate, 1), ofc=pm.Callback(self.setResolutionGate, 0))
                '''
                with pm.columnLayout(adj=True):
                    with pm.rowColumnLayout(nc=4, cw=[(1, 50),
                     (2, 70),
                     (3, 50),
                     (4, 70)], cat=[(1, 'both', 2),
                     (2, 'both', 2),
                     (3, 'both', 2),
                     (4, 'both', 2)]):
                        pm.text(label='Width:')
                        self.widthIF = pm.intField(value=1920)
                        pm.text(label='Height:')
                        self.heightIF = pm.intField(value=1080)
                pm.separator(style='in', h=2)

                with pm.columnLayout(adj=True, rs=2, cat=('both', 5)):
                    self.scaleFSG = pm.floatSliderGrp(label='Scale:', field=True, precision=2, minValue=0.1, maxValue=1, fieldMinValue=0.1, fieldMaxValue=1.0, cw=[(1, 40), (2, 40)], value=1)
                    with pm.horizontalLayout():
                        pm.button(label='Preview', h=30, command=self.aniPreview)
                        pm.button(label='Folder', h=30, command=self.currentScene)
                pm.separator(style='none', h=1)
        pm.window(self.winName, e=True, h=300, width=250)
        self.setDefaultTimeUnit()
        self.setDefaultResolution()
        self.setSafeAction(1)

    def aniPreview(self, *args):
        getScale = self.scaleFSG.getValue()
        setPercent = getScale * 100
        getWidth = self.widthIF.getValue()
        getHeight = self.heightIF.getValue()
        path = pm.sceneName()
        scFullName = os.path.basename(path)
        sceneName = os.path.splitext(scFullName)[0]
        if sceneName[-5:].lower() == '_temp':
            sceneName = sceneName[:-5]
        if sceneName[-3:].lower() == '_ad':
            sceneName = sceneName[:-3]
        fileName = TEMP_PREVIEW + sceneName + '.mov'
        aPlayBackSliderPython = pm.mel.eval('$tmpVar=$gPlayBackSlider')
        soundFile = pm.timeControl(aPlayBackSliderPython, q=True, sound=True)
        try:
            aviFile = pm.playblast(fp=4, format='qt', sound=soundFile, forceOverwrite=True, percent=setPercent, filename=fileName, viewer=0, quality=100, widthHeight=(getWidth, getHeight), compression=u'MPEG-4 \ube44\ub514\uc624')
        except:
            print 'Install Avid Codec First...'
            return

        try:
            qtPath = 'C:\\Program Files (x86)\\QuickTime\\QuickTimePlayer.exe'
            NewFileName = fileName.replace('/', '\\')
            subprocess.Popen([qtPath, NewFileName])
        except:
            print 'No QuickTime Player...'

    def currentScene(self, *args):
        if os.path.isdir(TEMP_PREVIEW):
            arg = ['Explorer', TEMP_PREVIEW.replace('/', '\\')]
        else:
            projPath = pm.workspace.getPath()
            currentPath = projPath / pm.workspace.fileRules['mayaAscii']
            arg = ['Explorer', currentPath.replace('/', '\\')]
        subprocess.call(arg)

    def changeTimeSelect(self, *args):
        selectNum = self.timeOM.getSelect()
        if selectNum == 1:
            self.setTimeUnit(unit='NTSC(30 fps)')
        if selectNum == 2:
            self.setTimeUnit(unit='Film(24 fps)')
        if selectNum == 3:
            self.setTimeUnit(unit='PAL(25 fps)')

    def setDefaultTimeUnit(self):
        pm.currentUnit(time=SET_TIME_UNIT)

    def setDefaultResolution(self):
        Resolution = pm.PyNode('defaultResolution')
        Resolution.width.set(1280)
        Resolution.height.set(720)

    def setTimeUnit(self, unit):
        timeType = unit.partition('(')[0].lower()
        pm.currentUnit(time=timeType)

    def onHUD(self, *args):
        self.setDefaultResolution()
        self.deleteDefaultHUD()
        if self.artistNameTF.getText() == '':
            artistName = os.getenv('USERNAME')
            print artistName
        else:
            artistName = self.artistNameTF.getText()
            print artistName
        self.showHUD(artistName)

    def offHUD(self, *args):
        self.deleteDefaultHUD()
        self.deleteHUD()

    def deleteDefaultHUD(self):
        pm.mel.setSelectDetailsVisibility(False)
        pm.mel.setObjectDetailsVisibility(False)
        pm.mel.setParticleCountVisibility(False)
        pm.mel.setPolyCountVisibility(False)
        pm.mel.setAnimationDetailsVisibility(False)
        pm.mel.setHikDetailsVisibility(False)
        pm.mel.setFrameRateVisibility(False)
        pm.mel.setCurrentFrameVisibility(False)
        pm.mel.setSceneTimecodeVisibility(False)
        pm.mel.setCurrentContainerVisibility(False)
        pm.mel.setCameraNamesVisibility(False)
        pm.mel.setFocalLengthVisibility(False)
        pm.mel.setViewAxisVisibility(False)
        pm.toggleAxis(o=False)

    def deleteHUD(self):
        if pm.headsUpDisplay('frameCounterHUD', exists=True):
            pm.headsUpDisplay('frameCounterHUD', rem=True)
        if pm.headsUpDisplay('artistNameHUD', exists=True):
            pm.headsUpDisplay('artistNameHUD', rem=True)
        if pm.headsUpDisplay('dateNameHUD', exists=True):
            pm.headsUpDisplay('dateNameHUD', rem=True)
        if pm.headsUpDisplay('cameraFocalHUD', exists=True):
            pm.headsUpDisplay('cameraFocalHUD', rem=True)

    def getData(self, *args):
        return strftime('%Y-%m-%d', gmtime())

    def getArtist(self, *args):
        return args[0]

    def getScene(self, *args):
        path = pm.sceneName()
        scFullName = os.path.basename(path)
        scName = os.path.splitext(scFullName)[0]
        if not scName.find('_') == -1 and not scName.split('_')[1] == '':
            validSCName = scName.split('_')[1] + '_' + scName.split('_')[2]
        else:
            validSCName = scName
        if pm.objExists('RENDER_CAM'):
            RENDER_CAM = pm.PyNode('RENDER_CAM')
            focal = str(int(RENDER_CAM.focalLength.get()))
        else:
            focal = '"RENDER_CAM" does not exist.'
            camList = pm.ls(type='camera')
            passList = ['frontShape',
             'perspShape',
             'sideShape',
             'topShape']
            for cam in camList:
                if cam.name() not in passList:
                    if cam.renderable.get():
                        focal = str(int(cam.focalLength.get()))

        return validSCName + ' / ' + focal

    def showHUD(self, userName):
        self.deleteHUD()
        pm.headsUpDisplay('frameCounterHUD', allowOverlap=1, l=u'\u25a0', b=4, s=5, dataFontSize='large', blockSize='large', dataWidth=5, preset='currentFrame')
        pm.headsUpDisplay('artistNameHUD', l=u'\u25a0', allowOverlap=1, b=3, s=5, dataFontSize='large', blockSize='large', command=pm.Callback(self.getArtist, userName), event='timeChanged')
        pm.headsUpDisplay('dateNameHUD', l=u'\u25a0', allowOverlap=1, b=2, s=5, dataFontSize='large', blockSize='large', command=self.getData, event='timeChanged')
        pm.headsUpDisplay('cameraFocalHUD', l=u'\u25a0', allowOverlap=1, b=1, s=5, dataFontSize='large', blockSize='large', command=self.getScene, event='timeChanged')

    def safeActionVisible(self, vis):
        self.setSafeAction(vis)

    def setResolutionGateVisible(self, vis):
        self.setResolutionGate(vis)

    def setSafeAction(self, state):
        perspCam = pm.PyNode('persp')
        perspCam.getShape().displaySafeAction.set(state)
        if pm.objExists('RENDER_CAM'):
            RENDER_CAM = pm.PyNode('RENDER_CAM')
            RENDER_CAM.getShape().displaySafeAction.set(state)
        else:
            camList = pm.ls(type='camera')
            passList = ['frontShape',
             'perspShape',
             'sideShape',
             'topShape']
            for cam in camList:
                if cam.name() not in passList:
                    if cam.renderable.get():
                        cam.displaySafeAction.set(state)

    def setResolutionGate(self, state):
        perspCam = pm.PyNode('persp')
        perspCam.getShape().displayResolution.set(state)
        perspCam.getShape().overscan.set(1.0)
        if pm.objExists('RENDER_CAM'):
            RENDER_CAM = pm.PyNode('RENDER_CAM')
            RENDER_CAM.getShape().displayResolution.set(state)
            RENDER_CAM.getShape().overscan.set(1.0)
        else:
            camList = pm.ls(type='camera')
            passList = ['frontShape',
             'perspShape',
             'sideShape',
             'topShape']
            for cam in camList:
                if cam.name() not in passList:
                    if cam.renderable.get():
                        cam.displayResolution.set(state)
                        cam.overscan.set(1.0)

    def setHUDLabelColor(self, *args):
        value = self.labelIndexSG.getValue()
        pm.displayColor('headsUpDisplayLabels', value, dormant=1)

    def setHUDFondColor(self, *args):
        value = self.fontIndexSG.getValue()
        pm.displayColor('headsUpDisplayValues', value, dormant=1)


def run():
    pt = PreviewTool()
    pt.buildUI()