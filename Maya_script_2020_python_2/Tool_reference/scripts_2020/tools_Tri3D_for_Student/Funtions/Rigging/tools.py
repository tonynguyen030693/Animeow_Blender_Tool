import maya.cmds as cmds
import maya.mel as mel
import webbrowser
def main_pass(*arg):
    pass

def run_code(*arg):
    cmds.warning("Running")

def run_web(*arg):
    webbrowser.open("https://help.autodesk.com/view/MAYAUL/2019/ENU/?guid=__CommandsPython_index_html")



def create_attr(*arg):
    selected = cmds.ls(sl=True)
    name_attr = cmds.textField("Name_Attribute_textField", query=True, text=True)
    min_value = float(cmds.textField("min_value_attribute", query=True, text=True))
    max_value = float(cmds.textField("max_value_attribute", query=True, text=True))
    data_type = str(cmds.textField("data_type_text", query=True, text=True))

    for obj in selected:
        cmds.addAttr(obj, longName = name_attr, attributeType = data_type, min=min_value, max=max_value, keyable=True)
        
def start_jnt(*arg):
    selected = cmds.ls(sl=True, type="joint")
    if selected :
        cmds.textField("start_jnt", edit=True, text=selected[0])
def end_jnt(*arg):
    selected = cmds.ls(sl=True, type="joint")
    if selected :
        cmds.textField("end_jnt", edit=True, text=selected[0])
def Create_IKHandle(*arg):
    start_jnt_name = cmds.textField("start_jnt", query=True, text=True)
    end_jnt_name = cmds.textField("end_jnt", query=True, text=True)

    if not start_jnt_name or not end_jnt_name:
        cmds.warning("Vui long select joint")
        return
    else:
        cmds.warning("oke")
    Ik_Handle_jnt = cmds.ikHandle(startJoint = start_jnt_name, endEffector = end_jnt_name, solver="ikRPsolver")[0]

    IK_Ctrl = cmds.curve(n="IK_Handle_Ctrl",
    d=1,
    p=[(-1, 0, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)],
    k=[0, 1, 2, 3, 4]
    )
    grp = cmds.group(n= IK_Ctrl + "_grp", empty=True)
    cmds.parent(IK_Ctrl, grp)
    cmds.matchTransform(grp, Ik_Handle_jnt)
    cmds.warning("Create IK oke")
    cmds.parent(Ik_Handle_jnt, IK_Ctrl)

