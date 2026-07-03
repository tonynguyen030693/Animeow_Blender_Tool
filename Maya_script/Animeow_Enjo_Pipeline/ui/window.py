# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import file_manager, playblast_manager

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
}
"""

class AnimeowMayaToolkitUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Animeow Anim Toolkit"
    WORKSPACE_CONTROL_NAME = "AnimeowAnimToolkitWorkspaceControl"
    OPTION_VAR_PROJ = "AnimeowProjRoot"

    def __init__(self, parent=None):
        super(AnimeowMayaToolkitUI, self).__init__(parent=parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setStyleSheet(QSS_STYLE)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.project_root = "Z:\\"
        self.current_work_files = []
        
        # Khởi tạo class quản lý
        self.file_manager = file_manager.FileManager(project_root=self.project_root)
        self.playblast_manager = playblast_manager.PlayblastManager()
        
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # 1. Khối Phân Cảnh (Shot Filter)
        shot_group = QtWidgets.QGroupBox("Cơ Cấu Cảnh (Shot Manager)")
        shot_layout = QtWidgets.QGridLayout(shot_group)
        shot_layout.setContentsMargins(8, 8, 8, 8)
        shot_layout.setSpacing(8)
        
        shot_layout.addWidget(QtWidgets.QLabel("Sequence:"), 0, 0)
        self.seq_combo = QtWidgets.QComboBox()
        self.seq_combo.currentIndexChanged.connect(self.on_seq_changed)
        shot_layout.addWidget(self.seq_combo, 0, 1)
        
        shot_layout.addWidget(QtWidgets.QLabel("Shot:"), 1, 0)
        self.shot_combo = QtWidgets.QComboBox()
        self.shot_combo.currentIndexChanged.connect(self.on_shot_changed)
        shot_layout.addWidget(self.shot_combo, 1, 1)
        
        # Danh sách file phiên bản
        shot_layout.addWidget(QtWidgets.QLabel("Work Files (Đúp click để Mở):"), 2, 0, 1, 2)
        self.files_list = QtWidgets.QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_open_file)
        shot_layout.addWidget(self.files_list, 3, 0, 1, 2)
        
        # Các nút bấm lưu/tạo mới
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.create_shot_btn = QtWidgets.QPushButton("Tạo Shot Mới (v001)")
        self.create_shot_btn.clicked.connect(self.on_create_shot)
        btn_layout.addWidget(self.create_shot_btn)
        
        self.save_version_btn = QtWidgets.QPushButton("Lưu Phiên Bản Mới (+1)")
        self.save_version_btn.setObjectName("accent_btn")
        self.save_version_btn.clicked.connect(self.on_increment_save)
        btn_layout.addWidget(self.save_version_btn)
        
        shot_layout.addLayout(btn_layout, 4, 0, 1, 2)
        
        self.main_layout.addWidget(shot_group)
        
        # 3. Khối Playblast
        playblast_group = QtWidgets.QGroupBox("Auto Playblast")
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
        
        self.run_pb_btn = QtWidgets.QPushButton("🎬 Chạy & Xuất Playblast")
        self.run_pb_btn.setObjectName("accent_btn")
        self.run_pb_btn.clicked.connect(self.on_run_playblast)
        playblast_layout.addWidget(self.run_pb_btn, 2, 0, 1, 2)
        
        self.main_layout.addWidget(playblast_group)
        
        # Giãn nở ở cuối
        self.main_layout.addStretch()

    # --- SỰ KIỆN & LOGIC ---
    
    def load_settings(self):
        """Tải cấu hình dự án mặc định ổ Z"""
        self.set_project_root("Z:\\")

    def set_project_root(self, path):
        self.project_root = path
        self.file_manager.project_root = path
        
        # Cập nhật danh sách Sequence
        self.populate_sequences()

    def populate_sequences(self):
        self.seq_combo.blockSignals(True)
        self.seq_combo.clear()
        
        sequences = self.file_manager.get_sequences()
        self.seq_combo.addItems(sequences)
        
        self.seq_combo.blockSignals(False)
        self.on_seq_changed()

    def on_seq_changed(self):
        self.shot_combo.blockSignals(True)
        self.shot_combo.clear()
        
        current_seq = self.seq_combo.currentText()
        if current_seq:
            shots = self.file_manager.get_shots(current_seq)
            self.shot_combo.addItems(shots)
            
        self.shot_combo.blockSignals(False)
        self.on_shot_changed()

    def on_shot_changed(self):
        self.refresh_files_list()

    def refresh_files_list(self):
        self.files_list.clear()
        self.current_work_files = []
        
        current_seq = self.seq_combo.currentText()
        current_shot = self.shot_combo.currentText()
        
        if not (self.project_root and current_seq and current_shot):
            return
            
        files_info = self.file_manager.get_work_files(current_seq, current_shot)
        self.current_work_files = files_info
        
        for info in files_info:
            item_text = "[v%03d] %s  (%s | %s)" % (
                info["version"], 
                info["filename"], 
                info["time"], 
                info["size"]
            )
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, info["filepath"])
            self.files_list.addItem(item)

    def on_open_file(self, item):
        """Mở file được chọn sau khi xác nhận cảnh báo an toàn"""
        filepath = item.data(QtCore.Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            return
            
        # Kiểm tra file hiện tại có thay đổi chưa lưu
        if cmds.file(query=True, modified=True):
            res = QtWidgets.QMessageBox.question(
                self, "Xác nhận mở file",
                "Cảnh hiện tại có thay đổi chưa lưu. Bạn có chắc muốn mở file mới?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
        # Mở file
        try:
            cmds.file(filepath, open=True, force=True)
            cmds.workspace(self.project_root, openWorkspace=True)
            print("Đã mở file thành công: %s" % filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể mở file: %s" % str(e))

    def on_create_shot(self):
        """Tạo file shot v001 mới"""
        current_seq = self.seq_combo.currentText()
        current_shot = self.shot_combo.currentText()
        
        if not (self.project_root and current_seq and current_shot):
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn đầy đủ Project, Sequence và Shot.")
            return
            
        res = QtWidgets.QMessageBox.question(
            self, "Tạo Shot mới",
            "Bạn có muốn tạo cảnh mới v001 cho %s / %s không?" % (current_seq, current_shot),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        new_filepath = self.file_manager.create_new_shot(current_seq, current_shot)
        if new_filepath:
            self.refresh_files_list()
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã tạo và mở cảnh mới v001 thành công!")

    def on_increment_save(self):
        """Lưu tăng phiên bản"""
        new_filepath = self.file_manager.increment_save()
        if new_filepath:
            self.refresh_files_list()
            # Thử cập nhật lựa chọn combo box nếu khớp cấu trúc dự án
            self.refresh_dropdowns_to_match_current(new_filepath)

    def refresh_dropdowns_to_match_current(self, filepath):
        """Tự động đồng bộ dropdown UI khớp với file vừa lưu (nếu thuộc Project)"""
        if not self.project_root or not filepath.startswith(self.project_root):
            return
            
        # Thử lấy sequence/shot từ đường dẫn
        rel_path = os.path.relpath(filepath, self.project_root)
        parts = rel_path.split(os.sep)
        
        # Cấu trúc: Shots/[Seq]/[Shot]/Anim/Work/File.ma
        if len(parts) >= 6 and parts[0] == "Shots":
            seq = parts[1]
            shot = parts[2]
            
            # Đổi selection của combo (tắt signal để tránh lặp)
            self.seq_combo.blockSignals(True)
            self.shot_combo.blockSignals(True)
            
            seq_idx = self.seq_combo.findText(seq)
            if seq_idx != -1:
                self.seq_combo.setCurrentIndex(seq_idx)
                
            # Cập nhật danh sách shot cho sequence vừa đổi
            self.shot_combo.clear()
            shots = self.file_manager.get_shots(seq)
            self.shot_combo.addItems(shots)
            
            shot_idx = self.shot_combo.findText(shot)
            if shot_idx != -1:
                self.shot_combo.setCurrentIndex(shot_idx)
                
            self.seq_combo.blockSignals(False)
            self.shot_combo.blockSignals(False)
            
            self.refresh_files_list()

    def on_run_playblast(self):
        """Chạy playblast"""
        format_text = self.pb_format_combo.currentText()
        format_ext = "qt" if "QuickTime" in format_text else "avi"
        
        res_text = self.pb_res_combo.currentText()
        if "1920x1080" in res_text:
            width, height = 1920, 1080
        elif "1280x720" in res_text:
            width, height = 1280, 720
        else:
            width, height = 640, 360
            
        output_path = self.playblast_manager.run_playblast(
            format_ext=format_ext,
            percent=100,
            width=width,
            height=height
        )
        
        if output_path:
            cmds.confirmDialog(
                title="Playblast hoàn thành",
                message="Video đã xuất thành công tại:\n%s" % output_path,
                button=["OK"]
            )

def show_window():
    if cmds.workspaceControl(AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME)
        
    ui_instance = AnimeowMayaToolkitUI()
    ui_instance.show(
        dockable=True,
        area="right",
        floating=False,
        allowedArea="left|right"
    )
    
    cmds.workspaceControl(
        AnimeowMayaToolkitUI.WORKSPACE_CONTROL_NAME, 
        edit=True, 
        label=AnimeowMayaToolkitUI.WINDOW_TITLE
    )
