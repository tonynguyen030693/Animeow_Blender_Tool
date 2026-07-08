# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import json
import subprocess
import tempfile
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import anim_combiner

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
    color: #00BCD4; /* Cyan accent for Toolboard */
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
    border-color: #00BCD4;
}
QPushButton:pressed {
    background-color: #222222;
}
QPushButton#accent_btn {
    background-color: #00838F;
    color: #FFFFFF;
    border: 1px solid #00BCD4;
}
QPushButton#accent_btn:hover {
    background-color: #0097A7;
}
QPushButton#accent_btn:pressed {
    background-color: #006064;
}
QLineEdit, QComboBox, QSpinBox {
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
    color: #00BCD4;
}
"""

class BatchProgressDialog(QtWidgets.QDialog):
    def __init__(self, mayapy_path, runner_path, config_path, output_path, parent=None):
        super(BatchProgressDialog, self).__init__(parent=parent)
        self.setWindowTitle("Tiến trình ghép nối chạy ngầm (mayapy)")
        self.resize(600, 400)
        self.setStyleSheet(QSS_STYLE)
        
        self.mayapy_path = mayapy_path
        self.runner_path = runner_path
        self.config_path = config_path
        self.output_path = output_path
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.status_lbl = QtWidgets.QLabel("Đang khởi động tiến trình...")
        self.status_lbl.setStyleSheet("font-weight: bold; color: #00BCD4;")
        layout.addWidget(self.status_lbl)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #444444; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #00BCD4; }")
        layout.addWidget(self.progress_bar)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1E1E1E; border: 1px solid #444444; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.log_text)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.cancel_btn = QtWidgets.QPushButton("Hủy tiến trình")
        self.cancel_btn.clicked.connect(self.on_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_ready_read)
        self.process.finished.connect(self.on_finished)
        
        QtCore.QTimer.singleShot(200, self.start_process)
        
    def start_process(self):
        self.status_lbl.setText("Đang khởi động mayapy và nạp Standalone...")
        exec_path = os.path.normpath(self.mayapy_path)
        args = [os.path.normpath(self.runner_path), os.path.normpath(self.config_path)]
        
        self.process.start(exec_path, args)
        if not self.process.waitForStarted(5000):
            self.status_lbl.setText("Lỗi: Không thể khởi chạy mayapy.exe!")
            self.log_text.append("Không thể chạy executable: %s" % exec_path)
            self.cancel_btn.setText("Đóng")
            
    def on_ready_read(self):
        output = self.process.readAllStandardOutput().data().decode("utf-8", "ignore")
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            self.log_text.append(line)
            self.log_text.moveCursor(QtGui.QTextCursor.End)
            
            if line.startswith("STANDALONE_STATUS:"):
                status_msg = line.replace("STANDALONE_STATUS:", "").strip()
                self.status_lbl.setText(status_msg)
            elif line.startswith("PROGRESS_UPDATE:"):
                try:
                    progress_info = line.replace("PROGRESS_UPDATE:", "").strip()
                    parts = progress_info.split("|")[0].strip().split("/")
                    curr = int(parts[0])
                    total = int(parts[1])
                    percent = int((curr / total) * 100)
                    self.progress_bar.setValue(percent)
                    
                    msg = progress_info.split("|")[1].strip() if "|" in progress_info else ""
                    if msg:
                        self.status_lbl.setText(msg)
                except Exception:
                    pass
            elif line.startswith("STANDALONE_ERROR:"):
                err_msg = line.replace("STANDALONE_ERROR:", "").strip()
                self.status_lbl.setText("Lỗi: %s" % err_msg)
                
    def on_finished(self, exit_code, exit_status):
        if os.path.exists(self.config_path):
            try:
                os.remove(self.config_path)
            except:
                pass
                
        if exit_code == 0:
            self.status_lbl.setText("Hoàn thành thành công!")
            self.progress_bar.setValue(100)
            self.cancel_btn.setText("Đóng")
            
            res = QtWidgets.QMessageBox.question(
                self, "Mở file kết quả?",
                "Ghép nối chuyển động hoàn thành ngầm thành công!\nBạn có muốn mở file tổng hợp vừa ghép vào phiên Maya hiện tại không?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.Yes:
                try:
                    cmds.file(self.output_path, open=True, force=True)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể mở file cảnh: %s" % str(e))
        else:
            self.status_lbl.setText("Lỗi: Tiến trình chạy ngầm thất bại!")
            self.cancel_btn.setText("Đóng")
            QtWidgets.QMessageBox.critical(
                self, "Lỗi chạy ngầm",
                "Đã xảy ra lỗi khi chạy ghép nối ngầm. Hãy xem chi tiết log hiển thị trong bảng."
            )
            
    def on_cancel(self):
        if self.process.state() == QtCore.QProcess.Running:
            res = QtWidgets.QMessageBox.question(
                self, "Hủy tiến trình?",
                "Tiến trình đang chạy. Bạn có chắc chắn muốn hủy không?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.Yes:
                self.process.kill()
                self.reject()
        else:
            self.accept()

class AnimeowMayaToolboardUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Animeow Anim Combiner Toolboard"
    WORKSPACE_CONTROL_NAME = "AnimeowAnimCombinerWorkspaceControl"
    
    # OptionVars cache
    OP_SOURCE_DIR = "AnimeowTbSourceDir"
    OP_MASTER_SCENE = "AnimeowTbMasterScene"
    OP_OUTPUT_FILE = "AnimeowTbOutputFile"
    OP_TIME_MODE = "AnimeowTbTimeMode"
    OP_START_FRAME = "AnimeowTbStartFrame"
    OP_BG_MODE = "AnimeowTbBgMode"

    def __init__(self, parent=None):
        super(AnimeowMayaToolboardUI, self).__init__(parent=parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setStyleSheet(QSS_STYLE)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # Tiêu đề giao diện
        title_label = QtWidgets.QLabel("ANIMEOW ANIM COMBINER")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        self.main_layout.addWidget(title_label)
        
        # 1. Khối Shot nguồn (Source Shots)
        src_group = QtWidgets.QGroupBox("1. Thư mục chứa các Shot lẻ")
        src_layout = QtWidgets.QVBoxLayout(src_group)
        src_layout.setContentsMargins(8, 8, 8, 8)
        src_layout.setSpacing(6)
        
        path_layout = QtWidgets.QHBoxLayout()
        self.src_dir_txt = QtWidgets.QLineEdit()
        self.src_dir_txt.setPlaceholderText("Đường dẫn đến thư mục chứa các file .ma, .mb con...")
        self.src_dir_txt.setReadOnly(True)
        path_layout.addWidget(self.src_dir_txt)
        
        self.src_browse_btn = QtWidgets.QPushButton("Browse")
        self.src_browse_btn.clicked.connect(self.on_browse_source_dir)
        path_layout.addWidget(self.src_browse_btn)
        src_layout.addLayout(path_layout)
        
        src_layout.addWidget(QtWidgets.QLabel("Danh sách Shot con sẽ ghép (tự động lọc):"))
        self.shots_list = QtWidgets.QListWidget()
        src_layout.addWidget(self.shots_list)
        
        self.main_layout.addWidget(src_group)
        
        # 2. Khối File Master mẫu (Master Template)
        master_group = QtWidgets.QGroupBox("2. File Master mẫu (Chứa Rig sạch)")
        master_layout = QtWidgets.QHBoxLayout(master_group)
        master_layout.setContentsMargins(8, 8, 8, 8)
        master_layout.setSpacing(6)
        
        self.master_path_txt = QtWidgets.QLineEdit()
        self.master_path_txt.setPlaceholderText("Chọn file .ma hoặc .mb master mẫu...")
        self.master_path_txt.setReadOnly(True)
        master_layout.addWidget(self.master_path_txt)
        
        self.master_browse_btn = QtWidgets.QPushButton("Browse")
        self.master_browse_btn.clicked.connect(self.on_browse_master_scene)
        master_layout.addWidget(self.master_browse_btn)
        
        self.main_layout.addWidget(master_group)
        
        # 3. Khối Đường dẫn lưu (Output Combined File)
        out_group = QtWidgets.QGroupBox("3. Đường dẫn lưu file kết quả (Combined Output)")
        out_layout = QtWidgets.QHBoxLayout(out_group)
        out_layout.setContentsMargins(8, 8, 8, 8)
        out_layout.setSpacing(6)
        
        self.out_path_txt = QtWidgets.QLineEdit()
        self.out_path_txt.setPlaceholderText("Nơi lưu file master sau khi ghép anim...")
        self.out_path_txt.setReadOnly(True)
        out_layout.addWidget(self.out_path_txt)
        
        self.out_browse_btn = QtWidgets.QPushButton("Browse")
        self.out_browse_btn.clicked.connect(self.on_browse_output_file)
        out_layout.addWidget(self.out_browse_btn)
        
        self.main_layout.addWidget(out_group)
        
        # 4. Khối Cấu hình thời gian (Time Settings)
        time_group = QtWidgets.QGroupBox("4. Thiết lập thời gian (Time Options)")
        time_layout = QtWidgets.QGridLayout(time_group)
        time_layout.setContentsMargins(8, 8, 8, 8)
        time_layout.setSpacing(8)
        
        time_layout.addWidget(QtWidgets.QLabel("Chế độ ghép:"), 0, 0)
        self.time_mode_combo = QtWidgets.QComboBox()
        self.time_mode_combo.addItems([
            "Nối đuôi tự động (Sequential Join)",
            "Giữ nguyên Frame gốc (Keep Original Frames)"
        ])
        self.time_mode_combo.currentIndexChanged.connect(self.on_time_mode_changed)
        time_layout.addWidget(self.time_mode_combo, 0, 1)
        
        time_layout.addWidget(QtWidgets.QLabel("Start Frame:"), 1, 0)
        self.start_frame_spin = QtWidgets.QSpinBox()
        self.start_frame_spin.setRange(-9999, 99999)
        self.start_frame_spin.setValue(1)
        time_layout.addWidget(self.start_frame_spin, 1, 1)
        
        # Checkbox Chạy ngầm
        self.bg_mode_cb = QtWidgets.QCheckBox("Chạy ngầm (Background Mode - Không đơ Maya)")
        self.bg_mode_cb.setChecked(True)
        time_layout.addWidget(self.bg_mode_cb, 2, 0, 1, 2)
        
        self.main_layout.addWidget(time_group)
        
        # 5. Nút thực thi chính
        self.run_btn = QtWidgets.QPushButton("🎬 Bắt Đầu Ghép Nối Animation")
        self.run_btn.setObjectName("accent_btn")
        self.run_btn.setFixedHeight(40)
        self.run_btn.clicked.connect(self.on_run_combiner)
        self.main_layout.addWidget(self.run_btn)
        
        # Thêm co giãn ở cuối
        self.main_layout.addStretch()

    # --- SỰ KIỆN & LOGIC ---

    def load_settings(self):
        """Tải lại các thiết lập trước đó từ optionVar"""
        if cmds.optionVar(exists=self.OP_SOURCE_DIR):
            saved_dir = cmds.optionVar(query=self.OP_SOURCE_DIR)
            if os.path.exists(saved_dir):
                self.src_dir_txt.setText(saved_dir)
                self.scan_source_directory(saved_dir)
                
        if cmds.optionVar(exists=self.OP_MASTER_SCENE):
            saved_master = cmds.optionVar(query=self.OP_MASTER_SCENE)
            if os.path.exists(saved_master):
                self.master_path_txt.setText(saved_master)
                
        if cmds.optionVar(exists=self.OP_OUTPUT_FILE):
            saved_out = cmds.optionVar(query=self.OP_OUTPUT_FILE)
            self.out_path_txt.setText(saved_out)
            
        if cmds.optionVar(exists=self.OP_TIME_MODE):
            mode_idx = cmds.optionVar(query=self.OP_TIME_MODE)
            self.time_mode_combo.setCurrentIndex(mode_idx)
            
        if cmds.optionVar(exists=self.OP_START_FRAME):
            start_f = cmds.optionVar(query=self.OP_START_FRAME)
            self.start_frame_spin.setValue(start_f)
            
        if cmds.optionVar(exists=self.OP_BG_MODE):
            bg_val = cmds.optionVar(query=self.OP_BG_MODE)
            self.bg_mode_cb.setChecked(bool(bg_val))

    def save_settings(self):
        """Lưu cấu hình hiện tại vào optionVar"""
        cmds.optionVar(stringValue=(self.OP_SOURCE_DIR, self.src_dir_txt.text()))
        cmds.optionVar(stringValue=(self.OP_MASTER_SCENE, self.master_path_txt.text()))
        cmds.optionVar(stringValue=(self.OP_OUTPUT_FILE, self.out_path_txt.text()))
        cmds.optionVar(intValue=(self.OP_TIME_MODE, self.time_mode_combo.currentIndex()))
        cmds.optionVar(intValue=(self.OP_START_FRAME, self.start_frame_spin.value()))
        cmds.optionVar(intValue=(self.OP_BG_MODE, int(self.bg_mode_cb.isChecked())))

    def on_browse_source_dir(self):
        current = self.src_dir_txt.text() or "Z:\\"
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa các file Shot con", current)
        if path:
            norm_path = os.path.normpath(path)
            self.src_dir_txt.setText(norm_path)
            self.scan_source_directory(norm_path)
            self.save_settings()

    def scan_source_directory(self, path):
        """Quét và tìm các file cảnh .ma hoặc .mb trong thư mục"""
        self.shots_list.clear()
        if not path or not os.path.exists(path):
            return
            
        files = []
        for item in os.listdir(path):
            if item.lower().endswith(".ma") or item.lower().endswith(".mb"):
                files.append(item)
                
        # Sắp xếp theo tên file (Shot01, Shot02...)
        files = sorted(files)
        
        for filename in files:
            filepath = os.path.join(path, filename)
            item = QtWidgets.QListWidgetItem(filename)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked) # Check mặc định
            item.setData(QtCore.Qt.UserRole, filepath)
            self.shots_list.addItem(item)

    def on_browse_master_scene(self):
        current = self.master_path_txt.text() or "Z:\\"
        file_filter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Chọn File Master mẫu", current, file_filter)
        if path:
            norm_path = os.path.normpath(path)
            self.master_path_txt.setText(norm_path)
            self.save_settings()
            
            # Gợi ý tự động tên file output nằm cùng thư mục file master
            if not self.out_path_txt.text():
                dirname = os.path.dirname(norm_path)
                filename = os.path.basename(norm_path)
                name, ext = os.path.splitext(filename)
                suggested_out = os.path.join(dirname, "%s_Combined%s" % (name, ext))
                self.out_path_txt.setText(os.path.normpath(suggested_out))

    def on_browse_output_file(self):
        current = self.out_path_txt.text() or "Z:\\"
        file_filter = "Maya ASCII (*.ma);;Maya Binary (*.mb)"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Chọn nơi lưu file kết quả", current, file_filter)
        if path:
            norm_path = os.path.normpath(path)
            self.out_path_txt.setText(norm_path)
            self.save_settings()

    def on_time_mode_changed(self, index):
        # Chỉ bật spin box nếu chọn chế độ nối đuôi tự động (Sequential Join)
        self.start_frame_spin.setEnabled(index == 0)
        self.save_settings()

    def get_selected_shot_paths(self):
        """Lấy danh sách các file được tick chọn"""
        paths = []
        for i in range(self.shots_list.count()):
            item = self.shots_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                paths.append(item.data(QtCore.Qt.UserRole))
        return paths

    def on_run_combiner(self):
        """Thực thi gom nhóm và ghép anim"""
        shot_files = self.get_selected_shot_paths()
        master_scene = self.master_path_txt.text()
        output_file = self.out_path_txt.text()
        
        if not shot_files:
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn ít nhất 1 file shot con trong danh sách.")
            return
            
        if not master_scene or not os.path.exists(master_scene):
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn file Master mẫu hợp lệ.")
            return
            
        if not output_file:
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn đường dẫn lưu file kết quả.")
            return
            
        # Xác định chế độ thời gian
        time_mode = "sequential" if self.time_mode_combo.currentIndex() == 0 else "keep_frames"
        start_frame = self.start_frame_spin.value()
        
        self.save_settings()
        
        if self.bg_mode_cb.isChecked():
            # CHẾ ĐỘ CHẠY NGẦM (Không gây đóng cảnh hiện tại)
            self.run_in_background(shot_files, master_scene, output_file, time_mode, start_frame)
        else:
            # CHẾ ĐỘ CHẠY TRỰC TIẾP (Cảnh báo đóng cảnh hiện tại)
            res = QtWidgets.QMessageBox.question(
                self, "Xác nhận ghép nối",
                "Công cụ sẽ đóng cảnh hiện tại để mở tuần tự các shot con và xuất anim.\nBạn đã lưu công việc hiện tại chưa?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return
                
            # Thực hiện ghép nối trực tiếp
            combiner = anim_combiner.AnimationCombiner(
                shot_files=shot_files,
                master_scene_path=master_scene,
                output_path=output_file,
                time_mode=time_mode,
                master_start_frame=start_frame
            )
            success = combiner.run()
            
            if success:
                # Đọc file kết quả đè lên luôn để hiển thị trực tiếp
                try:
                    cmds.file(output_file, open=True, force=True)
                except:
                    pass
                QtWidgets.QMessageBox.information(
                    self, "Thành công",
                    "Ghép nối chuyển động hoàn thành!\nCảnh tổng hợp hiện đã được mở."
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self, "Thất bại",
                    "Đã xảy ra lỗi trong quá trình ghép nối anim. Vui lòng kiểm tra Script Editor."
                )

    def run_in_background(self, shot_files, master_scene, output_file, time_mode, start_frame):
        # 1. Tìm mayapy.exe tự động từ sys.executable
        maya_bin_dir = os.path.dirname(sys.executable)
        mayapy_path = os.path.join(maya_bin_dir, "mayapy.exe")
        if not os.path.exists(mayapy_path):
            # Try default path for Maya 2020 on Windows if sys.executable isn't standard
            mayapy_path = "C:/Program Files/Autodesk/Maya2020/bin/mayapy.exe"
            
        if not os.path.exists(mayapy_path):
            QtWidgets.QMessageBox.critical(
                self, "Lỗi chạy ngầm", 
                "Không tìm thấy mayapy.exe tại đường dẫn:\n%s\nVui lòng kiểm tra lại bộ cài đặt Maya." % mayapy_path
            )
            return
            
        # 2. Tạo config JSON cấu hình tạm
        config_data = {
            "shot_files": shot_files,
            "master_scene_path": master_scene,
            "output_path": output_file,
            "time_mode": time_mode,
            "master_start_frame": start_frame
        }
        
        try:
            fd, temp_config_path = tempfile.mkstemp(suffix="_combiner_config.json")
            os.close(fd)
            with open(temp_config_path, "w") as f:
                json.dump(config_data, f)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi khởi tạo", "Không thể tạo file cấu hình tạm: %s" % str(e))
            return
            
        # 3. Tìm batch_runner.py
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(ui_dir)
        runner_path = os.path.join(parent_dir, "core", "batch_runner.py")
        
        if not os.path.exists(runner_path):
            QtWidgets.QMessageBox.critical(self, "Lỗi khởi tạo", "Không tìm thấy file batch_runner.py tại:\n%s" % runner_path)
            if os.path.exists(temp_config_path):
                os.remove(temp_config_path)
            return
            
        # 4. Mở hộp thoại tiến trình chạy ngầm
        dialog = BatchProgressDialog(
            mayapy_path=mayapy_path,
            runner_path=runner_path,
            config_path=temp_config_path,
            output_path=output_file,
            parent=self
        )
        dialog.exec_()

def is_ui_alive(ui_obj):
    """Kiểm tra xem đối tượng Qt UI còn sống ở phía C++ không để tránh lỗi pointer chết"""
    if ui_obj is None:
        return False
    try:
        ui_obj.objectName()
        return True
    except RuntimeError:
        return False


def show_window():
    import sys
    
    # 1. Đóng và giải phóng widget cũ (nếu có)
    old_ui = getattr(sys, "_animeow_maya_toolboard_ui", None)
    if is_ui_alive(old_ui):
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        sys._animeow_maya_toolboard_ui = None

    # 2. Xóa các workspaceControl cũ và dọn dẹp các control rác từ các bản build lỗi trước đó
    for ctrl_name in [AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, 
                      AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME + "WorkspaceControl"]:
        if cmds.workspaceControl(ctrl_name, exists=True):
            try:
                cmds.deleteUI(ctrl_name)
            except Exception:
                pass
            
    # 3. Tạo instance mới
    ui_instance = AnimeowMayaToolboardUI()
    sys._animeow_maya_toolboard_ui = ui_instance
    
    # Thiết lập objectName (không bao gồm hậu tố WorkspaceControl) để Maya tự động ghép thêm hậu tố này
    # tạo thành đúng tên AnimeowMayaToolboardWorkspaceControl khớp với WORKSPACE_CONTROL_NAME
    obj_name = AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME.replace("WorkspaceControl", "")
    ui_instance.setObjectName(obj_name)
    
    # 4. Kiểm tra xem người dùng đã từng có tùy biến vị trí (windowPref) được lưu cho workspace control này chưa
    pref_exists = False
    try:
        pref_exists = cmds.windowPref(AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, exists=True)
    except Exception:
        pass
        
    # 5. Hiển thị dưới dạng dockable panel
    if pref_exists:
        # Nếu đã có tùy chỉnh vị trí trước đó (Ví dụ kéo ra ngoài float hoặc dock chỗ khác),
        # ta để Maya tự động tải cấu hình cũ bằng cách không áp các giá trị mặc định (floating=False, area="right")
        ui_instance.show(dockable=True)
    else:
        # Nếu là lần đầu chạy tool, áp dụng docking mặc định ở bên phải
        ui_instance.show(
            dockable=True,
            area="right",
            floating=False,
            allowedArea="left|right"
        )
    
    # 6. Cập nhật tiêu đề hiển thị cho tab trong Maya
    if cmds.workspaceControl(AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, exists=True):
        cmds.workspaceControl(
            AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, 
            edit=True, 
            label=AnimeowMayaToolboardUI.WINDOW_TITLE
        )
    return ui_instance
