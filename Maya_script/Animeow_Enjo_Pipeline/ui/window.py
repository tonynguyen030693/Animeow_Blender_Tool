# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import file_manager, playblast_manager

# --- Tự động thêm đường dẫn thirdparty/studiolibrary/src vào sys.path ---
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
            return u"Lỗi ngoại lệ hệ thống"

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
        self.setWindowTitle(u"Tạo Tập Phim Mới")
        self.setFixedWidth(420)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Tự động tính toán tiền tố dự án (ví dụ KS, LL, EL)
        proj_prefix = self.file_manager.get_episode_abbreviation(self.project, "Sample").split("_")[0]
        
        # Hướng dẫn quy chuẩn đặt tên
        guide_box = QtWidgets.QGroupBox(u"Quy ước đặt tên Tập phim")
        guide_layout = QtWidgets.QVBoxLayout(guide_box)
        guide_label = QtWidgets.QLabel(
            u"<b>Quy tắc đặt tên Tập phim:</b><br>"
            u"- Viết đầy đủ tên tập tiếng Anh, dùng dấu gạch dưới thay khoảng trắng.<br>"
            u"- Tên thư mục trên Server: Viết hoa chữ cái đầu nối bằng dấu gạch dưới.<br>"
            u"- Mã file Maya: Viết tắt chữ cái đầu + version V02.<br>"
            u"- Ví dụ: <i>Elevator_Safety_Song_V2</i> &rarr;<br>"
            u"  &bull; Thư mục: <b>Elevator_Safety_Song_V02</b><br>"
            u"  &bull; Mã file: <b>%s_ESS_V02</b>" % proj_prefix
        )
        guide_label.setStyleSheet("color: #FF9800;")
        guide_layout.addWidget(guide_label)
        layout.addWidget(guide_box)
        
        # Nhập tên đầy đủ
        layout.addWidget(QtWidgets.QLabel(u"Nhập tên đầy đủ của tập phim (không dùng dấu cách):"))
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Elevator_Safety_Song_V2 hoặc AAA_25")
        self.name_input.textChanged.connect(self.update_preview)
        layout.addWidget(self.name_input)
        
        # Ô nhập Tên thư mục Server (Cho phép custom)
        layout.addWidget(QtWidgets.QLabel(u"Tên thư mục sẽ tạo trên Server (Có thể sửa tay):"))
        self.folder_input = QtWidgets.QLineEdit()
        layout.addWidget(self.folder_input)
        
        # Ô nhập Mã viết tắt file Maya (Cho phép custom)
        layout.addWidget(QtWidgets.QLabel(u"Mã viết tắt của file Maya (Có thể sửa tay):"))
        self.abbrev_input = QtWidgets.QLineEdit()
        self.abbrev_input.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 13px;")
        layout.addWidget(self.abbrev_input)
        
        # Nút bấm
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        # Hiển thị Preview mặc định
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
        self.setWindowTitle(u"Báo Cáo Hiệu Năng Mở Cảnh - %s" % os.path.basename(filepath))
        self.resize(650, 500)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Thông tin tổng quan
        summary_group = QtWidgets.QGroupBox(u"Tổng quan thời gian nạp")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        summary_layout.setSpacing(6)
        
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>Tổng thời gian mở cảnh:</b> %.2f giây" % report["total_time"]))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>File cảnh gốc (Không Reference):</b> %.2f giây" % report["base_scene_time"]))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>Số lượng Reference:</b> %d" % len(report["references"])))
        summary_layout.addWidget(QtWidgets.QLabel(u"<b>Số lượng Script Nodes:</b> %d" % len(report["script_nodes"])))
        
        layout.addWidget(summary_group)
        
        # 2. Chi tiết các Reference
        ref_group = QtWidgets.QGroupBox(u"Chi tiết thời gian nạp từng Reference")
        ref_layout = QtWidgets.QVBoxLayout(ref_group)
        
        self.ref_table = QtWidgets.QTableWidget()
        self.ref_table.setColumnCount(3)
        self.ref_table.setHorizontalHeaderLabels([u"Tên Node / File", u"Thời gian", u"Trạng thái"])
        self.ref_table.horizontalHeader().setStretchLastSection(True)
        
        self.ref_table.setRowCount(len(report["references"]))
        for i, ref in enumerate(report["references"]):
            name = ref["node"] if ref["node"] else os.path.basename(ref["filepath"])
            time_item = QtWidgets.QTableWidgetItem("%.2fs" % ref["time"])
            status_item = QtWidgets.QTableWidgetItem(ref["status"])
            
            # Tô màu đỏ nếu load lâu (> 5.0 giây)
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
        
        # 3. Chi tiết các Script Nodes
        if report["script_nodes"]:
            script_group = QtWidgets.QGroupBox(u"Danh sách Script Nodes trong Scene (Cảnh báo Virus/Script chạy ngầm)")
            script_layout = QtWidgets.QVBoxLayout(script_group)
            
            self.script_list = QtWidgets.QListWidget()
            for script in report["script_nodes"]:
                item_text = u"%s (Type: %d) - Code: %s" % (script["name"], script["type"], script["preview"])
                item = QtWidgets.QListWidgetItem(item_text)
                self.script_list.addItem(item)
            script_layout.addWidget(self.script_list)
            layout.addWidget(script_group)
            
        # Nút đóng
        close_btn = QtWidgets.QPushButton(u"Đóng")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

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
        
        # Khởi tạo class quản lý
        self.file_manager = file_manager.FileManager(project_root=self.project_root)
        self.playblast_manager = playblast_manager.PlayblastManager()
        
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # ========================================================
        # Tab chính: Quản lý File & Playblast (Tab 1) + Split/Merge (Tab 2)
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

        # --- TAB 1: Quản Lý File & Playblast ---
        tab1_widget = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1_widget)
        tab1_layout.setContentsMargins(5, 5, 5, 5)
        tab1_layout.setSpacing(10)
        self.tab_widget.addTab(tab1_widget, u"📂 Quản Lý File & Playblast")
        self._build_tab1_contents(tab1_layout)

        # --- TAB 2: Tách / Gộp Cảnh ---
        tab2_widget = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2_widget)
        tab2_layout.setContentsMargins(5, 5, 5, 5)
        tab2_layout.setSpacing(10)
        self.tab_widget.addTab(tab2_widget, u"✂️ Tách / Gộp Cảnh")
        self._build_tab2_split_merge(tab2_layout)

    def _build_tab1_contents(self, parent_layout):
        """Xây dựng nội dung Tab 1 - Quản Lý File & Playblast (giữ nguyên giao diện cũ)"""
        # 1. Khối Dự Án & File nháp
        shot_group = QtWidgets.QGroupBox()
        shot_layout = QtWidgets.QGridLayout(shot_group)
        shot_layout.setContentsMargins(8, 8, 8, 8)
        shot_layout.setSpacing(8)
        
        # Hàng 0: Header giả lập với nút Refresh ở góc phải
        header_layout = QtWidgets.QHBoxLayout()
        header_label = QtWidgets.QLabel(u"Quản Lý File (Pipeline)")
        header_label.setStyleSheet("font-weight: bold; color: #FF9800; font-size: 12px;")
        header_layout.addWidget(header_label)
        
        self.refresh_btn = QtWidgets.QPushButton(u"🔄 Làm mới")
        self.refresh_btn.setToolTip("Làm mới danh sách file từ Server")
        self.refresh_btn.setFixedWidth(110)
        self.refresh_btn.setFixedHeight(26)
        self.refresh_btn.clicked.connect(self.on_refresh)
        header_layout.addWidget(self.refresh_btn, 0, QtCore.Qt.AlignRight)
        
        shot_layout.addLayout(header_layout, 0, 0, 1, 3)
        
        # Hàng 1: Project
        shot_layout.addWidget(QtWidgets.QLabel("Project:"), 1, 0)
        self.proj_combo = QtWidgets.QComboBox()
        self.proj_combo.currentIndexChanged.connect(self.on_proj_changed)
        shot_layout.addWidget(self.proj_combo, 1, 1, 1, 2)
        
        # Hàng 2: Episode
        shot_layout.addWidget(QtWidgets.QLabel("Episode:"), 2, 0)
        self.ep_combo = QtWidgets.QComboBox()
        self.ep_combo.currentIndexChanged.connect(self.on_ep_changed)
        shot_layout.addWidget(self.ep_combo, 2, 1)
        
        self.create_ep_btn = QtWidgets.QPushButton("➕ Tập")
        self.create_ep_btn.setToolTip("Tạo tập phim mới (Dành cho Leader)")
        self.create_ep_btn.clicked.connect(self.on_create_episode)
        shot_layout.addWidget(self.create_ep_btn, 2, 2)
        
        # Nhãn cảnh báo quy chuẩn tên Episode (Hàng 3)
        self.ep_warning_label = QtWidgets.QLabel("")
        self.ep_warning_label.setStyleSheet("color: #FF9800; font-weight: bold; margin-left: 5px;")
        self.ep_warning_label.setVisible(False)
        shot_layout.addWidget(self.ep_warning_label, 3, 0, 1, 3)
        
        # Hàng 4: Task (Khâu)
        shot_layout.addWidget(QtWidgets.QLabel("Task:"), 4, 0)
        self.task_combo = QtWidgets.QComboBox()
        self.task_combo.addItems(["Layout", "Animation"])
        self.task_combo.currentIndexChanged.connect(self.on_task_changed)
        shot_layout.addWidget(self.task_combo, 4, 1)
        
        self.create_file_btn = QtWidgets.QPushButton("➕ Tạo File")
        self.create_file_btn.setToolTip("Tạo file nháp mới cho Khâu hiện tại")
        self.create_file_btn.clicked.connect(self.on_create_file)
        shot_layout.addWidget(self.create_file_btn, 4, 2)
        
        # Hàng 5: Label Danh sách file & Dropdown tuỳ chọn nạp Reference
        files_label_layout = QtWidgets.QHBoxLayout()
        files_label_layout.addWidget(QtWidgets.QLabel("Working Files (Đúp click để Mở):"))
        
        self.ref_load_combo = QtWidgets.QComboBox()
        self.ref_load_combo.addItems([
            u"⚡ Mở nhanh (Không load Ref)",
            u"👤 Nạp Nhân vật & Camera (Characters & Cameras)",
            u"📋 Tự chọn Ref (Selective Preload)",
            u"🔝 Chỉ nạp Ref cấp 1 (Top Level)",
            u"🔄 Mở bình thường (Nạp tất cả)"
        ])
        self.ref_load_combo.setToolTip(u"Chế độ tải Reference khi mở file Maya.")
        self.ref_load_combo.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.ref_load_combo.setFixedWidth(240)
        self.ref_load_combo.currentIndexChanged.connect(self.save_ref_load_setting)
        files_label_layout.addWidget(self.ref_load_combo, 0, QtCore.Qt.AlignRight)
        
        shot_layout.addLayout(files_label_layout, 5, 0, 1, 3)
        
        # Hàng 6: Bố cục 3 bảng (Shot bên trái, Maya Version ở giữa, Playblast Videos bên phải)
        list_container_layout = QtWidgets.QHBoxLayout()
        list_container_layout.setSpacing(6)
        
        # Bảng bên trái: Shot List
        shot_list_widget = QtWidgets.QWidget()
        shot_list_layout = QtWidgets.QVBoxLayout(shot_list_widget)
        shot_list_layout.setContentsMargins(0, 0, 0, 0)
        shot_list_layout.addWidget(QtWidgets.QLabel(u"🎬 Danh sách Shot:"))
        
        self.shot_list = QtWidgets.QListWidget()
        self.shot_list.itemSelectionChanged.connect(self.on_shot_selection_changed)
        shot_list_layout.addWidget(self.shot_list)
        
        # Bảng ở giữa: Maya File Version List
        version_list_widget = QtWidgets.QWidget()
        version_list_layout = QtWidgets.QVBoxLayout(version_list_widget)
        version_list_layout.setContentsMargins(0, 0, 0, 0)
        version_list_layout.addWidget(QtWidgets.QLabel(u"📂 File Maya (Đúp click mở):"))
        
        self.files_list = QtWidgets.QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_open_file)
        self.files_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.files_list.customContextMenuRequested.connect(self.show_file_list_context_menu)
        self.files_list.itemSelectionChanged.connect(self.update_playblast_count)
        version_list_layout.addWidget(self.files_list)
        
        # Bảng bên phải: Playblast Videos List
        pb_list_widget = QtWidgets.QWidget()
        pb_list_layout = QtWidgets.QVBoxLayout(pb_list_widget)
        pb_list_layout.setContentsMargins(0, 0, 0, 0)
        pb_list_layout.addWidget(QtWidgets.QLabel(u"🎥 Playblasts (Đúp click xem):"))
        
        self.pb_list = QtWidgets.QListWidget()
        self.pb_list.itemDoubleClicked.connect(self.on_open_playblast_file)
        self.pb_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.pb_list.customContextMenuRequested.connect(self.show_pb_list_context_menu)
        pb_list_layout.addWidget(self.pb_list)
        
        list_container_layout.addWidget(shot_list_widget, 3) # Chiếm 30% chiều rộng
        list_container_layout.addWidget(version_list_widget, 4) # Chiếm 40% chiều rộng
        list_container_layout.addWidget(pb_list_widget, 3) # Chiếm 30% chiều rộng
        
        shot_layout.addLayout(list_container_layout, 6, 0, 1, 3)
        
        # Hàng 7: Nút mở nhanh thư mục
        folder_btn_layout = QtWidgets.QHBoxLayout()
        folder_btn_layout.setSpacing(6)
        
        self.open_ep_dir_btn = QtWidgets.QPushButton(u"📂 Tập phim")
        self.open_ep_dir_btn.setToolTip("Mở thư mục gốc của Tập phim trên Server")
        self.open_ep_dir_btn.clicked.connect(self.on_open_ep_dir)
        
        self.open_work_dir_btn = QtWidgets.QPushButton(u"📂 Khâu làm việc")
        self.open_work_dir_btn.setToolTip("Mở thư mục chứa file Maya làm việc của khâu hiện tại")
        self.open_work_dir_btn.clicked.connect(self.on_open_work_dir)
        
        self.open_pub_dir_btn = QtWidgets.QPushButton(u"📂 Xuất bản")
        self.open_pub_dir_btn.setToolTip("Mở thư mục chứa file đã Publish của khâu hiện tại")
        self.open_pub_dir_btn.clicked.connect(self.on_open_pub_dir)
        
        self.open_mov_dir_btn = QtWidgets.QPushButton(u"📂 Playblast")
        self.open_mov_dir_btn.setToolTip("Mở thư mục chứa video Playblast nháp của khâu hiện tại")
        self.open_mov_dir_btn.clicked.connect(self.on_open_mov_dir)
        
        folder_btn_layout.addWidget(self.open_ep_dir_btn)
        folder_btn_layout.addWidget(self.open_work_dir_btn)
        folder_btn_layout.addWidget(self.open_pub_dir_btn)
        folder_btn_layout.addWidget(self.open_mov_dir_btn)
        
        shot_layout.addLayout(folder_btn_layout, 7, 0, 1, 3)
        
        # Hàng 8: Các nút bấm lưu/publish
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.save_version_btn = QtWidgets.QPushButton("Lưu Phiên Bản Mới (+1)")
        self.save_version_btn.setObjectName("accent_btn")
        self.save_version_btn.clicked.connect(self.on_increment_save)
        btn_layout.addWidget(self.save_version_btn)
        
        shot_layout.addLayout(btn_layout, 8, 0, 1, 3)
        
        # Hàng 9: Nút Kiểm tra quy chuẩn
        self.check_naming_btn = QtWidgets.QPushButton("🔍 Kiểm tra quy chuẩn tên File")
        self.check_naming_btn.setToolTip("Quét toàn bộ tập phim và tự động sửa các file đặt tên sai quy chuẩn")
        self.check_naming_btn.clicked.connect(self.on_check_filenames)
        shot_layout.addWidget(self.check_naming_btn, 9, 0, 1, 3)
        
        parent_layout.addWidget(shot_group)
        
        # 2. Khối Playblast
        playblast_group = QtWidgets.QGroupBox("Auto Playblast Nháp")
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
        
        # Thêm cấu hình Camera
        playblast_layout.addWidget(QtWidgets.QLabel("Camera:"), 2, 0)
        self.pb_cam_mode_combo = QtWidgets.QComboBox()
        self.pb_cam_mode_combo.addItems([
            u"Camera hiện hành (Active)", 
            u"Tùy chọn 1 Camera", 
            u"Xuất nhiều Camera (Batch)"
        ])
        self.pb_cam_mode_combo.currentIndexChanged.connect(self.on_pb_cam_mode_changed)
        playblast_layout.addWidget(self.pb_cam_mode_combo, 2, 1)
        
        # Cấu hình chọn 1 camera (Single)
        self.pb_single_cam_widget = QtWidgets.QWidget()
        single_cam_layout = QtWidgets.QHBoxLayout(self.pb_single_cam_widget)
        single_cam_layout.setContentsMargins(0, 0, 0, 0)
        single_cam_layout.setSpacing(6)
        
        self.pb_single_cam_combo = QtWidgets.QComboBox()
        single_cam_layout.addWidget(self.pb_single_cam_combo)
        
        self.pb_refresh_cams_btn = QtWidgets.QPushButton(u"🔄")
        self.pb_refresh_cams_btn.setToolTip(u"Làm mới danh sách camera trong scene")
        self.pb_refresh_cams_btn.setFixedWidth(30)
        self.pb_refresh_cams_btn.setFixedHeight(24)
        self.pb_refresh_cams_btn.clicked.connect(self.refresh_camera_list)
        single_cam_layout.addWidget(self.pb_refresh_cams_btn)
        
        playblast_layout.addWidget(self.pb_single_cam_widget, 3, 0, 1, 2)
        
        # Cấu hình chọn nhiều camera (Multi)
        self.pb_multi_cam_list = QtWidgets.QListWidget()
        self.pb_multi_cam_list.setFixedHeight(100)
        playblast_layout.addWidget(self.pb_multi_cam_list, 4, 0, 1, 2)
        
        # Checkbox Đè lên bản cũ
        self.pb_overwrite_checkbox = QtWidgets.QCheckBox(u"Đè lên bản cũ (Không lưu Old)")
        self.pb_overwrite_checkbox.setToolTip(u"Nếu tích chọn, video mới sẽ ghi đè trực tiếp lên video cũ.\nNếu không tích, bản cũ sẽ được di chuyển vào thư mục Old.")
        self.pb_overwrite_checkbox.setStyleSheet("margin-left: 2px;")
        playblast_layout.addWidget(self.pb_overwrite_checkbox, 5, 0, 1, 2)
        
        # Nhãn hiển thị trạng thái Playblast
        self.pb_count_label = QtWidgets.QLabel(u"Trạng thái Playblast: Chưa kiểm tra")
        self.pb_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 2px;")
        playblast_layout.addWidget(self.pb_count_label, 6, 0, 1, 2)
        
        # Hàng nút: Chạy Playblast và Mở thư mục
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
        
        # Trạng thái ẩn/hiện ban đầu
        self.pb_single_cam_widget.setVisible(False)
        self.pb_multi_cam_list.setVisible(False)
        
        parent_layout.addWidget(playblast_group)
        
        parent_layout.addStretch()

    # --- SỰ KIỆN & LOGIC ---
    
    def is_character_reference(self, ref_path):
        """Kiểm tra xem file reference có phải là nhân vật/rig hoặc camera dựa trên đường dẫn hoặc tên file hay không"""
        if not ref_path:
            return False
            
        # Nếu ref_path là list/tuple do Maya query trả về
        if isinstance(ref_path, (list, tuple)):
            if not ref_path:
                return False
            ref_path = ref_path[0]
            
        path_lower = ref_path.replace("\\", "/").lower()
        filename = os.path.basename(path_lower)
        
        # 0. Nhận diện Camera trước tiên (Ưu tiên nạp kèm với nhân vật)
        camera_keywords = ["cam_rig", "camera_rig", "camera", "shot_cam"]
        if "camera" in filename or filename.startswith("cam_") or any(ck in filename for ck in camera_keywords):
            return True
        
        # 1. BỘ LỌC LOẠI TRỪ (EXCLUDE): Loại bỏ các thư mục và file thuộc về bối cảnh (BG), đạo cụ (Props), map...
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

        # 2. BỘ LỌC CHẤP NHẬN (INCLUDE): Nhận diện thư mục hoặc từ khóa nhân vật
        # 2.1 Kiểm tra đường dẫn thư mục chứa nhân vật
        include_path_keywords = [
            "/character rig/", "/character_rig/", "/character model/", 
            "/character/", "/animal_rig/", "/animal/"
        ]
        for kw in include_path_keywords:
            if kw in path_lower:
                return True
                
        # 2.2 Kiểm tra tên file khớp từ khóa nhân vật
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
        """Lưu chỉ số chế độ tải Reference được chọn vào cấu hình Maya"""
        cmds.optionVar(iv=(self.OPTION_VAR_REF_MODE, index))

    def load_settings(self):
        """Tải cấu hình dự án mặc định và tự động đồng bộ file đang mở"""
        if cmds.optionVar(exists=self.OPTION_VAR_PROJ):
            saved_root = cmds.optionVar(q=self.OPTION_VAR_PROJ)
            if os.path.exists(saved_root):
                self.project_root = saved_root
                
        self.file_manager.project_root = self.project_root
        
        # Nạp cấu hình chế độ tải Reference
        if cmds.optionVar(exists=self.OPTION_VAR_REF_MODE):
            saved_mode = cmds.optionVar(q=self.OPTION_VAR_REF_MODE)
            self.ref_load_combo.setCurrentIndex(saved_mode)
        else:
            self.ref_load_combo.setCurrentIndex(0) # Mặc định mở nhanh

        self.populate_projects()
        
        # Tự động nhận diện và đồng bộ file đang mở trong scene khi khởi động UI
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
        """Kiểm tra xem tên thư mục tập phim hiện tại có đúng quy chuẩn hay không và hiển thị cảnh báo"""
        current_ep = self.ep_combo.currentText()
        if not current_ep:
            self.ep_warning_label.setVisible(False)
            return
            
        current_proj = self.proj_combo.currentText()
        standard_ep = self.file_manager.get_episode_folder_name(current_proj, current_ep)
        if current_ep != standard_ep:
            self.ep_warning_label.setText(u"⚠️ Thư mục không chuẩn! Khuyên dùng: %s" % standard_ep)
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
        
        # Nhớ shot đang chọn trước đó để khôi phục
        previous_selected_shot = ""
        selected_items = self.shot_list.selectedItems()
        if selected_items:
            previous_selected_shot = selected_items[0].text()
            
        # Gom nhóm file theo tên shot
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
            
        # Nạp tên shot lên bảng bên trái
        sorted_shots = sorted(self.shot_map.keys())
        for shot in sorted_shots:
            item = QtWidgets.QListWidgetItem(shot)
            self.shot_list.addItem(item)
            
        # Khôi phục lựa chọn
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
        
        # Sắp xếp version từ cao xuống thấp (mới nhất lên trên)
        sorted_files = sorted(shot_files, key=lambda x: x["version"], reverse=True)
        
        for info in sorted_files:
            item_text = "[v%02d] %s  (%s | %s)" % (
                info["version"], 
                info["filename"], 
                info["time"], 
                info["size"]
            )
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, info["filepath"])
            self.files_list.addItem(item)
            
        self.update_playblast_count()

    def on_open_file(self, item):
        """Mở file được chọn sau khi xác nhận cảnh báo an toàn"""
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        if cmds.file(query=True, modified=True):
            res = QtWidgets.QMessageBox.question(
                self, u"Xác nhận mở file",
                u"Cảnh hiện tại có thay đổi chưa lưu. Bạn có chắc muốn mở file mới?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
        try:
            kwargs = {"open": True, "force": True}
            mode = self.ref_load_combo.currentIndex()
            
            if mode == 0:  # Mở nhanh (Không load Ref)
                kwargs["loadReferenceDepth"] = "none"
            elif mode in [1, 2]:  # Chọn nạp nhân vật hoặc Tự chọn đều dùng trì hoãn nạp settings
                kwargs["buildLoadSettings"] = True
            elif mode == 3:  # Chỉ nạp Ref cấp 1
                kwargs["loadReferenceDepth"] = "topOnly"
            # mode == 4 là Mở bình thường (nạp tất cả)
            
            # Gán optionVar của Maya để Preload Reference Editor mở đúng file hiện tại
            normalized_path = os.path.normpath(filepath).replace("\\", "/")
            cmds.optionVar(stringValue=("preloadRefEdTopLevelFile", normalized_path))
                
            cmds.file(to_sys_path(filepath), **kwargs)
            
            if mode == 1:
                # Quét và tích chọn sẵn các Rig nhân vật & camera trong cấu hình tải
                print(u"Đang quét các Reference để tích chọn sẵn nhân vật & camera...")
                num_settings = cmds.selLoadSettings(q=True, numSettings=True) or 0
                char_count = 0
                
                for i in range(1, num_settings):
                    ref_path_raw = cmds.selLoadSettings(str(i), q=True, fileName=True)
                    ref_path = ref_path_raw[0] if isinstance(ref_path_raw, (list, tuple)) and ref_path_raw else ref_path_raw
                    
                    if self.is_character_reference(ref_path):
                        cmds.selLoadSettings(str(i), edit=True, deferReference=0)  # Tích chọn (Load)
                        char_count += 1
                        print(u"-> Đã tích chọn Rig/Camera: %s" % os.path.basename(ref_path))
                    else:
                        cmds.selLoadSettings(str(i), edit=True, deferReference=1)  # Bỏ chọn (Defer)
                        
                print(u"Đã chuẩn bị xong cấu hình nạp. Tự động tích chọn %d nhân vật & camera." % char_count)
                
                # Hiển thị bảng Preload Reference Editor của Maya để user xem và nhấn nạp
                import maya.mel as mel
                mel.eval("PreloadReferenceEditor;")
                
            elif mode == 2:
                # Hiển thị cửa sổ Preload Reference Editor gốc của Maya để người dùng chọn
                import maya.mel as mel
                mel.eval("PreloadReferenceEditor;")
                
            cmds.workspace(to_sys_path(self.project_root), openWorkspace=True)
            print(u"Đã mở file thành công: %s" % filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể mở file: %s" % exception_to_unicode(e))

    def on_create_episode(self):
        """Tạo tập phim mới (Dành cho Leader)"""
        current_proj = self.proj_combo.currentText()
        if not current_proj:
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn Dự án trước.")
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
                    self, u"Thành công", 
                    u"Đã tạo cấu trúc tập phim mới thành công trên Server:\n%s" % ep_folder_name
                )

    def on_create_file(self):
        """Tạo file nháp mới trực tiếp trong WorkingFile/[Task]/"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not current_proj or not current_ep or not current_task:
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn đầy đủ Dự án và Tập phim.")
            return
            
        if current_task == "Layout":
            # Gợi ý nhập dải shot
            text, ok = QtWidgets.QInputDialog.getText(
                self, u"Tạo File Layout mới", 
                u"Nhập dải Shot cho Layout (ví dụ: 01-30 hoặc 30-60):"
            )
        else:
            # Nhập số shot đơn
            text, ok = QtWidgets.QInputDialog.getText(
                self, u"Tạo File Animation mới", 
                u"Nhập số Shot cho Animation (ví dụ: 01 hoặc 02):"
            )
            
        if not (ok and text.strip()):
            return
            
        shot_range_or_num = text.strip()
        filepath = self.file_manager.create_new_work_file(current_proj, current_ep, current_task, shot_range_or_num)
        if filepath:
            self.refresh_files_list()
            QtWidgets.QMessageBox.information(
                self, u"Thành công", 
                u"Đã khởi tạo file nháp mới thành công trên Server:\n%s" % os.path.basename(filepath)
            )

    def on_increment_save(self):
        """Lưu phiên bản mới (+1)"""
        current_task = self.task_combo.currentText()
        new_filepath = self.file_manager.increment_save(current_task)
        if new_filepath:
            self.refresh_files_list()
            self.refresh_dropdowns_to_match_current(new_filepath)

    def refresh_dropdowns_to_match_current(self, filepath):
        """Tự động đồng bộ dropdown UI khớp với file đang mở"""
        if not filepath or not self.project_root:
            return
            
        # Chuẩn hóa đường dẫn dạng Windows/Linux không phân biệt hoa thường
        norm_filepath = os.path.normpath(filepath)
        norm_root = os.path.normpath(self.project_root)
        
        # So sánh không phân biệt hoa thường (tránh lỗi viết hoa ổ đĩa trên Windows)
        if not norm_filepath.lower().startswith(norm_root.lower()):
            return
            
        # Tính toán đường dẫn tương đối từ project_root chuẩn hóa
        rel_path = norm_filepath[len(norm_root):].lstrip(os.sep)
        parts = rel_path.split(os.sep)
        
        # Cấu trúc phẳng: [Project]/[Episode]/WorkingFile/[Task]/File.ma
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
            
            # Phân tích file hiện tại thuộc Shot nào để tự động select Shot đó trên bảng bên trái
            current_filename = os.path.basename(norm_filepath)
            current_parsed = self.file_manager.parse_scene_name(current_filename)
            if current_parsed:
                current_prefix = current_parsed[0]
            else:
                parts = current_filename.split("_v")
                current_prefix = parts[0] if len(parts) > 1 else os.path.splitext(current_filename)[0]
                
            # Chọn shot trên shot_list
            shot_items = self.shot_list.findItems(current_prefix, QtCore.Qt.MatchExactly)
            if shot_items:
                self.shot_list.blockSignals(True)
                self.shot_list.setCurrentItem(shot_items[0])
                self.shot_list.blockSignals(False)
                self.on_shot_selection_changed()
                
            # Tự động chọn (highlight) file hiện tại trong QListWidget bên phải
            for i in range(self.files_list.count()):
                item = self.files_list.item(i)
                item_path = item.data(QtCore.Qt.UserRole)
                if item_path and os.path.normpath(item_path).lower() == norm_filepath.lower():
                    self.files_list.setCurrentItem(item)
                    break

    def update_playblast_count(self):
        """Kiểm tra và hiển thị danh sách video Playblast nháp hiện có cho file Maya đang chọn"""
        self.pb_list.clear()
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            current_filepath = cmds.file(q=True, sceneName=True)
            if current_filepath:
                filepath = current_filepath
                filename = os.path.basename(current_filepath)
            else:
                self.pb_count_label.setText(u"Trạng thái Playblast: Không có file hoạt động")
                self.pb_count_label.setStyleSheet("color: gray; font-weight: bold; margin-left: 2px;")
                self.pb_count_label.setToolTip("")
                return
        else:
            filepath = selected_items[0].data(QtCore.Qt.UserRole)
            filename = os.path.basename(filepath)
            
        filename_no_ext, _ = os.path.splitext(filename)
        
        # Gọi playblast_manager để lấy đúng thư mục playblast nháp của file này
        playblast_dir, _ = self.playblast_manager.get_playblast_path(scene_filepath=filepath)
        if not playblast_dir:
            self.pb_count_label.setText(u"Trạng thái Playblast: Chưa kiểm tra")
            self.pb_count_label.setStyleSheet("color: gray; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip("")
            return
            
        # 1. Tìm toàn bộ video trong thư mục chính bắt đầu bằng filename_no_ext
        found_active_videos = []
        try:
            if os.path.exists(playblast_dir):
                for f in os.listdir(playblast_dir):
                    if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                        found_active_videos.append((f, os.path.join(playblast_dir, f)))
        except Exception:
            pass
            
        # Sắp xếp các video active theo bảng chữ cái
        found_active_videos = sorted(found_active_videos, key=lambda x: x[0])
                
        # 2. Tìm các video phiên bản cũ trong thư mục Old
        found_old_videos = []
        old_dir = os.path.join(playblast_dir, "Old")
        if os.path.exists(old_dir) and os.path.isdir(old_dir):
            try:
                for f in os.listdir(old_dir):
                    if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                        found_old_videos.append((f, os.path.join(old_dir, f)))
            except Exception:
                pass
                
        # Sắp xếp các video cũ theo bảng chữ cái/số version tăng dần
        found_old_videos = sorted(found_old_videos, key=lambda x: x[0])
        
        # 3. Nạp dữ liệu lên self.pb_list
        if found_active_videos:
            for name, path in found_active_videos:
                item = QtWidgets.QListWidgetItem(u"🟢 [Active] " + name)
                item.setData(QtCore.Qt.UserRole, path)
                item.setForeground(QtGui.QColor("#4CAF50")) # Chữ xanh lá
                self.pb_list.addItem(item)
            
            # Cập nhật nhãn trạng thái lấy file video đầu tiên tìm được
            first_name = found_active_videos[0][0]
            self.pb_count_label.setText(u"🎬 Đã có Playblast (%s)" % first_name)
            self.pb_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip(os.path.normpath(found_active_videos[0][1]))
        else:
            self.pb_count_label.setText(u"❌ Chưa có Playblast")
            self.pb_count_label.setStyleSheet("color: #F44336; font-weight: bold; margin-left: 2px;")
            self.pb_count_label.setToolTip("")
            
        for name, path in found_old_videos:
            item = QtWidgets.QListWidgetItem(u"⚪ [Old] " + name)
            item.setData(QtCore.Qt.UserRole, path)
            item.setForeground(QtGui.QColor("#9E9E9E")) # Chữ xám nhạt
            self.pb_list.addItem(item)

    def on_open_playblast_file(self, item):
        """Mở file video playblast bằng trình phát mặc định của hệ thống"""
        import os
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        try:
            os.startfile(os.path.normpath(filepath))
            print(u"Đã mở video playblast bằng trình phát mặc định: %s" % filepath)
        except Exception as e:
            cmds.warning(u"Không thể mở video playblast: %s" % str(e))

    def get_scene_cameras(self):
        """Lấy danh sách các camera transform trong scene, lọc camera mặc định và xếp camera custom lên trước"""
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
        """Làm mới danh sách camera trên giao diện"""
        cams = self.get_scene_cameras()
        
        # Cập nhật single combo
        self.pb_single_cam_combo.blockSignals(True)
        self.pb_single_cam_combo.clear()
        self.pb_single_cam_combo.addItems(cams)
        self.pb_single_cam_combo.blockSignals(False)
        
        # Cập nhật multi check list
        self.pb_multi_cam_list.clear()
        for cam in cams:
            item = QtWidgets.QListWidgetItem(cam)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.pb_multi_cam_list.addItem(item)

    def on_pb_cam_mode_changed(self, index):
        """Thay đổi chế độ camera hiển thị trên giao diện"""
        mode = self.pb_cam_mode_combo.currentText()
        if mode == u"Tùy chọn 1 Camera":
            self.pb_single_cam_widget.setVisible(True)
            self.pb_multi_cam_list.setVisible(False)
            self.refresh_camera_list()
        elif mode == u"Xuất nhiều Camera (Batch)":
            self.pb_single_cam_widget.setVisible(False)
            self.pb_multi_cam_list.setVisible(True)
            self.refresh_camera_list()
        else: # Camera hiện hành (Active)
            self.pb_single_cam_widget.setVisible(False)
            self.pb_multi_cam_list.setVisible(False)

    def on_run_playblast(self):
        """Chạy playblast nháp hàng ngày"""
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
            if cam_mode == u"Camera hiện hành (Active)":
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
                    
            elif cam_mode == u"Tùy chọn 1 Camera":
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
                    
            elif cam_mode == u"Xuất nhiều Camera (Batch)":
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
                
                # Hiển thị báo cáo kết quả
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
        """Xuất bản file sạch và tự động chạy playblast chính thức kèm theo"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn đầy đủ thông tin để Publish.")
            return
            
        res = QtWidgets.QMessageBox.question(
            self, u"Xác nhận Publish",
            u"Bạn có chắc chắn muốn Publish file hiện tại cho khâu %s không?\nHành động này sẽ dọn dẹp file và xuất playblast chính thức." % current_task,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        pub_filepath = self.file_manager.publish_file(current_proj, current_ep, current_task)
        if not pub_filepath:
            QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể Publish file Maya. Vui lòng kiểm tra log.")
            return
            
        pub_video_path = os.path.splitext(pub_filepath)[0] + ".mov"
        current_filepath = cmds.file(q=True, sceneName=True)
        
        try:
            cmds.file(to_sys_path(pub_filepath), open=True, force=True)
            print(u"Đang chạy Playblast chính thức cho file Publish...")
            self.playblast_manager.run_playblast(
                format_ext="qt",
                percent=100,
                width=1920,
                height=1080,
                custom_path=pub_video_path
            )
        except Exception as e:
            print(u"Lỗi khi chạy Playblast Publish: %s" % exception_to_unicode(e))
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(to_sys_path(current_filepath), open=True, force=True)
                
        QtWidgets.QMessageBox.information(
            self, u"Publish Thành Công",
            u"Đã xuất bản sạch sẽ file Maya và video Playblast lên Server:\n\nFile: %s\nVideo: %s" % (
                os.path.basename(pub_filepath), 
                os.path.basename(pub_video_path)
            )
        )
        self.refresh_files_list()

    def on_check_filenames(self):
        """Quét tìm file sai quy chuẩn thực tế trong tập phim, hỏi ý kiến user để tự động sửa toàn bộ"""
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        
        if not (current_proj and current_ep):
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn đầy đủ Dự án và Tập phim trước.")
            return

        # 1. Kiểm tra quy chuẩn của thư mục Episode trước
        standard_ep = self.file_manager.get_episode_folder_name(current_proj, current_ep)
        if current_ep != standard_ep:
            msg = (
                u"Thư mục tập phim hiện tại chưa đúng quy chuẩn:\n"
                u"  - Hiện tại: %s\n"
                u"  - Đúng chuẩn: %s\n\n"
                u"Bạn có muốn đổi tên thư mục này trên Server về đúng quy chuẩn không?\n"
                u"(Lưu ý: Chỉ thực hiện khi không có ai đang mở hoặc khóa file trong thư mục này)."
            ) % (current_ep, standard_ep)
            
            res = QtWidgets.QMessageBox.question(
                self, u"Chuẩn hóa tên thư mục Tập phim",
                msg,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
            )
            
            if res == QtWidgets.QMessageBox.Cancel:
                return
            elif res == QtWidgets.QMessageBox.Yes:
                success = self.file_manager.rename_episode_folder(current_proj, current_ep, standard_ep)
                if success:
                    # Cập nhật lại dropdown Episode
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
                        self, u"Thành công",
                        u"Đã đổi tên thư mục tập phim thành: %s" % standard_ep
                    )
                else:
                    QtWidgets.QMessageBox.critical(
                        self, u"Lỗi",
                        u"Không thể đổi tên thư mục tập phim. Thư mục hoặc file bên trong có thể đang bị khóa bởi Windows Explorer hoặc tiến trình khác."
                    )
                    # Hỏi xem có tiếp tục kiểm tra file bên trong thư mục cũ không
                    cont_res = QtWidgets.QMessageBox.question(
                        self, u"Tiếp tục kiểm tra?",
                        u"Bạn có muốn tiếp tục quét và chuẩn hóa các file bên trong thư mục hiện tại (%s) không?" % current_ep,
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    if cont_res == QtWidgets.QMessageBox.No:
                        return

        # 2. Quét tìm file sai quy chuẩn thực tế trong tập phim
        incorrect_files = self.file_manager.check_episode_filenames_naming(current_proj, current_ep)
        
        if not incorrect_files:
            QtWidgets.QMessageBox.information(
                self, u"Kết quả kiểm tra", 
                u"Tuyệt vời! Toàn bộ file làm việc trong tập phim đều đúng quy chuẩn!"
            )
            return
            
        def to_unicode(s):
            if isinstance(s, str):
                try:
                    return s.decode("utf-8")
                except:
                    return unicode(s)
            return s
            
        msg = u"Phát hiện %d file đặt tên sai quy chuẩn. Ví dụ:\n\n" % len(incorrect_files)
        for i, f_info in enumerate(incorrect_files[:5]):
            old_f = to_unicode(f_info["old_filename"])
            new_f = to_unicode(f_info["new_filename"])
            task_d = to_unicode(f_info["task_dir"])
            msg += u"  - [%s] %s -> %s\n" % (task_d, old_f, new_f)
        if len(incorrect_files) > 5:
            msg += u"  - và %d file khác...\n" % (len(incorrect_files) - 5)
        msg += u"\nBạn có muốn đổi tên toàn bộ các file này về đúng quy chuẩn không?"
        
        res = QtWidgets.QMessageBox.question(
            self, u"Xác nhận chuẩn hóa tên file làm việc",
            msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if res == QtWidgets.QMessageBox.Yes:
            success = self.file_manager.rename_work_files(incorrect_files)
            if success:
                self.refresh_files_list()
                QtWidgets.QMessageBox.information(
                    self, u"Thành công", 
                    u"Đã hoàn thành chuẩn hóa tên các file làm việc!"
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self, u"Lỗi chuẩn hoá", 
                    u"Có lỗi xảy ra trong quá trình đổi tên!\n\n"
                    u"Nguyên nhân phổ biến: File cần đổi tên đang bị khóa (có thể đang mở trong phần mềm khác).\n\n"
                    u"Vui lòng đóng các file liên quan và thử lại!"
                )

    def on_refresh(self):
        """Làm mới toàn bộ danh sách dự án, tập phim và file từ Server"""
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
        
        # Tự động nhận diện và đồng bộ file đang mở sau khi làm mới
        current_filepath = cmds.file(q=True, sceneName=True)
        if current_filepath:
            self.refresh_dropdowns_to_match_current(current_filepath)
        print("Da lam moi danh sach tu Server.")

    def open_folder_explorer(self, folder_path):
        """Mở thư mục trong Windows Explorer"""
        if not folder_path or not os.path.exists(folder_path):
            cmds.warning(u"Thư mục không tồn tại: %s" % folder_path)
            return
        try:
            # Chuẩn hóa đường dẫn dạng Windows
            folder_path = os.path.normpath(folder_path)
            os.startfile(to_sys_path(folder_path))
        except Exception as e:
            cmds.warning(u"Không thể mở thư mục: %s" % exception_to_unicode(e))

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
        
        # Nếu là Layout, Published có thư mục con của từng shot
        # Tìm shot đang chọn để mở đúng thư mục published của shot đó
        selected_items = self.shot_list.selectedItems() if hasattr(self, 'shot_list') else []
        if selected_items and task_dir_name == "Layout":
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
        
        action_open_folder = menu.addAction(u"Mở thư mục chứa file")
        action_copy_path = menu.addAction(u"Sao chép đường dẫn file")
        action_debug_open = menu.addAction(u"Mở và Debug hiệu năng (Đo thời gian tải)")
        menu.addSeparator()
        
        # Thêm action Publish file này offline
        action_publish = menu.addAction(u"🚀 Publish File này (Copy nhanh)")
        
        # Tìm video playblast nháp tương ứng (quét động theo shot cho cả Layout)
        filename = os.path.basename(filepath)
        filename_no_ext = os.path.splitext(filename)[0]
        
        # Gọi playblast_manager để lấy đúng thư mục playblast nháp của file này
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
            action_open_video = menu.addAction(u"Xem video Playblast nháp")
            
        # Thực thi menu
        action = menu.exec_(self.files_list.mapToGlobal(pos))
        
        if action == action_open_folder:
            self.open_folder_explorer(os.path.dirname(filepath))
        elif action == action_copy_path:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(os.path.normpath(filepath))
            print("Đã sao chép đường dẫn file vào Clipboard: %s" % filepath)
        elif action == action_publish:
            self.on_publish_file_offline(filepath)
        elif action == action_debug_open:
            res = QtWidgets.QMessageBox.question(
                self, u"Xác nhận Debug mở file",
                u"Hành động này sẽ mở file cảnh và tải từng Reference một để đo lường chi tiết.\n"
                u"Bạn có chắc muốn tiến hành không?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
            progress = QtWidgets.QProgressDialog(u"Đang đo lường hiệu năng mở file...", u"Hủy", 0, 100, self)
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.setAutoClose(True)
            progress.setValue(10)
            QtCore.QCoreApplication.processEvents()
            
            try:
                report = self.file_manager.debug_open_file(filepath)
                progress.setValue(100)
                
                # Hiển thị báo cáo kết quả
                self.show_debug_report_dialog(filepath, report)
            except Exception as e:
                progress.close()
                QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Lỗi khi debug mở file: %s" % exception_to_unicode(e))
        elif action_open_video and action == action_open_video:
            try:
                os.startfile(to_sys_path(os.path.normpath(active_video_path)))
            except Exception as e:
                cmds.warning(u"Không thể mở video Playblast: %s" % exception_to_unicode(e))

    def show_debug_report_dialog(self, filepath, report):
        dialog = DebugReportDialog(filepath, report, parent=self)
        dialog.exec_()

    def on_publish_file_offline(self, filepath):
        """Publish nhanh file Maya và video playblast nháp tương ứng bằng cách copy offline (tốc độ dưới 1 giây)"""
        if not filepath or not os.path.exists(filepath):
            return
            
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn đầy đủ Dự án và Tập phim.")
            return
            
        filename = os.path.basename(filepath)
        parsed = self.file_manager.parse_scene_name(filename)
        if not parsed:
            QtWidgets.QMessageBox.warning(self, u"Lỗi tên file", u"Tên file không đúng quy chuẩn, không thể Publish.")
            return
            
        prefix, file_task, ver, padding, ext = parsed
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        # Xác định thư mục published
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
        
        # Tiến hành copy file Maya
        import shutil
        try:
            shutil.copy2(filepath, published_filepath)
            print(u"[PUBLISH OFFLINE] Đã copy file Maya sang Published: %s" % published_filepath)
            
            # Thông báo thành công
            msg = u"Đã xuất bản (Publish) thành công thành file sạch trên server!\n\n"
            msg += u"📁 File Maya: %s\n\n" % os.path.basename(published_filepath)
            msg += u"💡 Gợi ý: Nhấp chuột phải vào video ở cột thứ 3 và chọn 'Publish Video này' nếu bạn muốn đẩy video playblast tương ứng lên server.\n"
                
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
            QtWidgets.QMessageBox.critical(self, u"Lỗi Publish", u"Không thể copy file lên server:\n%s" % str(e))

    def show_pb_list_context_menu(self, pos):
        item = self.pb_list.itemAt(pos)
        if not item:
            return
            
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        menu = QtWidgets.QMenu(self)
        
        action_open_video = menu.addAction(u"Xem video Playblast")
        action_open_folder = menu.addAction(u"Mở thư mục chứa video")
        menu.addSeparator()
        action_publish_video = menu.addAction(u"🚀 Publish Video này")
        
        action = menu.exec_(self.pb_list.mapToGlobal(pos))
        if action == action_open_video:
            self.on_open_playblast_file(item)
        elif action == action_open_folder:
            self.open_folder_explorer(os.path.dirname(filepath))
        elif action == action_publish_video:
            self.on_publish_video_offline(filepath)

    def on_publish_video_offline(self, filepath):
        """Publish nhanh video playblast được chọn lên server Published (offline copy)"""
        if not filepath or not os.path.exists(filepath):
            return
            
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn đầy đủ Dự án và Tập phim.")
            return
            
        # Lấy định danh của file Maya đang chọn ở cột 2
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            current_filepath = cmds.file(q=True, sceneName=True)
            if not current_filepath:
                QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Vui lòng chọn file Maya tương ứng ở cột 2 để xác định tên Publish.")
                return
            maya_filename = os.path.basename(current_filepath)
        else:
            maya_filename = os.path.basename(selected_items[0].data(QtCore.Qt.UserRole))
            
        parsed = self.file_manager.parse_scene_name(maya_filename)
        if not parsed:
            QtWidgets.QMessageBox.warning(self, u"Lỗi tên file", u"Tên file Maya không hợp lệ, không thể xác định tên Publish.")
            return
            
        prefix, file_task, ver, padding, ext = parsed
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        task_short = "Lay" if task_dir_name == "Layout" else "Anim"
        
        # Xác định thư mục published video
        published_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name)
        if task_short == "Lay":
            published_dir = os.path.join(published_dir, prefix)
            
        dest_mov_dir = os.path.join(published_dir, "mov")
        if not os.path.exists(dest_mov_dir):
            try:
                os.makedirs(dest_mov_dir)
            except Exception:
                pass
                
        # Lấy đuôi file video nguồn (.mov hoặc .avi)
        mov_ext = os.path.splitext(filepath)[1]
        dest_mov_filename = "%s_%s_pub%s" % (prefix, task_short, mov_ext)
        dest_mov_path = os.path.normpath(os.path.join(dest_mov_dir, dest_mov_filename))
        
        # Thực hiện copy offline
        import shutil
        try:
            shutil.copy2(filepath, dest_mov_path)
            print(u"[PUBLISH VIDEO] Đã copy video playblast sang Published: %s" % dest_mov_path)
            
            res = cmds.confirmDialog(
                title="Publish Video Success",
                message=u"Đã xuất bản (Publish) video playblast thành công lên server!\n\n"
                        u"🎬 Video: %s" % os.path.basename(dest_mov_path),
                button=["OK", "Open Published Folder"],
                defaultButton="OK",
                cancelButton="OK"
            )
            if res == "Open Published Folder":
                self.open_folder_explorer(published_dir)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Lỗi Publish", u"Không thể copy video lên server:\n%s" % str(e))

    # ================================================================
    # TAB 2: Tách / Gộp Cảnh (Split & Merge)
    # ================================================================

    def _build_tab2_split_merge(self, parent_layout):
        """Xây dựng nội dung Tab 2 - Tách / Gộp Cảnh (Đã căn chỉnh UI thẳng hàng dọc chuyên nghiệp)"""
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

        # ---- KHU VỰC 1: Tách Shot Layout Tổng ----
        split_group = QtWidgets.QGroupBox(u"Tách Shot Layout Tổng (Split)")
        split_group_layout = QtWidgets.QVBoxLayout(split_group)
        split_group_layout.setContentsMargins(12, 16, 12, 12)
        split_group_layout.setSpacing(10)

        # Hàng 1: Nút Quét Bookmarks từ Scene hiện tại
        self.sm_scan_btn = QtWidgets.QPushButton(u"🔍 Quét Bookmarks từ Scene hiện tại")
        self.sm_scan_btn.setToolTip(u"Quét toàn bộ các timeSliderBookmark đánh số từ scene Maya đang mở")
        self.sm_scan_btn.clicked.connect(self.on_scan_bookmarks)
        split_group_layout.addWidget(self.sm_scan_btn)

        # Hàng 2: Danh sách bookmark
        list_label_row = QtWidgets.QHBoxLayout()
        lbl_list = QtWidgets.QLabel(u"Bookmarks tìm thấy:")
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

        # Hàng 3: Lọc khoảng shot
        filter_row = QtWidgets.QHBoxLayout()
        lbl_filter = QtWidgets.QLabel(u"Lọc khoảng shot (tuỳ chọn):")
        lbl_filter.setFixedWidth(LABEL_WIDTH)
        filter_row.addWidget(lbl_filter)

        self.sm_split_start = QtWidgets.QSpinBox()
        self.sm_split_start.setRange(0, 999)
        self.sm_split_start.setValue(0)
        self.sm_split_start.setToolTip(u"Bắt đầu từ shot số (0 = không lọc)")
        self.sm_split_start.setFixedWidth(80)

        self.sm_split_end = QtWidgets.QSpinBox()
        self.sm_split_end.setRange(0, 999)
        self.sm_split_end.setValue(0)
        self.sm_split_end.setToolTip(u"Đến shot số (0 = không lọc)")
        self.sm_split_end.setFixedWidth(80)

        filter_row.addWidget(QtWidgets.QLabel(u"Từ:"))
        filter_row.addWidget(self.sm_split_start)
        filter_row.addWidget(QtWidgets.QLabel(u" Đến:"))
        filter_row.addWidget(self.sm_split_end)
        filter_row.addStretch()
        split_group_layout.addLayout(filter_row)

        # Hàng 4: Frame Padding
        padding_row = QtWidgets.QHBoxLayout()
        lbl_padding = QtWidgets.QLabel(u"Frame đệm (Padding):")
        lbl_padding.setFixedWidth(LABEL_WIDTH)
        padding_row.addWidget(lbl_padding)

        self.sm_padding_spin = QtWidgets.QSpinBox()
        self.sm_padding_spin.setRange(0, 50)
        self.sm_padding_spin.setValue(5)
        self.sm_padding_spin.setFixedWidth(80)
        self.sm_padding_spin.setToolTip(u"Số frame mở rộng trước/sau bookmark khi cắt key")
        padding_row.addWidget(self.sm_padding_spin)
        padding_row.addStretch()
        split_group_layout.addLayout(padding_row)





        # Hàng 7: Nút Bắt đầu Tách
        btn_row = QtWidgets.QHBoxLayout()
        lbl_btn_spacer = QtWidgets.QWidget()
        lbl_btn_spacer.setFixedWidth(LABEL_WIDTH)
        btn_row.addWidget(lbl_btn_spacer)

        self.sm_split_btn = QtWidgets.QPushButton(u"🚀 Bắt đầu Tách Shot vào Pipeline")
        self.sm_split_btn.setObjectName("accent_btn")
        self.sm_split_btn.clicked.connect(self.on_split_layout)
        btn_row.addWidget(self.sm_split_btn)
        split_group_layout.addLayout(btn_row)

        scroll_layout.addWidget(split_group)

        # ---- KHU VỰC 2: Gộp Animation Cảnh Tổng ----
        combine_group = QtWidgets.QGroupBox(u"Gộp Animation Cảnh Tổng (Combine)")
        combine_group_layout = QtWidgets.QVBoxLayout(combine_group)
        combine_group_layout.setContentsMargins(12, 16, 12, 12)
        combine_group_layout.setSpacing(10)

        # Hàng 0: Khoảng shot cần gộp
        c_range_row = QtWidgets.QHBoxLayout()
        lbl_crange = QtWidgets.QLabel(u"Khoảng shot cần gộp:")
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

        c_range_row.addWidget(QtWidgets.QLabel(u"Từ:"))
        c_range_row.addWidget(self.sm_combine_start)
        c_range_row.addWidget(QtWidgets.QLabel(u" Đến:"))
        c_range_row.addWidget(self.sm_combine_end)
        c_range_row.addStretch()
        combine_group_layout.addLayout(c_range_row)

        # Hàng 1: Checkbox Bake Constraints
        c_bake_row = QtWidgets.QHBoxLayout()
        lbl_cbake_spacer = QtWidgets.QWidget()
        lbl_cbake_spacer.setFixedWidth(LABEL_WIDTH)
        c_bake_row.addWidget(lbl_cbake_spacer)

        self.sm_bake_constraints_cb = QtWidgets.QCheckBox(u"Tự động Bake Constraints (Locator/Rig)")
        self.sm_bake_constraints_cb.setChecked(True)
        c_bake_row.addWidget(self.sm_bake_constraints_cb)
        c_bake_row.addStretch()
        combine_group_layout.addLayout(c_bake_row)

        # Hàng 2: Checkbox Smart Bake
        c_sbake_row = QtWidgets.QHBoxLayout()
        lbl_csbake_spacer = QtWidgets.QWidget()
        lbl_csbake_spacer.setFixedWidth(LABEL_WIDTH)
        c_sbake_row.addWidget(lbl_csbake_spacer)

        self.sm_smart_bake_cb = QtWidgets.QCheckBox(u"Smart Bake (Bake thưa giữ key cực trị)")
        self.sm_smart_bake_cb.setChecked(True)
        c_sbake_row.addWidget(self.sm_smart_bake_cb)
        c_sbake_row.addStretch()
        combine_group_layout.addLayout(c_sbake_row)

        # Hàng 3: Key Reducer Threshold
        threshold_row = QtWidgets.QHBoxLayout()
        lbl_threshold = QtWidgets.QLabel(u"Key Reducer Threshold:")
        lbl_threshold.setFixedWidth(LABEL_WIDTH)
        threshold_row.addWidget(lbl_threshold)

        self.sm_threshold_spin = QtWidgets.QDoubleSpinBox()
        self.sm_threshold_spin.setRange(0.01, 5.0)
        self.sm_threshold_spin.setValue(0.1)
        self.sm_threshold_spin.setSingleStep(0.05)
        self.sm_threshold_spin.setFixedWidth(80)
        self.sm_threshold_spin.setToolTip(u"Ngưỡng cho bộ lọc keyReducer (nhỏ hơn = giữ nhiều key hơn)")
        threshold_row.addWidget(self.sm_threshold_spin)
        threshold_row.addStretch()
        combine_group_layout.addLayout(threshold_row)

        # Hàng 4: Frame Padding cho gộp
        c_padding_row = QtWidgets.QHBoxLayout()
        lbl_cpadding = QtWidgets.QLabel(u"Frame đệm khi xuất/nhập:")
        lbl_cpadding.setFixedWidth(LABEL_WIDTH)
        c_padding_row.addWidget(lbl_cpadding)

        self.sm_combine_padding_spin = QtWidgets.QSpinBox()
        self.sm_combine_padding_spin.setRange(0, 50)
        self.sm_combine_padding_spin.setValue(5)
        self.sm_combine_padding_spin.setFixedWidth(80)
        c_padding_row.addWidget(self.sm_combine_padding_spin)
        c_padding_row.addStretch()
        combine_group_layout.addLayout(c_padding_row)

        # Hàng 5: Nút Gộp Cảnh
        c_btn_row = QtWidgets.QHBoxLayout()
        lbl_cbtn_spacer = QtWidgets.QWidget()
        lbl_cbtn_spacer.setFixedWidth(LABEL_WIDTH)
        c_btn_row.addWidget(lbl_cbtn_spacer)

        self.sm_combine_btn = QtWidgets.QPushButton(u"📦 Tiến hành Gộp Cảnh & Xuất File Cụm")
        self.sm_combine_btn.setObjectName("accent_btn")
        self.sm_combine_btn.clicked.connect(self.on_combine_shots)
        c_btn_row.addWidget(self.sm_combine_btn)
        combine_group_layout.addLayout(c_btn_row)

        scroll_layout.addWidget(combine_group)

        # ---- KHU VỰC 3: Tiện ích ----
        util_group = QtWidgets.QGroupBox(u"Tiện ích")
        util_layout = QtWidgets.QHBoxLayout(util_group)
        util_layout.setContentsMargins(8, 12, 8, 8)
        util_layout.setSpacing(8)

        self.sm_open_stlib_btn = QtWidgets.QPushButton(u"📖 Mở Studio Library UI")
        self.sm_open_stlib_btn.clicked.connect(self.on_open_studio_library)
        util_layout.addWidget(self.sm_open_stlib_btn)

        self.sm_export_csv_btn = QtWidgets.QPushButton(u"📄 Xuất Bookmarks ra CSV")
        self.sm_export_csv_btn.clicked.connect(self.on_export_bookmarks_csv)
        util_layout.addWidget(self.sm_export_csv_btn)

        scroll_layout.addWidget(util_group)
        scroll_layout.addStretch()

    # ================================================================
    # SỰ KIỆN & LOGIC - Tab 2: Tách / Gộp Cảnh
    # ================================================================



    def on_scan_bookmarks(self):
        """Quét toàn bộ timeSliderBookmark dạng số từ scene hiện tại"""
        self.sm_bookmark_list.clear()

        # Đảm bảo plugin timeSliderBookmark được nạp
        if not cmds.pluginInfo('timeSliderBookmark', q=True, loaded=True):
            try:
                cmds.loadPlugin('timeSliderBookmark')
            except Exception:
                QtWidgets.QMessageBox.warning(self, u"Lỗi", u"Không thể nạp plugin timeSliderBookmark.")
                return

        bookmarks = cmds.ls(type='timeSliderBookmark') or []
        if not bookmarks:
            QtWidgets.QMessageBox.information(self, u"Thông báo", u"Không tìm thấy Bookmark nào trong scene.")
            return

        valid_items = []
        for bm in bookmarks:
            try:
                b_name = cmds.getAttr(bm + ".name")
            except Exception:
                b_name = bm

            # Chỉ lấy các bookmark được đặt tên dạng số
            try:
                bm_num = int(b_name)
            except ValueError:
                continue

            start_f = cmds.getAttr(bm + ".timeRangeStart")
            end_f = cmds.getAttr(bm + ".timeRangeStop")
            valid_items.append((bm_num, b_name, start_f, end_f, bm))

        # Sắp xếp theo số thứ tự
        valid_items.sort(key=lambda x: x[0])

        for bm_num, b_name, start_f, end_f, bm_node in valid_items:
            display_text = u"Shot %02d  |  Frame: %.0f - %.0f" % (bm_num, start_f, end_f)
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, {
                "num": bm_num, "name": b_name,
                "start": start_f, "end": end_f, "node": bm_node
            })
            self.sm_bookmark_list.addItem(item)
            item.setSelected(True)  # Tự động tích chọn hết

        self.sm_bookmark_count_lbl.setText(u"(Tìm thấy %d)" % len(valid_items))
        QtWidgets.QMessageBox.information(
            self, u"Kết quả",
            u"Tìm thấy %d bookmark hợp lệ (dạng số)." % len(valid_items)
        )

    def get_smart_selection(self):
        """
        Lấy danh sách các đối tượng cần giữ key:
        1. Ưu tiên lấy trực tiếp vùng chọn hiện tại của người dùng.
        2. Nếu không có vùng chọn, tự động quét toàn bộ anim curves hoạt động trong scene,
           tìm các node đích đang kết nối và loại trừ camera rig, camera transform.
        """
        selection = cmds.ls(sl=True) or []
        if selection:
            return selection

        print(u"[Pipeline] Không có vùng chọn thủ công. Đang tự động quét toàn bộ control có keyframe trong scene...")

        # Tìm tất cả anim curves đang tồn tại
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

        # Định danh các node camera cần bảo hộ
        cameras = cmds.ls(type='camera') or []
        camera_transforms = []
        for cam in cameras:
            parents = cmds.listRelatives(cam, parent=True) or []
            if parents:
                camera_transforms.append(parents[0])

        # Lọc bỏ camera
        final_selection = []
        for node in keyed_nodes:
            if node in camera_transforms:
                continue
            node_lower = node.lower()
            if any(cam_word in node_lower for cam_word in ['cam', 'camera', 'shot_cam']):
                continue
            final_selection.append(node)

        print(u"[Pipeline] Tự động quét thành công %d control có keyframe (đã bảo vệ các node camera)." % len(final_selection))
        return final_selection

    def on_split_layout(self):
        """Tách file Layout tổng thành các file shot lẻ dựa trên bookmarks đã quét"""
        import os as _os
        import json as _json
        import tempfile as _tempfile

        # 1. Kiểm tra đầu vào
        selected_items = self.sm_bookmark_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, u"Thiếu dữ liệu", u"Chưa có bookmark nào được chọn.\nHãy nhấn 'Quét Bookmarks' trước.")
            return

        # Xác định file nguồn
        scene_name = cmds.file(q=True, sn=True)
        if not scene_name:
            QtWidgets.QMessageBox.warning(self, u"Chưa lưu file", u"Hãy SAVE file Maya hiện tại trước khi tách shot!")
            return
        scene_name = scene_name.replace('\\', '/')

        saved_selection = self.get_smart_selection()
        if not saved_selection:
            QtWidgets.QMessageBox.warning(
                self, u"Thiếu Selection",
                u"Không tìm thấy Control/Object nào có keyframe trong scene và không có vùng chọn thủ công để thực hiện cắt key!"
            )
            return

        # 2. Lấy thông tin project/episode hiện tại từ Tab 1
        project = self.proj_combo.currentText()
        episode = self.ep_combo.currentText()
        if not project or not episode:
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Hãy chọn Project và Episode ở Tab 'Quản Lý File' trước.")
            return

        # 3. Lọc theo khoảng filter (nếu có)
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
            QtWidgets.QMessageBox.warning(self, u"Không khớp", u"Không có bookmark nào khớp với khoảng lọc đã nhập.")
            return

        # 4. Xác nhận
        msg = u"Sẽ tách %d shot từ file Layout đang mở vào Pipeline.\n" % len(bookmarks_data)
        msg += u"Project: %s\nEpisode: %s\n" % (project, episode)
        msg += u"Frame Padding: ±%d frames\n" % padding
        msg += u"Chế độ: Trực tiếp (Có progress bar chống treo đơ Maya)\n"
        msg += u"\nBạn có chắc chắn?"

        reply = QtWidgets.QMessageBox.question(self, u"Xác nhận Tách Shot", msg,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 5. Lưu file hiện tại trước khi thao tác (chỉ lưu nếu scene hiện tại đã được đặt tên/được lưu trước đó)
        current_scene = cmds.file(q=True, sn=True)
        if current_scene:
            try:
                cmds.file(save=True, force=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể lưu file hiện tại:\n%s" % str(e))
                return



        # ============================================================
        # CHẾ ĐỘ CHẠY TRỰC TIẾP (FOREGROUND)
        # ============================================================
        # 6. Chuyển sang DG mode để tránh lỗi parallel evaluation
        original_eval_mode = cmds.evaluationManager(q=True, mode=True)[0]
        if original_eval_mode != 'off':
            cmds.evaluationManager(mode='off')

        base_name = _os.path.basename(scene_name)
        _, ext = _os.path.splitext(base_name)
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"

        # Khởi tạo progress dialog cho chế độ trực tiếp để tránh đơ giao diện
        progress = QtWidgets.QProgressDialog(
            u"Đang tách shot trực tiếp trong Maya...",
            u"Hủy bỏ", 0, len(bookmarks_data), self
        )
        progress.setWindowTitle(u"Đang Tách Shot (Foreground)")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        success_count = 0
        try:
            for i, data in enumerate(bookmarks_data):
                if progress.wasCanceled():
                    print(u"[Split] Người dùng đã hủy bỏ tiến trình.")
                    break

                # Cập nhật progress bar và vẽ lại GUI để tránh freeze
                progress.setValue(i)
                progress.setLabelText(u"Đang xử lý Shot %02d (%d/%d)..." % (data["num"], i + 1, len(bookmarks_data)))
                QtWidgets.QApplication.processEvents()

                bm_num = data["num"]
                start_f = data["start"]
                end_f = data["end"]

                # Xây đường dẫn lưu file shot lẻ
                filepath, shot_dir = self.file_manager.build_split_shot_path(
                    project, episode, bm_num, task="Anim"
                )
                if not filepath:
                    print(u"[Split] Không thể xây đường dẫn cho shot %d" % bm_num)
                    continue

                # Kiểm tra trùng file để chống ghi đè dữ liệu hoạt hình của artist
                if _os.path.exists(filepath):
                    confirm = cmds.confirmDialog(
                        title=u"File đã tồn tại",
                        message=u"File hoạt hình lẻ đã tồn tại:\n%s\n\nBạn có muốn ghi đè (làm mất keyframe anim cũ của shot này) không?" % _os.path.basename(filepath),
                        button=[u"Ghi đè (Overwrite)", u"Bỏ qua (Skip)", u"Hủy toàn bộ (Cancel)"],
                        defaultButton=u"Bỏ qua (Skip)",
                        cancelButton=u"Bỏ qua (Skip)"
                    )
                    if confirm == u"Bỏ qua (Skip)":
                        print(u"[Split] Đã bỏ qua shot %d để bảo vệ file Anim cũ." % bm_num)
                        continue
                    elif confirm == u"Hủy toàn bộ (Cancel)":
                        print(u"[Split] Đã hủy tiến trình tách theo yêu cầu.")
                        break

                # Tạo thư mục nếu chưa có
                if not _os.path.exists(shot_dir):
                    _os.makedirs(shot_dir)

                # Thao tác trong undo chunk
                cmds.undoInfo(openChunk=True)
                try:
                    # Xóa bookmark khác
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

                    # Truy quét toàn bộ anim curves trong scene để dọn sạch keyframe thừa 100% (bao gồm cả camera shape, custom attributes, v.v.)
                    try:
                        anim_curves = cmds.ls(type='animCurve') or []
                    except Exception:
                        anim_curves = []

                    # Cắt key trên từng curve
                    for curve in anim_curves:
                        try:
                            cmds.cutKey(curve, time=(-9999999, start_f - padding - 0.01), option="keys", clear=True)
                        except Exception:
                            pass
                        try:
                            cmds.cutKey(curve, time=(end_f + padding + 0.01, 9999999), option="keys", clear=True)
                        except Exception:
                            pass

                    # Thiết lập timeline
                    cmds.playbackOptions(
                        min=start_f, max=end_f,
                        animationStartTime=start_f, animationEndTime=end_f
                    )
                except Exception as e:
                    print(u"[Split] Lỗi xử lý shot %d: %s" % (bm_num, str(e)))
                finally:
                    cmds.undoInfo(closeChunk=True)

                # Lưu file shot lẻ
                cmds.file(rename=filepath.replace('\\', '/'))
                try:
                    cmds.file(save=True, force=True, type=file_type)
                    print(u"==> Đã xuất shot lẻ thành công: %s" % _os.path.basename(filepath))
                    success_count += 1
                except Exception as e:
                    print(u"[Split] Lỗi lưu file shot %d: %s" % (bm_num, str(e)))

                # Undo để trả scene về trạng thái ban đầu
                cmds.undo()

            progress.setValue(len(bookmarks_data))

        finally:
            # Phục hồi trạng thái ban đầu
            cmds.file(rename=scene_name)
            if original_eval_mode != 'off':
                cmds.evaluationManager(mode=original_eval_mode)
            if saved_selection:
                try:
                    cmds.select(saved_selection)
                except Exception:
                    pass

        QtWidgets.QMessageBox.information(
            self, u"Hoàn tất",
            u"Đã tách thành công %d/%d shot!" % (success_count, len(bookmarks_data))
        )
        # Làm mới danh sách file ở Tab 1
        self.refresh_files_list()



    def on_combine_shots(self):
        """Gộp Animation shot lẻ từ file Layout tổng bằng cách cắt key theo bookmark"""
        import os as _os

        # 1. Kiểm tra đầu vào
        saved_selection = self.get_smart_selection()
        if not saved_selection:
            QtWidgets.QMessageBox.warning(
                self, u"Thiếu Selection",
                u"Không tìm thấy Control/Object nào có keyframe trong scene và không có vùng chọn thủ công để thực hiện gộp!"
            )
            return

        scene_name = cmds.file(q=True, sn=True)
        if not scene_name:
            QtWidgets.QMessageBox.warning(self, u"Chưa lưu file", u"Hãy SAVE file Maya hiện tại trước khi gộp shot!")
            return
        scene_name = scene_name.replace('\\', '/')

        project = self.proj_combo.currentText()
        episode = self.ep_combo.currentText()
        if not project or not episode:
            QtWidgets.QMessageBox.warning(self, u"Thiếu thông tin", u"Hãy chọn Project và Episode ở Tab 'Quản Lý File' trước.")
            return

        start_shot = self.sm_combine_start.value()
        end_shot = self.sm_combine_end.value()
        if start_shot > end_shot:
            QtWidgets.QMessageBox.warning(self, u"Lỗi", u"Khoảng shot không hợp lệ (Start > End).")
            return

        padding = self.sm_combine_padding_spin.value()
        do_bake = self.sm_bake_constraints_cb.isChecked()
        do_smart_bake = self.sm_smart_bake_cb.isChecked()
        threshold = self.sm_threshold_spin.value()

        # 2. Quét bookmarks trong scene để lấy khoảng thời gian
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
                self, u"Không khớp",
                u"Không tìm thấy bookmark nào trong khoảng %d - %d." % (start_shot, end_shot)
            )
            return

        # 3. Xây đường dẫn file gộp
        combine_path = self.file_manager.build_combine_file_path(project, episode, start_shot, end_shot)
        if not combine_path:
            QtWidgets.QMessageBox.warning(self, u"Lỗi", u"Không thể xây đường dẫn file gộp.")
            return

        combine_dir = _os.path.dirname(combine_path)

        # 4. Xác nhận
        msg = u"Sẽ gộp shot từ %d đến %d thành file cụm tổng:\n%s\n\n" % (
            start_shot, end_shot, _os.path.basename(combine_path))
        if do_bake:
            msg += u"✅ Tự động Bake Constraints\n"
        if do_smart_bake:
            msg += u"✅ Smart Bake (threshold=%.2f)\n" % threshold
        msg += u"\nBạn có chắc chắn?"
        reply = QtWidgets.QMessageBox.question(self, u"Xác nhận Gộp Shot", msg,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 5. Lưu file hiện tại
        try:
            cmds.file(save=True, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể lưu file:\n%s" % str(e))
            return

        # 6. Chuyển sang DG mode
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
            # 7. Bake Constraints nếu được chọn
            if do_bake:
                print(u"[Combine] Đang Bake Constraints...")
                self.bake_and_clean_constraints(saved_selection)

            # 8. Smart Bake nếu được chọn
            if do_smart_bake:
                print(u"[Combine] Đang áp dụng Smart Bake...")
                self.apply_smart_bake_filter(saved_selection, threshold)

            # 9. Thực hiện gộp trong undo chunk
            cmds.undoInfo(openChunk=True)
            try:
                # Xóa bookmarks không thuộc khoảng gộp
                all_bms = cmds.ls(type='timeSliderBookmark') or []
                for b in all_bms:
                    if b not in valid_bookmarks:
                        try:
                            cmds.delete(b)
                        except Exception:
                            pass

                # Truy quét toàn bộ anim curves trong scene để dọn sạch keyframe thừa 100%
                try:
                    anim_curves = cmds.ls(type='animCurve') or []
                except Exception:
                    anim_curves = []

                # Cắt key trên từng curve
                for curve in anim_curves:
                    try:
                        cmds.cutKey(curve, time=(-9999999, global_start - padding - 0.01), option="keys", clear=True)
                    except Exception:
                        pass
                    try:
                        cmds.cutKey(curve, time=(global_end + padding + 0.01, 9999999), option="keys", clear=True)
                    except Exception:
                        pass

                # Thiết lập timeline
                cmds.playbackOptions(
                    min=global_start, max=global_end,
                    animationStartTime=global_start, animationEndTime=global_end
                )
            except Exception as e:
                print(u"[Combine] Lỗi: %s" % str(e))
            finally:
                cmds.undoInfo(closeChunk=True)

            # 10. Tạo thư mục và lưu file gộp
            if not _os.path.exists(combine_dir):
                _os.makedirs(combine_dir)

            cmds.file(rename=combine_path.replace('\\', '/'))
            try:
                cmds.file(save=True, force=True, type=file_type)
                print(u"==> Đã xuất file gộp cụm thành công: %s" % _os.path.basename(combine_path))
            except Exception as e:
                print(u"[Combine] Lỗi lưu file: %s" % str(e))

            # Undo để trả scene về trạng thái ban đầu
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
            self, u"Hoàn tất",
            u"Đã gộp cụm shot %d-%d thành công!\n\nFile: %s" % (
                start_shot, end_shot, _os.path.basename(combine_path))
        )

    def bake_and_clean_constraints(self, selection):
        """
        Tự động phát hiện constraint trên các đối tượng đã chọn,
        thực hiện Bake Simulation rồi xóa constraint.
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
            print(u"[Bake] Không tìm thấy control nào bị constraint trong vùng chọn.")
            return

        s_time = cmds.playbackOptions(q=True, minTime=True)
        e_time = cmds.playbackOptions(q=True, maxTime=True)

        print(u"[Bake] Đang bake cho %d objects có constraint..." % len(objects_to_bake))

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
            print(u"[Bake] Đã dọn dẹp xong %d constraints." % len(constraints_to_delete))

    def apply_smart_bake_filter(self, selection, threshold=0.1):
        """
        Áp dụng Smart Bake: bake thưa rồi giảm keyframe bằng keyReducer.
        """
        # 1. Lấy tất cả anim curves từ các objects được chọn
        anim_curves = cmds.keyframe(selection, q=True, name=True) or []
        if not anim_curves:
            print(u"[SmartBake] Không tìm thấy anim curve nào.")
            return

        anim_curves = list(set(anim_curves))

        # 2. Áp dụng bộ lọc keyReducer
        try:
            cmds.filterCurve(anim_curves, filter="keyReducer", precisionMode=0, precision=threshold)
            print(u"[SmartBake] Đã áp dụng keyReducer (threshold=%.2f) cho %d anim curves." % (
                threshold, len(anim_curves)))
        except Exception as e:
            print(u"[SmartBake] Lỗi: %s" % str(e))

    def on_open_studio_library(self):
        """Mở giao diện Studio Library UI"""
        try:
            import studiolibrary
            # Reset biến cửa sổ để tránh xung đột với cửa sổ cũ đã đóng
            studiolibrary._window = None
            studiolibrary.main()
            print(u"[StudioLibrary] Đã mở Studio Library UI.")
        except ImportError:
            QtWidgets.QMessageBox.warning(
                self, u"Lỗi Import",
                u"Không thể import Studio Library.\n"
                u"Kiểm tra thư mục: thirdparty/studiolibrary/src/"
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, u"Lỗi",
                u"Lỗi khi mở Studio Library UI:\n%s" % str(e)
            )

    def on_export_bookmarks_csv(self):
        """Xuất danh sách Bookmarks ra file CSV"""
        import csv

        if not cmds.pluginInfo('timeSliderBookmark', q=True, loaded=True):
            try:
                cmds.loadPlugin('timeSliderBookmark')
            except Exception:
                pass

        bookmarks = cmds.ls(type='timeSliderBookmark') or []
        if not bookmarks:
            QtWidgets.QMessageBox.information(self, u"Thông báo", u"Không tìm thấy Bookmark nào.")
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
            QtWidgets.QMessageBox.information(self, u"Thành công", u"Đã xuất bookmarks ra CSV thành công!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể ghi file CSV:\n%s" % str(e))


def show_window():
    import sys
    
    # 1. Đóng và giải phóng bộ nhớ của giao diện cũ từ sys module
    old_ui = getattr(sys, "_animeow_enjo_pipeline_ui", None)
    if old_ui is not None:
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        sys._animeow_enjo_pipeline_ui = None
        
    # 2. Xóa các workspace control cũ của cả phiên bản cũ và mới
    old_controls = ["AnimeowAnimToolkitWorkspaceControl", "AnimeowEnjoPipelineWorkspaceControl"]
    for ctrl in old_controls:
        if cmds.workspaceControl(ctrl, exists=True):
            try:
                cmds.deleteUI(ctrl)
            except Exception:
                pass
            
    # 3. Tạo instance mới và lưu tham chiếu vào sys module
    ui_instance = AnimeowMayaToolkitUI()
    sys._animeow_enjo_pipeline_ui = ui_instance
    
    # 4. Hiển thị dưới dạng dockable panel
    ui_instance.show(
        dockable=True,
        workspaceControlName=AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME,
        area="right",
        floating=False,
        allowedArea="left|right"
    )
    
    # 5. Cập nhật tiêu đề hiển thị cho tab trong Maya
    if cmds.workspaceControl(AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, exists=True):
        cmds.workspaceControl(
            AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, 
            edit=True, 
            label=AnimeowMayaToolkitUI.WINDOW_TITLE
        )
