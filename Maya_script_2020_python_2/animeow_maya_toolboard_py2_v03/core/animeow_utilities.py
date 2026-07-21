# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

class SelectionUtility(object):
    """
    Lop tien ich huong doi tuong dung de quan ly, loc va xac dinh cac doi tuong dang duoc chon trong Maya.
    """
    
    def __init__(self):
        """Khoi tao va luu tru danh sach doi tuong duoc chon tai thoi diem goi"""
        self._selection = cmds.ls(sl=True) or []

    @property
    def selection(self):
        """Tra ve danh sach cac doi tuong duoc chon ban dau"""
        return self._selection

    def refresh(self):
        """Quet lai (refresh) danh sach cac doi tuong dang duoc chon hien tai trong scene"""
        self._selection = cmds.ls(sl=True) or []
        return self._selection

    def get_count(self):
        """Tra ve so luong doi tuong dang chon"""
        return len(self._selection)

    def is_empty(self):
        """Kiem tra xem co doi tuong nao dang duoc chon hay khong"""
        return len(self._selection) == 0

    def get_first(self):
        """Tra ve doi tuong dau tien duoc chon (hoac None neu khong chon gi)"""
        return self._selection[0] if self._selection else None

    def get_last(self):
        """Tra ve doi tuong cuoi cung duoc chon (hoac None neu khong chon gi)"""
        return self._selection[-1] if self._selection else None

    def get_names(self):
        """Tra ve danh sach ten cua cac doi tuong dang chon"""
        return [obj for obj in self._selection]

    def get_short_names(self):
        """Tra ve danh sach ten ngan (khong bao gom duong dan phan cap cha con '|')"""
        return [obj.split("|")[-1] for obj in self._selection]

    def get_namespaces(self):
        """Tra ve danh sach chua cac namespace doc nhat cua cac vat the dang chon"""
        namespaces = set()
        for obj in self._selection:
            # Lay phan ten ngan (bo duong dan dai '|')
            short_name = obj.split("|")[-1]
            if ":" in short_name:
                # Lay phan namespace (cat bo phan ten node cuoi cung sau dau ':' cuoi cung)
                parts = short_name.rsplit(":", 1)
                namespaces.add(parts[0])
            else:
                namespaces.add("")
        return list(namespaces)

    def filter_by_type(self, node_type):
        """
        Loc danh sach chon chi giu lai cac doi tuong thuoc kieu node_type chi dinh
        (vi du: 'joint', 'transform', 'nurbsCurve')
        """
        filtered = []
        for obj in self._selection:
            if cmds.nodeType(obj) == node_type:
                filtered.append(obj)
            else:
                # Kiem tra xem Shape cua no co khop kieu khong (vi du doi voi NURBS Curve)
                shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                for s in shapes:
                    if cmds.nodeType(s) == node_type:
                        filtered.append(obj)
                        break
        return filtered

    def get_shapes(self):
        """Tra ve tat ca cac node Shape thuoc cac doi tuong dang chon"""
        shapes = []
        for obj in self._selection:
            obj_shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            shapes.extend(obj_shapes)
        return shapes

    def has_components(self):
        """Kiem tra xem lua chon hien tai co chua component (nhu vertex, edge, face, cv...) hay khong"""
        for item in self._selection:
            if "." in item:
                return True
        return False

    def get_components(self):
        """Tra ve danh sach cac component duoc chon (vi du: ['pSphere1.vtx[45]', ...])"""
        return [item for item in self._selection if "." in item]

    def validate_selection(self, min_count=1, max_count=None, expected_type=None, show_warning=True):
        """
        Kiem tra tinh hop le cua lua chon.
        Tra ve (True, "") neu hop le, nguoc lai tra ve (False, "Thong bao loi").
        Neu show_warning=True, se hien thi hop thoai canh bao (confirmDialog) trong Maya.
        """
        count = self.get_count()
        
        # 1. Kiem tra so luong toi thieu
        if count < min_count:
            msg = u"Vui long chon it nhat %d vat the! (Hien tai dang chon: %d)" % (min_count, count)
            if show_warning:
                self._show_maya_warning(msg)
            return False, msg
            
        # 2. Kiem tra so luong toi da
        if max_count is not None and count > max_count:
            msg = u"Vui long chon toi da %d vat the! (Hien tai dang chon: %d)" % (max_count, count)
            if show_warning:
                self._show_maya_warning(msg)
            return False, msg

        # 3. Kiem tra kieu node
        if expected_type is not None:
            filtered = self.filter_by_type(expected_type)
            if len(filtered) < min_count:
                msg = u"Cac vat the duoc chon phai thuoc kieu: %s" % expected_type
                if show_warning:
                    self._show_maya_warning(msg)
                return False, msg
                
        return True, ""

    def _show_maya_warning(self, message):
        """Hien thi hop thoai canh bao trong Maya"""
        cmds.confirmDialog(
            title=u"Canh bao lua chon",
            message=message,
            button=[u"Dong"],
            defaultButton=u"Dong"
        )
