import maya.cmds as cmds
import maya.mel as mel
import webbrowser
from PySide2 import QtGui

################################################################    
def reName(*arg):
	newName = cmds.textField("newName", query=True, text=True)
	objects = cmds.ls(selection=True)
	for i in objects:
		cmds.rename(i, newName)
#newName = cmds.textField("newName", edit=True, text="")                           
        
def frontName(*arg):
     #selected_objects = cmds.ls(selection=True)
	frontTextField = cmds.textField("frontName", query=True, text=True)
	objects = cmds.ls(selection=True)
	for i in objects:
		newNameF= frontTextField + i
		cmds.rename(i, newNameF)
          
    #frontTextField = cmds.textField("frontName", edit=True, text="")                           
def backName(*arg):
     #selected_objects = cmds.ls(selection=True)
	backTextField = cmds.textField("backName", query=True, text=True)
	objects = cmds.ls(selection=True)
	for i in objects:
		newNameB= i + backTextField
		cmds.rename(i, newNameB)
#backTextField = cmds.textField("backName", edit=True, text="") 
def pasterdelete(*arg):
     selected = cmds.ls(selection=True)
     for obj in selected:
          mel.eval("""
          searchReplaceNames "pasted__" "/" "hierarchy";
              """)
          mel.eval("""
          searchReplaceNames "pasted__" "/" "selected";
                   """)
################## Model #################
def OptimizeScene(*arg):
    cmds.OptimizeScene()
def filePathRepathWin(*arg):
     mel.eval('filePathRepathWin;')
def cubeAdd(*arg): 
     mel.eval('CreatePolygonCube;')
def sphereAdd(*arg):
     mel.eval('CreatePolygonSphere;')
def cylinderAdd(*arg):
     mel.eval('CreatePolygonCylinder;')
def torusAdd(*arg):
     mel.eval('CreatePolygonTorus;')
def coneAdd(*arg):
     mel.eval('CreatePolygonCone;')
def prismAdd(*arg):
     mel.eval('CreatePolygonPrism;')
def discAdd(*arg):
     mel.eval('CreatePolygonDisc;')
def pyramidAdd(*arg):
     mel.eval('CreatePolygonPyramid;')

def CombinePolygons(*arg):
     cmds.CombinePolygons()

def SeparatePolygon(*arg):
     cmds.SeparatePolygon()

def TextureViewWindow(*arg):
     cmds.TextureViewWindow()

def SelectHierarchy(*arg): 
     cmds.SelectHierarchy()

def CreateBlendShapeOptions(*arg): 
     cmds.ShapeEditor()

def freezeOptions(*arg): 
     cmds.FreezeTransformationsOptions()

def HypershadeWindow(*arg): 
     cmds.HypershadeWindow()

def FilePathEditor(*arg): 
     cmds.FilePathEditor()

def NamespaceEditor(*arg): 
     cmds.NamespaceEditor()

def Import(*arg): 
     cmds.Import()

def ReferenceEditor(*arg): 
     cmds.ReferenceEditor()


def freezeTrans(*arg):
     #cmds.FreezeTransformations()
     selections = cmds.ls(selection=True)
     for obj in selections:
          cmds.makeIdentity(obj, apply=True)
def resetPivot(*arg):
     cmds.ResetTransformations()
def centerPivot(*arg):
     cmds.CenterPivot()
def deleteHistory(*arg):
     selections = cmds.ls(selection=True)
     for obj in selections:
          cmds.DeleteHistory(obj, apply=True)
def MatchTransform(*arg):
     cmds.MatchTransform()

def unFreezeTrans(*arg):
     selections = cmds.ls(selection=True)
     for obj in selections:
          worlds = cmds.listRelatives(obj, parent=True)
          if worlds:
               cmds.parent(obj, world=True)
               cmds.makeIdentity(obj, apply=True, t=True)
               inPosition = cmds.xform(obj, query=True, rp=True, ws=True)
               rsPosition = [inPosition[0]*-1, inPosition[1]*-1, inPosition[2]*-1]
               cmds.xform(obj, t=rsPosition, ws=True)
               cmds.makeIdentity(obj, apply=True, t=True)
               cmds.xform(obj, t=inPosition, ws=True)
               cmds.parent(obj, worlds=True)
          else:
               cmds.makeIdentity(obj, apply=True, t=True)
               inPosition = cmds.xform(obj, query=True, rp=True, ws=True)
               rsPosition = [inPosition[0]*-1, inPosition[1]*-1, inPosition[2]*-1]
               cmds.xform(obj, t=rsPosition, ws=True)
               cmds.makeIdentity(obj, apply=True, t=True)
               cmds.xform(obj, t=inPosition, ws=True)


def PolygonBooleanUnion(*arg):
     cmds.PolygonBooleanUnion()

def MergeToCenter(*arg):
     cmds.MergeToCenter()

def SmoothPolygon(*arg):
     cmds.SmoothPolygon()

def ReducePolygon(*arg):
     cmds.ReducePolygon()

def MirrorPolygonGeometryOptions(*arg):
     cmds.MirrorPolygonGeometryOptions()

def CreatePolygonType(*arg):
    cmds.CreatePolygonType()

def dR_multiCutTool(*arg):
     cmds.dR_multiCutTool()

def MergeVertexTool(*arg):
     cmds.MergeVertexTool()

def DuplicateFace(*arg):
     cmds.DuplicateFace()

def performBevelOrChamfer(*arg):
     cmds.BevelPolygon()

def performBridgeOrFill(*arg):
     cmds.BevelOrChamfer()

def CleanupPolygon(*arg):
     cmds.CleanupPolygon()

def FlipMesh(*arg):
     cmds.FlipMesh()

def AverageVertex(*arg):
     cmds.AverageVertex()

def SetMeshSculptTool(*arg):
     cmds.SetMeshSculptTool()

def SetMeshSmoothTool(*arg):
     cmds.SetMeshSmoothTool()

def SetMeshRelaxTool(*arg):
     cmds.SetMeshRelaxTool()

def SetMeshGrabTool(*arg):
     cmds.SetMeshGrabTool()

def SetMeshPinchTool(*arg):
     cmds.SetMeshPinchTool()

def SetMeshFlattenTool(*arg):
     cmds.SetMeshFlattenTool()

def SetMeshFoamyTool(*arg):
     cmds.SetMeshFoamyTool()





################################################################
################################  About
def openWebMessFB(*args):
    webpage_url = "https://www.facebook.com/messages/t/108516382068518/"

    webbrowser.open(webpage_url)
def openWebPageFB(*args):
    webpage_url = "https://www.facebook.com/profile.php?id=100087409486213"

    webbrowser.open(webpage_url)    
def openWebgumroad(*args):
    webpage_url = "https://phamtri.gumroad.com/"
    webbrowser.open(webpage_url)

def openWebRiggingCause(*args):
    webpage_url = "https://phamtri.gumroad.com/l/basic?layout=profile"
    webbrowser.open(webpage_url)

def openWebRiggingSlide(*args):
    webpage_url = "https://docs.google.com/presentation/d/1ELEz1J8mR2REnp3-We48rX2ARDdkeFXH2o6wSLT8pLs/edit?usp=sharing"
    webbrowser.open(webpage_url)
        
def openGmail(*args):
     webpage_url = "https://mail.google.com/mail/u/0/#inbox?compose=VpCqJRzBSwJKQztWDTJMgbKRMktKhpdTjnmjtwdFzGMWVZpjZxFLTGJbwcjZkgttCcFklgb"
     webbrowser.open(webpage_url)

def copyEmail(*args):
    text_to_copy = "info.tri3d@gmail.com"
    clipboard = QtGui.QGuiApplication.clipboard()
    clipboard.setText(text_to_copy)
    cmds.warning("Copy : info.tri3d@gmail.com to clipboard")
    cmds.confirmDialog(title='Copy_Email', message="Copy Email done !   \n\n         UwU")