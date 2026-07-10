from __future__ import absolute_import, division, print_function
import os
import re
import tempfile
import sys
import subprocess
import platform

import maya.cmds as cmds
from maya import OpenMayaUI as omui
import maya.mel as mel

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtGui import QGuiApplication
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtCore, QtWidgets, QtGui
        from PySide2.QtGui import QGuiApplication
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1
        QGuiApplication = QtGui.QApplication

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    int = builtins.int
    str = builtins.str
except Exception:
    pass


def _is_macos():
    return platform.system() == "Darwin"


def _get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except Exception:
        return 2022


def _get_dpi_scale():
    maya_version = _get_maya_version()

    width, height, dpi = 1920, 1080, 96.0
    base_scale = 1.0
    got_screen_info = False

    try:
        app = QtWidgets.QApplication.instance()
        if app:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen()
                if screen:
                    try:
                        dpi = screen.logicalDotsPerInch()
                        geometry = screen.geometry()
                        width = geometry.width()
                        height = geometry.height()
                        got_screen_info = True
                    except (RuntimeError, AttributeError):
                        pass
            else:
                desktop = app.desktop()
                if desktop:
                    try:
                        screen = desktop.screen()
                        if screen:
                            dpi = screen.logicalDpiX()
                            width = screen.width()
                            height = screen.height()
                            got_screen_info = True
                    except (RuntimeError, AttributeError):
                        pass

            if got_screen_info:
                base_scale = dpi / 96.0

    except (RuntimeError, AttributeError):
        pass
    except Exception:
        pass

    if maya_version >= 2025:
        if base_scale > 2.0:
            return max(1.0, min(base_scale * 1.15, 3.0))
        return max(1.0, min(base_scale, 3.0))

    if maya_version >= 2022 and maya_version <= 2024:
        pixel_area = width * height

        if pixel_area >= 33000000:
            return 2.2
        elif pixel_area >= 20000000:
            return 1.9
        elif pixel_area >= 14000000:
            return 1.7
        elif pixel_area >= 8000000:
            return 1.5
        elif pixel_area >= 4500000:
            return 1.35
        else:
            return 1.0

    return max(1.0, min(base_scale, 3.0))


def _scale_size(size):
    return int(size * _get_dpi_scale())


def _scale_font_size(size):
    return int(size * _get_dpi_scale())

def _get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(ptr), QtWidgets.QWidget)


def _icons_dir():
    app_dir = cmds.internalVar(userAppDir=True)
    path = os.path.join(app_dir, "prefs", "icons")
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except Exception:
            pass
    return path


def _draw_icon_png(path, text):
    size = 64
    img = QtGui.QImage(size, size, QtGui.QImage.Format_ARGB32)
    img.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(img)
    painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing, True)

    bg_color = QtGui.QColor(40, 40, 40, 255)
    painter.setBrush(bg_color)
    painter.setPen(QtGui.QPen(QtGui.QColor(90, 90, 90), 2))
    rect = QtCore.QRectF(2, 2, size - 4, size - 4)
    painter.drawRoundedRect(rect, 10, 10)

    painter.setPen(QtCore.Qt.white)
    font = QtGui.QFont()
    font.setBold(True)
    font.setPointSize(20)
    painter.setFont(font)
    painter.drawText(QtCore.QRect(0, 0, size, size), QtCore.Qt.AlignCenter, text)
    painter.end()

    img.save(path, "PNG")


def _ensure_icons():
    icons_folder = _icons_dir()
    ex_icon = os.path.join(icons_folder, "TempEx_quickEx.png")
    imp_icon = os.path.join(icons_folder, "TempEx_quickImp.png")
    if not os.path.isfile(ex_icon):
        _draw_icon_png(ex_icon, "Ex")
    if not os.path.isfile(imp_icon):
        _draw_icon_png(imp_icon, "Imp")
    return ex_icon, imp_icon


def _open_file_location(path):
    if not os.path.exists(path):
        return False
    
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(directory)
        elif system == "Darwin":
            subprocess.Popen(["open", directory])
        else:
            subprocess.Popen(["xdg-open", directory])
        return True
    except Exception:
        return False


class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title="Section", parent=None, start_collapsed=True):
        super(CollapsibleSection, self).__init__(parent)
        self.toggle_btn = QtWidgets.QToolButton(text=title, checkable=True, checked=not start_collapsed)
        self.toggle_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(QtCore.Qt.DownArrow if not start_collapsed else QtCore.Qt.RightArrow)
        self.content = QtWidgets.QWidget()
        self.content.setVisible(not start_collapsed)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_btn)
        lay.addWidget(self.content)

        self.toggle_btn.toggled.connect(self._on_toggled)

    def _on_toggled(self, expanded):
        self.content.setVisible(expanded)
        self.toggle_btn.setArrowType(QtCore.Qt.DownArrow if expanded else QtCore.Qt.RightArrow)

    def setContentLayout(self, layout):
        self.content.setLayout(layout)


class NamespaceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(NamespaceDialog, self).__init__(parent)
        self.setWindowTitle("Import Options")
        self.setMinimumWidth(350)
        
        self.namespace_option = None
        self.namespace_text = ""
        
        self._build_ui()
    
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        info_label = QtWidgets.QLabel("Choose namespace import option:")
        main_layout.addWidget(info_label)
        
        self.no_namespace_radio = QtWidgets.QRadioButton("Import without namespace (clean)")
        self.no_namespace_radio.setChecked(True)
        main_layout.addWidget(self.no_namespace_radio)
        
        self.custom_namespace_radio = QtWidgets.QRadioButton("Import with custom namespace:")
        main_layout.addWidget(self.custom_namespace_radio)
        
        namespace_layout = QtWidgets.QHBoxLayout()
        namespace_layout.addSpacing(30)
        self.namespace_edit = QtWidgets.QLineEdit()
        self.namespace_edit.setPlaceholderText("Enter namespace...")
        self.namespace_edit.setEnabled(False)
        namespace_layout.addWidget(self.namespace_edit)
        main_layout.addLayout(namespace_layout)
        
        self.custom_namespace_radio.toggled.connect(self.namespace_edit.setEnabled)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def accept(self):
        if self.no_namespace_radio.isChecked():
            self.namespace_option = "none"
        else:
            self.namespace_option = "custom"
            self.namespace_text = self.namespace_edit.text().strip()
            if not self.namespace_text:
                return
        
        super(NamespaceDialog, self).accept()
    
    def get_options(self):
        return self.namespace_option, self.namespace_text


class DraggableHeader(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super(DraggableHeader, self).__init__(parent)
        self.parent_window = parent
        self.drag_position = None
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        left_spacer = QtWidgets.QWidget()
        left_spacer.setFixedWidth(_scale_size(22))
        layout.addWidget(left_spacer)
        
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #ffffff; font-weight: normal; font-size: {0}pt; padding: {1}px;".format(_scale_font_size(9), _scale_size(8)))
        layout.addWidget(self.title_label, 1)
        
        self.close_btn = QtWidgets.QPushButton("")
        self.close_btn.setFixedSize(_scale_size(22), _scale_size(22))
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {{
                background-color: #8B0000;
                border: none;
                border-radius: {0}px;
            }}
            QPushButton:hover {{
                background-color: #ff0000;
            }}
            QPushButton:pressed {{
                background-color: #660000;
            }}
        """.format(_scale_size(3)))
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn)
        
        self.setFixedHeight(_scale_size(30))
        self.setStyleSheet("""
            background-color: #1e1e1e;
            border-top-left-radius: {0}px;
            border-top-right-radius: {0}px;
        """.format(_scale_size(6)))
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position is not None:
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_position = None


class TempSelectionSaver(QtWidgets.QDialog):
    ORG = "DFTools"
    APP = "TempSelectionSaver"
    KEY_DIR = "temp_directory"
    KEY_POS = "window_position"

    def __init__(self, parent=None):
        super(TempSelectionSaver, self).__init__(parent or _get_maya_window())
        self.setObjectName("TempEx_UI")
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        if _is_macos():
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        maya_version = _get_maya_version()
        if maya_version >= 2020:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        else:
            self.setStyleSheet("QDialog { background-color: rgb(30, 30, 30); }")
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumWidth(_scale_size(380))
        self.setMaximumWidth(_scale_size(480))
        self.resize(_scale_size(400), _scale_size(420))
        self.settings = QtCore.QSettings(self.ORG, self.APP)
        
        self._apply_stylesheet()

        self._build_ui()
        self._wire_signals()
        self._load_settings()
        self._load_position()
        self.refresh_file_list()

    def _apply_stylesheet(self):
        font_size = _scale_font_size(9)
        padding = _scale_size(6)
        border_radius = _scale_size(3)
        item_padding = _scale_size(4)
        
        self.setStyleSheet("""
            QDialog {{
                background-color: transparent;
            }}
            QGroupBox {{
                color: #cccccc;
                border: 1px solid #3a3a3a;
                border-radius: {0}px;
                margin-top: {1}px;
                padding-top: {1}px;
                font-weight: bold;
                font-size: {2}pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {3}px;
                padding: 0 {4}px;
            }}
            QLabel {{
                color: #cccccc;
                font-size: {2}pt;
            }}
            QLineEdit {{
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: {0}px;
                padding: {5}px;
                font-size: {2}pt;
            }}
            QLineEdit:focus {{
                border: 1px solid #4a9eff;
                background-color: #404040;
            }}
            QPushButton {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: {0}px;
                padding: {4}px {3}px;
                font-weight: normal;
                font-size: {2}pt;
            }}
            QPushButton:hover {{
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }}
            QPushButton:pressed {{
                background-color: #1a1a1a;
            }}
            QListWidget {{
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: {0}px;
                padding: 2px;
                outline: none;
                font-size: {2}pt;
            }}
            QListWidget::item {{
                padding: {6}px;
                border-radius: 2px;
            }}
            QListWidget::item:selected {{
                background-color: #1e90ff;
                color: #000000;
                outline: none;
            }}
            QListWidget::item:hover {{
                background-color: #4a9eff;
                color: #1a1a1a;
            }}
            QListWidget::item:focus {{
                outline: none;
            }}
            QToolButton {{
                background-color: #2d2d2d;
                color: #cccccc;
                border: none;
                padding: 2px;
                font-size: {2}pt;
            }}
            QToolButton:hover {{
                background-color: #3a3a3a;
            }}
        """.format(border_radius, _scale_size(8), font_size, _scale_size(10), _scale_size(5), padding, item_padding))

    def _build_ui(self):
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        container = QtWidgets.QWidget()
        container.setStyleSheet("""
            QWidget {{
                background-color: #1e1e1e;
                border: none;
                border-radius: {0}px;
            }}
        """.format(_scale_size(6)))
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.header = DraggableHeader("Quick Export Selection", self)
        container_layout.addWidget(self.header)
        
        content = QtWidgets.QWidget()
        content.setStyleSheet("background-color: #1e1e1e; border: none;")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(_scale_size(6), _scale_size(6), _scale_size(6), _scale_size(6))
        content_layout.setSpacing(_scale_size(6))

        self.dir_section = CollapsibleSection("Directory", start_collapsed=True)
        dir_content = QtWidgets.QVBoxLayout()
        dir_content.setSpacing(_scale_size(4))

        dir_row = QtWidgets.QHBoxLayout()
        self.dir_edit = QtWidgets.QLineEdit()
        self.dir_edit.setPlaceholderText("Select temp directory...")
        self.dir_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dir_edit.customContextMenuRequested.connect(self.show_dir_context_menu)
        self.dir_browse = QtWidgets.QPushButton("...")
        self.dir_browse.setFixedWidth(_scale_size(30))
        self.dir_browse.setCursor(QtCore.Qt.PointingHandCursor)
        self.dir_browse.setToolTip("Browse for directory")
        dir_row.addWidget(self.dir_edit)
        dir_row.addWidget(self.dir_browse)
        dir_content.addLayout(dir_row)

        dir_btn_row = QtWidgets.QHBoxLayout()
        self.dir_set_btn = QtWidgets.QPushButton("Set")
        self.dir_set_btn.setFixedHeight(_scale_size(24))
        self.dir_set_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.dir_open_btn = QtWidgets.QPushButton("Open")
        self.dir_open_btn.setFixedHeight(_scale_size(24))
        self.dir_open_btn.setCursor(QtCore.Qt.PointingHandCursor)
        dir_btn_row.addWidget(self.dir_set_btn)
        dir_btn_row.addWidget(self.dir_open_btn)
        dir_content.addLayout(dir_btn_row)

        self.dir_section.setContentLayout(dir_content)
        content_layout.addWidget(self.dir_section)

        list_group = QtWidgets.QGroupBox("Files")
        list_layout = QtWidgets.QVBoxLayout(list_group)
        list_layout.setContentsMargins(_scale_size(4), _scale_size(8), _scale_size(4), _scale_size(4))
        list_layout.setSpacing(_scale_size(4))
        
        self.file_list = QtWidgets.QListWidget()
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        list_layout.addWidget(self.file_list)
        
        list_btn_row = QtWidgets.QHBoxLayout()
        list_btn_row.setSpacing(_scale_size(4))
        self.refresh_btn = QtWidgets.QPushButton("R")
        self.refresh_btn.setFixedSize(_scale_size(28), _scale_size(26))
        self.refresh_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.refresh_btn.setToolTip("Refresh file list")
        self.clear_all_btn = QtWidgets.QPushButton("Clear All")
        self.clear_all_btn.setFixedHeight(_scale_size(26))
        self.clear_all_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {{
                background-color: #2a2a2a;
                color: #bbbbbb;
                border: 1px solid #3a3a3a;
                font-size: {0}pt;
            }}
            QPushButton:hover {{
                background-color: #3a3a3a;
                color: #dddddd;
            }}
            QPushButton:pressed {{
                background-color: #1a1a1a;
            }}
        """.format(_scale_font_size(9)))
        list_btn_row.addWidget(self.refresh_btn)
        list_btn_row.addWidget(self.clear_all_btn)
        list_layout.addLayout(list_btn_row)
        
        content_layout.addWidget(list_group, 1)

        self.import_btn = QtWidgets.QPushButton("I M P O R T")
        self.import_btn.setFixedHeight(_scale_size(28))
        self.import_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.import_btn.setStyleSheet("""
            QPushButton {{
                background-color: #4a9eff;
                color: #1a1a1a;
                font-weight: bold;
                font-size: {0}pt;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #6ab0ff;
            }}
            QPushButton:pressed {{
                background-color: #3080e0;
            }}
        """.format(_scale_font_size(10)))
        content_layout.addWidget(self.import_btn)

        export_row = QtWidgets.QHBoxLayout()
        export_row.setSpacing(_scale_size(4))
        self.save_btn = QtWidgets.QPushButton("E X P O R T")
        self.save_btn.setFixedHeight(_scale_size(28))
        self.save_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {{
                background-color: #4a9eff;
                color: #1a1a1a;
                font-weight: bold;
                font-size: {0}pt;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #6ab0ff;
            }}
            QPushButton:pressed {{
                background-color: #3080e0;
            }}
        """.format(_scale_font_size(10)))
        export_row.addWidget(self.save_btn)
        content_layout.addLayout(export_row)

        footer = QtWidgets.QHBoxLayout()
        footer.setSpacing(_scale_size(6))
        self.status_lbl = QtWidgets.QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #999999; font-size: {0}pt;".format(_scale_font_size(9)))
        self.save_opts_btn = QtWidgets.QPushButton("Options")
        self.save_opts_btn.setFixedWidth(_scale_size(70))
        self.save_opts_btn.setFixedHeight(_scale_size(22))
        self.save_opts_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.save_opts_btn.setToolTip("Export options")
        footer.addWidget(self.status_lbl, 1)
        footer.addWidget(self.save_opts_btn)
        content_layout.addLayout(footer)
        
        container_layout.addWidget(content)
        main.addWidget(container)

    def _wire_signals(self):
        self.dir_browse.clicked.connect(self.on_browse)
        self.dir_set_btn.clicked.connect(self.on_set_directory)
        self.dir_open_btn.clicked.connect(self.on_open_location)
        self.save_btn.clicked.connect(self.on_export)
        self.save_opts_btn.clicked.connect(self.on_export_options)
        self.import_btn.clicked.connect(self.on_import)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        self.clear_all_btn.clicked.connect(self.on_clear_all)
        self.file_list.itemDoubleClicked.connect(self.on_import)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)

    def _load_settings(self):
        saved = self.settings.value(self.KEY_DIR, tempfile.gettempdir())
        if sys.version_info.major >= 3:
            saved = str(saved) if saved else tempfile.gettempdir()
        else:
            saved = unicode(saved) if saved else tempfile.gettempdir()
        self.dir_edit.setText(saved)
    
    def _load_position(self):
        pos = self.settings.value(self.KEY_POS)
        if pos:
            self.move(pos)
    
    def _save_position(self):
        self.settings.setValue(self.KEY_POS, self.pos())
    
    def closeEvent(self, event):
        self._save_position()
        super(TempSelectionSaver, self).closeEvent(event)

    def _get_target_dir(self):
        return self.dir_edit.text().strip()

    def _ensure_dir(self, directory):
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
                return True
            except Exception:
                return False
        return True

    def on_browse(self):
        current = self._get_target_dir() or tempfile.gettempdir()
        chosen = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Temp Directory", current)
        if chosen:
            self.dir_edit.setText(chosen)
            if not self._ensure_dir(chosen):
                self._set_status("Cannot create directory: {0}".format(chosen), error=True)
                return
            self.settings.setValue(self.KEY_DIR, chosen)
            self._set_status("Directory set to: {0}".format(chosen))
            self.refresh_file_list()

    def on_set_directory(self):
        directory = self._get_target_dir()
        if not directory:
            self._set_status("Please specify a directory.", error=True)
            return
        if not self._ensure_dir(directory):
            self._set_status("Cannot create directory: {0}".format(directory), error=True)
            return
        self.settings.setValue(self.KEY_DIR, directory)
        self._set_status("Directory set to: {0}".format(directory))
        self.refresh_file_list()

    def on_open_location(self):
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Directory does not exist: {0}".format(directory), error=True)
            return
        
        if _open_file_location(directory):
            self._set_status("Opened: {0}".format(directory))
        else:
            self._set_status("Failed to open directory", error=True)

    def on_export(self):
        directory = self._get_target_dir()
        if not directory or not self._ensure_dir(directory):
            self._set_status("Invalid temp directory.", error=True)
            return
        sel = cmds.ls(sl=True) or []
        if not sel:
            self._set_status("Nothing selected.", error=True)
            return
        base = self._derive_base_from_last_selection(sel)
        filename = self._next_available_filename(directory, base, ext=".ma")
        fullpath = os.path.join(directory, filename)
        if self._export_selection_to(fullpath):
            self._set_status("Exported -> {0}".format(filename))
            self.refresh_file_list()
        else:
            self._set_status("Export failed.", error=True)

    def on_export_options(self):
        try:
            mel.eval("ExportSelectionOptions;")
        except Exception:
            pass

    def on_import(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            self._set_status("No file selected.", error=True)
            return
        
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Invalid directory.", error=True)
            return
        
        namespace_dlg = NamespaceDialog(self)
        if namespace_dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        
        namespace_option, namespace_text = namespace_dlg.get_options()
        
        item = selected_items[0]
        filename = item.text()
        fullpath = os.path.join(directory, filename)
        
        if self._import_file(fullpath, namespace_option, namespace_text):
            self._set_status("Imported: {0}".format(filename))
        else:
            self._set_status("Import failed.", error=True)

    def on_clear_all(self):
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Invalid directory.", error=True)
            return
        
        files = [f for f in os.listdir(directory) if f.lower().endswith(".ma")]
        if not files:
            self._set_status("No files to clear.", error=False)
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Clear All",
            "Are you sure you want to delete all {0} .ma files from the directory?\n\nThis action cannot be undone.".format(len(files)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            deleted_count = 0
            failed_count = 0
            for filename in files:
                fullpath = os.path.join(directory, filename)
                try:
                    os.remove(fullpath)
                    deleted_count += 1
                except Exception:
                    failed_count += 1
            
            self.refresh_file_list()
            if failed_count == 0:
                self._set_status("Cleared {0} files successfully.".format(deleted_count))
            else:
                self._set_status("Cleared {0} files, {1} failed.".format(deleted_count, failed_count), error=True)

    def show_context_menu(self, position):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: {0}px;
                padding: {1}px;
                font-size: {2}pt;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: {3}px {4}px;
                border-radius: 2px;
            }}
            QMenu::item:selected {{
                background-color: #1e90ff;
                color: #000000;
            }}
            QMenu::item:hover {{
                background-color: #1e90ff;
                color: #000000;
            }}
        """.format(_scale_size(4), _scale_size(4), _scale_font_size(9), _scale_size(6), _scale_size(20)))
        
        rename_action = None
        open_location_action = None
        
        if len(selected_items) == 1:
            rename_action = menu.addAction("Rename")
            open_location_action = menu.addAction("Open File Location")
        
        delete_action = menu.addAction("Delete Selected")
        
        action = menu.exec_(self.file_list.mapToGlobal(position))
        
        if action == rename_action and rename_action:
            self.rename_file(selected_items[0])
        elif action == open_location_action and open_location_action:
            self.open_file_location(selected_items[0])
        elif action == delete_action:
            self.delete_selected_files()
    
    def open_file_location(self, item):
        filename = item.text()
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Invalid directory.", error=True)
            return
        
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            self._set_status("File not found: {0}".format(filename), error=True)
            return
        
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.Popen(['explorer', '/select,', filepath])
            elif system == "Darwin":
                subprocess.Popen(['open', '-R', filepath])
            else:
                subprocess.Popen(['xdg-open', directory])
            
            self._set_status("Opened location: {0}".format(filename))
        except Exception as e:
            self._set_status("Failed to open location: {0}".format(str(e)), error=True)
    
    def rename_file(self, item):
        old_filename = item.text()
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Invalid directory.", error=True)
            return
        
        old_filepath = os.path.join(directory, old_filename)
        if not os.path.isfile(old_filepath):
            self._set_status("File not found: {0}".format(old_filename), error=True)
            return
        
        base_name = os.path.splitext(old_filename)[0]
        extension = os.path.splitext(old_filename)[1]
        
        new_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Rename File",
            "Enter new name (without extension):",
            QtWidgets.QLineEdit.Normal,
            base_name
        )
        
        if ok and new_name and new_name.strip():
            new_name = new_name.strip()
            new_filename = new_name + extension
            new_filepath = os.path.join(directory, new_filename)
            
            if os.path.exists(new_filepath):
                return
            
            try:
                os.rename(old_filepath, new_filepath)
                item.setText(new_filename)
                self._set_status("Renamed: {0} -> {1}".format(old_filename, new_filename))
            except Exception as e:
                self._set_status("Failed to rename: {0}".format(str(e)), error=True)
    
    def show_dir_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: {0}px;
                padding: {1}px;
                font-size: {2}pt;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: {3}px {4}px;
                border-radius: 2px;
            }}
            QMenu::item:selected {{
                background-color: #1e90ff;
                color: #000000;
            }}
            QMenu::item:hover {{
                background-color: #1e90ff;
                color: #000000;
            }}
        """.format(_scale_size(4), _scale_size(4), _scale_font_size(9), _scale_size(6), _scale_size(20)))
        
        set_temp_action = menu.addAction("Set to Temp Folder")
        
        action = menu.exec_(self.dir_edit.mapToGlobal(position))
        
        if action == set_temp_action:
            temp_dir = tempfile.gettempdir()
            self.dir_edit.setText(temp_dir)
            if not self._ensure_dir(temp_dir):
                self._set_status("Cannot create directory: {0}".format(temp_dir), error=True)
                return
            self.settings.setValue(self.KEY_DIR, temp_dir)
            self._set_status("Directory set to temp folder: {0}".format(temp_dir))
            self.refresh_file_list()

    def delete_selected_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            self._set_status("Invalid directory.", error=True)
            return
        
        file_count = len(selected_items)
        file_list_text = "\n".join([item.text() for item in selected_items[:5]])
        if file_count > 5:
            file_list_text += "\n... and {0} more".format(file_count - 5)
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete {0} selected file(s)?\n\n{1}\n\nThis action cannot be undone.".format(
                file_count, file_list_text
            ),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            deleted_count = 0
            failed_count = 0
            for item in selected_items:
                filename = item.text()
                fullpath = os.path.join(directory, filename)
                try:
                    os.remove(fullpath)
                    deleted_count += 1
                except Exception:
                    failed_count += 1
            
            self.refresh_file_list()
            if failed_count == 0:
                self._set_status("Deleted {0} file(s) successfully.".format(deleted_count))
            else:
                self._set_status("Deleted {0} file(s), {1} failed.".format(deleted_count, failed_count), error=True)

    def refresh_file_list(self):
        self.file_list.clear()
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            return
        try:
            files = [f for f in os.listdir(directory) if f.lower().endswith(".ma")]
            paths = [os.path.join(directory, f) for f in files]
            paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            for p in paths:
                self.file_list.addItem(os.path.basename(p))
        except Exception:
            pass

    @staticmethod
    def _derive_base_from_last_selection(selection_list):
        last = selection_list[-1]
        last_short = last.split("|")[-1].split(":")[-1]
        base = re.sub(r'[^\w\-.]+', '_', last_short).strip("_") or "selection"
        return base

    @staticmethod
    def _export_selection_to(fullpath):
        try:
            prev_prompt = cmds.file(q=True, prompt=True)
            cmds.file(prompt=False)
            cmds.file(fullpath, force=True, options="", typ="mayaAscii", exportSelected=True)
            return True
        except Exception:
            return False
        finally:
            try:
                cmds.file(prompt=prev_prompt)
            except Exception:
                pass

    def _import_file(self, path, namespace_option="none", namespace_text=""):
        if not os.path.isfile(path):
            self._set_status("File missing: {0}".format(path), error=True)
            return False
        try:
            if namespace_option == "none":
                cmds.file(path, i=True, type="mayaAscii", ignoreVersion=True, ra=True,
                          mergeNamespacesOnClash=False, namespace=":", options="", pr=True)
            else:
                cmds.file(path, i=True, type="mayaAscii", ignoreVersion=True, ra=True,
                          mergeNamespacesOnClash=False, namespace=namespace_text, options="", pr=True)
            return True
        except Exception:
            return False

    @staticmethod
    def _next_available_filename(directory, base, ext=".ma"):
        candidate = os.path.join(directory, base + ext)
        if not os.path.exists(candidate):
            return base + ext
        pattern = re.compile(r"^" + re.escape(base) + r"_(\d{4})" + re.escape(ext) + r"$", re.IGNORECASE)
        max_n = 0
        try:
            for f in os.listdir(directory):
                m = pattern.match(f)
                if m:
                    n = int(m.group(1))
                    if n > max_n:
                        max_n = n
        except Exception:
            pass
        next_n = max_n + 1
        return "{0}_{1:04d}{2}".format(base, next_n, ext)

    def _latest_file_path(self):
        directory = self._get_target_dir()
        if not directory or not os.path.isdir(directory):
            return None
        mas = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(".ma")]
        if not mas:
            return None
        mas.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return mas[0]

    def _set_status(self, msg, error=False):
        font_size = _scale_font_size(9)
        if error:
            self.status_lbl.setStyleSheet("color: #ff4444; font-size: {0}pt;".format(font_size))
        else:
            self.status_lbl.setStyleSheet("color: #4a9eff; font-size: {0}pt;".format(font_size))
        self.status_lbl.setText(msg)

    def showEvent(self, event):
        super(TempSelectionSaver, self).showEvent(event)
        self.refresh_file_list()


_widget_instance = None

def show():
    global _widget_instance
    
    maya_main = _get_maya_window()
    existing = maya_main.findChild(QtWidgets.QDialog, "TempEx_UI")
    if existing:
        try:
            existing.raise_()
            existing.activateWindow()
            return existing
        except RuntimeError:
            pass
    
    if existing:
        try:
            existing.close()
            existing.deleteLater()
        except Exception:
            pass
    
    _widget_instance = TempSelectionSaver()
    _widget_instance.show()
    return _widget_instance

def export_selection_quick():
    ui = TempSelectionSaver()
    directory = ui._get_target_dir()
    if not directory or not ui._ensure_dir(directory):
        return None
    sel = cmds.ls(sl=True) or []
    if not sel:
        return None
    base = ui._derive_base_from_last_selection(sel)
    filename = ui._next_available_filename(directory, base, ext=".ma")
    fullpath = os.path.join(directory, filename)
    if ui._export_selection_to(fullpath):
        return fullpath
    return None

def import_latest():
    ui = TempSelectionSaver()
    latest = ui._latest_file_path()
    if not latest:
        return None
    if ui._import_file(latest, namespace_option="none", namespace_text=""):
        return latest
    return None


if __name__ == "__main__":
    show()