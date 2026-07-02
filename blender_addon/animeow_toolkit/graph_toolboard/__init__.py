"""
__init__.py — Animeow Toolkit / Graph Toolboard
=================================================
Khai báo danh sách classes cho module Graph Toolboard.
"""

from . import properties
from . import operators
from . import panels

# Các sub-module này tự quản lý register/unregister qua hàm riêng
_sub_modules = (properties, operators, panels)


def module_register():
    """Đăng ký toàn bộ classes trong Graph Toolboard."""
    for mod in _sub_modules:
        mod.register()


def module_unregister():
    """Huỷ đăng ký toàn bộ classes trong Graph Toolboard."""
    for mod in reversed(_sub_modules):
        mod.unregister()
