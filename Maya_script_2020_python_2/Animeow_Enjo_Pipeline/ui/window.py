# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import file_manager, playblast_manager

# --- Tu dong them duong dan thirdparty/studiolibrary/src vao sys.path ---
_THIRDPARTY_SRC = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "thirdparty", "studiolibrary", "src")
)
if _THIRDPARTY_SRC not in sys.path:
    sys.path.insert(0, _THIRDPARTY_SRC)

def to_sys_path(path):
    if not path:
        return path
    if isinstance(path, unicode):
        try:
            return path.encode(sys.getfilesystemencoding())
        except Exception:
            return path.encode("utf-8")
    return path

def exception_to_unicode(e):
    try:
        msg = e.message if hasattr(e, 'message') and e.message else ""
        if not msg and e.args:
            msg = e.args[0]
        if isinstance(msg, unicode):
            return msg
        return msg.decode('utf-8', errors='replace')
    except Exception:
        try:
            return str(e).decode('utf-8', errors='replace')
        except Exception:
            return u"Loi ngoai le he thong"

QSS_STYLE = """
QWidget {
    background-color: #2D2D2D;
    color: #E0E0E0;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #444444;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: #FF9800;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
}
QPushButton {
    background-color: #3C3C3C;
    color: #E0E0E0;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4C4C4C;
    border-color: #FF9800;
}
QPushButton:pressed {
    background-color: #222222;
}
QPushButton#accent_btn {
    background-color: #E65100;
    color: #FFFFFF;
    border: 1px solid #FF9800;
}
QPushButton#accent_btn:hover {
    background-color: #F57C00;
}
QPushButton#accent_btn:pressed {
    background-color: #D84315;
}
QPushButton#publish_btn {
    background-color: #1B5E20;
    color: #FFFFFF;
    border: 1px solid #4CAF50;
}
QPushButton#publish_btn:hover {
    background-color: #2E7D32;
}
QPushButton#publish_btn:pressed {
    background-color: #1B5E20;
}
QLineEdit, QComboBox {
    background-color: #1E1E1E;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 6px;
    color: #FFFFFF;
}
QComboBox::drop-down {
    border: none;
}
QListWidget {
    background-color: #1E1E1E;
    border: 1px solid #444444;
    border-radius: 4px;
}
QListWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #282828;
}
QListWidget::item:hover {
    background-color: #3A3A3A;
    color: #FF9800;
}
QListWidget::item:selected {
    background-color: #E65100;
    color: #FFFFFF;
    font-weight: bold;
    color: #FFFFFF;
}
"""

class CreateEpisodeDialog(QtWidgets.QDialog):
    def __init__(self, project, file_manager, parent=None):
        super(CreateEpisodeDialog, self).__init__(parent=parent)
        self.project = project
        self.file_manager = file_manager
        self.setWindowTitle(u"Tao Tap Phim Moi")
        self.setFixedWidth(420)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Tu dong tinh toan tien to du an (vi du KS, LL, EL)
        proj_prefix = self.file_manager.get_episode_abbreviation(self.project, "Sample").split("_")[0]
        
        # Huong dan quy chuan dat ten
        guide_box = QtWidgets.QGroupBox(u"Quy uoc dat ten Tap phim")
        guide_layout = QtWidgets.QVBoxLayout(guide_box)
        guide_label = QtWidgets.QLabel(
            u"<b>Quy tac dat ten Tap phim:</b><br>"
            u"- Viet day du ten tap tieng Anh, dung dau gach duoi thay khoang trang.<br>"
            u"- Ten thu muc tren Server: Viet hoa chu cai dau noi bang dau gach duoi.<br>"
            u"- Ma file Maya: Viet tat chu cai dau + version V02.<br>"
            u"- Vi du: <i>Elevator_Safety_Song_V2</i> &rarr;<br>"
            u"  &bull; Thu muc: <b>Elevator_Safety_Song_V02</b><br>"
            u"  &bull; Ma file: <b>%s_ESS_V02</b>" % proj_prefix
        )
        guide_label.setStyleSheet("color: #FF9800;")
        guide_layout.addWidget(guide_label)
        layout.addWidget(guide_box)
        
        # Nhap ten day du
        layout.addWidget(QtWidgets.QLabel(u"Nhap ten day du cua tap phim (khong dung dau cach):"))
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Elevator_Safety_Song_V2 hoac AAA_25")
        self.name_input.textChanged.connect(self.update_preview)
        layout.addWidget(self.name_input)
        
        # O nhap Ten thu muc Server (Cho phep custom)
        layout.addWidget(QtWidgets.QLabel(u"Ten thu muc se tao tren Server (Co the sua tay):"))
        self.folder_input = QtWidgets.QLineEdit()
        layout.addWidget(self.folder_input)
        
        # O nhap Ma viet tat file Maya (Cho phep custom)
        layout.addWidget(QtWidgets.QLabel(u"Ma viet tat cua file Maya (Co the sua tay):"))
        self.abbrev_input = QtWidgets.QLineEdit()
        self.abbrev_input.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 13px;")
        layout.addWidget(self.abbrev_input)
        
        # Nut bam
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        # Hien thi Preview mac dinh
        self.update_preview("")

    def update_preview(self, text):
        sample_text = text.strip() if text.strip() else "Elevator_Safety_Song_V2"
        folder_name = self.file_manager.get_episode_folder_name(self.project, sample_text)
        abbrev = self.file_manager.get_episode_abbreviation(self.project, folder_name)
        
        self.folder_input.setText(folder_name)
        self.abbrev_input.setText(abbrev)
        
    def get_data(self):
        return self.folder_input.text().strip(), self.abbrev_input.text().strip()

class DebugReportDialog(QtWidgets.QDialog):
    def __init__(self, filepath, report, parent=None):
        super(DebugReportDialog, self).__init__(parent=parent)
        self.setWindowTitle(u"Bao Cao Hieu Nang Mo Canh - %s" % os.path.basename(filepath))
        self.resize(650, 500)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Thong tin tong quan
        summary_group = QtWidgets.QGroupBox(u"Tong quan thoi gian nap")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        summary_layout.setSpacing(6)
        
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>Tong thoi gian mo canh:</b> %.2f giay" % report["total_time"]))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>File canh goc (Khong Reference):</b> %.2f giay" % report["base_scene_time"]))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>So luong Reference:</b> %d" % len(report["references"])))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>So luong Script Nodes:</b> %d" % len(report["script_nodes"])))
        
        layout.addWidget(summary_group)
        
        # 2. Chi tiet cac Reference
        ref_group = QtWidgets.QGroupBox(u"Chi tiet thoi gian nap tung Reference")
        ref_layout = QtWidgets.QVBoxLayout(ref_group)
        
        self.ref_table = QtWidgets.QTableWidget()
        self.ref_table.setColumnCount(3)
        self.ref_table.setHorizontalHeaderLabels([u"Ten Node / File", u"Thoi gian", u"Trang thai"])
        self.ref_table.horizontalHeader().setStretchLastSection(True)
        
        self.ref_table.setRowCount(len(report["references"]))
        for i, ref in enumerate(report["references"]):
            name = ref["node"] if ref["node"] else os.path.basename(ref["filepath"])
            time_item = QtWidgets.QTableWidgetItem("%.2fs" % ref["time"])
            status_item = QtWidgets.QTableWidgetItem(ref["status"])
            
            # To mau do neu load lau (> 5.0 giay)
            if ref["time"] > 5.0:
                time_item.setForeground(QtGui.QColor("#FF1744"))
                time_item.setFont(QtGui.QFont("", -1, QtGui.QFont.Bold))
                
            name_item = QtWidgets.QTableWidgetItem(name)
            name_item.setToolTip(ref["filepath"])
            
            self.ref_table.setItem(i, 0, name_item)
            self.ref_table.setItem(i, 1, time_item)
            self.ref_table.setItem(i, 2, status_item)
            
        ref_layout.addWidget(self.ref_table)
        layout.addWidget(ref_group)
        
        # 3. Chi tiet cac Script Nodes
        if report["script_nodes"]:
            script_group = QtWidgets.QGroupBox(u"Danh sach Script Nodes trong Scene (Canh bao Virus/Script chay ngam)")
            script_layout = QtWidgets.QVBoxLayout(script_group)
            
            self.script_list = QtWidgets.QListWidget()
            for script in report["script_nodes"]:
                item_text = u"%s (Type: %d) - Code: %s" % (script["name"], script["type"], script["preview"])
                item = QtWidgets.QListWidgetItem(item_text)
                self.script_list.addItem(item)
            script_layout.addWidget(self.script_list)
            layout.addWidget(script_group)
            
        # Nut dong
        close_btn = QtWidgets.QPushButton(u"Dong")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class StudioLibraryManagerDialog(QtWidgets.QDialog):
    """Cua so Quan ly cac Thu vien Studio Library cua cac du an"""
    def __init__(self, main_ui, parent=None):
        super(StudioLibraryManagerDialog, self).__init__(parent=parent)
        self.main_ui = main_ui
        self.setWindowTitle(u"Studio Library Manager - Quan Ly Thu Vien Du An")
        self.setMinimumSize(600, 380)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        
        header_lbl = QtWidgets.QLabel(u"<b>Danh sach cac Thu vien Studio Library dang quan ly:</b>")
        layout.addWidget(header_lbl)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([u"Ten Thu Vien", u"Duong dan (Path)", u"Trang thai"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        # Danh sach thu vien mac dinh cua du an
        self.libraries = [
            {"name": u"🎬 Studio Library Tong", "path": "Z:\\Animeow_Production\\Enjo_Library"},
            {"name": u"👤 01_Characters", "path": "Z:\\Animeow_Production\\Enjo_Library\\01_Characters"},
            {"name": u"🐾 02_Animals", "path": "Z:\\Animeow_Production\\Enjo_Library\\02_Animals"},
            {"name": u"🚗 03_Props_Vehicles", "path": "Z:\\Animeow_Production\\Enjo_Library\\03_Props_Vehicles"},
            {"name": u"✋ 04_Common_Library", "path": "Z:\\Animeow_Production\\Enjo_Library\\04_Common_Library"},
            {"name": u"🎨 05_User_Scratch", "path": "Z:\\Animeow_Production\\Enjo_Library\\05_User_Scratch"},
        ]
        
        # Them Thu vien cua Shot hien tai neu co
        current_proj = self.main_ui.proj_combo.currentText() if hasattr(self.main_ui, 'proj_combo') else ""
        current_ep = self.main_ui.ep_combo.currentText() if hasattr(self.main_ui, 'ep_combo') else ""
        if current_proj and current_ep:
            shot_sl_dir = self.main_ui.file_manager.get_studiolibrary_dir(current_proj, current_ep)
            if shot_sl_dir:
                self.libraries.append({
                    "name": u"Shot Library (%s)" % current_ep,
                    "path": shot_sl_dir
                })
                
        self.populate_table()
        
        # Hang nut thao tac
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.open_btn = QtWidgets.QPushButton(u"🚀 Mo Thu Vien Duoc Chon")
        self.open_btn.setObjectName("accent_btn")
        self.open_btn.clicked.connect(self.on_open_selected)
        btn_layout.addWidget(self.open_btn)
        
        self.explore_btn = QtWidgets.QPushButton(u"📂 Mo Folder Explorer")
        self.explore_btn.clicked.connect(self.on_explore_selected)
        btn_layout.addWidget(self.explore_btn)
        
        self.add_custom_btn = QtWidgets.QPushButton(u"➕ Them Thu Vien Custom...")
        self.add_custom_btn.clicked.connect(self.on_add_custom)
        btn_layout.addWidget(self.add_custom_btn)
        
        self.organize_btn = QtWidgets.QPushButton(u"🧹 Sap Xep Chuan Hoa Folder")
        self.organize_btn.setToolTip(u"Tu dong gom va sap xep cac folder trong Thu vien duoc chon ve dung cau truc chuan (01_Characters, 02_Animals...)")
        self.organize_btn.clicked.connect(self.on_organize_selected)
        btn_layout.addWidget(self.organize_btn)
        
        layout.addLayout(btn_layout)
        
    def populate_table(self):
        self.table.setRowCount(len(self.libraries))
        for i, lib in enumerate(self.libraries):
            name_item = QtWidgets.QTableWidgetItem(lib["name"])
            name_item.setFont(QtGui.QFont("", -1, QtGui.QFont.Bold))
            path_item = QtWidgets.QTableWidgetItem(lib["path"])
            
            exists = os.path.exists(lib["path"])
            status_str = u"🟢 San sang" if exists else u"🟡 Tu khoi tao"
            status_item = QtWidgets.QTableWidgetItem(status_str)
            if exists:
                status_item.setForeground(QtGui.QColor("#4CAF50"))
            else:
                status_item.setForeground(QtGui.QColor("#FF9800"))
                
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, path_item)
            self.table.setItem(i, 2, status_item)
            
    def on_open_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.libraries):
            row = 0
        lib = self.libraries[row]
        self.accept()
        self.main_ui.on_open_studio_library(library_path=lib["path"], library_name=lib["name"])
        
    def on_explore_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.libraries):
            return
        lib = self.libraries[row]
        self.main_ui.open_folder_explorer(lib["path"])
        
    def on_add_custom(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, u"Chon thu muc Studio Library Custom")
        if not path:
            return
        path = os.path.normpath(path)
        name, ok = QtWidgets.QInputDialog.getText(self, u"Ten Thu Vien", u"Nhap ten hien thi cho Thu vien:")
        if not (ok and name.strip()):
            name = os.path.basename(path)
            
        self.libraries.append({"name": name.strip(), "path": path})
        self.populate_table()

    def on_organize_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.libraries):
            row = 0
        lib = self.libraries[row]
        proj_name = "KidSong" if "kidsong" in lib["name"].lower() else "Lolo"
        
        ok, msg = self.main_ui.file_manager.organize_studio_library(proj_name)
        if ok:
            QtWidgets.QMessageBox.information(self, u"Chuan hoa Thanh Cong", msg)
            self.populate_table()
        else:
            QtWidgets.QMessageBox.warning(self, u"Thong bao", msg)


class AnimeowMayaToolkitUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Animeow Enjo Pipeline"
    WORKSPACE_CONTROL_NAME = "AnimeowEnjoPipelineWorkspaceControl"
    OPTION_VAR_PROJ = "AnimeowEnjoProjRoot"
    OPTION_VAR_REF_MODE = "AnimeowEnjoRefLoadMode"

    def __init__(self, parent=None):
        super(AnimeowMayaToolkitUI, self).__init__(parent=parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setStyleSheet(QSS_STYLE)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.project_root = "Z:\\Animeow_Production"
        self.current_work_files = []
        
        # Khoi tao class quan ly
        self.file_manager = file_manager.FileManager(project_root=self.project_root)
        self.playblast_manager = playblast_manager.PlayblastManager()
        
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # ========================================================
        # Tab chinh: Quan ly File & Playblast (Tab 1) + Split/Merge (Tab 2)
        # ========================================================
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                background: #3C3C3C; color: #BBBBBB;
                padding: 8px 18px; border: 1px solid #555;
                border-bottom: none; border-top-left-radius: 6px;
                border-top-right-radius: 6px; font-weight: bold;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2D2D2D; color: #FF9800;
                border-bottom: 2px solid #FF9800;
            }
            QTabBar::tab:hover:!selected {
                background: #4C4C4C; color: #FFB74D;
            }
        """)
        self.main_layout.addWidget(self.tab_widget)

        # --- TAB 1: Quan Ly File & Playblast ---
        tab1_widget = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1_widget)
        tab1_layout.setContentsMargins(5, 5, 5, 5)
        tab1_layout.setSpacing(10)
        self.tab_widget.addTab(tab1_widget, u"📂 Quan Ly File & Playblast")
        self._build_tab1_contents(tab1_layout)

        # --- TAB 2: Tach / Gop Canh ---
        tab2_widget = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2_widget)
        tab2_layout.setContentsMargins(5, 5, 5, 5)
        tab2_layout.setSpacing(10)
        self.tab_widget.addTab(tab2_widget, u"✂️ Tach / Gop Canh")
        self._build_tab2_split_merge(tab2_layout)

    def _build_tab1_contents(self, parent_layout):
        """Xay dung noi dung Tab 1 - Quan Ly File & Playblast (giu nguyen giao dien cu)"""
        # 1. Khoi Du An & File nhap
        shot_group = QtWidgets.QGroupBox()
        shot_layout = QtWidgets.QGridLayout(shot_group)
        shot_layout.setContentsMargins(8, 8, 8, 8)
        shot_layout.setSpacing(8)
        
        # Hang 0: Header gia lap voi nut Refresh o goc phai
        header_layout = QtWidgets.QHBoxLayout()
        header_label = QtWidgets.QLabel(u"Quan Ly File (Pipeline)")
        header_label.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 12px;")
        header_layout.addWidget(header_label)
        
        self.refresh_btn = QtWidgets.QPushButton(u"🔄 Lam moi")
        self.refresh_btn.setToolTip("Lam moi danh sach file tu Server")
        self.refresh_btn.setFixedWidth(110)
        self.refresh_btn.setFixedHeight(26)
        self.refresh_btn.clicked.connect(self.on_refresh)
        header_layout.addWidget(self.refresh_btn, 0, QtCore.Qt.AlignRight)
        
        shot_layout.addLayout(header_layout, 0, 0, 1, 3)
        
        # Hang 1: Project
        shot_layout.addWidget(QtWidgets.QLabel("Project:"), 1, 0)
        self.proj_combo = QtWidgets.QComboBox()
        self.proj_combo.currentIndexChanged.connect(self.on_proj_changed)
        shot_layout.addWidget(self.proj_combo, 1, 1, 1, 2)
        
        # Hang 2: Episode
        shot_layout.addWidget(QtWidgets.QLabel("Episode:"), 2, 0)
        self.ep_combo = QtWidgets.QComboBox()
        self.ep_combo.currentIndexChanged.connect(self.on_ep_changed)
        shot_layout.addWidget(self.ep_combo, 2, 1)
        
        self.create_ep_btn = QtWidgets.QPushButton("➕ Tap")
        self.create_ep_btn.setToolTip("Tao tap phim moi (Danh cho Leader)")
        self.create_ep_btn.clicked.connect(self.on_create_episode)
        shot_layout.addWidget(self.create_ep_btn, 2, 2)
        
        # Nhan canh bao quy chuan ten Episode (Hang 3)
        self.ep_warning_label = QtWidgets.QLabel("")
        self.ep_warning_label.setStyleSheet("color: #FF9800; font-weight: bold; margin-left: 5px;")
        self.ep_warning_label.setVisible(False)
        shot_layout.addWidget(self.ep_warning_label, 3, 0, 1, 3)
        
        # Hang 4: Task (Khau)
        shot_layout.addWidget(QtWidgets.QLabel("Task:"), 4, 0)
        self.task_combo = QtWidgets.QComboBox()
        self.task_combo.addItems(["Layout", "Animation"])
        self.task_combo.currentIndexChanged.connect(self.on_task_changed)
        shot_layout.addWidget(self.task_combo, 4, 1)
        
        self.create_file_btn = QtWidgets.QPushButton("➕ Tao File")
        self.create_file_btn.setToolTip("Tao file nhap moi cho Khau hien tai")
        self.create_file_btn.clicked.connect(self.on_create_file)
        shot_layout.addWidget(self.create_file_btn, 4, 2)
        
        # Hang 5: Label Danh sach file & Dropdown tuy chon nap Reference
        files_label_layout = QtWidgets.QHBoxLayout()
        files_label_layout.addWidget(QtWidgets.QLabel("Working Files (Dup click de Mo):"))
        
        self.ref_load_combo = QtWidgets.QComboBox()
        self.ref_load_combo.addItems([
            u"⚡ Mo nhanh (Khong load Ref)",
            u"👤 Nap Nhan vat & Camera (Characters & Cameras)",
            u"📋 Tu chon Ref (Selective Preload)",
            u"🔝 Chi nap Ref cap 1 (Top Level)",
            u"🔄 Mo binh thuong (Nap tat ca)"
        ])
        self.ref_load_combo.setToolTip(u"Che do tai Reference khi mo file Maya.")
        self.ref_load_combo.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.ref_load_combo.setFixedWidth(240)
        self.ref_load_combo.currentIndexChanged.connect(self.save_ref_load_setting)
        files_label_layout.addWidget(self.ref_load_combo, 0, QtCore.Qt.AlignRight)
        
        shot_layout.addLayout(files_label_layout, 5, 0, 1, 3)
        
        # Hang 6: Bo cuc 3 bang (Shot ben trai, Maya Version o giua, Playblast Videos ben phai)
        list_container_layout = QtWidgets.QHBoxLayout()
        list_container_layout.setSpacing(6)
        
        # Bang ben trai: Shot List
        shot_list_widget = QtWidgets.QWidget()
        shot_list_layout = QtWidgets.QVBoxLayout(shot_list_widget)
        shot_list_layout.setContentsMargins(0, 0, 0, 0)
        shot_list_layout.addWidget(QtWidgets.QLabel(u"🎬 Danh sach Shot:"))
        
        self.shot_list = QtWidgets.QListWidget()
        self.shot_list.itemSelectionChanged.connect(self.on_shot_selection_changed)
        self.shot_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.shot_list.customContextMenuRequested.connect(self.show_shot_list_context_menu)
        shot_list_layout.addWidget(self.shot_list)
        
        # Bang o giua: Maya File Version List
        version_list_widget = QtWidgets.QWidget()
        version_list_layout = QtWidgets.QVBoxLayout(version_list_widget)
        version_list_layout.setContentsMargins(0, 0, 0, 0)
        version_list_layout.addWidget(QtWidgets.QLabel(u"📂 File Maya (Dup click mo):"))
        
        self.files_list = QtWidgets.QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_open_file)
        self.files_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.files_list.customContextMenuRequested.connect(self.show_file_list_context_menu)
        self.files_list.itemSelectionChanged.connect(self.update_playblast_count)
        version_list_layout.addWidget(self.files_list)
        
        # Bang ben phai: Playblast Videos List
        pb_list_widget = QtWidgets.QWidget()
        pb_list_layout = QtWidgets.QVBoxLayout(pb_list_widget)
        pb_list_layout.setContentsMargins(0, 0, 0, 0)
        pb_list_layout.addWidget(QtWidgets.QLabel(u"🎥 Playblasts (Dup click xem):"))
        
        self.pb_list = QtWidgets.QListWidget()
        self.pb_list.itemDoubleClicked.connect(self.on_open_playblast_file)
        self.pb_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.pb_list.customContextMenuRequested.connect(self.show_pb_list_context_menu)
        pb_list_layout.addWidget(self.pb_list)
        
        list_container_layout.addWidget(shot_list_widget, 3) # Chiem 30% chieu rong
        list_container_layout.addWidget(version_list_widget, 4) # Chiem 40% chieu rong
        list_container_layout.addWidget(pb_list_widget, 3) # Chiem 30% chieu rong
        
        shot_layout.addLayout(list_container_layout, 6, 0, 1, 3)
        
        # Hang 7: Nut mo nhanh thu muc
        folder_btn_layout = QtWidgets.QHBoxLayout()
        folder_btn_layout.setSpacing(6)
        
        self.open_ep_dir_btn = QtWidgets.QPushButton(u"📂 Tap phim")
        self.open_ep_dir_btn.setToolTip("Mo thu muc goc cua Tap phim tren Server")
        self.open_ep_dir_btn.clicked.connect(self.on_open_ep_dir)
        
        self.open_work_dir_btn = QtWidgets.QPushButton(u"📂 Khau lam viec")
        self.open_work_dir_btn.setToolTip("Mo thu muc chua file Maya lam viec cua khau hien tai")
        self.open_work_dir_btn.clicked.connect(self.on_open_work_dir)
        
        self.open_pub_dir_btn = QtWidgets.QPushButton(u"📂 Xuan ban")
        self.open_pub_dir_btn.setToolTip("Mo thu muc chua file da Publish cua khau hien tai")
        self.open_pub_dir_btn.clicked.connect(self.on_open_pub_dir)
        
        self.open_mov_dir_btn = QtWidgets.QPushButton(u"📂 Playblast")
        self.open_mov_dir_btn.setToolTip("Mo thu muc chua video Playblast nhap cua khau hien tai")
        self.open_mov_dir_btn.clicked.connect(self.on_open_mov_dir)
        
        folder_btn_layout.addWidget(self.open_ep_dir_btn)
        folder_btn_layout.addWidget(self.open_work_dir_btn)
        folder_btn_layout.addWidget(self.open_pub_dir_btn)
        folder_btn_layout.addWidget(self.open_mov_dir_btn)
        
        shot_layout.addLayout(folder_btn_layout, 7, 0, 1, 3)
        
        # Hang 8: Cac nut bam luu/publish
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.save_version_btn = QtWidgets.QPushButton("Luu Phien Ban Moi (+1)")
        self.save_version_btn.setObjectName("accent_btn")
        self.save_version_btn.clicked.connect(self.on_increment_save)
        btn_layout.addWidget(self.save_version_btn)

        self.save_current_btn = QtWidgets.QPushButton(u"💾 Luu Canh Vao Pipeline")
        self.save_current_btn.setToolTip(u"Luu file Maya dang mo hien tai vao kho du an (Project -> Episode -> Task -> Shot)")
        self.save_current_btn.clicked.connect(self.on_save_current_scene_to_pipeline)
        btn_layout.addWidget(self.save_current_btn)
        
        shot_layout.addLayout(btn_layout, 8, 0, 1, 3)
        
        # Hang 9: Nut Kiem tra quy chuan
        self.check_naming_btn = QtWidgets.QPushButton("🔍 Kiem tra quy chuan ten File")
        self.check_naming_btn.setToolTip("Quet toan bo tap phim va tu dong sua cac file dat ten sai quy chuan")
        self.check_naming_btn.clicked.connect(self.on_check_filenames)
        shot_layout.addWidget(self.check_naming_btn, 9, 0, 1, 3)
        
        parent_layout.addWidget(shot_group)
        
        # 2. Khoi Playblast
        playblast_group = QtWidgets.QGroupBox("Auto Playblast Nhap")
        playblast_layout = QtWidgets.QGridLayout(playblast_group)
        playblast_layout.setContentsMargins(8, 8, 8, 8)
        playblast_layout.setSpacing(8)
        
        playblast_layout.addWidget(QtWidgets.QLabel("Format:"), 0, 0)
        self.pb_format_combo = QtWidgets.QComboBox()
        self.pb_format_combo.addItems(["QuickTime (.mov)", "AVI (.avi)"])
        playblast_layout.addWidget(self.pb_format_combo, 0, 1)
        
        playblast_layout.addWidget(QtWidgets.QLabel("Resolution:"), 1, 0)
        self.pb_res_combo = QtWidgets.QComboBox()
        self.pb_res_combo.addItems(["1920x1080 (HD 1080)", "1280x720 (HD 720)", "640x360"])
        playblast_layout.addWidget(self.pb_res_combo, 1, 1)
        
        # Them cau hinh Camera
        playblast_layout.addWidget(QtWidgets.QLabel("Camera:"), 2, 0)
        self.pb_cam_mode_combo = QtWidgets.QComboBox()
        self.pb_cam_mode_combo.addItems([
            u"Camera hien hanh (Active)", 
            u"Tuy chon 1 Camera", 
            u"Xuat nhieu Camera (Batch)"
        ])
        self.pb_cam_mode_combo.currentIndexChanged.connect(self.on_pb_cam_mode_changed)
        playblast_layout.addWidget(self.pb_cam_mode_combo, 2, 1)
        
        # Cau hinh chon 1 camera (Single)
        self.pb_single_cam_widget = QtWidgets.QWidget()
        single_cam_layout = QtWidgets.QHBoxLayout(self.pb_single_cam_widget)
        single_cam_layout.setContentsMargins(0, 0, 0, 0)
        single_cam_layout.setSpacing(6)
        
        self.pb_single_cam_combo = QtWidgets.QComboBox()
        single_cam_layout.addWidget(self.pb_single_cam_combo)
        
        self.pb_refresh_cams_btn = QtWidgets.QPushButton(u"🔄")
        self.pb_refresh_cams_btn.setToolTip(u"Lam moi danh sach camera trong scene")
        self.pb_refresh_cams_btn.setFixedWidth(30)
        self.pb_refresh_cams_btn.setFixedHeight(24)
        self.pb_refresh_cams_btn.clicked.connect(self.refresh_camera_list)
        single_cam_layout.addWidget(self.pb_refresh_cams_btn)
        
        playblast_layout.addWidget(self.pb_single_cam_widget, 3, 0, 1, 2)
        
        # Cau hinh chon nhieu camera (Multi)
        self.pb_multi_cam_list = QtWidgets.QListWidget()
        self.pb_multi_cam_list.setFixedHeight(100)
        playblast_layout.addWidget(self.pb_multi_cam_list, 4, 0, 1, 2)
        
        # Checkbox De len ban cu
        self.pb_overwrite_checkbox = QtWidgets.QCheckBox(u"De len ban cu (Khong luu Old)")
        self.pb_overwrite_checkbox.setToolTip(u"Neu tich chon, video moi se ghi de truc tiep len video cu.\nNeu khong tich, ban cu se duoc di chuyen vao thu muc Old.")
        self.pb_overwrite_checkbox.setStyleSheet("margin-left: 2px;")
        playblast_layout.addWidget(self.pb_overwrite_checkbox, 5, 0, 1, 2)
        
        # Nhan hien thi trang thai Playblast
        self.pb_count_label = QtWidgets.QLabel(u"Trang thai Playblast: Chua kiem tra")
        self.pb_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 2px;")
        playblast_layout.addWidget(self.pb_count_label, 6, 0, 1, 2)
        
        # Hang nut: Chay Playblast va Mo thu muc
        pb_buttons_layout = QtWidgets.QHBoxLayout()
        pb_buttons_layout.setSpacing(6)
        
        self.run_pb_btn = QtWidgets.QPushButton("🎬 Run Playblast")
        self.run_pb_btn.setObjectName("accent_btn")
        self.run_pb_btn.clicked.connect(self.on_run_playblast)
        pb_buttons_layout.addWidget(self.run_pb_btn, 7)
        
        self.pb_open_folder_btn = QtWidgets.QPushButton("📂 Open Folder")
        self.pb_open_folder_btn.setToolTip("Open Playblast folder on Server")
        self.pb_open_folder_btn.clicked.connect(self.on_open_mov_dir)
        pb_buttons_layout.addWidget(self.pb_open_folder_btn, 3)
        
        playblast_layout.addLayout(pb_buttons_layout, 7, 0, 1, 2)
        
        # Trang thai an/hien ban dau
        self.pb_single_cam_widget.setVisible(False)
        self.pb_multi_cam_list.setVisible(False)
        
        parent_layout.addWidget(playblast_group)
        
        parent_layout.addStretch()

    # --- SU KIEN & LOGIC ---
    
    def is_character_reference(self, ref_path):
        """Kiem tra xem file reference co phai la nhan vat/rig hoac camera dua tren duong dan hoac ten file hay khong"""
        if not ref_path:
            return False
            
        # Neu ref_path la list/tuple do Maya query tra ve
        if isinstance(ref_path, (list, tuple)):
            if not ref_path:
                return False
            ref_path = ref_path[0]
            
        path_lower = ref_path.replace("\\", "/").lower()
        filename = os.path.basename(path_lower)
        
        # 0. Nhan dien Camera truoc tien (Uu tien nap kem voi nhan vat)
        camera_keywords = ["cam_rig", "camera_rig", "camera", "shot_cam"]
        if "camera" in filename or filename.startswith("cam_") or any(ck in filename for ck in camera_keywords):
            return True
        
        # 1. BO LOC LOAI TRU (EXCLUDE): Loai bo cac thu muc va file thuoc ve boi canh (BG), dao cu (Props), map...
        exclude_path_keywords = [
            "/asset rig/", "/asset_rig/", "/bg_rig/", "/bg_rigs/", 
            "/bg/", "/set/", "/prop/", "/props/", "/environment/", 
            "/background/", "/stage/", "/map/", "/scene/"
        ]
        for kw in exclude_path_keywords:
            if kw in path_lower:
                return False
                
        exclude_file_keywords = [
            "bg_", "set_", "prop_", "scene_", "background", "map_", 
            "stage_", "prop", "bg", "set", "trung_tam_thuong_mai",
            "bien_bao", "canh_bao", "thang", "hanh_lang", "bang_nut_bam", "qua_bong"
        ]
        for kw in exclude_file_keywords:
            if kw in filename:
                return False

        # 2. BO LOC CHAP NHAN (INCLUDE): Nhan dien thu muc hoac tu khoa nhan vat
        # 2.1 Kiem tra duong dan thu muc chua nhan vat
        include_path_keywords = [
            "/character rig/", "/character_rig/", "/character model/", 
            "/character/", "/animal_rig/", "/animal/"
        ]
        for kw in include_path_keywords:
            if kw in path_lower:
                return True
                
        # 2.2 Kiem tra ten file khop tu khoa nhan vat
        char_keywords = [
            "baby", "mom", "sister", "brother", "dad", 
            "mac_donald", "tourist", "guide",
            "gau", "tho", "chicken", "clowfish", "cow", "dog", "duck", 
            "horse", "mouse", "pig", "spider", "star_fish", "turtle",
            "animal"
        ]
        for kw in char_keywords:
            if kw in filename:
                return True
                
        return False

    def save_ref_load_setting(self, index):
        """Luu chi so che do tai Reference duoc chon vao cau hinh Maya"""
        cmds.optionVar(iv=(self.OPTION_VAR_REF_MODE, index))

    def load_settings(self):
        """Tai cau hinh du an mac dinh va tu dong dong bo file dang mo"""
        if cmds.optionVar(exists=self.OPTION_VAR_PROJ):
            saved_root = cmds.optionVar(q=self.OPTION_VAR_PROJ)
            if os.path.exists(saved_root):
                self.project_root = saved_root
                
        self.file_manager.project_root = self.project_root
        
        # Nap cau hinh che do tai Reference
        if cmds.optionVar(exists=self.OPTION_VAR_REF_MODE):
            saved_mode = cmds.optionVar(q=self.OPTION_VAR_REF_MODE)
            self.ref_load_combo.setCurrentIndex(saved_mode)
        else:
            self.ref_load_combo.setCurrentIndex(0) # Mac dinh mo nhanh

        self.populate_projects()
        
        # Tu dong nhan dien va dong bo file dang mo trong scene khi khoi dong UI
        current_filepath = cmds.file(q=True, sceneName=True)
        if current_filepath:
            self.refresh_dropdowns_to_match_current(current_filepath)

    def populate_projects(self):
        self.proj_combo.blockSignals(True)
        self.proj_combo.clear()
        
        projects = self.file_manager.get_projects()
        self.proj_combo.addItems(projects)
        
        for default_proj in ["KidSong", "Lolo", "Elementies"]:
            idx = self.proj_combo.findText(default_proj)
            if idx != -1:
                self.proj_combo.setCurrentIndex(idx)
                break
                
        self.proj_combo.blockSignals(False)
        self.on_proj_changed()

    def on_proj_changed(self):
        self.ep_combo.blockSignals(True)
        self.ep_combo.clear()
        
        current_proj = self.proj_combo.currentText()
        if current_proj:
            episodes = self.file_manager.get_episodes(current_proj)
            self.ep_combo.addItems(episodes)
            
        self.ep_combo.blockSignals(False)
        self.on_ep_changed()

    def on_ep_changed(self):
        self.validate_episode_naming()
        self.refresh_files_list()

    def validate_episode_naming(self):
        """Kiem tra xem ten thu muc tap phim hien tai co dung quy chuan hay khong va hien thi canh bao"""
        current_ep = self.ep_combo.currentText()
        if not current_ep:
            self.ep_warning_label.setVisible(False)
            return
            
        current_proj = self.proj_combo.currentText()
        standard_ep = self.file_manager.get_episode_folder_name(current_proj, current_ep)
        if current_ep != standard_ep:
            self.ep_warning_label.setText(u"⚠️ Thu muc khong chuan! Khuyen dung: %s" % standard_ep)
            self.ep_warning_label.setVisible(True)
        else:
            self.ep_warning_label.setVisible(False)

    def on_task_changed(self):
        self.refresh_files_list()

    def refresh_files_list(self):
        self.shot_list.clear()
        self.files_list.clear()
        self.current_work_files = []
        self.shot_map = {}
        
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (self.project_root and current_proj and current_ep and current_task):
            return
            
        files_info = self.file_manager.get_work_files(current_proj, current_ep, current_task)
        self.current_work_files = files_info
        
        # Nho shot dang chon truoc do de khoi phuc
        previous_selected_shot = ""
        selected_items = self.shot_list.selectedItems()
        if selected_items:
            previous_selected_shot = selected_items[0].text()
            
        # Gom nhom file theo ten shot
        for info in files_info:
            filename = info["filename"]
            parsed = self.file_manager.parse_scene_name(filename)
            if parsed:
                prefix = parsed[0]
            else:
                parts = filename.split("_v")
                if len(parts) > 1:
                    prefix = parts[0]
                else:
                    prefix = os.path.splitext(filename)[0]
                    
            if prefix not in self.shot_map:
                self.shot_map[prefix] = []
            self.shot_map[prefix].append(info)
            
        # Nap ten shot len bang ben trai
        sorted_shots = sorted(self.shot_map.keys())
        for shot in sorted_shots:
            item = QtWidgets.QListWidgetItem(shot)
            self.shot_list.addItem(item)
            
        # Khoi phuc lua chon
        if previous_selected_shot:
            items = self.shot_list.findItems(previous_selected_shot, QtCore.Qt.MatchExactly)
            if items:
                self.shot_list.blockSignals(True)
                self.shot_list.setCurrentItem(items[0])
                self.shot_list.blockSignals(False)
                self.on_shot_selection_changed()
        elif sorted_shots:
            self.shot_list.setCurrentRow(0)
            
        self.update_playblast_count()

    def on_shot_selection_changed(self):
        self.files_list.clear()
        selected_items = self.shot_list.selectedItems()
        if not selected_items:
            return
            
        selected_shot = selected_items[0].text()
        shot_files = self.shot_map.get(selected_shot, [])
        
        # Sap xep version tu cao xuong thap (moi nhat len tren)
        sorted_files = sorted(shot_files, key=lambda x: x["version"], reverse=True)
        
        # Dem so lan xuat hien cua moi filename
        filename_counts = {}
        for info in sorted_files:
            fn = info["filename"]
            filename_counts[fn] = filename_counts.get(fn, 0) + 1
            
        for info in sorted_files:
            fn = info["filename"]
            location_tag = ""
            if filename_counts[fn] > 1:
                parent_dir = os.path.basename(os.path.dirname(info["filepath"]))
                location_tag = " [%s]" % parent_dir
                
            item_text = "[v%02d] %s%s  (%s | %s)" % (
                info["version"], 
                info["filename"], 
                location_tag,
                info["time"], 
                info["size"]
            )
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, info["filepath"])
            item.setToolTip(os.path.normpath(info["filepath"]))
            self.files_list.addItem(item)
            
        self.update_playblast_count()

    def on_open_file(self, item):
        """Mo file duoc chon sau khi xac nhan canh bao an toan"""
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        if cmds.file(query=True, modified=True):
            res = QtWidgets.QMessageBox.question(
                self, u"Xac nhan mo file",
                u"Canh hien tai co thay doi chua luu. Ban co chac muon mo file moi?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
        try:
            kwargs = {"open": True, "force": True}
            mode = self.ref_load_combo.currentIndex()
            
            if mode == 0:  # Mo nhanh (Khong load Ref)
                kwargs["loadReferenceDepth"] = "none"
            elif mode in [1, 2]:  # Chon nap nhan vat hoac Tu chon deu dung tri hoan nap settings
                kwargs["buildLoadSettings"] = True
            elif mode == 3:  # Chi nap Ref cap 1
                kwargs["loadReferenceDepth"] = "topOnly"
            # mode == 4 la Mo binh thuong (nap tat ca)
            
            # Gan optionVar cua Maya de Preload Reference Editor mo dung file hien tai
            normalized_path = os.path.normpath(filepath).replace("\\", "/")
            cmds.optionVar(stringValue=("preloadRefEdTopLevelFile", normalized_path))
                
            cmds.file(to_sys_path(filepath), **kwargs)
            
            if mode == 1:
                # Quet va tich chon san cac Rig nhan vat & camera trong cau hinh tai
                print(u"Dang quet cac Reference de tich chon san nhan vat & camera...")
                num_settings = cmds.selLoadSettings(q=True, numSettings=True) or 0
                char_count = 0
                
                for i in range(1, num_settings):
                    ref_path_raw = cmds.selLoadSettings(str(i), q=True, fileName=True)
                    ref_path = ref_path_raw[0] if isinstance(ref_path_raw, (list, tuple)) and ref_path_raw else ref_path_raw
                    
                    if self.is_character_reference(ref_path):
                        cmds.selLoadSettings(str(i), edit=True, deferReference=0)  # Tich chon (Load)
                        char_count += 1
                        print(u"-> Da tich chon Rig/Camera: %s" % os.path.basename(ref_path))
                    else:
                        cmds.selLoadSettings(str(i), edit=True, deferReference=1)  # Bo chon (Defer)
                        
                print(u"Da chuan bi xong cau hinh nap. Tu dong tich chon %d nhan vat & camera." % char_count)
                
                # Hien thi bang Preload Reference Editor cua Maya de user xem va nhan nap
                import maya.mel as mel
                mel.eval("PreloadReferenceEditor;")
                
            elif mode == 2:
                # Hien thi cua so Preload Reference Editor goc cua Maya de nguoi dung chon
                import maya.mel as mel
                mel.eval("PreloadReferenceEditor;")
                
            cmds.workspace(to_sys_path(self.project_root), openWorkspace=True)
            print(u"Da mo file thanh cong: %s" % filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the mo file: %s" % exception_to_unicode(e))

    def on_create_episode(self):
        """Tao tap phim moi (Danh cho Leader)"""
        current_proj = self.proj_combo.currentText()
        if not current_proj:
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon Du an truoc.")
            return
            
        dialog = CreateEpisodeDialog(current_proj, self.file_manager, parent=self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            ep_folder_name, custom_abbrev = dialog.get_data()
            if not ep_folder_name:
                return
                
            ep_dir = self.file_manager.create_new_episode(current_proj, ep_folder_name, custom_abbrev)
            if ep_dir:
                self.proj_combo.blockSignals(True)
                self.ep_combo.blockSignals(True)
                
                episodes = self.file_manager.get_episodes(current_proj)
                self.ep_combo.clear()
                self.ep_combo.addItems(episodes)
                
                idx = self.ep_combo.findText(ep_folder_name)
                if idx != -1:
                    self.ep_combo.setCurrentIndex(idx)
                    
                self.proj_combo.blockSignals(False)
                self.ep_combo.blockSignals(False)
                
                self.on_ep_changed()
                QtWidgets.QMessageBox.information(
                    self, u"Thanh cong", 
                    u"Da tao cau truc tap phim moi thanh cong tren Server:\n%s" % ep_folder_name
                )

    def on_create_file(self):
        """Tao file nhap moi truc tiep trong WorkingFile/[Task]/"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not current_proj or not current_ep or not current_task:
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du Du an va Tap phim.")
            return
            
        if current_task == "Layout":
            # Goi y nhap so shot hoac dai shot
            text, ok = QtWidgets.QInputDialog.getText(
                self, u"Tao File Layout moi", 
                u"Nhap so Shot hoac dai Shot cho Layout (vi du: 03 hoac 01-30):"
            )
        else:
            # Nhap so shot don hoac dai shot
            text, ok = QtWidgets.QInputDialog.getText(
                self, u"Tao File Animation moi", 
                u"Nhap so Shot hoac dai Shot cho Animation (vi du: 03 hoac 03-10):"
            )
            
        if not (ok and text.strip()):
            return
            
        shot_range_or_num = text.strip()
        filepath = self.file_manager.create_new_work_file(current_proj, current_ep, current_task, shot_range_or_num)
        if filepath:
            self.refresh_files_list()
            QtWidgets.QMessageBox.information(
                self, u"Thanh cong", 
                u"Da khoi tao file nhap moi thanh cong tren Server:\n%s" % os.path.basename(filepath)
            )

    def on_increment_save(self):
        """Luu phien ban moi (+1)"""
        current_task = self.task_combo.currentText()
        new_filepath = self.file_manager.increment_save(current_task)
        if new_filepath:
            self.refresh_files_list()
            self.refresh_dropdowns_to_match_current(new_filepath)

    def show_shot_list_context_menu(self, pos):
        """Menu ngu canh khi nhap chuot phai vao danh sach Shot"""
        item = self.shot_list.itemAt(pos)
        shot_name = item.text() if item else ""
        
        menu = QtWidgets.QMenu(self)
        
        if shot_name:
            action_save_layout = menu.addAction(u"💾 Luu canh hien tai vao Layout (Shot %s)" % shot_name)
            action_save_anim = menu.addAction(u"💾 Luu canh hien tai vao Animation (Shot %s)" % shot_name)
            menu.addSeparator()
            action_convert_anim = menu.addAction(u"🔄 Chuyen file hien tai sang khau Animation (Shot %s)" % shot_name)
            menu.addSeparator()
            action_delete_shot = menu.addAction(u"🗑️ Xoa toan bo Shot %s va cac file Maya" % shot_name)
        else:
            action_save_layout = menu.addAction(u"💾 Luu canh hien tai vao Layout...")
            action_save_anim = menu.addAction(u"💾 Luu canh hien tai vao Animation...")
            action_convert_anim = None
            action_delete_shot = None
            
        action = menu.exec_(self.shot_list.mapToGlobal(pos))
        if not action:
            return
            
        if action == action_save_layout:
            self.save_current_to_shot_with_task(shot_name=shot_name, target_task="Layout")
        elif action == action_save_anim:
            self.save_current_to_shot_with_task(shot_name=shot_name, target_task="Animation")
        elif action_convert_anim and action == action_convert_anim:
            self.save_current_to_shot_with_task(shot_name=shot_name, target_task="Animation")
        elif action_delete_shot and action == action_delete_shot:
            self.on_delete_shot(shot_name)

    def on_delete_shot(self, shot_name):
        """Xoa toan bo Shot va tat ca cac phien ban file Maya tuong ung tren disk"""
        if not shot_name:
            return
            
        shot_files = self.shot_map.get(shot_name, [])
        current_task = self.task_combo.currentText()
        
        msg = u"Ban co chac chan muon XOA TOAN BO Shot '%s' khong?\n\n" % shot_name
        msg += u"Hanh dong nay se xoa vinh vien %d file Maya trong khau %s:" % (len(shot_files), current_task)
        
        for info in shot_files[:5]:
            msg += u"\n  - %s" % info["filename"]
        if len(shot_files) > 5:
            msg += u"\n  - va %d file khac..." % (len(shot_files) - 5)
            
        msg += u"\n\nLuu y: Hanh dong nay KHONG THE HOAN TAC!"
        
        res = QtWidgets.QMessageBox.question(
            self, u"Xac nhan XOA SHOT", msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res != QtWidgets.QMessageBox.Yes:
            return
            
        deleted_count = 0
        error_count = 0
        current_scene = cmds.file(q=True, sceneName=True)
        if current_scene:
            current_scene = os.path.normpath(current_scene).lower()
            
        subfolders_to_clean = set()
        
        for info in shot_files:
            fp = os.path.normpath(info["filepath"])
            if current_scene and current_scene == fp.lower():
                QtWidgets.QMessageBox.warning(
                    self, u"Canh bao",
                    u"File %s dang mo trong Maya. Vui long tao/mo file khac truoc khi xoa!" % info["filename"]
                )
                continue
                
            try:
                if os.path.exists(fp):
                    os.remove(fp)
                    deleted_count += 1
                    
                parent_d = os.path.dirname(fp)
                subfolders_to_clean.add(parent_d)
                grandparent_d = os.path.dirname(parent_d)
                subfolders_to_clean.add(grandparent_d)
            except Exception as e:
                print(u"Loi khi xoa file %s: %s" % (fp, str(e)))
                error_count += 1
                
        # Don dep thu muc rong neu thuoc WorkingFile
        for d in sorted(subfolders_to_clean, key=lambda x: len(x), reverse=True):
            if os.path.exists(d) and os.path.isdir(d):
                try:
                    if not os.listdir(d):
                        os.rmdir(d)
                except Exception:
                    pass
                    
        self.refresh_files_list()
        QtWidgets.QMessageBox.information(
            self, u"Hoan tat",
            u"Da xoa thanh cong %d file cua Shot '%s'." % (deleted_count, shot_name)
        )

    def on_save_current_scene_to_pipeline(self):
        """Luu file Maya hien tai vao Pipeline theo thong tin dang chon tren UI"""
        selected_items = self.shot_list.selectedItems()
        shot_name = selected_items[0].text() if selected_items else ""
        self.save_current_to_shot_with_task(shot_name=shot_name, target_task=None)

    def save_current_to_shot_with_task(self, shot_name="", target_task=None):
        """Xu ly luu file hien tai vao Pipeline cho Shot va Task chi dinh"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = target_task if target_task else self.task_combo.currentText()
        
        if not current_proj or not current_ep or not current_task:
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du Du an va Tap phim.")
            return
            
        if not shot_name:
            prompt_msg = u"Nhap so Shot hoac dai Shot (vi du: 03 hoac 03-10):"
            text, ok = QtWidgets.QInputDialog.getText(
                self, u"Luu Canh Vao Pipeline (%s)" % current_task, 
                prompt_msg
            )
            if not (ok and text.strip()):
                return
            shot_name = text.strip()
            
        # Rut gon va lam sach prefix Shot (vi du LL_BGOTL_V01_Shot_01_Anim -> 01)
        ep_abbrev = self.file_manager.get_episode_abbreviation(current_proj, current_ep)
        shot_code = self.file_manager.clean_shot_code(ep_abbrev, shot_name)
            
        new_filepath = self.file_manager.save_current_scene_to_pipeline(
            current_proj, current_ep, current_task, shot_code
        )
        
        if new_filepath:
            if target_task and target_task != self.task_combo.currentText():
                idx = self.task_combo.findText(target_task)
                if idx != -1:
                    self.task_combo.blockSignals(True)
                    self.task_combo.setCurrentIndex(idx)
                    self.task_combo.blockSignals(False)
                    
            self.refresh_files_list()
            self.refresh_dropdowns_to_match_current(new_filepath)
            QtWidgets.QMessageBox.information(
                self, u"Thanh cong", 
                u"Da luu canh hien tai vao Pipeline thanh cong:\n%s" % os.path.basename(new_filepath)
            )

    def refresh_dropdowns_to_match_current(self, filepath):
        """Tu dong dong bo dropdown UI khop voi file dang mo"""
        if not filepath or not self.project_root:
            return
            
        # Chuan hoa duong dan dang Windows/Linux khong phan biet hoa thuong
        norm_filepath = os.path.normpath(filepath)
        norm_root = os.path.normpath(self.project_root)
        
        # So sanh khong phan biet hoa thuong (tranh loi viet hoa o dia tren Windows)
        if not norm_filepath.lower().startswith(norm_root.lower()):
            return
            
        # Tinh toan duong dan tuong doi tu project_root chuan hoa
        rel_path = norm_filepath[len(norm_root):].lstrip(os.sep)
        parts = rel_path.split(os.sep)
        
        # Cau truc phang: [Project]/[Episode]/WorkingFile/[Task]/File.ma
        if len(parts) >= 5 and parts[2] == "WorkingFile":
            proj = parts[0]
            ep = parts[1]
            task_dir = parts[3]
            
            self.proj_combo.blockSignals(True)
            self.ep_combo.blockSignals(True)
            self.task_combo.blockSignals(True)
            
            proj_idx = self.proj_combo.findText(proj)
            if proj_idx != -1:
                self.proj_combo.setCurrentIndex(proj_idx)
                
            self.ep_combo.clear()
            self.ep_combo.addItems(self.file_manager.get_episodes(proj))
            ep_idx = self.ep_combo.findText(ep)
            if ep_idx != -1:
                self.ep_combo.setCurrentIndex(ep_idx)
                
            task_name = "Layout" if task_dir.lower() == "layout" else "Animation"
            task_idx = self.task_combo.findText(task_name)
            if task_idx != -1:
                self.task_combo.setCurrentIndex(task_idx)
                
            self.proj_combo.blockSignals(False)
            self.ep_combo.blockSignals(False)
            self.task_combo.blockSignals(False)
            
            self.refresh_files_list()
            
            # Phan tich file hien tai thuoc Shot nao de tu dong select Shot do tren bang ben trai
            current_filename = os.path.basename(norm_filepath)
            current_parsed = self.file_manager.parse_scene_name(current_filename)
            if current_parsed:
                current_prefix = current_parsed[0]
            else:
                parts = current_filename.split("_v")
                current_prefix = parts[0] if len(parts) > 1 else os.path.splitext(current_filename)[0]
                
            # Chon shot tren shot_list
            shot_items = self.shot_list.findItems(current_prefix, QtCore.Qt.MatchExactly)
            if shot_items:
                self.shot_list.blockSignals(True)
                self.shot_list.setCurrentItem(shot_items[0])
                self.shot_list.blockSignals(False)
                self.on_shot_selection_changed()
                
            # Tu dong chon (highlight) file hien tai trong QListWidget ben phai
            for i in range(self.files_list.count()):
                item = self.files_list.item(i)
                item_path = item.data(QtCore.Qt.UserRole)
                if item_path and os.path.normpath(item_path).lower() == norm_filepath.lower():
                    self.files_list.setCurrentItem(item)
                    break

    def update_playblast_count(self):
        """Kiem tra va hien thi danh sach video Playblast nhap hien co cho file Maya dang chon"""
        self.pb_list.clear()
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            current_filepath = cmds.file(q=True, sceneName=True)
            if current_filepath:
                filepath = current_filepath
                filename = os.path.basename(current_filepath)
            else:
                self.pb_count_label.setText(u"Trang thai Playblast: Khong co file hoat dong")
                self.pb_count_label.setStyleSheet("color: gray; font-weight: bold; margin-left: 2px;")
                self.pb_count_label.setToolTip("")
                return
        else:
            filepath = selected_items[0].data(QtCore.Qt.UserRole)
            filename = os.path.basename(filepath)
            
        filename_no_ext, _ = os.path.splitext(filename)
        
        # Goi playblast_manager de lay dung thu muc playblast nhap cua file nay
        playblast_dir, _ = self.playblast_manager.get_playblast_path(scene_filepath=filepath)
        if not playblast_dir:
            self.pb_count_label.setText(u"Trang thai Playblast: Chua kiem tra")
            self.pb_count_label.setStyleSheet("color: gray; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip("")
            return
            
        # 1. Tim toan bo video trong thu muc chinh bat dau bang filename_no_ext
        found_active_videos = []
        try:
            if os.path.exists(playblast_dir):
                for f in os.listdir(playblast_dir):
                    if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                        found_active_videos.append((f, os.path.join(playblast_dir, f)))
        except Exception:
            pass
            
        # Sap xep cac video active theo bang chu cai
        found_active_videos = sorted(found_active_videos, key=lambda x: x[0])
                
        # 2. Tim cac video phien ban cu trong thu muc Old
        found_old_videos = []
        old_dir = os.path.join(playblast_dir, "Old")
        if os.path.exists(old_dir) and os.path.isdir(old_dir):
            try:
                for f in os.listdir(old_dir):
                    if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                        found_old_videos.append((f, os.path.join(old_dir, f)))
            except Exception:
                pass
                
        # Sap xep cac video cu theo bang chu cai/so version tang dan
        found_old_videos = sorted(found_old_videos, key=lambda x: x[0])
        
        # 3. Nap du lieu len self.pb_list
        if found_active_videos:
            for name, path in found_active_videos:
                item = QtWidgets.QListWidgetItem(u"🟢 [Active] " + name)
                item.setData(QtCore.Qt.UserRole, path)
                item.setForeground(QtGui.QColor("#4CAF50")) # Chu xanh la
                self.pb_list.addItem(item)
            
            # Cap nhat nhan trang thai lay file video dau tien tim duoc
            first_name = found_active_videos[0][0]
            self.pb_count_label.setText(u"🎬 Da co Playblast (%s)" % first_name)
            self.pb_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip(os.path.normpath(found_active_videos[0][1]))
        else:
            self.pb_count_label.setText(u"❌ Chua co Playblast")
            self.pb_count_label.setStyleSheet("color: #F44336; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip("")
            
        for name, path in found_old_videos:
            item = QtWidgets.QListWidgetItem(u"⚪ [Old] " + name)
            item.setData(QtCore.Qt.UserRole, path)
            item.setForeground(QtGui.QColor("#9E9E9E")) # Chu xam nhat
            self.pb_list.addItem(item)

    def on_open_playblast_file(self, item):
        """Mo file video playblast bang trinh phat mac dinh cua he thong"""
        import os
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        try:
            os.startfile(os.path.normpath(filepath))
            print(u"Da mo video playblast bang trinh phat mac dinh: %s" % filepath)
        except Exception as e:
            cmds.warning(u"Khong the mo video playblast: %s" % str(e))

    def get_scene_cameras(self):
        """Lay danh sach cac camera transform trong scene, loc camera mac dinh va xep camera custom len truoc"""
        cam_shapes = cmds.ls(cameras=True) or []
        cams = []
        for shape in cam_shapes:
            parents = cmds.listRelatives(shape, parent=True)
            if parents:
                cams.append(parents[0])
                
        startup_cams = ["persp", "top", "front", "side"]
        custom_cams = [c for c in cams if c not in startup_cams]
        default_cams = [c for c in cams if c in startup_cams]
        
        return sorted(custom_cams) + sorted(default_cams)

    def refresh_camera_list(self):
        """Lam moi danh sach camera tren giao dien"""
        cams = self.get_scene_cameras()
        
        # Cap nhat single combo
        self.pb_single_cam_combo.blockSignals(True)
        self.pb_single_cam_combo.clear()
        self.pb_single_cam_combo.addItems(cams)
        self.pb_single_cam_combo.blockSignals(False)
        
        # Cap nhat multi check list
        self.pb_multi_cam_list.clear()
        for cam in cams:
            item = QtWidgets.QListWidgetItem(cam)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.pb_multi_cam_list.addItem(item)

    def on_pb_cam_mode_changed(self, index):
        """Thay doi che do camera hien thi tren giao dien"""
        mode = self.pb_cam_mode_combo.currentText()
        if mode == u"Tuy chon 1 Camera":
            self.pb_single_cam_widget.setVisible(True)
            self.pb_multi_cam_list.setVisible(False)
            self.refresh_camera_list()
        elif mode == u"Xuat nhieu Camera (Batch)":
            self.pb_single_cam_widget.setVisible(False)
            self.pb_multi_cam_list.setVisible(True)
            self.refresh_camera_list()
        else: # Camera hien hanh (Active)
            self.pb_single_cam_widget.setVisible(False)
            self.pb_multi_cam_list.setVisible(False)

    def on_run_playblast(self):
        """Chay playblast nhap hang ngay"""
        format_text = self.pb_format_combo.currentText()
        format_ext = "qt" if "QuickTime" in format_text else "avi"
        
        res_text = self.pb_res_combo.currentText()
        if "1920x1080" in res_text:
            width, height = 1920, 1080
        elif "1280x720" in res_text:
            width, height = 1280, 720
        else:
            width, height = 640, 360
            
        cam_mode = self.pb_cam_mode_combo.currentText()
        overwrite = self.pb_overwrite_checkbox.isChecked()
        
        try:
            if cam_mode == u"Camera hien hanh (Active)":
                output_path = self.playblast_manager.run_playblast(
                    format_ext=format_ext,
                    percent=100,
                    width=width,
                    height=height,
                    viewer=True,
                    overwrite=overwrite
                )
                if output_path:
                    res = cmds.confirmDialog(
                        title="Playblast completed",
                        message="Playblast video exported successfully at:\n%s" % output_path,
                        button=["OK", "Open Folder"],
                        defaultButton="OK",
                        cancelButton="OK"
                    )
                    if res == "Open Folder":
                        self.open_folder_explorer(os.path.dirname(output_path))
                    
            elif cam_mode == u"Tuy chon 1 Camera":
                camera = self.pb_single_cam_combo.currentText()
                if not camera:
                    QtWidgets.QMessageBox.warning(self, "Missing Info", "Please select a camera to export.")
                    return
                    
                output_path = self.playblast_manager.run_playblast(
                    format_ext=format_ext,
                    percent=100,
                    width=width,
                    height=height,
                    camera=camera,
                    viewer=True,
                    overwrite=overwrite
                )
                if output_path:
                    res = cmds.confirmDialog(
                        title="Playblast completed",
                        message="Playblast video for camera [%s] exported successfully at:\n%s" % (camera, output_path),
                        button=["OK", "Open Folder"],
                        defaultButton="OK",
                        cancelButton="OK"
                    )
                    if res == "Open Folder":
                        self.open_folder_explorer(os.path.dirname(output_path))
                    
            elif cam_mode == u"Xuat nhieu Camera (Batch)":
                selected_cams = []
                for i in range(self.pb_multi_cam_list.count()):
                    item = self.pb_multi_cam_list.item(i)
                    if item.checkState() == QtCore.Qt.Checked:
                        selected_cams.append(item.text())
                        
                if not selected_cams:
                    QtWidgets.QMessageBox.warning(self, "Missing Info", "Please check at least one camera in the list to batch export.")
                    return
                    
                success_paths = []
                failed_cams = []
                
                progress = QtWidgets.QProgressDialog("Batch exporting Playblasts...", "Cancel", 0, len(selected_cams), self)
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.setAutoClose(True)
                progress.setValue(0)
                QtCore.QCoreApplication.processEvents()
                
                for idx, cam in enumerate(selected_cams):
                    if progress.wasCanceled():
                        break
                        
                    progress.setLabelText("Exporting Playblast for camera: %s..." % cam)
                    progress.setValue(idx)
                    QtCore.QCoreApplication.processEvents()
                    
                    try:
                        out_path = self.playblast_manager.run_playblast(
                            format_ext=format_ext,
                            percent=100,
                            width=width,
                            height=height,
                            camera=cam,
                            viewer=False,  # Disable viewer in batch to avoid collision
                            overwrite=overwrite
                        )
                        if out_path:
                            success_paths.append(out_path)
                    except Exception as err:
                        failed_cams.append((cam, exception_to_unicode(err)))
                        
                progress.setValue(len(selected_cams))
                
                # Hien thi bao cao ket qua
                msg = "Batch Playblast process finished!\n\n"
                if success_paths:
                    msg += "Success (%d videos):\n" % len(success_paths)
                    for p in success_paths[:5]:
                        msg += "  - %s\n" % os.path.basename(p)
                    if len(success_paths) > 5:
                        msg += "  - and %d more...\n" % (len(success_paths) - 5)
                        
                if failed_cams:
                    msg += "\nFailed (%d cameras):\n" % len(failed_cams)
                    for cam, err in failed_cams[:5]:
                        msg += "  - %s: %s\n" % (cam, err)
                        
                if success_paths:
                    msg += "\nDo you want to open the folder containing the exported videos?"
                    res = QtWidgets.QMessageBox.question(
                        self, "Batch Export Results", msg,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    if res == QtWidgets.QMessageBox.Yes:
                        self.open_folder_explorer(os.path.dirname(success_paths[0]))
                else:
                    QtWidgets.QMessageBox.warning(self, "Batch Export Results", msg)
            
            self.update_playblast_count()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Playblast Error",
                "An error occurred during Playblast process:\n\n%s" % exception_to_unicode(e)
            )

    def on_publish_file(self):
        """Xuat ban file sach va tu dong chay playblast chinh thuc kem theo"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du thong tin de Publish.")
            return
            
        res = QtWidgets.QMessageBox.question(
            self, u"Xac nhan Publish",
            u"Ban co chac chan muon Publish file hien tai cho khau %s khong?\nHanh dong nay se don dep file va xuat playblast chinh thuc." % current_task,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        pub_filepath = self.file_manager.publish_file(current_proj, current_ep, current_task)
        if not pub_filepath:
            QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the Publish file Maya. Vui long kiem tra log.")
            return
            
        pub_video_path = os.path.splitext(pub_filepath)[0] + ".mov"
        current_filepath = cmds.file(q=True, sceneName=True)
        
        try:
            cmds.file(to_sys_path(pub_filepath), open=True, force=True)
            print(u"Dang chay Playblast chinh thuc cho file Publish...")
            self.playblast_manager.run_playblast(
                format_ext="qt",
                percent=100,
                width=1920,
                height=1080,
                custom_path=pub_video_path
            )
        except Exception as e:
            print(u"Loi khi chay Playblast Publish: %s" % exception_to_unicode(e))
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(to_sys_path(current_filepath), open=True, force=True)
                
        QtWidgets.QMessageBox.information(
            self, u"Publish Thanh Cong",
            u"Da xuat ban sach se file Maya va video Playblast len Server:\n\nFile: %s\nVideo: %s" % (
                os.path.basename(pub_filepath), 
                os.path.basename(pub_video_path)
            )
        )
        self.refresh_files_list()

    def on_check_filenames(self):
        """Quet tim file sai quy chuan thuc te trong tap phim, hoi y kien user de tu dong sua toan bo"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        
        if not (current_proj and current_ep):
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du Du an va Tap phim truoc.")
            return

        # 1. Kiem tra quy chuan cua thu muc Episode truoc
        standard_ep = self.file_manager.get_episode_folder_name(current_proj, current_ep)
        if current_ep != standard_ep:
            msg = (
                u"Thu muc tap phim hien tai chua dung quy chuan:\n"
                u"  - Hien tai: %s\n"
                u"  - Dung chuan: %s\n\n"
                u"Ban co muon doi ten thu muc nay tren Server ve dung quy chuan khong?\n"
                u"(Luu y: Chi thuc hien khi khong co ai dang mo hoac khoa file trong thu muc nay)."
            ) % (current_ep, standard_ep)
            
            res = QtWidgets.QMessageBox.question(
                self, u"Chuan hoa ten thu muc Tap phim",
                msg,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
            )
            
            if res == QtWidgets.QMessageBox.Cancel:
                return
            elif res == QtWidgets.QMessageBox.Yes:
                success = self.file_manager.rename_episode_folder(current_proj, current_ep, standard_ep)
                if success:
                    # Cap nhat lai dropdown Episode
                    self.ep_combo.blockSignals(True)
                    self.ep_combo.clear()
                    episodes = self.file_manager.get_episodes(current_proj)
                    self.ep_combo.addItems(episodes)
                    idx = self.ep_combo.findText(standard_ep)
                    if idx != -1:
                        self.ep_combo.setCurrentIndex(idx)
                    self.ep_combo.blockSignals(False)
                    
                    current_ep = standard_ep
                    self.validate_episode_naming()
                    QtWidgets.QMessageBox.information(
                        self, u"Thanh cong",
                        u"Da doi ten thu muc tap phim thanh: %s" % standard_ep
                    )
                else:
                    QtWidgets.QMessageBox.critical(
                        self, u"Loi",
                        u"Khong the doi ten thu muc tap phim. Thu muc hoac file ben trong co the dang bi khoa bai Windows Explorer hoac tien trinh khac."
                    )
                    # Hoi xem co tiep tuc kiem tra file ben trong thu muc cu khong
                    cont_res = QtWidgets.QMessageBox.question(
                        self, u"Tiep tuc kiem tra?",
                        u"Ban co muon tiep tuc quet va chuan hoa cac file ben trong thu muc hien tai (%s) khong?" % current_ep,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    if cont_res == QtWidgets.QMessageBox.No:
                        return

        # 2. Quet tim file sai quy chuan thuc te trong tap phim
        incorrect_files = self.file_manager.check_episode_filenames_naming(current_proj, current_ep)
        
        if not incorrect_files:
            QtWidgets.QMessageBox.information(
                self, u"Ket qua kiem tra", 
                u"Tuyet voi! Toan bo file lam viec trong tap phim deu dung quy chuan!"
            )
            return
            
        def to_unicode(s):
            if isinstance(s, str):
                try:
                    return s.decode("utf-8")
                except:
                    return unicode(s)
            return s
            
        msg = u"Phat hien %d file dat ten sai quy chuan. Vi du:\n\n" % len(incorrect_files)
        for i, f_info in enumerate(incorrect_files[:5]):
            old_f = to_unicode(f_info["old_filename"])
            new_f = to_unicode(f_info["new_filename"])
            task_d = to_unicode(f_info["task_dir"])
            msg += u"  - [%s] %s -> %s\n" % (task_d, old_f, new_f)
        if len(incorrect_files) > 5:
            msg += u"  - va %d file khac...\n" % (len(incorrect_files) - 5)
        msg += u"\nBan co muon doi ten toan bo cac file nay ve dung quy chuan khong?"
        
        res = QtWidgets.QMessageBox.question(
            self, u"Xac nhan chuan hoa ten file lam viec",
            msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if res == QtWidgets.QMessageBox.Yes:
            success = self.file_manager.rename_work_files(incorrect_files)
            if success:
                self.refresh_files_list()
                QtWidgets.QMessageBox.information(
                    self, u"Thanh cong", 
                    u"Da hoan thanh chuan hoa ten cac file lam viec!"
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self, u"Loi chuan hoa", 
                    u"Co loi xay ra trong qua trinh doi ten!\n\n"
                    u"Nguyen nhan pho bien: File can doi ten dang bi khoa (co the dang mo trong phan mem khac).\n\n"
                    u"Vui long dong cac file lien quan va thu lai!"
                )

    def on_refresh(self):
        """Lam moi toan bo danh sach du an, tap phim va file tu Server"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        self.proj_combo.blockSignals(True)
        self.proj_combo.clear()
        projects = self.file_manager.get_projects()
        self.proj_combo.addItems(projects)
        
        idx = self.proj_combo.findText(current_proj)
        if idx != -1:
            self.proj_combo.setCurrentIndex(idx)
        self.proj_combo.blockSignals(False)
        
        self.ep_combo.blockSignals(True)
        self.ep_combo.clear()
        if self.proj_combo.currentText():
            episodes = self.file_manager.get_episodes(self.proj_combo.currentText())
            self.ep_combo.addItems(episodes)
            
        idx = self.ep_combo.findText(current_ep)
        if idx != -1:
            self.ep_combo.setCurrentIndex(idx)
        self.ep_combo.blockSignals(False)
        
        self.task_combo.blockSignals(True)
        idx = self.task_combo.findText(current_task)
        if idx != -1:
            self.task_combo.setCurrentIndex(idx)
        self.task_combo.blockSignals(False)
        
        self.refresh_files_list()
        
        # Tu dong nhan dien va dong bo file dang mo sau khi lam moi
        current_filepath = cmds.file(q=True, sceneName=True)
        if current_filepath:
            self.refresh_dropdowns_to_match_current(current_filepath)
        print("Da lam moi danh sach tu Server.")

    def open_folder_explorer(self, folder_path):
        """Mo thu muc trong Windows Explorer"""
        if not folder_path or not os.path.exists(folder_path):
            cmds.warning(u"Thu muc khong ton tai: %s" % folder_path)
            return
        try:
            # Chuan hoa duong dan dang Windows
            folder_path = os.path.normpath(folder_path)
            os.startfile(to_sys_path(folder_path))
        except Exception as e:
            cmds.warning(u"Khong the mo thu muc: %s" % exception_to_unicode(e))

    def on_open_ep_dir(self):
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        if not (current_proj and current_ep):
            return
        ep_dir = os.path.join(self.project_root, current_proj, current_ep)
        self.open_folder_explorer(ep_dir)

    def on_open_work_dir(self):
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        if not (current_proj and current_ep and current_task):
            return
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        work_dir = os.path.join(self.project_root, current_proj, current_ep, "WorkingFile", task_dir_name)
        self.open_folder_explorer(work_dir)

    def on_open_mov_dir(self):
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            filepath = cmds.file(q=True, sceneName=True)
        else:
            filepath = selected_items[0].data(QtCore.Qt.UserRole)
            
        if filepath:
            mov_dir, _ = self.playblast_manager.get_playblast_path(scene_filepath=filepath)
        else:
            current_proj = self.proj_combo.currentText()
            current_ep = self.ep_combo.currentText()
            current_task = self.task_combo.currentText()
            if not (current_proj and current_ep and current_task):
                return
            task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
            mov_dir = os.path.join(self.project_root, current_proj, current_ep, "mov", task_dir_name)
            
        if mov_dir and not os.path.exists(mov_dir):
            try:
                os.makedirs(mov_dir)
            except Exception:
                pass
                
        self.open_folder_explorer(mov_dir)

    def on_open_pub_dir(self):
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        if not (current_proj and current_ep and current_task):
            return
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        
        # Published co thu muc con cua tung shot
        # Tim shot dang chon de mo dung thu muc published cua shot do
        selected_items = self.shot_list.selectedItems() if hasattr(self, 'shot_list') else []
        if selected_items:
            shot_name = selected_items[0].text()
            pub_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name, shot_name)
        else:
            pub_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name)
            
        if not os.path.exists(pub_dir):
            try:
                os.makedirs(pub_dir)
            except Exception:
                pass
                
        self.open_folder_explorer(pub_dir)

    def show_file_list_context_menu(self, pos):
        import os
        item = self.files_list.itemAt(pos)
        if not item:
            return
            
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath:
            return
            
        menu = QtWidgets.QMenu(self)
        
        action_open_folder = menu.addAction(u"Mo thu muc chua file")
        action_copy_path = menu.addAction(u"Sao chep duong dan file")
        action_debug_open = menu.addAction(u"Mo va Debug hieu nang (Do thoi gian tai)")
        menu.addSeparator()
        
        # Them action Publish file nay offline
        action_publish = menu.addAction(u"🚀 Publish File nay (Copy nhanh)")
        
        # Tim video playblast nhap tuong ung (quet dong theo shot cho ca Layout)
        filename = os.path.basename(filepath)
        filename_no_ext = os.path.splitext(filename)[0]
        
        # Goi playblast_manager de lay dung thu muc playblast nhap cua file nay
        playblast_dir, _ = self.playblast_manager.get_playblast_path(scene_filepath=filepath)
        
        active_video_path = None
        if playblast_dir and os.path.exists(playblast_dir):
            try:
                for f in os.listdir(playblast_dir):
                    if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                        active_video_path = os.path.join(playblast_dir, f)
                        break
            except Exception:
                pass
                
        action_open_video = None
        if active_video_path:
            action_open_video = menu.addAction(u"Xem video Playblast nhap")
            
        menu.addSeparator()
        action_delete_file = menu.addAction(u"🗑️ Xoa file Maya nay (Delete)")
            
        # Thuc thi menu
        action = menu.exec_(self.files_list.mapToGlobal(pos))
        
        if action == action_open_folder:
            self.open_folder_explorer(os.path.dirname(filepath))
        elif action == action_copy_path:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(os.path.normpath(filepath))
            print("Da sao chep duong dan file vao Clipboard: %s" % filepath)
        elif action == action_delete_file:
            res = QtWidgets.QMessageBox.question(
                self, u"Xac nhan xoa file",
                u"Ban co chac chan muon xoa vinh vien file Maya nay khong?\n\n%s" % os.path.normpath(filepath),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.Yes:
                try:
                    os.remove(filepath)
                    self.refresh_files_list()
                    print(u"Da xoa file: %s" % filepath)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the xoa file:\n%s" % str(e))
        elif action == action_publish:
            self.on_publish_file_offline(filepath)
        elif action == action_debug_open:
            res = QtWidgets.QMessageBox.question(
                self, u"Xac nhan Debug mo file",
                u"Hanh dong nay se mo file canh va tai tung Reference mot de do luong chi tiet.\n"
                u"Ban co chac muon tien hanh khong?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
            progress = QtWidgets.QProgressDialog(u"Dang do luong hieu nang mo file...", u"Huy", 0, 100, self)
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.setAutoClose(True)
            progress.setValue(10)
            QtCore.QCoreApplication.processEvents()
            
            try:
                report = self.file_manager.debug_open_file(filepath)
                progress.setValue(100)
                
                # Hien thi bao cao ket qua
                self.show_debug_report_dialog(filepath, report)
            except Exception as e:
                progress.close()
                QtWidgets.QMessageBox.critical(self, u"Loi", u"Loi khi debug mo file: %s" % exception_to_unicode(e))
        elif action_open_video and action == action_open_video:
            try:
                os.startfile(to_sys_path(os.path.normpath(active_video_path)))
            except Exception as e:
                cmds.warning(u"Khong the mo video Playblast: %s" % exception_to_unicode(e))

    def show_debug_report_dialog(self, filepath, report):
        dialog = DebugReportDialog(filepath, report, parent=self)
        dialog.exec_()

    def on_publish_file_offline(self, filepath):
        """Publish nhanh file Maya va video playblast nhap tuong ung bang cach copy offline (toc do duoi 1 giay)"""
        if not filepath or not os.path.exists(filepath):
            return
            
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du Du an va Tap phim.")
            return
            
        filename = os.path.basename(filepath)
        parsed = self.file_manager.parse_scene_name(filename)
        if not parsed:
            QtWidgets.QMessageBox.warning(self, u"Loi ten file", u"Ten file khong dung quy chuan, khong the Publish.")
            return
            
        prefix, file_task, ver, padding, ext = parsed
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        # Xac dinh thu muc published
        published_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name)
        if task_short == "Lay":
            published_dir = os.path.join(published_dir, prefix)
            
        if not os.path.exists(published_dir):
            try:
                os.makedirs(published_dir)
            except Exception:
                pass
                
        published_filename = "%s_%s_pub%s" % (prefix, task_short, ext)
        published_filepath = os.path.normpath(os.path.join(published_dir, published_filename))
        
        # Check if the published file is the currently open scene file
        current_scene = cmds.file(q=True, sceneName=True)
        is_current_scene = False
        if current_scene:
            is_current_scene = (os.path.normpath(current_scene).lower() == os.path.normpath(filepath).lower())
            
        # Tien hanh copy file Maya
        import shutil
        try:
            shutil.copy2(filepath, published_filepath)
            print(u"[PUBLISH OFFLINE] Da copy file Maya sang Published: %s" % published_filepath)
            
            # Tu dong xuat anim sang Studio Library neu la file dang mo
            anim_msg = ""
            if is_current_scene:
                try:
                    self.export_current_scene_anim(current_proj, current_ep, filename)
                    anim_msg = u"✅ Da tu dong xuat du lieu Anim sang thu vien Studio Library chuan bi cho khau Gop Canh.\n\n"
                except Exception as ex:
                    anim_msg = u"❌ Gap loi khi xuat du lieu Anim: %s\n\n" % exception_to_unicode(ex)
            else:
                anim_msg = u"⚠️ Chu y: Ban dang publish offline mot tep khong phai scene dang mo hien tai, vi vay he thong khong the xuat du lieu anim cho khau Gop Canh. Vui long mo file va publish de xuat anim.\n\n"

            # Thong bao thanh cong
            msg = u"Da xuat ban (Publish) thanh cong thanh file sach tren server!\n\n"
            msg += anim_msg
            msg += u"📁 File Maya: %s\n\n" % os.path.basename(published_filepath)
            msg += u"💡 Goi y: Nhap chuot phai vao video o cot thu 3 va chon 'Publish Video nay' neu ban muon day video playblast tuong ung len server.\n"
                
            res = cmds.confirmDialog(
                title="Publish Success",
                message=msg,
                button=["OK", "Open Published Folder"],
                defaultButton="OK",
                cancelButton="OK"
            )
            if res == "Open Published Folder":
                self.open_folder_explorer(published_dir)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Loi Publish", u"Khong the copy file len server:\n%s" % str(e))

    def show_pb_list_context_menu(self, pos):
        item = self.pb_list.itemAt(pos)
        if not item:
            return
            
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        menu = QtWidgets.QMenu(self)
        
        action_open_video = menu.addAction(u"Xem video Playblast")
        action_open_folder = menu.addAction(u"Mo thu muc chua video")
        menu.addSeparator()
        action_publish_video = menu.addAction(u"🚀 Publish Video nay")
        
        action = menu.exec_(self.pb_list.mapToGlobal(pos))
        if action == action_open_video:
            self.on_open_playblast_file(item)
        elif action == action_open_folder:
            self.open_folder_explorer(os.path.dirname(filepath))
        elif action == action_publish_video:
            self.on_publish_video_offline(filepath)

    def on_publish_video_offline(self, filepath):
        """Publish nhanh video playblast duoc chon len server Published (offline copy)"""
        if not filepath or not os.path.exists(filepath):
            return
            
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon day du Du an va Tap phim.")
            return
            
        # Lay dinh danh cua file Maya dang chon o cot 2
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            current_filepath = cmds.file(q=True, sceneName=True)
            if not current_filepath:
                QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Vui long chon file Maya tuong ung o cot 2 de xac dinh ten Publish.")
                return
            maya_filename = os.path.basename(current_filepath)
        else:
            maya_filename = os.path.basename(selected_items[0].data(QtCore.Qt.UserRole))
            
        parsed = self.file_manager.parse_scene_name(maya_filename)
        if not parsed:
            QtWidgets.QMessageBox.warning(self, u"Loi ten file", u"Ten file Maya khong hop le, khong the xac dinh ten Publish.")
            return
            
        prefix, file_task, ver, padding, ext = parsed
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        # Xac dinh thu muc published video
        published_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name)
        if task_short == "Lay":
            published_dir = os.path.join(published_dir, prefix)
            
        dest_mov_dir = os.path.join(published_dir, "mov")
        if not os.path.exists(dest_mov_dir):
            try:
                os.makedirs(dest_mov_dir)
            except Exception:
                pass
                
        # Lay duoi file video nguon (.mov hoac .avi)
        mov_ext = os.path.splitext(filepath)[1]
        dest_mov_filename = "%s_%s_pub%s" % (prefix, task_short, mov_ext)
        dest_mov_path = os.path.normpath(os.path.join(dest_mov_dir, dest_mov_filename))
        
        # Thuc hien copy offline
        import shutil
        try:
            shutil.copy2(filepath, dest_mov_path)
            print(u"[PUBLISH VIDEO] Da copy video playblast sang Published: %s" % dest_mov_path)
            
            res = cmds.confirmDialog(
                title="Publish Video Success",
                message=u"Da xuat ban (Publish) video playblast thanh cong len server!\n\n"
                        u"🎬 Video: %s" % os.path.basename(dest_mov_path),
                button=["OK", "Open Published Folder"],
                defaultButton="OK",
                cancelButton="OK"
            )
            if res == "Open Published Folder":
                self.open_folder_explorer(published_dir)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Loi Publish", u"Khong the copy video len server:\n%s" % str(e))

    def export_current_scene_anim(self, project, episode, filename):
        """Tu dong xuat anim cua scene hien tai thanh file Studio Library .anim cho quy trinh Gop Canh"""
        parsed = self.file_manager.parse_scene_name(filename)
        if not parsed:
            return
        prefix, file_task, ver, padding, ext = parsed
        if file_task.lower() != "anim":
            return
            
        import re
        shot_match = re.search(r'Shot_(\d+)', prefix, re.IGNORECASE)
        if not shot_match:
            print(u"[StudioLibrary] Khong tim thay so Shot hap le tu tien to: %s" % prefix)
            return
        shot_num = shot_match.group(1)
        
        # Xay duong dan thu muc Studio Library cho shot
        shot_stlib_dir = self.file_manager.build_studiolibrary_shot_dir(project, episode, shot_num)
        if not shot_stlib_dir:
            return
            
        if not os.path.exists(shot_stlib_dir):
            try:
                os.makedirs(shot_stlib_dir)
            except Exception as e:
                print(u"[StudioLibrary] Loi tao thu muc Studio Library: %s" % str(e))
                return
                
        # Lay danh sach cac node co keyframe
        saved_selection = self.get_smart_selection()
        if not saved_selection:
            print(u"[StudioLibrary] Khong tim thay control nao co keyframe de xuat anim.")
            return
            
        s_time = int(cmds.playbackOptions(q=True, minTime=True))
        e_time = int(cmds.playbackOptions(q=True, maxTime=True))
        
        import mutils
        import shutil
        
        # 1. Xuat file gop all_assets.anim
        all_assets_path = os.path.normpath(os.path.join(shot_stlib_dir, "all_assets.anim")).replace('\\', '/')
        if os.path.exists(all_assets_path):
            try:
                shutil.rmtree(all_assets_path)
            except Exception:
                pass
        try:
            mutils.saveAnim(
                objects=saved_selection,
                path=all_assets_path,
                time=(s_time, e_time),
                bakeConnected=True
            )
            print(u"[StudioLibrary] Da tu dong xuat anim gop thanh cong: %s" % all_assets_path)
        except Exception as e:
            print(u"[StudioLibrary] Loi khi tu dong xuat anim gop: %s" % exception_to_unicode(e))
            
        # 2. Phan nhom doi tuong theo namespace va xuat anim le cho tung Rig
        namespace_groups = {}
        for obj in saved_selection:
            if ":" in obj:
                parts = obj.split(":")
                ns = ":".join(parts[:-1])
            else:
                ns = "no_namespace"
            if ns not in namespace_groups:
                namespace_groups[ns] = []
            namespace_groups[ns].append(obj)
            
        for ns, objs in namespace_groups.items():
            ns_clean = ns.replace(":", "_")
            ns_anim_path = os.path.normpath(os.path.join(shot_stlib_dir, "%s.anim" % ns_clean)).replace('\\', '/')
            if os.path.exists(ns_anim_path):
                try:
                    shutil.rmtree(ns_anim_path)
                except Exception:
                    pass
            try:
                mutils.saveAnim(
                    objects=objs,
                    path=ns_anim_path,
                    time=(s_time, e_time),
                    bakeConnected=True
                )
                print(u"[StudioLibrary] Da xuat anim cho namespace %s: %s" % (ns, ns_anim_path))
            except Exception as e:
                print(u"[StudioLibrary] Loi khi xuat anim cho namespace %s: %s" % (ns, exception_to_unicode(e)))

    # ================================================================
    # TAB 2: Tach / Gop Canh (Split & Merge)
    # ================================================================

    def _build_tab2_split_merge(self, parent_layout):
        """Xay dung noi dung Tab 2 - Tach / Gop Canh"""
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(10)
        scroll.setWidget(scroll_widget)
        parent_layout.addWidget(scroll)

        LABEL_WIDTH = 160

        # ---- KHU VUC 1: Tach Shot Layout Tong ----
        split_group = QtWidgets.QGroupBox(u"Tach Shot Layout Tong (Split)")
        split_group_layout = QtWidgets.QVBoxLayout(split_group)
        split_group_layout.setContentsMargins(12, 16, 12, 12)
        split_group_layout.setSpacing(10)

        # Hang 1: Nut Quet Bookmarks tu Scene hien tai
        self.sm_scan_btn = QtWidgets.QPushButton(u"🔍 Quet Bookmarks tu Scene hien tai")
        self.sm_scan_btn.setToolTip(u"Quet toan bo cac timeSliderBookmark danh so tu scene Maya dang mo")
        self.sm_scan_btn.clicked.connect(self.on_scan_bookmarks)
        split_group_layout.addWidget(self.sm_scan_btn)

        # Hang 2: Danh sach bookmark
        list_label_row = QtWidgets.QHBoxLayout()
        lbl_list = QtWidgets.QLabel(u"Bookmarks tim thay:")
        lbl_list.setFixedWidth(LABEL_WIDTH)
        list_label_row.addWidget(lbl_list)
        
        self.sm_bookmark_count_lbl = QtWidgets.QLabel(u"")
        self.sm_bookmark_count_lbl.setStyleSheet("color: #FF9800; font-weight: bold;")
        list_label_row.addWidget(self.sm_bookmark_count_lbl)
        list_label_row.addStretch()
        split_group_layout.addLayout(list_label_row)

        list_row = QtWidgets.QHBoxLayout()
        lbl_list_spacer = QtWidgets.QWidget()
        lbl_list_spacer.setFixedWidth(LABEL_WIDTH)
        list_row.addWidget(lbl_list_spacer)
        
        self.sm_bookmark_list = QtWidgets.QListWidget()
        self.sm_bookmark_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.sm_bookmark_list.setFixedHeight(150)
        list_row.addWidget(self.sm_bookmark_list)
        split_group_layout.addLayout(list_row)

        # Hang 3: Loc khoang shot
        filter_row = QtWidgets.QHBoxLayout()
        lbl_filter = QtWidgets.QLabel(u"Loc khoang shot (tuy chon):")
        lbl_filter.setFixedWidth(LABEL_WIDTH)
        filter_row.addWidget(lbl_filter)

        self.sm_split_start = QtWidgets.QSpinBox()
        self.sm_split_start.setRange(0, 999)
        self.sm_split_start.setValue(0)
        self.sm_split_start.setToolTip(u"Bat dau tu shot so (0 = khong loc)")
        self.sm_split_start.setFixedWidth(80)

        self.sm_split_end = QtWidgets.QSpinBox()
        self.sm_split_end.setRange(0, 999)
        self.sm_split_end.setValue(0)
        self.sm_split_end.setToolTip(u"Den shot so (0 = khong loc)")
        self.sm_split_end.setFixedWidth(80)

        filter_row.addWidget(QtWidgets.QLabel(u"Tu:"))
        filter_row.addWidget(self.sm_split_start)
        filter_row.addWidget(QtWidgets.QLabel(u" Den:"))
        filter_row.addWidget(self.sm_split_end)
        filter_row.addStretch()
        split_group_layout.addLayout(filter_row)

        # Hang 4: Frame Padding
        padding_row = QtWidgets.QHBoxLayout()
        lbl_padding = QtWidgets.QLabel(u"Frame dem (Padding):")
        lbl_padding.setFixedWidth(LABEL_WIDTH)
        padding_row.addWidget(lbl_padding)

        self.sm_padding_spin = QtWidgets.QSpinBox()
        self.sm_padding_spin.setRange(0, 50)
        self.sm_padding_spin.setValue(5)
        self.sm_padding_spin.setFixedWidth(80)
        self.sm_padding_spin.setToolTip(u"So frame mo rong truoc/sau bookmark khi cat key")
        padding_row.addWidget(self.sm_padding_spin)
        padding_row.addStretch()
        split_group_layout.addLayout(padding_row)

        # Hang 7: Nut Bat dau Tach
        btn_row = QtWidgets.QHBoxLayout()
        lbl_btn_spacer = QtWidgets.QWidget()
        lbl_btn_spacer.setFixedWidth(LABEL_WIDTH)
        btn_row.addWidget(lbl_btn_spacer)

        self.sm_split_btn = QtWidgets.QPushButton(u"🚀 Bat dau Tach Shot vao Pipeline")
        self.sm_split_btn.setObjectName("accent_btn")
        self.sm_split_btn.clicked.connect(self.on_split_layout)
        btn_row.addWidget(self.sm_split_btn)
        split_group_layout.addLayout(btn_row)

        scroll_layout.addWidget(split_group)

        # ---- KHU VUC 2: Gop Animation Canh Tong ----
        combine_group = QtWidgets.QGroupBox(u"Gop Animation Canh Tong (Combine)")
        combine_group_layout = QtWidgets.QVBoxLayout(combine_group)
        combine_group_layout.setContentsMargins(12, 16, 12, 12)
        combine_group_layout.setSpacing(10)

        # Hang 0: Khoang shot can gop
        c_range_row = QtWidgets.QHBoxLayout()
        lbl_crange = QtWidgets.QLabel(u"Khoang shot can gop:")
        lbl_crange.setFixedWidth(LABEL_WIDTH)
        c_range_row.addWidget(lbl_crange)

        self.sm_combine_start = QtWidgets.QSpinBox()
        self.sm_combine_start.setRange(1, 999)
        self.sm_combine_start.setValue(1)
        self.sm_combine_start.setFixedWidth(80)

        self.sm_combine_end = QtWidgets.QSpinBox()
        self.sm_combine_end.setRange(1, 999)
        self.sm_combine_end.setValue(30)
        self.sm_combine_end.setFixedWidth(80)

        c_range_row.addWidget(QtWidgets.QLabel(u"Tu:"))
        c_range_row.addWidget(self.sm_combine_start)
        c_range_row.addWidget(QtWidgets.QLabel(u" Den:"))
        c_range_row.addWidget(self.sm_combine_end)
        c_range_row.addStretch()
        combine_group_layout.addLayout(c_range_row)

        # Hang 1: Checkbox Bake Constraints
        c_bake_row = QtWidgets.QHBoxLayout()
        lbl_cbake_spacer = QtWidgets.QWidget()
        lbl_cbake_spacer.setFixedWidth(LABEL_WIDTH)
        c_bake_row.addWidget(lbl_cbake_spacer)

        self.sm_bake_constraints_cb = QtWidgets.QCheckBox(u"Tu dong Bake Constraints (Locator/Rig)")
        self.sm_bake_constraints_cb.setChecked(True)
        c_bake_row.addWidget(self.sm_bake_constraints_cb)
        c_bake_row.addStretch()
        combine_group_layout.addLayout(c_bake_row)

        # Hang 2: Checkbox Smart Bake
        c_sbake_row = QtWidgets.QHBoxLayout()
        lbl_csbake_spacer = QtWidgets.QWidget()
        lbl_csbake_spacer.setFixedWidth(LABEL_WIDTH)
        c_sbake_row.addWidget(lbl_csbake_spacer)

        self.sm_smart_bake_cb = QtWidgets.QCheckBox(u"Smart Bake (Bake thua giu key cuc tri)")
        self.sm_smart_bake_cb.setChecked(True)
        c_sbake_row.addWidget(self.sm_smart_bake_cb)
        c_sbake_row.addStretch()
        combine_group_layout.addLayout(c_sbake_row)

        # Hang 3: Key Reducer Threshold
        threshold_row = QtWidgets.QHBoxLayout()
        lbl_threshold = QtWidgets.QLabel(u"Key Reducer Threshold:")
        lbl_threshold.setFixedWidth(LABEL_WIDTH)
        threshold_row.addWidget(lbl_threshold)

        self.sm_threshold_spin = QtWidgets.QDoubleSpinBox()
        self.sm_threshold_spin.setRange(0.01, 5.0)
        self.sm_threshold_spin.setValue(0.1)
        self.sm_threshold_spin.setSingleStep(0.05)
        self.sm_threshold_spin.setFixedWidth(80)
        self.sm_threshold_spin.setToolTip(u"Nguong cho bo loc keyReducer (nho hon = giu nhieu key hon)")
        threshold_row.addWidget(self.sm_threshold_spin)
        threshold_row.addStretch()
        combine_group_layout.addLayout(threshold_row)

        # Hang 4: Frame Padding cho gop
        c_padding_row = QtWidgets.QHBoxLayout()
        lbl_cpadding = QtWidgets.QLabel(u"Frame dem khi xuat/nhap:")
        lbl_cpadding.setFixedWidth(LABEL_WIDTH)
        c_padding_row.addWidget(lbl_cpadding)

        self.sm_combine_padding_spin = QtWidgets.QSpinBox()
        self.sm_combine_padding_spin.setRange(0, 50)
        self.sm_combine_padding_spin.setValue(5)
        self.sm_combine_padding_spin.setFixedWidth(80)
        c_padding_row.addWidget(self.sm_combine_padding_spin)
        c_padding_row.addStretch()
        combine_group_layout.addLayout(c_padding_row)

        # Hang 5: Nut Gop Canh
        c_btn_row = QtWidgets.QHBoxLayout()
        lbl_cbtn_spacer = QtWidgets.QWidget()
        lbl_cbtn_spacer.setFixedWidth(LABEL_WIDTH)
        c_btn_row.addWidget(lbl_cbtn_spacer)

        self.sm_combine_btn = QtWidgets.QPushButton(u"📦 Tien hanh Gop Canh & Xuat File Cum")
        self.sm_combine_btn.setObjectName("accent_btn")
        self.sm_combine_btn.clicked.connect(self.on_combine_shots)
        c_btn_row.addWidget(self.sm_combine_btn)
        combine_group_layout.addLayout(c_btn_row)

        scroll_layout.addWidget(combine_group)

        # ---- KHU VUC 3: Tien ich & Thu vien ----
        util_group = QtWidgets.QGroupBox(u"Tien ich & Thu vien Studio Library")
        util_layout = QtWidgets.QVBoxLayout(util_group)
        util_layout.setContentsMargins(10, 12, 10, 10)
        util_layout.setSpacing(8)

        # Hang 1: Cac nut mo nhanh theo Danh muc (Characters, Animals, Props, Common)
        cat_btn_row = QtWidgets.QHBoxLayout()
        cat_btn_row.setSpacing(6)

        self.sm_chars_stlib_btn = QtWidgets.QPushButton(u"👤 Characters")
        self.sm_chars_stlib_btn.setObjectName("accent_btn")
        self.sm_chars_stlib_btn.setToolTip(u"Mo thu vien Nhan Vat:\nZ:\\Animeow_Production\\Enjo_Library\\01_Characters")
        self.sm_chars_stlib_btn.clicked.connect(lambda: self.on_open_studio_library(
            library_path=r"Z:\Animeow_Production\Enjo_Library\01_Characters",
            library_name=u"Characters Library"
        ))

        self.sm_anim_stlib_btn = QtWidgets.QPushButton(u"🐾 Animals")
        self.sm_anim_stlib_btn.setObjectName("accent_btn")
        self.sm_anim_stlib_btn.setToolTip(u"Mo thu vien Dong Vat:\nZ:\\Animeow_Production\\Enjo_Library\\02_Animals")
        self.sm_anim_stlib_btn.clicked.connect(lambda: self.on_open_studio_library(
            library_path=r"Z:\Animeow_Production\Enjo_Library\02_Animals",
            library_name=u"Animals Library"
        ))

        self.sm_props_stlib_btn = QtWidgets.QPushButton(u"🚗 Props & Vehicles")
        self.sm_props_stlib_btn.setObjectName("accent_btn")
        self.sm_props_stlib_btn.setToolTip(u"Mo thu vien Dao Cu & Xe Co:\nZ:\\Animeow_Production\\Enjo_Library\\03_Props_Vehicles")
        self.sm_props_stlib_btn.clicked.connect(lambda: self.on_open_studio_library(
            library_path=r"Z:\Animeow_Production\Enjo_Library\03_Props_Vehicles",
            library_name=u"Props & Vehicles Library"
        ))

        self.sm_common_stlib_btn = QtWidgets.QPushButton(u"✋ Common Poses")
        self.sm_common_stlib_btn.setObjectName("accent_btn")
        self.sm_common_stlib_btn.setToolTip(u"Mo thu vien Dangs & Biieu Cam Dung Chung:\nZ:\\Animeow_Production\\Enjo_Library\\04_Common_Library")
        self.sm_common_stlib_btn.clicked.connect(lambda: self.on_open_studio_library(
            library_path=r"Z:\Animeow_Production\Enjo_Library\04_Common_Library",
            library_name=u"Common Library"
        ))

        cat_btn_row.addWidget(self.sm_chars_stlib_btn)
        cat_btn_row.addWidget(self.sm_anim_stlib_btn)
        cat_btn_row.addWidget(self.sm_props_stlib_btn)
        cat_btn_row.addWidget(self.sm_common_stlib_btn)
        util_layout.addLayout(cat_btn_row)

        # Hang 2: Cac nut tien ich va quan ly thu vien
        other_util_row = QtWidgets.QHBoxLayout()
        other_util_row.setSpacing(6)

        self.sm_open_stlib_btn = QtWidgets.QPushButton(u"📖 Studio Library Tong")
        self.sm_open_stlib_btn.setToolTip(u"Click chuot trai: Mo Studio Library Tong (Enjo_Library).\nChuot phai: Chon nhanh danh muc hoac Manager.")
        self.sm_open_stlib_btn.clicked.connect(lambda: self.on_open_studio_library(
            library_path=r"Z:\Animeow_Production\Enjo_Library",
            library_name=u"Studio Library"
        ))
        self.sm_open_stlib_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sm_open_stlib_btn.customContextMenuRequested.connect(self.show_studiolibrary_context_menu)
        other_util_row.addWidget(self.sm_open_stlib_btn)

        self.sm_manage_stlib_btn = QtWidgets.QPushButton(u"⚙️ Studio Library Manager")
        self.sm_manage_stlib_btn.setToolTip(u"Quan ly danh sach cac Thu vien Studio Library cua du an")
        self.sm_manage_stlib_btn.clicked.connect(self.on_open_studiolibrary_manager)
        other_util_row.addWidget(self.sm_manage_stlib_btn)

        self.sm_export_csv_btn = QtWidgets.QPushButton(u"📄 Xuat CSV Bookmarks")
        self.sm_export_csv_btn.clicked.connect(self.on_export_bookmarks_csv)
        other_util_row.addWidget(self.sm_export_csv_btn)

        util_layout.addLayout(other_util_row)

        scroll_layout.addWidget(util_group)
        scroll_layout.addStretch()

    # ================================================================
    # SU KIEN & LOGIC - Tab 2: Tach / Gop Canh
    # ================================================================

    def on_scan_bookmarks(self):
        """Quet toan bo timeSliderBookmark dang so tu scene hien tai"""
        self.sm_bookmark_list.clear()

        # Dam bao plugin timeSliderBookmark duoc nap
        if not cmds.pluginInfo('timeSliderBookmark', q=True, loaded=True):
            try:
                cmds.loadPlugin('timeSliderBookmark')
            except Exception:
                QtWidgets.QMessageBox.warning(self, u"Loi", u"Khong the nap plugin timeSliderBookmark.")
                return

        bookmarks = cmds.ls(type='timeSliderBookmark') or []
        if not bookmarks:
            QtWidgets.QMessageBox.information(self, u"Thong bao", u"Khong tim thay Bookmark nao trong scene.")
            return

        valid_items = []
        for bm in bookmarks:
            try:
                b_name = cmds.getAttr(bm + ".name")
            except Exception:
                b_name = bm

            # Chi lay cac bookmark duoc dat ten dang so
            try:
                bm_num = int(b_name)
            except ValueError:
                continue

            start_f = cmds.getAttr(bm + ".timeRangeStart")
            end_f = cmds.getAttr(bm + ".timeRangeStop")
            valid_items.append((bm_num, b_name, start_f, end_f, bm))

        # Sap xep theo so thu tu
        valid_items.sort(key=lambda x: x[0])

        for bm_num, b_name, start_f, end_f, bm_node in valid_items:
            display_text = u"Shot %02d  |  Frame: %.0f - %.0f" % (bm_num, start_f, end_f)
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, {
                "num": bm_num, "name": b_name,
                "start": start_f, "end": end_f, "node": bm_node
            })
            self.sm_bookmark_list.addItem(item)
            item.setSelected(True)  # Tu dong tich chon het

        self.sm_bookmark_count_lbl.setText(u"(Tim thay %d)" % len(valid_items))
        QtWidgets.QMessageBox.information(
            self, u"Ket qua",
            u"Tim thay %d bookmark hop le (dang so)." % len(valid_items)
        )

    def get_smart_selection(self):
        """
        Lay danh sach cac doi tuong can giu key:
        1. Uu tien lay truc tiep vung chon hien tai cua nguoi dung.
        2. Neu khong co vung chon, tu dong quet toan bo anim curves hoat dong trong scene,
           tim cac node dich dang ket noi va loai tru camera rig, camera transform.
        """
        selection = cmds.ls(sl=True) or []
        if selection:
            return selection

        print(u"[Pipeline] Khong co vung chon thu cong. Dang tu dong quet toan bo control co keyframe trong scene...")

        # Tim tat ca anim curves dang ton tai
        anim_curves = cmds.ls(type=['animCurveTL', 'animCurveTA', 'animCurveTU', 'animCurveTT']) or []
        if not anim_curves:
            return []

        keyed_nodes = []
        for curve in anim_curves:
            connections = cmds.listConnections(curve + ".output", plugs=True) or []
            for conn in connections:
                node_name = conn.split('.')[0]
                keyed_nodes.append(node_name)

        keyed_nodes = list(set(keyed_nodes))

        # Dinh danh cac node camera can bao ho
        cameras = cmds.ls(type='camera') or []
        camera_transforms = []
        for cam in cameras:
            parents = cmds.listRelatives(cam, parent=True) or []
            if parents:
                camera_transforms.append(parents[0])

        # Loc bo camera
        final_selection = []
        for node in keyed_nodes:
            if node in camera_transforms:
                continue
            node_lower = node.lower()
            if any(cam_word in node_lower for cam_word in ['cam', 'camera', 'shot_cam']):
                continue
            final_selection.append(node)

        print(u"[Pipeline] Tu dong quet thanh cong %d control co keyframe (da bao ve cac node camera)." % len(final_selection))
        return final_selection

    def on_split_layout(self):
        """Tach file Layout tong thanh cac file shot le dua tren bookmarks da quet"""
        import os as _os
        import json as _json
        import tempfile as _tempfile

        # 1. Kiem tra dau vao
        selected_items = self.sm_bookmark_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, u"Thieu du lieu", u"Chua co bookmark nao duoc chon.\nHay nhan 'Quet Bookmarks' truoc.")
            return

        # Xac dinh file nguon
        scene_name = cmds.file(q=True, sn=True)
        if not scene_name:
            QtWidgets.QMessageBox.warning(self, u"Chua luu file", u"Hay SAVE file Maya hien tai truoc khi tach shot!")
            return
        scene_name = scene_name.replace('\\', '/')

        saved_selection = self.get_smart_selection()
        if not saved_selection:
            QtWidgets.QMessageBox.warning(
                self, u"Thieu Selection",
                u"Khong tim thay Control/Object nao co keyframe trong scene va khong co vung chon thu cong de thuc hien cat key!"
            )
            return

        # 2. Lay thong tin project/episode hien tai tu Tab 1
        project = self.proj_combo.currentText()
        episode = self.ep_combo.currentText()
        if not project or not episode:
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Hay chon Project va Episode o Tab 'Quan Ly File' truoc.")
            return

        # 3. Loc theo khoang filter (neu co)
        start_filter = self.sm_split_start.value()
        end_filter = self.sm_split_end.value()
        padding = self.sm_padding_spin.value()

        bookmarks_data = []
        for item in selected_items:
            data = item.data(QtCore.Qt.UserRole)
            bm_num = data["num"]
            if start_filter != 0 and bm_num < start_filter:
                continue
            if end_filter != 0 and bm_num > end_filter:
                continue
            bookmarks_data.append(data)

        if not bookmarks_data:
            QtWidgets.QMessageBox.warning(self, u"Khong khop", u"Khong co bookmark nao khop voi khoang loc da nhap.")
            return

        # 4. Xac nhan
        msg = u"Se tach %d shot tu file Layout dang mo vao Pipeline.\n" % len(bookmarks_data)
        msg += u"Project: %s\nEpisode: %s\n" % (project, episode)
        msg += u"Frame Padding: ±%d frames\n" % padding
        msg += u"Che do: Truc tiep (Co progress bar chong treo do Maya)\n"
        msg += u"\nBan co chac chan?"

        reply = QtWidgets.QMessageBox.question(self, u"Xac nhan Tach Shot", msg,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 5. Luu file hien tai truoc khi thao tac (chi luu neu scene hien tai da duoc dat ten/duoc luu truoc do)
        current_scene = cmds.file(q=True, sn=True)
        if current_scene:
            try:
                cmds.file(save=True, force=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the luu file hien tai:\n%s" % str(e))
                return



        # ============================================================
        # CHE DO CHAY TRUC TIEP (FOREGROUND)
        # ============================================================
        # 6. Chuyen sang DG mode de tranh loi parallel evaluation
        original_eval_mode = cmds.evaluationManager(q=True, mode=True)[0]
        if original_eval_mode != 'off':
            cmds.evaluationManager(mode='off')

        base_name = _os.path.basename(scene_name)
        _, ext = _os.path.splitext(base_name)
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"

        # Khoi tao progress dialog cho che do truc tiep de tranh do giao dien
        progress = QtWidgets.QProgressDialog(
            u"Dang tach shot truc tiep trong Maya...",
            u"Huy bo", 0, len(bookmarks_data), self
        )
        progress.setWindowTitle(u"Dang Tach Shot (Foreground)")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        success_count = 0
        try:
            for i, data in enumerate(bookmarks_data):
                if progress.wasCanceled():
                    print(u"[Split] Nguoi dung da huy bo tien trinh.")
                    break

                # Cap nhat progress bar va ve lai GUI de tranh freeze
                progress.setValue(i)
                progress.setLabelText(u"Dang xu ly Shot %02d (%d/%d)..." % (data["num"], i + 1, len(bookmarks_data)))
                QtWidgets.QApplication.processEvents()

                bm_num = data["num"]
                start_f = data["start"]
                end_f = data["end"]

                # Xay duong dan luu file shot le
                filepath, shot_dir = self.file_manager.build_split_shot_path(
                    project, episode, bm_num, task="Anim"
                )
                if not filepath:
                    print(u"[Split] Khong the xay duong dan cho shot %d" % bm_num)
                    continue

                # Kiem tra trung file de chong ghi de du lieu hoat hinh cua artist
                if _os.path.exists(filepath):
                    confirm = cmds.confirmDialog(
                        title=u"File da ton tai",
                        message=u"File hoat hinh le da ton tai:\n%s\n\nBan co muon ghi de (lam mat keyframe anim cu cua shot nay) khong?" % _os.path.basename(filepath),
                        button=[u"Ghi de (Overwrite)", u"Bo qua (Skip)", u"Huy toan bo (Cancel)"],
                        defaultButton=u"Bo qua (Skip)",
                        cancelButton=u"Bo qua (Skip)"
                    )
                    if confirm == u"Bo qua (Skip)":
                        print(u"[Split] Da bo qua shot %d de bao ve file Anim cu." % bm_num)
                        continue
                    elif confirm == u"Huy toan bo (Cancel)":
                        print(u"[Split] Da huy tien trinh tach theo yeu cau.")
                        break

                # Tao thu muc neu chua co
                if not _os.path.exists(shot_dir):
                    _os.makedirs(shot_dir)

                # Thao tac trong undo chunk
                cmds.undoInfo(openChunk=True)
                try:
                    # Xoa bookmark khac
                    all_bms = cmds.ls(type='timeSliderBookmark') or []
                    for b in all_bms:
                        try:
                            check_name = cmds.getAttr(b + ".name")
                        except Exception:
                            check_name = b
                        if check_name != data["name"]:
                            try:
                                cmds.delete(b)
                            except Exception:
                                pass

                    # Truy quet toan bo anim curves trong scene de don sach keyframe thua 100% (bao gom ca camera shape, custom attributes, v.v.)
                    try:
                        anim_curves = cmds.ls(type='animCurve') or []
                    except Exception:
                        anim_curves = []

                    # Cat key tren tung curve
                    for curve in anim_curves:
                        try:
                            cmds.cutKey(curve, time=(-9999999, start_f - padding - 0.01), option="keys", clear=True)
                        except Exception:
                            pass
                        try:
                            cmds.cutKey(curve, time=(end_f + padding + 0.01, 9999999), option="keys", clear=True)
                        except Exception:
                            pass

                    # Thiet lap timeline
                    cmds.playbackOptions(
                        min=start_f, max=end_f,
                        animationStartTime=start_f, animationEndTime=end_f
                    )
                except Exception as e:
                    print(u"[Split] Loi xu ly shot %d: %s" % (bm_num, str(e)))
                finally:
                    cmds.undoInfo(closeChunk=True)

                # Luu file shot le
                cmds.file(rename=filepath.replace('\\', '/'))
                try:
                    cmds.file(save=True, force=True, type=file_type)
                    print(u"==> Da xuat shot le thanh cong: %s" % _os.path.basename(filepath))
                    success_count += 1
                except Exception as e:
                    print(u"[Split] Loi luu file shot %d: %s" % (bm_num, str(e)))

                # Undo de tra scene ve trang thai ban dau
                cmds.undo()

            progress.setValue(len(bookmarks_data))

        finally:
            # Phuc hoi trang thai ban dau
            cmds.file(rename=scene_name)
            if original_eval_mode != 'off':
                cmds.evaluationManager(mode=original_eval_mode)
            if saved_selection:
                try:
                    cmds.select(saved_selection)
                except Exception:
                    pass

        QtWidgets.QMessageBox.information(
            self, u"Hoan tat",
            u"Da tach thanh cong %d/%d shot!" % (success_count, len(bookmarks_data))
        )
        # Lam moi danh sach file o Tab 1
        self.refresh_files_list()



    def on_combine_shots(self):
        """Gop Animation shot le tu file Layout tong bang cach cat key theo bookmark"""
        import os as _os

        # 1. Kiem tra dau vao
        saved_selection = self.get_smart_selection()
        if not saved_selection:
            QtWidgets.QMessageBox.warning(
                self, u"Thieu Selection",
                u"Khong tim thay Control/Object nao co keyframe trong scene va khong co vung chon thu cong de thuc hien gop!"
            )
            return

        scene_name = cmds.file(q=True, sn=True)
        if not scene_name:
            QtWidgets.QMessageBox.warning(self, u"Chua luu file", u"Hay SAVE file Maya hien tai truoc khi gop shot!")
            return
        scene_name = scene_name.replace('\\', '/')

        project = self.proj_combo.currentText()
        episode = self.ep_combo.currentText()
        if not project or not episode:
            QtWidgets.QMessageBox.warning(self, u"Thieu thong tin", u"Hay chon Project va Episode o Tab 'Quan Ly File' truoc.")
            return

        start_shot = self.sm_combine_start.value()
        end_shot = self.sm_combine_end.value()
        if start_shot > end_shot:
            QtWidgets.QMessageBox.warning(self, u"Loi", u"Khoang shot khong hop le (Start > End).")
            return

        padding = self.sm_combine_padding_spin.value()
        do_bake = self.sm_bake_constraints_cb.isChecked()
        do_smart_bake = self.sm_smart_bake_cb.isChecked()
        threshold = self.sm_threshold_spin.value()

        # 2. Quet bookmarks trong scene de lay khoang thoi gian
        if not cmds.pluginInfo('timeSliderBookmark', q=True, loaded=True):
            try:
                cmds.loadPlugin('timeSliderBookmark')
            except Exception:
                pass

        bookmarks = cmds.ls(type='timeSliderBookmark') or []
        valid_bookmarks = []
        global_start = 9999999
        global_end = -9999999

        for bm in bookmarks:
            try:
                b_name = cmds.getAttr(bm + ".name")
            except Exception:
                b_name = bm
            try:
                bm_num = int(b_name)
            except ValueError:
                continue
            if bm_num < start_shot or bm_num > end_shot:
                continue

            start_f = cmds.getAttr(bm + ".timeRangeStart")
            end_f = cmds.getAttr(bm + ".timeRangeStop")
            if start_f < global_start:
                global_start = start_f
            if end_f > global_end:
                global_end = end_f
            valid_bookmarks.append(bm)

        if not valid_bookmarks:
            QtWidgets.QMessageBox.warning(
                self, u"Khong khop",
                u"Khong tim thay bookmark nao trong khoang %d - %d." % (start_shot, end_shot)
            )
            return

        # 3. Xay duong dan file gop
        combine_path = self.file_manager.build_combine_file_path(project, episode, start_shot, end_shot)
        if not combine_path:
            QtWidgets.QMessageBox.warning(self, u"Loi", u"Khong the xay duong dan file gop.")
            return

        combine_dir = _os.path.dirname(combine_path)

        # 4. Xac nhan
        msg = u"Se gop shot tu %d den %d thanh file cum tong:\n%s\n\n" % (
            start_shot, end_shot, _os.path.basename(combine_path))
        if do_bake:
            msg += u"✅ Tu dong Bake Constraints\n"
        if do_smart_bake:
            msg += u"✅ Smart Bake (threshold=%.2f)\n" % threshold
        msg += u"\nBan co chac chan?"
        reply = QtWidgets.QMessageBox.question(self, u"Xac nhan Gop Shot", msg,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 5. Luu file hien tai
        try:
            cmds.file(save=True, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the luu file:\n%s" % str(e))
            return

        # 6. Chuyen sang DG mode
        original_eval_mode = cmds.evaluationManager(q=True, mode=True)[0]
        if original_eval_mode != 'off':
            cmds.evaluationManager(mode='off')

        undo_was_enabled = cmds.undoInfo(q=True, state=True)
        if not undo_was_enabled:
            cmds.undoInfo(state=True)

        base_name = _os.path.basename(scene_name)
        _, ext = _os.path.splitext(base_name)
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"

        try:
            # 7. Bake Constraints neu duoc chon
            if do_bake:
                print(u"[Combine] Dang Bake Constraints...")
                self.bake_and_clean_constraints(saved_selection)

            # 8. Smart Bake neu duoc chon
            if do_smart_bake:
                print(u"[Combine] Dang ap dung Smart Bake...")
                self.apply_smart_bake_filter(saved_selection, threshold)

            # 9. Thuc hien gop trong undo chunk
            cmds.undoInfo(openChunk=True)
            try:
                # Xoa bookmarks khong thuoc khoang gop
                all_bms = cmds.ls(type='timeSliderBookmark') or []
                for b in all_bms:
                    if b not in valid_bookmarks:
                        try:
                            cmds.delete(b)
                        except Exception:
                            pass

                # Truy quet toan bo anim curves trong scene de don sach keyframe thua 100%
                try:
                    anim_curves = cmds.ls(type='animCurve') or []
                except Exception:
                    anim_curves = []

                # Cat key tren tung curve
                for curve in anim_curves:
                    try:
                        cmds.cutKey(curve, time=(-9999999, global_start - padding - 0.01), option="keys", clear=True)
                    except Exception:
                        pass
                    try:
                        cmds.cutKey(curve, time=(global_end + padding + 0.01, 9999999), option="keys", clear=True)
                    except Exception:
                        pass

                # Thiet lap timeline
                cmds.playbackOptions(
                    min=global_start, max=global_end,
                    animationStartTime=global_start, animationEndTime=global_end
                )
            except Exception as e:
                print(u"[Combine] Loi: %s" % str(e))
            finally:
                cmds.undoInfo(closeChunk=True)

            # 10. Tao thu muc va luu file gop
            if not _os.path.exists(combine_dir):
                _os.makedirs(combine_dir)

            cmds.file(rename=combine_path.replace('\\', '/'))
            try:
                cmds.file(save=True, force=True, type=file_type)
                print(u"==> Da xuat file gop cum thanh cong: %s" % _os.path.basename(combine_path))
            except Exception as e:
                print(u"[Combine] Loi luu file: %s" % str(e))

            # Undo de tra scene ve trang thai ban dau
            cmds.undo()

        finally:
            cmds.file(rename=scene_name)
            if original_eval_mode != 'off':
                cmds.evaluationManager(mode=original_eval_mode)
            if not undo_was_enabled:
                cmds.undoInfo(state=False)
            if saved_selection:
                try:
                    cmds.select(saved_selection)
                except Exception:
                    pass

        QtWidgets.QMessageBox.information(
            self, u"Hoan tat",
            u"Da gop cum shot %d-%d thanh cong!\n\nFile: %s" % (
                start_shot, end_shot, _os.path.basename(combine_path))
        )

    def bake_and_clean_constraints(self, selection):
        """
        Tu dong phat hien constraint tren cac doi tuong da chon,
        thuc hien Bake Simulation roi xoa constraint.
        """
        constraint_types = [
            'parentConstraint', 'pointConstraint', 'orientConstraint',
            'scaleConstraint', 'aimConstraint', 'geometryConstraint'
        ]

        objects_to_bake = []
        constraints_to_delete = []

        for obj in selection:
            connections = cmds.listConnections(obj, source=True, destination=False) or []
            found = False
            for node in connections:
                n_type = cmds.nodeType(node)
                if n_type in constraint_types or n_type == 'pairBlend':
                    constraints_to_delete.append(node)
                    found = True
            if found:
                objects_to_bake.append(obj)

        if not objects_to_bake:
            print(u"[Bake] Khong tim thay control nao bi constraint trong vung chon.")
            return

        s_time = cmds.playbackOptions(q=True, minTime=True)
        e_time = cmds.playbackOptions(q=True, maxTime=True)

        print(u"[Bake] Dang bake cho %d objects co constraint..." % len(objects_to_bake))

        cmds.bakeResults(
            objects_to_bake,
            t=(s_time, e_time),
            simulation=True,
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
            at=["tx", "ty", "tz", "rx", "ry", "rz"]
        )

        if constraints_to_delete:
            constraints_to_delete = list(set(constraints_to_delete))
            cmds.delete(constraints_to_delete)
            print(u"[Bake] Da don dep xong %d constraints." % len(constraints_to_delete))

    def apply_smart_bake_filter(self, selection, threshold=0.1):
        """
        Ap dung Smart Bake: bake thua roi giam keyframe bang keyReducer.
        """
        # 1. Lay tat ca anim curves tu cac objects duoc chon
        anim_curves = cmds.keyframe(selection, q=True, name=True) or []
        if not anim_curves:
            print(u"[SmartBake] Khong tim thay anim curve nao.")
            return

        anim_curves = list(set(anim_curves))

        # 2. Ap dung bo loc keyReducer
        try:
            cmds.filterCurve(anim_curves, filter="keyReducer", precisionMode=0, precision=threshold)
            print(u"[SmartBake] Da ap dung keyReducer (threshold=%.2f) cho %d anim curves." % (
                threshold, len(anim_curves)))
        except Exception as e:
            print(u"[SmartBake] Loi: %s" % str(e))

    def on_open_studio_library(self, library_path=None, library_name=None):
        """
        Mo giao dien Studio Library UI voi duong dan va ten thu vien chi dinh.
        Neu khong truyen tham so, tu dong mo thu vien dung chung theo Project dang chon (Kidsong hoac Lolo).
        """
        if not library_path:
            current_proj = self.proj_combo.currentText() if hasattr(self, 'proj_combo') else ""
            if current_proj:
                library_path = self.file_manager.get_project_studiolibrary_dir(current_proj)
                library_name = u"Studio Library (%s)" % current_proj
            else:
                library_path = r"Z:\Animeow_Production\Enjo_Library\Kidsong"
                library_name = "Kidsong Studio Library"
                
        if not library_name:
            library_name = os.path.basename(library_path)
            
        if not os.path.exists(library_path):
            try:
                os.makedirs(library_path)
            except Exception:
                pass

        try:
            import studiolibrary
            # Reset bien cua so de tranh xung dot voi cua so cu da dong
            studiolibrary._window = None
            studiolibrary.main(name=library_name, path=library_path)
            print(u"[StudioLibrary] Da mo Studio Library UI: %s (%s)" % (library_name, library_path))
        except ImportError:
            QtWidgets.QMessageBox.warning(
                self, u"Loi Import",
                u"Khong the import Studio Library.\n"
                u"Kiem tra thu muc: thirdparty/studiolibrary/src/"
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, u"Loi",
                u"Loi khi mo Studio Library UI:\n%s" % exception_to_unicode(e)
            )

    def show_studiolibrary_context_menu(self, pos):
        """Menu ngu canh cho nut Studio Library"""
        menu = QtWidgets.QMenu(self)
        
        act_root = menu.addAction(u"🎬 Mo Studio Library Tong (Enjo_Library)")
        menu.addSeparator()
        act_chars = menu.addAction(u"👤 Mo Library Characters (01_Characters)")
        act_anim = menu.addAction(u"🐾 Mo Library Animals (02_Animals)")
        act_props = menu.addAction(u"🚗 Mo Library Props & Vehicles (03_Props_Vehicles)")
        act_common = menu.addAction(u"✋ Mo Library Common Poses (04_Common_Library)")
        act_user = menu.addAction(u"🎨 Mo Library User Scratch (05_User_Scratch)")
        menu.addSeparator()
        act_manage = menu.addAction(u"⚙️ Mo Cua So Studio Library Manager...")
        
        sender_btn = self.sender() if hasattr(self, 'sender') and self.sender() else self.sm_open_stlib_btn
        action = menu.exec_(sender_btn.mapToGlobal(pos))
        if action == act_root:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library", library_name="Studio Library")
        elif action == act_chars:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library\01_Characters", library_name="Characters Library")
        elif action == act_anim:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library\02_Animals", library_name="Animals Library")
        elif action == act_props:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library\03_Props_Vehicles", library_name="Props & Vehicles Library")
        elif action == act_common:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library\04_Common_Library", library_name="Common Library")
        elif action == act_user:
            self.on_open_studio_library(library_path=r"Z:\Animeow_Production\Enjo_Library\05_User_Scratch", library_name="User Scratch Library")
        elif action == act_manage:
            self.on_open_studiolibrary_manager()

    def on_open_studiolibrary_manager(self):
        """Mo cua so Studio Library Manager"""
        dialog = StudioLibraryManagerDialog(main_ui=self, parent=self)
        dialog.exec_()

    def on_export_bookmarks_csv(self):
        """Xuat danh sach Bookmarks ra file CSV"""
        import csv

        if not cmds.pluginInfo('timeSliderBookmark', q=True, loaded=True):
            try:
                cmds.loadPlugin('timeSliderBookmark')
            except Exception:
                pass

        bookmarks = cmds.ls(type='timeSliderBookmark') or []
        if not bookmarks:
            QtWidgets.QMessageBox.information(self, u"Thong bao", u"Khong tim thay Bookmark nao.")
            return

        path = cmds.fileDialog2(ff="CSV Files (*.csv)", ds=2, fm=0, cap="Save Bookmark Data")
        if not path:
            return

        data = [["Bookmark Name", "Start Frame", "End Frame"]]
        for bm in bookmarks:
            try:
                n = cmds.getAttr(bm + ".name")
            except Exception:
                n = bm
            s = cmds.getAttr(bm + ".timeRangeStart")
            e = cmds.getAttr(bm + ".timeRangeStop")
            data.append([n, s, e])

        try:
            if sys.version_info[0] < 3:
                with open(path[0], 'wb') as f:
                    csv.writer(f).writerows(data)
            else:
                with open(path[0], 'w', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerows(data)
            QtWidgets.QMessageBox.information(self, u"Thanh cong", u"Da xuat bookmarks ra CSV thanh cong!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Loi", u"Khong the ghi file CSV:\n%s" % str(e))


def show_window():
    import sys
    
    # 1. Dong va giai phong bo nho cua giao dien cu tu sys module
    old_ui = getattr(sys, "_animeow_enjo_pipeline_ui", None)
    if old_ui is not None:
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        sys._animeow_enjo_pipeline_ui = None
        
    # 2. Xoa cac workspace control cu cua ca phien ban cu va moi
    old_controls = ["AnimeowAnimToolkitWorkspaceControl", "AnimeowEnjoPipelineWorkspaceControl"]
    for ctrl in old_controls:
        if cmds.workspaceControl(ctrl, exists=True):
            try:
                cmds.deleteUI(ctrl)
            except Exception:
                pass
            
    # 3. Tao instance moi va luu tham chieu vao sys module
    ui_instance = AnimeowMayaToolkitUI()
    sys._animeow_enjo_pipeline_ui = ui_instance
    
    # 4. Hien thi duoi dang dockable panel
    ui_instance.show(
        dockable=True,
        workspaceControlName=AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME,
        area="right",
        floating=False,
        allowedArea="left|right"
    )
    
    # 5. Cap nhat tieu de hien thi cho tab trong Maya
    if cmds.workspaceControl(AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, exists=True):
        cmds.workspaceControl(
            AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, 
            edit=True, 
            label=AnimeowMayaToolkitUI.WINDOW_TITLE
        )
