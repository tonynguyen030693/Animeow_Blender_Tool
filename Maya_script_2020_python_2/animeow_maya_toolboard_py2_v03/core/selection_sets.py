# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import json
import maya.cmds as cmds
import maya.mel as mel

from PySide2 import QtWidgets, QtCore, QtGui


class MayaUndoChunk(object):
    """Context manager giup nhom tat ca hanh dong vao mot khoi undo duy nhat trong Maya"""
    def __enter__(self):
        cmds.undoInfo(openChunk=True, chunkName="AnimeowSelectionSets")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)


class SelectionSetsIcons(object):
    """Ve icon mat an/hien vector bang QPainter phong cach AnimBot"""
    
    COLOR_ACCENT = QtGui.QColor("#00BCD4")  # Cyan chu dao
    COLOR_MUTED = QtGui.QColor("#888888")   # Mau xam mo cho trang thai an
    
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
    """Giao dien quan ly Selection Sets phan cap (Hierarchical Tree) phong cach AnimBot"""
    
    def __init__(self, parent=None):
        super(SelectionSetsManagerUI, self).__init__(parent=parent)
        self.sets_list = []
        self.init_ui()
        self.refresh_sets()

    def init_ui(self):
        # Layout chinh
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(6)

        # Tieu de Tab
        title_lbl = QtWidgets.QLabel("SELECTION SETS MANAGER")
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet("font-weight: bold; font-size: 11px; color: #00BCD4; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # Thanh tim kiem va Lam moi
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.setSpacing(4)
        
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Tim kiem selection set...")
        self.search_input.textChanged.connect(self.filter_sets)
        search_layout.addWidget(self.search_input)

        self.refresh_btn = QtWidgets.QPushButton("🔄")
        self.refresh_btn.setFixedSize(24, 24)
        self.refresh_btn.setToolTip("Lam moi danh sach Sets")
        self.refresh_btn.clicked.connect(self.refresh_sets)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)

        # Cay hien thi cac Selection Sets (Cot 0: Ten Set (cha/con), Cot 1: Visible, Cot 2: So Luong)
        self.sets_tree = QtWidgets.QTreeWidget()
        self.sets_tree.setColumnCount(3)
        self.sets_tree.setHeaderLabels(["Ten Set", "👁", "So Luong"])
        self.sets_tree.setAlternatingRowColors(True)
        self.sets_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sets_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # Cau hinh kich thuoc cot (Cot 0 co gian chinh, cot 1 va 2 gon gang o goc)
        self.sets_tree.header().setStretchLastSection(False)
        header = self.sets_tree.header()
        _set_resize = getattr(header, 'setSectionResizeMode', None) or getattr(header, 'setResizeMode', None)
        if _set_resize:
            _set_resize(0, QtWidgets.QHeaderView.Stretch)
            _set_resize(1, QtWidgets.QHeaderView.Fixed)
        self.sets_tree.setColumnWidth(1, 30)
        if _set_resize:
            _set_resize(2, QtWidgets.QHeaderView.ResizeToContents)
        
        # Ap dung stylesheet dong bo voi tong mau Cyan Accent cua toolboard
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
        
        # Su kien
        self.sets_tree.itemDoubleClicked.connect(self.on_double_click_set)
        self.sets_tree.itemClicked.connect(self.on_item_clicked)
        self.sets_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sets_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.sets_tree)

        # Group Thao tac Vung chon (Selection)
        sel_ops_group = QtWidgets.QGroupBox("Thao tac Vung chon (Selection)")
        sel_ops_layout = QtWidgets.QVBoxLayout(sel_ops_group)
        sel_ops_layout.setContentsMargins(6, 10, 6, 6)
        sel_ops_layout.setSpacing(6)

        # Nut Chon thanh vien chinh (Select)
        self.select_members_btn = QtWidgets.QPushButton("Chon thanh vien (Select)")
        self.select_members_btn.setObjectName("accent_btn")
        self.select_members_btn.setFixedHeight(28)
        self.select_members_btn.setToolTip("Chon tat ca cac doi tuong trong set dang chon (thay the vung chon hien tai)")
        self.select_members_btn.clicked.connect(lambda: self.operate_on_members("select"))
        sel_ops_layout.addWidget(self.select_members_btn)

        # Dong thao tac Cong / Tru / Giao
        sel_sub_layout = QtWidgets.QHBoxLayout()
        sel_sub_layout.setSpacing(4)

        self.add_sel_btn = QtWidgets.QPushButton("+ Cong them")
        self.add_sel_btn.setToolTip("Cong them cac thanh vien cua set vao vung chon hien tai")
        self.add_sel_btn.clicked.connect(lambda: self.operate_on_members("add"))
        sel_sub_layout.addWidget(self.add_sel_btn)

        self.sub_sel_btn = QtWidgets.QPushButton("- Bo bot")
        self.sub_sel_btn.setToolTip("Loai bo cac thanh vien cua set khoi vung chon hien tai")
        self.sub_sel_btn.clicked.connect(lambda: self.operate_on_members("remove"))
        sel_sub_layout.addWidget(self.sub_sel_btn)

        self.intersect_sel_btn = QtWidgets.QPushButton("∩ Giao")
        self.intersect_sel_btn.setToolTip("Giao cac thanh vien cua set voi vung chon hien tai")
        self.intersect_sel_btn.clicked.connect(lambda: self.operate_on_members("intersect"))
        sel_sub_layout.addWidget(self.intersect_sel_btn)

        sel_ops_layout.addLayout(sel_sub_layout)

        # Hang nut Grow / Shrink / Toggle Mode vung chon
        grow_shrink_layout = QtWidgets.QHBoxLayout()
        grow_shrink_layout.setSpacing(4)

        self.grow_sel_btn = QtWidgets.QPushButton("Grow (>)")
        self.grow_sel_btn.setToolTip("Mo rong vung chon component hien tai (Shift + >)")
        self.grow_sel_btn.clicked.connect(self.grow_selection)
        grow_shrink_layout.addWidget(self.grow_sel_btn)

        self.shrink_sel_btn = QtWidgets.QPushButton("Shrink (<)")
        self.shrink_sel_btn.setToolTip("Thu nho vung chon component hien tai (Shift + <)")
        self.shrink_sel_btn.clicked.connect(self.shrink_selection)
        grow_shrink_layout.addWidget(self.shrink_sel_btn)

        self.toggle_mode_btn = QtWidgets.QPushButton("Toggle Mode (F8)")
        self.toggle_mode_btn.setToolTip("Chuyen doi qua lai giua che do chon Object va Component (F8)")
        self.toggle_mode_btn.clicked.connect(self.toggle_select_mode)
        grow_shrink_layout.addWidget(self.toggle_mode_btn)

        sel_ops_layout.addLayout(grow_shrink_layout)

        layout.addWidget(sel_ops_group)

        # Group Quan ly Thanh vien Set (Membership)
        set_ops_group = QtWidgets.QGroupBox("Quan ly Thanh vien Set (Membership)")
        set_ops_layout = QtWidgets.QHBoxLayout(set_ops_group)
        set_ops_layout.setContentsMargins(6, 10, 6, 6)
        set_ops_layout.setSpacing(4)

        self.add_to_set_btn = QtWidgets.QPushButton("Them vao Set")
        self.add_to_set_btn.setToolTip("Them cac doi tuong dang chon trong Viewport vao Set dang chon")
        self.add_to_set_btn.clicked.connect(self.add_selected_to_set)
        set_ops_layout.addWidget(self.add_to_set_btn)

        self.remove_from_set_btn = QtWidgets.QPushButton("Xoa khoi Set")
        self.remove_from_set_btn.setToolTip("Xoa cac doi tuong dang chon trong Viewport khoi Set dang chon")
        self.remove_from_set_btn.clicked.connect(self.remove_selected_from_set)
        set_ops_layout.addWidget(self.remove_from_set_btn)

        layout.addWidget(set_ops_group)

        # Hang nut quan ly Set (Create, Rename, Delete)
        mgmt_layout = QtWidgets.QHBoxLayout()
        mgmt_layout.setSpacing(4)

        self.create_set_btn = QtWidgets.QPushButton("Tao Set Moi")
        self.create_set_btn.setToolTip("Tao selection set moi. Neu chon san 1 set cha trong bang, set moi se tu dong tro thanh con.")
        self.create_set_btn.clicked.connect(self.create_new_set)
        mgmt_layout.addWidget(self.create_set_btn)

        self.rename_set_btn = QtWidgets.QPushButton("Doi Ten")
        self.rename_set_btn.setToolTip("Doi ten Selection Set dang chon")
        self.rename_set_btn.clicked.connect(self.rename_selected_set)
        mgmt_layout.addWidget(self.rename_set_btn)

        self.delete_set_btn = QtWidgets.QPushButton("Xoa Set")
        self.delete_set_btn.setToolTip("Xoa Selection Set dang chon")
        self.delete_set_btn.clicked.connect(self.delete_selected_sets)
        mgmt_layout.addWidget(self.delete_set_btn)

        layout.addLayout(mgmt_layout)

        # Hang nut Luu / Tai Sets ra file ngoai (Export / Import)
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setSpacing(4)

        self.export_sets_btn = QtWidgets.QPushButton("Xuat File (Export)")
        self.export_sets_btn.setToolTip("Xuat cac selection sets da chon ra file JSON")
        self.export_sets_btn.clicked.connect(self.export_selected_sets)
        file_layout.addWidget(self.export_sets_btn)

        self.import_sets_btn = QtWidgets.QPushButton("Nhap File (Import)")
        self.import_sets_btn.setToolTip("Nhap cac selection sets tu file JSON kem theo map Namespace tu dong")
        self.import_sets_btn.clicked.connect(self.import_sets)
        file_layout.addWidget(self.import_sets_btn)

        layout.addLayout(file_layout)

    def ensure_parent_group(self):
        """Dam bao group cha Animeow_sets ton tai duoi dang mot objectSet trong"""
        parent_set = "Animeow_sets"
        if not cmds.objExists(parent_set):
            try:
                cmds.sets(empty=True, name=parent_set)
            except Exception as e:
                print("Khong the tao parent set Animeow_sets: %s" % e)
        return parent_set

    def create_tree_item(self, set_name):
        """Helper tao QTreeWidgetItem cho set voi con mat o cot 1 de tranh bi dich chuyen do thut dong o cot 0"""
        item = QtWidgets.QTreeWidgetItem()
        
        # Cot 0: Ten Set (Qt tu dong ve mui ten va thut dong o cot 0 nay)
        item.setText(0, set_name)
        
        # Cot 1: Visibility (Luon can le thang dung hoan hao vi nam o cot rieng)
        is_vis = self.is_set_visible(set_name)
        item.setIcon(1, SelectionSetsIcons.icon_eye(is_vis))
        item.setToolTip(1, "Click de an/hien toan bo thanh vien cua set (Ctrl+H / Shift+H)")
        
        # Cot 2: So luong thanh vien
        members = cmds.sets(set_name, query=True) or []
        item.setText(2, str(len(members)))
        item.setTextAlignment(2, QtCore.Qt.AlignCenter)
        
        return item

    def is_under_animeow_sets(self, set_node):
        """Kiem tra de quy xem set_node co duoc chua trong group Animeow_sets hay khong"""
        curr = set_node
        visited = set()
        while curr:
            if curr in visited:
                break
            visited.add(curr)
            parents = cmds.listConnections(curr + ".message", destination=True, source=False, type="objectSet") or []
            if "Animeow_sets" in parents:
                return True
            next_parent = None
            for p in parents:
                if p != curr:
                    next_parent = p
                    break
            curr = next_parent
        return False

    def refresh_sets(self):
        """Loc va tai danh sach Selection Sets phan cap trong scene hien tai"""
        # Luu cac set dang duoc chon de khoi phuc lai sau khi lam moi
        selected_items = self.sets_tree.selectedItems()
        selected_names = [item.text(0) for item in selected_items if item]

        all_sets = cmds.ls(type="objectSet") or []
        self.sets_list = []
        for s in all_sets:
            # An group cha Animeow_sets chinh khoi bang danh sach
            if s == "Animeow_sets":
                continue
            # Bo qua cac shadingEngine/material sets (renderable sets)
            if cmds.sets(s, query=True, renderable=True):
                continue
            # Bo qua cac system sets mac dinh cua Maya
            if s in ["defaultLightSet", "defaultObjectSet", "initialShadingGroup", "initialParticleSE"]:
                continue
            # Bo qua cac set an component tu dong sinh ra boi Maya
            if s == "defaultHideFaceDataSet" or s.endswith("HiddenFacesSet"):
                continue
            # Dam bao node type chinh xac la objectSet (loai tru character, partition ke thua tu objectSet)
            if cmds.nodeType(s) != "objectSet":
                continue
                
            # LOC CHI NHAN DIEN SET CUA ANIMEOW:
            # 1. Co ten co ban bat dau bang ANM_ (bo qua Namespace)
            base_name = s.split(":")[-1]
            is_anm = base_name.upper().startswith("ANM_")
            
            # 2. Hoac duoc chua trong group cha Animeow_sets
            is_nested = self.is_under_animeow_sets(s)
            
            if not is_anm and not is_nested:
                continue
                
            self.sets_list.append(s)

        # Xay dung moi quan he cha-con dua tren ket noi connection trong Maya
        parent_map = {}
        for s in self.sets_list:
            parents = cmds.listConnections(s + ".message", destination=True, source=False, type="objectSet") or []
            # Chi lay parent nam trong danh sach custom_sets va khong phai Animeow_sets
            valid_parents = [p for p in parents if p in self.sets_list]
            if valid_parents:
                parent_map[s] = valid_parents[0]  # Lay parent dau tien lam cha phan cap chinh

        # Sap xep theo bang chu cai
        self.sets_list.sort(key=lambda x: x.lower())
        
        # Lam sach cay
        self.sets_tree.clear()
        
        # Ban do luu cac item da duoc tao
        tree_items = {}
        
        # Tim cac root sets (nhung set khong co cha nam trong sets_list)
        root_sets = [s for s in self.sets_list if s not in parent_map]
        child_sets = [s for s in self.sets_list if s in parent_map]
        
        # 1. Them cac root sets len Top Level
        for s in root_sets:
            item = self.create_tree_item(s)
            self.sets_tree.addTopLevelItem(item)
            tree_items[s] = item
            
        # 2. Them cac con vao cac cha tuong ung (lap cho den khi het hoac tranh cycle loop)
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
                # Neu phat hien cycle loop hoac co lap, day cac con con lai len Top Level
                for s in child_sets:
                    item = self.create_tree_item(s)
                    self.sets_tree.addTopLevelItem(item)
                    tree_items[s] = item
                break
                
            for s in added_this_loop:
                child_sets.remove(s)
            max_loops -= 1

        # Tu dong mo rong toan bo cay
        self.sets_tree.expandAll()
        
        # Thuc hien loc tu khoa neu co nhap
        self.filter_sets()

        # Khoi phuc trang thai chon hang
        self.restore_selection_by_names(self.sets_tree.invisibleRootItem(), selected_names)

    def restore_selection_by_names(self, parent_item, selected_names):
        """Khoi phuc trang thai chon dua tren danh sach ten set"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.text(0) in selected_names:
                child.setSelected(True)
            self.restore_selection_by_names(child, selected_names)

    def filter_sets(self):
        """Loc danh sach cac set trong cay dua tren tu khoa tim kiem"""
        filter_text = self.search_input.text().lower()
        self.filter_tree_item(self.sets_tree.invisibleRootItem(), filter_text)

    def filter_tree_item(self, parent_item, filter_text):
        """Duyet de quy va an cac item khong khop tu khoa, giu nguyen cha neu co con khop"""
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
        """Lay danh sach ten cac set dang chon trong bang"""
        selected_items = self.sets_tree.selectedItems()
        return [item.text(0) for item in selected_items if item]

    def is_set_visible(self, set_name):
        """Kiem tra xem set co dang hien thi khong."""
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
        """Dat trang thai hien thi cho cac thanh vien cua set va cac sub-sets con de quy"""
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
                print("Loi khi thay doi visibility cua set %s: %s" % (set_name, e))

        # Luu trang thai toggle vao thuoc tinh tuy bien tren Set Node
        if cmds.objExists(set_name):
            if not cmds.attributeQuery("set_visibility_state", node=set_name, exists=True):
                try:
                    cmds.addAttr(set_name, longName="set_visibility_state", attributeType="bool", defaultValue=True)
                except Exception as e:
                    print("Khong the them attribute set_visibility_state vao set %s: %s" % (set_name, e))
            if cmds.attributeQuery("set_visibility_state", node=set_name, exists=True):
                try:
                    cmds.setAttr(set_name + ".set_visibility_state", state)
                except Exception as e:
                    print("Khong the luu set_visibility_state cho set %s: %s" % (set_name, e))

        # Goi de quy xuong cac set con
        for cs in child_sets:
            self.set_set_visibility_recursive(cs, state, visited)

    def on_item_clicked(self, item, col):
        """Xu ly nhap chuot vao cot visibility (cot 1)"""
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
        """Double-click chuot de chon nhanh thanh vien cua set"""
        set_name = item.text(0)
        members = cmds.sets(set_name, query=True) or []
        if members:
            cmds.select(members, replace=True)
        else:
            cmds.select(clear=True)
            cmds.warning("Selection Set '%s' rong!" % set_name)

    def operate_on_members(self, mode):
        """Thuc hien cac thao tac vung chon (Select, Add, Remove, Intersect)"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon it nhat mot selection set trong bang!")
            return

        all_members = []
        for set_name in selected_sets:
            members = cmds.sets(set_name, query=True) or []
            all_members.extend(members)

        if not all_members:
            if mode == "select":
                cmds.select(clear=True)
            cmds.warning("Cac selection set duoc chon deu rong!")
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
                cmds.warning("Khong co doi tuong nao dang chon de giao!")
                return
            intersected = list(set(curr_sel) & set(all_members))
            if intersected:
                cmds.select(intersected, replace=True)
            else:
                cmds.select(clear=True)
                cmds.warning("Giao vung chon rong!")

    def grow_selection(self):
        """Mo rong vung chon component hien tai (Grow Polygon Selection Region)"""
        try:
            mel.eval("GrowPolygonSelectionRegion;")
        except Exception as e:
            cmds.warning("Khong the grow vung chon: %s" % e)

    def shrink_selection(self):
        """Thu nho vung chon component hien tai (Shrink Polygon Selection Region)"""
        try:
            mel.eval("ShrinkPolygonSelectionRegion;")
        except Exception as e:
            cmds.warning("Khong the shrink vung chon: %s" % e)

    def toggle_select_mode(self):
        """Chuyen doi giua che do chon Object va Component (F8)"""
        try:
            is_component = cmds.selectMode(query=True, component=True)
            if is_component:
                cmds.selectMode(object=True)
                print("Da chuyen sang che do chon Object.")
            else:
                cmds.selectMode(component=True)
                print("Da chuyen sang che do chon Component.")
        except Exception as e:
            cmds.warning("Khong the chuyen doi che do chon: %s" % e)

    def add_selected_to_set(self):
        """Them vung chon hien tai vao cac set dang chon trong bang"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon Selection Set dich trong bang!")
            return
        
        sel = cmds.ls(selection=True) or []
        if not sel:
            cmds.warning("Vui long chon doi tuong trong Viewport de them vao Set!")
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                cmds.sets(sel, edit=True, add=set_name)
        
        self.refresh_sets()
        print("Da them cac doi tuong vao set: %s" % ", ".join(selected_sets))

    def remove_selected_from_set(self):
        """Xoa cac doi tuong dang chon trong Viewport khoi cac set dang chon trong bang"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon Selection Set trong bang!")
            return
        
        sel = cmds.ls(selection=True) or []
        if not sel:
            cmds.warning("Vui long chon doi tuong trong Viewport de xoa khoi Set!")
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                cmds.sets(sel, edit=True, remove=set_name)
        
        self.refresh_sets()
        print("Da xoa cac doi tuong khoi set: %s" % ", ".join(selected_sets))

    def create_new_set(self):
        """Tao selection set moi. Neu chon san 1 set cha trong bang, set moi se tu dong tro thanh con."""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Tao Selection Set", "Nhap ten cho Selection Set moi:"
        )
        if not ok or not text.strip():
            return

        set_name = text.strip()
        
        # Dam bao ten Set do tool tao ra luon co tien to ANM_ (sau Namespace neu co)
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
                
            # Dua set moi vao group: Neu chon 1 set, set do lam cha, neu khong thi dua vao root Animeow_sets
            if selected_sets:
                parent_set = selected_sets[0]
            else:
                parent_set = self.ensure_parent_group()
                
            if cmds.objExists(parent_set) and cmds.objExists(new_set):
                try:
                    cmds.sets(new_set, edit=True, add=parent_set)
                except Exception as e:
                    print("Khong the dua set %s vao cha %s: %s" % (new_set, parent_set, e))
        
        self.refresh_sets()
        print("Da tao Selection Set moi va dua vao cha '%s': %s" % (parent_set, new_set))

    def rename_selected_set(self):
        """Doi ten Selection Set dang chon"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon mot Selection Set de doi ten!")
            return
        if len(selected_sets) > 1:
            cmds.warning("Chi chon duy nhat mot Selection Set de doi ten!")
            return

        old_name = selected_sets[0]
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Doi ten Selection Set", "Nhap ten moi:", text=old_name
        )
        if not ok or not text.strip() or text.strip() == old_name:
            return

        new_name = text.strip()
        
        # Dam bao ten Set doi moi luon co tien to ANM_
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
        print("Da doi ten Set tu '%s' thanh '%s'" % (old_name, renamed))

    def delete_selected_sets(self):
        """Xoa cac Selection Sets da chon"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon Selection Set can xoa!")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Xac nhan xoa", 
            "Ban co chac chan muon xoa %d selection set da chon khong?" % len(selected_sets),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        with MayaUndoChunk():
            for set_name in selected_sets:
                if cmds.objExists(set_name):
                    cmds.delete(set_name)

        self.refresh_sets()
        print("Da xoa cac selection set: %s" % ", ".join(selected_sets))

    def clear_set(self, set_name):
        """Don dep sach toan bo thanh vien cua set"""
        members = cmds.sets(set_name, query=True) or []
        if members:
            with MayaUndoChunk():
                cmds.sets(members, edit=True, remove=set_name)
            self.refresh_sets()
            print("Da don dep sach thanh vien cua set: %s" % set_name)

    def group_selected_sets_under_another(self):
        """Nhom cac set dang chon lam con cua mot set khac thong qua hop thoai chon"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            cmds.warning("Vui long chon it nhat mot selection set!")
            return
            
        other_sets = [s for s in self.sets_list if s not in selected_sets]
        if not other_sets:
            cmds.warning("Khong co selection set nao khac trong canh de chon lam cha!")
            return
            
        options = ["Animeow_sets (Thu muc goc)"] + other_sets
        parent_choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Nhom vao Set khac", "Chon Selection Set cha:", options, 0, False
        )
        if not ok or not parent_choice:
            return
            
        if parent_choice.startswith("Animeow_sets"):
            parent_set = self.ensure_parent_group()
        else:
            parent_set = parent_choice
            
        with MayaUndoChunk():
            for set_name in selected_sets:
                # Go khoi cac cha cu trong danh sach quan ly
                old_parents = cmds.listConnections(set_name + ".message", destination=True, source=False, type="objectSet") or []
                for op in old_parents:
                    if op in self.sets_list or op == "Animeow_sets":
                        try:
                            cmds.sets(set_name, edit=True, remove=op)
                        except Exception:
                            pass
                
                # Dua vao cha moi
                try:
                    cmds.sets(set_name, edit=True, add=parent_set)
                except Exception as e:
                    print("Loi khi dua set %s vao cha %s: %s" % (set_name, parent_set, e))
                    
        self.refresh_sets()
        print("Da nhom cac set duoc chon vao cha: %s" % parent_set)

    def get_all_child_sets_recursive(self, set_name, visited=None):
        """Quet de quy lay toan bo cac set con (subset) cua set_name"""
        if visited is None:
            visited = set()
        if set_name in visited:
            return []
        visited.add(set_name)

        children = []
        members = cmds.sets(set_name, query=True) or []
        for m in members:
            if cmds.objExists(m) and cmds.nodeType(m) == "objectSet":
                if m in self.sets_list:  # Chi lay cac set tuy bien thuoc danh sach quan ly
                    children.append(m)
                    children.extend(self.get_all_child_sets_recursive(m, visited))
        return list(set(children))

    def export_selected_sets(self):
        """Xuat cac selection set da chon (bao gom de quy cac set con) ra file JSON"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            selected_sets = self.sets_list
            if not selected_sets:
                cmds.warning("Khong co selection set nao trong canh de xuat!")
                return
            
            confirm = QtWidgets.QMessageBox.question(
                self, "Xuat toan bo", 
                "Khong co set nao dang duoc chon. Ban co muon xuat toan bo %d selection set khong?" % len(selected_sets),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm != QtWidgets.QMessageBox.Yes:
                return
        else:
            # Thu thap toan bo set con de quy cua cac set duoc chon
            all_sets_to_export = list(selected_sets)
            for s in selected_sets:
                child_sets = self.get_all_child_sets_recursive(s)
                all_sets_to_export.extend(child_sets)
            # Loai bo trung lap va gan lai
            selected_sets = list(set(all_sets_to_export))

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Xuat Selection Sets ra File JSON", "", "JSON Files (*.json)"
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
            print("Da xuat %d selection sets ra file: %s" % (len(selected_sets), file_path))
        except Exception as e:
            cmds.warning("Loi xuat file JSON: %s" % e)

    def import_sets(self):
        """Nhap selection sets tu file JSON voi co che map Namespace thong minh va giu nguyen quan he cha con"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Nhap Selection Sets tu File JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
        except Exception as e:
            cmds.warning("Loi doc file JSON: %s" % e)
            return

        if not isinstance(import_data, dict):
            cmds.warning("Dinh dang file JSON khong hop le!")
            return

        parent_set = self.ensure_parent_group()
        
        imported_count = 0
        missing_objects_log = []
        
        # Doc Namespace cua vat the dang chon trong Viewport (neu co) de tu dong anh xa
        current_namespace = ""
        sel = cmds.ls(selection=True)
        if sel:
            first_sel = sel[0]
            if ":" in first_sel:
                current_namespace = first_sel.rsplit(":", 1)[0] + ":"

        # Map ten set goc (trong JSON) sang ten set thuc te trong Maya
        created_sets_map = {}

        with MayaUndoChunk():
            # PHASE 1: Tao tat ca cac Set Node truoc
            for set_name in import_data.keys():
                target_set = set_name
                # Loc bo namespace cu trong file JSON
                if ":" in target_set:
                    target_set = target_set.split(":")[-1]
                
                # Ap namespace hien tai dang chon
                if current_namespace:
                    target_set = current_namespace + target_set
                    
                # Dam bao ten Set luon co tien to ANM_ (sau Namespace neu co)
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
                
                # Tao set neu chua ton tai trong scene
                if not cmds.objExists(target_set):
                    target_set = cmds.sets(empty=True, name=target_set)
                    # Mac dinh them vao root group Animeow_sets
                    if cmds.objExists(parent_set):
                        cmds.sets(target_set, edit=True, add=parent_set)
                
                created_sets_map[set_name] = target_set

            # PHASE 2: Dien thanh vien (bao gom cac set con) vao tung set
            for original_set_name, members in import_data.items():
                target_set = created_sets_map.get(original_set_name)
                if not target_set or not cmds.objExists(target_set):
                    continue

                valid_members = []
                child_sets_added = []
                
                for m in members:
                    # Kiem tra xem thanh vien nay co phai la mot set con duoc import khong
                    if m in import_data:
                        child_set_real_name = created_sets_map.get(m)
                        if child_set_real_name and cmds.objExists(child_set_real_name):
                            valid_members.append(child_set_real_name)
                            child_sets_added.append(child_set_real_name)
                        continue

                    # Neu la doi tuong/component binh thuong
                    target_obj = m
                    if not cmds.objExists(target_obj):
                        # Tach ten co ban (base name)
                        if ":" in m:
                            base_name = m.split(":")[-1]
                        else:
                            base_name = m
                        
                        # Anh xa thu sang namespace dang lam viec
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
                    # Them thanh vien vao set
                    cmds.sets(valid_members, edit=True, add=target_set)
                    
                    # Neu co set con duoc them vao set cha nay, go set con do khoi group goc Animeow_sets
                    # de dam bao cau truc phan cap cay sach se
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
        
        # Thong bao tong ket
        msg = "Da nhap thanh cong %d sets!" % imported_count
        if missing_objects_log:
            print("Cac doi tuong khong tim thay trong scene hien tai:")
            for item in missing_objects_log[:15]:
                print("  - %s" % item)
            if len(missing_objects_log) > 15:
                print("  - ... va %d doi tuong khac" % (len(missing_objects_log) - 15))
            msg += " (Phat hien %d doi tuong khong tim thay trong scene, xem chi tiet trong Script Editor)" % len(missing_objects_log)
            
        QtWidgets.QMessageBox.information(self, "Hoan tat Nhap", msg)

    def show_context_menu(self, pos):
        """Hien thi menu chuot phai khi click vao set trong cay"""
        selected_sets = self.get_selected_sets()
        if not selected_sets:
            return

        menu = QtWidgets.QMenu(self)
        
        action_select = menu.addAction("Chon thanh vien (Select)")
        action_add_sel = menu.addAction("Cong them vao vung chon (+)")
        action_sub_sel = menu.addAction("Tru bot khoi vung chon (-)")
        action_intersect = menu.addAction("Giao voi vung chon (n)")
        menu.addSeparator()
        
        action_add_to = menu.addAction("Them doi tuong dang chon vao Set")
        action_remove_from = menu.addAction("Xoa doi tuong dang chon khoi Set")
        action_clear = menu.addAction("Don sach Set (Clear)")
        menu.addSeparator()
        
        action_rename = menu.addAction("Doi ten")
        action_delete = menu.addAction("Xoa Selection Set")
        menu.addSeparator()
        
        # Menu options quan ly phan cap
        action_group_under = menu.addAction("Nhom vao Set khac...")
        action_group_root = menu.addAction("Dua ra group goc Animeow_sets")

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
                            # Xoa khoi cha cu
                            old_parents = cmds.listConnections(set_name + ".message", destination=True, source=False, type="objectSet") or []
                            for op in old_parents:
                                if op in self.sets_list or op == "Animeow_sets":
                                    cmds.sets(set_name, edit=True, remove=op)
                            # Dua ve root
                            cmds.sets(set_name, edit=True, add=parent_set)
                        except Exception as e:
                            print("Loi khi dua set %s ve group goc: %s" % (set_name, e))
            self.refresh_sets()
            print("Da dua cac set da chon ra group goc Animeow_sets.")
