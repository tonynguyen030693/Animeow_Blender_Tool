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

import compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

class ToolButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()
    delete_requested = QtCore.Signal()
    rename_requested = QtCore.Signal()
    
    def __init__(self, icon_name, label, icon_color, bg_color="#3A3A3A", 
                 icon_manager=None, can_delete=False, parent=None):
        super(ToolButton, self).__init__(parent)
        self.icon_name = icon_name
        self.label_text = label
        self.icon_color = icon_color
        self.bg_color = bg_color
        self.is_selected = False
        self.icon_manager = icon_manager
        self.can_delete = can_delete
        self.setFixedHeight(45)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
        if self.icon_manager:
            self.icon_pixmap = self.icon_manager.create_pixmap(icon_name, 24)
        else:
            self.icon_pixmap = None
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        if self.is_selected:
            bg_color = QtGui.QColor("#4A5F7F")
        else:
            bg_color = QtGui.QColor(self.bg_color)
        
        painter.fillRect(self.rect(), bg_color)
        
        icon_rect = QtCore.QRect(8, 8, 30, 30)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.icon_color)))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(icon_rect, 3, 3)
        
        if self.icon_pixmap and not self.icon_pixmap.isNull():
            icon_x = icon_rect.x() + (icon_rect.width() - self.icon_pixmap.width()) // 2
            icon_y = icon_rect.y() + (icon_rect.height() - self.icon_pixmap.height()) // 2
            painter.drawPixmap(icon_x, icon_y, self.icon_pixmap)
        
        painter.setPen(QtGui.QColor("#CCCCCC"))
        font = painter.font()
        font.setPixelSize(12)
        font.setBold(False)
        painter.setFont(font)
        text_rect = QtCore.QRect(45, 0, self.width() - 45, self.height())
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, self.label_text)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            if self.can_delete:
                self.show_context_menu(event.pos())
        else:
            self.clicked.emit()
    
    def mouseDoubleClickEvent(self, event):
        if self.can_delete:
            self.rename_requested.emit()
    
    def show_context_menu(self, pos):
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
        
        change_icon_action = menu.addAction("Change Icon")
        change_color_action = menu.addAction("Change Color")
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_requested.emit()
        elif action == rename_action:
            self.rename_requested.emit()
        elif action == change_icon_action:
            self.change_icon()
        elif action == change_color_action:
            self.change_color()
    
    def setSelected(self, selected):
        self.is_selected = selected
        self.update()
    
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
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #2B2B2B; }")
        
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
            icons_layout.addWidget(btn, i // 6, i % 6)
        
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
                self.icon_pixmap = self.icon_manager.create_pixmap(new_icon, 24)
                self.update()
                
                parent_widget = self.parent()
                while parent_widget:
                    if hasattr(parent_widget, 'save_data'):
                        parent_widget.save_data()
                        break
                    parent_widget = parent_widget.parent()
    
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
        
        colors_widget = QtWidgets.QWidget()
        colors_layout = QtWidgets.QGridLayout(colors_widget)
        colors_layout.setSpacing(10)
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        for i, (color_hex, color_name) in enumerate(self.icon_manager.available_colors):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(60, 60)
            btn.setCheckable(True)
            btn.setProperty('color_hex', color_hex)
            btn.setStyleSheet("background-color: {0};".format(color_hex))
            
            if color_hex == self.icon_color:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            colors_layout.addWidget(btn, i // 6, i % 6)
        
        layout.addWidget(colors_widget)
        
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
                self.update()
                
                parent_widget = self.parent()
                while parent_widget:
                    if hasattr(parent_widget, 'save_data'):
                        parent_widget.save_data()
                        break
                    parent_widget = parent_widget.parent()
