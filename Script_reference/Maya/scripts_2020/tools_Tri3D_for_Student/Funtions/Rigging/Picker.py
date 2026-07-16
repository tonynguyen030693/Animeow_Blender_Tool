import maya.cmds as cmds
import os
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Icons")



######################### define ##########################
Main = "Main_Ctrl"




################################################################
################################################################
def animPickerTri3D(*arg):
    if cmds.window("Tri3DPicker", exists=True):
        cmds.deleteUI("Tri3DPicker")

    WDPicker = cmds.window("Tri3DPicker",title="Picker Basic Tri3D", w=230, sizeable=False, menuBar=True, resizeToFitChildren=True)
    cmds.windowPref("Tri3DPicker",  remove=True)
    cmds.menu(l="Modify")
    cmds.menuItem(l="Test", image= IMAGE_PATH + "/FreezeTransform.png" )
    cmds.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )
    cmds.menuItem(l="Test", image= IMAGE_PATH + "/unfreetransform.png" )

    ############################## define button #############################
    main_layout = cmds.formLayout()
    Head_Ctrl = cmds.button(l="", width=35, height=36, backgroundColor=[0.284,0.352,0.352])
    Neck_Ctrl = cmds.button(l="", width=35, height=14, backgroundColor=[0.284,0.352,0.352])
    Chest_Ctrl = cmds.button(l=" ", w=120, h=18, backgroundColor=[0.284,0.352,0.352])
    IK_Chest_Ctrl = cmds.button(l="", w=120, h=18, backgroundColor=[0.7,0.17,0.17])
    Spine_Ctrl = cmds.button(l="", w=120, h=18, backgroundColor=[0.284,0.352,0.352])
    Root_Ctrl = cmds.button("Root_Ctrl",l="", w=120, h=18, backgroundColor=[0.284,0.352,0.352])
    Body_Ctrl = cmds.button(l="", w=50, h=18, backgroundColor=[0.284,0.352,0.352])
    IK_Root_Ctrl = cmds.button(l=" ", w=120, h=18, backgroundColor=[0.7,0.17,0.17])

    R_Hip_Ctrl = cmds.button(l="", w=30, h=60, backgroundColor=[0.284,0.352,0.352])
    R_Knee_Ctrl = cmds.button(l="", w=30, h=60, backgroundColor=[0.284,0.352,0.352])
    R_IK_Knee_Ctrl = cmds.button(l="+", w=20, h=20, backgroundColor=[0.7,0.17,0.17])
    R_Ankle_Ctrl = cmds.button(l="", w=45, h=25, backgroundColor=[0.284,0.352,0.352])
    R_IKFK_Ctrl = cmds.button(l="", w=15, h=15, backgroundColor=[0.284,0.352,0.352])
    R_Toe_Ctrl = cmds.button(l="", w=38, h=20, backgroundColor=[0.284,0.352,0.352])
    R_Ankle_Ctrl_IK = cmds.button(l="", w=45, h=20, backgroundColor=[0.7,0.17,0.17])
    R_Heel_Ctrl_IK = cmds.button(l="", w=15, h=20, backgroundColor=[0.7,0.17,0.17])
    R_Toe_Ctrl_IK = cmds.button(l="", w=38, h=20, backgroundColor=[0.7,0.17,0.17])

    L_Hip_Ctrl = cmds.button(l="", w=30, h=60, backgroundColor=[0.284,0.352,0.352])
    L_Knee_Ctrl = cmds.button(l="", w=30, h=60, backgroundColor=[0.284,0.352,0.352])
    L_IK_Knee_Ctrl = cmds.button(l="+", w=20, h=20, backgroundColor=[0.7,0.17,0.17])
    L_Ankle_Ctrl = cmds.button(l="", w=45, h=25, backgroundColor=[0.284,0.352,0.352])
    L_IKFK_Ctrl = cmds.button(l="", w=15, h=15, backgroundColor=[0.284,0.352,0.352])
    L_Toe_Ctrl = cmds.button(l="", w=38, h=20, backgroundColor=[0.284,0.352,0.352])
    L_Ankle_Ctrl_IK = cmds.button(l="", w=45, h=20, backgroundColor=[0.7,0.17,0.17])
    L_Heel_Ctrl_IK = cmds.button(l="", w=15, h=20, backgroundColor=[0.7,0.17,0.17])
    L_Toe_Ctrl_IK = cmds.button(l="", w=38, h=20, backgroundColor=[0.7,0.17,0.17])

    L_Specula_Ctrl = cmds.button(l="", w=38, h=20, backgroundColor=[0.284,0.352,0.352])
    L_Shoulder_Ctrl = cmds.button(l="", w=30, h=45, backgroundColor=[0.284,0.352,0.352])
    L_Elbow_Ctrl = cmds.button(l="", w=30, h=45, backgroundColor=[0.284,0.352,0.352])
    L_IK_Elbow_Ctrl = cmds.button(l="+", w=20, h=20, backgroundColor=[0.7,0.17,0.17])
    L_Wrist_Ctrl = cmds.button(l="", w=30, h=20, backgroundColor=[0.284,0.352,0.352])
    L_IK_Hand_Ctrl = cmds.button(l="", w=30, h=20, backgroundColor=[0.7,0.17,0.17])
    L_Hand_Ctrl = cmds.button(l="", w=30, h=10, backgroundColor=[0.284,0.352,0.352])

    R_Specula_Ctrl = cmds.button(l="", w=38, h=20, backgroundColor=[0.284,0.352,0.352])
    R_Shoulder_Ctrl = cmds.button(l="", w=30, h=45, backgroundColor=[0.284,0.352,0.352])
    R_Elbow_Ctrl = cmds.button(l="", w=30, h=45, backgroundColor=[0.284,0.352,0.352])
    R_IK_Elbow_Ctrl = cmds.button(l="+", w=20, h=20, backgroundColor=[0.7,0.17,0.17])
    R_Wrist_Ctrl = cmds.button(l="", w=30, h=20, backgroundColor=[0.284,0.352,0.352])
    R_IK_Hand_Ctrl = cmds.button(l="", w=30, h=20, backgroundColor=[0.7,0.17,0.17])
    R_Hand_Ctrl = cmds.button(l="", w=30, h=10, backgroundColor=[0.284,0.352,0.352])
    
    Main_Ctrl = cmds.button(Main, backgroundColor=[0.284,0.352,0.352]\
                            ,l="              Main Ctrl              ",\
                             w=280, h=20)
    All_Ctrl = cmds.button(l="All", w=40, h=20)
    Build_Ctrl = cmds.button(l="Build Pose", w=80, h=20)

    cmds.separator(w=280, h=3, style="in", backgroundColor=[0.284,0.352,0.352])

    ############################### options #############################
    optionsBT = cmds.optionMenu("Test_Layout", l='Ver :',ni=2)
    cmds.menuItem('Body_OT_Ctrl', l='Body' )
    cmds.menuItem('Face_OT_Ctrl', l='Face' )

    ############################### button #############################
    selectedLights = cmds.checkBox(enable=True, l="Selected" )

    ################################# setup button ######################
    cmds.formLayout(main_layout, edit=True, attachForm=[
    ####
        (optionsBT, 'top', 10),
        (optionsBT, 'left', 5),
    ####
        (selectedLights, 'top', 10),
        (selectedLights, 'left', 120),        
    ####
        (Head_Ctrl, 'top', 84),
        (Head_Ctrl, 'left', 124),
    ####
        (Neck_Ctrl, 'top', 125),
        (Neck_Ctrl, 'left', 124),
    ####
        (IK_Chest_Ctrl, 'top', 150),
        (IK_Chest_Ctrl, 'left', 80),
    ####
        (Chest_Ctrl, 'top', 170),
        (Chest_Ctrl, 'left', 80),
    ####
        (Spine_Ctrl, 'top', 195),
        (Spine_Ctrl, 'left', 80),
    ####    
        (Root_Ctrl, 'top', 220),
        (Root_Ctrl, 'left', 80),
    ####    
        (IK_Root_Ctrl, 'top', 240),
        (IK_Root_Ctrl, 'left', 80),
    ####    
        (Body_Ctrl, 'top', 260),
        (Body_Ctrl, 'left', 115),        
    ####    
        (R_Hip_Ctrl, 'top', 260),
        (R_Hip_Ctrl, 'left', 80),
    ####    
        (R_Knee_Ctrl, 'top', 325),
        (R_Knee_Ctrl, 'left', 80),
    ####    
        (R_IK_Knee_Ctrl, 'top', 325),
        (R_IK_Knee_Ctrl, 'left', 50),        
    ####    
        (R_Ankle_Ctrl, 'top', 390),
        (R_Ankle_Ctrl, 'left', 70),    
    ####    
        (R_IKFK_Ctrl, 'top', 400),
        (R_IKFK_Ctrl, 'left', 117), 
    ####    
        (R_Toe_Ctrl, 'top', 395),
        (R_Toe_Ctrl, 'left', 30), 
    ####    
        (R_Ankle_Ctrl_IK, 'top', 417),
        (R_Ankle_Ctrl_IK, 'left', 70),    
    ####    
        (R_Heel_Ctrl_IK, 'top', 417),
        (R_Heel_Ctrl_IK, 'left', 117), 
    ####    
        (R_Toe_Ctrl_IK, 'top', 417),
        (R_Toe_Ctrl_IK, 'left', 30),         
    ####    
        (L_Hip_Ctrl, 'top', 260),
        (L_Hip_Ctrl, 'left', 170),
    ####    
        (L_Knee_Ctrl, 'top', 325),
        (L_Knee_Ctrl, 'left', 170),
    ####    
        (L_IK_Knee_Ctrl, 'top', 325),
        (L_IK_Knee_Ctrl, 'left', 210),        
    ####    
        (L_Ankle_Ctrl, 'top', 390),
        (L_Ankle_Ctrl, 'left', 165),    
    ####    
        (L_IKFK_Ctrl, 'top', 400),
        (L_IKFK_Ctrl, 'left', 148), 
    ####    
        (L_Toe_Ctrl, 'top', 395),
        (L_Toe_Ctrl, 'left', 212), 
    ####    
        (L_Ankle_Ctrl_IK, 'top', 417),
        (L_Ankle_Ctrl_IK, 'left', 165),    
    ####    
        (L_Heel_Ctrl_IK, 'top', 417),
        (L_Heel_Ctrl_IK, 'left', 148), 
    ####    
        (L_Toe_Ctrl_IK, 'top', 417),
        (L_Toe_Ctrl_IK, 'left', 212),         
    ####
        (R_Specula_Ctrl, 'top', 150),
        (R_Specula_Ctrl, 'left', 35),
    ####
        (R_Shoulder_Ctrl, 'top', 175),
        (R_Shoulder_Ctrl, 'left', 40),
    ####
        (R_Elbow_Ctrl, 'top', 225),
        (R_Elbow_Ctrl, 'left', 40),
    ####
        (R_IK_Elbow_Ctrl, 'top', 225),
        (R_IK_Elbow_Ctrl, 'left', 10),        
    ####    
        (R_Wrist_Ctrl, 'top', 275),
        (R_Wrist_Ctrl, 'left', 40),
    ####    
        (R_IK_Hand_Ctrl, 'top', 275),
        (R_IK_Hand_Ctrl, 'left', 5),        
    ####    
        (R_Hand_Ctrl, 'top', 300),
        (R_Hand_Ctrl, 'left', 40),        
    ####      
        (L_Specula_Ctrl, 'top', 150),
        (L_Specula_Ctrl, 'left', 207),
    ####
        (L_Shoulder_Ctrl, 'top', 175),
        (L_Shoulder_Ctrl, 'left', 210),
    ####
        (L_Elbow_Ctrl, 'top', 225),
        (L_Elbow_Ctrl, 'left', 210),
    ####
        (L_IK_Elbow_Ctrl, 'top', 225),
        (L_IK_Elbow_Ctrl, 'left', 250),        
    ####    
        (L_Wrist_Ctrl, 'top', 275),
        (L_Wrist_Ctrl, 'left', 210),
    ####    
        (L_IK_Hand_Ctrl, 'top', 275),
        (L_IK_Hand_Ctrl, 'left', 245),      
    ####    
        (L_Hand_Ctrl, 'top', 300),
        (L_Hand_Ctrl, 'left', 210),  
    ####    
        (Main_Ctrl, 'top', 450),
        (Main_Ctrl, 'left', 0), 
    ####    
        (All_Ctrl, 'top', 100),
        (All_Ctrl, 'left', 20), 
    ####    
        (Build_Ctrl, 'top', 60),
        (Build_Ctrl, 'left', 20),        
        ])
    cmds.showWindow(WDPicker)




