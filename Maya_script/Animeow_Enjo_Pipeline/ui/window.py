# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import file_manager, playblast_manager

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
        
        # Hàng 5: Label Danh sách file & Checkbox mở nhanh
        files_label_layout = QtWidgets.QHBoxLayout()
        files_label_layout.addWidget(QtWidgets.QLabel("Working Files (Đúp click để Mở):"))
        
        self.quick_open_cb = QtWidgets.QCheckBox(u"Mở nhanh (Không load References)")
        self.quick_open_cb.setToolTip(u"Tải nhanh cảnh diễn hoạt bằng cách trì hoãn nạp tất cả các file reference bối cảnh/rig nặng.")
        self.quick_open_cb.setStyleSheet("color: #FF9800; font-weight: bold;")
        files_label_layout.addWidget(self.quick_open_cb, 0, QtCore.Qt.AlignRight)
        
        shot_layout.addLayout(files_label_layout, 5, 0, 1, 3)
        
        # Hàng 6: Danh sách file phiên bản
        self.files_list = QtWidgets.QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_open_file)
        self.files_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.files_list.customContextMenuRequested.connect(self.show_file_list_context_menu)
        self.files_list.itemSelectionChanged.connect(self.update_playblast_count)
        shot_layout.addWidget(self.files_list, 6, 0, 1, 3)
        
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
        
        self.publish_btn = QtWidgets.QPushButton("🚀 Publish File")
        self.publish_btn.setObjectName("publish_btn")
        self.publish_btn.setToolTip("Xuất bản file sạch và video playblast lên Server")
        self.publish_btn.clicked.connect(self.on_publish_file)
        btn_layout.addWidget(self.publish_btn)
        
        shot_layout.addLayout(btn_layout, 8, 0, 1, 3)
        
        # Hàng 9: Nút Kiểm tra quy chuẩn
        self.check_naming_btn = QtWidgets.QPushButton("🔍 Kiểm tra quy chuẩn tên File")
        self.check_naming_btn.setToolTip("Quét toàn bộ tập phim và tự động sửa các file đặt tên sai quy chuẩn")
        self.check_naming_btn.clicked.connect(self.on_check_filenames)
        shot_layout.addWidget(self.check_naming_btn, 9, 0, 1, 3)
        
        self.main_layout.addWidget(shot_group)
        
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
        
        # Nhãn hiển thị số lượng Playblast trên Server
        self.pb_count_label = QtWidgets.QLabel("Playblasts on Server: 0 files")
        self.pb_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 2px;")
        playblast_layout.addWidget(self.pb_count_label, 5, 0, 1, 2)
        
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
        
        playblast_layout.addLayout(pb_buttons_layout, 6, 0, 1, 2)
        
        # Trạng thái ẩn/hiện ban đầu
        self.pb_single_cam_widget.setVisible(False)
        self.pb_multi_cam_list.setVisible(False)
        
        self.main_layout.addWidget(playblast_group)
        
        self.main_layout.addStretch()

    # --- SỰ KIỆN & LOGIC ---
    
    def load_settings(self):
        """Tải cấu hình dự án mặc định và tự động đồng bộ file đang mở"""
        if cmds.optionVar(exists=self.OPTION_VAR_PROJ):
            saved_root = cmds.optionVar(q=self.OPTION_VAR_PROJ)
            if os.path.exists(saved_root):
                self.project_root = saved_root
                
        self.file_manager.project_root = self.project_root
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
        self.files_list.clear()
        self.current_work_files = []
        
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (self.project_root and current_proj and current_ep and current_task):
            return
            
        files_info = self.file_manager.get_work_files(current_proj, current_ep, current_task)
        self.current_work_files = files_info
        
        for info in files_info:
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
            if self.quick_open_cb.isChecked():
                kwargs["loadReferenceDepth"] = "none"
                
            cmds.file(to_sys_path(filepath), **kwargs)
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
            
            # Tự động chọn (highlight) file hiện tại trong QListWidget
            for i in range(self.files_list.count()):
                item = self.files_list.item(i)
                item_path = item.data(QtCore.Qt.UserRole)
                if item_path and os.path.normpath(item_path).lower() == norm_filepath.lower():
                    self.files_list.setCurrentItem(item)
                    break

    def update_playblast_count(self):
        """Đếm số lượng file video playblast hiện có trên server cho file Maya đang chọn hoặc file đang mở"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            current_filepath = cmds.file(q=True, sceneName=True)
            if current_filepath:
                filename = os.path.basename(current_filepath)
            else:
                self.pb_count_label.setText("Playblasts on Server: No active file")
                self.pb_count_label.setToolTip("")
                return
        else:
            filepath = selected_items[0].data(QtCore.Qt.UserRole)
            filename = os.path.basename(filepath)
            
        filename_no_ext, _ = os.path.splitext(filename)
        
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        if not (current_proj and current_ep and current_task):
            self.pb_count_label.setText("Playblasts on Server: Unknown")
            self.pb_count_label.setToolTip("")
            return
            
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        mov_dir = os.path.join(self.project_root, current_proj, current_ep, "mov", task_dir_name)
        
        if not os.path.exists(mov_dir):
            self.pb_count_label.setText("Playblasts on Server: 0 files")
            self.pb_count_label.setToolTip("")
            return
            
        count = 0
        matching_files = []
        try:
            for f in os.listdir(mov_dir):
                if f.lower().startswith(filename_no_ext.lower()) and (f.lower().endswith(".mov") or f.lower().endswith(".avi")):
                    count += 1
                    matching_files.append(f)
        except Exception:
            pass
                
        if count == 0:
            self.pb_count_label.setText("Playblasts on Server: 0 files")
            self.pb_count_label.setToolTip("")
        else:
            self.pb_count_label.setText("Playblasts on Server: %d files" % count)
            self.pb_count_label.setToolTip("Exported Playblasts:\n" + "\n".join(matching_files))

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
        
        try:
            if cam_mode == u"Camera hiện hành (Active)":
                output_path = self.playblast_manager.run_playblast(
                    format_ext=format_ext,
                    percent=100,
                    width=width,
                    height=height,
                    viewer=True
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
                    viewer=True
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
                            viewer=False  # Disable viewer in batch to avoid collision
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
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        if not (current_proj and current_ep and current_task):
            return
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        mov_dir = os.path.join(self.project_root, current_proj, current_ep, "mov", task_dir_name)
        
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(mov_dir):
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
        pub_dir = os.path.join(self.project_root, current_proj, current_ep, "Published", task_dir_name)
        self.open_folder_explorer(pub_dir)

    def on_open_mov_dir(self):
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        if not (current_proj and current_ep and current_task):
            return
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        mov_dir = os.path.join(self.project_root, current_proj, current_ep, "mov", task_dir_name)
        self.open_folder_explorer(mov_dir)

    def show_file_list_context_menu(self, pos):
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
        
        # Thêm action xem playblast tương ứng nếu có
        filename = os.path.basename(filepath)
        filename_no_ext = os.path.splitext(filename)[0]
        
        current_proj = self.proj_combo.currentText()
        current_ep = self.ep_combo.currentText()
        current_task = self.task_combo.currentText()
        
        task_dir_name = "Layout" if current_task.lower() in ["layout", "lay"] else "Anim"
        mov_dir = os.path.join(self.project_root, current_proj, current_ep, "mov", task_dir_name)
        
        mov_path = os.path.join(mov_dir, filename_no_ext + ".mov")
        avi_path = os.path.join(mov_dir, filename_no_ext + ".avi")
        
        active_video_path = None
        if os.path.exists(mov_path):
            active_video_path = mov_path
        elif os.path.exists(avi_path):
            active_video_path = avi_path
            
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
