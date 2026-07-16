# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import sys
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui

# ---------------------------------------------------------------------------
# Undo Chunk Context Manager
# ---------------------------------------------------------------------------
class MayaUndoChunk(object):
    """Context manager giúp nhóm tất cả hành động vào một khối undo duy nhất"""
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)


# ---------------------------------------------------------------------------
# ViewLayerIcons — Bộ icon vector QPainter tự vẽ phong cách AnimBot
# ---------------------------------------------------------------------------
class ViewLayerIcons(object):
    """Vẽ icon vector inline bằng QPainter để tăng tốc tải và tùy biến màu dễ dàng"""
    
    COLOR_ACCENT = QtGui.QColor("#00BCD4")  # Cyan chủ đạo của bộ tool
    COLOR_MUTED = QtGui.QColor("#888888")   # Màu xám mờ cho trạng thái đóng/tắt
    
    @staticmethod
    def _create_pixmap(draw_func, size=16, color=None):
        if color is None:
            color = ViewLayerIcons.COLOR_ACCENT
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

    # --- Các phương thức vẽ vector ---
    
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
        c = ViewLayerIcons.COLOR_MUTED
        p.setPen(QtGui.QPen(c, 1.5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.center().y() - 1)
        path.quadTo(r.center().x(), r.bottom() - 2, r.right(), r.center().y() - 1)
        p.drawPath(path)
        cx, cy = r.center().x(), r.center().y()
        p.drawLine(cx - 3, cy, cx - 5, cy + 3)
        p.drawLine(cx, cy + 1, cx, cy + 5)
        p.drawLine(cx + 3, cy, cx + 5, cy + 3)

    @staticmethod
    def _draw_layer(p, r, c):
        p.setPen(QtGui.QPen(c, 1.2, QtCore.Qt.SolidLine))
        p.setBrush(QtGui.QBrush(c, QtCore.Qt.SolidPattern))
        top_poly = QtGui.QPolygonF([
            QtCore.QPointF(r.center().x(), r.top()),
            QtCore.QPointF(r.right(), r.top() + r.height() * 0.25),
            QtCore.QPointF(r.center().x(), r.top() + r.height() * 0.5),
            QtCore.QPointF(r.left(), r.top() + r.height() * 0.25)
        ])
        p.drawPolygon(top_poly)
        
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.left(), r.top() + r.height() * 0.5),
            QtCore.QPointF(r.center().x(), r.top() + r.height() * 0.75),
            QtCore.QPointF(r.right(), r.top() + r.height() * 0.5)
        ]))
        
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.left(), r.top() + r.height() * 0.75),
            QtCore.QPointF(r.center().x(), r.bottom()),
            QtCore.QPointF(r.right(), r.top() + r.height() * 0.75)
        ]))

    @staticmethod
    def _draw_group(p, r, c):
        p.setPen(QtGui.QPen(c, 1.3, QtCore.Qt.SolidLine))
        p.setBrush(QtCore.Qt.NoBrush)
        folder_path = QtGui.QPainterPath()
        folder_path.moveTo(r.left(), r.bottom())
        folder_path.lineTo(r.left(), r.top() + 2)
        folder_path.lineTo(r.left() + r.width() * 0.4, r.top() + 2)
        folder_path.lineTo(r.left() + r.width() * 0.5, r.top() + 4)
        folder_path.lineTo(r.right(), r.top() + 4)
        folder_path.lineTo(r.right(), r.bottom())
        folder_path.closeSubpath()
        p.drawPath(folder_path)

    @staticmethod
    def _draw_plus(p, r, c):
        p.setPen(QtGui.QPen(c, 2.0, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        cx, cy = r.center().x(), r.center().y()
        p.drawLine(cx, r.top() + 1, cx, r.bottom() - 1)
        p.drawLine(r.left() + 1, cy, r.right() - 1, cy)

    @staticmethod
    def _draw_sub(p, r, c):
        p.setPen(QtGui.QPen(c, 1.2, QtCore.Qt.SolidLine))
        p.drawRect(QtCore.QRectF(r.left(), r.top(), r.width() * 0.6, r.height() * 0.6))
        
        p.setPen(QtGui.QPen(c, 1.8, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        cx = r.right() - r.width() * 0.2
        cy = r.bottom() - r.height() * 0.2
        p.drawLine(cx, r.bottom() - r.height() * 0.4, cx, r.bottom())
        p.drawLine(r.right() - r.width() * 0.4, cy, r.right(), cy)

    @staticmethod
    def _draw_grow(p, r, c):
        p.setPen(QtGui.QPen(c, 2.0, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        cx, cy = r.center().x(), r.center().y()
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.left() + 2, r.top() + 1),
            QtCore.QPointF(r.center().x() + 1, cy),
            QtCore.QPointF(r.left() + 2, r.bottom() - 1)
        ]))
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.center().x() + 2, r.top() + 1),
            QtCore.QPointF(r.right() - 1, cy),
            QtCore.QPointF(r.center().x() + 2, r.bottom() - 1)
        ]))

    @staticmethod
    def _draw_shrink(p, r, c):
        p.setPen(QtGui.QPen(c, 2.0, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        cx, cy = r.center().x(), r.center().y()
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.right() - 2, r.top() + 1),
            QtCore.QPointF(r.center().x() - 1, cy),
            QtCore.QPointF(r.right() - 2, r.bottom() - 1)
        ]))
        p.drawPolyline(QtGui.QPolygonF([
            QtCore.QPointF(r.center().x() - 2, r.top() + 1),
            QtCore.QPointF(r.left() + 1, cy),
            QtCore.QPointF(r.center().x() - 2, r.bottom() - 1)
        ]))

    # --- Gọi nhanh các Icon ---
    @classmethod
    def icon_eye(cls, open_state):
        return cls.make_icon(cls._draw_eye_open if open_state else cls._draw_eye_closed, None if open_state else cls.COLOR_MUTED)

    @classmethod
    def icon_layer(cls):
        return cls.make_icon(cls._draw_layer)

    @classmethod
    def icon_group(cls):
        return cls.make_icon(cls._draw_group)

    @classmethod
    def icon_plus(cls):
        return cls.make_icon(cls._draw_plus)

    @classmethod
    def icon_sub(cls):
        return cls.make_icon(cls._draw_sub)

    @classmethod
    def icon_grow(cls):
        return cls.make_icon(cls._draw_grow)

    @classmethod
    def icon_shrink(cls):
        return cls.make_icon(cls._draw_shrink)


# ---------------------------------------------------------------------------
# Class AnimeowMeshGroupModel (Model)
# ---------------------------------------------------------------------------
class AnimeowMeshGroupModel(object):
    """
    Lớp xử lý logic tạo lập, phân loại và ẩn/hiện Selection Sets trong Maya.
    """
    
    ATTR_CHAR_LAYER = "animeow_char_layer"
    ATTR_GROUP_LAYER = "animeow_group_layer"
    ATTR_VISIBILITY = "animeow_visibility"

    @classmethod
    def create_character_layer(cls, char_name):
        """Tạo Set cha cho nhân vật (Character Layer)"""
        with MayaUndoChunk():
            if cmds.objExists(char_name):
                if cmds.attributeQuery(cls.ATTR_CHAR_LAYER, node=char_name, exists=True):
                    return char_name
                base_name = char_name
                suffix = 1
                while cmds.objExists(f"{base_name}_{suffix}"):
                    suffix += 1
                char_name = f"{base_name}_{suffix}"
                
            char_set = cmds.sets(name=char_name, empty=True)
            cmds.addAttr(char_set, longName=cls.ATTR_CHAR_LAYER, attributeType="bool", defaultValue=True)
            cmds.addAttr(char_set, longName=cls.ATTR_VISIBILITY, attributeType="bool", defaultValue=True)
            return char_set

    @classmethod
    def create_group_layer(cls, char_set, group_name):
        """Tạo Group con thuộc Set cha"""
        with MayaUndoChunk():
            unique_name = group_name
            if cmds.objExists(unique_name):
                base_name = group_name
                suffix = 1
                while cmds.objExists(f"{base_name}_{suffix}"):
                    suffix += 1
                unique_name = f"{base_name}_{suffix}"
                
            group_set = cmds.sets(name=unique_name, empty=True)
            cmds.addAttr(group_set, longName=cls.ATTR_GROUP_LAYER, attributeType="bool", defaultValue=True)
            cmds.addAttr(group_set, longName=cls.ATTR_VISIBILITY, attributeType="bool", defaultValue=True)
            
            # Đăng ký Group Set là thành viên của Character Set
            cmds.sets(group_set, edit=True, addElement=char_set)
            return group_set

    @classmethod
    def add_to_group(cls, group_set, selection_list):
        """Phân loại selection_list rồi nạp vào Set con"""
        if not selection_list:
            return
            
        with MayaUndoChunk():
            faces = cmds.filterExpand(selection_list, selectionMask=34) or []
            objects = [item for item in selection_list if "." not in item]
            
            items_to_add = faces + objects
            if items_to_add:
                cmds.sets(items_to_add, edit=True, addElement=group_set)
                
                # Nếu Group đang ẩn, ẩn ngay lập tức các phần tử mới được thêm
                is_visible = cls.get_group_visibility(group_set)
                if not is_visible:
                    cls.set_items_visibility(faces, objects, False)

    @classmethod
    def remove_from_group(cls, group_set, items):
        """Xóa items khỏi Group con và khôi phục hiển thị của chúng nếu Group đang ẩn"""
        if not items:
            return
            
        with MayaUndoChunk():
            is_visible = cls.get_group_visibility(group_set)
            if not is_visible:
                faces = cmds.filterExpand(items, selectionMask=34) or []
                objects = [i for i in items if "." not in i]
                cls.set_items_visibility(faces, objects, True)
                
            cmds.sets(items, remove=group_set)

    @classmethod
    def get_group_visibility(cls, group_set):
        """Lấy trạng thái hiển thị hiện tại của Group set"""
        if cmds.objExists(group_set) and cmds.attributeQuery(cls.ATTR_VISIBILITY, node=group_set, exists=True):
            return cmds.getAttr(f"{group_set}.{cls.ATTR_VISIBILITY}")
        return True

    @classmethod
    def set_visibility(cls, group_set, state):
        """Ẩn/hiện thông minh các thành viên trong Group"""
        if not cmds.objExists(group_set):
            return
            
        with MayaUndoChunk():
            if not cmds.attributeQuery(cls.ATTR_VISIBILITY, node=group_set, exists=True):
                cmds.addAttr(group_set, longName=cls.ATTR_VISIBILITY, attributeType="bool", defaultValue=True)
            cmds.setAttr(f"{group_set}.{cls.ATTR_VISIBILITY}", state)
            
            members = cmds.sets(group_set, query=True) or []
            faces = cmds.filterExpand(members, selectionMask=34) or []
            objects = [m for m in members if "." not in m]
            
            cls.set_items_visibility(faces, objects, state)

    @classmethod
    def set_multiple_groups_visibility(cls, group_sets, state):
        """Ẩn/hiện thông minh cho nhiều Group cùng lúc, gộp chung để tăng hiệu suất tối đa"""
        if not group_sets:
            return
            
        with MayaUndoChunk():
            all_faces = []
            all_objects = []
            
            for group_set in group_sets:
                if not cmds.objExists(group_set):
                    continue
                # Cập nhật thuộc tính visibility riêng lẻ của từng group để hiển thị icon con mắt đúng
                if not cmds.attributeQuery(cls.ATTR_VISIBILITY, node=group_set, exists=True):
                    cmds.addAttr(group_set, longName=cls.ATTR_VISIBILITY, attributeType="bool", defaultValue=True)
                cmds.setAttr(f"{group_set}.{cls.ATTR_VISIBILITY}", state)
                
                # Gom thành viên
                members = cmds.sets(group_set, query=True) or []
                faces = cmds.filterExpand(members, selectionMask=34) or []
                objects = [m for m in members if "." not in m]
                
                all_faces.extend(faces)
                all_objects.extend(objects)
                
            # Loại bỏ trùng lặp nếu có
            all_faces = list(set(all_faces))
            all_objects = list(set(all_objects))
            
            # Cập nhật hiển thị một lần duy nhất cho tất cả thành viên gom được
            cls.set_items_visibility(all_faces, all_objects, state)

    @classmethod
    def set_faces_visibility_cmd(cls, faces, state):
        """Ẩn hoặc hiện các face components bằng lệnh hide/showHidden chuẩn của Maya để đảm bảo tương thích Viewport 2.0"""
        if not faces:
            return
            
        with MayaUndoChunk():
            try:
                # Sử dụng lệnh hide/showHidden cốt lõi của Maya hoạt động trực tiếp trên cả object và components
                if state:
                    cmds.showHidden(faces)  # Hiển thị lại các mặt
                else:
                    cmds.hide(faces)        # Ẩn các mặt
            except Exception as e:
                print("[Animeow View Layer] Lỗi khi thực thi hide/showHidden trên faces: %s" % e)
                
            # Ép buộc viewport cập nhật
            cmds.refresh(force=True)

    @classmethod
    def set_items_visibility(cls, faces, objects, state):
        """Thực thi ẩn/hiện thực tế trên Viewport"""
        for obj in objects:
            if cmds.objExists(obj + ".visibility"):
                try:
                    if not cmds.getAttr(obj + ".visibility", lock=True):
                        cmds.setAttr(obj + ".visibility", state)
                except Exception as e:
                    print("[Animeow View Layer] Không thể set visibility cho %s: %s" % (obj, e))
                    
        if faces:
            cls.set_faces_visibility_cmd(faces, state)

    @classmethod
    def grow_group_selection(cls, group_set):
        """Mở rộng vùng chọn polygon faces trong Group"""
        if not cmds.objExists(group_set):
            return
            
        with MayaUndoChunk():
            members = cmds.sets(group_set, query=True) or []
            faces = cmds.filterExpand(members, selectionMask=34) or []
            if not faces:
                cmds.warning("Group '%s' không chứa polygon faces để Grow." % group_set)
                return
                
            cmds.select(faces, replace=True)
            try:
                cmds.GrowPolygonSelectionRegion()
            except AttributeError:
                mel.eval("GrowPolygonSelectionRegion;")
                
            new_sel = cmds.ls(selection=True)
            new_faces = cmds.filterExpand(new_sel, selectionMask=34) or []
            
            if new_faces:
                cmds.sets(faces, remove=group_set)
                cmds.sets(new_faces, edit=True, addElement=group_set)
                
                is_visible = cls.get_group_visibility(group_set)
                if not is_visible:
                    cls.set_items_visibility(new_faces, [], False)

    @classmethod
    def shrink_group_selection(cls, group_set):
        """Thu hẹp vùng chọn polygon faces trong Group"""
        if not cmds.objExists(group_set):
            return
            
        with MayaUndoChunk():
            members = cmds.sets(group_set, query=True) or []
            faces = cmds.filterExpand(members, selectionMask=34) or []
            if not faces:
                cmds.warning("Group '%s' không chứa polygon faces để Shrink." % group_set)
                return
                
            cmds.select(faces, replace=True)
            try:
                cmds.ShrinkPolygonSelectionRegion()
            except AttributeError:
                mel.eval("ShrinkPolygonSelectionRegion;")
                
            new_sel = cmds.ls(selection=True)
            new_faces = cmds.filterExpand(new_sel, selectionMask=34) or []
            
            is_visible = cls.get_group_visibility(group_set)
            if not is_visible:
                # Hiện lại các face cũ trước để tránh 'lỗi kẹt hiển thị'
                cls.set_items_visibility(faces, [], True)
                
            cmds.sets(faces, remove=group_set)
            
            if new_faces:
                cmds.sets(new_faces, edit=True, addElement=group_set)
                if not is_visible:
                    cls.set_items_visibility(new_faces, [], False)


# ---------------------------------------------------------------------------
# Class AnimeowTreeModel (Data Model)
# ---------------------------------------------------------------------------
class AnimeowTreeModel(QtGui.QStandardItemModel):
    """Cấu trúc dữ liệu phân cấp phục vụ hiển thị trên QTreeView"""
    
    def __init__(self, parent=None):
        super(AnimeowTreeModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Layer / Group", "Visibility"])
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def populate_tree(self):
        """Tìm các Set trong Maya để dựng lại cây hiển thị"""
        self.clear()
        self.setHorizontalHeaderLabels(["Layer / Group", "Visibility"])
        
        all_sets = cmds.ls(type="objectSet") or []
        char_sets = []
        for s in all_sets:
            if cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_CHAR_LAYER, node=s, exists=True):
                char_sets.append(s)
                
        char_sets.sort()
        
        for char_set in char_sets:
            char_item = QtGui.QStandardItem(char_set)
            char_item.setData(char_set, QtCore.Qt.UserRole)
            char_item.setData("layer", QtCore.Qt.UserRole + 1)
            
            font = char_item.font()
            font.setBold(True)
            char_item.setFont(font)
            char_item.setIcon(ViewLayerIcons.icon_layer())
            
            char_vis_val = True
            if cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_VISIBILITY, node=char_set, exists=True):
                char_vis_val = cmds.getAttr(f"{char_set}.{AnimeowMeshGroupModel.ATTR_VISIBILITY}")
                
            char_vis_item = QtGui.QStandardItem()
            char_vis_item.setData(char_set, QtCore.Qt.UserRole)
            char_vis_item.setData("layer_vis", QtCore.Qt.UserRole + 1)
            char_vis_item.setIcon(ViewLayerIcons.icon_eye(char_vis_val))
            char_vis_item.setTextAlignment(QtCore.Qt.AlignCenter)
            
            members = cmds.sets(char_set, query=True) or []
            group_sets = []
            for m in members:
                if (cmds.nodeType(m) == "objectSet" and 
                        cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_GROUP_LAYER, node=m, exists=True)):
                    group_sets.append(m)
                    
            group_sets.sort()
            
            for group_set in group_sets:
                group_item = QtGui.QStandardItem(group_set)
                group_item.setData(group_set, QtCore.Qt.UserRole)
                group_item.setData("group", QtCore.Qt.UserRole + 1)
                group_item.setIcon(ViewLayerIcons.icon_group())
                
                group_vis_val = AnimeowMeshGroupModel.get_group_visibility(group_set)
                group_vis_item = QtGui.QStandardItem()
                group_vis_item.setData(group_set, QtCore.Qt.UserRole)
                group_vis_item.setData("group_vis", QtCore.Qt.UserRole + 1)
                group_vis_item.setIcon(ViewLayerIcons.icon_eye(group_vis_val))
                group_vis_item.setTextAlignment(QtCore.Qt.AlignCenter)
                
                char_item.appendRow([group_item, group_vis_item])
                
            self.appendRow([char_item, char_vis_item])


# ---------------------------------------------------------------------------
# Class AnimeowViewLayerUI (View)
# ---------------------------------------------------------------------------
class AnimeowViewLayerUI(QtWidgets.QWidget):
    """Giao diện chính của công cụ quản lý hiển thị phân cấp"""
    
    def __init__(self, parent=None):
        super(AnimeowViewLayerUI, self).__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        # 1. THANH TOOLBAR PHÍA TRÊN
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(4)
        
        self.btn_toggle_all = QtWidgets.QPushButton()
        self.btn_toggle_all.setIcon(ViewLayerIcons.icon_eye(True))
        self.btn_toggle_all.setToolTip("Ẩn / Hiện tất cả các Layers")
        self.btn_toggle_all.setFixedSize(28, 28)
        self.btn_toggle_all.clicked.connect(self.on_toggle_all_visibility)
        toolbar.addWidget(self.btn_toggle_all)
        
        v_line = QtWidgets.QFrame()
        v_line.setFrameShape(QtWidgets.QFrame.VLine)
        v_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        toolbar.addWidget(v_line)
        
        self.btn_add_layer = QtWidgets.QPushButton()
        self.btn_add_layer.setIcon(ViewLayerIcons.icon_plus())
        self.btn_add_layer.setToolTip("Tạo Layer cha mới (Character Layer)")
        self.btn_add_layer.setFixedSize(28, 28)
        self.btn_add_layer.clicked.connect(self.on_create_layer)
        toolbar.addWidget(self.btn_add_layer)
        
        self.btn_add_group = QtWidgets.QPushButton()
        self.btn_add_group.setIcon(ViewLayerIcons.icon_sub())
        self.btn_add_group.setToolTip("Tạo Group con mới từ vùng chọn hiện tại")
        self.btn_add_group.setFixedSize(28, 28)
        self.btn_add_group.clicked.connect(self.on_create_group)
        toolbar.addWidget(self.btn_add_group)
        
        self.btn_grow = QtWidgets.QPushButton()
        self.btn_grow.setIcon(ViewLayerIcons.icon_grow())
        self.btn_grow.setToolTip("Mở rộng vùng chọn Polygon Faces (Grow)")
        self.btn_grow.setFixedSize(28, 28)
        self.btn_grow.setEnabled(False)
        self.btn_grow.clicked.connect(self.on_grow_selection)
        toolbar.addWidget(self.btn_grow)
        
        self.btn_shrink = QtWidgets.QPushButton()
        self.btn_shrink.setIcon(ViewLayerIcons.icon_shrink())
        self.btn_shrink.setToolTip("Thu hẹp vùng chọn Polygon Faces (Shrink)")
        self.btn_shrink.setFixedSize(28, 28)
        self.btn_shrink.setEnabled(False)
        self.btn_shrink.clicked.connect(self.on_shrink_selection)
        toolbar.addWidget(self.btn_shrink)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 2. BẢNG CÂY TRÌNH DIỄN (QTreeView)
        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_custom_context_menu)
        
        # TỐI ƯU UX: Double click để Select nhanh
        self.tree_view.doubleClicked.connect(self.on_tree_double_clicked)
        
        self.model = AnimeowTreeModel(self)
        self.tree_view.setModel(self.model)
        
        self.tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tree_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        
        self.tree_view.clicked.connect(self.on_tree_clicked)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.model.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.tree_view)
        
        self.model.populate_tree()
        self.tree_view.expandAll()

    # --- CÁC SLOT SỰ KIỆN ---

    def on_tree_double_clicked(self, index):
        """UX Tối ưu: Double click vào dòng bất kỳ để select các thành viên của nó"""
        if index.column() != 0:
            return
        set_name = index.data(QtCore.Qt.UserRole)
        if set_name and cmds.objExists(set_name):
            self.on_select_members(set_name)

    def on_tree_clicked(self, index):
        """Xử lý khi click vào cột Visibility"""
        if index.column() != 1:
            return
            
        set_name = index.data(QtCore.Qt.UserRole)
        item_type = index.data(QtCore.Qt.UserRole + 1)
        
        if not set_name or not cmds.objExists(set_name):
            return
            
        with MayaUndoChunk():
            if "layer" in item_type:  # click layer cha
                current_vis = True
                if cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_VISIBILITY, node=set_name, exists=True):
                    current_vis = cmds.getAttr(f"{set_name}.{AnimeowMeshGroupModel.ATTR_VISIBILITY}")
                new_vis = not current_vis
                
                cmds.setAttr(f"{set_name}.{AnimeowMeshGroupModel.ATTR_VISIBILITY}", new_vis)
                
                # Toggle tất cả group con bên trong (gộp hiển thị để tối ưu hóa)
                members = cmds.sets(set_name, query=True) or []
                group_sets = [m for m in members if (cmds.nodeType(m) == "objectSet" and 
                                                     cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_GROUP_LAYER, node=m, exists=True))]
                AnimeowMeshGroupModel.set_multiple_groups_visibility(group_sets, new_vis)
                        
            elif "group" in item_type:  # click group con
                current_vis = AnimeowMeshGroupModel.get_group_visibility(set_name)
                AnimeowMeshGroupModel.set_visibility(set_name, not current_vis)
                
        self.model.populate_tree()
        self.tree_view.expandAll()

    def on_selection_changed(self, selected, deselected):
        """Bật/tắt nút Grow & Shrink dựa trên group đang chọn"""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            self.btn_grow.setEnabled(False)
            self.btn_shrink.setEnabled(False)
            return
            
        index_col0 = indexes[0].siblingAtColumn(0)
        set_name = index_col0.data(QtCore.Qt.UserRole)
        item_type = index_col0.data(QtCore.Qt.UserRole + 1)
        
        if item_type == "group" and set_name and cmds.objExists(set_name):
            members = cmds.sets(set_name, query=True) or []
            faces = cmds.filterExpand(members, selectionMask=34) or []
            if faces:
                self.btn_grow.setEnabled(True)
                self.btn_shrink.setEnabled(True)
                return
                
        self.btn_grow.setEnabled(False)
        self.btn_shrink.setEnabled(False)

    def on_item_changed(self, item):
        """Xử lý đổi tên Selection Set trực tiếp khi user sửa trên cây"""
        if item.column() != 0:
            return
            
        old_set_name = item.data(QtCore.Qt.UserRole)
        new_name = item.text().strip()
        
        if not old_set_name or not cmds.objExists(old_set_name):
            return
            
        if not new_name:
            item.setText(old_set_name)
            return
            
        if old_set_name == new_name:
            return
            
        with MayaUndoChunk():
            try:
                actual_name = cmds.rename(old_set_name, new_name)
                
                self.model.blockSignals(True)
                self.model.populate_tree()
                self.tree_view.expandAll()
                self.model.blockSignals(False)
                
                self._reselect_by_set_name(actual_name)
            except Exception as e:
                cmds.warning("Không thể đổi tên set trong Maya: %s" % e)
                item.setText(old_set_name)

    def _reselect_by_set_name(self, set_name):
        for r in range(self.model.rowCount()):
            parent_item = self.model.item(r, 0)
            if parent_item.data(QtCore.Qt.UserRole) == set_name:
                self.tree_view.setCurrentIndex(parent_item.index())
                return
            for c in range(parent_item.rowCount()):
                child_item = parent_item.child(c, 0)
                if child_item.data(QtCore.Qt.UserRole) == set_name:
                    self.tree_view.setCurrentIndex(child_item.index())
                    return

    # --- CÁC ACTION TỪ TOOLBAR ---

    def on_toggle_all_visibility(self):
        all_sets = cmds.ls(type="objectSet") or []
        char_sets = [s for s in all_sets if cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_CHAR_LAYER, node=s, exists=True)]
        if not char_sets:
            return
            
        any_visible = False
        for s in char_sets:
            if cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_VISIBILITY, node=s, exists=True):
                if cmds.getAttr(f"{s}.{AnimeowMeshGroupModel.ATTR_VISIBILITY}"):
                    any_visible = True
                    break
                    
        target_state = not any_visible
        
        with MayaUndoChunk():
            all_groups = []
            for char_set in char_sets:
                cmds.setAttr(f"{char_set}.{AnimeowMeshGroupModel.ATTR_VISIBILITY}", target_state)
                members = cmds.sets(char_set, query=True) or []
                for m in members:
                    if (cmds.nodeType(m) == "objectSet" and 
                            cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_GROUP_LAYER, node=m, exists=True)):
                        all_groups.append(m)
            
            # Ẩn/hiện gộp chung cho toàn bộ các group con
            AnimeowMeshGroupModel.set_multiple_groups_visibility(all_groups, target_state)
                        
        self.model.populate_tree()
        self.tree_view.expandAll()

    def on_create_layer(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Tạo Layer mới", "Nhập tên Layer cha (Nhân vật):")
        if ok and text.strip():
            char_name = text.strip()
            AnimeowMeshGroupModel.create_character_layer(char_name)
            self.model.populate_tree()
            self.tree_view.expandAll()

    def on_create_group(self):
        indexes = self.tree_view.selectedIndexes()
        char_set = None
        
        if indexes:
            index_col0 = indexes[0].siblingAtColumn(0)
            set_name = index_col0.data(QtCore.Qt.UserRole)
            item_type = index_col0.data(QtCore.Qt.UserRole + 1)
            
            if item_type == "layer":
                char_set = set_name
            elif item_type == "group":
                parent_index = index_col0.parent()
                if parent_index.isValid():
                    char_set = parent_index.data(QtCore.Qt.UserRole)
                    
        if not char_set:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Layer cha hoặc Group con trên danh sách trước.")
            return
            
        text, ok = QtWidgets.QInputDialog.getText(self, "Tạo Group mới", "Nhập tên Group con hiển thị:")
        if ok and text.strip():
            group_name = text.strip()
            
            with MayaUndoChunk():
                group_set = AnimeowMeshGroupModel.create_group_layer(char_set, group_name)
                sel = cmds.ls(selection=True)
                if sel:
                    AnimeowMeshGroupModel.add_to_group(group_set, sel)
                    
            self.model.populate_tree()
            self.tree_view.expandAll()
            self._reselect_by_set_name(group_set)

    def on_grow_selection(self):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return
        index_col0 = indexes[0].siblingAtColumn(0)
        set_name = index_col0.data(QtCore.Qt.UserRole)
        
        if set_name and cmds.objExists(set_name):
            AnimeowMeshGroupModel.grow_group_selection(set_name)

    def on_shrink_selection(self):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return
        index_col0 = indexes[0].siblingAtColumn(0)
        set_name = index_col0.data(QtCore.Qt.UserRole)
        
        if set_name and cmds.objExists(set_name):
            AnimeowMeshGroupModel.shrink_group_selection(set_name)

    # --- CHUỘT PHẢI (CONTEXT MENU) ---

    def on_custom_context_menu(self, point):
        index = self.tree_view.indexAt(point)
        if not index.isValid():
            menu = QtWidgets.QMenu(self)
            action_new_layer = menu.addAction("Tạo Layer mới...")
            action_new_layer.triggered.connect(self.on_create_layer)
            menu.exec_(self.tree_view.mapToGlobal(point))
            return
            
        index_col0 = index.siblingAtColumn(0)
        set_name = index_col0.data(QtCore.Qt.UserRole)
        item_type = index_col0.data(QtCore.Qt.UserRole + 1)
        
        menu = QtWidgets.QMenu(self)
        
        action_select = menu.addAction("Select Members")
        action_select.triggered.connect(lambda: self.on_select_members(set_name))
        
        if item_type == "group":
            action_add = menu.addAction("Add Selected to Group")
            action_add.triggered.connect(lambda: self.on_add_selected(set_name))
            
            action_remove = menu.addAction("Remove Selected from Group")
            action_remove.triggered.connect(lambda: self.on_remove_selected(set_name))
            
        menu.addSeparator()
        
        action_rename = menu.addAction("Rename")
        action_rename.triggered.connect(lambda: self.tree_view.edit(index_col0))
        
        action_delete = menu.addAction("Delete Layer" if item_type == "layer" else "Delete Group")
        action_delete.triggered.connect(lambda: self.on_delete_item(set_name, item_type))
        
        menu.exec_(self.tree_view.mapToGlobal(point))

    def on_select_members(self, set_name):
        """Chọn các thành viên thuộc Set trên Viewport"""
        if not cmds.objExists(set_name):
            return
        members = cmds.sets(set_name, query=True) or []
        if members:
            actual_members = []
            for m in members:
                if cmds.nodeType(m) == "objectSet" and cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_GROUP_LAYER, node=m, exists=True):
                    sub_members = cmds.sets(m, query=True) or []
                    actual_members.extend(sub_members)
                else:
                    actual_members.append(m)
                    
            if actual_members:
                cmds.select(actual_members, replace=True)
            else:
                cmds.select(clear=True)
        else:
            cmds.select(clear=True)

    def on_add_selected(self, group_set):
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.warning("Vui lòng chọn các đối tượng hoặc components trong viewport trước.")
            return
        AnimeowMeshGroupModel.add_to_group(group_set, sel)
        self.on_selection_changed(None, None)

    def on_remove_selected(self, group_set):
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.warning("Vui lòng chọn các đối tượng hoặc components cần xoá khỏi Group.")
            return
        AnimeowMeshGroupModel.remove_from_group(group_set, sel)
        self.on_selection_changed(None, None)

    def on_delete_item(self, set_name, item_type):
        """Xóa Group hoặc Layer AN TOÀN - Không xóa các vật thể gốc trong Scene và bảo toàn Selection"""
        if not cmds.objExists(set_name):
            return
            
        with MayaUndoChunk():
            if item_type == "layer":
                res = QtWidgets.QMessageBox.question(
                    self, "Xóa Layer",
                    "Bạn có chắc chắn muốn xóa Layer cha '%s' (Mọi Group con sẽ bị gỡ bỏ, các Control và Mesh gốc vẫn giữ nguyên)?" % set_name,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if res == QtWidgets.QMessageBox.Yes:
                    members = cmds.sets(set_name, query=True) or []
                    group_sets = [m for m in members if (cmds.nodeType(m) == "objectSet" and 
                                                         cmds.attributeQuery(AnimeowMeshGroupModel.ATTR_GROUP_LAYER, node=m, exists=True))]
                    # Hiện lại members trước khi xóa group
                    for g in group_sets:
                        if not AnimeowMeshGroupModel.get_group_visibility(g):
                            AnimeowMeshGroupModel.set_visibility(g, True)
                        
                        # An toàn 100%: Giải phóng (clear) toàn bộ thành viên ra khỏi set trước khi delete node set
                        try:
                            cmds.sets(clear=g)
                        except Exception:
                            pass
                        cmds.delete(g)
                        
                    # Clear và xóa set cha
                    try:
                        cmds.sets(clear=set_name)
                    except Exception:
                        pass
                    cmds.delete(set_name)
            else:
                if not AnimeowMeshGroupModel.get_group_visibility(set_name):
                    AnimeowMeshGroupModel.set_visibility(set_name, True)
                
                # An toàn 100%: Giải phóng (clear) toàn bộ thành viên ra khỏi set trước khi delete node set
                try:
                    cmds.sets(clear=set_name)
                except Exception:
                    pass
                cmds.delete(set_name)
                
        self.model.populate_tree()
        self.tree_view.expandAll()


# ---------------------------------------------------------------------------
# Hàm show_animeow_ui() khởi chạy độc lập (Standalone)
# ---------------------------------------------------------------------------
def get_maya_main_window():
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == "MayaWindow":
            return widget
    return None


class AnimeowViewLayerStandaloneWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(AnimeowViewLayerStandaloneWindow, self).__init__(parent)
        
        self.setWindowTitle("Animeow View Layer v1.1")
        self.setObjectName("AnimeowViewLayerStandaloneWindow")
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.view_layer_ui = AnimeowViewLayerUI()
        self.setCentralWidget(self.view_layer_ui)
        
        self.setStyleSheet("""
            QWidget { background-color: #2B2B2B; color: #D4D4D4; font-family: "Segoe UI", sans-serif; font-size: 11px; }
            QPushButton { background-color: #3C3C3C; border: 1px solid #555555; border-radius: 4px; padding: 4px; }
            QPushButton:hover { background-color: #444444; border-color: #00BCD4; color: #FFFFFF; }
            QTreeView { background-color: #202020; border: 1px solid #3F3F3F; }
            QTreeView::item { height: 22px; }
            QTreeView::item:hover { background-color: #333333; }
            QTreeView::item:selected { background-color: #005060; color: #FFFFFF; }
            QHeaderView::section { background-color: #2D2D2D; color: #00BCD4; border: 1px solid #3F3F3F; font-weight: bold; }
        """)


def show_animeow_ui():
    sys_key = "_animeow_view_layer_standalone_ui"
    
    old_ui = getattr(sys, sys_key, None)
    if old_ui:
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        setattr(sys, sys_key, None)
        
    ui_instance = AnimeowViewLayerStandaloneWindow()
    setattr(sys, sys_key, ui_instance)
    
    ui_instance.resize(300, 450)
    ui_instance.show()
    return ui_instance
