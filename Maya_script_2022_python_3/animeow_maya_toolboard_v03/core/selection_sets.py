# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import json
import maya.cmds as cmds
import maya.mel as mel

# Safe import for PySide2 and PySide6 compatibility
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui


class MayaUndoChunk(object):
    """Context manager giúp nhóm tất cả hành động vào một khối undo duy nhất trong Maya"""
    def __enter__(self):
        cmds.undoInfo(openChunk=True, chunkName="AnimeowSelectionSets")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)


class SelectionSetsIcons(object):
    """Vẽ icon mắt ẩn/hiện vector bằng QPainter phong cách AnimBot"""
    
    COLOR_ACCENT = QtGui.QColor("#00BCD4")  # Cyan chủ đạo
    COLOR_MUTED = QtGui.QColor("#888888")   # Màu xám mờ cho trạng thái ẩn
    
    @staticmethod
    def _create_pixmap(draw_func, size=16, color=None):
        if color is None:
            color = SelectionSetsIcons.COLOR_ACCENT
        pix = QtGui.QPixmap(size, size)
        pix.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        draw_func(p, QtCore.QRectF(2, 2, size - 4, size - 4), color)
        p.end()
        return pix

    @classmethod
    def make_icon(cls, draw_func, color=None):
        return QtGui.QIcon(cls._create_pixmap(draw_func, color=color))

    @staticmethod
    def _draw_eye_open(p, r, c):
        p.setPen(QtGui.QPen(c, 1.5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.center().y())
        path.quadTo(r.center().x(), r.top() + 1, r.right(), r.center().y())
        path.quadTo(r.center().x(), r.bottom() - 1, r.left(), r.center().y())
        p.drawPath(path)
        p.setBrush(c)
        p.drawEllipse(r.center(), 2.5, 2.5)

    @staticmethod
    def _draw_eye_closed(p, r, c):
        c = SelectionSetsIcons.COLOR_MUTED
        p.setPen(QtGui.QPen(c, 1.5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.center().y() - 1)
        path.quadTo(r.center().x(), r.bottom() - 2, r.right(), r.center().y() - 1)
        p.drawPath(path)
        cx, cy = r.center().x(), r.center().y()
        p.drawLine(cx - 3, cy, cx - 5, cy + 3)
        p.drawLine(cx, cy + 1, cx, cy + 5)
        p.drawLine(cx + 3, cy, cx + 5, cy + 3)

    @classmethod
    def icon_eye(cls, open_state):
        return cls.make_icon(cls._draw_eye_open if open_state else cls._draw_eye_closed, None if open_state else cls.COLOR_MUTED)


class SelectionSetsManagerUI(QtWidgets.QWidget):
    """Giao diện quản lý Selection Sets phân cấp (Hierarchical Tree) phong cách AnimBot"""
    
    def __init__(self, parent=None):
        super(SelectionSetsManagerUI, self).__init__(parent=parent)
        self.sets_list = []
        self.init_ui()
        self.refresh_sets()

    def init_ui(self):
        # Layout chính
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(6)

        # Tiêu đề Tab
        title_lbl = QtWidgets.QLabel("SELECTION SETS MANAGER")
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet("font-weight: bold; font-size: 11px; color: #00BCD4; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # Thanh tìm kiếm và Làm mới
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.setSpacing(4)
        
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm selection set...")
        self.search_input.textChanged.connect(self.filter_sets)
        search_layout.addWidget(self.search_input)

        self.refresh_btn = QtWidgets.QPushButton("🔄")
        self.refresh_btn.setFixedSize(24, 24)
        self.refresh_btn.setToolTip("Làm mới danh sách Sets")
        self.refresh_btn.clicked.connect(self.refresh_sets)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)

        # Cây hiển thị các Selection Sets (Cột 0: Tên Set (cha/con), Cột 1: Visible, Cột 2: Số Lượng)
        self.sets_tree = QtWidgets.QTreeWidget()
        self.sets_tree.setColumnCount(3)
        self.sets_tree.setHeaderLabels(["Tên Set", "👁", "Số Lượng"])
        self.sets_tree.setAlternatingRowColors(True)
        self.sets_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sets_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # Cấu hình kích thước cột (Cột 0 co giãn chính, cột 1 và 2 gọn gàng ở góc)
        self.sets_tree.header().setStretchLastSection(False)
        self.sets_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.sets_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.sets_tree.setColumnWidth(1, 30)
        self.sets_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        
        # Áp dụng stylesheet đồng bộ với tông màu Cyan Accent của toolboard
        self.sets_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #4A4A4A;
                background-color: #2E2E2E;
                color: #D4D4D4;
                border-radius: 3px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #3A3A3A;
            }
            QTreeWidget::item:hover {
                background-color: #3D3D3D;
                color: #00BCD4;
            }
            QTreeWidget::item:selected {
                background-color: #00838F;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #3A3A3A;
                color: #00BCD4;
                border: 1px solid #4A4A4A;
                font-weight: bold;
                padding: 3px;
                font-size: 11px;
            }
        """)
        
        # Sự kiện
        self.sets_tree.itemDoubleClicked.connect(self.on_double_click_set)
        self.sets_tree.itemClicked.connect(self.on_item_clicked)
        self.sets_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sets_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.sets_tree)

        # Group Thao tác Vùng chọn (Selection)
        sel_ops_group = QtWidgets.QGroupBox("Thao tác Vùng chọn (Selection)")
        sel_ops_layout = QtWidgets.QVBoxLayout(sel_ops_group)
        sel_ops_layout.setContentsMargins(6, 10, 6, 6)
        sel_ops_layout.setSpacing(6)

        # Nút Chọn thành viên chính (Select)
        self.select_members_btn = QtWidgets.QPushButton("Chọn thành viên (Select)")
        self.select_members_btn.setObjectName("accent_btn")
        self.select_members_btn.setFixedHeight(28)
        self.select_members_btn.setToolTip("Chọn tất cả các đối tượng trong set đang chọn (thay thế vùng chọn hiện tại)")
        self.select_members_btn.clicked.connect(lambda: self.operate_on_members("select"))
        sel_ops_layout.addWidget(self.select_members_btn)

        # Dòng thao tác Cộng / Trừ / Giao
        sel_sub_layout = QtWidgets.QHBoxLayout()
        sel_sub_layout.setSpacing(4)

        self.add_sel_btn = QtWidgets.QPushButton("+ Cộng thêm")
        self.add_sel_btn.setToolTip("Cộng thêm các thành viên của set vào vùng chọn hiện tại")
        self.add_sel_btn.clicked.connect(lambda: self.operate_on_members("add"))
        sel_sub_layout.addWidget(self.add_sel_btn)

        self.sub_sel_btn = QtWidgets.QPushButton("- Bỏ bớt")
        self.sub_sel_btn.setToolTip("Loại bỏ các thành viên của set khỏi vùng chọn hiện tại")
        self.sub_sel_btn.clicked.connect(lambda: self.operate_on_members("remove"))
        sel_sub_layout.addWidget(self.sub_sel_btn)

        self.intersect_sel_btn = QtWidgets.QPushButton("∩ Giao")
        self.intersect_sel_btn.setToolTip("Giao các thành viên của set với vùng chọn hiện tại")
        self.intersect_sel_btn.clicked.connect(lambda: self.operate_on_members("intersect"))
        sel_sub_layout.addWidget(self.intersect_sel_btn)

        sel_ops_layout.addLayout(sel_sub_layout)

        # Hàng nút Grow / Shrink / Toggle Mode vùng chọn
        grow_shrink_layout = QtWidgets.QHBoxLayout()
        grow_shrink_layout.setSpacing(4)

        self.grow_sel_btn = QtWidgets.QPushButton("Grow (>)")
        self.grow_sel_btn.setToolTip("Mở rộng vùng chọn component hiện tại (Shift + >)")
        self.grow_sel_btn.clicked.connect(self.grow_selection)
        grow_shrink_layout.addWidget(self.grow_sel_btn)

        self.shrink_sel_btn = QtWidgets.QPushButton("Shrink (<)")
        self.shrink_sel_btn.setToolTip("Thu nhỏ vùng chọn component hiện tại (Shift + <)")
        self.shrink_sel_btn.clicked.connect(self.shrink_selection)
        grow_shrink_layout.addWidget(self.shrink_sel_btn)

        self.toggle_mode_btn = QtWidgets.QPushButton("Toggle Mode (F8)")
        self.toggle_mode_btn.setToolTip("Chuyển đổi qua lại giữa chế độ chọn Object và Component (F8)")
        self.toggle_mode_btn.clicked.connect(self.toggle_select_mode)
        grow_shrink_layout.addWidget(self.toggle_mode_btn)

        sel_ops_layout.addLayout(grow_shrink_layout)

        layout.addWidget(sel_ops_group)

        # Group Quản lý Thành viên Set (Membership)
        set_ops_group = QtWidgets.QGroupBox("Quản lý Thành viên Set (Membership)")
        set_ops_layout = QtWidgets.QHBoxLayout(set_ops_group)
        set_ops_layout.setContentsMargins(6, 10, 6, 6)
        set_ops_layout.setSpacing(4)

        self.add_to_set_btn = QtWidgets.QPushButton("Thêm vào Set")
        self.add_to_set_btn.setToolTip("Thêm các đối tượng đang chọn trong Viewport vào Set đang chọn")
        self.add_to_set_btn.clicked.connect(self.add_selected_to_set)
        set_ops_layout.addWidget(self.add_to_set_btn)

        self.remove_from_set_btn = QtWidgets.QPushButton("Xóa khỏi Set")
        self.remove_from_set_btn.setToolTip("Xóa các đối tượng đang chọn trong Viewport khỏi Set đang chọn")
        self.remove_from_set_btn.clicked.connect(self.remove_selected_from_set)
        set_ops_layout.addWidget(self.remove_from_set_btn)

        layout.addWidget(set_ops_group)

        # Hàng nút quản lý Set (Create, Rename, Delete)
        mgmt_layout = QtWidgets.QHBoxLayout()
        mgmt_layout.setSpacing(4)

        self.create_set_btn = QtWidgets.QPushButton("Tạo Set Mới")
        self.create_set_btn.setToolTip("Tạo selection set mới. Nếu chọn sẵn 1 set cha trong bảng, set mới sẽ tự động trở thành con.")
        self.create_set_btn.clicked.connect(self.create_new_set)
        mgmt_layout.addWidget(self.create_set_btn)

        self.rename_set_btn = QtWidgets.QPushButton("Đổi Tên")
        self.rename_set_btn.setToolTip("Đổi tên Selection Set đang chọn")
        self.rename_set_btn.clicked.connect(self.rename_selected_set)
        mgmt_layout.addWidget(self.rename_set_btn)

        self.delete_set_btn = QtWidgets.QPushButton("Xóa Set")
        self.delete_set_btn.setToolTip("Xóa Selection Set đang chọn")
        self.delete_set_btn.clicked.connect(self.delete_selected_sets)
        mgmt_layout.addWidget(self.delete_set_btn)

        layout.addLayout(mgmt_layout)

        # Hàng nút Lưu / Tải Sets ra file ngoài (Export / Import)
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setSpacing(4)

        self.export_sets_btn = QtWidgets.QPushButton("Xuất File (Export)")
        self.export_sets_btn.setToolTip("Xuất các selection sets đã chọn ra file JSON")
        self.export_sets_btn.clicked.connect(self.export_selected_sets)
        file_layout.addWidget(self.export_sets_btn)

        self.import_sets_btn = QtWidgets.QPushButton("Nhập File (Import)")
        self.import_sets_btn.setToolTip("Nhập các selection sets từ file JSON kèm theo map Namespace tự động")
        self.import_sets_btn.clicked.connect(self.import_sets)
        file_layout.addWidget(self.import_sets_btn)

        layout.addLayout(file_layout)

    def ensure_parent_group(self):
        """Đảm bảo group cha Animeow_sets tồn tại dưới dạng một objectSet trống"""
        parent_set = "Animeow_sets"
        if not cmds.objExists(parent_set):
            try:
                cmds.sets(empty=True, name=parent_set)
            except Exception as e:
                print("Không thể tạo parent set Animeow_sets: %s" % e)
        return parent_set

    def create_tree_item(self, set_name):
        """Helper tạo QTreeWidgetItem cho set với con mắt ở cột 1 để tránh bị dịch chuyển do thụt dòng ở cột 0"""
        item = QtWidgets.QTreeWidgetItem()
        
        # Cột 0: Tên Set (Qt tự động vẽ mũi tên và thụt dòng ở cột 0 này)
        item.setText(0, set_name)
        
        # Cột 1: Visibility (Luôn căn lề thẳng đứng hoàn hảo vì nằm ở cột riêng)
        is_vis = self.is_set_visible(set_name)
        item.setIcon(1, SelectionSetsIcons.icon_eye(is_vis))
        item.setToolTip(1, "Click để ẩn/hiện toàn bộ thành viên của set (Ctrl+H / Shift+H)")
        
        # Cột 2: Số lượng thành viên
        members = cmds.sets(set_name, query=True) or []
        item.setText(2, str(len(members)))
        item.setTextAlignment(2, QtCore.Qt.AlignCenter)
        
        return item

    def refresh_sets(self):
        """Lọc và tải danh sách Selection Sets phân cấp trong scene hiện tại"""
        # Lưu các set đang được chọn để khôi phục lại sau khi làm mới
        selected_items = self.sets_tree.selectedItems()
        selected_names = [item.text(0) for item in selected_items if item]

        all_sets = cmds.ls(type="objectSet") or []
        self.sets_list = []
        for s in all_sets:
            # Ẩn group cha Animeow_sets chính khỏi bảng danh sách
            if s == "Animeow_sets":
                continue
            # Bỏ qua các shadingEngine/material sets (renderable sets)
            if cmds.sets(s, query=True, renderable=True):
                continue
            # Bỏ qua các system sets mặc định của Maya
            if s in ["defaultLightSet", "defaultObjectSet", "initialShadingGroup", "initialParticleSE"]:
                continue
            # Bỏ qua các set ẩn component tự động sinh ra bởi Maya
            if s == "defaultHideFaceDataSet" or s.endswith("HiddenFacesSet"):
                continue
            # Đảm bảo node type chính xác là objectSet (loại trừ character, partition kế thừa từ objectSet)
            if cmds.nodeType(s) != "objectSet":
                continue
            self.sets_list.append(s)

        # Xây dựng mối quan hệ cha-con dựa trên kết nối connection trong Maya
        parent_map = {}
        for s in self.sets_list:
            parents = cmds.listConnections(s + ".message", destination=True, source=False, type="objectSet") or []
            # Chỉ lấy parent nằm trong danh sách custom_sets và không phải Animeow_sets
            valid_parents = [p for p in parents if p in self.sets_list]
            if valid_parents:
                parent_map[s] = valid_parents[0]  # Lấy parent đầu tiên làm cha phân cấp chính

        # Sắp xếp theo bảng chữ cái
        self.sets_list.sort(key=lambda x: x.lower())
        
        # Làm sạch cây
        self.sets_tree.clear()
        
        # Bản đồ lưu các item đã được tạo
        tree_items = {}
        
        # Tìm các root sets (những set không có cha nằm trong sets_list)
        root_sets = [s for s in self.sets_list if s not in parent_map]
        child_sets = [s for s in self.sets_list if s in parent_map]
        
        # 1. Thêm các root sets lên Top Level
        for s in root_sets:
            item = self.create_tree_item(s)
            self.sets_tree.addTopLevelItem(item)
            tree_items[s] = item
            
        # 2. Thêm các con vào các cha tương ứng (lặp cho đến khi hết hoặc tránh cycle loop)
        max_loops = 10
        while child_sets and max_loops > 0:
            added_this_loop = []
            for s in child_sets:
                p = parent_map[s]
                if p in tree_items:
                    item = self.create_tree_item(s)
                    tree_items[p].addChild(item)
                    tree_items[s] = item
                    added_this_loop.append(s)
            
            if not added_this_loop:
                # Nếu phát hiện cycle loop hoặc cô lập, đẩy các con còn lại lên Top Level
                for s in child_sets:
                    item = self.create_tree_item(s)
                    self.sets_tree.addTopLevelItem(item)
                    tree_items[s] = item
                break
                
            for s in added_this_loop:
                child_sets.remove(s)
            max_loops -= 1

        # Tự động mở rộng toàn bộ cây
        self.sets_tree.expandAll()
        
        # Thực hiện lọc từ khóa nếu có nhập
        self.filter_sets()

        # Khôi phục trạng thái chọn hàng
        self.restore_selection_by_names(self.sets_tree.invisibleRootItem(), selected_names)

    def restore_selection_by_names(self, parent_item, selected_names):
        """Khôi phục trạng thái chọn dựa trên danh sách tên set"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.text(0) in selected_names:
                child.setSelected(True)
            self.restore_selection_by_names(child, selected_names)

    def filter_sets(self):
        """Lọc danh sách các set trong cây dựa trên từ khóa tìm kiếm"""
        filter_text = self.search_input.text().lower()
        self.filter_tree_item(self.sets_tree.invisibleRootItem(), filter_text)

    def filter_tree_item(self, parent_item, filter_text):
        """Duyệt đệ quy và ẩn các item không khớp từ khóa, giữ nguyên cha nếu có con khớp"""
        has_visible_child = False
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child_visible = self.filter_tree_item(child, filter_text)
            
            name_match = filter_text in child.text(0).lower()
            if name_match or child_visible:
                child.setHidden(False)
                has_visible_child = True
            else:
                child.setHidden(True)
                
        return has_visible_child

    def get_selected_sets(self):
        """Lấy danh sách tên các set đang chọn trong bảng"""
        selected_items = self.sets_tree.selectedItems()
        return [item.text(0) for item in selected_items if item]

    def is_set_visible(self, set_name):
        """Kiểm tra xem set có đang hiển thị không."""
        if cmds.objExists(set_name) and cmds.attributeQuery("set_visibility_state", node=set_name, exists=True):
            return bool(cmds.getAttr(set_name + ".set_visibility_state"))
            
        members = cmds.sets(set_name, query=True) or []
        if not members:
            return True
            
        dag_nodes = []
        for obj in members:
            if "." in obj:
                transform = obj.split(".")[0]
            else:
                transform = obj
            if cmds.objExists(transform) and cmds.attributeQuery("visibility", node=transform, exists=True):
                dag_nodes.append(transform)
                
        if not dag_nodes:
            return True
            
        hidden_count = sum(1 for node in dag_nodes if not cmds.getAttr(node + ".visibility"))
        if hidden_count == len(dag_nodes):
            return False
        return True

    def set_set_visibility(self, set_name, state):
        """Đặt trạng thái hiển thị cho các thành viên của set và các sub-sets con đệ quy"""
        self.set_set_visibility_recursive(set_name, state)

    def set_set_visibility_recursive(self, set_name, state, visited=None):
        if visited is None:
            visited = set()
        if set_name in visited:
            return
        visited.add(set_name)

        if not cmds.objExists(set_name):
            return

        members = cmds.sets(set_name, query=True) or []
        hideable_members = []
        child_sets = []

        for m in members:
            if not cmds.objExists(m):
                continue
            if cmds.nodeType(m) == "objectSet":
                child_sets.append(m)
            else:
                if "." in m:  # component
                    parent = m.split(".")[0]
                    if cmds.ls(parent, dag=True):
                        hideable_members.append(m)
                else:  # object
                    if cmds.ls(m, dag=True):
                        hideable_members.append(m)

        if hideable_members:
            try:
                if state:
                    cmds.showHidden(hideable_members)
                else:
                    cmds.hide(hideable_members)
            except Exception as e:
                print("Lỗi khi thay đổi visibility của set %s: %s" % (set_name, e))

        # Lưu trạng thái toggle vào thuộc tính tuỳ biến trên Set Node
        if cmds.objExists(set_name):
            if not cmds.attributeQuery("set_visibility_state", node=set_name, exists=True):
                try:
                    cmds.addAttr(set_name, longName="set_visibility_state", attributeType="bool", defaultValue=True)
                except Exception as e:
                    print("Không thể thêm attribute set_visibility_state vào set %s: %s" % (set_name, e))
            if cmds.attributeQuery("set_visibility_state", node=set_name, exists=True):
                try:
                    cmds.setAttr(set_name + ".set_visibility_state", state)
                except Exception as e:
                    print("Không thể lưu set_visibility_state cho set %s: %s" % (set_name, e))

        # Gọi đệ quy xuống các set con
        for cs in child_sets:
            self.set_set_visibility_recursive(cs, state, visited)

    def on_item_clicked(self, item, col):
        """Xử lý nhấp chuột vào cột visibility (cột 1)"""
        if col != 1:
            return
            
        clicked_set = item.text(0)
        selected_sets = self.get_selected_sets()
        
        if clicked_set in selected_sets:
            target_state = not self.is_set_visible(clicked_set)
            with MayaUndoChunk():
                for set_name in selected_sets:
                    self.set_set_visibility(set_name, target_state)
        else:
            target_state = not self.is_set_visible(clicked_set)
            with MayaUndoChunk():
                self.set_set_visibility(clicked_set, target_state)
                
        self.refresh_sets()

    def on_double_click_set(self, item, column):
        """Double-click chuột để chọn nhanh thành viên của set"""
        set_name = item.text(0)
        members = cmds.sets(set_name, query=True) or []
        if members:
            cmds.select(members, replace=True)
        else:
            cmds.select(clear=True)
            cmds.warning("Selection Set '%s' rỗng!" % set_name)

    def operate_on_members(self, mode):
        """Thực hiện các thao tác vùng chọn (Select, Add, Remove, Intersect)"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn ít nhất một selection set trong bảng!")
            return

        all_members = []
        for set_name in selected_sets:
            members = cmds.sets(set_name, query=True) or []
            all_members.extend(members)

        if not all_members:
            if mode == "select":
                cmds.select(clear=True)
            cmds.warning("Các selection set được chọn đều rỗng!")
            return

        all_members = list(set(all_members))

        if mode == "select":
            cmds.select(all_members, replace=True)
        elif mode == "add":
            cmds.select(all_members, add=True)
        elif mode == "remove":
            cmds.select(all_members, deselect=True)
        elif mode == "intersect":
            curr_sel = cmds.ls(selection=True) or []
            if not curr_sel:
                cmds.warning("Không có đối tượng nào đang chọn để giao!")
                return
            intersected = list(set(curr_sel) & set(all_members))
            if intersected:
                cmds.select(intersected, replace=True)
            else:
                cmds.select(clear=True)
                cmds.warning("Giao vùng chọn rỗng!")

    def grow_selection(self):
        """Mở rộng vùng chọn component hiện tại (Grow Polygon Selection Region)"""
        try:
            mel.eval("GrowPolygonSelectionRegion;")
        except Exception as e:
            cmds.warning("Không thể grow vùng chọn: %s" % e)

    def shrink_selection(self):
        """Thu nhỏ vùng chọn component hiện tại (Shrink Polygon Selection Region)"""
        try:
            mel.eval("ShrinkPolygonSelectionRegion;")
        except Exception as e:
            cmds.warning("Không thể shrink vùng chọn: %s" % e)

    def toggle_select_mode(self):
        """Chuyển đổi giữa chế độ chọn Object và Component (F8)"""
        try:
            is_component = cmds.selectMode(query=True, component=True)
            if is_component:
                cmds.selectMode(object=True)
                print("Đã chuyển sang chế độ chọn Object.")
            else:
                cmds.selectMode(component=True)
                print("Đã chuyển sang chế độ chọn Component.")
        except Exception as e:
            cmds.warning("Không thể chuyển đổi chế độ chọn: %s" % e)

    def add_selected_to_set(self):
        """Thêm vùng chọn hiện tại vào các set đang chọn trong bảng"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn Selection Set đích trong bảng!")
            return
        
        sel = cmds.ls(selection=True) or []
        if not sel:
            cmds.warning("Vui lòng chọn đối tượng trong Viewport để thêm vào Set!")
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                cmds.sets(sel, edit=True, add=set_name)
        
        self.refresh_sets()
        print("Đã thêm các đối tượng vào set: %s" % ", ".join(selected_sets))

    def remove_selected_from_set(self):
        """Xóa các đối tượng đang chọn trong Viewport khỏi các set đang chọn trong bảng"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn Selection Set trong bảng!")
            return
        
        sel = cmds.ls(selection=True) or []
        if not sel:
            cmds.warning("Vui lòng chọn đối tượng trong Viewport để xóa khỏi Set!")
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                cmds.sets(sel, edit=True, remove=set_name)
        
        self.refresh_sets()
        print("Đã xóa các đối tượng khỏi set: %s" % ", ".join(selected_sets))

    def create_new_set(self):
        """Tạo selection set mới. Nếu chọn sẵn 1 set cha trong bảng, set mới sẽ tự động trở thành con."""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Tạo Selection Set", "Nhập tên cho Selection Set mới:"
        )
        if not ok or not text.strip():
            return

        set_name = text.strip()
        
        # Đảm bảo tên Set do tool tạo ra luôn có tiền tố ANM_ (sau Namespace nếu có)
        if ":" in set_name:
            parts = set_name.rsplit(":", 1)
            ns = parts[0] + ":"
            base = parts[1]
        else:
            ns = ""
            base = set_name
            
        if not base.upper().startswith("ANM_"):
            base = "ANM_" + base
        set_name = ns + base

        sel = cmds.ls(selection=True) or []
        selected_sets = self.get_selected_sets()
        
        with MayaUndoChunk():
            if sel:
                new_set = cmds.sets(sel, name=set_name)
            else:
                new_set = cmds.sets(empty=True, name=set_name)
                
            # Đưa set mới vào group: Nếu chọn 1 set, set đó làm cha, nếu không thì đưa vào root Animeow_sets
            if selected_sets:
                parent_set = selected_sets[0]
            else:
                parent_set = self.ensure_parent_group()
                
            if cmds.objExists(parent_set) and cmds.objExists(new_set):
                try:
                    cmds.sets(new_set, edit=True, add=parent_set)
                except Exception as e:
                    print("Không thể đưa set %s vào cha %s: %s" % (new_set, parent_set, e))
        
        self.refresh_sets()
        print("Đã tạo Selection Set mới và đưa vào cha '%s': %s" % (parent_set, new_set))

    def rename_selected_set(self):
        """Đổi tên Selection Set đang chọn"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn một Selection Set để đổi tên!")
            return
        if len(selected_sets) > 1:
            cmds.warning("Chỉ chọn duy nhất một Selection Set để đổi tên!")
            return

        old_name = selected_sets[0]
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Đổi tên Selection Set", "Nhập tên mới:", text=old_name
        )
        if not ok or not text.strip() or text.strip() == old_name:
            return

        new_name = text.strip()
        
        # Đảm bảo tên Set đổi mới luôn có tiền tố ANM_
        if ":" in new_name:
            parts = new_name.rsplit(":", 1)
            ns = parts[0] + ":"
            base = parts[1]
        else:
            ns = ""
            base = new_name
            
        if not base.upper().startswith("ANM_"):
            base = "ANM_" + base
        new_name = ns + base

        with MayaUndoChunk():
            renamed = cmds.rename(old_name, new_name)
        
        self.refresh_sets()
        print("Đã đổi tên Set từ '%s' thành '%s'" % (old_name, renamed))

    def delete_selected_sets(self):
        """Xóa các Selection Sets đã chọn"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn Selection Set cần xóa!")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Xác nhận xóa", 
            "Bạn có chắc chắn muốn xóa %d selection set đã chọn không?" % len(selected_sets),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                if cmds.objExists(set_name):
                    cmds.delete(set_name)

        self.refresh_sets()
        print("Đã xóa các selection set: %s" % ", ".join(selected_sets))

    def clear_set(self, set_name):
        """Dọn dẹp sạch toàn bộ thành viên của set"""
        members = cmds.sets(set_name, query=True) or []
        if members:
            with MayaUndoChunk():
                cmds.sets(members, edit=True, remove=set_name)
            self.refresh_sets()
            print("Đã dọn dẹp sạch thành viên của set: %s" % set_name)

    def group_selected_sets_under_another(self):
        """Nhóm các set đang chọn làm con của một set khác thông qua hộp thoại chọn"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui lòng chọn ít nhất một selection set!")
            return
            
        other_sets = [s for s in self.sets_list if s not in selected_sets]
        if not other_sets:
            cmds.warning("Không có selection set nào khác trong cảnh để chọn làm cha!")
            return
            
        options = ["Animeow_sets (Thư mục gốc)"] + other_sets
        parent_choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Nhóm vào Set khác", "Chọn Selection Set cha:", options, 0, False
        )
        if not ok or not parent_choice:
            return
            
        if parent_choice.startswith("Animeow_sets"):
            parent_set = self.ensure_parent_group()
        else:
            parent_set = parent_choice
            
        with MayaUndoChunk():
            for set_name in selected_sets:
                # Gỡ khỏi các cha cũ trong danh sách quản lý
                old_parents = cmds.listConnections(set_name + ".message", destination=True, source=False, type="objectSet") or []
                for op in old_parents:
                    if op in self.sets_list or op == "Animeow_sets":
                        try:
                            cmds.sets(set_name, edit=True, remove=op)
                        except Exception:
                            pass
                
                # Đưa vào cha mới
                try:
                    cmds.sets(set_name, edit=True, add=parent_set)
                except Exception as e:
                    print("Lỗi khi đưa set %s vào cha %s: %s" % (set_name, parent_set, e))
                    
        self.refresh_sets()
        print("Đã nhóm các set được chọn vào cha: %s" % parent_set)

    def get_all_child_sets_recursive(self, set_name, visited=None):
        """Quét đệ quy lấy toàn bộ các set con (subset) của set_name"""
        if visited is None:
            visited = set()
        if set_name in visited:
            return []
        visited.add(set_name)

        children = []
        members = cmds.sets(set_name, query=True) or []
        for m in members:
            if cmds.objExists(m) and cmds.nodeType(m) == "objectSet":
                if m in self.sets_list:  # Chỉ lấy các set tuỳ biến thuộc danh sách quản lý
                    children.append(m)
                    children.extend(self.get_all_child_sets_recursive(m, visited))
        return list(set(children))

    def export_selected_sets(self):
        """Xuất các selection set đã chọn (bao gồm đệ quy các set con) ra file JSON"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            selected_sets = self.sets_list
            if not selected_sets:
                cmds.warning("Không có selection set nào trong cảnh để xuất!")
                return
            
            confirm = QtWidgets.QMessageBox.question(
                self, "Xuất toàn bộ", 
                "Không có set nào đang được chọn. Bạn có muốn xuất toàn bộ %d selection set không?" % len(selected_sets),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm != QtWidgets.QMessageBox.Yes:
                return
        else:
            # Thu thập toàn bộ set con đệ quy của các set được chọn
            all_sets_to_export = list(selected_sets)
            for s in selected_sets:
                child_sets = self.get_all_child_sets_recursive(s)
                all_sets_to_export.extend(child_sets)
            # Loại bỏ trùng lặp và gán lại
            selected_sets = list(set(all_sets_to_export))

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Xuất Selection Sets ra File JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        export_data = {}
        for set_name in selected_sets:
            members = cmds.sets(set_name, query=True) or []
            export_data[set_name] = members

        try:
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            print("Đã xuất %d selection sets ra file: %s" % (len(selected_sets), file_path))
        except Exception as e:
            cmds.warning("Lỗi xuất file JSON: %s" % e)

    def import_sets(self):
        """Nhập selection sets từ file JSON với cơ chế map Namespace thông minh và giữ nguyên quan hệ cha con"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Nhập Selection Sets từ File JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
        except Exception as e:
            cmds.warning("Lỗi đọc file JSON: %s" % e)
            return

        if not isinstance(import_data, dict):
            cmds.warning("Định dạng file JSON không hợp lệ!")
            return

        parent_set = self.ensure_parent_group()
        
        imported_count = 0
        missing_objects_log = []
        
        # Đọc Namespace của vật thể đang chọn trong Viewport (nếu có) để tự động ánh xạ
        current_namespace = ""
        sel = cmds.ls(selection=True)
        if sel:
            first_sel = sel[0]
            if ":" in first_sel:
                current_namespace = first_sel.rsplit(":", 1)[0] + ":"

        # Map tên set gốc (trong JSON) sang tên set thực tế trong Maya
        created_sets_map = {}

        with MayaUndoChunk():
            # PHASE 1: Tạo tất cả các Set Node trước
            for set_name in import_data.keys():
                target_set = set_name
                # Lọc bỏ namespace cũ trong file JSON
                if ":" in target_set:
                    target_set = target_set.split(":")[-1]
                
                # Áp namespace hiện tại đang chọn
                if current_namespace:
                    target_set = current_namespace + target_set
                    
                # Đảm bảo tên Set luôn có tiền tố ANM_ (sau Namespace nếu có)
                if ":" in target_set:
                    parts = target_set.rsplit(":", 1)
                    ns = parts[0] + ":"
                    base = parts[1]
                else:
                    ns = ""
                    base = target_set
                    
                if not base.upper().startswith("ANM_"):
                    base = "ANM_" + base
                target_set = ns + base
                
                # Tạo set nếu chưa tồn tại trong scene
                if not cmds.objExists(target_set):
                    target_set = cmds.sets(empty=True, name=target_set)
                    # Mặc định thêm vào root group Animeow_sets
                    if cmds.objExists(parent_set):
                        cmds.sets(target_set, edit=True, add=parent_set)
                
                created_sets_map[set_name] = target_set

            # PHASE 2: Điền thành viên (bao gồm các set con) vào từng set
            for original_set_name, members in import_data.items():
                target_set = created_sets_map.get(original_set_name)
                if not target_set or not cmds.objExists(target_set):
                    continue

                valid_members = []
                child_sets_added = []
                
                for m in members:
                    # Kiểm tra xem thành viên này có phải là một set con được import không
                    if m in import_data:
                        child_set_real_name = created_sets_map.get(m)
                        if child_set_real_name and cmds.objExists(child_set_real_name):
                            valid_members.append(child_set_real_name)
                            child_sets_added.append(child_set_real_name)
                        continue

                    # Nếu là đối tượng/component bình thường
                    target_obj = m
                    if not cmds.objExists(target_obj):
                        # Tách tên cơ bản (base name)
                        if ":" in m:
                            base_name = m.split(":")[-1]
                        else:
                            base_name = m
                        
                        # Ánh xạ thử sang namespace đang làm việc
                        if current_namespace:
                            mapped_obj = current_namespace + base_name
                            if cmds.objExists(mapped_obj):
                                target_obj = mapped_obj
                            else:
                                missing_objects_log.append("%s (Original: %s)" % (mapped_obj, m))
                                continue
                        else:
                            missing_objects_log.append(m)
                            continue
                    
                    valid_members.append(target_obj)
                
                if valid_members:
                    # Thêm thành viên vào set
                    cmds.sets(valid_members, edit=True, add=target_set)
                    
                    # Nếu có set con được thêm vào set cha này, gỡ set con đó khỏi group gốc Animeow_sets
                    # để đảm bảo cấu trúc phân cấp cây sạch sẽ
                    for cs in child_sets_added:
                        if cmds.objExists(parent_set):
                            root_members = cmds.sets(parent_set, query=True) or []
                            if cs in root_members:
                                try:
                                    cmds.sets(cs, edit=True, remove=parent_set)
                                except Exception:
                                    pass
                                    
                imported_count += 1

        self.refresh_sets()
        
        # Thông báo tổng kết
        msg = "Đã nhập thành công %d sets!" % imported_count
        if missing_objects_log:
            print("Các đối tượng không tìm thấy trong scene hiện tại:")
            for item in missing_objects_log[:15]:
                print("  - %s" % item)
            if len(missing_objects_log) > 15:
                print("  - ... và %d đối tượng khác" % (len(missing_objects_log) - 15))
            msg += " (Phát hiện %d đối tượng không tìm thấy trong scene, xem chi tiết trong Script Editor)" % len(missing_objects_log)
            
        QtWidgets.QMessageBox.information(self, "Hoàn tất Nhập", msg)

    def show_context_menu(self, pos):
        """Hiển thị menu chuột phải khi click vào set trong cây"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            return

        menu = QtWidgets.QMenu(self)
        
        action_select = menu.addAction("Chọn thành viên (Select)")
        action_add_sel = menu.addAction("Cộng thêm vào vùng chọn (+)")
        action_sub_sel = menu.addAction("Trừ bớt khỏi vùng chọn (-)")
        action_intersect = menu.addAction("Giao với vùng chọn (∩)")
        menu.addSeparator()
        
        action_add_to = menu.addAction("Thêm đối tượng đang chọn vào Set")
        action_remove_from = menu.addAction("Xóa đối tượng đang chọn khỏi Set")
        action_clear = menu.addAction("Dọn sạch Set (Clear)")
        menu.addSeparator()
        
        action_rename = menu.addAction("Đổi tên")
        action_delete = menu.addAction("Xóa Selection Set")
        menu.addSeparator()
        
        # Menu options quản lý phân cấp
        action_group_under = menu.addAction("Nhóm vào Set khác...")
        action_group_root = menu.addAction("Đưa ra group gốc Animeow_sets")

        action = menu.exec_(self.sets_tree.viewport().mapToGlobal(pos))
        if not action:
            return

        if action == action_select:
            self.operate_on_members("select")
        elif action == action_add_sel:
            self.operate_on_members("add")
        elif action == action_sub_sel:
            self.operate_on_members("remove")
        elif action == action_intersect:
            self.operate_on_members("intersect")
        elif action == action_add_to:
            self.add_selected_to_set()
        elif action == action_remove_from:
            self.remove_selected_from_set()
        elif action == action_clear:
            for s in selected_sets:
                self.clear_set(s)
        elif action == action_rename:
            self.rename_selected_set()
        elif action == action_delete:
            self.delete_selected_sets()
        elif action == action_group_under:
            self.group_selected_sets_under_another()
        elif action == action_group_root:
            parent_set = self.ensure_parent_group()
            with MayaUndoChunk():
                for set_name in selected_sets:
                    if cmds.objExists(parent_set) and cmds.objExists(set_name):
                        try:
                            # Xóa khỏi cha cũ
                            old_parents = cmds.listConnections(set_name + ".message", destination=True, source=False, type="objectSet") or []
                            for op in old_parents:
                                if op in self.sets_list or op == "Animeow_sets":
                                    cmds.sets(set_name, edit=True, remove=op)
                            # Đưa về root
                            cmds.sets(set_name, edit=True, add=parent_set)
                        except Exception as e:
                            print("Lỗi khi đưa set %s về group gốc: %s" % (set_name, e))
            self.refresh_sets()
            print("Đã đưa các set đã chọn ra group gốc Animeow_sets.")
