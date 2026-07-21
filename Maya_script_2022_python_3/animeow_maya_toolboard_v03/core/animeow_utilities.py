# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

class SelectionUtility(object):
    """
    Lớp tiện ích hướng đối tượng dùng để quản lý, lọc và xác định các đối tượng đang được chọn trong Maya.
    """
    
    def __init__(self):
        """Khởi tạo và lưu trữ danh sách đối tượng được chọn tại thời điểm gọi"""
        self._selection = cmds.ls(sl=True) or []

    @property
    def selection(self):
        """Trả về danh sách các đối tượng được chọn ban đầu"""
        return self._selection

    def refresh(self):
        """Quét lại (refresh) danh sách các đối tượng đang được chọn hiện tại trong scene"""
        self._selection = cmds.ls(sl=True) or []
        return self._selection

    def get_count(self):
        """Trả về số lượng đối tượng đang chọn"""
        return len(self._selection)

    def is_empty(self):
        """Kiểm tra xem có đối tượng nào đang được chọn hay không"""
        return len(self._selection) == 0

    def get_first(self):
        """Trả về đối tượng đầu tiên được chọn (hoặc None nếu không chọn gì)"""
        return self._selection[0] if self._selection else None

    def get_last(self):
        """Trả về đối tượng cuối cùng được chọn (hoặc None nếu không chọn gì)"""
        return self._selection[-1] if self._selection else None

    def get_names(self):
        """Trả về danh sách tên của các đối tượng đang chọn"""
        return [obj for obj in self._selection]

    def get_short_names(self):
        """Trả về danh sách tên ngắn (không bao gồm đường dẫn phân cấp cha con '|')"""
        return [obj.split("|")[-1] for obj in self._selection]

    def get_namespaces(self):
        """Trả về danh sách chứa các namespace độc nhất của các vật thể đang chọn"""
        namespaces = set()
        for obj in self._selection:
            # Lấy phần tên ngắn (bỏ đường dẫn dài '|')
            short_name = obj.split("|")[-1]
            if ":" in short_name:
                # Lấy phần namespace (cắt bỏ phần tên node cuối cùng sau dấu ':' cuối cùng)
                parts = short_name.rsplit(":", 1)
                namespaces.add(parts[0])
            else:
                namespaces.add("")
        return list(namespaces)

    def filter_by_type(self, node_type):
        """
        Lọc danh sách chọn chỉ giữ lại các đối tượng thuộc kiểu node_type chỉ định
        (ví dụ: 'joint', 'transform', 'nurbsCurve')
        """
        filtered = []
        for obj in self._selection:
            if cmds.nodeType(obj) == node_type:
                filtered.append(obj)
            else:
                # Kiểm tra xem Shape của nó có khớp kiểu không (ví dụ đối với NURBS Curve)
                shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                for s in shapes:
                    if cmds.nodeType(s) == node_type:
                        filtered.append(obj)
                        break
        return filtered

    def get_shapes(self):
        """Trả về tất cả các node Shape thuộc các đối tượng đang chọn"""
        shapes = []
        for obj in self._selection:
            obj_shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            shapes.extend(obj_shapes)
        return shapes

    def has_components(self):
        """Kiểm tra xem lựa chọn hiện tại có chứa component (như vertex, edge, face, cv...) hay không"""
        for item in self._selection:
            if "." in item:
                return True
        return False

    def get_components(self):
        """Trả về danh sách các component được chọn (ví dụ: ['pSphere1.vtx[45]', ...])"""
        return [item for item in self._selection if "." in item]

    def validate_selection(self, min_count=1, max_count=None, expected_type=None, show_warning=True):
        """
        Kiểm tra tính hợp lệ của lựa chọn.
        Trả về (True, "") nếu hợp lệ, ngược lại trả về (False, "Thông báo lỗi").
        Nếu show_warning=True, sẽ hiển thị hộp thoại cảnh báo (confirmDialog) trong Maya.
        """
        count = self.get_count()
        
        # 1. Kiểm tra số lượng tối thiểu
        if count < min_count:
            msg = u"Vui lòng chọn ít nhất %d vật thể! (Hiện tại đang chọn: %d)" % (min_count, count)
            if show_warning:
                self._show_maya_warning(msg)
            return False, msg
            
        # 2. Kiểm tra số lượng tối đa
        if max_count is not None and count > max_count:
            msg = u"Vui lòng chọn tối đa %d vật thể! (Hiện tại đang chọn: %d)" % (max_count, count)
            if show_warning:
                self._show_maya_warning(msg)
            return False, msg

        # 3. Kiểm tra kiểu node
        if expected_type is not None:
            filtered = self.filter_by_type(expected_type)
            if len(filtered) < min_count:
                msg = u"Các vật thể được chọn phải thuộc kiểu: %s" % expected_type
                if show_warning:
                    self._show_maya_warning(msg)
                return False, msg
                
        return True, ""

    def _show_maya_warning(self, message):
        """Hiển thị hộp thoại cảnh báo trong Maya"""
        cmds.confirmDialog(
            title=u"Cảnh báo lựa chọn",
            message=message,
            button=[u"Đóng"],
            defaultButton=u"Đóng"
        )
