import maya.cmds as mc
import maya.mel as mel


mc.pluginInfo("lookdevKit",e = True,autoload = True)
mc.loadPlugin("lookdevKit")

mc.evaluationManager(mode = "off")
mc.optionVar(iv = ("maxImageSizeForSwatchGen",512))
mc.optionVar(fv =("animEdCadenceLineFreq",24))
mc.optionVar(fv = ("timeSliderPlaySpeed",1))
mc.setAttr("hardwareRenderingGlobals.transparencyAlgorithm",5)
mc.setAttr("hardwareRenderingGlobals.textureMaxResolution",512)
mc.optionVar(iv = ("autoSaveEnable",1))
mc.optionVar(iv =("autoSaveDestination",1))
mc.optionVar(sv = ("autoSaveFolder","C:/Users/User/Documents/maya/projects/"))
mc.savePrefs()

