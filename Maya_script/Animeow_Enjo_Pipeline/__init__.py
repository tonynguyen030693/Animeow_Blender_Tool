# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

# Hỗ trợ reload khi lập trình trong Maya
try:
    from importlib import reload
except ImportError:
    # Python 2 fallback (Maya 2020 Python 2.7)
    pass

from .core import file_manager
from .core import playblast_manager
from .ui import window

def show():
    """Hàm khởi tạo chính để hiển thị UI từ Shelf hoặc Menu"""
    reload(file_manager)
    reload(playblast_manager)
    reload(window)
    window.show_window()
