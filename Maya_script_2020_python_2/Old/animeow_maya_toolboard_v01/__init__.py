# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

# Hỗ trợ reload khi lập trình trong Maya
try:
    from importlib import reload
except ImportError:
    pass

from .ui import window

def show(tab_index=None, standalone_tab=None):
    """Hàm khởi tạo chính để hiển thị UI từ Shelf hoặc Menu"""
    reload(window)
    window.show_window(tab_index=tab_index, standalone_tab=standalone_tab)
