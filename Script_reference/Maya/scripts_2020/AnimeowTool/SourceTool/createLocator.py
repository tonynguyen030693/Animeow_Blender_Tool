'''
            LMlocator 1.6.18
by Luismi Herrera. Twitter: @luismiherrera


- Creates a locator at origin (if nothing selected).
- If there is anything selected it will create locators with the same
  transforms as the object(s) selected.
- If there are vertices selected it will create a locator at the center of
  the selected vertices bounding box.
'''


import maya.cmds as cmds


def createLocatorAtSelection(*args):
    sel = cmds.ls(selection = True)
    sel_verts = cmds.filterExpand(sm=31)


    suffix = '_LOC' # or '_LOC#' if we want to add a number at the end in the firt locator too.


    if (len(sel) == 0):
        loc = cmds.spaceLocator()
    elif (sel_verts != None):
        locName = sel_verts[0].split('.')[0] + suffix
        bb = cmds.exactWorldBoundingBox(sel_verts)
        pos = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
        newLoc = cmds.spaceLocator(name=locName)
        cmds.move(pos[0], pos[1], pos[2], newLoc)
    else:
        for i in range(len(sel)):
            locName = sel[i] + suffix
            loc = cmds.spaceLocator(name= locName)
            tempConst = cmds.parentConstraint(sel[i], loc, mo=False)
            cmds.delete(tempConst)


    # cmds.select(clear=True)
