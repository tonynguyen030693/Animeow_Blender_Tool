from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

# Get directory - use sys._animo_tools_path set by launcher, fallback to __file__
def _get_this_dir():
    # First check if launcher set the path
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    
    # Fallback: try __file__
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    
    # Last resort: use Maya scripts folder
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
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import widget_hotkey_input as widget_hotkey_input
HotkeyLineEdit = widget_hotkey_input.HotkeyLineEdit

import animo_hotkeys as animo_hotkeys

import tooltip_widget as tooltip_widget
AnimoTooltip = tooltip_widget.AnimoTooltip

import tooltip_data as tooltip_data
get_tooltip_data = tooltip_data.get_tooltip_data

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size

class ToolItem(QtWidgets.QWidget):
    delete_requested = QtCore.Signal()
    
    def __init__(self, icon_name, icon_color, label, script_data=None, 
                 icon_manager=None, is_custom=False, parent=None):
        super(ToolItem, self).__init__(parent)
        self.icon_name = icon_name
        self.icon_color = icon_color
        self.label_text = label
        self.script_data = script_data or {}
        self.icon_manager = icon_manager
        self.is_custom = is_custom
        self.setFixedHeight(scale_size(36))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)
        
        self._hover_timer = QtCore.QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_tooltip_at_cursor)
        self._hover_delay = 500
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(scale_size(10), scale_size(5), scale_size(10), scale_size(5))
        layout.setSpacing(scale_size(10))
        
        icon_box_size = scale_size(20)
        icon_size = scale_size(16)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(icon_box_size, icon_box_size)
        self.icon_label.setStyleSheet("background-color: {0}; border-radius: {1}px;".format(icon_color, scale_size(2)))
        
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(icon_name, icon_size)
            if icon_pixmap and not icon_pixmap.isNull():
                self.icon_label.setPixmap(icon_pixmap)
                self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        layout.addWidget(self.icon_label)
        
        self.text_label = QtWidgets.QLabel(label)
        self.text_label.setStyleSheet("color: #DDDDDD; font-size: {0}px;".format(scale_font_size(11)))
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        if self.is_custom:
            self.edit_btn = QtWidgets.QPushButton("Edit")
            self.edit_btn.setFixedWidth(scale_size(80))
            self.edit_btn.setStyleSheet("""
                QPushButton {{
                    background-color: #3A3A3A;
                    color: #FFFFFF;
                    border: none;
                    border-radius: {border_radius}px;
                    padding: {pad_v}px {pad_h}px;
                    font-size: {font_size}px;
                }}
                QPushButton:hover {{
                    background-color: #444444;
                }}
                QPushButton:pressed {{
                    background-color: #2A2A2A;
                }}
            """.format(
                border_radius=scale_size(3),
                pad_v=scale_size(5),
                pad_h=scale_size(10),
                font_size=scale_font_size(11)
            ))
            self.edit_btn.clicked.connect(self.edit_script)
            layout.addWidget(self.edit_btn)
        
        self.tooltip_btn = QtWidgets.QPushButton("Tool Tips")
        self.tooltip_btn.setFixedWidth(scale_size(70))
        self.tooltip_btn.setStyleSheet("""
            QPushButton {{
                background-color: #3A3A3A;
                color: #AAAAAA;
                border: none;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #444444;
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(8),
            font_size=scale_font_size(10)
        ))
        self.tooltip_btn.clicked.connect(self.show_tooltip)
        layout.addWidget(self.tooltip_btn)
        
        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setFixedWidth(scale_size(120))
        self.hotkey_input.setStyleSheet("""
            QLineEdit {{
                background-color: #3A3A3A;
                color: #AAAAAA;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #6A6A6A;
                color: #DDDDDD;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(8),
            font_size=scale_font_size(10)
        ))
        self.hotkey_input.returnPressed.connect(self.assign_hotkey)
        layout.addWidget(self.hotkey_input)
        
        self.shelf_btn = QtWidgets.QPushButton("+ Add to Shelf")
        self.shelf_btn.setFixedWidth(scale_size(120))
        self.shelf_btn.setStyleSheet("""
            QPushButton {{
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: none;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #444444;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(10),
            font_size=scale_font_size(11)
        ))
        self.shelf_btn.clicked.connect(self.add_to_shelf)
        layout.addWidget(self.shelf_btn)
    
    def enterEvent(self, event):
        self._hover_timer.start(self._hover_delay)
        super(ToolItem, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self._hover_timer.stop()
        super(ToolItem, self).leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._hover_timer.stop()
            self._close_all_tooltips_in_parent()
            if not self.childAt(event.pos()):
                self.run_script()
    
    def _close_all_tooltips_in_parent(self):
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'close_all_tooltips'):
            parent_dialog.close_all_tooltips()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.run_script()
    
    def run_script(self):
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            import os
            import marshal
            import re
            
            script_file = self.script_data.get('script_file', '')
            script_name = os.path.splitext(script_file)[0] if script_file else "AnimoTool"
            
            cmds.undoInfo(openChunk=True, chunkName=script_name)
            
            try:
                if script_file:
                    # Use _this_dir which is set at module load time
                    tools_dir = os.path.join(_this_dir, 'tools')
                    script_path = os.path.join(tools_dir, script_file)
                    
                    exec_globals = {
                        '__builtins__': __builtins__,
                        '__name__': '__main__',
                        'cmds': cmds,
                        'mel': mel,
                    }
                    
                    # First check for .py file
                    if os.path.exists(script_path):
                        if tools_dir not in sys.path:
                            sys.path.insert(0, tools_dir)
                        
                        exec_globals['__file__'] = script_path
                        
                        with open(script_path, 'r') as f:
                            script_content = f.read()
                        
                        exec(script_content, exec_globals)
                    else:
                        # Look for versioned .pyc file
                        pyc_path = self._find_pyc_for_maya_version(tools_dir, script_name)
                        
                        if pyc_path and os.path.exists(pyc_path):
                            if tools_dir not in sys.path:
                                sys.path.insert(0, tools_dir)
                            
                            exec_globals['__file__'] = pyc_path
                            
                            with open(pyc_path, 'rb') as f:
                                f.read(16)
                                code = marshal.load(f)
                            
                            exec(code, exec_globals)
                        else:
                            cmds.warning("Script file not found: {0}".format(script_path))
                else:
                    command = self.script_data.get('command', '')
                    if command:
                        exec_globals = {
                            '__builtins__': __builtins__,
                            'cmds': cmds,
                            'mel': mel,
                        }
                        
                        exec(command, exec_globals)
            finally:
                cmds.undoInfo(closeChunk=True)
                self._set_maya_focus()
                
        except Exception as e:
            try:
                cmds.undoInfo(closeChunk=True)
            except:
                pass
            cmds.warning("Error running script: {0}".format(str(e)))
    
    def _find_pyc_for_maya_version(self, tools_dir, script_name):
        import maya.cmds as cmds
        import os
        import re
        
        maya_version = int(cmds.about(version=True)[:4])
        
        versioned_pyc = "{0}_py{1}.pyc".format(script_name, maya_version)
        versioned_path = os.path.join(tools_dir, versioned_pyc)
        if os.path.exists(versioned_path):
            return versioned_path
        
        pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\d{4})\.pyc$', re.IGNORECASE)
        available_versions = []
        
        if os.path.exists(tools_dir):
            for filename in os.listdir(tools_dir):
                match = pattern.match(filename)
                if match:
                    file_version = int(match.group(1))
                    available_versions.append((file_version, filename))
        
        if available_versions:
            available_versions.sort(key=lambda x: x[0], reverse=True)
            
            for file_version, filename in available_versions:
                if file_version <= maya_version:
                    return os.path.join(tools_dir, filename)
            
            oldest_version, oldest_file = available_versions[-1]
            return os.path.join(tools_dir, oldest_file)
        
        generic_pyc = script_name + '.pyc'
        generic_path = os.path.join(tools_dir, generic_pyc)
        if os.path.exists(generic_path):
            return generic_path
        
        return None
    
    def _set_maya_focus(self):
        try:
            import compat
            maya_window = compat.get_maya_main_window()
            if maya_window:
                maya_window.activateWindow()
                maya_window.setFocus()
        except:
            pass
    
    def contextMenuEvent(self, event):
        if not self.is_custom:
            return
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: 1px solid #555555;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #4A4A4A;
            }
        """)
        
        run_action = menu.addAction("Run")
        menu.addSeparator()
        icon_action = menu.addAction("Change Icon")
        color_action = menu.addAction("Change Color")
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(event.globalPos())
        
        if action == run_action:
            self.run_script()
        elif action == icon_action:
            self.change_icon()
        elif action == color_action:
            self.change_color()
        elif action == rename_action:
            self.rename_tool()
        elif action == delete_action:
            self.delete_tool()
    
    def change_icon(self):
        if not self.icon_manager:
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Icon")
        dialog.setFixedSize(520, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #CCCCCC;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border-color: #6A6A6A;
            }
            QPushButton:checked {
                background-color: #5A8AB5;
                border-color: #7AAAD5;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QtWidgets.QLabel("Select an icon:")
        label.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(label)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        icons_widget = QtWidgets.QWidget()
        icons_layout = QtWidgets.QGridLayout(icons_widget)
        icons_layout.setSpacing(10)
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        available_icons = self.icon_manager.get_available_icons()
        
        for i, icon_name in enumerate(available_icons):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(60, 60)
            btn.setCheckable(True)
            btn.setProperty('icon_name', icon_name)
            
            pixmap = self.icon_manager.create_pixmap(icon_name, 32)
            if not pixmap.isNull():
                btn.setIcon(QtGui.QIcon(pixmap))
                btn.setIconSize(QtCore.QSize(32, 32))
            
            if icon_name == self.icon_name:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            icons_layout.addWidget(btn, i // 5, i % 5)
        
        scroll.setWidget(icons_widget)
        layout.addWidget(scroll)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedSize(70, 28)
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(70, 28)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            checked_btn = button_group.checkedButton()
            if checked_btn:
                new_icon = checked_btn.property('icon_name')
                self.icon_name = new_icon
                
                if self.icon_manager:
                    icon_pixmap = self.icon_manager.create_pixmap(new_icon, 16)
                    if icon_pixmap and not icon_pixmap.isNull():
                        self.icon_label.setPixmap(icon_pixmap)
                
                self.update()
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
    
    def change_color(self):
        if not self.icon_manager:
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Color")
        dialog.setFixedSize(490, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #CCCCCC;
            }
            QPushButton {
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                border-color: #6A6A6A;
            }
            QPushButton:checked {
                border: 3px solid #FFFFFF;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QtWidgets.QLabel("Select a color:")
        label.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(label)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        colors_widget = QtWidgets.QWidget()
        colors_layout = QtWidgets.QGridLayout(colors_widget)
        colors_layout.setSpacing(10)
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        for i, (color_hex, color_name) in enumerate(self.icon_manager.available_colors):
            btn = QtWidgets.QPushButton(color_name)
            btn.setFixedSize(80, 40)
            btn.setCheckable(True)
            btn.setProperty('color_hex', color_hex)
            btn.setStyleSheet("background-color: {0}; color: white; font-weight: bold;".format(color_hex))
            
            if color_hex == self.icon_color:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            colors_layout.addWidget(btn, i // 4, i % 4)
        
        scroll.setWidget(colors_widget)
        layout.addWidget(scroll)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedSize(70, 28)
        ok_btn.setStyleSheet("background-color: #4A4A4A; color: #CCCCCC;")
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(70, 28)
        cancel_btn.setStyleSheet("background-color: #4A4A4A; color: #CCCCCC;")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            checked_btn = button_group.checkedButton()
            if checked_btn:
                new_color = checked_btn.property('color_hex')
                self.icon_color = new_color
                self.icon_label.setStyleSheet("background-color: {0}; border-radius: 2px;".format(new_color))
                self.update()
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
    
    def rename_tool(self):
        from .animo_dialogs import ScriptEditorDialog
        
        dialog = ScriptEditorDialog(self, edit_mode=True)
        dialog.setWindowTitle("Rename Tool")
        
        dialog.name_input.setText(self.label_text)
        dialog.description_input.setText(self.script_data.get('description', ''))
        dialog.script_editor.setPlainText(self.script_data.get('command', ''))
        dialog.script_type_combo.setCurrentText(self.script_data.get('script_type', 'Python'))
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            
            self.script_data['command'] = tool_data['script']
            self.script_data['description'] = tool_data['description']
            self.script_data['script_type'] = tool_data['script_type']
            
            if tool_data['name'] != self.label_text:
                self.label_text = tool_data['name']
                self.text_label.setText(tool_data['name'])
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def delete_tool(self):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Delete Tool")
        msg_box.setText("Are you sure you want to delete '{0}'?".format(self.label_text))
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        
        msg_box.setStyleSheet("""
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
        """)
        
        for button in msg_box.buttons():
            button.setFixedSize(65, 26)
        
        reply = msg_box.exec_()
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.deleteLater()
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def add_to_shelf(self):
        try:
            import os
            
            current_shelf = cmds.tabLayout("ShelfLayout", query=True, selectTab=True)
            
            icon_path = ""
            if self.icon_manager:
                icon_path = self.icon_manager.get_icon_path(self.icon_name)
            
            script_file = self.script_data.get('script_file', '')
            
            if script_file:
                animo_tools_dir = _this_dir
                tools_dir = os.path.join(animo_tools_dir, 'tools')
                script_name = os.path.splitext(script_file)[0]
                
                shelf_command = '''import sys
import os
import re
import marshal
import maya.cmds as cmds

def get_maya_version():
    return int(cmds.about(version=True)[:4])

def find_script(tools_dir, script_name):
    maya_version = get_maya_version()
    py_path = os.path.join(tools_dir, script_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    versioned_pyc = os.path.join(tools_dir, script_name + "_py" + str(maya_version) + ".pyc")
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\\d{{4}})\\.pyc$', re.IGNORECASE)
    available = []
    if os.path.exists(tools_dir):
        for f in os.listdir(tools_dir):
            m = pattern.match(f)
            if m:
                available.append((int(m.group(1)), f))
    if available:
        available.sort(reverse=True)
        for v, f in available:
            if v <= maya_version:
                return os.path.join(tools_dir, f), "pyc"
        return os.path.join(tools_dir, available[-1][1]), "pyc"
    generic = os.path.join(tools_dir, script_name + ".pyc")
    if os.path.exists(generic):
        return generic, "pyc"
    return None, None

tools_dir = r"{0}"
script_name = "{1}"
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
path, ftype = find_script(tools_dir, script_name)
if path:
    if ftype == "py":
        with open(path, 'r') as f:
            exec(f.read())
    else:
        with open(path, 'rb') as f:
            f.read(16)
            exec(marshal.load(f))
else:
    cmds.warning("Script not found: " + script_name)
'''.format(tools_dir, script_name)
            else:
                shelf_command = self.script_data.get('command', 'print("Execute: {0}")'.format(self.label_text))
            
            cmds.shelfButton(
                parent=current_shelf,
                image=icon_path if icon_path else "pythonFamily.png",
                command=shelf_command,
                annotation=self.label_text,
                label=self.label_text,
                imageOverlayLabel=self.label_text[:3].upper(),
                sourceType="python"
            )
        except Exception as e:
            import traceback
            print("Error adding to shelf: {0}".format(str(e)))
            traceback.print_exc()
    
    def assign_hotkey(self):
        hotkey_text = self.hotkey_input.text().strip()
        if not hotkey_text:
            return
        
        try:
            import os
            
            script_file = self.script_data.get('script_file', '')
            
            if script_file:
                animo_tools_dir = _this_dir
                tools_dir = os.path.join(animo_tools_dir, 'tools')
                script_name = os.path.splitext(script_file)[0]
                
                command = '''import sys
import os
import re
import marshal
import maya.cmds as cmds

def get_maya_version():
    return int(cmds.about(version=True)[:4])

def find_script(tools_dir, script_name):
    maya_version = get_maya_version()
    py_path = os.path.join(tools_dir, script_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    versioned_pyc = os.path.join(tools_dir, script_name + "_py" + str(maya_version) + ".pyc")
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\\d{{4}})\\.pyc$', re.IGNORECASE)
    available = []
    if os.path.exists(tools_dir):
        for f in os.listdir(tools_dir):
            m = pattern.match(f)
            if m:
                available.append((int(m.group(1)), f))
    if available:
        available.sort(reverse=True)
        for v, f in available:
            if v <= maya_version:
                return os.path.join(tools_dir, f), "pyc"
        return os.path.join(tools_dir, available[-1][1]), "pyc"
    generic = os.path.join(tools_dir, script_name + ".pyc")
    if os.path.exists(generic):
        return generic, "pyc"
    return None, None

tools_dir = r"{0}"
script_name = "{1}"
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
path, ftype = find_script(tools_dir, script_name)
if path:
    if ftype == "py":
        with open(path, 'r') as f:
            exec(f.read())
    else:
        with open(path, 'rb') as f:
            f.read(16)
            exec(marshal.load(f))
else:
    cmds.warning("Script not found: " + script_name)
'''.format(tools_dir, script_name)
                language = "python"
            else:
                command = self.script_data.get('command', 'print("Execute: {0}")'.format(self.label_text))
                script_type = self.script_data.get('script_type', 'Python')
                language = "python" if script_type == "Python" else "mel"
            
            success, message = animo_hotkeys.assign_hotkey(command, hotkey_text, self.label_text, language)
            
            if success:
                self.hotkey_input.setStyleSheet("""
                    QLineEdit {
                        background-color: #3A5A3A;
                        color: #AAFFAA;
                        border: 1px solid #5A8A5A;
                        border-radius: 3px;
                        padding: 5px 8px;
                        font-size: 10px;
                    }
                """)
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_hotkeys_to_data'):
                    parent_dialog.save_hotkeys_to_data()
            else:
                self.hotkey_input.setStyleSheet("""
                    QLineEdit {
                        background-color: #5A3A3A;
                        color: #FFAAAA;
                        border: 1px solid #8A5A5A;
                        border-radius: 3px;
                        padding: 5px 8px;
                        font-size: 10px;
                    }
                """)
            
        except Exception:
            self.hotkey_input.setStyleSheet("""
                QLineEdit {
                    background-color: #5A3A3A;
                    color: #FFAAAA;
                    border: 1px solid #8A5A5A;
                    border-radius: 3px;
                    padding: 5px 8px;
                    font-size: 10px;
                }
            """)
    
    def edit_script(self):
        from .animo_dialogs import ScriptEditorDialog
        
        dialog = ScriptEditorDialog(
            self, 
            edit_mode=True, 
            icon_manager=self.icon_manager,
            current_icon=self.icon_name,
            current_color=self.icon_color
        )
        
        dialog.name_input.setText(self.label_text)
        dialog.description_input.setText(self.script_data.get('description', ''))
        
        command = self.script_data.get('command', '')
        script_type = self.script_data.get('script_type', 'Python')
        
        dialog.script_editor.setPlainText(command)
        dialog.script_type_combo.setCurrentText(script_type)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            
            self.script_data['command'] = tool_data['script']
            self.script_data['description'] = tool_data['description']
            self.script_data['script_type'] = tool_data['script_type']
            
            if 'icon' in tool_data and tool_data['icon'] != self.icon_name:
                self.icon_name = tool_data['icon']
                if self.icon_manager:
                    icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, 16)
                    if icon_pixmap and not icon_pixmap.isNull():
                        self.icon_label.setPixmap(icon_pixmap)
            
            if 'color' in tool_data and tool_data['color'] != self.icon_color:
                self.icon_color = tool_data['color']
                self.icon_label.setStyleSheet("background-color: {0}; border-radius: 2px;".format(self.icon_color))
            
            if tool_data['name'] != self.label_text:
                self.label_text = tool_data['name']
                self.text_label.setText(tool_data['name'])
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def show_tooltip(self):
        if hasattr(self, '_active_tooltip') and self._active_tooltip is not None:
            try:
                if self._active_tooltip.isVisible():
                    self._active_tooltip.hide_tooltip()
                    self._active_tooltip = None
                    return
                else:
                    self._active_tooltip = None
            except RuntimeError:
                self._active_tooltip = None
        
        tooltip_data = get_tooltip_data(self.label_text)
        
        icon_pixmap = None
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, 28)
        
        hotkey_text = self.hotkey_input.text().strip()
        shortcut = tooltip_data.get("shortcut", "")
        if hotkey_text:
            shortcut = hotkey_text
        
        gif_path = ""
        script_file = self.script_data.get('script_file', '')
        if script_file:
            animo_tools_dir = _this_dir
            gifs_dir = os.path.join(animo_tools_dir, 'gifs')
            gif_name = os.path.splitext(script_file)[0] + '.gif'
            potential_gif_path = os.path.join(gifs_dir, gif_name)
            if os.path.exists(potential_gif_path):
                gif_path = potential_gif_path
        
        tooltip = AnimoTooltip()
        tooltip.set_trigger_button(self.tooltip_btn)
        tooltip.set_content(
            title=tooltip_data.get("title", self.label_text),
            description=tooltip_data.get("description", ""),
            info_lines=tooltip_data.get("info_lines", []),
            shortcut=shortcut,
            icon_pixmap=icon_pixmap,
            gif_path=gif_path
        )
        tooltip.show_at_widget(self.tooltip_btn)
        self._active_tooltip = tooltip
    
    def _show_tooltip_at_cursor(self):
        self._close_all_tooltips_in_parent()
        
        tooltip_data = get_tooltip_data(self.label_text)
        
        icon_pixmap = None
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, 28)
        
        hotkey_text = self.hotkey_input.text().strip()
        shortcut = tooltip_data.get("shortcut", "")
        if hotkey_text:
            shortcut = hotkey_text
        
        gif_path = ""
        script_file = self.script_data.get('script_file', '')
        if script_file:
            animo_tools_dir = _this_dir
            gifs_dir = os.path.join(animo_tools_dir, 'gifs')
            gif_name = os.path.splitext(script_file)[0] + '.gif'
            potential_gif_path = os.path.join(gifs_dir, gif_name)
            if os.path.exists(potential_gif_path):
                gif_path = potential_gif_path
        
        tooltip = AnimoTooltip()
        tooltip.set_trigger_button(self.tooltip_btn)
        tooltip.set_source_widget(self)
        tooltip.set_content(
            title=tooltip_data.get("title", self.label_text),
            description=tooltip_data.get("description", ""),
            info_lines=tooltip_data.get("info_lines", []),
            shortcut=shortcut,
            icon_pixmap=icon_pixmap,
            gif_path=gif_path
        )
        tooltip.show_at_cursor()
        self._active_tooltip = tooltip