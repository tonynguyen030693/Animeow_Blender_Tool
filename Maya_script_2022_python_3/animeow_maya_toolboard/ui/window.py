# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import smart_link, playblast, arc_tracker, world_bake, round_tool

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
    OP_PB_MULTI_CAM = "AnimeowTbPbMultiCam"
    OP_PB_MULTI_CAMS_LIST = "AnimeowTbPbMultiCamsList"
    OP_AT_SHOW_TICKS = "AnimeowTbAtShowTicks"
    OP_AT_SHOW_KEYS = "AnimeowTbAtShowKeys"
    OP_AT_TICK_SIZE = "AnimeowTbAtTickSize"
    OP_WB_CHANNELS = "AnimeowTbWbChannels"
    OP_WB_STEP = "AnimeowTbWbStep"
    OP_WB_SMART_CLEAN = "AnimeowTbWbSmartClean"
    OP_RT_PRECISION = "AnimeowTbRtPrecision"
    OP_RT_TARGET = "AnimeowTbRtTarget"

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
        
        self.animo_btn = QtWidgets.QPushButton("🚀 Animo")
        self.animo_btn.setFixedHeight(32)
        self.animo_btn.clicked.connect(self.on_launch_animo)
        tools_layout.addWidget(self.animo_btn, 2, 0)
        
        self.world_bake_btn = QtWidgets.QPushButton("🌍 World Bake")
        self.world_bake_btn.setFixedHeight(32)
        self.world_bake_btn.clicked.connect(self.on_launch_worldbake)
        tools_layout.addWidget(self.world_bake_btn, 2, 1)
        
        tab2_layout.addWidget(tools_group)
        
        # Khối tiện ích Maya nhanh
        utils_group = QtWidgets.QGroupBox("Tiện ích nhanh Maya")
        utils_layout = QtWidgets.QGridLayout(utils_group)
        utils_layout.setContentsMargins(8, 12, 8, 8)
        utils_layout.setSpacing(10)
        
        self.toggle_graph_btn = QtWidgets.QPushButton("📈 Graph Editor")
        self.toggle_graph_btn.setFixedHeight(32)
        self.toggle_graph_btn.clicked.connect(self.on_toggle_graph_editor)
        utils_layout.addWidget(self.toggle_graph_btn, 0, 0)
        
        self.toggle_ref_btn = QtWidgets.QPushButton("📂 Reference Editor")
        self.toggle_ref_btn.setFixedHeight(32)
        self.toggle_ref_btn.clicked.connect(self.on_toggle_reference_editor)
        utils_layout.addWidget(self.toggle_ref_btn, 0, 1)
        
        self.save_inc_btn = QtWidgets.QPushButton("💾 Save Increment")
        self.save_inc_btn.setFixedHeight(32)
        self.save_inc_btn.clicked.connect(self.on_save_increment)
        utils_layout.addWidget(self.save_inc_btn, 1, 0)
        
        self.save_up_ver_btn = QtWidgets.QPushButton("🚀 Save Up Version")
        self.save_up_ver_btn.setFixedHeight(32)
        self.save_up_ver_btn.clicked.connect(self.on_save_up_version)
        utils_layout.addWidget(self.save_up_ver_btn, 1, 1)
        
        self.clean_folder_btn = QtWidgets.QPushButton("🧹 Clean Folder (Dọn dẹp thư mục)")
        self.clean_folder_btn.setFixedHeight(32)
        self.clean_folder_btn.clicked.connect(self.on_clean_folder)
        utils_layout.addWidget(self.clean_folder_btn, 2, 0, 1, 2)
        
        tab2_layout.addWidget(utils_group)
        
        # Khối làm tròn số
        round_group = QtWidgets.QGroupBox("Làm tròn số (Round Values)")
        round_layout = QtWidgets.QGridLayout(round_group)
        round_layout.setContentsMargins(8, 12, 8, 8)
        round_layout.setSpacing(10)
        
        # Độ chính xác
        round_layout.addWidget(QtWidgets.QLabel("Làm tròn đến:"), 0, 0)
        self.round_precision_combo = QtWidgets.QComboBox()
        self.round_precision_combo.addItems([
            "Số nguyên (ví dụ: 1)", 
            "1 chữ số thập phân (ví dụ: 1.1)", 
            "2 chữ số thập phân (ví dụ: 1.23)"
        ])
        round_layout.addWidget(self.round_precision_combo, 0, 1)
        
        # Đối tượng làm tròn
        round_layout.addWidget(QtWidgets.QLabel("Môi trường:"), 1, 0)
        self.round_target_combo = QtWidgets.QComboBox()
        self.round_target_combo.addItems([
            "Channel Box (Thuộc tính hiện tại)", 
            "Graph Editor (Keyframe đang chọn)"
        ])
        round_layout.addWidget(self.round_target_combo, 1, 1)
        
        # Nút thực thi
        self.round_btn = QtWidgets.QPushButton("🔢 Làm tròn số")
        self.round_btn.setObjectName("accent_btn")
        self.round_btn.setFixedHeight(35)
        self.round_btn.clicked.connect(self.on_round_values)
        round_layout.addWidget(self.round_btn, 2, 0, 1, 2)
        
        tab2_layout.addWidget(round_group)
        
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
        cam_container = QtWidgets.QWidget()
        cam_vbox = QtWidgets.QVBoxLayout(cam_container)
        cam_vbox.setContentsMargins(0, 0, 0, 0)
        cam_vbox.setSpacing(6)
        
        cam_row = QtWidgets.QHBoxLayout()
        self.camera_combo = QtWidgets.QComboBox()
        cam_row.addWidget(self.camera_combo)
        self.refresh_cam_btn = QtWidgets.QPushButton("🔄")
        self.refresh_cam_btn.setFixedWidth(30)
        self.refresh_cam_btn.clicked.connect(self.on_refresh_cameras)
        cam_row.addWidget(self.refresh_cam_btn)
        cam_vbox.addLayout(cam_row)
        
        self.camera_list_widget = QtWidgets.QListWidget()
        self.camera_list_widget.setFixedHeight(100)
        self.camera_list_widget.setVisible(False)
        cam_vbox.addWidget(self.camera_list_widget)
        
        self.multi_cam_cb = QtWidgets.QCheckBox("Quay hàng loạt (Multi-Camera)")
        self.multi_cam_cb.stateChanged.connect(self.on_toggle_multi_cam)
        cam_vbox.addWidget(self.multi_cam_cb)
        
        pb_layout.addWidget(cam_container, 0, 1)
        
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
        
        # --- TAB 4: ARC TRACKER ---
        tab4 = QtWidgets.QWidget()
        tab4_layout = QtWidgets.QVBoxLayout(tab4)
        tab4_layout.setContentsMargins(6, 10, 6, 6)
        tab4_layout.setSpacing(12)
        
        # Tiêu đề Tab 4
        at_title = QtWidgets.QLabel("📈 ANIMEOW ARC TRACKER")
        at_title.setAlignment(QtCore.Qt.AlignCenter)
        at_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        tab4_layout.addWidget(at_title)
        
        # Khối cấu hình Arc Tracker
        at_group = QtWidgets.QGroupBox("Cài đặt Đường dẫn (Trail Settings)")
        at_layout = QtWidgets.QGridLayout(at_group)
        at_layout.setContentsMargins(8, 12, 8, 8)
        at_layout.setSpacing(10)
        
        self.at_show_ticks_cb = QtWidgets.QCheckBox("Hiển thị Ticks thường (Màu vàng)")
        self.at_show_ticks_cb.setChecked(True)
        at_layout.addWidget(self.at_show_ticks_cb, 0, 0, 1, 2)
        
        self.at_show_keys_cb = QtWidgets.QCheckBox("Hiển thị Ticks Keyframe (Màu đỏ)")
        self.at_show_keys_cb.setChecked(True)
        at_layout.addWidget(self.at_show_keys_cb, 1, 0, 1, 2)
        
        at_layout.addWidget(QtWidgets.QLabel("Kích thước Ticks (Size):"), 2, 0)
        self.at_tick_size_spin = QtWidgets.QDoubleSpinBox()
        self.at_tick_size_spin.setRange(0.01, 2.0)
        self.at_tick_size_spin.setValue(0.1)
        self.at_tick_size_spin.setSingleStep(0.02)
        at_layout.addWidget(self.at_tick_size_spin, 2, 1)
        
        tab4_layout.addWidget(at_group)
        
        # Các nút bấm hành động
        at_btn_layout = QtWidgets.QVBoxLayout()
        at_btn_layout.setSpacing(8)
        
        self.create_trail_btn = QtWidgets.QPushButton("🚀 Vẽ Arc Trail (Vật thể chọn)")
        self.create_trail_btn.setObjectName("accent_btn")
        self.create_trail_btn.setFixedHeight(35)
        self.create_trail_btn.clicked.connect(self.on_create_arc_trail)
        at_btn_layout.addWidget(self.create_trail_btn)
        
        self.clear_selected_trail_btn = QtWidgets.QPushButton("❌ Xóa Trail của vật thể chọn")
        self.clear_selected_trail_btn.setFixedHeight(30)
        self.clear_selected_trail_btn.clicked.connect(self.on_clear_selected_trails)
        at_btn_layout.addWidget(self.clear_selected_trail_btn)
        
        self.clear_all_trails_btn = QtWidgets.QPushButton("🗑️ Xóa tất cả Arc Trails")
        self.clear_all_trails_btn.setFixedHeight(30)
        self.clear_all_trails_btn.clicked.connect(self.on_clear_all_trails)
        at_btn_layout.addWidget(self.clear_all_trails_btn)
        
        tab4_layout.addLayout(at_btn_layout)
        
        # Mẹo sử dụng
        at_info_label = QtWidgets.QLabel("💡 Mẹo: Đường dẫn tĩnh này chạy mượt 100% không bị lag.\nNhấp lại 'Vẽ Arc Trail' để cập nhật khi đổi animation.")
        at_info_label.setAlignment(QtCore.Qt.AlignCenter)
        at_info_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        tab4_layout.addWidget(at_info_label)
        
        tab4_layout.addStretch()
        
        # --- TAB 5: WORLD BAKE ---
        tab5 = QtWidgets.QWidget()
        tab5_layout = QtWidgets.QVBoxLayout(tab5)
        tab5_layout.setContentsMargins(6, 10, 6, 6)
        tab5_layout.setSpacing(12)
        
        # Tiêu đề Tab 5
        wb_title = QtWidgets.QLabel("🌍 ANIMEOW WORLD BAKE")
        wb_title.setAlignment(QtCore.Qt.AlignCenter)
        wb_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        tab5_layout.addWidget(wb_title)
        
        # Khối cấu hình World Bake
        wb_group = QtWidgets.QGroupBox("Cấu hình World Bake")
        wb_layout = QtWidgets.QGridLayout(wb_group)
        wb_layout.setContentsMargins(8, 12, 8, 8)
        wb_layout.setSpacing(10)
        
        # Kênh nướng
        wb_layout.addWidget(QtWidgets.QLabel("Kênh nướng (Channels):"), 0, 0)
        self.wb_channels_combo = QtWidgets.QComboBox()
        self.wb_channels_combo.addItems(["Translate & Rotate (Both)", "Translate Only", "Rotate Only"])
        wb_layout.addWidget(self.wb_channels_combo, 0, 1)
        
        # Step
        wb_layout.addWidget(QtWidgets.QLabel("Bước nhảy (Step):"), 1, 0)
        self.wb_step_spin = QtWidgets.QSpinBox()
        self.wb_step_spin.setRange(1, 100)
        self.wb_step_spin.setValue(1)
        wb_layout.addWidget(self.wb_step_spin, 1, 1)
        
        # Smart clean
        self.wb_smart_clean_cb = QtWidgets.QCheckBox("Smart Clean (Bảo toàn keyframe cực trị và khớp lưới)")
        self.wb_smart_clean_cb.setChecked(True)
        wb_layout.addWidget(self.wb_smart_clean_cb, 2, 0, 1, 2)
        
        tab5_layout.addWidget(wb_group)
        
        # Các nút bấm hành động
        wb_btn_layout = QtWidgets.QVBoxLayout()
        wb_btn_layout.setSpacing(8)
        
        self.wb_to_loc_btn = QtWidgets.QPushButton("🚀 Bake sang Locator (To Locator)")
        self.wb_to_loc_btn.setObjectName("accent_btn")
        self.wb_to_loc_btn.setFixedHeight(38)
        self.wb_to_loc_btn.clicked.connect(self.on_world_bake_to_locator)
        wb_btn_layout.addWidget(self.wb_to_loc_btn)
        
        self.wb_from_loc_btn = QtWidgets.QPushButton("🎬 Bake ngược về Vật thể (From Locator)")
        self.wb_from_loc_btn.setFixedHeight(38)
        self.wb_from_loc_btn.clicked.connect(self.on_world_bake_from_locator)
        wb_btn_layout.addWidget(self.wb_from_loc_btn)
        
        tab5_layout.addLayout(wb_btn_layout)
        
        # Hướng dẫn nhỏ
        wb_info_label = QtWidgets.QLabel("💡 Mẹo: Chế độ Smart Clean sẽ giúp nướng thưa\n(2s, 3s...) mà không bị mất đi các pose chính/cực trị của bạn.")
        wb_info_label.setAlignment(QtCore.Qt.AlignCenter)
        wb_info_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        tab5_layout.addWidget(wb_info_label)
        
        tab5_layout.addStretch()
        
        # Thêm các tab vào Widget
        self.tab_widget.addTab(tab1, "🔗 Smart Link")
        self.tab_widget.addTab(tab2, "🛠️ Quick Tools")
        self.tab_widget.addTab(tab3, "🎬 Playblast")
        self.tab_widget.addTab(tab4, "📈 Arc Tracker")
        self.tab_widget.addTab(tab5, "🌍 World Bake")

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
            
        if cmds.optionVar(exists=self.OP_PB_MULTI_CAM):
            self.multi_cam_cb.setChecked(bool(cmds.optionVar(query=self.OP_PB_MULTI_CAM)))
            
        if cmds.optionVar(exists=self.OP_PB_MULTI_CAMS_LIST):
            saved_cams = cmds.optionVar(query=self.OP_PB_MULTI_CAMS_LIST).split(";")
            for i in range(self.camera_list_widget.count()):
                item = self.camera_list_widget.item(i)
                if item.text() in saved_cams:
                    item.setCheckState(QtCore.Qt.Checked)
                    
        # Arc Tracker Settings
        if cmds.optionVar(exists=self.OP_AT_SHOW_TICKS):
            self.at_show_ticks_cb.setChecked(bool(cmds.optionVar(query=self.OP_AT_SHOW_TICKS)))
        if cmds.optionVar(exists=self.OP_AT_SHOW_KEYS):
            self.at_show_keys_cb.setChecked(bool(cmds.optionVar(query=self.OP_AT_SHOW_KEYS)))
        if cmds.optionVar(exists=self.OP_AT_TICK_SIZE):
            self.at_tick_size_spin.setValue(cmds.optionVar(query=self.OP_AT_TICK_SIZE))
            
        # World Bake Settings
        if cmds.optionVar(exists=self.OP_WB_CHANNELS):
            fmt = cmds.optionVar(query=self.OP_WB_CHANNELS)
            idx = self.wb_channels_combo.findText(fmt)
            if idx >= 0:
                self.wb_channels_combo.setCurrentIndex(idx)
        if cmds.optionVar(exists=self.OP_WB_STEP):
            self.wb_step_spin.setValue(cmds.optionVar(query=self.OP_WB_STEP))
        if cmds.optionVar(exists=self.OP_WB_SMART_CLEAN):
            self.wb_smart_clean_cb.setChecked(bool(cmds.optionVar(query=self.OP_WB_SMART_CLEAN)))
            
        # Round Tool Settings
        if cmds.optionVar(exists=self.OP_RT_PRECISION):
            self.round_precision_combo.setCurrentIndex(cmds.optionVar(query=self.OP_RT_PRECISION))
        if cmds.optionVar(exists=self.OP_RT_TARGET):
            self.round_target_combo.setCurrentIndex(cmds.optionVar(query=self.OP_RT_TARGET))

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
        cmds.optionVar(intValue=(self.OP_PB_MULTI_CAM, int(self.multi_cam_cb.isChecked())))
        
        checked_cams = []
        for i in range(self.camera_list_widget.count()):
            item = self.camera_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                checked_cams.append(item.text())
        cmds.optionVar(stringValue=(self.OP_PB_MULTI_CAMS_LIST, ";".join(checked_cams)))
        
        # Arc Tracker Settings
        cmds.optionVar(intValue=(self.OP_AT_SHOW_TICKS, int(self.at_show_ticks_cb.isChecked())))
        cmds.optionVar(intValue=(self.OP_AT_SHOW_KEYS, int(self.at_show_keys_cb.isChecked())))
        cmds.optionVar(floatValue=(self.OP_AT_TICK_SIZE, self.at_tick_size_spin.value()))
        
        # World Bake Settings
        cmds.optionVar(stringValue=(self.OP_WB_CHANNELS, self.wb_channels_combo.currentText()))
        cmds.optionVar(intValue=(self.OP_WB_STEP, self.wb_step_spin.value()))
        cmds.optionVar(intValue=(self.OP_WB_SMART_CLEAN, int(self.wb_smart_clean_cb.isChecked())))
        
        # Round Tool Settings
        cmds.optionVar(intValue=(self.OP_RT_PRECISION, self.round_precision_combo.currentIndex()))
        cmds.optionVar(intValue=(self.OP_RT_TARGET, self.round_target_combo.currentIndex()))

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
        path = ensure_scripts_2022_path()
        if not path:
            return
            
        tween_mel_path = os.path.join(path, "tweenMachine.mel").replace("\\", "/")
        if not os.path.exists(tween_mel_path):
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không tìm thấy file tweenMachine.mel tại:\n%s" % tween_mel_path)
            return
            
        try:
            import maya.mel as mel
            if cmds.window("tweenMachineWin", exists=True):
                cmds.deleteUI("tweenMachineWin")
                print("[TweenMachine] Da dong Tween Machine.")
            else:
                mel.eval('source "%s"; tweenMachine;' % tween_mel_path)
                print("[TweenMachine] Da mo Tween Machine.")
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

    def on_toggle_multi_cam(self, state):
        is_multi = (state == QtCore.Qt.Checked)
        self.camera_combo.setVisible(not is_multi)
        self.refresh_cam_btn.setVisible(not is_multi)
        self.camera_list_widget.setVisible(is_multi)

    def on_refresh_cameras(self):
        """Làm mới danh sách camera trong scene"""
        previously_checked = []
        for i in range(self.camera_list_widget.count()):
            item = self.camera_list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                previously_checked.append(item.text())
                
        current_cam = self.camera_combo.currentText()
        self.camera_combo.clear()
        self.camera_list_widget.clear()
        
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
        
        # Nạp Combobox
        self.camera_combo.addItems(sorted_cams)
        
        # Nạp ListWidget checkable
        for cam in sorted_cams:
            item = QtWidgets.QListWidgetItem(cam)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if cam in previously_checked:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.camera_list_widget.addItem(item)
            
        idx = self.camera_combo.findText(current_cam)
        if idx >= 0:
            self.camera_combo.setCurrentIndex(idx)

    def on_run_playblast(self):
        """Thực thi quay thử Playblast (hỗ trợ camera đơn hoặc hàng loạt camera)"""
        self.save_settings()
        
        fmt_text = self.pb_format_combo.currentText()
        format_ext = "avi" if "avi" in fmt_text.lower() else "qt"
        
        width = self.pb_width_spin.value()
        height = self.pb_height_spin.value()
        percent = self.pb_scale_spin.value()
        viewer = self.pb_viewer_cb.isChecked()
        overwrite = self.pb_overwrite_cb.isChecked()
        
        is_multi = self.multi_cam_cb.isChecked()
        
        target_cameras = []
        if is_multi:
            for i in range(self.camera_list_widget.count()):
                item = self.camera_list_widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    target_cameras.append(item.text())
            if not target_cameras:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một camera trong danh sách để quay hàng loạt!")
                return
        else:
            single_cam = self.camera_combo.currentText()
            if not single_cam:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy camera khả dụng!")
                return
            target_cameras = [single_cam]
            
        # Xác nhận nếu xuất nhiều camera cùng lúc
        if len(target_cameras) > 1:
            res = QtWidgets.QMessageBox.question(
                self, "Xác nhận quay hàng loạt",
                "Bạn có chắc chắn muốn chạy Playblast cho %d camera đã chọn?" % len(target_cameras),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if res == QtWidgets.QMessageBox.No:
                return

        success_files = []
        failed_cameras = []
        
        # Hiển thị QProgressDialog để báo cáo tiến trình
        progress_dialog = QtWidgets.QProgressDialog("Đang xuất Playblast...", "Hủy", 0, len(target_cameras), self)
        progress_dialog.setWindowTitle("Playblast Hàng Loạt")
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        
        pbm = playblast.PlayblastManager()
        
        for idx, cam in enumerate(target_cameras):
            if progress_dialog.wasCanceled():
                break
                
            progress_dialog.setLabelText("Đang quay camera: %s (%d/%d)..." % (cam, idx + 1, len(target_cameras)))
            progress_dialog.setValue(idx)
            QtCore.QCoreApplication.processEvents()
            
            try:
                # Nếu nhiều camera, chỉ mở video cuối cùng bằng trình phát để tránh mở hàng loạt tab VLC làm đơ máy
                should_view = viewer if len(target_cameras) == 1 else (viewer and (idx == len(target_cameras) - 1))
                
                output_file = pbm.run_playblast(
                    format_ext=format_ext,
                    percent=percent,
                    width=width,
                    height=height,
                    camera=cam,
                    viewer=should_view,
                    overwrite=overwrite
                )
                success_files.append(output_file)
            except Exception as e:
                failed_cameras.append((cam, playblast.exception_to_unicode(e)))
                
        progress_dialog.setValue(len(target_cameras))
        
        # Báo cáo kết quả
        if not failed_cameras:
            if len(target_cameras) == 1:
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    "Đã xuất Playblast thành công cho camera: %s!\nĐường dẫn:\n%s" % (target_cameras[0], success_files[0])
                )
            else:
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    "Đã hoàn thành xuất Playblast hàng loạt cho %d camera thành công!\nCác tệp được lưu trong thư mục 'mov'." % len(success_files)
                )
        else:
            err_msg = "Kết quả xuất Playblast:\n\n"
            if success_files:
                err_msg += "✅ Thành công %d camera.\n" % len(success_files)
            err_msg += "❌ Thất bại %d camera:\n" % len(failed_cameras)
            for f_cam, f_err in failed_cameras:
                err_msg += "  + %s: %s\n" % (f_cam, f_err)
            QtWidgets.QMessageBox.warning(self, "Hoàn thành có lỗi", err_msg)

    def on_launch_worldbake(self):
        ensure_scripts_2022_path()
        try:
            is_open = False
            for win in ['ml_worldBake', 'ml_worldBakeWin']:
                if cmds.window(win, exists=True):
                    cmds.deleteUI(win)
                    is_open = True
                    print("[WorldBake] Da dong World Bake.")
                    
            if not is_open:
                import ml_worldBake
                import importlib
                importlib.reload(ml_worldBake)
                ml_worldBake.ui()
                print("[WorldBake] Da mo World Bake.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể chạy World Bake:\n%s" % str(e))

    def on_create_arc_trail(self):
        """Tạo Arc Trail cho các vật thể đang chọn"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một vật thể để tạo Arc Trail!")
            return
            
        self.save_settings()
        
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        show_ticks = self.at_show_ticks_cb.isChecked()
        show_keys = self.at_show_keys_cb.isChecked()
        tick_size = self.at_tick_size_spin.value()
        
        tracker = arc_tracker.ArcTracker()
        try:
            for obj in sel:
                tracker.create_trail(
                    obj=obj,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    show_ticks=show_ticks,
                    show_keys=show_keys,
                    tick_size=tick_size
                )
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã tạo Arc Trail thành công cho %d vật thể!" % len(sel)
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi vẽ Trail",
                "Lỗi xảy ra khi vẽ Arc Trail:\n%s" % str(e)
            )
            
    def on_clear_selected_trails(self):
        """Xóa trail của các vật thể đang chọn"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn vật thể muốn xóa Arc Trail!")
            return
            
        tracker = arc_tracker.ArcTracker()
        tracker.clear_selected_trails(sel)
        QtWidgets.QMessageBox.information(self, "Thành công", "Đã xóa Arc Trail của các vật thể được chọn!")

    def on_clear_all_trails(self):
        """Xóa sạch toàn bộ các Arc Trails"""
        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa sạch toàn bộ các Arc Trails trong scene?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        tracker = arc_tracker.ArcTracker()
        tracker.clear_all_trails()
        QtWidgets.QMessageBox.information(self, "Thành công", "Đã xóa sạch toàn bộ Arc Trails!")

    def on_world_bake_to_locator(self):
        """Bake vật thể được chọn sang Locator thế giới"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một vật thể để tạo World Locator!")
            return
            
        self.save_settings()
        
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        step = self.wb_step_spin.value()
        smart_clean = self.wb_smart_clean_cb.isChecked()
        
        idx = self.wb_channels_combo.currentIndex()
        channels = ['both', 'translate', 'rotate'][idx]
        
        wbm = world_bake.WorldBakeManager()
        
        success_locs = []
        try:
            for obj in sel:
                loc = wbm.bake_to_locator(
                    obj=obj,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    step=step,
                    smart_clean=smart_clean,
                    channels=channels
                )
                success_locs.append(loc)
                
            cmds.select(success_locs)
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã bake thành công %d vật thể sang Locator không gian thế giới!\nCác locator mới: %s" % (
                    len(sel), ", ".join(success_locs))
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi World Bake",
                "Lỗi xảy ra khi Bake sang Locator:\n%s" % world_bake.exception_to_unicode(e)
            )

    def on_world_bake_from_locator(self):
        """Bake ngược từ Locator trở về vật thể gốc"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Locator hoặc vật thể gốc để Bake ngược trở lại!")
            return
            
        self.save_settings()
        
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        step = self.wb_step_spin.value()
        smart_clean = self.wb_smart_clean_cb.isChecked()
        
        wbm = world_bake.WorldBakeManager()
        
        success_objs = []
        try:
            for item in sel:
                obj = wbm.bake_from_locator(
                    locator_or_obj=item,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    step=step,
                    smart_clean=smart_clean
                )
                success_objs.append(obj)
                
            cmds.select(success_objs)
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã bake ngược thành công từ Locator về %d vật thể gốc!" % len(success_objs)
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi World Bake",
                "Lỗi xảy ra khi Bake ngược trở về:\n%s" % world_bake.exception_to_unicode(e)
            )

    def on_toggle_graph_editor(self):
        """Bật/Tắt Graph Editor"""
        try:
            import maya.mel as mel
            if cmds.window("graphEditor1Window", exists=True):
                cmds.deleteUI("graphEditor1Window", window=True)
                print("[Toolboard] Da dong Graph Editor.")
            else:
                mel.eval("GraphEditor;")
                print("[Toolboard] Da mo Graph Editor.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể bật/tắt Graph Editor:\n%s" % str(e))

    def on_toggle_reference_editor(self):
        """Bật/Tắt Reference Editor"""
        try:
            import maya.mel as mel
            if cmds.window("referenceEditorPanel1Window", exists=True):
                cmds.deleteUI("referenceEditorPanel1Window", window=True)
                print("[Toolboard] Da dong Reference Editor.")
            else:
                mel.eval("ReferenceEditor;")
                print("[Toolboard] Da mo Reference Editor.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể bật/tắt Reference Editor:\n%s" % str(e))

    def on_save_increment(self):
        """Lưu file tăng dần (Save Increment)"""
        try:
            import maya.mel as mel
            mel.eval("IncrementAndSave;")
            print("[Toolboard] Da thuc hien Save Increment.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể thực hiện Save Increment:\n%s" % str(e))

    def on_save_up_version(self):
        """Lưu file nâng Version (ví dụ: từ _v01.0001 thành _v02)"""
        import os
        import re
        
        scene_path = cmds.file(q=True, sceneName=True)
        if not scene_path:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Scene chưa được lưu! Hãy lưu file trước khi nâng Version.")
            return
            
        scene_dir, scene_file = os.path.split(scene_path)
        file_name, ext = os.path.splitext(scene_file)
        
        # Regex tìm version _v01, _v02,... hoặc .v01, .v02...
        version_pattern = re.compile(r'([_\.]v)(\d+)(.*)', re.IGNORECASE)
        
        match = version_pattern.search(file_name)
        if match:
            prefix = file_name[:match.start()]
            v_prefix = match.group(1) # '_v' hoặc '.v'
            v_num_str = match.group(2) # '01', '1', '001'
            
            # Tăng số version lên 1
            new_v_num = int(v_num_str) + 1
            # Đệm số 0 tương ứng độ dài cũ (v01 -> v02)
            new_v_num_str = str(new_v_num).zfill(len(v_num_str))
            
            # Bỏ qua phần hậu tố số increment phía sau (ví dụ: .0001)
            new_file_name = prefix + v_prefix + new_v_num_str + ext
        else:
            # Nếu không có _vXX nhưng có hậu tố increment (ví dụ: .0005)
            inc_pattern = re.compile(r'\.(\d{3,5})$')
            inc_match = inc_pattern.search(file_name)
            if inc_match:
                prefix = file_name[:inc_match.start()]
                new_file_name = prefix + "_v02" + ext
            else:
                # Không tìm thấy version và increment
                new_file_name = file_name + "_v02" + ext
                
        new_scene_path = os.path.join(scene_dir, new_file_name).replace('\\', '/')
        
        # Xác nhận với người dùng trước khi lưu nâng version
        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận nâng Version",
            "Bạn có muốn nâng version hiện tại lên phiên bản mới không?\nTên file mới:\n%s" % new_file_name,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        try:
            cmds.file(rename=new_scene_path)
            file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
            cmds.file(save=True, type=file_type)
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã nâng version thành công!\nTên file mới: %s" % new_file_name
            )
            print("[Toolboard] Da nang version thanh cong: %s" % new_file_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi",
                "Lỗi xảy ra khi nâng version:\n%s" % str(e)
            )

    def on_clean_folder(self):
        """Dọn dẹp thư mục chứa file: giữ lại 5 version mới nhất, chuyển các file cũ hơn vào thư mục Old"""
        import os
        import re
        import shutil
        
        # 1. Lấy thông tin file hiện tại
        scene_path = cmds.file(q=True, sceneName=True)
        if not scene_path:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Scene hiện tại chưa được lưu trên đĩa! Hãy lưu file trước khi thực hiện dọn dẹp.")
            return
            
        scene_dir, scene_file = os.path.split(scene_path)
        file_name, ext = os.path.splitext(scene_file)
        
        # 2. Rút trích phần tên gốc (root prefix) bằng cách bỏ version (_v01) và increment (.0001)
        root_prefix = re.sub(r'([_\.]v\d+)?(\.\d{3,5})?(_org)?$', '', file_name, flags=re.IGNORECASE)
        
        # Quét các file trong cùng thư mục
        try:
            files_in_dir = os.listdir(scene_dir)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể truy cập thư mục scene:\n%s" % str(e))
            return
            
        # Lọc các file bắt đầu bằng root_prefix và có đuôi .ma/.mb
        matched_files = []
        for f in files_in_dir:
            f_path = os.path.join(scene_dir, f).replace('\\', '/')
            if os.path.isfile(f_path) and f.lower().startswith(root_prefix.lower()) and f.lower().endswith(('.ma', '.mb')):
                mtime = os.path.getmtime(f_path)
                matched_files.append((f, f_path, mtime))
                
        if not matched_files:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Không tìm thấy file nào khớp trong thư mục để dọn dẹp!")
            return
            
        # Sắp xếp các file theo mtime giảm dần (mới nhất lên đầu)
        matched_files.sort(key=lambda x: x[2], reverse=True)
        
        # Xác định 5 tệp mới nhất để giữ lại
        keep_filenames = [x[0] for x in matched_files[:5]]
        
        # Đảm bảo tệp hiện tại đang mở trong Maya LUÔN LUÔN được giữ lại (tránh mất file handle)
        if scene_file not in keep_filenames:
            keep_filenames.append(scene_file)
            
        # Các tệp cũ cần di chuyển
        files_to_move = [x for x in matched_files if x[0] not in keep_filenames]
        
        if not files_to_move:
            QtWidgets.QMessageBox.information(
                self, "Thông báo", 
                "Thư mục hiện tại đang rất sạch sẽ!\nChỉ có %d tệp khớp và toàn bộ đã được giữ lại (tối đa 5 tệp gần nhất)." % len(matched_files)
            )
            return
            
        # Hỏi ý kiến người dùng trước khi dọn dẹp
        confirm_msg = "Bạn có muốn dọn dẹp thư mục này không?\n\n"
        confirm_msg += "- Giữ lại %d tệp mới nhất (bao gồm file đang mở).\n" % len(keep_filenames)
        confirm_msg += "- Di chuyển %d tệp cũ hơn vào thư mục 'Old'.\n\nDanh sách file sẽ di chuyển:\n" % len(files_to_move)
        for f, _, _ in files_to_move[:10]:
            confirm_msg += "  + %s\n" % f
        if len(files_to_move) > 10:
            confirm_msg += "  + ... và %d file khác.\n" % (len(files_to_move) - 10)
            
        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận dọn dẹp thư mục",
            confirm_msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        # 3. Tạo thư mục Old và di chuyển các file cũ
        old_dir = os.path.join(scene_dir, "Old").replace('\\', '/')
        if not os.path.exists(old_dir):
            try:
                os.makedirs(old_dir)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Lỗi tạo thư mục", "Không thể tạo thư mục 'Old':\n%s" % str(e))
                return
                
        moved_count = 0
        error_count = 0
        error_files = []
        
        for f, f_path, _ in files_to_move:
            dest_path = os.path.join(old_dir, f).replace('\\', '/')
            try:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(f_path, dest_path)
                moved_count += 1
            except Exception as ex:
                error_count += 1
                error_files.append((f, str(ex)))
                
        # 4. Hiển thị báo cáo kết quả
        if error_count == 0:
            QtWidgets.QMessageBox.information(
                self, "Dọn dẹp thành công",
                "Đã di chuyển thành công %d tệp cũ vào thư mục 'Old'!\nThư mục hiện tại chỉ giữ lại 5 tệp mới nhất." % moved_count
            )
        else:
            warn_msg = "Dọn dẹp hoàn thành một phần:\n"
            warn_msg += "- Di chuyển thành công: %d file.\n" % moved_count
            warn_msg += "- Thất bại: %d file.\n\nChi tiết lỗi:\n" % error_count
            QtWidgets.QMessageBox.warning(self, "Hoàn thành có lỗi", warn_msg)

    def on_round_values(self):
        """Làm tròn số thuộc tính hoặc keyframe"""
        self.save_settings()
        
        # Lấy độ chính xác: 0 = số nguyên, 1 = 1 chữ số, 2 = 2 chữ số thập phân
        precision = self.round_precision_combo.currentIndex()
        
        # Lấy môi trường đích: channel_box hoặc graph_editor
        target_idx = self.round_target_combo.currentIndex()
        target = 'channel_box' if target_idx == 0 else 'graph_editor'
        
        # Bọc trong một khối Undo chunk để animator có thể Ctrl + Z hoàn tác nhanh
        cmds.undoInfo(openChunk=True)
        try:
            success, msg = round_tool.round_selected_values(precision, target)
            if success:
                # Hiển thị thông báo góc dưới Maya
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Làm tròn số",
                "Lỗi xảy ra khi thực hiện làm tròn số:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)


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
