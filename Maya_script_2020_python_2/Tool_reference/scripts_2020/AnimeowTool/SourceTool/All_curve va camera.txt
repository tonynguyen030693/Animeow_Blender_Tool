import maya.cmds as cmds
from maya import mel

#tao danh sach
list_curve = []

"""Tao camera name
Co the thay doi camera name
kiem tra camera co ton tai khong
neu ton tai thi them vao list"""
camera_name = "v02_Cam_Rig_DOF:Shot_Cam"
if cmds.objExists(camera_name):
    list_curve.append(camera_name)

""" melscript la chon all curve
tao bien selection_curve bang cau truc mel.eval, lenh nay chi thuc hien hanh dong chon
tao bien selection la list danh sach nhung selection dang chon, tuple
gan bien ctrl la moi item nam trong selection
 them ctr vao danh sach list_curve"""


    
mel_script = 'SelectAllNURBSCurves; select -r `listTransforms "-type nurbsCurve"`;'
selection_curve = mel.eval(mel_script)
selection = cmds.ls(selection=True)
for ctrl in selection: 
    list_curve.append(ctrl)       

#chon het tat ca moi bien co trong list_curve, replace danh sach truoc do neu danh sach da ton tai
cmds.select(list_curve, replace=True)
