# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import sys

def force_reload():
    """Xoa sach cache sys.modules cua Animeow_Enjo_Pipeline de dam bao load code python moi 100%"""
    mod_prefix = "Animeow_Enjo_Pipeline"
    modules_to_del = [k for k in sys.modules if k.startswith(mod_prefix)]
    for k in modules_to_del:
        try:
            del sys.modules[k]
        except KeyError:
            pass

from Animeow_Enjo_Pipeline.core import file_manager
from Animeow_Enjo_Pipeline.core import playblast_manager
from Animeow_Enjo_Pipeline.ui import window
from Animeow_Enjo_Pipeline import menu

def show():
    """Ham khoi tao chinh de hien thi UI tu Shelf hoac Menu"""
    window.show_window()

