# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

MENU_NAME = "AnimeowMenu"
MENU_LABEL = "Animeow"

def delete_menu():
    """Xoa menu Animeow cu neu ton tai"""
    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME, menu=True)

def create_menu():
    """Dang ky nut bam Toolboard vao thanh cong cu chung Animeow"""
    g_main_window = mel.eval("$tmpVar=$gMainWindow")
    if not g_main_window:
        return
        
    # Tao menu chinh Animeow neu chua co
    if not cmds.menu(MENU_NAME, exists=True):
        cmds.menu(MENU_NAME, label=MENU_LABEL, parent=g_main_window, tearOff=True)
        
    # Lay danh sach cac menu item hien co de tranh tao trung lap
    menu_items = cmds.menu(MENU_NAME, query=True, itemArray=True) or []
    
    # Xoa cac menu item cu de tranh bi trung hoac thua nut
    for item in menu_items:
        try:
            lbl = cmds.menuItem(item, query=True, label=True)
            if lbl in ["Anim Combiner Toolboard", "Animeow Toolboard"]:
                cmds.deleteUI(item, menuItem=True)
        except Exception:
            pass
            
    # Lay lai danh sach sau khi xoa
    menu_items = cmds.menu(MENU_NAME, query=True, itemArray=True) or []
            
    # Them dau gach phan cach neu da co cac menu item khac tu truoc
    if menu_items:
        cmds.menuItem(divider=True, parent=MENU_NAME)
        
    pkg_name = __name__.split('.')[0]
    cmds.menuItem(
        label="Animeow Toolboard",
        command="import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('{0}'):\n        del sys.modules[m]\nimport {0}\n{0}.show()".format(pkg_name),
        image="fileOpen.png",
        parent=MENU_NAME
    )
    print("Da dang ky 'Animeow Toolboard' vao menu '%s'." % MENU_LABEL)
