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


import maya.cmds as tri3d
import os


# link file funtions
import tools_Tri3D_for_Student.Funtions.Tri3D_functions as func
reload(func)
import tools_Tri3D_for_Student.Funtions.Animation.Tri3D_animation as anim
import tools_Tri3D_for_Student.Funtions.Animation.Tri3D_animationFuntions as Funcanim
import tools_Tri3D_for_Student.Funtions.Rigging.Tri3D_rigFunctions as Rig
reload(Rig)
import tools_Tri3D_for_Student.Funtions.Curve.CurveBasic as Cur
import tools_Tri3D_for_Student.Funtions.Rigging.Picker as pk
import tools_Tri3D_for_Student.Funtions.Tri_Tools as tools
import tools_Tri3D_for_Student.Funtions.Rigging.tools as tools2


IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Icons")
dock= ""
################################################################ window functions
def createUI():
    global dock
    if tri3d.window("triWin", exists=True):
        tri3d.deleteUI("triWin")


    triWin = tri3d.window("triWin", title="tools_Tri3D for Student", sizeable=True, menuBar=True, resizeToFitChildren=False, w=250, h=985)
    # tri3d.windowPref("triWin", remove=True, w=250)

    tri3d.menu(l="Modify")
    tri3d.menuItem(l="Freeze Transformations", image= IMAGE_PATH + "/FreezeTransform.png", c=func.freezeOptions )
    tri3d.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )
    # tri3d.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )


    tri3d.menu(l="Display")
    tri3d.menuItem(l="Window", image= IMAGE_PATH + "/jointSize.png", c=windowUi)
    tri3d.menuItem(l="Joint Size", image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions)
    # tri3d.menuItem(l="Test", image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions)

    tri3d.menu(l="About")
    tri3d.menuItem(l="Command Maya", image= IMAGE_PATH + "/mayaIcon.png", c=func.run_web)
    tri3d.menuItem(l="Follow Fanpage", image= IMAGE_PATH + "/LogoGumroad.jpg", c=func.openWebPageFB)
    tri3d.menuItem(l="Khoa hoc Rigging ", image= IMAGE_PATH + "/LogoGumroad.jpg", c=func.openWebRigging)
    tri3d.menuItem(l="Gumroad", image= IMAGE_PATH + "/gumroad.png", c=func.openWebgumroad)
    tri3d.menuItem(l="Contact by Email", image= IMAGE_PATH + "/Gmail_icon.png", c=func.openGmail)
    tri3d.menuItem("info.tri3d@gmail.com", image=IMAGE_PATH + "/copyIcon.png", c=func.copyEmail)
    tri3d.menuItem("Update Version to 2.0", image=IMAGE_PATH + "/updateicon.png", c=func.update_tools)

    # tri3d.menu(l="Course Rigging")
    # tri3d.menuItem(l="Khoa hoc Animation Basic", image= IMAGE_PATH + "/BasicAnimation.png")
    # tri3d.menuItem(l="Khoa hoc Rigging Basic", image= IMAGE_PATH + "/BasicRigging.png", c=func.openWebRiggingSlide)
    # tri3d.menuItem(l="Fanpage", image= IMAGE_PATH + "/LogoGumroad.jpg")
    # tri3d.menuItem(l="Fanpage", image= IMAGE_PATH + "/LogoGumroad.jpg")


################################################################ UI UX
################################################################
    main_layout = tri3d.columnLayout(adjustableColumn=True, h=990)
    tab_layout_main = tri3d.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    tri3d.setParent(tab_layout_main)
    tri3d.scrollLayout("Modify", horizontalScrollBarThickness=500, verticalScrollBarThickness=6000, h=985)
    
    tri3d.textField("frontName", w=250, h=30, placeholderText="Front_", text="")
    tri3d.button(l="Front Name", w=250, c=func.frontName, backgroundColor=[0.284,0.352,0.352])
    tri3d.textField("backName", w=250, h=30, placeholderText="_Back", text="")
    tri3d.button(l="Back Name", w=250, c=func.backName, backgroundColor=[0.284,0.352,0.352])
    tri3d.separator(w=250, h=3, style="in", backgroundColor=[0.284,0.352,0.352])
    tri3d.button(l=" Delete : Pasted__", w=250, c=tools.pasterdelete)



    tri3d.setParent("Modify")
    tri3d.frameLayout("Connect ", w=250, cll=True, cl=False)
    tri3d.rowColumnLayout("Layout1", w=250, nc=4)
    tri3d.button(l="Attribute", c=func.addattribute, w=63)
    tri3d.button(label="Set", c=func.setdrivenkey, w=63)
    tri3d.button(label="Connect", c=func.connectEditor, w=63)
    tri3d.button(label="Node", c=func.Node, w=63)
    tri3d.button(label="Influe", c=func.addinfluence, w=63)
    tri3d.button(label="Group", c=func.groupobj, w=63)
    tri3d.button(label="Lock", c=func.lockandhide, w=63)
    # tri3d.button(label="Color", c=func.add_color_attribute, w=63)
    # tri3d.button(label="Blend", c=func.add_blend_attribute, w=63)
    tri3d.button(l="Channel", c=func.channelcontrol, w=63)



    ########## polygon #################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Polygon_layout", w=250)
    tri3d.frameLayout("Polygon", w=250, cll=False)
    tri3d.rowColumnLayout("Polygon", w=250, nc=6)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCube.png", w=42, h=42, c=tools.cubeAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySphere.png", w=42, h=42, c=tools.sphereAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCylinder.png", w=42, h=42, c=tools.cylinderAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCone.png", w=42, h=42, c=tools.coneAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyDisc.png", w=42, h=42, c=tools.discAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyTorus.png", w=42, h=42, c=tools.torusAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyPrism.png", w=42, h=42, c=tools.prismAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyPyramid.png", w=42, h=42, c=tools.pyramidAdd)

    tri3d.symbolButton(image=IMAGE_PATH + "/polyUnite.png", w=42, h=42, c=tools.CombinePolygons)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySeparate.png", w=42, h=42, c=tools.SeparatePolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBooleansUnion.png", w=42, h=42, c=tools.PolygonBooleanUnion)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyMergeToCenter.png", w=42, h=42, c=tools.MergeToCenter)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySmooth.png", w=42, h=42, c=tools.SmoothPolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyReduce.png", w=42, h=42, c=tools.ReducePolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyMirrorGeometry.png", w=42, h=42, c=tools.MirrorPolygonGeometryOptions)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyType.png", w=42, h=42, c=tools.CreatePolygonType)
    
    tri3d.symbolButton(image=IMAGE_PATH + "/multiCut_NEX32.png", w=42, h=42, c=tools.dR_multiCutTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/weld_NEX32.png", w=42, h=42, c=tools.MergeVertexTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyDuplicateFacet.png", w=42, h=42, c=tools.DuplicateFace)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBevel.png", w=42, h=42, c=tools.performBevelOrChamfer)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBridge.png", w=42, h=42, c=tools.performBridgeOrFill)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCleanup.png", w=42, h=42, c=tools.CleanupPolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyFlip.png", w=42, h=42, c=tools.FlipMesh)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyAverageVertex.png", w=42, h=42, c=tools.AverageVertex)

    ########## sculp #################
    tri3d.setParent("Modify")
    tri3d.frameLayout("Sculpting", w=250, cll=False)
    tri3d.rowColumnLayout("Sculpting", w=250, nc=7)
    tri3d.symbolButton(image=IMAGE_PATH + "/Sculpt.png", w=36, h=36, c=tools.SetMeshSculptTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Smooth.png", w=36, h=36, c=tools.SetMeshSmoothTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Relax.png", w=36, h=36, c=tools.SetMeshRelaxTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Grab.png", w=36, h=36, c=tools.SetMeshGrabTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Pinch.png", w=36, h=36, c=tools.SetMeshPinchTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Flatten.png", w=36, h=36, c=tools.SetMeshFlattenTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Foamy.png", w=36, h=36, c=tools.SetMeshFoamyTool)

    ########## modify #################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Modify_layout", w=250)
    tri3d.frameLayout("Modify", w=250, cll=False)
    tri3d.rowColumnLayout("Modify_row", w=250, nc=7)
    tri3d.symbolButton(image=IMAGE_PATH + "/match.png", w=35, h=35, c=tools.MatchTransform)
    tri3d.symbolButton(image=IMAGE_PATH + "/unfreetransform.png", w=35, h=35, c=tools.unFreezeTrans)
    tri3d.symbolButton(image=IMAGE_PATH + "/menuIconSelect.png", w=35, h=35, c=tools.SelectHierarchy)
    tri3d.symbolButton(image=IMAGE_PATH + "/pivotReset.png", w=35, h=35, c=tools.resetPivot)
    tri3d.symbolButton(image=IMAGE_PATH + "/CenterPivot.png", w=35, h=35, c=tools.centerPivot)
    tri3d.symbolButton(image=IMAGE_PATH + "/FreezeTransform.png", w=35, h=35, c=tools.freezeTrans)
    tri3d.symbolButton(image=IMAGE_PATH + "/deleteHist.png", w=35, h=35, c=tools.deleteHistory)
################################   Functions    #################################
#################################################################################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Functions", w=250)
    tri3d.setParent("Functions")
    tri3d.text(l="Move Object to vertex : " , w=250, h=15, backgroundColor=[0.284,0.352,0.352])
    tri3d.rowColumnLayout("Tools_model", w=250, nc=2)
    tri3d.button(l="Select", w=40, h=20, c=func.button1_select_obj)
    tri3d.textField("move_obj_to_vertex", placeholderText = "Select Model", editable=False, w=250, h=20)
    tri3d.button(l="Move", w=80, h=20, c=func.button2_move_obj)
    tri3d.textField("move_obj_to_vertex_comp", placeholderText = "!!!", editable=False, w=250, h=20)

    ########################## control functions #########################
    tri3d.setParent("Modify")
    tri3d.frameLayout("Controller", w=250, cll=True, cl=False)
    tri3d.columnLayout("Controller_Main", w=250)

    tri3d.setParent("Controller_Main")
    tri3d.rowColumnLayout("Controller_Layout_Rig", w=250, nc=7)
    ButtonLocParent1 = tri3d.textField("scaleTextField", w=35, h=35, ec=func.ctrlIn, placeholderText="_____", text="1")
    tri3d.symbolButton(image=IMAGE_PATH + "/objtoctrl.png",  c=func.ctrlIn, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/add1ctrl.png",  c=func.create1Ctrl, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/add2ctrl.png",  c=func.create2Ctrl, w=35, h=35)
    ButtonLocParent = tri3d.symbolButton(image=IMAGE_PATH + "/Locator.png", w=35, h=35, c=func.ctrlInB)
    tri3d.symbolButton(image=IMAGE_PATH + "/jointadd.png", c=Rig.createJoint, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/jointaddpivot.png", c=func.create1Ctrlparentobj, w=35, h=35)

    tri3d.setParent("Controller_Main")
    tri3d.rowColumnLayout("Edge_to_curve", w=250, nc=7)
    degree_Curve = tri3d.textField("degree_text", w=35, h=25, ec=Cur.edgeToCurve, placeholderText="1 or 3", text="3")
    tri3d.symbolButton(image=IMAGE_PATH + "/Ari_etc.png", c=Cur.edgeToCurve, w=95, h=20)
    tri3d.separator(w=1, h=25, style="in")
    tri3d.text(l="", w=10)
    tri3d.button(l="Scale + ", w=50, c=Rig.scalePoCurve)
    tri3d.text(l="", w=5)
    tri3d.button(l="Scale - ", w=50, c=Rig.scaleNeCurve)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Add attribute", w=250, cll=True, cl=False)
    tri3d.columnLayout("Add_attribute", w=250)
    tri3d.rowColumnLayout("Add_Attr", w=250, nc=5)
    tri3d.textField("Name_Attribute_textField", w=95, placeholderText="Name_Attribute")
    tri3d.text(l="Min :", w=38)
    tri3d.textField("min_value_attribute", w=38, text="1")
    tri3d.text(l="Max :", w=38)
    tri3d.textField("max_value_attribute", w=38)
    tri3d.setParent("Add_attribute")
    tri3d.rowColumnLayout("Add_data_type_set", w=250, nc=3)
    tri3d.textField("data_type_text", w=95, placeholderText="long or float", text="float")
    tri3d.text(l="", w=38)
    tri3d.button(l="Create attribute", w=135, command=tools2.create_attr)


    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Change Color", w=250, cll=True, cl=False)
    tri3d.rowColumnLayout("ChangeColor_Layout", w=250, nc=5)
    tri3d.button(l="Refill",c=func.refillcolorctrl, w=49, backgroundColor=[1,1,1])
    tri3d.canvas(w=50, rgb=[1,0,0], pressCommand=func.redColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0.250,0.078], pressCommand=func.cl_lightOrangeColorCtrl)
    tri3d.canvas(w=50, rgb=[1,1,0], pressCommand=func.yellowColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0.506,0.766], pressCommand=func.pinkColorCtrl)
    tri3d.canvas(w=50, rgb=[0,1,0], pressCommand=func.greenColorCtrl)
    tri3d.canvas(w=50, rgb=[1,1,1], pressCommand=func.whileColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0,1], pressCommand=func.purpleColorCtrl)
    tri3d.canvas(w=50, rgb=[0,1,1], pressCommand=func.blueLColorCtrl)
    tri3d.canvas(w=50, rgb=[0,0,1], pressCommand=func.cl_darkBlueColorCtrl)
    tri3d.canvas(w=50, rgb=[0,0,0], pressCommand=func.blackColorCtrl)
    tri3d.canvas(w=50, rgb=[0.19,0.19,0.19], pressCommand=func.greyColorCtrl)
    tri3d.canvas(w=50, rgb=[0.352,0.116,0.037], pressCommand=func.cl_brownColorCtrl)
    tri3d.canvas(w=50, rgb=[0.53,0.014,0.014], pressCommand=func.cl_darkRedColorCtrl)
    tri3d.canvas(w=50, rgb=[0.085,0.386,0.206], pressCommand=func.cl_midnightGreenColorCtrl)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Curve", w=250, cll=True, cl=True)
    tri3d.columnLayout("Curve_Layout_Main", w=250)
    tri3d.rowColumnLayout("Curve_Layout", w=250, nc=6)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton02.png", w=42, h=42, c=Cur.cubeCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton08.png", w=42, h=42, c=Cur.pringleCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton48.png", w=42, h=42, c=Cur.handCircleCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton11.png", w=42, h=42, c=Cur.handCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton12.png", w=42, h=42, c=Cur.footCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton46.png", w=42, h=42, c=Cur.VerticalSlider)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton47.png", w=42, h=42, c=Cur.handPet)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton03.png", w=42, h=42, c=Cur.arrowTriangle)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton09.png", w=42, h=42, c=Cur.LocatorCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton10.png", w=42, h=42, c=Cur.circleD)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton19.png", w=42, h=42, c=Cur.ccButton19)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton17.png", w=42, h=42, c=Cur.plusCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton23.png", w=42, h=42, c=Cur.circleP)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton27.png", w=42, h=42, c=Cur.rotateCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton28.png", w=42, h=42, c=Cur.axisC)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton29.png", w=42, h=42, c=Cur.arrowCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton32.png", w=42, h=42, c=Cur.circleAround)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton35.png", w=42, h=42, c=Cur.wardCtrl)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton36.png", w=42, h=42, c=Cur.EyeCtrl)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton38.png", w=42, h=42, c=Cur.fourAround)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton40.png", w=42, h=42, c=Cur.ccButton40)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton43.png", w=42, h=42, c=Cur.ccButton43)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccSquare.png", w=42, h=42, c=Cur.squareCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccSlider.png", w=42, h=42, c=Cur.functionsCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccFace.png", w=42, h=42, c=Cur.faceCurve)

    tri3d.setParent("Curve_Layout_Main")
    tri3d.columnLayout("Curve_Layout_cl", w=250, columnAttach = ('left', 5))
    #tri3d.button(l="Combine Shape", w=250)
    tri3d.colorIndexSliderGrp(Rig.ctrlColor, minValue = 1, maxValue = 31, value = 16, columnWidth = (1,60), columnWidth2 = (1, 215),\
                              dragCommand = Rig.hideManipulator, changeCommand = Rig.showManipulator) 
    #tri3d.symbolButton(image=IMAGE_PATH + "/blendShapeEditor.png", w=42, h=42, c=func.ShapeEditor)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Curve Code", w=250, cll=True, cl=True)
    tri3d.columnLayout("Curve_code", w=250)
    tri3d.textField("tx_roundNum_ctt", w=250,text="2", placeholderText="        Select to curve")
    tri3d.scrollField("tx_codeCTL_ctt", w=250, h=50, wordWrap=True)
    tri3d.button(l="Create Code", w=250, c=Cur.createCodeCurve_ctt)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Modify", w=250, cll=True, cl=False)
    tri3d.columnLayout("Modify_Layout", w=250)

    tri3d.setParent("Modify_Layout")
    tri3d.rowColumnLayout("Modify_Layout", w=250, nc=6, backgroundColor=[0.284,0.352,0.352])
    tri3d.symbolButton(image=IMAGE_PATH + "/circle.png", w=40, h=40, c=func.createCircle)
    tri3d.symbolButton(image=IMAGE_PATH + "/pencil.png", w=40, h=40, c=func.PencilCurveTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/curveEP.png", w=40, h=40, c=func.EPCurveTool)
    # tri3d.symbolButton(image=IMAGE_PATH + "/ngSkinTools2ShelfIcon.png", w=40, h=40)
    tri3d.symbolButton(image=IMAGE_PATH + "/textureEditor.png", w=40, h=40, c=func.TextureViewWindow)
    tri3d.symbolButton(image=IMAGE_PATH + "/getGraphEditor.png", w=40, h=40, c=func.graphEditor)
    # tri3d.symbolButton(h=30, w=30, image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions) 
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/kinJoint.png" , c=func.jointTools)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/kinMirrorJoint_S.png" , c=func.jointMirror)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/orientJoint.png", c=func.orientJoint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/smoothSkin.png" , c=func.SmoothBindSkin)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/detachSkin.png" , c=func.DetachSkin)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/copySkinWeight.png" , c=func.CopySkinWeights)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/lattice.png", c=func.CreateLattice)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/parentConstraint.png" , c=func.ParentConstraintOptions)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/orientConstraint.png" , c=func.OrientConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/aimConstraint.png" , c=func.AimConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/posConstraint.png" , c=func.PointConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/scaleConstraint.png" , c=func.ScaleConstraintOptions)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/poleVectorConstraint.png" , c=func.PoleVectorConstraint)
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")

################################################################ Animation
################################################################
    tri3d.setParent(tab_layout_main)
    tri3d.columnLayout("Animation", w=260)
    tri3d.setParent("Animation")
    tri3d.frameLayout("Graph", w=270)
    tri3d.rowColumnLayout("FunctionsKey_Layout", nc=5, w=260, backgroundColor=[0.284,0.352,0.352])
    tri3d.symbolButton(image = IMAGE_PATH +"/ResetKey.png", w=66, h=25, c=Funcanim.resetKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/copyKey.png", w=66, h=25, c=Funcanim.copyKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/pasteKey.png", w=66, h=25, c=Funcanim.pasteKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/deleteKey.png", w=66, h=25, c=Funcanim.cutKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/Picker.png", w=66, h=25, c=pk.animPickerTri3D)

    tri3d.setParent("Animation")
    tri3d.columnLayout("Animation_layout", w=270)
    tri3d.rowColumnLayout("FunctionsGraph_Layout", nc=7, w=260, backgroundColor=[0.284,0.352,0.352])
    tri3d.textField("timeChangeField", w=40, placeholderText="move key")
    tri3d.symbolButton(image = IMAGE_PATH + "/moveKeyLe.png", w=40, h=40, c=Funcanim.moveKeyBUi)
    tri3d.symbolButton(image = IMAGE_PATH + "/moveKeyRi.png", w=40, h=40, c=Funcanim.moveKeyFUi)
    tri3d.symbolButton(image = IMAGE_PATH + "/getGraphEditor.png", w=40, h=40, c=func.graphEditor)
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.symbolButton(image = IMAGE_PATH +"/autoTangent.png", w=40, h=40, c=Funcanim.TangentsAuto)
    tri3d.symbolButton(image = IMAGE_PATH +"/splineTangent.png", w=40, h=40, c=Funcanim.TangentsSpline)
    tri3d.symbolButton(image = IMAGE_PATH +"/clampedTangent.png", w=40, h=40, c=Funcanim.TangentsClamped)
    tri3d.symbolButton(image = IMAGE_PATH +"/linearTangent.png", w=40, h=40, c=Funcanim.TangentsLinear)
    tri3d.symbolButton(image = IMAGE_PATH +"/flatTangent.png", w=40, h=40, c=Funcanim.TangentsFlat)

    tri3d.setParent("Animation")
    tri3d.rowColumnLayout("Layer8", w=260, nc=2, backgroundColor=[0.284,0.352,0.352])
    tri3d.button(l="Detach Window", w=270, c=anim.animWindow)

    ################################################################ move key pro
    tri3d.setParent("Animation")
    tri3d.frameLayout("Move Key Pro", w=270, cll=True, cl=False)
    tri3d.columnLayout("Main_Layout", w=260, adj= 1)
    tri3d.rowColumnLayout("Move_Pro", w=260, nc=4)
    tri3d.button(l= 'Select', c= Funcanim.selectCtrl, w=50)
    tri3d.textField('selectCtrl', w= 270, ed= 0, placeholderText="Select_Controller")
    tri3d.button(l= 'Select', c= Funcanim.selectAll, w=50)
    tri3d.textField('selectAll', w= 100, ed= 0, placeholderText="Select_Ctrl")

    tri3d.setParent("Main_Layout")
    tri3d.checkBox('UseSEK', l= 'On_Start_End', v= 0, cc= Funcanim.useSEK)
    tri3d.rowColumnLayout("Button2", w=260, nc=4)
    tri3d.button(l= 'Start Key', c= Funcanim.butt_startKey, w=50)
    tri3d.textField('startKey', w= 100, ed= 0, tx= '')
    tri3d.button(l= 'End Key', c= Funcanim.butt_endKey, w=50)
    tri3d.textField('endKey', w= 100, ed= 0, tx= '')
    tri3d.setParent("Main_Layout")
    tri3d.intSliderGrp('numbersKey', f= 1, min= 1, v= 1, max= 999999)
    tri3d.setParent("Main_Layout")
    tri3d.rowColumnLayout("button select", w=260, nc=2)
    tri3d.button('moveBackward', l= '<<< Move Back', c= Funcanim.butt_moveBackward, w=150)
    tri3d.button('moveForward', l= 'Move Go >>>', c= Funcanim.butt_moveForward, w=150)    

################################################################ copy right by Tri 3D
################################################################
    tri3d.setParent(tab_layout_main)
    tri3d.columnLayout("About", w=250)
    tri3d.frameLayout("Click to button :", w=270)
    tri3d.rowColumnLayout("Layer6", w=260, nc=5)
    tri3d.symbolButton(image=IMAGE_PATH +"/LogoGumroad.jpg", w=50, h=50, c=func.openWebMessFB)
    tri3d.text("                   ")
    tri3d.symbolButton(image=IMAGE_PATH +"/gumroad.png", w=50, h=50, c=func.openWebgumroad)
    tri3d.text("                   ")

    tri3d.symbolButton(image=IMAGE_PATH +"/Gmail_Icon.png", w=50, h=50, c=func.openGmail)
    tri3d.setParent("About")
    tri3d.rowColumnLayout("Layer7", w=260, nc=3)
    tri3d.button("Copy   ", w=100, c=func.copyEmail)
    tri3d.textField("Email", w=199, text="info.tri3d@gmail.com")
    tri3d.setParent("About")
    tri3d.columnLayout("duongdungrong", w=260)
    tri3d.button(l="Hoang Sa Truong Sa la cua Viet Nam", w=270)
    tri3d.text(l="                              Kiem tra cap nhap tools : ", h=20)
    tri3d.button(l="Update Version ", w=270, h=30, c=func.update_tools)
    tri3d.button(l="User manual ", w=270, h=30, c=func.user_manual)
    
    tri3d.button(l="Khoa hoc ve Rigging", w=270, h=30, c=func.openWebRiggingSlide)
    tri3d.image(image=IMAGE_PATH +"/vn.png", w=270)
    tri3d.setParent(tab_layout_main)

    tri3d.showWindow(triWin)
    dock = tri3d.dockControl(allowedArea=['right', 'left'], area='right', content=triWin, label="Tri 3D Tools", epo=True)

####################
#####################
#####################
#####################
#####################
#####################
#####################
#####################
#####################
# createUI()
def windowUi(*arg):
    global dock
    if tri3d.window("tri3dwin", exists=True):
        tri3d.deleteUI("tri3dwin")


    tri3dwin = tri3d.window("tri3dwin", title="tools_Tri3D for Student", sizeable=False, menuBar=True, resizeToFitChildren=False, w=273, h=550)
    tri3d.windowPref("tri3dwin", remove=True)

    tri3d.menu(l="Modify")
    tri3d.menuItem(l="Freeze Transformations", image= IMAGE_PATH + "/FreezeTransform.png", c=func.freezeOptions )
    tri3d.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )
    # tri3d.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )


    tri3d.menu(l="Display")
    tri3d.menuItem(l="Window", image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions)
    tri3d.menuItem(l="Joint Size", image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions)
    # tri3d.menuItem(l="Test", image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions)

    tri3d.menu(l="About")
    tri3d.menuItem(l="Command Maya", image= IMAGE_PATH + "/mayaIcon.png", c=func.run_web)
    tri3d.menuItem(l="Follow Fanpage", image= IMAGE_PATH + "/LogoGumroad.jpg", c=func.openWebPageFB)
    tri3d.menuItem(l="Khoa hoc Rigging ", image= IMAGE_PATH + "/LogoGumroad.jpg", c=func.openWebRigging)
    tri3d.menuItem(l="Gumroad", image= IMAGE_PATH + "/gumroad.png", c=func.openWebgumroad)
    tri3d.menuItem(l="Contact by Email", image= IMAGE_PATH + "/Gmail_icon.png", c=func.openGmail)
    tri3d.menuItem("info.tri3d@gmail.com", image=IMAGE_PATH + "/copyIcon.png", c=func.copyEmail)
    tri3d.menuItem("Update Version to 2.0", image=IMAGE_PATH + "/updateicon.png", c=func.update_tools)



################################################################ UI UX
################################################################
    main_layout = tri3d.columnLayout(adjustableColumn=True, h=990)
    tab_layout_main = tri3d.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    tri3d.setParent(tab_layout_main)
    tri3d.scrollLayout("Modify", horizontalScrollBarThickness=500, verticalScrollBarThickness=500, h=500)
    
    tri3d.textField("frontName", w=250, h=30, placeholderText="Front_", text="")
    tri3d.button(l="Front Name", w=250, c=func.frontName, backgroundColor=[0.284,0.352,0.352])
    tri3d.textField("backName", w=250, h=30, placeholderText="_Back", text="")
    tri3d.button(l="Back Name", w=250, c=func.backName, backgroundColor=[0.284,0.352,0.352])
    tri3d.separator(w=250, h=3, style="in", backgroundColor=[0.284,0.352,0.352])
    tri3d.button(l=" Delete : Pasted__", w=250, c=tools.pasterdelete)



    tri3d.setParent("Modify")
    tri3d.frameLayout("Connect ", w=250, cll=True, cl=False)
    tri3d.rowColumnLayout("Layout1", w=250, nc=4)
    tri3d.button(l="Attribute", c=func.addattribute, w=63)
    tri3d.button(label="Set", c=func.setdrivenkey, w=63)
    tri3d.button(label="Connect", c=func.connectEditor, w=63)
    tri3d.button(label="Node", c=func.Node, w=63)
    tri3d.button(label="Influe", c=func.addinfluence, w=63)
    tri3d.button(label="Group", c=func.groupobj, w=63)
    tri3d.button(label="Lock", c=func.lockandhide, w=63)
    # tri3d.button(label="Color", c=func.add_color_attribute, w=63)
    # tri3d.button(label="Blend", c=func.add_blend_attribute, w=63)
    tri3d.button(l="Channel", c=func.channelcontrol, w=63)



    ########## polygon #################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Polygon_layout", w=250)
    tri3d.frameLayout("Polygon", w=250, cll=False)
    tri3d.rowColumnLayout("Polygon", w=250, nc=6)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCube.png", w=42, h=42, c=tools.cubeAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySphere.png", w=42, h=42, c=tools.sphereAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCylinder.png", w=42, h=42, c=tools.cylinderAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCone.png", w=42, h=42, c=tools.coneAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyDisc.png", w=42, h=42, c=tools.discAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyTorus.png", w=42, h=42, c=tools.torusAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyPrism.png", w=42, h=42, c=tools.prismAdd)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyPyramid.png", w=42, h=42, c=tools.pyramidAdd)

    tri3d.symbolButton(image=IMAGE_PATH + "/polyUnite.png", w=42, h=42, c=tools.CombinePolygons)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySeparate.png", w=42, h=42, c=tools.SeparatePolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBooleansUnion.png", w=42, h=42, c=tools.PolygonBooleanUnion)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyMergeToCenter.png", w=42, h=42, c=tools.MergeToCenter)
    tri3d.symbolButton(image=IMAGE_PATH + "/polySmooth.png", w=42, h=42, c=tools.SmoothPolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyReduce.png", w=42, h=42, c=tools.ReducePolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyMirrorGeometry.png", w=42, h=42, c=tools.MirrorPolygonGeometryOptions)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyType.png", w=42, h=42, c=tools.CreatePolygonType)
    
    tri3d.symbolButton(image=IMAGE_PATH + "/multiCut_NEX32.png", w=42, h=42, c=tools.dR_multiCutTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/weld_NEX32.png", w=42, h=42, c=tools.MergeVertexTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyDuplicateFacet.png", w=42, h=42, c=tools.DuplicateFace)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBevel.png", w=42, h=42, c=tools.performBevelOrChamfer)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyBridge.png", w=42, h=42, c=tools.performBridgeOrFill)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyCleanup.png", w=42, h=42, c=tools.CleanupPolygon)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyFlip.png", w=42, h=42, c=tools.FlipMesh)
    tri3d.symbolButton(image=IMAGE_PATH + "/polyAverageVertex.png", w=42, h=42, c=tools.AverageVertex)

    ########## sculp #################
    tri3d.setParent("Modify")
    tri3d.frameLayout("Sculpting", w=250, cll=False)
    tri3d.rowColumnLayout("Sculpting", w=250, nc=7)
    tri3d.symbolButton(image=IMAGE_PATH + "/Sculpt.png", w=36, h=36, c=tools.SetMeshSculptTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Smooth.png", w=36, h=36, c=tools.SetMeshSmoothTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Relax.png", w=36, h=36, c=tools.SetMeshRelaxTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Grab.png", w=36, h=36, c=tools.SetMeshGrabTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Pinch.png", w=36, h=36, c=tools.SetMeshPinchTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Flatten.png", w=36, h=36, c=tools.SetMeshFlattenTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/Foamy.png", w=36, h=36, c=tools.SetMeshFoamyTool)

    ########## modify #################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Modify_layout", w=250)
    tri3d.frameLayout("Modify", w=250, cll=False)
    tri3d.rowColumnLayout("Modify_row", w=250, nc=7)
    tri3d.symbolButton(image=IMAGE_PATH + "/match.png", w=35, h=35, c=tools.MatchTransform)
    tri3d.symbolButton(image=IMAGE_PATH + "/unfreetransform.png", w=35, h=35, c=tools.unFreezeTrans)
    tri3d.symbolButton(image=IMAGE_PATH + "/menuIconSelect.png", w=35, h=35, c=tools.SelectHierarchy)
    tri3d.symbolButton(image=IMAGE_PATH + "/pivotReset.png", w=35, h=35, c=tools.resetPivot)
    tri3d.symbolButton(image=IMAGE_PATH + "/CenterPivot.png", w=35, h=35, c=tools.centerPivot)
    tri3d.symbolButton(image=IMAGE_PATH + "/FreezeTransform.png", w=35, h=35, c=tools.freezeTrans)
    tri3d.symbolButton(image=IMAGE_PATH + "/deleteHist.png", w=35, h=35, c=tools.deleteHistory)
################################   Functions    #################################
#################################################################################
    tri3d.setParent("Modify")
    tri3d.columnLayout("Functions", w=250)
    tri3d.setParent("Functions")
    tri3d.text(l="Move Object to vertex : " , w=250, h=15, backgroundColor=[0.284,0.352,0.352])
    tri3d.rowColumnLayout("Tools_model", w=250, nc=2)
    tri3d.button(l="Select", w=40, h=20, c=func.button1_select_obj)
    tri3d.textField("move_obj_to_vertex", placeholderText = "Select Model", editable=False, w=250, h=20)
    tri3d.button(l="Move", w=80, h=20, c=func.button2_move_obj)
    tri3d.textField("move_obj_to_vertex_comp", placeholderText = "!!!", editable=False, w=250, h=20)

    ########################## control functions #########################
    tri3d.setParent("Modify")
    tri3d.frameLayout("Controller", w=250, cll=True, cl=False)
    tri3d.columnLayout("Controller_Main", w=250)

    tri3d.setParent("Controller_Main")
    tri3d.rowColumnLayout("Controller_Layout_Rig", w=250, nc=7)
    ButtonLocParent1 = tri3d.textField("scaleTextField", w=35, h=35, ec=func.ctrlIn, placeholderText="_____", text="1")
    tri3d.symbolButton(image=IMAGE_PATH + "/objtoctrl.png",  c=func.ctrlIn, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/add1ctrl.png",  c=func.create1Ctrl, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/add2ctrl.png",  c=func.create2Ctrl, w=35, h=35)
    ButtonLocParent = tri3d.symbolButton(image=IMAGE_PATH + "/Locator.png", w=35, h=35, c=func.ctrlInB)
    tri3d.symbolButton(image=IMAGE_PATH + "/jointadd.png", c=Rig.createJoint, w=35, h=35)
    tri3d.symbolButton(image=IMAGE_PATH + "/jointaddpivot.png", c=func.create1Ctrlparentobj, w=35, h=35)

    tri3d.setParent("Controller_Main")
    tri3d.rowColumnLayout("Edge_to_curve", w=250, nc=7)
    degree_Curve = tri3d.textField("degree_text", w=35, h=25, ec=Cur.edgeToCurve, placeholderText="1 or 3", text="3")
    tri3d.symbolButton(image=IMAGE_PATH + "/Ari_etc.png", c=Cur.edgeToCurve, w=95, h=20)
    tri3d.separator(w=1, h=25, style="in")
    tri3d.text(l="", w=10)
    tri3d.button(l="Scale + ", w=50, c=Rig.scalePoCurve)
    tri3d.text(l="", w=5)
    tri3d.button(l="Scale - ", w=50, c=Rig.scaleNeCurve)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Add attribute", w=250, cll=True, cl=False)
    tri3d.columnLayout("Add_attribute", w=250)
    tri3d.rowColumnLayout("Add_Attr", w=250, nc=5)
    tri3d.textField("Name_Attribute_textField", w=95, placeholderText="Name_Attribute")
    tri3d.text(l="Min :", w=38)
    tri3d.textField("min_value_attribute", w=38, text="1")
    tri3d.text(l="Max :", w=38)
    tri3d.textField("max_value_attribute", w=38)
    tri3d.setParent("Add_attribute")
    tri3d.rowColumnLayout("Add_data_type_set", w=250, nc=3)
    tri3d.textField("data_type_text", w=95, placeholderText="long or float", text="float")
    tri3d.text(l="", w=38)
    tri3d.button(l="Create attribute", w=135, command=tools2.create_attr)


    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Change Color", w=250, cll=True, cl=False)
    tri3d.rowColumnLayout("ChangeColor_Layout", w=250, nc=5)
    tri3d.button(l="Refill",c=func.refillcolorctrl, w=49, backgroundColor=[1,1,1])
    tri3d.canvas(w=50, rgb=[1,0,0], pressCommand=func.redColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0.250,0.078], pressCommand=func.cl_lightOrangeColorCtrl)
    tri3d.canvas(w=50, rgb=[1,1,0], pressCommand=func.yellowColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0.506,0.766], pressCommand=func.pinkColorCtrl)
    tri3d.canvas(w=50, rgb=[0,1,0], pressCommand=func.greenColorCtrl)
    tri3d.canvas(w=50, rgb=[1,1,1], pressCommand=func.whileColorCtrl)
    tri3d.canvas(w=50, rgb=[1,0,1], pressCommand=func.purpleColorCtrl)
    tri3d.canvas(w=50, rgb=[0,1,1], pressCommand=func.blueLColorCtrl)
    tri3d.canvas(w=50, rgb=[0,0,1], pressCommand=func.cl_darkBlueColorCtrl)
    tri3d.canvas(w=50, rgb=[0,0,0], pressCommand=func.blackColorCtrl)
    tri3d.canvas(w=50, rgb=[0.19,0.19,0.19], pressCommand=func.greyColorCtrl)
    tri3d.canvas(w=50, rgb=[0.352,0.116,0.037], pressCommand=func.cl_brownColorCtrl)
    tri3d.canvas(w=50, rgb=[0.53,0.014,0.014], pressCommand=func.cl_darkRedColorCtrl)
    tri3d.canvas(w=50, rgb=[0.085,0.386,0.206], pressCommand=func.cl_midnightGreenColorCtrl)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Curve", w=250, cll=True, cl=True)
    tri3d.columnLayout("Curve_Layout_Main", w=250)
    tri3d.rowColumnLayout("Curve_Layout", w=250, nc=6)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton02.png", w=42, h=42, c=Cur.cubeCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton08.png", w=42, h=42, c=Cur.pringleCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton48.png", w=42, h=42, c=Cur.handCircleCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton11.png", w=42, h=42, c=Cur.handCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton12.png", w=42, h=42, c=Cur.footCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton46.png", w=42, h=42, c=Cur.VerticalSlider)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton47.png", w=42, h=42, c=Cur.handPet)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton03.png", w=42, h=42, c=Cur.arrowTriangle)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton09.png", w=42, h=42, c=Cur.LocatorCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton10.png", w=42, h=42, c=Cur.circleD)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton19.png", w=42, h=42, c=Cur.ccButton19)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton17.png", w=42, h=42, c=Cur.plusCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton23.png", w=42, h=42, c=Cur.circleP)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton27.png", w=42, h=42, c=Cur.rotateCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton28.png", w=42, h=42, c=Cur.axisC)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton29.png", w=42, h=42, c=Cur.arrowCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton32.png", w=42, h=42, c=Cur.circleAround)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton35.png", w=42, h=42, c=Cur.wardCtrl)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton36.png", w=42, h=42, c=Cur.EyeCtrl)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton38.png", w=42, h=42, c=Cur.fourAround)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton40.png", w=42, h=42, c=Cur.ccButton40)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccButton43.png", w=42, h=42, c=Cur.ccButton43)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccSquare.png", w=42, h=42, c=Cur.squareCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccSlider.png", w=42, h=42, c=Cur.functionsCurve)
    tri3d.symbolButton(image = IMAGE_PATH + "/ccFace.png", w=42, h=42, c=Cur.faceCurve)

    tri3d.setParent("Curve_Layout_Main")
    tri3d.columnLayout("Curve_Layout_cl", w=250, columnAttach = ('left', 5))
    #tri3d.button(l="Combine Shape", w=250)
    tri3d.colorIndexSliderGrp(Rig.ctrlColor, minValue = 1, maxValue = 31, value = 16, columnWidth = (1,60), columnWidth2 = (1, 215),\
                              dragCommand = Rig.hideManipulator, changeCommand = Rig.showManipulator) 
    #tri3d.symbolButton(image=IMAGE_PATH + "/blendShapeEditor.png", w=42, h=42, c=func.ShapeEditor)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Curve Code", w=250, cll=True, cl=True)
    tri3d.columnLayout("Curve_code", w=250)
    tri3d.textField("tx_roundNum_ctt", w=250,text="2", placeholderText="        Select to curve")
    tri3d.scrollField("tx_codeCTL_ctt", w=250, h=50, wordWrap=True)
    tri3d.button(l="Create Code", w=250, c=Cur.createCodeCurve_ctt)

    tri3d.setParent("Controller_Main")
    tri3d.frameLayout("Modify", w=250, cll=True, cl=False)
    tri3d.columnLayout("Modify_Layout", w=250)

    tri3d.setParent("Modify_Layout")
    tri3d.rowColumnLayout("Modify_Layout", w=250, nc=6, backgroundColor=[0.284,0.352,0.352])
    tri3d.symbolButton(image=IMAGE_PATH + "/circle.png", w=40, h=40, c=func.createCircle)
    tri3d.symbolButton(image=IMAGE_PATH + "/pencil.png", w=40, h=40, c=func.PencilCurveTool)
    tri3d.symbolButton(image=IMAGE_PATH + "/curveEP.png", w=40, h=40, c=func.EPCurveTool)
    # tri3d.symbolButton(image=IMAGE_PATH + "/ngSkinTools2ShelfIcon.png", w=40, h=40)
    tri3d.symbolButton(image=IMAGE_PATH + "/textureEditor.png", w=40, h=40, c=func.TextureViewWindow)
    tri3d.symbolButton(image=IMAGE_PATH + "/getGraphEditor.png", w=40, h=40, c=func.graphEditor)
    # tri3d.symbolButton(h=30, w=30, image= IMAGE_PATH + "/jointSize.png", c=func.jointSizeOptions) 
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/kinJoint.png" , c=func.jointTools)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/kinMirrorJoint_S.png" , c=func.jointMirror)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/orientJoint.png", c=func.orientJoint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/smoothSkin.png" , c=func.SmoothBindSkin)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/detachSkin.png" , c=func.DetachSkin)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/copySkinWeight.png" , c=func.CopySkinWeights)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/lattice.png", c=func.CreateLattice)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/parentConstraint.png" , c=func.ParentConstraintOptions)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/orientConstraint.png" , c=func.OrientConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/aimConstraint.png" , c=func.AimConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/posConstraint.png" , c=func.PointConstraint)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/scaleConstraint.png" , c=func.ScaleConstraintOptions)
    tri3d.symbolButton(h=40, w=40, image= IMAGE_PATH +"/poleVectorConstraint.png" , c=func.PoleVectorConstraint)


################################################################ Animation
################################################################
    tri3d.setParent(tab_layout_main)
    tri3d.columnLayout("Animation", w=260)
    tri3d.setParent("Animation")
    tri3d.frameLayout("Graph", w=270)
    tri3d.rowColumnLayout("FunctionsKey_Layout", nc=5, w=260, backgroundColor=[0.284,0.352,0.352])
    tri3d.symbolButton(image = IMAGE_PATH +"/ResetKey.png", w=66, h=25, c=Funcanim.resetKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/copyKey.png", w=66, h=25, c=Funcanim.copyKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/pasteKey.png", w=66, h=25, c=Funcanim.pasteKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/deleteKey.png", w=66, h=25, c=Funcanim.cutKey)
    tri3d.symbolButton(image = IMAGE_PATH +"/Picker.png", w=66, h=25, c=pk.animPickerTri3D)

    tri3d.setParent("Animation")
    tri3d.columnLayout("Animation_layout", w=270)
    tri3d.rowColumnLayout("FunctionsGraph_Layout", nc=7, w=260, backgroundColor=[0.284,0.352,0.352])
    tri3d.textField("timeChangeField", w=40, placeholderText="move key")
    tri3d.symbolButton(image = IMAGE_PATH + "/moveKeyLe.png", w=40, h=40, c=Funcanim.moveKeyBUi)
    tri3d.symbolButton(image = IMAGE_PATH + "/moveKeyRi.png", w=40, h=40, c=Funcanim.moveKeyFUi)
    tri3d.symbolButton(image = IMAGE_PATH + "/getGraphEditor.png", w=40, h=40, c=func.graphEditor)
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.text(l="")
    tri3d.symbolButton(image = IMAGE_PATH +"/autoTangent.png", w=40, h=40, c=Funcanim.TangentsAuto)
    tri3d.symbolButton(image = IMAGE_PATH +"/splineTangent.png", w=40, h=40, c=Funcanim.TangentsSpline)
    tri3d.symbolButton(image = IMAGE_PATH +"/clampedTangent.png", w=40, h=40, c=Funcanim.TangentsClamped)
    tri3d.symbolButton(image = IMAGE_PATH +"/linearTangent.png", w=40, h=40, c=Funcanim.TangentsLinear)
    tri3d.symbolButton(image = IMAGE_PATH +"/flatTangent.png", w=40, h=40, c=Funcanim.TangentsFlat)

    tri3d.setParent("Animation")
    tri3d.rowColumnLayout("Layer8", w=260, nc=2, backgroundColor=[0.284,0.352,0.352])
    tri3d.button(l="Detach Window", w=270, c=anim.animWindow)

    ################################################################ move key pro
    tri3d.setParent("Animation")
    tri3d.frameLayout("Move Key Pro", w=270, cll=True, cl=False)
    tri3d.columnLayout("Main_Layout", w=260, adj= 1)
    tri3d.rowColumnLayout("Move_Pro", w=260, nc=4)
    tri3d.button(l= 'Select', c= Funcanim.selectCtrl, w=50)
    tri3d.textField('selectCtrl', w= 270, ed= 0, placeholderText="Select_Controller")
    tri3d.button(l= 'Select', c= Funcanim.selectAll, w=50)
    tri3d.textField('selectAll', w= 100, ed= 0, placeholderText="Select_Ctrl")

    tri3d.setParent("Main_Layout")
    tri3d.checkBox('UseSEK', l= 'On_Start_End', v= 0, cc= Funcanim.useSEK)
    tri3d.rowColumnLayout("Button2", w=260, nc=4)
    tri3d.button(l= 'Start Key', c= Funcanim.butt_startKey, w=50)
    tri3d.textField('startKey', w= 100, ed= 0, tx= '')
    tri3d.button(l= 'End Key', c= Funcanim.butt_endKey, w=50)
    tri3d.textField('endKey', w= 100, ed= 0, tx= '')
    tri3d.setParent("Main_Layout")
    tri3d.intSliderGrp('numbersKey', f= 1, min= 1, v= 1, max= 999999)
    tri3d.setParent("Main_Layout")
    tri3d.rowColumnLayout("button select", w=260, nc=2)
    tri3d.button('moveBackward', l= '<<< Move Back', c= Funcanim.butt_moveBackward, w=150)
    tri3d.button('moveForward', l= 'Move Go >>>', c= Funcanim.butt_moveForward, w=150)    

################################################################ copy right by Tri 3D
################################################################
    tri3d.setParent(tab_layout_main)
    tri3d.columnLayout("About", w=250)
    tri3d.frameLayout("Click to button :", w=270)
    tri3d.rowColumnLayout("Layer6", w=260, nc=5)
    tri3d.symbolButton(image=IMAGE_PATH +"/LogoGumroad.jpg", w=50, h=50, c=func.openWebMessFB)
    tri3d.text("                   ")
    tri3d.symbolButton(image=IMAGE_PATH +"/gumroad.png", w=50, h=50, c=func.openWebgumroad)
    tri3d.text("                   ")

    tri3d.symbolButton(image=IMAGE_PATH +"/Gmail_Icon.png", w=50, h=50, c=func.openGmail)
    tri3d.setParent("About")
    tri3d.rowColumnLayout("Layer7", w=260, nc=3)
    tri3d.button("Copy   ", w=100, c=func.copyEmail)
    tri3d.textField("Email", w=199, text="info.tri3d@gmail.com")
    tri3d.setParent("About")
    tri3d.columnLayout("duongdungrong", w=260)
    tri3d.button(l="Hoang Sa Truong Sa la cua Viet Nam", w=270)
    tri3d.text(l="                              Kiem tra cap nhap tools : ", h=20)
    tri3d.button(l="Update Version ", w=270, h=30, c=func.update_tools)
    tri3d.button(l="User manual ", w=270, h=30, c=func.user_manual)
    
    tri3d.button(l="Khoa hoc ve Rigging", w=270, h=30, c=func.openWebRiggingSlide)
    tri3d.image(image=IMAGE_PATH +"/vn.png", w=270)
    # tri3d.setParent(tab_layout_main)

    tri3d.showWindow(tri3dwin)







