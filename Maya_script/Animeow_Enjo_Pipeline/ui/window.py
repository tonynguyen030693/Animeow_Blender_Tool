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
        folder_name = self.file_manager.get_episode_folder_name(sample_text)
        abbrev = self.file_manager.get_episode_abbreviation(self.project, folder_name)
        
        self.folder_input.setText(folder_name)
        self.abbrev_input.setText(abbrev)
        
    def get_data(self):
        return self.folder_input.text().strip(), self.abbrev_input.text().strip()

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
        
        # Hàng 3: Task (Khâu)
        shot_layout.addWidget(QtWidgets.QLabel("Task:"), 3, 0)
        self.task_combo = QtWidgets.QComboBox()
        self.task_combo.addItems(["Layout", "Animation"])
        self.task_combo.currentIndexChanged.connect(self.on_task_changed)
        shot_layout.addWidget(self.task_combo, 3, 1)
        
        self.create_file_btn = QtWidgets.QPushButton("➕ Tạo File")
        self.create_file_btn.setToolTip("Tạo file nháp mới cho Khâu hiện tại")
        self.create_file_btn.clicked.connect(self.on_create_file)
        shot_layout.addWidget(self.create_file_btn, 3, 2)
        
        # Hàng 4: Label Danh sách file
        shot_layout.addWidget(QtWidgets.QLabel("Working Files (Đúp click để Mở):"), 4, 0, 1, 3)
        
        # Hàng 5: Danh sách file phiên bản
        self.files_list = QtWidgets.QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_open_file)
        shot_layout.addWidget(self.files_list, 5, 0, 1, 3)
        
        # Hàng 6: Các nút bấm lưu/publish
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
        
        shot_layout.addLayout(btn_layout, 6, 0, 1, 3)
        
        # Hàng 7: Nút Kiểm tra quy chuẩn
        self.check_naming_btn = QtWidgets.QPushButton("🔍 Kiểm tra quy chuẩn tên File")
        self.check_naming_btn.setToolTip("Quét toàn bộ tập phim và tự động sửa các file đặt tên sai quy chuẩn")
        self.check_naming_btn.clicked.connect(self.on_check_filenames)
        shot_layout.addWidget(self.check_naming_btn, 7, 0, 1, 3)
        
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
        
        self.run_pb_btn = QtWidgets.QPushButton("🎬 Chạy & Xuất Playblast Nháp")
        self.run_pb_btn.setObjectName("accent_btn")
        self.run_pb_btn.clicked.connect(self.on_run_playblast)
        playblast_layout.addWidget(self.run_pb_btn, 2, 0, 1, 2)
        
        self.main_layout.addWidget(playblast_group)
        
        self.main_layout.addStretch()

    # --- SỰ KIỆN & LOGIC ---
    
    def load_settings(self):
        """Tải cấu hình dự án mặc định"""
        if cmds.optionVar(exists=self.OPTION_VAR_PROJ):
            saved_root = cmds.optionVar(q=self.OPTION_VAR_PROJ)
            if os.path.exists(saved_root):
                self.project_root = saved_root
                
        self.file_manager.project_root = self.project_root
        self.populate_projects()

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
        self.refresh_files_list()

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
            cmds.file(filepath, open=True, force=True)
            cmds.workspace(self.project_root, openWorkspace=True)
            print("Đã mở file thành công: %s" % filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, u"Lỗi", u"Không thể mở file: %s" % str(e))

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
        """Tự động đồng bộ dropdown UI khớp với file vừa lưu"""
        if not self.project_root or not filepath.startswith(self.project_root):
            return
            
        rel_path = os.path.relpath(filepath, self.project_root)
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
            
        output_path = self.playblast_manager.run_playblast(
            format_ext=format_ext,
            percent=100,
            width=width,
            height=height
        )
        
        if output_path:
            cmds.confirmDialog(
                title="Playblast nháp hoàn thành",
                message="Video nháp đã xuất thành công tại:\n%s" % output_path,
                button=["OK"]
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
            cmds.file(pub_filepath, open=True, force=True)
            print("Đang chạy Playblast chính thức cho file Publish...")
            self.playblast_manager.run_playblast(
                format_ext="qt",
                percent=100,
                width=1920,
                height=1080,
                custom_path=pub_video_path
            )
        except Exception as e:
            print("Lỗi khi chạy Playblast Publish: %s" % str(e))
        finally:
            if current_filepath and os.path.exists(current_filepath):
                cmds.file(current_filepath, open=True, force=True)
                
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
        print("Da lam moi danh sach tu Server.")

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
