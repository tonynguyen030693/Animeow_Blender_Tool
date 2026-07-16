import maya.cmds as cmds
unknownNodes=cmds.ls(type = "unknown")
for item in unknownNodes:
    if cmds.objExists(item):
        print item
        cmds.delete(item)