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
    
    # Xoá các menu item cũ để tránh bị trùng hoặc thừa nút
    for item in menu_items:
        try:
            lbl = cmds.menuItem(item, query=True, label=True)
            if lbl in ["Anim Combiner Toolboard", "Animeow Toolboard"]:
                cmds.deleteUI(item, menuItem=True)
        except Exception:
            pass
            
    # Lấy lại danh sách sau khi xoá
    menu_items = cmds.menu(MENU_NAME, query=True, itemArray=True) or []
            
    # Thêm dấu gạch phân cách nếu đã có các menu item khác từ trước
    if menu_items:
        cmds.menuItem(divider=True, parent=MENU_NAME)
        
    cmds.menuItem(
        label="Animeow Toolboard",
        command="import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show()",
        image="fileOpen.png",
        parent=MENU_NAME
    )
    print("Đã đăng ký 'Animeow Toolboard' vào menu '%s'." % MENU_LABEL)
