import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import maya.api.OpenMaya as om
ccWin = 'ctrlCreatorWin'
ctrlColor = 'ctrlColor'
groupsNum = 'groupsNum'
ColorCurve1 = 3 # xam
ColorCurve2 = 18 # xanh
ColorCurve3 = 17 # vang
ColorCurve4 = 17 # vang
ColorCurve5 = 17 # vang
ColorCurve6 = 17 # vang
ColorCurve7 = 17 # vang

def faceCurve(*arg):
    groupMain = cmds.group(name="Main_Face_Grp_dont_FreezeTransformations", empty=True)
    Main_Functions = cmds.curve(name="Main_Face",d=1, p=[
        (-0.43, 0, -0.86),
        (0.43, 0, -0.86),
        (0.43, 0, 0.71),
        (-0.43, 0, 0.71),
        (-0.43, 0, -0.86)])
        
    mel.eval('setAttr -lock true -keyable false -channelBox false "Main_Face.v";')
    Functions = cmds.curve(name="LineFunction",d=1, p=[        
        (-0.4, 0, 0.45),
        (0.4, 0, 0.45),
        (0.4, 0, 0.68),
        (-0.4, 0, 0.68),
        (-0.4, 0, 0.45)])
    mel.eval("""
curve -d 2 -p -0.08 0 0.65 -p -0.08 0 0.56 -p -0.08 0 0.48 -p -0.06 0 0.48 -p -0.05 0 0.48 -p -0.03 0 0.54 -p -0.01 0 0.6 -p 0 0 0.62 -p 0 0 0.62 -p 0.01 0 0.61 -p 0.01 0 0.6 -p 0.03 0 0.54 -p 0.05 0 0.48 -p 0.07 0 0.48 -p 0.08 0 0.48 -p 0.08 0 0.56 -p 0.08 0 0.65 -p 0.07 0 0.65 -p 0.06 0 0.65 -p 0.06 0 0.58 -p 0.06 0 0.51 -p 0.04 0 0.58 -p 0.01 0 0.65 -p 0 0 0.65 -p -0.01 0 0.65 -p -0.03 0 0.58 -p -0.06 0 0.5 -p -0.06 0 0.58 -p -0.06 0 0.65 -p -0.07 0 0.65 -p -0.08 0 0.65;
                          """)    
    mel.eval("""    
    select -r LineFunction ;
    setAttr "curveShape2.template" 1;
             """)
    cmds.parent(Functions, Main_Functions)
    cmds.listRelatives(Main_Functions, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Main_Functions), True)
    cmds.setAttr("{0}.overrideColor".format(Main_Functions), ColorCurve2)  
    cmds.parent(Main_Functions, groupMain)

    Ctrl_grp = cmds.group(name="Ctrl_Grp", empty=True)
    cmds.parent(Ctrl_grp, Main_Functions)
    Line_grp = cmds.group(name="Line_grp", empty=True)
    cmds.parent(Line_grp, Main_Functions)
    Line2 = cmds.curve(name="Line2",d=1, p=[(-0.14, 0, -0.14),
        (0.14, 0, -0.14),
        (0.14, 0, 0.14),
        (-0.14, 0, 0.14),
        (-0.14, 0, -0.14)])
    gr4 = cmds.group(n="BR", empty=True)
    Func4 = cmds.curve(name="Bow_Ctrl_R", d=1, p=[        
        (0, 0, -0.36),(0.12, 0, -0.36),
        (0.24, 0, -0.24),(0.36, 0, -0.12),(0.36, 0, 0),(0.36, 0, 0.12),(0.24, 0, 0.24),
        (0.12, 0, 0.36),(0, 0, 0.36),(-0.12, 0, 0.36),(-0.24, 0, 0.24),(-0.36, 0, 0.12),
        (-0.36, 0, 0),(-0.36, 0, -0.12),(-0.24, 0, -0.24),(-0.12, 0, -0.36),(0, 0, -0.36)])
    cmds.parent(Func4, gr4)
    cmds.parent(gr4, Line2) 
    mel.eval("""
    setAttr "BR.scaleZ" 0.140;
    setAttr "BR.scaleX" 0.140;
    setAttr "BR.scaleY" 0.140;
             """)   
             
    cmds.parent(Line2, Line_grp)     
    mel.eval("""
    setAttr "Line2.translateX" -0.216;
    setAttr "Line2.translateZ" -0.646;

    select -r Line2 ;
    setAttr "curveShape4.template" 1;

             """)
    cmds.listRelatives(Line2, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Line2), True)
    cmds.setAttr("{0}.overrideColor".format(Line2), ColorCurve1)  

    Line3 = cmds.curve(name="Line3",d=1, p=[(-0.14, 0, -0.14),
        (0.14, 0, -0.14),
        (0.14, 0, 0.14),
        (-0.14, 0, 0.14),
        (-0.14, 0, -0.14)])
    gr3 = cmds.group(n="BL", empty=True)
    Func3 = cmds.curve(name="Bow_Ctrl_L", d=1, p=[        
        (0, 0, -0.36),(0.12, 0, -0.36),
        (0.24, 0, -0.24),(0.36, 0, -0.12),(0.36, 0, 0),(0.36, 0, 0.12),(0.24, 0, 0.24),
        (0.12, 0, 0.36),(0, 0, 0.36),(-0.12, 0, 0.36),(-0.24, 0, 0.24),(-0.36, 0, 0.12),
        (-0.36, 0, 0),(-0.36, 0, -0.12),(-0.24, 0, -0.24),(-0.12, 0, -0.36),(0, 0, -0.36)])
    cmds.parent(Func3, gr3)
    cmds.parent(gr3, Line3) 
    mel.eval("""
    setAttr "BL.scaleZ" 0.140;
    setAttr "BL.scaleX" 0.140;
    setAttr "BL.scaleY" 0.140;
             """)  
    
    cmds.parent(Line3, Line_grp)        
    mel.eval("""
    setAttr "Line3.translateX" 0.216;
    setAttr "Line3.translateZ" -0.646;
    setAttr -lock true -keyable false -channelBox false "Line3.v";    
    select -r Line3 ;
    setAttr "curveShape6.template" 1;

             """)
    cmds.listRelatives(Line3, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Line3), True)
    cmds.setAttr("{0}.overrideColor".format(Line3), ColorCurve1)  

 
    
    Line4 = cmds.curve(name="Line4",d=1, p=[(-0.14, 0, -0.14),
        (0.14, 0, -0.14),
        (0.14, 0, 0.14),
        (-0.14, 0, 0.14),
        (-0.14, 0, -0.14)])
    gr1 = cmds.group(n="ER", empty=True)
    Func1 = cmds.curve(name="Eye_Ctrl_R", d=1, p=[        
        (0, 0, -0.36),(0.12, 0, -0.36),
        (0.24, 0, -0.24),(0.36, 0, -0.12),(0.36, 0, 0),(0.36, 0, 0.12),(0.24, 0, 0.24),
        (0.12, 0, 0.36),(0, 0, 0.36),(-0.12, 0, 0.36),(-0.24, 0, 0.24),(-0.36, 0, 0.12),
        (-0.36, 0, 0),(-0.36, 0, -0.12),(-0.24, 0, -0.24),(-0.12, 0, -0.36),(0, 0, -0.36)])
    cmds.parent(Func1, gr1)
    cmds.parent(gr1, Line4) 
    mel.eval("""
    setAttr "ER.scaleZ" 0.140;
    setAttr "ER.scaleX" 0.140;
    setAttr "ER.scaleY" 0.140;
             """)   
             
    cmds.parent(Line4, Line_grp)    
    mel.eval("""
    setAttr "Line4.translateX" -0.216;
    setAttr "Line4.translateZ" -0.264;
    setAttr -lock true -keyable false -channelBox false "Line4.v";
    select -r Line4 ;
    setAttr "curveShape8.template" 1;

             """)
    cmds.listRelatives(Line4, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Line4), True)
    cmds.setAttr("{0}.overrideColor".format(Line4), ColorCurve1)  

    Line5 = cmds.curve(name="Line5",d=1, p=[(-0.14, 0, -0.14),
        (0.14, 0, -0.14),
        (0.14, 0, 0.14),
        (-0.14, 0, 0.14),
        (-0.14, 0, -0.14)])
    gr2 = cmds.group(n="EL", empty=True)
    Func2 = cmds.curve(name="Eye_Ctrl_L", d=1, p=[        
        (0, 0, -0.36),(0.12, 0, -0.36),
        (0.24, 0, -0.24),(0.36, 0, -0.12),(0.36, 0, 0),(0.36, 0, 0.12),(0.24, 0, 0.24),
        (0.12, 0, 0.36),(0, 0, 0.36),(-0.12, 0, 0.36),(-0.24, 0, 0.24),(-0.36, 0, 0.12),
        (-0.36, 0, 0),(-0.36, 0, -0.12),(-0.24, 0, -0.24),(-0.12, 0, -0.36),(0, 0, -0.36)])
    cmds.parent(Func2, gr2)
    cmds.parent(gr2, Line5) 
    mel.eval("""
    setAttr "EL.scaleZ" 0.140;
    setAttr "EL.scaleX" 0.140;
    setAttr "EL.scaleY" 0.140;
             """)   
    cmds.parent(Line5, Line_grp)    
    mel.eval("""
    setAttr "Line5.translateX" 0.216;
    setAttr "Line5.translateZ" -0.264;
    setAttr -lock true -keyable false -channelBox false "Line5.v";
    select -r Line5 ;
    setAttr "curveShape10.template" 1;

             """)
    cmds.listRelatives(Line5, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Line5), True)
    cmds.setAttr("{0}.overrideColor".format(Line5), ColorCurve1)  


    Line6 = cmds.curve(name="Line6",d=1, p=[(-0.14, 0, -0.14),
        (0.14, 0, -0.14),
        (0.14, 0, 0.14),
        (-0.14, 0, 0.14),
        (-0.14, 0, -0.14)])
    gr5 = cmds.group(n="MM", empty=True)
    Func5 = cmds.curve(name="Mouth", d=1, p=[        
        (0, 0, -0.36),(0.12, 0, -0.36),
        (0.24, 0, -0.24),(0.36, 0, -0.12),(0.36, 0, 0),(0.36, 0, 0.12),(0.24, 0, 0.24),
        (0.12, 0, 0.36),(0, 0, 0.36),(-0.12, 0, 0.36),(-0.24, 0, 0.24),(-0.36, 0, 0.12),
        (-0.36, 0, 0),(-0.36, 0, -0.12),(-0.24, 0, -0.24),(-0.12, 0, -0.36),(0, 0, -0.36)])
    cmds.parent(Func5, gr5) 
    cmds.parent(Line6, Line_grp)     
    mel.eval("""
    setAttr "Line6.scaleZ" 1.5;
    setAttr "Line6.scaleX" 1.5;
    setAttr "Line6.scaleY" 1.5;
    setAttr "Line6.translateZ" 0.20;
    select -r Line6 ;
    setAttr "curveShape12.template" 1;

             """)
    cmds.listRelatives(Line6, shapes=True)
    cmds.setAttr("{0}.overrideEnabled".format(Line6), True)
    cmds.setAttr("{0}.overrideColor".format(Line6), ColorCurve1)  
    cmds.parent(gr5, Line6) 
    mel.eval("""
    setAttr "MM.scaleZ" 0.140;
    setAttr "MM.scaleX" 0.140;
    setAttr "MM.scaleY" 0.140;
    setAttr "MM.translateZ" -0.14;
    
             """)  


    mel.eval("""
    setAttr -keyable false -channelBox true "Main_Face.tx";
    setAttr -keyable false -channelBox true "Main_Face.ty";
    setAttr -keyable false -channelBox true "Main_Face.tz";
    setAttr -keyable false -channelBox true "Main_Face.rx";
    setAttr -keyable false -channelBox true "Main_Face.ry";
    setAttr -keyable false -channelBox true "Main_Face.rz";
    setAttr -keyable false -channelBox true "Main_Face.sx";
    setAttr -keyable false -channelBox true "Main_Face.sy";
    setAttr -keyable false -channelBox true "Main_Face.sz";
             """)
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.ty";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.sz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.sx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.sy";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.ry";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.rx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.rz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_R.v";')
    cmds.transformLimits(Func4, tx=(-1, 1), ty=(0, 0), tz=(-1, 1), rx=(0, 0), ry=(0, 0), rz=(0, 0), sx=(1, 1), sy=(1, 1), sz=(1, 1), etx=(True, True), ety=(True, True), etz=(True, True))
    cmds.listRelatives(Func4, shapes=True)
    cmds.addAttr(Func4, longName='______________________', attributeType='enum', en='____________', keyable=True)
    mel.eval('setAttr -lock true "Bow_Ctrl_R.______________________";')
    # cmds.addAttr(Func4, longName = 'Blink', attributeType = 'float', min = 0, max = 10, keyable=True) 
    # cmds.addAttr(Func4, longName = 'Iris', attributeType = 'float', min = 0, max = 10, keyable=True) 
    # cmds.addAttr(Func4, longName = 'Pupil', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.setAttr("{0}.overrideEnabled".format(Func4), True)
    cmds.setAttr("{0}.overrideColor".format(Func4), ColorCurve3) 

    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.ty";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.sz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.sx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.sy";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.ry";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.rx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.rz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Bow_Ctrl_L.v";')
    cmds.transformLimits(Func3, tx=(-1, 1), ty=(0, 0), tz=(-1, 1), rx=(0, 0), ry=(0, 0), rz=(0, 0), sx=(1, 1), sy=(1, 1), sz=(1, 1), etx=(True, True), ety=(True, True), etz=(True, True))
    cmds.listRelatives(Func3, shapes=True)
    cmds.addAttr(Func3, longName='______________________', attributeType='enum', en='____________', keyable=True)
    mel.eval('setAttr -lock true "Bow_Ctrl_L.______________________";')
    # cmds.addAttr(Func3, longName = 'Blink', attributeType = 'float', min = 0, max = 10, keyable=True) 
    # cmds.addAttr(Func3, longName = 'Iris', attributeType = 'float', min = 0, max = 10, keyable=True) 
    # cmds.addAttr(Func3, longName = 'Pupil', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.setAttr("{0}.overrideEnabled".format(Func3), True)
    cmds.setAttr("{0}.overrideColor".format(Func3), ColorCurve3) 

    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.ty";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.sz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.sx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.sy";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.ry";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.rx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.rz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_R.v";')
    cmds.transformLimits(Func1, tx=(-1, 1), ty=(0, 0), tz=(-1, 1), rx=(0, 0), ry=(0, 0), rz=(0, 0), sx=(1, 1), sy=(1, 1), sz=(1, 1), etx=(True, True), ety=(True, True), etz=(True, True))
    cmds.listRelatives(Func1, shapes=True)
    cmds.addAttr(Func1, longName='______________________', attributeType='enum', en='____________', keyable=True)
    mel.eval('setAttr -lock true "Eye_Ctrl_R.______________________";')
    cmds.addAttr(Func1, longName = 'Blink', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func1, longName = 'Iris', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func1, longName = 'Pupil', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.setAttr("{0}.overrideEnabled".format(Func1), True)
    cmds.setAttr("{0}.overrideColor".format(Func1), ColorCurve3) 

    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.ty";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.sz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.sx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.sy";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.ry";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.rx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.rz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Eye_Ctrl_L.v";')
    cmds.transformLimits(Func2, tx=(-1, 1), ty=(0, 0), tz=(-1, 1), rx=(0, 0), ry=(0, 0), rz=(0, 0), sx=(1, 1), sy=(1, 1), sz=(1, 1), etx=(True, True), ety=(True, True), etz=(True, True))
    cmds.listRelatives(Func2, shapes=True)
    cmds.addAttr(Func2, longName='______________________', attributeType='enum', en='____________', keyable=True)
    mel.eval('setAttr -lock true "Eye_Ctrl_L.______________________";')
    cmds.addAttr(Func2, longName = 'Blink', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func2, longName = 'Iris', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func2, longName = 'Pupil', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.setAttr("{0}.overrideEnabled".format(Func2), True)
    cmds.setAttr("{0}.overrideColor".format(Func2), ColorCurve3) 

    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.ty";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.sz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.sx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.sy";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.ry";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.rx";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.rz";')
    mel.eval('setAttr -lock true -keyable false -channelBox false "Mouth.v";')
    cmds.transformLimits(Func5, tx=(-1, 1), ty=(0, 0), tz=(0, 2), rx=(0, 0), ry=(0, 0), rz=(0, 0), sx=(1, 1), sy=(1, 1), sz=(1, 1), etx=(True, True), ety=(True, True), etz=(True, True))
    cmds.listRelatives(Func5, shapes=True)
    cmds.addAttr(Func5, longName='______________________', attributeType='enum', en='____________', keyable=True)
    mel.eval('setAttr -lock true "Mouth.______________________";')
    cmds.addAttr(Func5, longName = 'Happy', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func5, longName = 'Wow', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.addAttr(Func5, longName = 'Angry', attributeType = 'float', min = 0, max = 10, keyable=True) 
    cmds.setAttr("{0}.overrideEnabled".format(Func5), True)
    cmds.setAttr("{0}.overrideColor".format(Func5), ColorCurve3)     

    mel.eval("""
    rename "curve1" "Mouth_Function";
    """)
    cmds.parent("Mouth_Function", "LineFunction")
    groupMain_xf = cmds.xform(joint_Neck, query=True, translation=True, worldSpace=True)
    groupMain_xf_tuple = tuple(groupMain_xf)
    cmds.xform(groupMain, worldSpace=True, translation=groupMain_xf_tuple)

    mel.eval("""
    setAttr "Main_Face_Grp_dont_FreezeTransformations.rotateX" 90;
    select -r Main_Face_Grp_dont_FreezeTransformations ;
    //scale -r 0.3 0.3 0.3;
    setAttr "Main_Face_Grp_dont_FreezeTransformations.translateX" 3;
    setAttr "Main_Face_Grp_dont_FreezeTransformations.translateY" 16;

    """)
    cmds.parent(groupMain, "Controller")

    mel.eval("""    
    select -r Main_Face_Grp_dont_FreezeTransformations ;
    select -tgl Neck_Ctrl ;
    parent;
    """)
    mel.eval('select -cl ;')  
