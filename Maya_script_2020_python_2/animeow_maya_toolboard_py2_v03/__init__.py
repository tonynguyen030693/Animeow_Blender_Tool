# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

# Ho tro reload khi lap trinh trong Maya
try:
    from importlib import reload
except ImportError:
    pass

from .ui import window

def show(tab_index=None, standalone_tab=None):
    """Ham khoi tao chinh de hien thi UI tu Shelf hoac Menu"""
    reload(window)
    window.show_window(tab_index=tab_index, standalone_tab=standalone_tab)
