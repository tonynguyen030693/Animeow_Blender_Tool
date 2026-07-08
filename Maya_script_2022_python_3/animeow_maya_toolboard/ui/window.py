# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import smart_link, playblast

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
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1E1E1E;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 6px;
    color: #FFFFFF;
}
QTabWidget::pane {
    border: 1px solid #444444;
    top: -1px;
    background-color: #2D2D2D;
}
QTabBar::tab {
    background-color: #3C3C3C;
    color: #AAAAAA;
    border: 1px solid #444444;
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #2D2D2D;
    border-bottom: 1px solid #2D2D2D;
    color: #00BCD4;
}
QTabBar::tab:hover {
    color: #FFFFFF;
    border-top: 2px solid #00BCD4;
}
"""

def ensure_scripts_2022_path():
    # 1. Thử lấy đường dẫn động tương đối theo cấu trúc thư mục của git repo
    ui_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(ui_dir)
    python3_dir = os.path.dirname(package_dir)
    workspace_root = os.path.dirname(python3_dir)
    
    dynamic_path = os.path.join(workspace_root, "Maya_script_2020_python_2", "Tool_reference", "scripts_2022")
    
    # 2. Thử đường dẫn tuyệt đối mặc định cũ làm phương án dự phòng
    hardcoded_path = r"E:\AI_Work\Blender_Maya_Script\Maya_script_2020_python_2\Tool_reference\scripts_2022"
    
    # Xác định đường dẫn thực tế tồn tại trên máy hiện hành (Ưu tiên nạp từ thirdparty nội bộ trước)
    thirdparty_path = os.path.join(package_dir, "thirdparty")
    path = ""
    if os.path.exists(thirdparty_path) and os.path.isdir(thirdparty_path) and len(os.listdir(thirdparty_path)) > 1:
        path = thirdparty_path
    elif os.path.exists(dynamic_path):
        path = dynamic_path
    elif os.path.exists(hardcoded_path):
        path = hardcoded_path

    if not path:
        print("[AnimeowToolboard] Khong tim thay thu muc scripts_2022 hay thirdparty chua cac tool bo tro!")
        return ""
        
    import sys
    if path not in sys.path:
        sys.path.insert(0, path)
        print("[AnimeowToolboard] Da them duong dan Python: %s" % path)
        
    # Thêm thư mục src của Studio Library vào sys.path
    sl_path = os.path.join(path, "studiolibrary-2.9.6.b3", "studiolibrary-2.9.6.b3", "src")
    if os.path.exists(sl_path) and sl_path not in sys.path:
        sys.path.insert(0, sl_path)
        print("[AnimeowToolboard] Da them duong dan Studio Library: %s" % sl_path)
        
    # Thêm vào MAYA_SCRIPT_PATH để source file mel
    import maya.mel as mel
    current_script_paths = mel.eval("getenv \"MAYA_SCRIPT_PATH\"") or ""
    sep = ";" if os.name == 'nt' else ":"
    paths_list = current_script_paths.split(sep)
    
    norm_path = os.path.normpath(path).lower()
    has_path = any(os.path.normpath(p).lower() == norm_path for p in paths_list if p)
    
    if not has_path:
        new_script_paths = "%s%s%s" % (path, sep, current_script_paths)
        mel.eval('putenv "MAYA_SCRIPT_PATH" "%s"' % new_script_paths.replace("\\", "/"))
        print("[AnimeowToolboard] Da them duong dan MEL: %s" % path)
        
    return path

class AnimeowMayaToolboardUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Animeow Maya Toolboard"
    WORKSPACE_CONTROL_NAME = "AnimeowMayaToolboardWorkspaceControl"
    
    # optionVars
    OP_TARGET = "AnimeowTbSmartLinkTarget"
    OP_OWNER = "AnimeowTbSmartLinkOwner"
    OP_STEP = "AnimeowTbBakeStep"
    OP_SMART_CLEAN = "AnimeowTbBakeSmartClean"
    OP_THRESHOLD = "AnimeowTbBakeThreshold"
    OP_PB_CAMERA = "AnimeowTbPbCamera"
    OP_PB_FORMAT = "AnimeowTbPbFormat"
    OP_PB_WIDTH = "AnimeowTbPbWidth"
    OP_PB_HEIGHT = "AnimeowTbPbHeight"
    OP_PB_SCALE = "AnimeowTbPbScale"
    OP_PB_VIEWER = "AnimeowTbPbViewer"
    OP_PB_OVERWRITE = "AnimeowTbPbOverwrite"

    def __init__(self, parent=None):
        super(AnimeowMayaToolboardUI, self).__init__(parent=parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setStyleSheet(QSS_STYLE)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)
        
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # Khởi tạo QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # --- TAB 1: SMART LINK ---
        tab1 = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(6, 10, 6, 6)
        tab1_layout.setSpacing(12)
        
        # Tiêu đề Tab 1
        title_label = QtWidgets.QLabel("🎯 ANIMEOW SMART LINK")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        tab1_layout.addWidget(title_label)
        
        # 1. Khối đối tượng (Link Targets)
        link_group = QtWidgets.QGroupBox("1. Thiết lập Đối Tượng liên kết (Target & Owner)")
        link_layout = QtWidgets.QVBoxLayout(link_group)
        link_layout.setContentsMargins(8, 12, 8, 8)
        link_layout.setSpacing(10)
        
        # Hàng Target
        target_row = QtWidgets.QHBoxLayout()
        target_row.addWidget(QtWidgets.QLabel("Target (Vật dẫn):"))
        self.target_txt = QtWidgets.QLineEdit()
        self.target_txt.setPlaceholderText("Xương / Vật dẫn đường (Driver)...")
        target_row.addWidget(self.target_txt)
        self.get_target_btn = QtWidgets.QPushButton("Lấy đang chọn")
        self.get_target_btn.clicked.connect(self.on_get_target)
        target_row.addWidget(self.get_target_btn)
        link_layout.addLayout(target_row)
        
        # Hàng Owner
        owner_row = QtWidgets.QHBoxLayout()
        owner_row.addWidget(QtWidgets.QLabel("Owner (Vật bị dẫn):"))
        self.owner_txt = QtWidgets.QLineEdit()
        self.owner_txt.setPlaceholderText("Vật bị ràng buộc (Driven)...")
        owner_row.addWidget(self.owner_txt)
        self.get_owner_btn = QtWidgets.QPushButton("Lấy đang chọn")
        self.get_owner_btn.clicked.connect(self.on_get_owner)
        owner_row.addWidget(self.get_owner_btn)
        link_layout.addLayout(owner_row)
        
        # Tùy chọn locator
        self.use_locator_cb = QtWidgets.QCheckBox("Sử dụng cặp Locator (Hook & Offset) lồng nhau")
        self.use_locator_cb.setChecked(True)
        link_layout.addWidget(self.use_locator_cb)
        
        tab1_layout.addWidget(link_group)
        
        # 2. Khối cấu hình Bake (Bake Settings)
        bake_group = QtWidgets.QGroupBox("2. Thiết lập Bake chuyển động")
        bake_layout = QtWidgets.QGridLayout(bake_group)
        bake_layout.setContentsMargins(8, 12, 8, 8)
        bake_layout.setSpacing(8)
        
        bake_layout.addWidget(QtWidgets.QLabel("Step (Bước nhảy):"), 0, 0)
        self.bake_step_spin = QtWidgets.QSpinBox()
        self.bake_step_spin.setRange(1, 100)
        self.bake_step_spin.setValue(1)
        bake_layout.addWidget(self.bake_step_spin, 0, 1)
        
        self.smart_clean_cb = QtWidgets.QCheckBox("Smart Clean (Bake thưa tối ưu key thô)")
        self.smart_clean_cb.setChecked(True)
        bake_layout.addWidget(self.smart_clean_cb, 1, 0, 1, 2)
        
        bake_layout.addWidget(QtWidgets.QLabel("Key Reducer Threshold:"), 2, 0)
        self.threshold_spin = QtWidgets.QDoubleSpinBox()
        self.threshold_spin.setRange(0.001, 2.0)
        self.threshold_spin.setValue(0.05)
        self.threshold_spin.setSingleStep(0.01)
        bake_layout.addWidget(self.threshold_spin, 2, 1)
        
        tab1_layout.addWidget(bake_group)
        
        # 3. Khu vực nút bấm hành động
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(8)
        
        self.link_btn = QtWidgets.QPushButton("🚀 Gán Liên Kết (Link)")
        self.link_btn.setObjectName("accent_btn")
        self.link_btn.setFixedHeight(35)
        self.link_btn.clicked.connect(self.on_link)
        btn_layout.addWidget(self.link_btn)
        
        self.switch_btn = QtWidgets.QPushButton("🔄 Đổi Vật Dẫn (Switch Target)")
        self.switch_btn.setFixedHeight(30)
        self.switch_btn.clicked.connect(self.on_switch_target)
        btn_layout.addWidget(self.switch_btn)
        
        self.bake_btn = QtWidgets.QPushButton("🎬 Bake & Clean (Giải phóng)")
        self.bake_btn.setFixedHeight(35)
        self.bake_btn.clicked.connect(self.on_bake_clean)
        btn_layout.addWidget(self.bake_btn)
        
        tab1_layout.addLayout(btn_layout)
        tab1_layout.addStretch()
        
        # --- TAB 2: TIỆN ÍCH (QUICK TOOLS) ---
        tab2 = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(6, 10, 6, 6)
        tab2_layout.setSpacing(12)
        
        # Tiêu đề Tab 2
        tools_title = QtWidgets.QLabel("🛠️ ANIMEOW QUICK TOOLS")
        tools_title.setAlignment(QtCore.Qt.AlignCenter)
        tools_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        tab2_layout.addWidget(tools_title)
        
        # Khối công cụ mở rộng
        tools_group = QtWidgets.QGroupBox("Tích hợp các bộ công cụ hoạt họa bên thứ ba")
        tools_layout = QtWidgets.QGridLayout(tools_group)
        tools_layout.setContentsMargins(8, 12, 8, 8)
        tools_layout.setSpacing(10)
        
        self.studio_lib_btn = QtWidgets.QPushButton("🎨 Studio Library")
        self.studio_lib_btn.setFixedHeight(32)
        self.studio_lib_btn.clicked.connect(self.on_launch_studiolibrary)
        tools_layout.addWidget(self.studio_lib_btn, 0, 0)
        
        self.dwpicker_btn = QtWidgets.QPushButton("🖱️ DWPicker")
        self.dwpicker_btn.setFixedHeight(32)
        self.dwpicker_btn.clicked.connect(self.on_launch_dwpicker)
        tools_layout.addWidget(self.dwpicker_btn, 0, 1)
        
        self.tween_machine_btn = QtWidgets.QPushButton("⏱️ Tween Machine")
        self.tween_machine_btn.setFixedHeight(32)
        self.tween_machine_btn.clicked.connect(self.on_launch_tweenmachine)
        tools_layout.addWidget(self.tween_machine_btn, 1, 0)
        
        self.atools_btn = QtWidgets.QPushButton("🛠️ aTools")
        self.atools_btn.setFixedHeight(32)
        self.atools_btn.clicked.connect(self.on_launch_atools)
        tools_layout.addWidget(self.atools_btn, 1, 1)
        
        self.animo_btn = QtWidgets.QPushButton("🚀 Animo (Animation Tools)")
        self.animo_btn.setFixedHeight(32)
        self.animo_btn.clicked.connect(self.on_launch_animo)
        tools_layout.addWidget(self.animo_btn, 2, 0, 1, 2)
        
        tab2_layout.addWidget(tools_group)
        
        # Lời giải thích nhỏ
        info_label = QtWidgets.QLabel("💡 Mẹo: Nhấp vào nút công cụ lần đầu để mở,\nnhấp lại lần nữa để tắt (Toggle đóng/mở nhanh).")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        tab2_layout.addWidget(info_label)
        
        tab2_layout.addStretch()
        
        # --- TAB 3: PLAYBLAST ---
        tab3 = QtWidgets.QWidget()
        tab3_layout = QtWidgets.QVBoxLayout(tab3)
        tab3_layout.setContentsMargins(6, 10, 6, 6)
        tab3_layout.setSpacing(12)
        
        # Tiêu đề Tab 3
        pb_title = QtWidgets.QLabel("🎬 ANIMEOW PLAYBLAST MANAGER")
        pb_title.setAlignment(QtCore.Qt.AlignCenter)
        pb_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        tab3_layout.addWidget(pb_title)
        
        # Khối cấu hình Playblast
        pb_group = QtWidgets.QGroupBox("Cấu hình Quay thử (Playblast Settings)")
        pb_layout = QtWidgets.QGridLayout(pb_group)
        pb_layout.setContentsMargins(8, 12, 8, 8)
        pb_layout.setSpacing(10)
        
        # Camera
        pb_layout.addWidget(QtWidgets.QLabel("Camera:"), 0, 0)
        cam_row = QtWidgets.QHBoxLayout()
        self.camera_combo = QtWidgets.QComboBox()
        cam_row.addWidget(self.camera_combo)
        self.refresh_cam_btn = QtWidgets.QPushButton("🔄")
        self.refresh_cam_btn.setFixedWidth(30)
        self.refresh_cam_btn.clicked.connect(self.on_refresh_cameras)
        cam_row.addWidget(self.refresh_cam_btn)
        pb_layout.addLayout(cam_row, 0, 1)
        
        # Format
        pb_layout.addWidget(QtWidgets.QLabel("Định dạng (Format):"), 1, 0)
        self.pb_format_combo = QtWidgets.QComboBox()
        self.pb_format_combo.addItems(["QuickTime (mov)", "AVI (avi)"])
        pb_layout.addWidget(self.pb_format_combo, 1, 1)
        
        # Resolution (W x H)
        pb_layout.addWidget(QtWidgets.QLabel("Độ phân giải:"), 2, 0)
        res_row = QtWidgets.QHBoxLayout()
        self.pb_width_spin = QtWidgets.QSpinBox()
        self.pb_width_spin.setRange(320, 7680)
        self.pb_width_spin.setValue(1920)
        self.pb_height_spin = QtWidgets.QSpinBox()
        self.pb_height_spin.setRange(240, 4320)
        self.pb_height_spin.setValue(1080)
        res_row.addWidget(self.pb_width_spin)
        res_row.addWidget(QtWidgets.QLabel("x"))
        res_row.addWidget(self.pb_height_spin)
        pb_layout.addLayout(res_row, 2, 1)
        
        # Scale (Percent)
        pb_layout.addWidget(QtWidgets.QLabel("Tỉ lệ (Scale %):"), 3, 0)
        self.pb_scale_spin = QtWidgets.QSpinBox()
        self.pb_scale_spin.setRange(10, 100)
        self.pb_scale_spin.setValue(100)
        self.pb_scale_spin.setSuffix(" %")
        pb_layout.addWidget(self.pb_scale_spin, 3, 1)
        
        tab3_layout.addWidget(pb_group)
        
        # Khối tùy chọn thêm
        pb_options_group = QtWidgets.QGroupBox("Tùy chọn bổ sung")
        pb_opt_layout = QtWidgets.QVBoxLayout(pb_options_group)
        pb_opt_layout.setContentsMargins(8, 12, 8, 8)
        pb_opt_layout.setSpacing(8)
        
        self.pb_viewer_cb = QtWidgets.QCheckBox("Tự động mở trình phát sau khi quay xong")
        self.pb_viewer_cb.setChecked(True)
        pb_opt_layout.addWidget(self.pb_viewer_cb)
        
        self.pb_overwrite_cb = QtWidgets.QCheckBox("Ghi đè trực tiếp lên tệp cũ (Không lưu trữ Old)")
        self.pb_overwrite_cb.setChecked(False)
        pb_opt_layout.addWidget(self.pb_overwrite_cb)
        
        tab3_layout.addWidget(pb_options_group)
        
        # Nút thực thi Playblast
        self.run_pb_btn = QtWidgets.QPushButton("🎬 Xuất Video Playblast (Nháp)")
        self.run_pb_btn.setObjectName("accent_btn")
        self.run_pb_btn.setFixedHeight(40)
        self.run_pb_btn.clicked.connect(self.on_run_playblast)
        tab3_layout.addWidget(self.run_pb_btn)
        
        tab3_layout.addStretch()
        
        # Thêm các tab vào Widget
        self.tab_widget.addTab(tab1, "🔗 Smart Link")
        self.tab_widget.addTab(tab2, "🛠️ Quick Tools")
        self.tab_widget.addTab(tab3, "🎬 Playblast")

    # --- HÀNH ĐỘNG DỮ LIỆU ---

    def load_settings(self):
        if cmds.optionVar(exists=self.OP_TARGET):
            self.target_txt.setText(cmds.optionVar(query=self.OP_TARGET))
        if cmds.optionVar(exists=self.OP_OWNER):
            self.owner_txt.setText(cmds.optionVar(query=self.OP_OWNER))
        if cmds.optionVar(exists=self.OP_STEP):
            self.bake_step_spin.setValue(cmds.optionVar(query=self.OP_STEP))
        if cmds.optionVar(exists=self.OP_SMART_CLEAN):
            self.smart_clean_cb.setChecked(bool(cmds.optionVar(query=self.OP_SMART_CLEAN)))
        if cmds.optionVar(exists=self.OP_THRESHOLD):
            self.threshold_spin.setValue(cmds.optionVar(query=self.OP_THRESHOLD))

        # Khởi tạo danh sách camera trước
        self.on_refresh_cameras()
        if cmds.optionVar(exists=self.OP_PB_CAMERA):
            cam = cmds.optionVar(query=self.OP_PB_CAMERA)
            idx = self.camera_combo.findText(cam)
            if idx >= 0:
                self.camera_combo.setCurrentIndex(idx)
        if cmds.optionVar(exists=self.OP_PB_FORMAT):
            fmt = cmds.optionVar(query=self.OP_PB_FORMAT)
            idx = self.pb_format_combo.findText(fmt)
            if idx >= 0:
                self.pb_format_combo.setCurrentIndex(idx)
        if cmds.optionVar(exists=self.OP_PB_WIDTH):
            self.pb_width_spin.setValue(cmds.optionVar(query=self.OP_PB_WIDTH))
        if cmds.optionVar(exists=self.OP_PB_HEIGHT):
            self.pb_height_spin.setValue(cmds.optionVar(query=self.OP_PB_HEIGHT))
        if cmds.optionVar(exists=self.OP_PB_SCALE):
            self.pb_scale_spin.setValue(cmds.optionVar(query=self.OP_PB_SCALE))
        if cmds.optionVar(exists=self.OP_PB_VIEWER):
            self.pb_viewer_cb.setChecked(bool(cmds.optionVar(query=self.OP_PB_VIEWER)))
        if cmds.optionVar(exists=self.OP_PB_OVERWRITE):
            self.pb_overwrite_cb.setChecked(bool(cmds.optionVar(query=self.OP_PB_OVERWRITE)))

    def save_settings(self):
        cmds.optionVar(stringValue=(self.OP_TARGET, self.target_txt.text()))
        cmds.optionVar(stringValue=(self.OP_OWNER, self.owner_txt.text()))
        cmds.optionVar(intValue=(self.OP_STEP, self.bake_step_spin.value()))
        cmds.optionVar(intValue=(self.OP_SMART_CLEAN, int(self.smart_clean_cb.isChecked())))
        cmds.optionVar(floatValue=(self.OP_THRESHOLD, self.threshold_spin.value()))

        # Lưu cấu hình Playblast
        cmds.optionVar(stringValue=(self.OP_PB_CAMERA, self.camera_combo.currentText()))
        cmds.optionVar(stringValue=(self.OP_PB_FORMAT, self.pb_format_combo.currentText()))
        cmds.optionVar(intValue=(self.OP_PB_WIDTH, self.pb_width_spin.value()))
        cmds.optionVar(intValue=(self.OP_PB_HEIGHT, self.pb_height_spin.value()))
        cmds.optionVar(intValue=(self.OP_PB_SCALE, self.pb_scale_spin.value()))
        cmds.optionVar(intValue=(self.OP_PB_VIEWER, int(self.pb_viewer_cb.isChecked())))
        cmds.optionVar(intValue=(self.OP_PB_OVERWRITE, int(self.pb_overwrite_cb.isChecked())))

    def on_get_target(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.target_txt.setText(sel[0])
            self.save_settings()
        else:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Hãy chọn một đối tượng làm Target!")

    def on_get_owner(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.owner_txt.setText(sel[0])
            self.save_settings()
        else:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Hãy chọn một đối tượng làm Owner!")

    # --- LOGIC THỰC THI ---

    def on_link(self):
        target = self.target_txt.text()
        owner = self.owner_txt.text()
        
        # Nếu chưa gán thông tin rõ ràng, tự động sử dụng vùng chọn
        if not target or not owner:
            sel = cmds.ls(sl=True) or []
            if len(sel) >= 2:
                target = sel[0]
                owner = sel[1]
                self.target_txt.setText(target)
                self.owner_txt.setText(owner)
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Thiếu thông tin",
                    "Vui lòng gán Target & Owner hoặc chọn ít nhất 2 đối tượng trên viewport (đầu tiên là Target, thứ hai là Owner)!"
                )
                return

        if not cmds.objExists(target) or not cmds.objExists(owner):
            QtWidgets.QMessageBox.critical(self, "Lỗi đối tượng", "Đối tượng Target hoặc Owner không tồn tại trong scene!")
            return

        if target == owner:
            QtWidgets.QMessageBox.warning(self, "Lỗi ràng buộc", "Không thể liên kết một đối tượng với chính nó!")
            return

        use_locator = self.use_locator_cb.isChecked()
        self.save_settings()

        if use_locator:
            # Kiểm tra xem owner đã có liên kết locator nào chưa
            baker = smart_link.AnimationBaker(owner)
            loc_parent, loc_child = baker.find_locator_names()
            if loc_parent or loc_child:
                QtWidgets.QMessageBox.warning(
                    self, "Liên kết đã tồn tại",
                    "Đối tượng này đã có liên kết locator rồi. Hãy thực hiện Bake & Clean trước khi tạo liên kết mới!"
                )
                return

            # Tiến hành tạo Smart Link
            manager = smart_link.SmartLinkManager(owner, target)
            has_anim = manager.detect_existing_animation()
            
            s_time = cmds.playbackOptions(q=True, minTime=True)
            e_time = cmds.playbackOptions(q=True, maxTime=True)
            curr_time = cmds.currentTime(q=True)

            loc_temp = None
            if has_anim:
                print(u"[SmartLink] Đang ghi hình chuyển động cũ của %s..." % owner)
                loc_temp = manager.record_world_animation(s_time, e_time)
                manager.clear_owner_keyframes()
                cmds.currentTime(curr_time, edit=True)

            # Khởi tạo locator
            manager.create_locator_pair()
            manager.apply_constraint_to_target()
            manager.apply_constraint_to_owner()

            # Chuyển anim nếu có
            if has_anim and loc_temp:
                manager.match_animation_to_child(loc_temp, s_time, e_time)
                cmds.currentTime(curr_time, edit=True)
                smart_link.SmartLinkManager.cleanup_temp(loc_temp)
                manager.reset_owner_transforms()

            print(u"[SmartLink] Đã liên kết thành công %s đi theo %s thông qua cặp Locator." % (owner, target))
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã tạo liên kết Locator thành công!")

        else:
            # Gán trực tiếp không qua locator
            cmds.parentConstraint(target, owner, maintainOffset=True)
            try:
                cmds.scaleConstraint(target, owner, maintainOffset=True)
            except:
                pass
            print(u"[SmartLink] Đã liên kết trực tiếp %s đi theo %s." % (owner, target))
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã tạo liên kết trực tiếp thành công!")

    def on_switch_target(self):
        owner = self.owner_txt.text()
        if not owner:
            sel = cmds.ls(sl=True)
            if sel:
                owner = sel[0]
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn vật bị dẫn (Owner)!")
                return

        new_target = self.target_txt.text()
        if not new_target or not cmds.objExists(new_target):
            # Nếu trống, thử lấy vật chọn đầu tiên không phải owner
            sel = cmds.ls(sl=True) or []
            possible = [s for s in sel if s != owner]
            if possible:
                new_target = possible[0]
                self.target_txt.setText(new_target)
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn hoặc gán Target mới để chuyển đổi!")
                return

        curr_time = cmds.currentTime(q=True)
        switcher = smart_link.SpaceSwitcher(owner, curr_time)
        success = switcher.switch_to_target(new_target)
        
        if success:
            QtWidgets.QMessageBox.information(
                self, "Chuyển Driver Thành công",
                "Đã chuyển đổi driver của %s sang %s thành công tại frame %d." % (owner, new_target, curr_time)
            )
        else:
            QtWidgets.QMessageBox.critical(
                self, "Thất bại",
                "Không thể chuyển driver. Vui lòng kiểm tra lại xem đối tượng đã có liên kết locator chưa."
            )

    def on_bake_clean(self):
        owner = self.owner_txt.text()
        if not owner:
            sel = cmds.ls(sl=True)
            if sel:
                owner = sel[0]
                self.owner_txt.setText(owner)
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn đối tượng cần Bake!")
                return

        if not cmds.objExists(owner):
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Vật thể %s không tồn tại!" % owner)
            return

        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận Bake & Clean",
            "Sẽ nướng chuyển động từ locator/constraint vào keyframe của %s và dọn dẹp các locator/constraint thừa.\nBạn có chắc chắn?" % owner,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return

        self.save_settings()
        s_time = cmds.playbackOptions(q=True, minTime=True)
        e_time = cmds.playbackOptions(q=True, maxTime=True)
        step = self.bake_step_spin.value()
        smart_clean = self.smart_clean_cb.isChecked()
        threshold = self.threshold_spin.value()

        try:
            baker = smart_link.AnimationBaker(owner)
            baker.bake(
                start_frame=s_time,
                end_frame=e_time,
                step=step,
                smart_clean=smart_clean,
                clean_threshold=threshold
            )
            print(u"[SmartLink] Đã bake và dọn dẹp liên kết cho %s thành công." % owner)
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã nướng và dọn dẹp thành công chuyển động cho %s!" % owner)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi Bake", "Lỗi xảy ra khi bake: %s" % smart_link.exception_to_unicode(e))

    def on_launch_studiolibrary(self):
        ensure_scripts_2022_path()
        try:
            import studiolibrary
            window = getattr(studiolibrary, "_window", None)
            if window is not None:
                try:
                    window.close()
                    studiolibrary._window = None
                    print("[StudioLibrary] Da dong Studio Library.")
                    return
                except Exception:
                    pass
            studiolibrary._window = None
            studiolibrary.main()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể chạy Studio Library:\n%s" % str(e))

    def on_launch_dwpicker(self):
        ensure_scripts_2022_path()
        try:
            import dwpicker
            from dwpicker.main import WINDOW_CONTROL_NAME
            if cmds.workspaceControl(WINDOW_CONTROL_NAME, exists=True):
                dwpicker.close()
                print("[DWPicker] Da dong DWPicker.")
            else:
                dwpicker.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể chạy DWPicker:\n%s" % str(e))

    def on_launch_tweenmachine(self):
        ensure_scripts_2022_path()
        try:
            import maya.mel as mel
            if cmds.window("tweenMachineWin", exists=True):
                cmds.deleteUI("tweenMachineWin")
                print("[TweenMachine] Da dong Tween Machine.")
            else:
                mel.eval('source "tweenMachine.mel"; tweenMachine;')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể chạy Tween Machine:\n%s" % str(e))

    def on_launch_atools(self):
        ensure_scripts_2022_path()
        try:
            from aTools.animTools.animBar import animBarUI
            # aTools co ho tro mode="toggle" tich hop san
            animBarUI.show(mode="toggle")
        except Exception as e:
            try:
                import aTools.general.main as aToolsMain
                aToolsMain.show()
            except Exception as e2:
                QtWidgets.QMessageBox.critical(
                    self, "Lỗi", 
                    "Không thể chạy aTools. Vui lòng đảm bảo bạn đã cài đặt aTools qua thư mục aTools_install:\n%s" % str(e)
                )

    def on_launch_animo(self):
        thirdparty_dir = ensure_scripts_2022_path()
        if not thirdparty_dir:
            return
            
        animo_data_path = os.path.join(thirdparty_dir, "Animo_v5.9.6", "Animo_v5.9.6", "Animo_Data")
        if not os.path.exists(animo_data_path):
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không tìm thấy thư mục Animo_Data tại:\n%s" % animo_data_path)
            return
            
        # Kiểm tra xem Animo đang mở hay không để thực hiện Bật/Tắt (Toggle)
        animo_visible = False
        if cmds.workspaceControl('animo', exists=True):
            animo_visible = cmds.workspaceControl('animo', query=True, visible=True)
            
        # Kiểm tra Qt Toolbar của Animo
        qt_toolbar_visible = False
        existing_qt_toolbar = None
        try:
            import maya.OpenMayaUI as mui
            from PySide2 import QtWidgets as QtW
            from shiboken2 import wrapInstance
            maya_main_ptr = mui.MQtUtil.mainWindow()
            if maya_main_ptr:
                maya_main = wrapInstance(int(maya_main_ptr), QtW.QMainWindow)
                existing_qt_toolbar = maya_main.findChild(QtW.QWidget, "animo_qt_toolbar")
                if existing_qt_toolbar and existing_qt_toolbar.isVisible():
                    qt_toolbar_visible = True
        except Exception:
            pass

        if animo_visible or qt_toolbar_visible:
            # --- ĐÓNG ANIMO ---
            if cmds.workspaceControl('animo', exists=True):
                cmds.workspaceControl('animo', edit=True, visible=False)
            if existing_qt_toolbar:
                try:
                    existing_qt_toolbar.hide()
                except Exception:
                    pass
            print("[Animo] Đã đóng Animo.")
        else:
            # --- MỞ ANIMO ---
            if cmds.workspaceControl('animo', exists=True):
                cmds.deleteUI('animo', control=True)
            if existing_qt_toolbar:
                try:
                    existing_qt_toolbar.hide()
                    existing_qt_toolbar.setParent(None)
                    existing_qt_toolbar.deleteLater()
                except Exception:
                    pass
                    
            # Xoá cache sys.modules
            mods_to_delete = [mod for mod in list(sys.modules.keys()) 
                              if 'Animo' in mod or 'animo' in mod or 'styleMod' in mod or 'barMod' in mod]
            for mod in mods_to_delete:
                del sys.modules[mod]
                
            # Thêm các đường dẫn nạp vào sys.path
            animo_launcher_dir = os.path.join(animo_data_path, "Animo_Launcher")
            for p in [animo_data_path, animo_launcher_dir]:
                if p not in sys.path:
                    sys.path.insert(0, p)
                    
            # Load và thực thi khởi động UI Animo
            try:
                import importlib.util
                launcher_file = os.path.join(animo_launcher_dir, "Animo_Launcher.py")
                spec = importlib.util.spec_from_file_location("Animo_Launcher_Module", launcher_file)
                launcher_module = importlib.util.module_from_spec(spec)
                sys.modules["Animo_Launcher_Module"] = launcher_module
                spec.loader.exec_module(launcher_module)
                _tb = launcher_module.toolbar()
                _tb.startUI()
                print("[Animo] Đã khởi chạy Animo thành công.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Lỗi", "Lỗi khởi chạy Animo:\n%s" % str(e))

    def on_refresh_cameras(self):
        """Làm mới danh sách camera trong scene"""
        current_cam = self.camera_combo.currentText()
        self.camera_combo.clear()
        
        cams = cmds.ls(type="camera")
        cam_transforms = []
        for cam in cams:
            parent = cmds.listRelatives(cam, parent=True)
            if parent:
                cam_transforms.append(parent[0])
                
        cam_transforms = sorted(list(set(cam_transforms)))
        startup_cams = ["persp", "top", "front", "side"]
        custom_cams = [c for c in cam_transforms if c not in startup_cams]
        sorted_cams = custom_cams + startup_cams
        
        self.camera_combo.addItems(sorted_cams)
        
        idx = self.camera_combo.findText(current_cam)
        if idx >= 0:
            self.camera_combo.setCurrentIndex(idx)

    def on_run_playblast(self):
        """Thực thi quay thử Playblast"""
        self.save_settings()
        
        camera = self.camera_combo.currentText()
        if not camera:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy camera khả dụng!")
            return
            
        fmt_text = self.pb_format_combo.currentText()
        format_ext = "avi" if "avi" in fmt_text.lower() else "qt"
        
        width = self.pb_width_spin.value()
        height = self.pb_height_spin.value()
        percent = self.pb_scale_spin.value()
        viewer = self.pb_viewer_cb.isChecked()
        overwrite = self.pb_overwrite_cb.isChecked()
        
        try:
            pbm = playblast.PlayblastManager()
            output_file = pbm.run_playblast(
                format_ext=format_ext,
                percent=percent,
                width=width,
                height=height,
                camera=camera,
                viewer=viewer,
                overwrite=overwrite
            )
            print("[Playblast] Xuat video thanh cong: %s" % output_file)
            QtWidgets.QMessageBox.information(
                self, "Thành công", 
                "Đã xuất Playblast thành công!\nĐường dẫn:\n%s" % output_file
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Playblast", 
                "Lỗi xảy ra khi xuất Playblast:\n%s" % playblast.exception_to_unicode(e)
            )


def show_window():
    import sys
    
    # 1. Đóng và giải phóng bộ nhớ của giao diện cũ từ sys module
    old_ui = getattr(sys, "_animeow_maya_toolboard_ui", None)
    if old_ui is not None:
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        sys._animeow_maya_toolboard_ui = None
        
    # 2. Xóa workspace control cũ nếu tồn tại
    if cmds.workspaceControl(AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, exists=True):
        try:
            cmds.deleteUI(AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME)
        except Exception:
            pass
            
    # 3. Tạo instance mới và lưu tham chiếu vào sys module
    ui_instance = AnimeowMayaToolboardUI()
    sys._animeow_maya_toolboard_ui = ui_instance
    
    # 4. Hiển thị dưới dạng dockable panel với workspaceControlName định danh
    ui_instance.show(
        dockable=True,
        workspaceControlName=AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME,
        area="right",
        floating=False,
        allowedArea="left|right"
    )
    
    # 5. Cập nhật tiêu đề hiển thị cho tab trong Maya
    if cmds.workspaceControl(AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, exists=True):
        cmds.workspaceControl(
            AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME, 
            edit=True, 
            label=AnimeowMayaToolboardUI.WINDOW_TITLE
        )
