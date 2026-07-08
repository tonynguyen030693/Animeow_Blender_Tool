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

import maya.cmds as cmds

import compat as compat
QtGui = compat.QtGui
QSvgRenderer = compat.QSvgRenderer

import icon_data as icon_data
AVAILABLE_ICONS = icon_data.AVAILABLE_ICONS
AVAILABLE_COLORS = icon_data.AVAILABLE_COLORS

import icon_svg_data as icon_svg_data
SVG_ICONS = icon_svg_data.SVG_ICONS

import icon_svg_data2 as icon_svg_data2
SVG_ICONS_2 = icon_svg_data2.SVG_ICONS_2

import icon_svg_data3 as icon_svg_data3
SVG_ICONS_3 = icon_svg_data3.SVG_ICONS_3

class IconManager(object):
    
    def __init__(self):
        self.icons_dir = self.get_icons_directory()
        self.ensure_icons_exist()
        self.available_icons = AVAILABLE_ICONS
        self.available_colors = AVAILABLE_COLORS
    
    def get_icons_directory(self):
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        icons_dir = os.path.join(maya_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "icons")
        
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
        
        custom_icons_dir = os.path.join(icons_dir, "custom")
        if not os.path.exists(custom_icons_dir):
            os.makedirs(custom_icons_dir)
        
        return icons_dir
    
    def get_custom_icons_directory(self):
        return os.path.join(self.icons_dir, "custom")
    
    def get_icon_path(self, icon_name):
        custom_path = os.path.join(self.get_custom_icons_directory(), icon_name + '.svg')
        if os.path.exists(custom_path):
            return custom_path
        
        return os.path.join(self.icons_dir, icon_name + '.svg')
    
    def get_available_icons(self):
        icons = []
        
        custom_dir = self.get_custom_icons_directory()
        if os.path.exists(custom_dir):
            for filename in os.listdir(custom_dir):
                if filename.endswith('.svg'):
                    icons.append(filename[:-4])
        
        for icon_name in self.available_icons:
            if icon_name not in icons:
                icon_path = os.path.join(self.icons_dir, icon_name + '.svg')
                if os.path.exists(icon_path):
                    icons.append(icon_name)
        
        return sorted(icons)
    
    def create_pixmap(self, icon_name, size=20):
        icon_path = self.get_icon_path(icon_name)
        
        if os.path.exists(icon_path):
            renderer = QSvgRenderer(icon_path)
            pixmap = QtGui.QPixmap(size, size)
            pixmap.fill(QtGui.QColor(0, 0, 0, 0))
            painter = QtGui.QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap
        
        return QtGui.QPixmap()
    
    def ensure_icons_exist(self):
        all_svg_icons = {}
        all_svg_icons.update(SVG_ICONS)
        all_svg_icons.update(SVG_ICONS_2)
        all_svg_icons.update(SVG_ICONS_3)
        
        for filename, svg_content in all_svg_icons.items():
            filepath = os.path.join(self.icons_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(svg_content)
