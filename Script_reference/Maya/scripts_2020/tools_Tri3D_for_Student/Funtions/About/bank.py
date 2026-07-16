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


import maya.cmds as cmds
import os


IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Icons")

def createBank(*arg):
    if cmds.window("bank", exists=True):
        cmds.deleteUI("bank")

    bank = cmds.window("bank", title="Tai tro cho do ngheo khi Tri_3D", sizeable=False, resizeToFitChildren=True, w=400)
    cmds.windowPref("bank", remove=True)
    
    cmds.columnLayout(adjustableColumn=True)
    cmds.symbolButton(image=IMAGE_PATH + "/banking.png")

    cmds.showWindow(bank)
