# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds
import maya.mel as mel

MENU_NAME = "AnimeowMenu"
MENU_LABEL = "Animeow"

def delete_menu():
    """Xóa menu Animeow cũ nếu tồn tại"""
    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME, menu=True)

def create_menu():
    """Tạo menu Animeow trên thanh công cụ chính của Maya"""
    delete_menu()
    
    # Tìm kiếm Menu Bar chính của Maya
    g_main_window = mel.eval("$tmpVar=$gMainWindow")
    if not g_main_window:
        return
        
    # Tạo menu mới
    cmds.menu(MENU_NAME, label=MENU_LABEL, parent=g_main_window, tearOff=True)
    
    # Thêm nút mở Anim File Manager
    cmds.menuItem(
        label="Anim File Manager",
        command="import animeow_Maya_pipeline; animeow_Maya_pipeline.show()",
        image="fileOpen.png"
    )
    
    print("Đã tạo menu '%s' trên thanh công cụ chính." % MENU_LABEL)
