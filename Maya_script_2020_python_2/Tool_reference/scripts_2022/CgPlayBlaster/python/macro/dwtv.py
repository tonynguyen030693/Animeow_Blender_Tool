import maya.cmds as mc
import os

def get_stage_str():
    return '_'.join(os.path.splitext(os.path.basename(mc.file(q=True, sn=True)))[0].split('_')[4:6])