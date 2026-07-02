"""
base_panel.py — Animeow Toolkit
================================
Lớp cơ sở (Base Class) cho mọi Panel hiển thị trong 3D Viewport Sidebar.
Các module con kế thừa lớp này để tự động thống nhất vùng hiển thị
và tab Sidebar mà không cần khai báo lại.
"""


class AnimeowBasePanel:
    """Lớp cha chung cho mọi Panel trong hệ thống Animeow Toolkit.

    Attributes:
        bl_space_type: Hiển thị trong cửa sổ 3D Viewport.
        bl_region_type: Hiển thị ở vùng Sidebar (N-Panel).
        bl_category: Tên tab Sidebar sẽ là "Animeow".
        bl_options: Mặc định thu gọn (đóng) khi mới mở để giao diện gọn gàng.
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animeow'
    bl_options = {'DEFAULT_CLOSED'}
