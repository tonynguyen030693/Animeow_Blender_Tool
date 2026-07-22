# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys

from .core import file_manager
from .core import playblast_manager
from .ui import window
from . import menu

def show():
    """Ham khoi tao chinh de hien thi UI tu Shelf hoac Menu"""
    window.show_window()


