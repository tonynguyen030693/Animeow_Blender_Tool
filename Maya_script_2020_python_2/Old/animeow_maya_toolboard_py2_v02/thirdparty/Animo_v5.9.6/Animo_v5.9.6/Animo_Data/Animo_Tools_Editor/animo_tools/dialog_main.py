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

# Import modules using versioned import
import compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
get_maya_main_window = compat.get_maya_main_window

import animo_icons as animo_icons
IconManager = animo_icons.IconManager

import animo_widgets as animo_widgets
ToolButton = animo_widgets.ToolButton
ToolItem = animo_widgets.ToolItem

import animo_dialogs as animo_dialogs
ScriptEditorDialog = animo_dialogs.ScriptEditorDialog

import animo_data as animo_data

import tool_defaults as tool_defaults
RECOMMENDED_TOOLS = tool_defaults.RECOMMENDED_TOOLS

import styles as styles

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size


class AnimoToolsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(AnimoToolsDialog, self).__init__(parent)
        
        self.setWindowTitle("Animo Tools Editor")
        self.setFixedSize(scale_size(1000), scale_size(650))
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.icon_manager = IconManager()
        self.custom_tools = []
        self.custom_categories = []
        
        self.setStyleSheet(styles.MAIN_DIALOG_STYLE)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.load_data()
        self.load_recommended_tools()
        
        self.scroll_area.viewport().installEventFilter(self)
        self.tools_widget.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                self.close_all_tooltips()
        return super(AnimoToolsDialog, self).eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.close_all_tooltips()
        super(AnimoToolsDialog, self).mousePressEvent(event)
    
    def close_all_tooltips(self):
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                tool_item = item.widget()
                if hasattr(tool_item, '_active_tooltip') and tool_item._active_tooltip is not None:
                    try:
                        if tool_item._active_tooltip.isVisible():
                            tool_item._active_tooltip.hide_tooltip()
                    except RuntimeError:
                        pass
                    tool_item._active_tooltip = None
    
    def create_widgets(self):
        self.header_title = QtWidgets.QLabel("Animo Tools Editor")
        self.header_title.setStyleSheet("color: #CCCCCC; font-size: {0}px; font-weight: bold;".format(scale_font_size(18)))
        
        self.tools_label = QtWidgets.QLabel("Categories")
        self.tools_label.setStyleSheet("color: #888888; font-size: {0}px; padding: {1}px;".format(scale_font_size(10), scale_size(5)))
        
        self.animo_tools_btn = ToolButton("recommended", "Animo Tools", 
                                         "#5A8AB5", icon_manager=self.icon_manager, can_delete=False)
        
        self.create_category_btn = QtWidgets.QPushButton("+ New Category")
        self.create_category_btn.setStyleSheet(styles.CREATE_CATEGORY_BTN_STYLE)
        
        self.tools_title = QtWidgets.QLabel("Animo Tools")
        self.tools_title.setStyleSheet("color: #888888; font-size: {0}px; padding: {1}px;".format(scale_font_size(11), scale_size(10)))
        
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search tools...")
        self.search_bar.setStyleSheet(styles.SEARCH_BAR_STYLE)
        
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.tools_widget = QtWidgets.QWidget()
        self.tools_layout = QtWidgets.QVBoxLayout(self.tools_widget)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.tools_widget)
        
        self.import_btn = QtWidgets.QPushButton("Import Scripts")
        self.create_tool_btn = QtWidgets.QPushButton("+ Create New Tool")
        self.clear_btn = QtWidgets.QPushButton("Clear Custom Tools")
        self.import_hotkeys_btn = QtWidgets.QPushButton("Import Hotkeys")
        self.export_hotkeys_btn = QtWidgets.QPushButton("Export Hotkeys")
        self.apply_btn = QtWidgets.QPushButton("Apply Hotkeys")
        self.apply_btn.setStyleSheet(styles.APPLY_BTN_STYLE)
        self.close_bottom_btn = QtWidgets.QPushButton("Close")
        self.close_bottom_btn.setStyleSheet(styles.CLOSE_BTN_STYLE)
    
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet("background-color: #2A2A2A;")
        header_widget.setFixedHeight(50)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        left_panel = QtWidgets.QWidget()
        left_panel.setStyleSheet("background-color: #2A2A2A;")
        left_panel.setFixedWidth(250)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 10, 0, 0)
        left_layout.setSpacing(0)
        
        left_layout.addWidget(self.tools_label)
        left_layout.addWidget(self.animo_tools_btn)
        left_layout.addWidget(self.create_category_btn)
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel)
        
        right_panel = QtWidgets.QWidget()
        right_panel.setStyleSheet("background-color: #2B2B2B;")
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        right_layout.addWidget(self.tools_title)
        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.scroll_area)
        
        content_layout.addWidget(right_panel)
        
        main_layout.addLayout(content_layout)
        
        bottom_widget = QtWidgets.QWidget()
        bottom_widget.setStyleSheet("background-color: #353535;")
        bottom_widget.setFixedHeight(60)
        bottom_layout = QtWidgets.QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(15, 10, 15, 10)
        bottom_layout.setSpacing(10)
        
        bottom_layout.addWidget(self.import_btn)
        bottom_layout.addWidget(self.create_tool_btn)
        bottom_layout.addWidget(self.clear_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.import_hotkeys_btn)
        bottom_layout.addWidget(self.export_hotkeys_btn)
        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.close_bottom_btn)
        
        main_layout.addWidget(bottom_widget)
    
    def create_connections(self):
        self.close_bottom_btn.clicked.connect(self.close)
        self.import_btn.clicked.connect(self.import_scripts)
        self.create_tool_btn.clicked.connect(self.create_new_tool)
        self.clear_btn.clicked.connect(self.clear_custom_tools)
        self.create_category_btn.clicked.connect(self.create_new_category)
        self.search_bar.textChanged.connect(self.filter_tools)
        self.apply_btn.clicked.connect(self.apply_all_hotkeys)
        self.import_hotkeys_btn.clicked.connect(self.import_hotkeys)
        self.export_hotkeys_btn.clicked.connect(self.export_hotkeys)
        
        self.animo_tools_btn.clicked.connect(lambda: self.on_tool_selected(self.animo_tools_btn))
        self.animo_tools_btn.setSelected(True)
    
    def on_tool_selected(self, selected_btn):
        self.animo_tools_btn.setSelected(selected_btn == self.animo_tools_btn)
        for category in self.custom_categories:
            category['button'].setSelected(category['button'] == selected_btn)
        
        if selected_btn == self.animo_tools_btn:
            self.tools_title.setText("Animo Tools")
            self.load_recommended_tools()
        else:
            for category in self.custom_categories:
                if category['button'] == selected_btn:
                    self.tools_title.setText(category['name'])
                    self.load_category_tools(category)
                    break
    
    def load_recommended_tools(self):
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for icon_name, color, label, script_data in RECOMMENDED_TOOLS:
            item = ToolItem(icon_name, color, label, script_data, 
                          icon_manager=self.icon_manager, is_custom=False)
            self.tools_layout.addWidget(item)
        
        self.tools_layout.addStretch()
        self.load_hotkeys_from_data()
    
    def load_category_tools(self, category):
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for tool_data in category.get('tools_data', []):
            item = ToolItem(
                tool_data.get('icon', 'smart_key'),
                tool_data.get('color', '#7A8A9A'),
                tool_data['name'],
                {
                    'command': tool_data.get('script', ''),
                    'description': tool_data.get('description', ''),
                    'script_type': tool_data.get('script_type', 'Python')
                },
                icon_manager=self.icon_manager,
                is_custom=True
            )
            self.tools_layout.addWidget(item)
        
        self.tools_layout.addStretch()
        self.load_hotkeys_from_data()
    
    def import_scripts(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Import Scripts", 
            "", 
            "Script Files (*.py *.mel);;Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    script_content = f.read()
                
                script_type = "Python" if file_path.endswith('.py') else "MEL"
                script_name = os.path.basename(file_path).replace('.py', '').replace('.mel', '')
                
                tool_data = {
                    'name': script_name,
                    'description': 'Imported {0} script'.format(script_type),
                    'script': script_content,
                    'script_type': script_type
                }
                
                self.add_custom_tool(tool_data)
            except Exception:
                pass
    
    def create_new_tool(self):
        dialog = ScriptEditorDialog(self)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            
            if not tool_data['name']:
                return
            
            self.add_custom_tool(tool_data)
    
    def add_custom_tool(self, tool_data):
        icon_name = "gear"
        color = "#7A8A9A"
        
        script_command = tool_data['script']
        if tool_data['script_type'] == 'MEL':
            script_command = "import maya.mel as mel; mel.eval('''{0}''')".format(script_command)
        
        tool_entry = {
            'name': tool_data['name'],
            'icon': icon_name,
            'color': color,
            'script': script_command,
            'description': tool_data.get('description', ''),
            'script_type': tool_data['script_type']
        }
        
        added_to_category = False
        for category in self.custom_categories:
            if category['button'].is_selected:
                if 'tools_data' not in category:
                    category['tools_data'] = []
                category['tools_data'].append(tool_entry)
                
                item = ToolItem(
                    icon_name, 
                    color, 
                    tool_data['name'], 
                    {'command': script_command, 'description': tool_data.get('description', ''), 'script_type': tool_data['script_type']},
                    icon_manager=self.icon_manager,
                    is_custom=True
                )
                self.tools_layout.insertWidget(self.tools_layout.count() - 1, item)
                added_to_category = True
                break
        
        if not added_to_category:
            self.custom_tools.append(tool_data)
            item = ToolItem(
                icon_name, 
                color, 
                tool_data['name'], 
                {'command': script_command, 'description': tool_data.get('description', ''), 'script_type': tool_data['script_type']},
                icon_manager=self.icon_manager,
                is_custom=True
            )
            self.tools_layout.insertWidget(self.tools_layout.count() - 1, item)
        
        self.save_data()
    
    def clear_custom_tools(self):
        self.custom_tools.clear()
        self.load_recommended_tools()
    
    def create_new_category(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("New Category")
        dialog.setFixedSize(280, 130)
        dialog.setStyleSheet(styles.CATEGORY_DIALOG_STYLE)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        label = QtWidgets.QLabel("Enter category name:")
        layout.addWidget(label)
        
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("Category name...")
        line_edit.returnPressed.connect(dialog.accept)
        layout.addWidget(line_edit)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setObjectName("okButton")
        ok_btn.setFixedSize(70, 28)
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(70, 28)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        line_edit.setFocus()
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            category_name = line_edit.text()
            
            if category_name:
                new_category_btn = ToolButton(
                    "recommended", 
                    category_name, 
                    "#6A7A8A", 
                    "#3A3A3A",
                    icon_manager=self.icon_manager,
                    can_delete=True
                )
                
                new_category_btn.clicked.connect(lambda: self.on_tool_selected(new_category_btn))
                new_category_btn.delete_requested.connect(lambda: self.delete_category(new_category_btn))
                new_category_btn.rename_requested.connect(lambda: self.rename_category(new_category_btn))
                
                left_layout = self.create_category_btn.parent().layout()
                button_index = left_layout.indexOf(self.create_category_btn)
                left_layout.insertWidget(button_index, new_category_btn)
                
                self.custom_categories.append({
                    'name': category_name,
                    'button': new_category_btn,
                    'tools_data': []
                })
                
                self.save_data()
    
    def filter_tools(self, text):
        text = text.lower()
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    should_show = text in widget.label_text.lower()
                    widget.setVisible(should_show)
    
    def delete_category(self, category_btn):
        for i, category in enumerate(self.custom_categories):
            if category['button'] == category_btn:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Delete Category")
                msg_box.setText("Are you sure you want to delete '{0}'?".format(category['name']))
                msg_box.setInformativeText("All tools in this category will be removed.")
                msg_box.setIcon(QtWidgets.QMessageBox.Question)
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
                msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
                
                for button in msg_box.buttons():
                    button.setFixedSize(65, 26)
                
                reply = msg_box.exec_()
                
                if reply == QtWidgets.QMessageBox.Yes:
                    category_btn.deleteLater()
                    self.custom_categories.pop(i)
                    
                    if category_btn.is_selected:
                        self.animo_tools_btn.clicked.emit()
                    
                    self.save_data()
                break
    
    def rename_category(self, category_btn):
        for category in self.custom_categories:
            if category['button'] == category_btn:
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Rename Category")
                dialog.setFixedSize(280, 130)
                dialog.setStyleSheet(styles.CATEGORY_DIALOG_STYLE)
                
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setContentsMargins(15, 15, 15, 15)
                layout.setSpacing(12)
                
                label = QtWidgets.QLabel("Enter new category name:")
                layout.addWidget(label)
                
                line_edit = QtWidgets.QLineEdit()
                line_edit.setText(category['name'])
                line_edit.selectAll()
                line_edit.returnPressed.connect(dialog.accept)
                layout.addWidget(line_edit)
                
                btn_layout = QtWidgets.QHBoxLayout()
                btn_layout.addStretch()
                
                ok_btn = QtWidgets.QPushButton("OK")
                ok_btn.setObjectName("okButton")
                ok_btn.setFixedSize(70, 28)
                ok_btn.clicked.connect(dialog.accept)
                
                cancel_btn = QtWidgets.QPushButton("Cancel")
                cancel_btn.setFixedSize(70, 28)
                cancel_btn.clicked.connect(dialog.reject)
                
                btn_layout.addWidget(ok_btn)
                btn_layout.addWidget(cancel_btn)
                layout.addLayout(btn_layout)
                
                line_edit.setFocus()
                
                if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    new_name = line_edit.text()
                    if new_name:
                        category['name'] = new_name
                        category_btn.label_text = new_name
                        category_btn.update()
                        
                        if category_btn.is_selected:
                            self.tools_title.setText(new_name)
                        
                        self.save_data()
                break
    
    def save_data(self):
        data = {
            'custom_tools': self.custom_tools,
            'custom_categories': []
        }
        
        for category in self.custom_categories:
            category_data = {
                'name': category['name'],
                'icon': category['button'].icon_name,
                'color': category['button'].icon_color,
                'tools_data': []
            }
            
            if 'tools_data' in category:
                category_data['tools_data'] = category['tools_data']
            
            data['custom_categories'].append(category_data)
        
        animo_data.save_tools_data(data)
    
    def load_data(self):
        data = animo_data.load_tools_data()
        
        self.custom_tools = data.get('custom_tools', [])
        
        for category_data in data.get('custom_categories', []):
            icon = category_data.get('icon', 'recommended')
            color = category_data.get('color', '#6A7A8A')
            
            new_category_btn = ToolButton(
                icon, 
                category_data['name'], 
                color, 
                "#3A3A3A",
                icon_manager=self.icon_manager,
                can_delete=True
            )
            
            new_category_btn.clicked.connect(lambda btn=new_category_btn: self.on_tool_selected(btn))
            new_category_btn.delete_requested.connect(lambda btn=new_category_btn: self.delete_category(btn))
            new_category_btn.rename_requested.connect(lambda btn=new_category_btn: self.rename_category(btn))
            
            left_layout = self.create_category_btn.parent().layout()
            button_index = left_layout.indexOf(self.create_category_btn)
            left_layout.insertWidget(button_index, new_category_btn)
            
            category = {
                'name': category_data['name'],
                'button': new_category_btn,
                'tools_data': category_data.get('tools_data', [])
            }
            
            self.custom_categories.append(category)
        
        self.load_hotkeys_from_data()
    
    def save_hotkeys_to_data(self):
        hotkeys_dict = {}
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    hotkey_text = widget.hotkey_input.text().strip()
                    if hotkey_text:
                        hotkeys_dict[widget.label_text] = hotkey_text
        
        animo_data.save_hotkeys_data(hotkeys_dict)
    
    def load_hotkeys_from_data(self):
        hotkeys_dict = animo_data.load_hotkeys_data()
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    if widget.label_text in hotkeys_dict:
                        widget.hotkey_input.setText(hotkeys_dict[widget.label_text])
    
    def apply_all_hotkeys(self):
        applied_count = 0
        failed_count = 0
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    hotkey_text = widget.hotkey_input.text().strip()
                    if hotkey_text:
                        widget.assign_hotkey()
                        if "background-color: #3A5A3A" in widget.hotkey_input.styleSheet():
                            applied_count += 1
                        else:
                            failed_count += 1
        
        if applied_count > 0 or failed_count > 0:
            msg = "Applied {0} hotkey(s)".format(applied_count)
            if failed_count > 0:
                msg += "\nFailed: {0}".format(failed_count)
            
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Apply Hotkeys")
            msg_box.setText(msg)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in msg_box.buttons():
                button.setFixedSize(65, 26)
            
            msg_box.exec_()
    
    def export_hotkeys(self):
        hotkeys_data = {}
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    hotkey_text = widget.hotkey_input.text().strip()
                    if hotkey_text:
                        hotkeys_data[widget.label_text] = hotkey_text
        
        if not hotkeys_data:
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Hotkeys",
            "animo_hotkeys.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            animo_data.export_hotkeys(file_path, hotkeys_data)
    
    def import_hotkeys(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Hotkeys",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            hotkeys_data = animo_data.import_hotkeys(file_path)
            
            if hotkeys_data:
                for i in range(self.tools_layout.count()):
                    item = self.tools_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, ToolItem):
                            if widget.label_text in hotkeys_data:
                                widget.hotkey_input.setText(hotkeys_data[widget.label_text])
    
    def closeEvent(self, event):
        self.save_data()
        event.accept()
