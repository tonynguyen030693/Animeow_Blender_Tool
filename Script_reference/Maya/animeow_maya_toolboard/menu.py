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
    """Đăng ký nút bấm Toolboard vào thanh công cụ chung Animeow"""
    g_main_window = mel.eval("$tmpVar=$gMainWindow")
    if not g_main_window:
        return
        
    # Tạo menu chính Animeow nếu chưa có
    if not cmds.menu(MENU_NAME, exists=True):
        cmds.menu(MENU_NAME, label=MENU_LABEL, parent=g_main_window, tearOff=True)
        
    # Lấy danh sách các menu item hiện có để tránh tạo trùng lặp
    menu_items = cmds.menu(MENU_NAME, query=True, itemArray=True) or []
    
    has_toolboard = False
    for item in menu_items:
        try:
            if cmds.menuItem(item, query=True, label=True) == "Anim Combiner Toolboard":
                has_toolboard = True
                break
        except Exception:
            pass
            
    if not has_toolboard:
        # Nếu đã có các item khác (ví dụ từ bộ pipeline), ta thêm dấu gạch phân cách
        if menu_items:
            cmds.menuItem(divider=True, parent=MENU_NAME)
            
        cmds.menuItem(
            label="Anim Combiner Toolboard",
            command="import animeow_maya_toolboard; animeow_maya_toolboard.show()",
            image="fileOpen.png",
            parent=MENU_NAME
        )
        print("Đã đăng ký 'Anim Combiner Toolboard' vào menu '%s'." % MENU_LABEL)
