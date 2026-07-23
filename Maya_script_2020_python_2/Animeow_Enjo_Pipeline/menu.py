# -*- coding: utf-8 -*-
from __future__ import print_function, division

import maya.cmds as cmds
import maya.mel as mel

MENU_NAME = "AnimeowMenu"
MENU_LABEL = "Animeow"

def delete_menu():
    """Xoa menu Animeow cu neu ton tai"""
    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME, menu=True)

def create_menu():
    """Tao menu Animeow tren thanh cong cu chinh cua Maya"""
    delete_menu()
    
    # Tim kiem Menu Bar chinh cua Maya
    g_main_window = mel.eval("$tmpVar=$gMainWindow")
    if not g_main_window:
        return
        
    # Tao menu moi
    cmds.menu(MENU_NAME, label=MENU_LABEL, parent=g_main_window, tearOff=True)
    
    # Them nut mo Anim File Manager
    cmds.menuItem(
        label="Anim File Manager",
        command="import Animeow_Enjo_Pipeline; Animeow_Enjo_Pipeline.show()",
        image="fileOpen.png"
    )
    
    print("Da tao menu '%s' tren thanh cong cu chinh." % MENU_LABEL)
