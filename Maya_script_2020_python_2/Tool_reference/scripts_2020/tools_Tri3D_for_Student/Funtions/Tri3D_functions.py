############################################################################################################

###############################
###############################
                ###
                ###
                ###
                ###             #######################       ###          ##########        ##########
                ###             #######################       ###           #########        ###########
                ###             ###                 ###       ###                  ##        ##        ##
                ###             ###                 ###       ###                 ##         ##          ##
                ###             ###                 ###       ###            ########        ##          ##
                ###             ###                 ###       ###                   ##       ##         ##
                ###             ###                 ###       ###                  ##        ##        ##
                ###             ###                 ###       ###          ########          ##########

########### " Contacts with me : info.tri3d@gmail.com "
########### " Gumroad : https://phamtri.gumroad.com/"
########### " Copyright by Tri 3D "
########### " Thanks for you !!! "


import maya.cmds as tri
import maya.cmds as mc
import maya.mel as mel
import webbrowser
from PySide2 import QtGui



################################################################
driven_obj =""
driver_obj =""

cl_back = 1
cl_grey = 3
cl_darkRed = 4
cl_darkBlue = 6
cl_darkGreen = 7
cl_purple = 9
cl_brown = 10 
cl_red = 13
cl_lightGreen = 14
cl_while = 16
cl_yellow = 17
cl_lightBlue = 18
cl_pink = 20
cl_lightOrange = 21
cl_midnightGreen = 23 
cl_darkOrange = 24

def reName(*arg):
	newName = tri.textField("newName", query=True, text=True)
	objects = tri.ls(selection=True)
	for i in objects:
		tri.rename(i, newName)
#newName = tri.textField("newName", edit=True, text="")                           

               
def frontName(*arg):
     #selected_objects = tri.ls(selection=True)
	frontTextField = tri.textField("frontName", query=True, text=True)
	objects = tri.ls(selection=True)
	for i in objects:
		newNameF= frontTextField + i
		tri.rename(i, newNameF)
          
    #frontTextField = tri.textField("frontName", edit=True, text="")                           
def backName(*arg):
     #selected_objects = tri.ls(selection=True)
	backTextField = tri.textField("backName", query=True, text=True)
	objects = tri.ls(selection=True)
	for i in objects:
		newNameB= i + backTextField
		tri.rename(i, newNameB)
#backTextField = tri.textField("backName", edit=True, text="")                           

def pasterdelete(*arg):
     mel.eval("""
     searchReplaceNames "pasted__" "/" "hierarchy";
              """)
     
def deleteImportName(*arg): 
     mel.eval("""
     treeViewChangeSelectCallback;
     namespaceEditCmd add namespaceEditor|namespaceEditorForm|treeView1;
     statusLineUpdateInputField;
     treeViewChangeSelectCallback;
     namespaceEditCmd add namespaceEditor|namespaceEditorForm|treeView1;
     statusLineUpdateInputField;
              """)

################################################################ connect options

def Node(*arg):
    tri.NodeEditorWindow()
def connectEditor(*arg):
    tri.ConnectionEditor()
def setdrivenkey(*arg):
    tri.SetDrivenKey()
def addinfluence(*arg):
    tri.AddInfluenceOptions()
def addattribute(*arg):
    tri.AddAttribute()
def channelcontrol(*arg):
    tri.ChannelControlEditor()
def jointSizeOptions(*arg):
    tri.JdsWin()
def TextureViewWindow(*arg):
     tri.TextureViewWindow()
def graphEditor(*arg):
     tri.GraphEditor()
def jointTools(*arg):    
     tri.JointTool()
def jointMirror(*arg):    
     tri.MirrorJointOptions()
def CreateLattice(*arg):    
     tri.CreateLattice()
def CopySkinWeights(*arg):    
     tri.CopySkinWeights()
def SelectHierarchy(*arg): 
     tri.SelectHierarchy()
def CreateBlendShapeOptions(*arg): 
     tri.CreateBlendShapeOptions()
def CreateBlendShape(*arg): 
     tri.CreateBlendShape()
def freezeOptions(*arg): 
     tri.FreezeTransformationsOptions()
def ParentConstraintOptions(*arg): 
     tri.ParentConstraintOptions()
def ScaleConstraintOptions(*arg): 
     tri.ScaleConstraintOptions()
def OrientConstraint(*arg): 
     tri.OrientConstraintOptions()
def AimConstraint(*arg): 
     tri.AimConstraintOptions()
def PointConstraint(*arg): 
     tri.PointConstraintOptions()
def PoleVectorConstraint(*arg): 
     tri.PoleVectorConstraintOptions()
def orientJoint(*arg): 
     tri.OrientJointOptions()
def PencilCurveTool(*arg): 
     tri.PencilCurveTool()
def EPCurveTool(*arg): 
     tri.EPCurveTool()
def createCircle(*arg): 
     tri.circle( nr=(0, 1, 0), r=3)[0]
def SmoothBindSkin(*arg):
     tri.SmoothBindSkinOptions()
def DetachSkin(*arg):
     tri.DetachSkin()

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
     tri.CombinePolygons()
def SeparatePolygon(*arg):
     tri.SeparatePolygon()

     
def Otz(*arg): 
     mel.eval("""
     OptimizeScene;
     cleanUpScene 1;
              """)



################################################################ rigs

################################################################### translations

def freezeTrans(*arg):
     #tri.FreezeTransformations()
     selections = tri.ls(selection=True)
     for obj in selections:
          tri.makeIdentity(selections, apply=True)
def resetPivot(*arg):
     tri.ResetTransformations()
def centerPivot(*arg):
     tri.CenterPivot()
def deleteHistory(*arg):
     selections = tri.ls(selection=True)
     for obj in selections:
          tri.DeleteHistory(selections, apply=True)
def MatchTransform(*arg):
     tri.MatchTransform()

def unFreezeTrans(*arg):
     selections = tri.ls(selection=True)
     for obj in selections:
          worlds = tri.listRelatives(obj, parent=True)
          if worlds:
               tri.parent(obj, world=True)
               tri.makeIdentity(obj, apply=True, t=True)
               inPosition = tri.xform(obj, query=True, rp=True, ws=True)
               rsPosition = [inPosition[0]*-1, inPosition[1]*-1, inPosition[2]*-1]
               tri.xform(obj, t=rsPosition, ws=True)
               tri.makeIdentity(obj, apply=True, t=True)
               tri.xform(obj, t=inPosition, ws=True)
               tri.parent(obj, worlds=True)
          else:
               tri.makeIdentity(obj, apply=True, t=True)
               inPosition = tri.xform(obj, query=True, rp=True, ws=True)
               rsPosition = [inPosition[0]*-1, inPosition[1]*-1, inPosition[2]*-1]
               tri.xform(obj, t=rsPosition, ws=True)
               tri.makeIdentity(obj, apply=True, t=True)
               tri.xform(obj, t=inPosition, ws=True)

################################################################### controllers
def lockandhide(*arg):
    selected_attributes = tri.channelBox("mainChannelBox", query=True, selectedMainAttributes=True)
    selected_objects = tri.ls(selection=True)
    for obj in selected_objects:
        for attr in selected_attributes:
            tri.setAttr(obj + "." + attr, lock=True, keyable=False)

def create2Ctrl(*arg):
    # select point object 
    selected_objects = tri.ls(selection=True)
    scale_value = float(tri.textField("scaleTextField", query =True, text=True))
    
    for obj in selected_objects:
        pivot_position = tri.xform(selected_objects, query=True, worldSpace=True, rotatePivot=True)
        
        # create grp 1
        group = tri.group( empty=True, name= obj + '_Main_Grp')
        tri.xform(group, worldSpace=True, translation=pivot_position)
        
        # create ctrl 1
        controller = tri.circle( nr=(0, 1, 0), r=3, name= obj + '_Main_Ctrl')[0]
        tri.xform(controller, worldSpace=True, translation=pivot_position)
        tri.parent(controller, group)
        
        # creat grp 2
        child_group = tri.group(empty=True, name=obj + '_Core_Grp')
        tri.xform(child_group, worldSpace=True, translation=pivot_position)
        tri.setAttr(controller + ".scale", scale_value, scale_value, scale_value)
        tri.parent(child_group, controller)
        
        # creat ctrl 2 in grp 2
        inner_controller = tri.circle(nr=(0, 1, 0), r=2, name=obj + '_Core_Ctrl')[0]
        tri.xform(inner_controller, worldSpace=True, translation=pivot_position)
        tri.setAttr(inner_controller + ".scale", scale_value, scale_value, scale_value)
        tri.parent(inner_controller, child_group)
        
        # creat joint in ctrl 2
        joint = tri.joint(name=obj + '_jnt')
        tri.xform(joint, worldSpace=True, translation=pivot_position)

           
def create1Ctrl(*arg):
    selected_objects = tri.ls(selection=True)
    scale_value = float(tri.textField("scaleTextField", query =True, text=True))
    for obj in selected_objects:
        pivot_position = tri.xform(selected_objects, ws=True, query=True, rotatePivot=True)
        
        # create grp 
        group= tri.group(empty=True, name= obj +'_Main_Grp')
        tri.xform(group, ws=True, translation=pivot_position)


        #creat Ctr
        controller = tri.circle(nr=(0, 1, 0), r=3, name= obj +'_Main_Ctrl')[0]
        tri.xform(controller, ws=True, translation=pivot_position)
        tri.setAttr(controller + ".scale", scale_value, scale_value, scale_value)
        tri.parent(controller, group)

        # create joint
        joint = tri.joint(name=obj + '_jnt')
        tri.xform(joint, ws=True, translation=pivot_position)
        tri.parent(joint, controller)

def create1Ctrlparentobj(*arg):
    selected_objects = tri.ls(selection=True)
#     scale_value = float(tri.textField("scaleTextField", query =True, text=True))
    for obj in selected_objects:
        pivot_position = tri.xform(selected_objects, ws=True, query=True, rotatePivot=True)
        
        # create grp 
        joint = tri.joint(name=obj + '_jnt')
        tri.xform(joint, ws=True, translation=pivot_position)
        tri.parent(joint, world=True)

def ctrlIn(*arg):
    selected_objects = tri.ls(selection=True)
    scale_value = float(tri.textField("scaleTextField", query =True, text=True))

    #parent_objects = tri.checkBox("Parent", query=True, value=True)
    for obj in selected_objects:
        pivot_position = tri.xform(selected_objects, ws=True, query=True, rotatePivot=True)
        
        # create grp 
        group= tri.group(empty=True, name= obj +'_Main_Grp')
        tri.xform(group, ws=True, translation=pivot_position)

        #creat Ctr
        controller = tri.circle(nr=(0, 1, 0), r=3, name= obj +'_Main_Ctrl')[0]
        tri.xform(controller, ws=True, translation=pivot_position)
        tri.parent(controller, group)
        tri.setAttr(group + ".scale", scale_value, scale_value, scale_value)
        tri.parent(obj, controller)

        #if parent_objects:
            #tri.button(label="parentCtrl", command=lambda obj=obj, controller=controller: tri.parent(obj, controller)) 
def ctrlInB(*arg):
    selected_objects = tri.ls(selection=True)
    scale_value = float(tri.textField("scaleTextField", query =True, text=True))

    #parent_objects = tri.checkBox("Parent", query=True, value=True)
    for obj in selected_objects:
        pivot_position = tri.xform(selected_objects, ws=True, query=True, rotatePivot=True)
        
        # create grp 
        group= tri.group(empty=True, name= obj +'_Main_Grp')
        tri.xform(group, ws=True, translation=pivot_position)

        #creat Ctr
        controller = tri.spaceLocator(name= obj +'_Main_Ctrl')[0]
        tri.xform(controller, ws=True, translation=pivot_position)
        tri.parent(controller, group)
        tri.setAttr(group + ".scale", scale_value, scale_value, scale_value)
        tri.parent(obj, controller)            
################################################################ 
def add_color_attribute(*arg):    
    selected_objects = tri.ls(selection=True)
    for obj in selected_objects:       
        tri.addAttr(selected_objects, longName='Color', attributeType='long', min=1, max=10, keyable=True)


def add_blend_attribute(*arg):    
    selected_objects = tri.ls(selection=True)
    for obj in selected_objects:   
        tri.addAttr(selected_objects, longName='Blendshape', attributeType='float', min=1, max=10, keyable=True)    

def groupobj(*arg):
    selObj = mc.ls(sl=True)
    for all in selObj:
        grp = mc.group(em=True)
        rnm_grp = mc.rename(grp,all + "_grp")
        mc.parent(rnm_grp,all)

        mc.setAttr(rnm_grp + ".tx", 0)
        mc.setAttr(rnm_grp + ".ty", 0)
        mc.setAttr(rnm_grp + ".tz", 0)
        mc.setAttr(rnm_grp + ".rx", 0)
        mc.setAttr(rnm_grp + ".ry", 0)
        mc.setAttr(rnm_grp + ".rz", 0)
        mc.setAttr(rnm_grp + ".sx", 1)
        mc.setAttr(rnm_grp + ".sy", 1)
        mc.setAttr(rnm_grp + ".sz", 1)

        mc.delete(mc.parentConstraint(all,rnm_grp))

        mc.ungroup(all)

        mc.parent(all,rnm_grp)

        mc.makeIdentity(all, apply=True, t=True, r=True, s=True)
        
################################################################ copyRight
def run_web(*arg):
    webbrowser.open("https://help.autodesk.com/view/MAYAUL/2019/ENU/?guid=__CommandsPython_index_html")

def openWebMessFB(*args):
    webpage_url = "https://www.facebook.com/trithuck/"

    webbrowser.open(webpage_url)
def openWebPageFB(*args):
    webpage_url = "https://www.facebook.com/trithuck/"

    webbrowser.open(webpage_url)    
def openWebgumroad(*args):
    webpage_url = "https://phamtri.gumroad.com/"
    webbrowser.open(webpage_url)

def openWebRiggingSlide(*args):
    webpage_url = "https://docs.google.com/document/d/1y65pZtAQbmDMrDfu6240hO__pPr8v_o70PwRqKEm4-c/edit"
    webbrowser.open(webpage_url)

def openWebRigging(*args):
    webpage_url = "https://www.udemy.com/user/tri-3d-advanced/"
    webbrowser.open(webpage_url)
        
def openGmail(*args):
     webpage_url = "https://mail.google.com/mail/u/0/#inbox?compose=VpCqJRzBSwJKQztWDTJMgbKRMktKhpdTjnmjtwdFzGMWVZpjZxFLTGJbwcjZkgttCcFklgb"
     webbrowser.open(webpage_url)

def update_tools(*args):
     webpage_url = "https://phamtri.gumroad.com/l/hpouk?layout=profile"
     webbrowser.open(webpage_url)
def user_manual(*args):
     webpage_url = "https://www.youtube.com/watch?v=pAq5d0ARenA&list=PLLUiXehMlfsAw41PY1dSIRtbXc15vtW0s"
     webbrowser.open(webpage_url)

def copyEmail(*args):
    text_to_copy = "info.tri3d@gmail.com"
    clipboard = QtGui.QGuiApplication.clipboard()
    clipboard.setText(text_to_copy)
    tri.warning("Copy : info.tri3d@gmail.com to clipboard")
    tri.confirmDialog(title='Copy_Email', message="Copy Email done !   \n\n         UwU")

################################################################ color line objects

def redColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_red)
               tri.setAttr(curve + ".overrideRGBColors", False)
                 
def pinkColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_pink)
               tri.setAttr(curve + ".overrideRGBColors", False)


def yellowColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_yellow)
               tri.setAttr(curve + ".overrideRGBColors", False)

def blueLColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_lightBlue)
               tri.setAttr(curve + ".overrideRGBColors", False)

def greenColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_lightGreen)
               tri.setAttr(curve + ".overrideRGBColors", False)

def whileColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_while)
               tri.setAttr(curve + ".overrideRGBColors", False)


def blueColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_darkBlue)
               tri.setAttr(curve + ".overrideRGBColors", False)

def purpleColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_purple)
               tri.setAttr(curve + ".overrideRGBColors", False)

def blackColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_back)
               tri.setAttr(curve + ".overrideRGBColors", False)


def greyColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_grey)
               tri.setAttr(curve + ".overrideRGBColors", False)

def cl_brownColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_brown)
               tri.setAttr(curve + ".overrideRGBColors", False)

def cl_darkRedColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_darkRed)
               tri.setAttr(curve + ".overrideRGBColors", False)

def cl_lightOrangeColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_lightOrange)
               tri.setAttr(curve + ".overrideRGBColors", False)

def cl_midnightGreenColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_midnightGreen)
               tri.setAttr(curve + ".overrideRGBColors", False)

def cl_darkBlueColorCtrl(*arg):
     selected_curves = tri.ls(selection=True, dag=True, shapes=True)
     if selected_curves:
          for curve in selected_curves:
               tri.listRelatives(curve, shapes=True)
               tri.setAttr(curve + ".overrideEnabled", True)
               tri.setAttr(curve + ".overrideColor", cl_darkBlue)
               tri.setAttr(curve + ".overrideRGBColors", False)

def refillcolorctrl(*arg):
     allObjs = tri.ls(sl=True)
     for obj in allObjs:
            shapes = tri.listRelatives(obj, shapes=True)
            for shape in shapes:
                 tri.setAttr("{0}.overrideEnabled".format(shape), False)
                
def holdOut(*arg):
     selected_objects = tri.ls(sl=True)
     for obj in selected_objects:
        holdout_state = tri.getAttr(obj + ".holdOut")
        tri.setAttr(obj + ".holdOut", not holdout_state)


################ move model to vertex ########
def button1_select_obj(*args):
    selected_mesh = tri.ls(selection=True, type='transform')
    if selected_mesh:
        tri.textField("move_obj_to_vertex", edit=True, text=selected_mesh[0])
    else:
        tri.textField("move_obj_to_vertex", edit=True, text='')

def button2_move_obj(*args):
    target_vertex = tri.ls(selection=True, flatten=True)
    if not target_vertex:
        tri.warning("Select vertex .")
        return

    source_mesh_name = tri.textField("move_obj_to_vertex", query=True, text=True)
    if not source_mesh_name:
        tri.warning("Select mesh.")
        return

    duplicate_mesh = tri.duplicate(source_mesh_name)[0]
    position = tri.pointPosition(target_vertex[0], world=True)
    tri.move(position[0], position[1], position[2], duplicate_mesh)
    if button2_move_obj:
        tri.textField("move_obj_to_vertex_comp", edit=True, text="Move !")







