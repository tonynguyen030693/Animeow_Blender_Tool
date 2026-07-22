# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import sys

# Khai bao import o cap module de tuong thich 100% ca Python 2 (Maya 2020) va Python 3 (Maya 2022+)
from .core import file_manager
from .core import playblast_manager
from .ui import window
from . import menu

try:
    from importlib import reload
except ImportError:
    pass

def force_reload():
    """Xoa sach cache sys.modules cua Animeow_Enjo_Pipeline de dam bao load code python moi 100%"""
    mod_prefix = "Animeow_Enjo_Pipeline"
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(mod_prefix) and mod_name != mod_prefix:
            try:
                del sys.modules[mod_name]
            except KeyError:
                pass

def show():
    """Ham khoi tao chinh de hien thi UI tu Shelf hoac Menu"""
    force_reload()
    
    try:
        reload(file_manager)
        reload(playblast_manager)
        reload(window)
        reload(menu)
    except Exception:
        pass
        
    window.show_window()
