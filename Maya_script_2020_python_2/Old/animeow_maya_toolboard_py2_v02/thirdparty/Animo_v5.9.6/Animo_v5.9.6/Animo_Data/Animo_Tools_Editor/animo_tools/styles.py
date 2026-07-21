from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

# Get directory - use sys._animo_tools_path set by launcher, fallback to __file__
def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size

def get_main_dialog_style():
    return """
    QDialog {{
        background-color: #2B2B2B;
    }}
    QLabel {{
        color: #CCCCCC;
    }}
    QPushButton {{
        background-color: #4A4A4A;
        color: #CCCCCC;
        border: none;
        border-radius: {border_radius}px;
        padding: {padding_v}px {padding_h}px;
        font-size: {font_size}px;
        min-height: {min_height}px;
    }}
    QPushButton:hover {{
        background-color: #555555;
    }}
    QPushButton:pressed {{
        background-color: #3A3A3A;
    }}
    QScrollArea {{
        border: none;
        background-color: #2B2B2B;
    }}
    QScrollBar:vertical {{
        background-color: #2B2B2B;
        width: {scrollbar_width}px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background-color: #4A4A4A;
        border-radius: {scrollbar_radius}px;
        min-height: {scrollbar_min_height}px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: #555555;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
""".format(
        border_radius=scale_size(3),
        padding_v=scale_size(10),
        padding_h=scale_size(20),
        font_size=scale_font_size(11),
        min_height=scale_size(25),
        scrollbar_width=scale_size(12),
        scrollbar_radius=scale_size(6),
        scrollbar_min_height=scale_size(20)
    )

def get_create_category_btn_style():
    return """
    QPushButton {{
        background-color: #3A3A3A;
        color: #CCCCCC;
        border: none;
        border-radius: {border_radius}px;
        padding: {padding}px;
        font-size: {font_size}px;
        margin: {margin}px;
        text-align: left;
    }}
    QPushButton:hover {{
        background-color: #444444;
    }}
""".format(
        border_radius=scale_size(3),
        padding=scale_size(10),
        font_size=scale_font_size(11),
        margin=scale_size(5)
    )

def get_search_bar_style():
    return """
    QLineEdit {{
        background-color: #252525;
        color: #DDDDDD;
        border: 1px solid #444444;
        border-radius: {border_radius}px;
        padding: {padding}px;
        font-size: {font_size}px;
        margin: 0px {margin}px {margin}px {margin}px;
    }}
    QLineEdit:focus {{
        border: 1px solid #6A6A6A;
    }}
""".format(
        border_radius=scale_size(3),
        padding=scale_size(8),
        font_size=scale_font_size(11),
        margin=scale_size(10)
    )

MAIN_DIALOG_STYLE = get_main_dialog_style()
CREATE_CATEGORY_BTN_STYLE = get_create_category_btn_style()
SEARCH_BAR_STYLE = get_search_bar_style()

APPLY_BTN_STYLE = """
    QPushButton {
        background-color: #888888;
        color: #2B2B2B;
        font-weight: bold;
        padding: 8px 16px;
        min-height: 20px;
        max-height: 32px;
    }
    QPushButton:hover {
        background-color: #999999;
    }
"""

CLOSE_BTN_STYLE = """
    QPushButton {
        background-color: #4A4A4A;
        color: #CCCCCC;
        font-weight: bold;
        padding: 8px 16px;
        min-height: 20px;
        max-height: 32px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
"""

MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: #2B2B2B;
    }
    QMessageBox QLabel {
        color: #CCCCCC;
        font-size: 11px;
    }
    QPushButton {
        background-color: #4A4A4A;
        color: #CCCCCC;
        border: none;
        border-radius: 3px;
        padding: 0px;
        font-size: 11px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
"""

CATEGORY_DIALOG_STYLE = """
    QDialog {
        background-color: #2B2B2B;
    }
    QLabel {
        color: #CCCCCC;
        font-size: 11px;
    }
    QLineEdit {
        background-color: #3A3A3A;
        color: #FFFFFF;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 6px;
        font-size: 11px;
    }
    QLineEdit:focus {
        border: 1px solid #6A6A6A;
    }
    QPushButton {
        background-color: #4A4A4A;
        color: #CCCCCC;
        border: none;
        border-radius: 3px;
        padding: 6px 15px;
        font-size: 11px;
        min-height: 20px;
        max-height: 28px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QPushButton#okButton {
        background-color: #B8B8B8;
        color: #2B2B2B;
        font-weight: bold;
    }
    QPushButton#okButton:hover {
        background-color: #C8C8C8;
    }
"""
