"""
DPI Scaling Utilities for High-DPI Display Support
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui


def get_dpi_scale():
    """Get the current DPI scale factor"""
    app = QtWidgets.QApplication.instance()
    if app:
        try:
            screen = app.primaryScreen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                return dpi / 96.0
        except:
            pass
    return 1.0


def scale_size(base_size):
    """Scale a size value based on DPI"""
    return int(base_size * get_dpi_scale())


def scale_font_size(base_size):
    """Scale a font size based on DPI"""
    return int(base_size * get_dpi_scale())
