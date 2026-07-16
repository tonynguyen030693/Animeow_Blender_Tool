# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui

from ..core import smart_link, playblast, arc_tracker, world_bake, round_tool, space_order_tool, retarget_tool, mirror_tool, temp_pivot, shelf, tween_machine, animeow_view_layer

# ---------------------------------------------------------------------------
# AnimBot-inspired Professional Color Palette
# ---------------------------------------------------------------------------
ACCENT       = "#00BCD4"    # Cyan chủ đạo (giữ nguyên theo yêu cầu)
ACCENT_HOVER = "#00E5FF"    # Cyan sáng hơn khi hover
ACCENT_DIM   = "#00838F"    # Cyan tối cho pressed / accent button
ACCENT_BG    = "#006064"    # Cyan rất tối cho pressed accent

QSS_STYLE = """
/* ── Base ── */
QWidget {
    background-color: #3A3A3A;
    color: #D4D4D4;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 11px;
}

/* ── GroupBox: viền mỏng, nhạt ── */
QGroupBox {
    border: 1px solid #4A4A4A;
    border-radius: 4px;
    margin-top: 14px;
    padding: 8px 6px 6px 6px;
    font-weight: bold;
    font-size: 11px;
    color: #00BCD4;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    color: #00BCD4;
}

/* ── Buttons ── */
QPushButton {
    background-color: #464646;
    color: #D4D4D4;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #525252;
    border-color: #00BCD4;
    color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #2A2A2A;
}
QPushButton#accent_btn {
    background-color: #00838F;
    color: #FFFFFF;
    border: 1px solid #00BCD4;
}
QPushButton#accent_btn:hover {
    background-color: #0097A7;
    border-color: #00E5FF;
}
QPushButton#accent_btn:pressed {
    background-color: #006064;
}

/* ── Inputs ── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #2E2E2E;
    border: 1px solid #4A4A4A;
    border-radius: 3px;
    padding: 3px 5px;
    color: #E0E0E0;
    font-size: 11px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #00BCD4;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QComboBox QAbstractItemView {
    background-color: #2E2E2E;
    border: 1px solid #4A4A4A;
    color: #E0E0E0;
    selection-background-color: #00838F;
    selection-color: #FFFFFF;
}

/* ── Tabs: flat underline style ── */
QTabWidget::pane {
    border-top: 1px solid #4A4A4A;
    background-color: #3A3A3A;
}
QTabBar::tab {
    background-color: transparent;
    color: #888888;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 12px;
    margin-right: 2px;
    font-size: 11px;
    font-weight: bold;
}
QTabBar::tab:selected {
    color: #00BCD4;
    border-bottom: 2px solid #00BCD4;
}
QTabBar::tab:hover:!selected {
    color: #D4D4D4;
    border-bottom: 2px solid #555555;
}

/* ── Table ── */
QTableWidget {
    gridline-color: #3A3A3A;
    border: 1px solid #4A4A4A;
    background-color: #2E2E2E;
    color: #D4D4D4;
    border-radius: 3px;
    font-size: 11px;
}
QTableWidget::item:selected {
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

/* ── Checkbox ── */
QCheckBox {
    spacing: 5px;
    font-size: 11px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #2E2E2E;
}
QCheckBox::indicator:checked {
    background-color: #00BCD4;
    border-color: #00BCD4;
}
QCheckBox::indicator:hover {
    border-color: #00BCD4;
}

/* ── ScrollBar: slim ── */
QScrollBar:vertical {
    border: none;
    background-color: #333333;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #555555;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background-color: #00BCD4;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #2E2E2E;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 12px;
    height: 12px;
    margin: -4px 0;
    background: #00BCD4;
    border-radius: 6px;
}
QSlider::handle:horizontal:hover {
    background: #00E5FF;
}

/* ── Label ── */
QLabel {
    font-size: 11px;
}

/* ── ToolTip ── */
QToolTip {
    background-color: #2E2E2E;
    color: #E0E0E0;
    border: 1px solid #00BCD4;
    padding: 4px;
    font-size: 11px;
}

/* ── ProgressBar ── */
QProgressBar {
    border: 1px solid #4A4A4A;
    border-radius: 3px;
    background-color: #2E2E2E;
    text-align: center;
    color: #D4D4D4;
    font-size: 10px;
}
QProgressBar::chunk {
    background-color: #00BCD4;
    border-radius: 2px;
}
"""

# ---------------------------------------------------------------------------
# AnimeowIcons — Bộ icon vector QPainter phong cách AnimBot (flat, monochrome)
# ---------------------------------------------------------------------------
class AnimeowIcons:
    """Vẽ icon vector inline bằng QPainter, không cần file ảnh bên ngoài."""

    @staticmethod
    def _create_pixmap(size, draw_func, color=None):
        """Helper: tạo QPixmap trong suốt và gọi draw_func(painter, rect)."""
        if color is None:
            color = QtGui.QColor(ACCENT)
        pix = QtGui.QPixmap(size, size)
        pix.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        pen = QtGui.QPen(color, 1.6, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(QtCore.Qt.NoBrush)
        rect = QtCore.QRectF(2, 2, size - 4, size - 4)
        draw_func(p, rect, color)
        p.end()
        return pix

    @staticmethod
    def make_icon(size, draw_func, color=None):
        return QtGui.QIcon(AnimeowIcons._create_pixmap(size, draw_func, color))

    # ── Individual icon draw functions ──

    @staticmethod
    def _draw_link(p, r, c):
        """Mắt xích — Smart Link"""
        cx, cy = r.center().x(), r.center().y()
        w, h = r.width(), r.height()
        # Vòng tròn trái
        p.drawEllipse(QtCore.QPointF(cx - w*0.18, cy), w*0.22, h*0.3)
        # Vòng tròn phải
        p.drawEllipse(QtCore.QPointF(cx + w*0.18, cy), w*0.22, h*0.3)

    @staticmethod
    def _draw_bake(p, r, c):
        """Hình vuông + sóng nhiệt — Bake"""
        m = r.adjusted(r.width()*0.1, r.height()*0.3, -r.width()*0.1, 0)
        p.drawRoundedRect(m, 2, 2)
        # 3 sóng nhiệt phía trên
        for i, dx in enumerate([-0.2, 0.0, 0.2]):
            x = r.center().x() + r.width() * dx
            path = QtGui.QPainterPath()
            y0 = m.top() - 2
            path.moveTo(x, y0)
            path.cubicTo(x - 2, y0 - 4, x + 2, y0 - 7, x, y0 - 10)
            p.drawPath(path)

    @staticmethod
    def _draw_curve(p, r, c):
        """Đường cong S — Curve Editor"""
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.bottom())
        path.cubicTo(r.center().x(), r.bottom(),
                     r.center().x(), r.top(),
                     r.right(), r.top())
        p.drawPath(path)

    @staticmethod
    def _draw_key(p, r, c):
        """Hình thoi — Keyframe"""
        cx, cy = r.center().x(), r.center().y()
        s = min(r.width(), r.height()) * 0.38
        poly = QtGui.QPolygonF([
            QtCore.QPointF(cx, cy - s),
            QtCore.QPointF(cx + s, cy),
            QtCore.QPointF(cx, cy + s),
            QtCore.QPointF(cx - s, cy),
        ])
        p.setBrush(c)
        p.drawPolygon(poly)
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_mirror(p, r, c):
        """2 mũi tên đối xứng — Mirror"""
        cx = r.center().x()
        # Đường dọc giữa
        p.drawLine(QtCore.QPointF(cx, r.top()), QtCore.QPointF(cx, r.bottom()))
        # Mũi tên trái
        p.drawLine(QtCore.QPointF(r.left(), r.center().y()), QtCore.QPointF(cx - 3, r.center().y()))
        p.drawLine(QtCore.QPointF(r.left(), r.center().y()), QtCore.QPointF(r.left() + 3, r.center().y() - 3))
        p.drawLine(QtCore.QPointF(r.left(), r.center().y()), QtCore.QPointF(r.left() + 3, r.center().y() + 3))
        # Mũi tên phải
        p.drawLine(QtCore.QPointF(r.right(), r.center().y()), QtCore.QPointF(cx + 3, r.center().y()))
        p.drawLine(QtCore.QPointF(r.right(), r.center().y()), QtCore.QPointF(r.right() - 3, r.center().y() - 3))
        p.drawLine(QtCore.QPointF(r.right(), r.center().y()), QtCore.QPointF(r.right() - 3, r.center().y() + 3))

    @staticmethod
    def _draw_play(p, r, c):
        """Tam giác play — Playblast"""
        poly = QtGui.QPolygonF([
            QtCore.QPointF(r.left() + r.width()*0.2, r.top()),
            QtCore.QPointF(r.right(), r.center().y()),
            QtCore.QPointF(r.left() + r.width()*0.2, r.bottom()),
        ])
        p.setBrush(c)
        p.drawPolygon(poly)
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_arc(p, r, c):
        """Đường cong + 3 chấm — Arc Tracker"""
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.bottom() - r.height()*0.2)
        path.quadTo(r.center().x(), r.top() - r.height()*0.1,
                    r.right(), r.bottom() - r.height()*0.2)
        p.drawPath(path)
        # 3 chấm trên arc
        dot_r = 2.0
        p.setBrush(c)
        for t in [0.2, 0.5, 0.8]:
            pt = path.pointAtPercent(t)
            p.drawEllipse(pt, dot_r, dot_r)
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_round(p, r, c):
        """Hình tròn + dấu thập phân — Round Tool"""
        cx, cy = r.center().x(), r.center().y()
        rad = min(r.width(), r.height()) * 0.38
        p.drawEllipse(QtCore.QPointF(cx, cy), rad, rad)
        # Chấm thập phân
        p.setBrush(c)
        p.drawEllipse(QtCore.QPointF(cx, cy), 1.5, 1.5)
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_constraint(p, r, c):
        """Ổ khóa nhỏ — Constraint"""
        cx, cy = r.center().x(), r.center().y()
        w, h = r.width(), r.height()
        # Vòng cung trên
        arc_r = QtCore.QRectF(cx - w*0.2, r.top(), w*0.4, h*0.5)
        p.drawArc(arc_r, 0, 180 * 16)
        # Thân khóa
        body = QtCore.QRectF(cx - w*0.28, cy - h*0.05, w*0.56, h*0.45)
        p.setBrush(c)
        p.drawRoundedRect(body, 2, 2)
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_pivot(p, r, c):
        """Chữ thập + vòng tròn — Temp Pivot"""
        cx, cy = r.center().x(), r.center().y()
        s = min(r.width(), r.height()) * 0.4
        p.drawLine(QtCore.QPointF(cx - s, cy), QtCore.QPointF(cx + s, cy))
        p.drawLine(QtCore.QPointF(cx, cy - s), QtCore.QPointF(cx, cy + s))
        p.drawEllipse(QtCore.QPointF(cx, cy), s * 0.5, s * 0.5)

    @staticmethod
    def _draw_euler(p, r, c):
        """Mũi tên xoay vòng — Euler Filter"""
        cx, cy = r.center().x(), r.center().y()
        rad = min(r.width(), r.height()) * 0.35
        arc_rect = QtCore.QRectF(cx - rad, cy - rad, rad * 2, rad * 2)
        p.drawArc(arc_rect, 30 * 16, 280 * 16)
        # Mũi tên ở cuối arc
        angle_end = 310  # degrees
        import math
        ex = cx + rad * math.cos(math.radians(angle_end))
        ey = cy - rad * math.sin(math.radians(angle_end))
        p.drawLine(QtCore.QPointF(ex, ey), QtCore.QPointF(ex + 3, ey - 3))
        p.drawLine(QtCore.QPointF(ex, ey), QtCore.QPointF(ex - 1, ey - 4))

    @staticmethod
    def _draw_star(p, r, c):
        """Ngôi sao 5 cánh — Favorite"""
        import math
        cx, cy = r.center().x(), r.center().y()
        R = min(r.width(), r.height()) * 0.42
        r2 = R * 0.4
        pts = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            radius = R if i % 2 == 0 else r2
            pts.append(QtCore.QPointF(cx + radius * math.cos(angle),
                                      cy + radius * math.sin(angle)))
        p.setBrush(c)
        p.drawPolygon(QtGui.QPolygonF(pts))
        p.setBrush(QtCore.Qt.NoBrush)

    @staticmethod
    def _draw_graph(p, r, c):
        """Biểu đồ sóng — Graph Editor"""
        path = QtGui.QPainterPath()
        path.moveTo(r.left(), r.center().y())
        w4 = r.width() * 0.25
        path.cubicTo(r.left() + w4, r.top(),
                     r.left() + w4*2, r.bottom(),
                     r.left() + w4*3, r.center().y())
        path.lineTo(r.right(), r.center().y())
        p.drawPath(path)

    @staticmethod
    def _draw_folder(p, r, c):
        """Thư mục — File / Folder"""
        tab_w = r.width() * 0.35
        tab_h = r.height() * 0.15
        body = r.adjusted(0, tab_h, 0, 0)
        p.drawRoundedRect(body, 2, 2)
        # Tab nhỏ trên
        tab = QtCore.QRectF(r.left(), r.top(), tab_w, tab_h + 2)
        p.drawRoundedRect(tab, 2, 2)

    @staticmethod
    def _draw_shield(p, r, c):
        """Khiên — Antivirus"""
        path = QtGui.QPainterPath()
        cx = r.center().x()
        path.moveTo(cx, r.top())
        path.lineTo(r.right(), r.top() + r.height()*0.2)
        path.quadTo(r.right(), r.bottom() - r.height()*0.1,
                    cx, r.bottom())
        path.quadTo(r.left(), r.bottom() - r.height()*0.1,
                    r.left(), r.top() + r.height()*0.2)
        path.closeSubpath()
        p.drawPath(path)
        # Checkmark
        p.drawLine(QtCore.QPointF(cx - r.width()*0.15, r.center().y()),
                   QtCore.QPointF(cx - r.width()*0.02, r.center().y() + r.height()*0.12))
        p.drawLine(QtCore.QPointF(cx - r.width()*0.02, r.center().y() + r.height()*0.12),
                   QtCore.QPointF(cx + r.width()*0.18, r.center().y() - r.height()*0.12))

    @staticmethod
    def _draw_save(p, r, c):
        """Đĩa mềm — Save"""
        p.drawRoundedRect(r, 2, 2)
        # Khe đĩa trên
        slot = QtCore.QRectF(r.left() + r.width()*0.25, r.top(),
                             r.width()*0.5, r.height()*0.3)
        p.drawRect(slot)
        # Label dưới
        label = QtCore.QRectF(r.left() + r.width()*0.15, r.center().y() + 1,
                              r.width()*0.7, r.height()*0.35)
        p.drawRect(label)

    @staticmethod
    def _draw_reset(p, r, c):
        """Mũi tên xoay vòng — Reset"""
        cx, cy = r.center().x(), r.center().y()
        rad = min(r.width(), r.height()) * 0.35
        arc_rect = QtCore.QRectF(cx - rad, cy - rad, rad*2, rad*2)
        p.drawArc(arc_rect, 60*16, 240*16)
        # Mũi tên
        import math
        ex = cx + rad * math.cos(math.radians(60))
        ey = cy - rad * math.sin(math.radians(60))
        p.drawLine(QtCore.QPointF(ex, ey), QtCore.QPointF(ex + 4, ey))
        p.drawLine(QtCore.QPointF(ex, ey), QtCore.QPointF(ex, ey + 4))

    @staticmethod
    def _draw_clean(p, r, c):
        """Chổi quét — Clean Keys"""
        # Cán chổi
        p.drawLine(QtCore.QPointF(r.right() - r.width()*0.15, r.top() + r.height()*0.15),
                   QtCore.QPointF(r.center().x(), r.center().y()))
        # Đầu chổi
        broom = QtCore.QRectF(r.left(), r.center().y() - r.height()*0.05,
                              r.width()*0.55, r.height()*0.52)
        p.drawRoundedRect(broom, 3, 3)
        # 3 đường ngang trên đầu chổi
        for i in range(3):
            y = broom.top() + broom.height() * (0.3 + i * 0.22)
            p.drawLine(QtCore.QPointF(broom.left() + 3, y),
                       QtCore.QPointF(broom.right() - 3, y))

    @staticmethod
    def _draw_tween(p, r, c):
        """2 chấm + đường nội suy — Tween Machine"""
        dot_r = 2.5
        y = r.center().y()
        x1 = r.left() + r.width() * 0.2
        x2 = r.right() - r.width() * 0.2
        p.setBrush(c)
        p.drawEllipse(QtCore.QPointF(x1, y), dot_r, dot_r)
        p.drawEllipse(QtCore.QPointF(x2, y), dot_r, dot_r)
        p.setBrush(QtCore.Qt.NoBrush)
        # Đường nối
        pen = p.pen()
        pen.setStyle(QtCore.Qt.DashLine)
        p.setPen(pen)
        p.drawLine(QtCore.QPointF(x1 + dot_r + 1, y), QtCore.QPointF(x2 - dot_r - 1, y))
        pen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(pen)

    @staticmethod
    def _draw_world(p, r, c):
        """Quả cầu — World Space"""
        cx, cy = r.center().x(), r.center().y()
        rad = min(r.width(), r.height()) * 0.4
        p.drawEllipse(QtCore.QPointF(cx, cy), rad, rad)
        # Đường kinh tuyến
        p.drawEllipse(QtCore.QPointF(cx, cy), rad*0.45, rad)
        # Đường vĩ tuyến
        p.drawLine(QtCore.QPointF(cx - rad, cy), QtCore.QPointF(cx + rad, cy))

    @staticmethod
    def _draw_retarget(p, r, c):
        """2 nhân vật nối nhau — Retarget"""
        # Nhân vật trái (nhỏ)
        lx = r.left() + r.width()*0.2
        ly = r.center().y()
        p.drawEllipse(QtCore.QPointF(lx, ly - r.height()*0.2), 3, 3)
        p.drawLine(QtCore.QPointF(lx, ly - r.height()*0.2 + 3), QtCore.QPointF(lx, ly + r.height()*0.15))
        # Nhân vật phải
        rx_pos = r.right() - r.width()*0.2
        p.drawEllipse(QtCore.QPointF(rx_pos, ly - r.height()*0.2), 3, 3)
        p.drawLine(QtCore.QPointF(rx_pos, ly - r.height()*0.2 + 3), QtCore.QPointF(rx_pos, ly + r.height()*0.15))
        # Mũi tên nối
        p.drawLine(QtCore.QPointF(lx + 5, ly), QtCore.QPointF(rx_pos - 5, ly))
        p.drawLine(QtCore.QPointF(rx_pos - 5, ly), QtCore.QPointF(rx_pos - 8, ly - 2))
        p.drawLine(QtCore.QPointF(rx_pos - 5, ly), QtCore.QPointF(rx_pos - 8, ly + 2))

    @staticmethod
    def _draw_outliner(p, r, c):
        """Danh sách phân cấp — Outliner"""
        y = r.top()
        step = r.height() / 4.5
        for i in range(4):
            indent = 0 if i == 0 else r.width() * 0.15
            p.drawLine(QtCore.QPointF(r.left() + indent, y + step*(i+0.5)),
                       QtCore.QPointF(r.right() - 2, y + step*(i+0.5)))
            if i > 0:
                p.drawLine(QtCore.QPointF(r.left() + indent - 3, y + step*(i-0.2)),
                           QtCore.QPointF(r.left() + indent - 3, y + step*(i+0.5)))

    @staticmethod
    def _draw_launch(p, r, c):
        """Tên lửa — Launcher"""
        path = QtGui.QPainterPath()
        cx = r.center().x()
        path.moveTo(cx, r.top())
        path.quadTo(r.right() - r.width()*0.15, r.center().y(),
                    cx + r.width()*0.1, r.bottom() - r.height()*0.2)
        path.lineTo(cx, r.bottom())
        path.lineTo(cx - r.width()*0.1, r.bottom() - r.height()*0.2)
        path.quadTo(r.left() + r.width()*0.15, r.center().y(),
                    cx, r.top())
        p.drawPath(path)
        # Ngọn lửa nhỏ
        p.drawLine(QtCore.QPointF(cx, r.bottom()), QtCore.QPointF(cx, r.bottom() + 2))

    @staticmethod
    def _draw_compact(p, r, c):
        """3 gạch ngang — Menu/Compact"""
        for i in range(3):
            y = r.top() + r.height() * (0.25 + i * 0.25)
            p.drawLine(QtCore.QPointF(r.left() + 2, y), QtCore.QPointF(r.right() - 2, y))

    @staticmethod
    def _draw_space_order(p, r, c):
        """Mũi tên xoay 3 trục — Space & Rotate Order"""
        cx, cy = r.center().x(), r.center().y()
        s = min(r.width(), r.height()) * 0.35
        # 3 mũi tên xoay
        p.drawLine(QtCore.QPointF(cx, cy), QtCore.QPointF(cx + s, cy))
        p.drawLine(QtCore.QPointF(cx, cy), QtCore.QPointF(cx, cy - s))
        p.drawLine(QtCore.QPointF(cx, cy), QtCore.QPointF(cx - s*0.6, cy + s*0.6))
        # Mũi nhọn
        p.drawLine(QtCore.QPointF(cx + s, cy), QtCore.QPointF(cx + s - 3, cy - 2))
        p.drawLine(QtCore.QPointF(cx, cy - s), QtCore.QPointF(cx - 2, cy - s + 3))

    # ── Factory Methods ──

    @staticmethod
    def icon_link(sz=18):      return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_link)
    @staticmethod
    def icon_bake(sz=18):      return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_bake)
    @staticmethod
    def icon_curve(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_curve)
    @staticmethod
    def icon_key(sz=18):       return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_key)
    @staticmethod
    def icon_mirror(sz=18):    return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_mirror)
    @staticmethod
    def icon_play(sz=18):      return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_play)
    @staticmethod
    def icon_arc(sz=18):       return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_arc)
    @staticmethod
    def icon_round(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_round)
    @staticmethod
    def icon_constraint(sz=18): return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_constraint)
    @staticmethod
    def icon_pivot(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_pivot)
    @staticmethod
    def icon_euler(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_euler)
    @staticmethod
    def icon_star(sz=18):      return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_star)
    @staticmethod
    def icon_graph(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_graph)
    @staticmethod
    def icon_folder(sz=18):    return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_folder)
    @staticmethod
    def icon_shield(sz=18):    return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_shield)
    @staticmethod
    def icon_save(sz=18):      return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_save)
    @staticmethod
    def icon_reset(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_reset)
    @staticmethod
    def icon_clean(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_clean)
    @staticmethod
    def icon_tween(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_tween)
    @staticmethod
    def icon_world(sz=18):     return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_world)
    @staticmethod
    def icon_retarget(sz=18):  return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_retarget)
    @staticmethod
    def icon_outliner(sz=18):  return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_outliner)
    @staticmethod
    def icon_launch(sz=18):    return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_launch)
    @staticmethod
    def icon_compact(sz=18):   return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_compact)
    @staticmethod
    def icon_space_order(sz=18): return AnimeowIcons.make_icon(sz, AnimeowIcons._draw_space_order)

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
        
    mel.eval("rehash;")
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
    OP_PB_CUSTOM_DIR = "AnimeowTbPbCustomDir"
    OP_AT_SHOW_TICKS = "AnimeowTbAtShowTicks"
    OP_AT_SHOW_KEYS = "AnimeowTbAtShowKeys"
    OP_AT_TICK_SIZE = "AnimeowTbAtTickSize"
    OP_WB_CHANNELS = "AnimeowTbWbChannels"
    OP_WB_STEP = "AnimeowTbWbStep"
    OP_WB_SMART_CLEAN = "AnimeowTbWbSmartClean"
    OP_RT_PRECISION = "AnimeowTbRtPrecision"
    OP_RT_TARGET = "AnimeowTbRtTarget"
    
    # Overlapper Settings OptionVars
    OP_OV_SOFTNESS = "AnimeowTbOvSoftness"
    OP_OV_SCALE = "AnimeowTbOvScale"
    OP_OV_WIND_ENABLED = "AnimeowTbOvWindEnabled"
    OP_OV_WIND_SCALE = "AnimeowTbOvWindScale"
    OP_OV_WIND_SPEED = "AnimeowTbOvWindSpeed"
    OP_OV_SKIP_FIRST = "AnimeowTbOvSkipFirst"
    OP_OV_TRANSLATE = "AnimeowTbOvTranslate"
    OP_OV_HIERARCHY = "AnimeowTbOvHierarchy"
    OP_OV_CYCLE = "AnimeowTbOvCycle"
    OP_OV_BAKE_LAYER = "AnimeowTbOvBakeLayer"
    OP_OV_ADAPTIVE_SCALE = "AnimeowTbOvAdaptiveScale"
    OP_OV_SEL_SET = "AnimeowTbOvSelSet"

    def __init__(self, parent=None, standalone_tab=None):
        self.standalone_tab = standalone_tab
        
        if standalone_tab is not None:
            if standalone_tab == 0 or standalone_tab == "smart_link":
                self.WINDOW_TITLE = "Constraint & Smart Link"
                self.WORKSPACE_CONTROL_NAME = "AnimeowSmartLinkWorkspaceControl"
            elif standalone_tab == "world_bake":
                self.WINDOW_TITLE = "Smart World Bake & Pivot"
                self.WORKSPACE_CONTROL_NAME = "AnimeowWorldBakeWorkspaceControl"
            elif standalone_tab == 1:
                self.WINDOW_TITLE = "Curve & Motion"
                self.WORKSPACE_CONTROL_NAME = "AnimeowCurveWorkspaceControl"
            elif standalone_tab == 2:
                self.WINDOW_TITLE = "Rig & Mirror"
                self.WORKSPACE_CONTROL_NAME = "AnimeowRigWorkspaceControl"
            elif standalone_tab == 3:
                self.WINDOW_TITLE = "Output & Scene"
                self.WORKSPACE_CONTROL_NAME = "AnimeowOutputWorkspaceControl"
            elif standalone_tab == "arc_tracker":
                self.WINDOW_TITLE = "Arc Tracker"
                self.WORKSPACE_CONTROL_NAME = "AnimeowArcWorkspaceControl"
            elif standalone_tab == "overlapper":
                self.WINDOW_TITLE = "Overlapper"
                self.WORKSPACE_CONTROL_NAME = "AnimeowOverlapperWorkspaceControl"
            elif standalone_tab == "round_tool":
                self.WINDOW_TITLE = "Làm tròn số"
                self.WORKSPACE_CONTROL_NAME = "AnimeowRoundWorkspaceControl"
                
        super(AnimeowMayaToolboardUI, self).__init__(parent=parent)
        self._is_tweening_drag = False
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setStyleSheet(QSS_STYLE)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(4)
        
        # Header Layout — compact, professional
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(4, 0, 4, 0)
        header_layout.setSpacing(6)
        
        self.title_lbl = QtWidgets.QLabel("ANIMEOW TOOLBOARD")
        self.title_lbl.setStyleSheet("color: #00BCD4; font-weight: bold; font-size: 10px; letter-spacing: 1px;")
        header_layout.addWidget(self.title_lbl)
        
        version_lbl = QtWidgets.QLabel("v5.0")
        version_lbl.setStyleSheet("color: #666666; font-size: 9px;")
        header_layout.addWidget(version_lbl)
        header_layout.addStretch()
        
        self.compact_toggle_btn = QtWidgets.QPushButton()
        self.compact_toggle_btn.setIcon(AnimeowIcons.icon_compact(14))
        self.compact_toggle_btn.setCheckable(True)
        self.compact_toggle_btn.setFixedSize(22, 22)
        self.compact_toggle_btn.setToolTip("Chế độ gọn (Compact Mode)")
        self.compact_toggle_btn.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 3px; } QPushButton:hover { background-color: #4A4A4A; } QPushButton:checked { background-color: #00838F; }")
        self.compact_toggle_btn.clicked.connect(self.on_toggle_compact_mode)
        header_layout.addWidget(self.compact_toggle_btn)
        
        self.main_layout.addLayout(header_layout)
        
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        
        # Left compact toolbar (hidden by default)
        self.compact_toolbar = QtWidgets.QWidget()
        self.compact_toolbar.setFixedWidth(38)
        self.compact_toolbar.setStyleSheet("""
            QWidget {
                background-color: #212121;
                border-right: 1px solid #333333;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 15px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.compact_toolbar_layout = QtWidgets.QVBoxLayout(self.compact_toolbar)
        self.compact_toolbar_layout.setContentsMargins(4, 6, 4, 4)
        self.compact_toolbar_layout.setSpacing(4)
        
        compact_icon_funcs = [
            AnimeowIcons.icon_link,
            AnimeowIcons.icon_curve,
            AnimeowIcons.icon_mirror,
            AnimeowIcons.icon_play,
            AnimeowIcons.icon_launch,
        ]
        compact_tooltips = [
            "Space & Bake",
            "Curve & Motion",
            "Rig & Mirror",
            "Output & Scene",
            "Launchers"
        ]
        self.compact_buttons = []
        for i, icon_func in enumerate(compact_icon_funcs):
            btn = QtWidgets.QPushButton()
            btn.setIcon(icon_func(16))
            btn.setFixedSize(28, 28)
            btn.setToolTip(compact_tooltips[i])
            def make_click(idx):
                return lambda checked=False: self.tab_widget.setCurrentIndex(idx)
            btn.clicked.connect(make_click(i))
            self.compact_toolbar_layout.addWidget(btn)
            self.compact_buttons.append(btn)
        self.compact_toolbar_layout.addStretch()
        
        self.content_layout.addWidget(self.compact_toolbar)
        self.compact_toolbar.hide() # Hidden by default
        
        # QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.tabBar().setElideMode(QtCore.Qt.ElideNone)
        self.tab_widget.tabBar().setUsesScrollButtons(True)
        self.content_layout.addWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.main_layout.addLayout(self.content_layout)
        
        self.build_ui()
        self.load_settings()
    def build_ui(self):
        # Helper function to wrap widgets in scroll area
        def wrap_in_scroll(widget):
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QtWidgets.QScrollArea.NoFrame)
            # Thiết lập nền tối đồng bộ
            scroll.setStyleSheet("QScrollArea { background-color: #2D2D2D; border: none; }")
            scroll.setWidget(widget)
            return scroll

        # Khởi tạo QTabWidget
        # Khói tạo QTabWidget
        # Tab widget is already initialized in __init__
        pass
        
        # =========================================================================
        # --- TAB 1: LINK & BAKE (LIÊN KẾT & NƯỚNG) ---
        # =========================================================================
        tab1 = QtWidgets.QWidget(self)
        tab1.hide()
        tab1_layout = QtWidgets.QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(6, 8, 6, 6)
        tab1_layout.setSpacing(8)
        
        t1_title = QtWidgets.QLabel("CONSTRAINT, SPACE & BAKE MANAGER")
        t1_title.setAlignment(QtCore.Qt.AlignCenter)
        t1_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00BCD4;")
        tab1_layout.addWidget(t1_title)
        
        # GroupBox 0: Quick Constraint
        qc_group = QtWidgets.QGroupBox("Quick Constraint (Tạo Constraint nhanh)")
        qc_layout = QtWidgets.QVBoxLayout(qc_group)
        qc_layout.setContentsMargins(8, 8, 8, 8)
        qc_layout.setSpacing(6)
        
        # Checkbox Maintain Offset
        mo_row = QtWidgets.QHBoxLayout()
        self.qc_mo_cb = QtWidgets.QCheckBox("Maintain Offset")
        self.qc_mo_cb.setChecked(True)
        mo_row.addWidget(self.qc_mo_cb)
        mo_row.addStretch()
        qc_layout.addLayout(mo_row)
        
        # Checkbox Translate axes
        t_row = QtWidgets.QHBoxLayout()
        t_row.addWidget(QtWidgets.QLabel("Translate (Dịch chuyển):"))
        self.qc_tx_cb = QtWidgets.QCheckBox("X")
        self.qc_tx_cb.setChecked(True)
        self.qc_ty_cb = QtWidgets.QCheckBox("Y")
        self.qc_ty_cb.setChecked(True)
        self.qc_tz_cb = QtWidgets.QCheckBox("Z")
        self.qc_tz_cb.setChecked(True)
        t_row.addWidget(self.qc_tx_cb)
        t_row.addWidget(self.qc_ty_cb)
        t_row.addWidget(self.qc_tz_cb)
        t_row.addStretch()
        qc_layout.addLayout(t_row)
        
        # Checkbox Rotate axes
        r_row = QtWidgets.QHBoxLayout()
        r_row.addWidget(QtWidgets.QLabel("Rotate (Xoay):            "))
        self.qc_rx_cb = QtWidgets.QCheckBox("X")
        self.qc_rx_cb.setChecked(True)
        self.qc_ry_cb = QtWidgets.QCheckBox("Y")
        self.qc_ry_cb.setChecked(True)
        self.qc_rz_cb = QtWidgets.QCheckBox("Z")
        self.qc_rz_cb.setChecked(True)
        r_row.addWidget(self.qc_rx_cb)
        r_row.addWidget(self.qc_ry_cb)
        r_row.addWidget(self.qc_rz_cb)
        r_row.addStretch()
        qc_layout.addLayout(r_row)
        
        # Hàng nút bấm
        btns_layout = QtWidgets.QHBoxLayout()
        btn_parent = QtWidgets.QPushButton("Parent")
        btn_parent.setFixedHeight(24)
        btn_parent.clicked.connect(self.on_qc_parent)
        
        btn_point = QtWidgets.QPushButton("Point")
        btn_point.setFixedHeight(24)
        btn_point.clicked.connect(self.on_qc_point)
        
        btn_orient = QtWidgets.QPushButton("Orient")
        btn_orient.setFixedHeight(24)
        btn_orient.clicked.connect(self.on_qc_orient)
        
        btn_scale = QtWidgets.QPushButton("Scale")
        btn_scale.setFixedHeight(24)
        btn_scale.clicked.connect(self.on_qc_scale)
        
        btn_delete = QtWidgets.QPushButton("Xóa Constraint")
        btn_delete.setFixedHeight(24)
        btn_delete.setStyleSheet("background-color: #5A2A2A; color: #FFAAAA;")
        btn_delete.clicked.connect(self.on_qc_delete)
        
        btns_layout.addWidget(btn_parent)
        btns_layout.addWidget(btn_point)
        btns_layout.addWidget(btn_orient)
        btns_layout.addWidget(btn_scale)
        btns_layout.addWidget(btn_delete)
        qc_layout.addLayout(btns_layout)
        
        tab1_layout.addWidget(qc_group)
        
        # GroupBox 1: Smart Link
        link_group = QtWidgets.QGroupBox("Smart Link (Liên kết đối tượng)")
        link_layout = QtWidgets.QVBoxLayout(link_group)
        link_layout.setContentsMargins(8, 12, 8, 8)
        link_layout.setSpacing(8)
        
        target_row = QtWidgets.QHBoxLayout()
        target_row.addWidget(QtWidgets.QLabel("Target (Vật dẫn):"))
        self.target_txt = QtWidgets.QLineEdit()
        self.target_txt.setPlaceholderText("Xương / Vật dẫn đường (Driver)...")
        target_row.addWidget(self.target_txt)
        self.get_target_btn = QtWidgets.QPushButton("Lấy chọn")
        self.get_target_btn.clicked.connect(self.on_get_target)
        target_row.addWidget(self.get_target_btn)
        link_layout.addLayout(target_row)
        
        swap_row = QtWidgets.QHBoxLayout()
        swap_row.addStretch()
        self.swap_target_owner_btn = QtWidgets.QPushButton("  ⇅ Đổi bên Target / Owner  ")
        self.swap_target_owner_btn.setFixedHeight(22)
        self.swap_target_owner_btn.setStyleSheet("font-size: 11px; max-width: 180px; padding: 2px 8px;")
        self.swap_target_owner_btn.clicked.connect(self.on_swap_target_owner)
        swap_row.addWidget(self.swap_target_owner_btn)
        swap_row.addStretch()
        link_layout.addLayout(swap_row)

        owner_row = QtWidgets.QHBoxLayout()
        owner_row.addWidget(QtWidgets.QLabel("Owner (Vật bị dẫn):"))
        self.owner_txt = QtWidgets.QLineEdit()
        self.owner_txt.setPlaceholderText("Đối tượng đi theo (Driven)...")
        owner_row.addWidget(self.owner_txt)
        self.get_owner_btn = QtWidgets.QPushButton("Lấy chọn")
        self.get_owner_btn.clicked.connect(self.on_get_owner)
        owner_row.addWidget(self.get_owner_btn)
        link_layout.addLayout(owner_row)
        
        link_ops_row = QtWidgets.QHBoxLayout()
        self.link_btn = QtWidgets.QPushButton("Tạo Smart Link")
        self.link_btn.setIcon(AnimeowIcons.icon_link())
        self.link_btn.setObjectName("accent_btn")
        self.link_btn.setFixedHeight(28)
        self.link_btn.clicked.connect(self.on_link)
        link_ops_row.addWidget(self.link_btn)
        
        self.switch_target_btn = QtWidgets.QPushButton("Đổi Target (Switch)")
        self.switch_target_btn.setIcon(AnimeowIcons.icon_retarget())
        self.switch_target_btn.setFixedHeight(28)
        self.switch_target_btn.clicked.connect(self.on_switch_target)
        link_ops_row.addWidget(self.switch_target_btn)
        
        self.bake_clean_btn = QtWidgets.QPushButton("Bake & Clean Link")
        self.bake_clean_btn.setIcon(AnimeowIcons.icon_bake())
        self.bake_clean_btn.setFixedHeight(28)
        self.bake_clean_btn.clicked.connect(self.on_bake_clean)
        link_ops_row.addWidget(self.bake_clean_btn)
        link_layout.addLayout(link_ops_row)
        
        smart_bake_layout = QtWidgets.QGridLayout()
        smart_bake_layout.addWidget(QtWidgets.QLabel("Step (Bake Link):"), 0, 0)
        self.bake_step_spin = QtWidgets.QSpinBox()
        self.bake_step_spin.setRange(1, 100)
        self.bake_step_spin.setValue(1)
        smart_bake_layout.addWidget(self.bake_step_spin, 0, 1)
        
        self.smart_clean_cb = QtWidgets.QCheckBox("Smart Clean Link (Bảo toàn key cực trị)")
        self.smart_clean_cb.setChecked(True)
        smart_bake_layout.addWidget(self.smart_clean_cb, 0, 2)
        
        smart_bake_layout.addWidget(QtWidgets.QLabel("Reducer Threshold:"), 1, 0)
        self.threshold_spin = QtWidgets.QDoubleSpinBox()
        self.threshold_spin.setRange(0.001, 2.0)
        self.threshold_spin.setValue(0.05)
        self.threshold_spin.setSingleStep(0.01)
        smart_bake_layout.addWidget(self.threshold_spin, 1, 1, 1, 2)
        link_layout.addLayout(smart_bake_layout)
        
        tab1_layout.addWidget(link_group)
        
        # GroupBox 2: World Bake
        wb_group = QtWidgets.QGroupBox("World Bake (Bake không gian thế giới)")
        wb_layout = QtWidgets.QGridLayout(wb_group)
        wb_layout.setContentsMargins(8, 12, 8, 8)
        wb_layout.setSpacing(8)
        
        wb_layout.addWidget(QtWidgets.QLabel("Kênh Bake:"), 0, 0)
        self.wb_channels_combo = QtWidgets.QComboBox()
        self.wb_channels_combo.addItems(["Both (Translate & Rotate)", "Translate Only", "Rotate Only"])
        wb_layout.addWidget(self.wb_channels_combo, 0, 1)
        
        wb_layout.addWidget(QtWidgets.QLabel("Step (Bake):"), 0, 2)
        self.wb_step_spin = QtWidgets.QSpinBox()
        self.wb_step_spin.setRange(1, 100)
        self.wb_step_spin.setValue(1)
        wb_layout.addWidget(self.wb_step_spin, 0, 3)
        
        self.wb_smart_clean_cb = QtWidgets.QCheckBox("Smart Clean (Bảo toàn Pose cực trị)")
        self.wb_smart_clean_cb.setChecked(True)
        wb_layout.addWidget(self.wb_smart_clean_cb, 1, 0, 1, 2)
        
        self.wb_smart_bake_cb = QtWidgets.QCheckBox("Smart Bake (Key-on-key từ nguồn)")
        self.wb_smart_bake_cb.setChecked(True)
        wb_layout.addWidget(self.wb_smart_bake_cb, 1, 2, 1, 2)
        
        wb_layout.addWidget(QtWidgets.QLabel("Reducer Threshold:"), 2, 0)
        self.wb_threshold_spin = QtWidgets.QDoubleSpinBox()
        self.wb_threshold_spin.setRange(0.001, 2.0)
        self.wb_threshold_spin.setValue(0.05)
        self.wb_threshold_spin.setSingleStep(0.01)
        wb_layout.addWidget(self.wb_threshold_spin, 2, 1, 1, 3)
        
        wb_layout.addWidget(QtWidgets.QLabel("Bake Action:"), 3, 0)
        self.wb_bake_btn = QtWidgets.QPushButton("Bake sang Locator thế giới (Record)")
        self.wb_bake_btn.setIcon(AnimeowIcons.icon_world())
        self.wb_bake_btn.setFixedHeight(26)
        self.wb_bake_btn.clicked.connect(self.on_world_bake_to_locator)
        wb_layout.addWidget(self.wb_bake_btn, 3, 1, 1, 3)
        
        self.wb_restore_btn = QtWidgets.QPushButton("Bake ngược về Vật thể nguồn (Restore)")
        self.wb_restore_btn.setIcon(AnimeowIcons.icon_reset())
        self.wb_restore_btn.setFixedHeight(26)
        self.wb_restore_btn.clicked.connect(self.on_world_bake_from_locator)
        wb_layout.addWidget(self.wb_restore_btn, 4, 1, 1, 3)
        
        tab1_layout.addWidget(wb_group)

        # GroupBox 3: Bake theo bước (Bake on Ns)
        ns_group = QtWidgets.QGroupBox("Bake theo bước (Bake on Ns)")
        ns_layout = QtWidgets.QGridLayout(ns_group)
        ns_layout.setContentsMargins(8, 12, 8, 8)
        ns_layout.setSpacing(8)
        
        ns_layout.addWidget(QtWidgets.QLabel("Bước Bake:"), 0, 0)
        self.ns_step_combo = QtWidgets.QComboBox()
        self.ns_step_combo.addItems([
            "On 1s (Bước 1)",
            "On 2s (Bước 2)",
            "On 3s (Bước 3)",
            "On 4s (Bước 4)",
            "On 5s (Bước 5)"
        ])
        ns_layout.addWidget(self.ns_step_combo, 0, 1)
        
        self.ns_remove_constraints_cb = QtWidgets.QCheckBox("Xóa Constraints")
        self.ns_remove_constraints_cb.setChecked(False)
        ns_layout.addWidget(self.ns_remove_constraints_cb, 0, 2)
        
        self.ns_bake_btn = QtWidgets.QPushButton("Bake đối tượng chọn")
        self.ns_bake_btn.setIcon(AnimeowIcons.icon_bake())
        self.ns_bake_btn.setObjectName("accent_btn")
        self.ns_bake_btn.setFixedHeight(26)
        self.ns_bake_btn.clicked.connect(self.on_bake_selected_ns)
        ns_layout.addWidget(self.ns_bake_btn, 1, 0, 1, 3)
        
        tab1_layout.addWidget(ns_group)

        # GroupBox 3: Temp Pivot
        tp_group = QtWidgets.QGroupBox("Tâm xoay tạm thời (Temp Pivot)")
        tp_layout = QtWidgets.QHBoxLayout(tp_group)
        tp_layout.setContentsMargins(8, 12, 8, 8)
        tp_layout.setSpacing(8)
        
        self.tp_create_btn = QtWidgets.QPushButton("1. Tạo Temp Locator")
        self.tp_create_btn.setIcon(AnimeowIcons.icon_pivot())
        self.tp_create_btn.setFixedHeight(28)
        self.tp_create_btn.clicked.connect(self.on_tp_create)
        tp_layout.addWidget(self.tp_create_btn)
        
        self.tp_active_btn = QtWidgets.QPushButton("2. Kích hoạt Pivot")
        self.tp_active_btn.setIcon(AnimeowIcons.icon_pivot())
        self.tp_active_btn.setFixedHeight(28)
        self.tp_active_btn.clicked.connect(self.on_tp_active)
        tp_layout.addWidget(self.tp_active_btn)
        
        self.tp_release_btn = QtWidgets.QPushButton("3. Bake & Giải phóng")
        self.tp_release_btn.setIcon(AnimeowIcons.icon_bake())
        self.tp_release_btn.setFixedHeight(28)
        self.tp_release_btn.clicked.connect(self.on_tp_release)
        tp_layout.addWidget(self.tp_release_btn)
        
        tab1_layout.addWidget(tp_group)

        # GroupBox 4: Space & Rotate Order
        so_group = QtWidgets.QGroupBox("Space & Rotate Order (Bảo toàn Key)")
        so_layout = QtWidgets.QVBoxLayout(so_group)
        so_layout.setContentsMargins(8, 12, 8, 8)
        so_layout.setSpacing(8)
        
        order_row = QtWidgets.QHBoxLayout()
        order_row.addWidget(QtWidgets.QLabel("Đổi Rotate Order:"))
        self.so_order_combo = QtWidgets.QComboBox()
        self.so_order_combo.addItems(["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"])
        order_row.addWidget(self.so_order_combo)
        
        self.so_apply_order_btn = QtWidgets.QPushButton("Đổi Order && Giữ dáng")
        self.so_apply_order_btn.setIcon(AnimeowIcons.icon_space_order())
        self.so_apply_order_btn.setFixedHeight(26)
        self.so_apply_order_btn.clicked.connect(self.on_change_rotate_order)
        order_row.addWidget(self.so_apply_order_btn)
        so_layout.addLayout(order_row)
        
        space_row = QtWidgets.QHBoxLayout()
        self.so_record_btn = QtWidgets.QPushButton("Ghi Space Thế giới (Record)")
        self.so_record_btn.setFixedHeight(26)
        self.so_record_btn.clicked.connect(self.on_record_world_space)
        space_row.addWidget(self.so_record_btn)
        
        self.so_restore_btn = QtWidgets.QPushButton("Khôi phục Space (Restore)")
        self.so_restore_btn.setFixedHeight(26)
        self.so_restore_btn.clicked.connect(self.on_restore_world_space)
        space_row.addWidget(self.so_restore_btn)
        so_layout.addLayout(space_row)
        
        tab1_layout.addWidget(so_group)
        tab1_layout.addStretch()

        # =========================================================================
        # --- TAB 2: CURVE & MOTION (ĐƯỜNG CONG & DIỄN HOẠT) ---
        # =========================================================================
        tab2 = QtWidgets.QWidget(self)
        tab2.hide()
        tab2_layout = QtWidgets.QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(6, 8, 6, 6)
        tab2_layout.setSpacing(8)
        
        self.t2_title = QtWidgets.QLabel("CURVE EDITING & MOTION ANALYSIS")
        self.t2_title.setAlignment(QtCore.Qt.AlignCenter)
        self.t2_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00BCD4;")
        tab2_layout.addWidget(self.t2_title)
        
        # GroupBox 1: Arc Tracker
        self.at_group = QtWidgets.QGroupBox("Arc Tracker (Vẽ Quỹ đạo chuyển động)")
        at_layout = QtWidgets.QVBoxLayout(self.at_group)
        at_layout.setContentsMargins(8, 12, 8, 8)
        at_layout.setSpacing(8)
        
        at_opt_row = QtWidgets.QHBoxLayout()
        self.at_show_ticks_cb = QtWidgets.QCheckBox("Hiển thị Ticks thường (Màu vàng)")
        self.at_show_ticks_cb.setChecked(True)
        at_opt_row.addWidget(self.at_show_ticks_cb)
        
        self.at_show_keys_cb = QtWidgets.QCheckBox("Hiển thị Ticks Keyframe (Màu đỏ)")
        self.at_show_keys_cb.setChecked(True)
        at_opt_row.addWidget(self.at_show_keys_cb)
        at_layout.addLayout(at_opt_row)
        
        at_size_row = QtWidgets.QHBoxLayout()
        at_size_row.addWidget(QtWidgets.QLabel("Kích thước Ticks (Size):"))
        self.at_tick_size_spin = QtWidgets.QDoubleSpinBox()
        self.at_tick_size_spin.setRange(0.01, 5.0)
        self.at_tick_size_spin.setValue(0.1)
        self.at_tick_size_spin.setSingleStep(0.05)
        at_size_row.addWidget(self.at_tick_size_spin)
        at_layout.addLayout(at_size_row)
        
        at_btn_row = QtWidgets.QGridLayout()
        self.at_create_btn = QtWidgets.QPushButton("Vẽ Arc Trail")
        self.at_create_btn.setIcon(AnimeowIcons.icon_arc())
        self.at_create_btn.setObjectName("accent_btn")
        self.at_create_btn.setFixedHeight(28)
        self.at_create_btn.clicked.connect(self.on_create_arc_trail)
        at_btn_row.addWidget(self.at_create_btn, 0, 0)
        
        self.at_update_btn = QtWidgets.QPushButton("Cập nhật Arc Trails (Update)")
        self.at_update_btn.setFixedHeight(28)
        self.at_update_btn.clicked.connect(self.on_update_arc_trails)
        at_btn_row.addWidget(self.at_update_btn, 0, 1)
        
        self.at_clear_sel_btn = QtWidgets.QPushButton("Xóa chọn")
        self.at_clear_sel_btn.setFixedHeight(28)
        self.at_clear_sel_btn.clicked.connect(self.on_clear_selected_trails)
        at_btn_row.addWidget(self.at_clear_sel_btn, 1, 0)
        
        self.at_clear_all_btn = QtWidgets.QPushButton("Xóa tất cả")
        self.at_clear_all_btn.setFixedHeight(28)
        self.at_clear_all_btn.clicked.connect(self.on_clear_all_trails)
        at_btn_row.addWidget(self.at_clear_all_btn, 1, 1)
        at_layout.addLayout(at_btn_row)
        
        tab2_layout.addWidget(self.at_group)
        
        # GroupBox 2: Overlapper (Tạo chuyển động trễ & follow-through)
        self.ov_group = QtWidgets.QGroupBox("Overlapper (Tạo Chuyển Động Trễ & Follow Through)")
        ov_layout = QtWidgets.QVBoxLayout(self.ov_group)
        ov_layout.setContentsMargins(8, 12, 8, 8)
        ov_layout.setSpacing(6)
        
        # Hàng 1: Softness (timeShift) và Scale (globalScale)
        ov_param_row = QtWidgets.QHBoxLayout()
        ov_param_row.addWidget(QtWidgets.QLabel("Softness:"))
        self.ov_softness_spin = QtWidgets.QDoubleSpinBox()
        self.ov_softness_spin.setRange(0.1, 100.0)
        self.ov_softness_spin.setValue(3.0)
        self.ov_softness_spin.setSingleStep(0.5)
        self.ov_softness_spin.setFixedHeight(22)
        ov_param_row.addWidget(self.ov_softness_spin)
        
        ov_param_row.addWidget(QtWidgets.QLabel("Scale:"))
        self.ov_scale_spin = QtWidgets.QDoubleSpinBox()
        self.ov_scale_spin.setRange(0.01, 100.0)
        self.ov_scale_spin.setValue(1.0)
        self.ov_scale_spin.setSingleStep(0.1)
        self.ov_scale_spin.setFixedHeight(22)
        ov_param_row.addWidget(self.ov_scale_spin)
        ov_layout.addLayout(ov_param_row)
        
        # Hàng 2: Wind Checkbox, Wind Scale, Wind Speed
        ov_wind_row = QtWidgets.QHBoxLayout()
        self.ov_wind_cb = QtWidgets.QCheckBox("Wind (Gió)")
        self.ov_wind_cb.setChecked(False)
        ov_wind_row.addWidget(self.ov_wind_cb)
        
        ov_wind_row.addWidget(QtWidgets.QLabel("Wind Scale:"))
        self.ov_wind_scale_spin = QtWidgets.QDoubleSpinBox()
        self.ov_wind_scale_spin.setRange(0.01, 100.0)
        self.ov_wind_scale_spin.setValue(1.0)
        self.ov_wind_scale_spin.setSingleStep(0.1)
        self.ov_wind_scale_spin.setFixedHeight(20)
        ov_wind_row.addWidget(self.ov_wind_scale_spin)
        
        ov_wind_row.addWidget(QtWidgets.QLabel("Wind Speed:"))
        self.ov_wind_speed_spin = QtWidgets.QDoubleSpinBox()
        self.ov_wind_speed_spin.setRange(0.01, 100.0)
        self.ov_wind_speed_spin.setValue(1.0)
        self.ov_wind_speed_spin.setSingleStep(0.1)
        self.ov_wind_speed_spin.setFixedHeight(20)
        ov_wind_row.addWidget(self.ov_wind_speed_spin)
        ov_layout.addLayout(ov_wind_row)
        
        # Hàng 3: Advanced options
        ov_opt_layout = QtWidgets.QGridLayout()
        self.ov_skip_first_cb = QtWidgets.QCheckBox("Skip First (Bỏ qua control gốc)")
        self.ov_skip_first_cb.setToolTip("Không áp dụng overlapping cho control đầu tiên được chọn")
        ov_opt_layout.addWidget(self.ov_skip_first_cb, 0, 0)
        
        self.ov_translate_cb = QtWidgets.QCheckBox("Add Translate (IK Mode)")
        self.ov_translate_cb.setToolTip("Overlap cả tịnh tiến Translate (dành cho tay/chân IK)")
        ov_opt_layout.addWidget(self.ov_translate_cb, 0, 1)
        
        self.ov_hierarchy_cb = QtWidgets.QCheckBox("Hierarchy (Phân cấp)")
        self.ov_hierarchy_cb.setToolTip("Tự động áp dụng cho toàn bộ chuỗi điều khiển con bên dưới")
        ov_opt_layout.addWidget(self.ov_hierarchy_cb, 1, 0)
        
        self.ov_cycle_cb = QtWidgets.QCheckBox("Cycle (Lặp vô tận)")
        self.ov_cycle_cb.setToolTip("Tạo chuyển động overlapping lặp liền mạch (seamless cycle)")
        ov_opt_layout.addWidget(self.ov_cycle_cb, 1, 1)
        
        self.ov_bake_layer_cb = QtWidgets.QCheckBox("Bake on Layer")
        self.ov_bake_layer_cb.setToolTip("Nướng kết quả lên một Animation Layer mới thay vì BaseAnimation")
        ov_opt_layout.addWidget(self.ov_bake_layer_cb, 2, 0)
        
        self.ov_adaptive_scale_cb = QtWidgets.QCheckBox("Adaptive Scale")
        self.ov_adaptive_scale_cb.setToolTip("Tự động thay đổi Scale dựa trên khoảng cách giữa các control")
        self.ov_adaptive_scale_cb.setChecked(True)
        ov_opt_layout.addWidget(self.ov_adaptive_scale_cb, 2, 1)
        
        self.ov_sel_set_cb = QtWidgets.QCheckBox("Create Selection Set")
        self.ov_sel_set_cb.setToolTip("Tạo selection set 'OverlapperSet' chứa các control được overlap")
        self.ov_sel_set_cb.setChecked(True)
        ov_opt_layout.addWidget(self.ov_sel_set_cb, 3, 0, 1, 2)
        ov_layout.addLayout(ov_opt_layout)
        
        # Hàng 4: Nút bấm
        ov_btn_row = QtWidgets.QHBoxLayout()
        self.ov_execute_btn = QtWidgets.QPushButton("Overlap Action")
        self.ov_execute_btn.setIcon(AnimeowIcons.icon_tween())
        self.ov_execute_btn.setObjectName("accent_btn")
        self.ov_execute_btn.setFixedHeight(28)
        self.ov_execute_btn.clicked.connect(self.on_overlapper_execute)
        ov_btn_row.addWidget(self.ov_execute_btn)
        
        self.ov_cleanup_btn = QtWidgets.QPushButton("Clean Up (Dọn dẹp)")
        self.ov_cleanup_btn.setIcon(AnimeowIcons.icon_clean())
        self.ov_cleanup_btn.setFixedHeight(28)
        self.ov_cleanup_btn.clicked.connect(self.on_overlapper_cleanup)
        ov_btn_row.addWidget(self.ov_cleanup_btn)
        ov_layout.addLayout(ov_btn_row)
        
        tab2_layout.addWidget(self.ov_group)
        
        # GroupBox 3: Curve Editor Utilities
        self.curve_group = QtWidgets.QGroupBox("Curve Utilities (Tinh chỉnh đường cong)")
        curve_layout = QtWidgets.QVBoxLayout(self.curve_group)
        curve_layout.setContentsMargins(8, 12, 8, 8)
        curve_layout.setSpacing(8)
        
        self.local_scale_btn = QtWidgets.QPushButton("Local Scale (Co dãn keyframe cục bộ)")
        self.local_scale_btn.setIcon(AnimeowIcons.icon_tween())
        self.local_scale_btn.setFixedHeight(28)
        self.local_scale_btn.clicked.connect(self.on_local_scale_tool)
        curve_layout.addWidget(self.local_scale_btn)
        
        tab2_layout.addWidget(self.curve_group)
        tab2_layout.addStretch()

        # =========================================================================
        # --- TAB 3: RIG & MIRROR (CÔNG CỤ RIG & ĐỐI XỨNG) ---
        # =========================================================================
        tab3 = QtWidgets.QWidget(self)
        tab3.hide()
        tab3_layout = QtWidgets.QVBoxLayout(tab3)
        tab3_layout.setContentsMargins(6, 8, 6, 6)
        tab3_layout.setSpacing(8)
        
        t3_title = QtWidgets.QLabel("RIG MAPPING & ANIMATION MIRRORING")
        t3_title.setAlignment(QtCore.Qt.AlignCenter)
        t3_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00BCD4;")
        tab3_layout.addWidget(t3_title)
        
        # GroupBox 1: Rig Retargeting
        rt_group = QtWidgets.QGroupBox("Rig Retargeting (Ghép nối chuyển động)")
        rt_layout = QtWidgets.QVBoxLayout(rt_group)
        rt_layout.setContentsMargins(8, 12, 8, 8)
        rt_layout.setSpacing(8)
        
        ns_layout = QtWidgets.QHBoxLayout()
        ns_layout.addWidget(QtWidgets.QLabel("Source NS:"))
        self.rt_src_ns_combo = QtWidgets.QComboBox()
        ns_layout.addWidget(self.rt_src_ns_combo)
        
        ns_layout.addWidget(QtWidgets.QLabel("Target NS:"))
        self.rt_tgt_ns_combo = QtWidgets.QComboBox()
        ns_layout.addWidget(self.rt_tgt_ns_combo)
        
        self.rt_refresh_ns_btn = QtWidgets.QPushButton("Quét NS")
        self.rt_refresh_ns_btn.setFixedWidth(65)
        self.rt_refresh_ns_btn.clicked.connect(self.on_rt_refresh_namespaces)
        ns_layout.addWidget(self.rt_refresh_ns_btn)
        rt_layout.addLayout(ns_layout)
        
        map_layout = QtWidgets.QVBoxLayout()
        map_layout.addWidget(QtWidgets.QLabel("Bảng ánh xạ các bộ điều khiển (Green: Ok, Red: Missing):"))
        self.rt_table = QtWidgets.QTableWidget()
        self.rt_table.setColumnCount(2)
        self.rt_table.setHorizontalHeaderLabels(["Source Control", "Target Control"])
        self.rt_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.rt_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.rt_table.setFixedHeight(150)
        self.rt_table.itemChanged.connect(self.on_rt_item_changed)
        map_layout.addWidget(self.rt_table)
        
        manual_layout = QtWidgets.QHBoxLayout()
        self.rt_get_src_btn = QtWidgets.QPushButton("Lấy Nguồn (Get Source)")
        self.rt_get_src_btn.clicked.connect(self.on_rt_get_source)
        manual_layout.addWidget(self.rt_get_src_btn)
        self.rt_get_tgt_btn = QtWidgets.QPushButton("Lấy Đích (Get Target)")
        self.rt_get_tgt_btn.clicked.connect(self.on_rt_get_target)
        manual_layout.addWidget(self.rt_get_tgt_btn)
        map_layout.addLayout(manual_layout)
        rt_layout.addLayout(map_layout)
        
        rt_btn_layout = QtWidgets.QGridLayout()
        self.rt_auto_map_btn = QtWidgets.QPushButton("Khớp tự động (Auto Map)")
        self.rt_auto_map_btn.clicked.connect(self.on_rt_auto_map)
        rt_btn_layout.addWidget(self.rt_auto_map_btn, 0, 0)
        
        self.rt_add_row_btn = QtWidgets.QPushButton("Thêm dòng")
        self.rt_add_row_btn.clicked.connect(self.on_rt_add_row)
        rt_btn_layout.addWidget(self.rt_add_row_btn, 0, 1)
        
        self.rt_del_btn = QtWidgets.QPushButton("Xóa dòng chọn")
        self.rt_del_btn.clicked.connect(self.on_rt_del_row)
        rt_btn_layout.addWidget(self.rt_del_btn, 1, 0)
        
        self.rt_clear_btn = QtWidgets.QPushButton("Xóa hết bảng")
        self.rt_clear_btn.clicked.connect(self.on_rt_clear_table)
        rt_btn_layout.addWidget(self.rt_clear_btn, 1, 1)
        
        self.rt_load_btn = QtWidgets.QPushButton("Tải file Mapping (JSON)")
        self.rt_load_btn.clicked.connect(self.on_rt_load_json)
        rt_btn_layout.addWidget(self.rt_load_btn, 2, 0)
        
        self.rt_save_btn = QtWidgets.QPushButton("Lưu cấu hình Mapping (JSON)")
        self.rt_save_btn.clicked.connect(self.on_rt_save_json)
        rt_btn_layout.addWidget(self.rt_save_btn, 2, 1)
        rt_layout.addLayout(rt_btn_layout)
        
        rt_opts = QtWidgets.QHBoxLayout()
        self.rt_maintain_offset_cb = QtWidgets.QCheckBox("Maintain Offset (Snap vị trí)")
        self.rt_maintain_offset_cb.setChecked(True)
        rt_opts.addWidget(self.rt_maintain_offset_cb)
        self.rt_smart_bake_cb = QtWidgets.QCheckBox("Smart Bake (Timing nguồn)")
        self.rt_smart_bake_cb.setChecked(True)
        rt_opts.addWidget(self.rt_smart_bake_cb)
        rt_layout.addLayout(rt_opts)
        
        self.rt_execute_btn = QtWidgets.QPushButton("Thực hiện Retarget Animation (Bake)")
        self.rt_execute_btn.setIcon(AnimeowIcons.icon_retarget())
        self.rt_execute_btn.setObjectName("accent_btn")
        self.rt_execute_btn.setFixedHeight(30)
        self.rt_execute_btn.clicked.connect(self.on_rt_execute)
        rt_layout.addWidget(self.rt_execute_btn)
        
        tab3_layout.addWidget(rt_group)
        
        # GroupBox 2: Mirror Animation
        mir_group = QtWidgets.QGroupBox("Mirror Animation (Đối xứng chuyển động)")
        mir_layout = QtWidgets.QGridLayout(mir_group)
        mir_layout.setContentsMargins(8, 12, 8, 8)
        mir_layout.setSpacing(8)
        
        mir_layout.addWidget(QtWidgets.QLabel("Chế độ Mirror:"), 0, 0)
        self.mir_mode_combo = QtWidgets.QComboBox()
        self.mir_mode_combo.addItems([
            "Swap Left && Right (Đổi bên)",
            "Left -> Right (Trái sang Phải)",
            "Right -> Left (Phải sang Trái)",
            "Flip Selected (Lật đối tượng chọn)"
        ])
        mir_layout.addWidget(self.mir_mode_combo, 0, 1)
        
        mir_layout.addWidget(QtWidgets.QLabel("Phạm vi:"), 0, 2)
        self.mir_scope_combo = QtWidgets.QComboBox()
        self.mir_scope_combo.addItems(["Selected Controls (Đối tượng chọn)", "Whole Rig (Toàn bộ Rig)"])
        mir_layout.addWidget(self.mir_scope_combo, 0, 3)
        
        mir_layout.addWidget(QtWidgets.QLabel("Thời gian:"), 1, 0)
        self.mir_time_combo = QtWidgets.QComboBox()
        self.mir_time_combo.addItems(["Whole Timeline (Toàn bộ)", "Selected Range (Khoảng chọn)"])
        mir_layout.addWidget(self.mir_time_combo, 1, 1)

        mir_layout.addWidget(QtWidgets.QLabel("Rig Preset:"), 2, 0)
        self.mir_preset_combo = QtWidgets.QComboBox()
        self.mir_preset_combo.addItems([
            "Chuẩn L/R (L_, _L, Left, Right)",
            "Mixamo (mixamorig:Left/Right)",
            "Advanced Skeleton (FKArmL/R)",
            "MetaHuman (l_hand/r_hand)",
            "Tự định nghĩa (Custom)"
        ])
        self.mir_preset_combo.currentIndexChanged.connect(self.on_mir_preset_changed)
        mir_layout.addWidget(self.mir_preset_combo, 2, 1)

        self.mir_custom_left_label = QtWidgets.QLabel("Custom Left:")
        self.mir_custom_left_txt = QtWidgets.QLineEdit()
        self.mir_custom_left_txt.setPlaceholderText("Ví dụ: _L")
        self.mir_custom_right_label = QtWidgets.QLabel("Custom Right:")
        self.mir_custom_right_txt = QtWidgets.QLineEdit()
        self.mir_custom_right_txt.setPlaceholderText("Ví dụ: _R")
        
        mir_layout.addWidget(self.mir_custom_left_label, 2, 2)
        mir_layout.addWidget(self.mir_custom_left_txt, 2, 3)
        mir_layout.addWidget(self.mir_custom_right_label, 3, 2)
        mir_layout.addWidget(self.mir_custom_right_txt, 3, 3)
        
        self.mir_custom_left_label.hide()
        self.mir_custom_left_txt.hide()
        self.mir_custom_right_label.hide()
        self.mir_custom_right_txt.hide()

        self.mir_execute_btn = QtWidgets.QPushButton("Thực hiện Mirror Animation (Bake)")
        self.mir_execute_btn.setIcon(AnimeowIcons.icon_mirror())
        self.mir_execute_btn.setObjectName("accent_btn")
        self.mir_execute_btn.setFixedHeight(30)
        self.mir_execute_btn.clicked.connect(self.on_mir_execute)
        mir_layout.addWidget(self.mir_execute_btn, 4, 0, 1, 4)
        
        tab3_layout.addWidget(mir_group)
        tab3_layout.addStretch()

        # =========================================================================
        # --- TAB 4: OUTPUT & SCENE (XUẤT BẢN & CẢNH QUAN) ---
        # =========================================================================
        tab4 = QtWidgets.QWidget(self)
        tab4.hide()
        tab4_layout = QtWidgets.QVBoxLayout(tab4)
        tab4_layout.setContentsMargins(6, 8, 6, 6)
        tab4_layout.setSpacing(8)
        
        t4_title = QtWidgets.QLabel("PLAYBLAST EXPORT & SCENE OPTIMIZATION")
        t4_title.setAlignment(QtCore.Qt.AlignCenter)
        t4_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00BCD4;")
        tab4_layout.addWidget(t4_title)
        
        # GroupBox 1: Playblast Exporter
        pb_group = QtWidgets.QGroupBox("Playblast Exporter (Xuất video review)")
        pb_layout = QtWidgets.QGridLayout(pb_group)
        pb_layout.setContentsMargins(8, 12, 8, 8)
        pb_layout.setSpacing(8)
        
        pb_layout.addWidget(QtWidgets.QLabel("Camera:"), 0, 0)
        self.camera_combo = QtWidgets.QComboBox()
        pb_layout.addWidget(self.camera_combo, 0, 1)
        
        pb_layout.addWidget(QtWidgets.QLabel("Định dạng:"), 0, 2)
        self.pb_format_combo = QtWidgets.QComboBox()
        self.pb_format_combo.addItems(["qt (QuickTime)", "image (Image Sequence)"])
        pb_layout.addWidget(self.pb_format_combo, 0, 3)
        
        pb_layout.addWidget(QtWidgets.QLabel("Kích thước (Rộng x Cao):"), 1, 0)
        dim_layout = QtWidgets.QHBoxLayout()
        self.pb_width_spin = QtWidgets.QSpinBox()
        self.pb_width_spin.setRange(128, 4096)
        self.pb_width_spin.setValue(1920)
        dim_layout.addWidget(self.pb_width_spin)
        
        dim_layout.addWidget(QtWidgets.QLabel("x"))
        self.pb_height_spin = QtWidgets.QSpinBox()
        self.pb_height_spin.setRange(128, 4096)
        self.pb_height_spin.setValue(1080)
        dim_layout.addWidget(self.pb_height_spin)
        pb_layout.addLayout(dim_layout, 1, 1)
        
        pb_layout.addWidget(QtWidgets.QLabel("Tỉ lệ (Scale):"), 1, 2)
        self.pb_scale_spin = QtWidgets.QDoubleSpinBox()
        self.pb_scale_spin.setRange(0.1, 1.0)
        self.pb_scale_spin.setValue(1.0)
        self.pb_scale_spin.setSingleStep(0.1)
        pb_layout.addWidget(self.pb_scale_spin, 1, 3)
        
        self.pb_viewer_cb = QtWidgets.QCheckBox("Tự động mở xem video (Viewer)")
        self.pb_viewer_cb.setChecked(True)
        pb_layout.addWidget(self.pb_viewer_cb, 2, 0, 1, 2)
        
        self.pb_overwrite_cb = QtWidgets.QCheckBox("Ghi đè tệp cũ mà không hỏi")
        self.pb_overwrite_cb.setChecked(True)
        pb_layout.addWidget(self.pb_overwrite_cb, 2, 2, 1, 2)
        
        # Dòng chọn thư mục lưu tùy chỉnh (Custom Output Directory)
        pb_layout.addWidget(QtWidgets.QLabel("Thư mục lưu:"), 3, 0)
        self.pb_dir_edit = QtWidgets.QLineEdit()
        self.pb_dir_edit.setPlaceholderText("Mặc định lưu vào thư mục 'mov' cùng cấp file scene")
        self.pb_dir_edit.setToolTip("Chọn thư mục lưu video Playblast tùy chọn. Để trống nếu muốn tự động lưu theo Scene.")
        pb_layout.addWidget(self.pb_dir_edit, 3, 1, 1, 2)
        
        self.pb_browse_btn = QtWidgets.QPushButton()
        self.pb_browse_btn.setFixedSize(30, 22)
        self.pb_browse_btn.setIcon(AnimeowIcons.icon_folder())
        self.pb_browse_btn.setToolTip("Chọn thư mục...")
        self.pb_browse_btn.clicked.connect(self.on_browse_pb_dir)
        pb_layout.addWidget(self.pb_browse_btn, 3, 3)
        
        self.multi_cam_cb = QtWidgets.QCheckBox("Quay hàng loạt (Multi-Camera)")
        self.multi_cam_cb.setChecked(False)
        self.multi_cam_cb.toggled.connect(self.on_toggle_multi_cam)
        pb_layout.addWidget(self.multi_cam_cb, 4, 0, 1, 4)
        
        self.camera_list_widget = QtWidgets.QListWidget()
        self.camera_list_widget.setFixedHeight(80)
        self.camera_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.camera_list_widget.itemClicked.connect(self.on_camera_item_clicked)
        self.camera_list_widget.hide()
        pb_layout.addWidget(self.camera_list_widget, 5, 0, 1, 4)
        
        self.refresh_cam_btn = QtWidgets.QPushButton("Quét lại Cameras")
        self.refresh_cam_btn.setFixedHeight(22)
        self.refresh_cam_btn.clicked.connect(self.on_refresh_cameras)
        # Bỏ ẩn nút quét camera để nút luôn hiển thị phục vụ người dùng
        pb_layout.addWidget(self.refresh_cam_btn, 6, 0, 1, 4)
        
        self.pb_execute_btn = QtWidgets.QPushButton("Thực hiện Playblast")
        self.pb_execute_btn.setIcon(AnimeowIcons.icon_play())
        self.pb_execute_btn.setObjectName("accent_btn")
        self.pb_execute_btn.setFixedHeight(30)
        self.pb_execute_btn.clicked.connect(self.on_run_playblast)
        pb_layout.addWidget(self.pb_execute_btn, 7, 0, 1, 4)
        
        tab4_layout.addWidget(pb_group)
        
        tab4_layout.addStretch()

        # =========================================================================
        # --- TAB 5: LAUNCHERS (KHỞI CHẠY NHANH) ---
        # =========================================================================
        tab5 = QtWidgets.QWidget(self)
        tab5.hide()
        tab5_layout = QtWidgets.QVBoxLayout(tab5)
        tab5_layout.setContentsMargins(6, 8, 6, 6)
        tab5_layout.setSpacing(8)
        
        t5_title = QtWidgets.QLabel("QUICK START THIRD-PARTY PLUGINS")
        t5_title.setAlignment(QtCore.Qt.AlignCenter)
        t5_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00BCD4;")
        tab5_layout.addWidget(t5_title)
        
        launch_group = QtWidgets.QGroupBox("Khởi chạy ứng dụng (Quick Launchers)")
        launch_layout = QtWidgets.QVBoxLayout(launch_group)
        launch_layout.setContentsMargins(8, 12, 8, 8)
        launch_layout.setSpacing(10)
        
        self.launch_studiolibrary_btn = QtWidgets.QPushButton("Khởi động Studio Library")
        self.launch_studiolibrary_btn.setIcon(AnimeowIcons.icon_folder())
        self.launch_studiolibrary_btn.setFixedHeight(30)
        self.launch_studiolibrary_btn.clicked.connect(self.on_launch_studiolibrary)
        launch_layout.addWidget(self.launch_studiolibrary_btn)
        
        self.launch_dwpicker_btn = QtWidgets.QPushButton("Khởi động DWPicker")
        self.launch_dwpicker_btn.setIcon(AnimeowIcons.icon_key())
        self.launch_dwpicker_btn.setFixedHeight(30)
        self.launch_dwpicker_btn.clicked.connect(self.on_launch_dwpicker)
        launch_layout.addWidget(self.launch_dwpicker_btn)
        
        self.launch_tweenmachine_btn = QtWidgets.QPushButton("Khởi động Tween Machine")
        self.launch_tweenmachine_btn.setIcon(AnimeowIcons.icon_tween())
        self.launch_tweenmachine_btn.setFixedHeight(30)
        self.launch_tweenmachine_btn.clicked.connect(self.on_launch_tweenmachine)
        launch_layout.addWidget(self.launch_tweenmachine_btn)
        
        self.launch_atools_btn = QtWidgets.QPushButton("Khởi động aTools Anim School")
        self.launch_atools_btn.setIcon(AnimeowIcons.icon_launch())
        self.launch_atools_btn.setFixedHeight(30)
        self.launch_atools_btn.clicked.connect(self.on_launch_atools)
        launch_layout.addWidget(self.launch_atools_btn)
        
        self.launch_animo_btn = QtWidgets.QPushButton("Khởi động Animo (Cụm Công cụ Anim)")
        self.launch_animo_btn.setIcon(AnimeowIcons.icon_launch())
        self.launch_animo_btn.setFixedHeight(30)
        self.launch_animo_btn.clicked.connect(self.on_launch_animo)
        launch_layout.addWidget(self.launch_animo_btn)
        
        self.launch_anm_hider_btn = QtWidgets.QPushButton("Khởi động ANM Hider (Ẩn/Hiện bộ phận)")
        self.launch_anm_hider_btn.setIcon(AnimeowIcons.icon_clean())
        self.launch_anm_hider_btn.setFixedHeight(30)
        self.launch_anm_hider_btn.clicked.connect(self.on_launch_anm_hider)
        launch_layout.addWidget(self.launch_anm_hider_btn)
        
        tab5_layout.addWidget(launch_group)
        
        shelf_group = QtWidgets.QGroupBox("Thanh công cụ nhanh (Shelf)")
        shelf_layout = QtWidgets.QVBoxLayout(shelf_group)
        shelf_layout.setContentsMargins(8, 12, 8, 8)
        shelf_layout.setSpacing(10)
        
        self.create_shelf_btn = QtWidgets.QPushButton("✨ Tạo / Cập nhật Shelf Animeow")
        self.create_shelf_btn.setIcon(AnimeowIcons.icon_star())
        self.create_shelf_btn.setObjectName("accent_btn")
        self.create_shelf_btn.setFixedHeight(30)
        self.create_shelf_btn.clicked.connect(self.on_create_custom_shelf)
        shelf_layout.addWidget(self.create_shelf_btn)
        
        tab5_layout.addWidget(shelf_group)
        tab5_layout.addStretch()

        # =========================================================================
        # --- ADD TABS TO TABWIDGET ---
        # =========================================================================
        if self.standalone_tab is not None:
            if self.standalone_tab == 0 or self.standalone_tab == "smart_link":
                self.tab_widget.addTab(wrap_in_scroll(tab1), "Space & Bake")
                try:
                    t1_title.hide()
                    qc_group.hide()
                    wb_group.hide()
                    ns_group.hide()
                    tp_group.hide()
                    so_group.hide()
                except Exception:
                    pass
            elif self.standalone_tab == "world_bake":
                self.tab_widget.addTab(wrap_in_scroll(tab1), "Space & Bake")
                try:
                    t1_title.hide()
                    link_group.hide()
                    qc_group.hide()
                except Exception:
                    pass
            elif self.standalone_tab == 1:
                self.tab_widget.addTab(wrap_in_scroll(tab2), "Curve & Motion")
            elif self.standalone_tab == 2:
                self.tab_widget.addTab(wrap_in_scroll(tab3), "Rig & Mirror")
            elif self.standalone_tab == 3:
                self.tab_widget.addTab(wrap_in_scroll(tab4), "Output & Scene")
            elif self.standalone_tab == "arc_tracker":
                self.tab_widget.addTab(wrap_in_scroll(tab2), "Arc Tracker")
                # Ẩn tiêu đề và các công cụ Curve khác, chỉ chừa lại Arc Tracker
                try:
                    self.t2_title.hide()
                    self.curve_group.hide()
                except Exception:
                    pass
            elif self.standalone_tab == "round_tool":
                self.tab_widget.addTab(wrap_in_scroll(tab2), "Round Tool")
                # Ẩn tiêu đề, Arc Tracker và nút Euler Filter, đổi tên GroupBox
                try:
                    self.t2_title.hide()
                    self.at_group.hide()
                    self.euler_filter_btn.hide()
                    self.curve_group.setTitle("Công cụ làm tròn số")
                except Exception:
                    pass
            elif self.standalone_tab == "overlapper":
                self.tab_widget.addTab(wrap_in_scroll(tab2), "Overlapper")
                # Chỉ hiển thị Overlapper, ẩn các thành phần khác trong Tab 2
                try:
                    self.t2_title.hide()
                    self.at_group.hide()
                    self.curve_group.hide()
                except Exception:
                    pass
            elif self.standalone_tab == "view_layer":
                tab_view_layer = animeow_view_layer.AnimeowViewLayerUI()
                self.tab_widget.addTab(tab_view_layer, "View Layer")
            elif self.standalone_tab == "quick_const":
                qc_widget = QtWidgets.QWidget(self)
                qc_layout = QtWidgets.QVBoxLayout(qc_widget)
                qc_layout.setContentsMargins(6, 6, 6, 6)
                qc_layout.setSpacing(6)
                
                # Checkbox Offset
                mo_row = QtWidgets.QHBoxLayout()
                self.qc_mo_cb = QtWidgets.QCheckBox("Maintain Offset")
                self.qc_mo_cb.setChecked(True)
                mo_row.addWidget(self.qc_mo_cb)
                mo_row.addStretch()
                qc_layout.addLayout(mo_row)
                
                # Checkbox Translate
                t_row = QtWidgets.QHBoxLayout()
                t_row.addWidget(QtWidgets.QLabel("T: "))
                self.qc_tx_cb = QtWidgets.QCheckBox("X")
                self.qc_tx_cb.setChecked(True)
                self.qc_ty_cb = QtWidgets.QCheckBox("Y")
                self.qc_ty_cb.setChecked(True)
                self.qc_tz_cb = QtWidgets.QCheckBox("Z")
                self.qc_tz_cb.setChecked(True)
                t_row.addWidget(self.qc_tx_cb)
                t_row.addWidget(self.qc_ty_cb)
                t_row.addWidget(self.qc_tz_cb)
                t_row.addStretch()
                qc_layout.addLayout(t_row)
                
                # Checkbox Rotate
                r_row = QtWidgets.QHBoxLayout()
                r_row.addWidget(QtWidgets.QLabel("R: "))
                self.qc_rx_cb = QtWidgets.QCheckBox("X")
                self.qc_rx_cb.setChecked(True)
                self.qc_ry_cb = QtWidgets.QCheckBox("Y")
                self.qc_ry_cb.setChecked(True)
                self.qc_rz_cb = QtWidgets.QCheckBox("Z")
                self.qc_rz_cb.setChecked(True)
                r_row.addWidget(self.qc_rx_cb)
                r_row.addWidget(self.qc_ry_cb)
                r_row.addWidget(self.qc_rz_cb)
                r_row.addStretch()
                qc_layout.addLayout(r_row)
                
                btn_parent = QtWidgets.QPushButton("Parent Constraint")
                btn_parent.setFixedHeight(26)
                btn_parent.clicked.connect(self.on_qc_parent)
                
                btn_point = QtWidgets.QPushButton("Point Constraint")
                btn_point.setFixedHeight(26)
                btn_point.clicked.connect(self.on_qc_point)
                
                btn_orient = QtWidgets.QPushButton("Orient Constraint")
                btn_orient.setFixedHeight(26)
                btn_orient.clicked.connect(self.on_qc_orient)
                
                btn_scale = QtWidgets.QPushButton("Scale Constraint")
                btn_scale.setFixedHeight(26)
                btn_scale.clicked.connect(self.on_qc_scale)
                
                btn_delete = QtWidgets.QPushButton("Xóa Constraints (Delete)")
                btn_delete.setFixedHeight(26)
                btn_delete.setStyleSheet("background-color: #5A2A2A; color: #FFAAAA; font-weight: bold;")
                btn_delete.clicked.connect(self.on_qc_delete)
                
                qc_layout.addWidget(btn_parent)
                qc_layout.addWidget(btn_point)
                qc_layout.addWidget(btn_orient)
                qc_layout.addWidget(btn_scale)
                qc_layout.addWidget(btn_delete)
                
                self.tab_widget.addTab(qc_widget, "Quick Const")
                self.setMinimumWidth(180)
            elif self.standalone_tab == "fav_tools":
                fav_widget = QtWidgets.QWidget(self)
                fav_layout = QtWidgets.QVBoxLayout(fav_widget)
                fav_layout.setContentsMargins(6, 6, 6, 6)
                fav_layout.setSpacing(8)
                
                # GroupBox 1: Clean & Filter Key
                ck_group = QtWidgets.QGroupBox("Dọn dẹp & Lọc Keyframe (Clean & Filter)")
                ck_lay = QtWidgets.QVBoxLayout(ck_group)
                ck_lay.setContentsMargins(8, 10, 8, 8)
                ck_lay.setSpacing(6)
                
                btn_clean = QtWidgets.QPushButton("Dọn Key Bằng Nhau (Clean Key)")
                btn_clean.setIcon(AnimeowIcons.icon_clean())
                btn_clean.setFixedHeight(28)
                btn_clean.clicked.connect(self.on_clean_redundant_keys)
                ck_lay.addWidget(btn_clean)
                
                btn_euler = QtWidgets.QPushButton("Euler Filter (Lọc xoay)")
                btn_euler.setIcon(AnimeowIcons.icon_euler())
                btn_euler.setFixedHeight(28)
                btn_euler.clicked.connect(self.on_euler_filter)
                ck_lay.addWidget(btn_euler)
                
                # Hàng ngang Clean Neighborhood trong Favorites
                fav_neighborhood_row = QtWidgets.QHBoxLayout()
                fav_neighborhood_row.addWidget(QtWidgets.QLabel("Dọn lân cận (Bán kính):"))
                self.fav_clean_radius_spin = QtWidgets.QSpinBox()
                self.fav_clean_radius_spin.setRange(1, 500)
                self.fav_clean_radius_spin.setValue(3)
                self.fav_clean_radius_spin.setFixedHeight(22)
                fav_neighborhood_row.addWidget(self.fav_clean_radius_spin)
                
                self.fav_clean_neighbor_btn = QtWidgets.QPushButton("Clean Neighborhood")
                self.fav_clean_neighbor_btn.setIcon(AnimeowIcons.icon_clean())
                self.fav_clean_neighbor_btn.setFixedHeight(24)
                self.fav_clean_neighbor_btn.clicked.connect(self.on_clean_neighborhood)
                fav_neighborhood_row.addWidget(self.fav_clean_neighbor_btn)
                ck_lay.addLayout(fav_neighborhood_row)
                
                # Nút dọn key lẻ trong Favorites
                self.fav_clean_subframe_btn = QtWidgets.QPushButton("Dọn Key Lẻ (Clean Sub-frame Keys)")
                self.fav_clean_subframe_btn.setIcon(AnimeowIcons.icon_clean())
                self.fav_clean_subframe_btn.setFixedHeight(28)
                self.fav_clean_subframe_btn.clicked.connect(self.on_clean_subframe_keys)
                ck_lay.addWidget(self.fav_clean_subframe_btn)
                
                # Cụm Smooth Keys & Slider trong Favorites
                fav_smooth_row = QtWidgets.QHBoxLayout()
                self.fav_smooth_btn = QtWidgets.QPushButton("Smooth Keys")
                self.fav_smooth_btn.setIcon(AnimeowIcons.icon_clean())
                self.fav_smooth_btn.setFixedHeight(24)
                self.fav_smooth_btn.setToolTip("Làm mịn 100% các keyframe được chọn trong Graph Editor")
                self.fav_smooth_btn.clicked.connect(self.on_smooth_btn_clicked)
                fav_smooth_row.addWidget(self.fav_smooth_btn)
                
                self.fav_smooth_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
                self.fav_smooth_slider.setRange(0, 100)
                self.fav_smooth_slider.setValue(0)
                self.fav_smooth_slider.setFixedHeight(20)
                self.fav_smooth_slider.setToolTip("Kéo trượt để làm mịn keyframe tương tác từ 0% đến 100%")
                self.fav_smooth_slider.setStyleSheet("""
                    QSlider::groove:horizontal {
                        background: #3A3A3A;
                        height: 4px;
                        border-radius: 2px;
                    }
                    QSlider::handle:horizontal {
                        background: #00BCD4;
                        width: 12px;
                        height: 12px;
                        margin: -4px 0;
                        border-radius: 6px;
                    }
                """)
                fav_smooth_row.addWidget(self.fav_smooth_slider)
                
                self.fav_smooth_pct_label = QtWidgets.QLabel("0%")
                self.fav_smooth_pct_label.setFixedWidth(30)
                self.fav_smooth_pct_label.setAlignment(QtCore.Qt.AlignCenter)
                self.fav_smooth_pct_label.setStyleSheet("font-weight: bold; color: #00BCD4;")
                fav_smooth_row.addWidget(self.fav_smooth_pct_label)
                ck_lay.addLayout(fav_smooth_row)
                
                self.fav_smooth_slider.sliderPressed.connect(self.on_smooth_slider_pressed)
                self.fav_smooth_slider.valueChanged.connect(self.on_smooth_slider_changed)
                self.fav_smooth_slider.sliderReleased.connect(self.on_smooth_slider_released)
                
                fav_layout.addWidget(ck_group)
                
                # GroupBox 1b: Curve Utilities (Favorites)
                fav_curve_group = QtWidgets.QGroupBox("Curve Utilities (Tinh chỉnh đường cong)")
                fav_curve_layout = QtWidgets.QVBoxLayout(fav_curve_group)
                fav_curve_layout.setContentsMargins(8, 10, 8, 8)
                fav_curve_layout.setSpacing(6)
                
                self.fav_local_scale_btn = QtWidgets.QPushButton("Local Scale (Co dãn keyframe cục bộ)")
                self.fav_local_scale_btn.setIcon(AnimeowIcons.icon_tween())
                self.fav_local_scale_btn.setFixedHeight(28)
                self.fav_local_scale_btn.clicked.connect(self.on_local_scale_tool)
                fav_curve_layout.addWidget(self.fav_local_scale_btn)
                
                fav_layout.addWidget(fav_curve_group)
                
                # GroupBox 2: Tween Machine (Favorites)
                fav_tween_group = QtWidgets.QGroupBox("Tween Machine (Nội suy Keyframe)")
                fav_tween_layout = QtWidgets.QVBoxLayout(fav_tween_group)
                fav_tween_layout.setContentsMargins(8, 10, 8, 8)
                fav_tween_layout.setSpacing(6)
                
                fav_tween_row = QtWidgets.QHBoxLayout()
                fav_tween_row.addWidget(QtWidgets.QLabel("Prev"))
                self.fav_tween_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
                self.fav_tween_slider.setRange(0, 100)
                self.fav_tween_slider.setValue(50)
                self.fav_tween_slider.setFixedHeight(24)
                self.fav_tween_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
                self.fav_tween_slider.setTickInterval(25)
                self.fav_tween_slider.setStyleSheet("""
                    QSlider::groove:horizontal {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #FF6B35, stop:0.5 #00BCD4, stop:1 #4CAF50);
                        height: 6px;
                        border-radius: 3px;
                    }
                    QSlider::handle:horizontal {
                        background: #FFFFFF;
                        border: 2px solid #00BCD4;
                        width: 14px;
                        height: 14px;
                        margin: -5px 0;
                        border-radius: 8px;
                    }
                    QSlider::handle:horizontal:hover {
                        background: #00BCD4;
                        border: 2px solid #FFFFFF;
                    }
                """)
                fav_tween_row.addWidget(self.fav_tween_slider)
                fav_tween_row.addWidget(QtWidgets.QLabel("Next"))
                
                self.fav_tween_pct_label = QtWidgets.QLabel("50%")
                self.fav_tween_pct_label.setFixedWidth(35)
                self.fav_tween_pct_label.setAlignment(QtCore.Qt.AlignCenter)
                self.fav_tween_pct_label.setStyleSheet("font-weight: bold; color: #00BCD4; font-size: 11px;")
                fav_tween_row.addWidget(self.fav_tween_pct_label)
                fav_tween_layout.addLayout(fav_tween_row)
                
                # Preset row cho Favorites
                fav_preset_row = QtWidgets.QHBoxLayout()
                from functools import partial
                for pct in [0, 25, 50, 75, 100]:
                    btn = QtWidgets.QPushButton("%d%%" % pct)
                    btn.setFixedHeight(20)
                    btn.setStyleSheet("""
                        QPushButton {
                            background: #3A3A3A;
                            border: 1px solid #555;
                            border-radius: 4px;
                            color: #E0E0E0;
                            font-size: 10px;
                        }
                        QPushButton:hover {
                            background: #00BCD4;
                            color: #FFFFFF;
                            border-color: #00BCD4;
                        }
                    """)
                    btn.clicked.connect(partial(self.on_tween_preset, pct))
                    fav_preset_row.addWidget(btn)
                fav_tween_layout.addLayout(fav_preset_row)
                
                self.fav_tween_slider.sliderPressed.connect(self.on_tween_slider_pressed)
                self.fav_tween_slider.valueChanged.connect(self.on_tween_slider_changed)
                self.fav_tween_slider.sliderReleased.connect(self.on_tween_slider_released)
                
                fav_layout.addWidget(fav_tween_group)
                
                # GroupBox 3: Timing & Inbetweens (Favorites)
                fav_time_group = QtWidgets.QGroupBox("Timing & Inbetweens (Timing & Diễn hoạt)")
                fav_time_layout = QtWidgets.QVBoxLayout(fav_time_group)
                fav_time_layout.setContentsMargins(8, 10, 8, 8)
                fav_time_layout.setSpacing(6)
                
                fav_ib_count_row = QtWidgets.QHBoxLayout()
                fav_ib_count_row.addWidget(QtWidgets.QLabel("Số lượng (Frames):"))
                self.fav_ib_count_spin = QtWidgets.QSpinBox()
                self.fav_ib_count_spin.setRange(1, 500)
                self.fav_ib_count_spin.setValue(1)
                self.fav_ib_count_spin.setFixedHeight(22)
                fav_ib_count_row.addWidget(self.fav_ib_count_spin)
                fav_time_layout.addLayout(fav_ib_count_row)
                
                fav_ib_btn_row = QtWidgets.QHBoxLayout()
                self.fav_add_ib_btn = QtWidgets.QPushButton("Add Inbetween (+)")
                self.fav_add_ib_btn.setIcon(AnimeowIcons.icon_reset())
                self.fav_add_ib_btn.setFixedHeight(24)
                self.fav_add_ib_btn.clicked.connect(self.on_add_inbetween)
                fav_ib_btn_row.addWidget(self.fav_add_ib_btn)
                
                self.fav_remove_ib_btn = QtWidgets.QPushButton("Remove Inbetween (-)")
                self.fav_remove_ib_btn.setIcon(AnimeowIcons.icon_clean())
                self.fav_remove_ib_btn.setFixedHeight(24)
                self.fav_remove_ib_btn.clicked.connect(self.on_remove_inbetween)
                fav_ib_btn_row.addWidget(self.fav_remove_ib_btn)
                fav_time_layout.addLayout(fav_ib_btn_row)
                
                fav_layout.addWidget(fav_time_group)
                
                # GroupBox 4: Round Tool (Favorites)
                rnd_group = QtWidgets.QGroupBox("Làm tròn số (Round Tool)")
                rnd_lay = QtWidgets.QVBoxLayout(rnd_group)
                rnd_lay.setContentsMargins(8, 10, 8, 8)
                rnd_lay.setSpacing(6)
                
                round_sub_layout = QtWidgets.QGridLayout()
                round_sub_layout.addWidget(QtWidgets.QLabel("Làm tròn đến:"), 0, 0)
                self.fav_round_precision_combo = QtWidgets.QComboBox()
                self.fav_round_precision_combo.addItems([
                    "Số nguyên (ví dụ: 1)", 
                    "1 chữ số thập phân (ví dụ: 1.1)", 
                    "2 chữ số thập phân (ví dụ: 1.23)",
                    "Đặt giá trị về 0 (Reset)"
                ])
                round_sub_layout.addWidget(self.fav_round_precision_combo, 0, 1)
                
                round_sub_layout.addWidget(QtWidgets.QLabel("Môi trường:"), 1, 0)
                self.fav_round_target_combo = QtWidgets.QComboBox()
                self.fav_round_target_combo.addItems([
                    "Channel Box (Thuộc tính chọn)", 
                    "Graph Editor (Keyframe chọn)",
                    "Keyframe tại frame hiện tại",
                    "Toàn bộ keyframe (Timeline)"
                ])
                round_sub_layout.addWidget(self.fav_round_target_combo, 1, 1)
                
                self.fav_round_btn = QtWidgets.QPushButton("Làm tròn số")
                self.fav_round_btn.setIcon(AnimeowIcons.icon_round())
                self.fav_round_btn.setObjectName("accent_btn")
                self.fav_round_btn.setFixedHeight(28)
                self.fav_round_btn.clicked.connect(self.on_round_values)
                round_sub_layout.addWidget(self.fav_round_btn, 2, 0, 1, 2)
                
                # Reset row
                reset_row = QtWidgets.QHBoxLayout()
                self.fav_reset_t_btn = QtWidgets.QPushButton("Reset Translate (T -> 0)")
                self.fav_reset_t_btn.setIcon(AnimeowIcons.icon_reset())
                self.fav_reset_t_btn.setFixedHeight(24)
                self.fav_reset_t_btn.clicked.connect(self.on_reset_translate)
                reset_row.addWidget(self.fav_reset_t_btn)
                
                self.fav_reset_r_btn = QtWidgets.QPushButton("Reset Rotate (R -> 0)")
                self.fav_reset_r_btn.setIcon(AnimeowIcons.icon_reset())
                self.fav_reset_r_btn.setFixedHeight(24)
                self.fav_reset_r_btn.clicked.connect(self.on_reset_rotate)
                reset_row.addWidget(self.fav_reset_r_btn)
                
                round_sub_layout.addLayout(reset_row, 3, 0, 1, 2)
                rnd_lay.addLayout(round_sub_layout)
                fav_layout.addWidget(rnd_group)
                fav_layout.addStretch()
                
                self.tab_widget.addTab(fav_widget, "Favorites")
                self.setMinimumWidth(250)
            self.tab_widget.tabBar().hide()
        else:
            self.tab_widget.addTab(wrap_in_scroll(tab1), "Space & Bake")
            self.tab_widget.addTab(wrap_in_scroll(tab2), "Curve & Motion")
            self.tab_widget.addTab(wrap_in_scroll(tab3), "Rig & Mirror")
            self.tab_widget.addTab(wrap_in_scroll(tab4), "Output & Scene")
            tab_view_layer = animeow_view_layer.AnimeowViewLayerUI()
            self.tab_widget.addTab(tab_view_layer, "View Layer")
            self.tab_widget.addTab(wrap_in_scroll(tab5), "Launchers")
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
        if cmds.optionVar(exists=self.OP_PB_CUSTOM_DIR):
            self.pb_dir_edit.setText(cmds.optionVar(query=self.OP_PB_CUSTOM_DIR))
            
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
            val = cmds.optionVar(query=self.OP_RT_PRECISION)
            if hasattr(self, 'round_precision_combo'):
                self.round_precision_combo.setCurrentIndex(val)
            if hasattr(self, 'fav_round_precision_combo'):
                self.fav_round_precision_combo.setCurrentIndex(val)
        if cmds.optionVar(exists=self.OP_RT_TARGET):
            val = cmds.optionVar(query=self.OP_RT_TARGET)
            if hasattr(self, 'round_target_combo'):
                self.round_target_combo.setCurrentIndex(val)
            if hasattr(self, 'fav_round_target_combo'):
                self.fav_round_target_combo.setCurrentIndex(val)
                
        # Overlapper Settings
        if hasattr(self, 'ov_softness_spin'):
            if cmds.optionVar(exists=self.OP_OV_SOFTNESS):
                self.ov_softness_spin.setValue(cmds.optionVar(query=self.OP_OV_SOFTNESS))
            if cmds.optionVar(exists=self.OP_OV_SCALE):
                self.ov_scale_spin.setValue(cmds.optionVar(query=self.OP_OV_SCALE))
            if cmds.optionVar(exists=self.OP_OV_WIND_ENABLED):
                self.ov_wind_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_WIND_ENABLED)))
            if cmds.optionVar(exists=self.OP_OV_WIND_SCALE):
                self.ov_wind_scale_spin.setValue(cmds.optionVar(query=self.OP_OV_WIND_SCALE))
            if cmds.optionVar(exists=self.OP_OV_WIND_SPEED):
                self.ov_wind_speed_spin.setValue(cmds.optionVar(query=self.OP_OV_WIND_SPEED))
            if cmds.optionVar(exists=self.OP_OV_SKIP_FIRST):
                self.ov_skip_first_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_SKIP_FIRST)))
            if cmds.optionVar(exists=self.OP_OV_TRANSLATE):
                self.ov_translate_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_TRANSLATE)))
            if cmds.optionVar(exists=self.OP_OV_HIERARCHY):
                self.ov_hierarchy_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_HIERARCHY)))
            if cmds.optionVar(exists=self.OP_OV_CYCLE):
                self.ov_cycle_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_CYCLE)))
            if cmds.optionVar(exists=self.OP_OV_BAKE_LAYER):
                self.ov_bake_layer_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_BAKE_LAYER)))
            if cmds.optionVar(exists=self.OP_OV_ADAPTIVE_SCALE):
                self.ov_adaptive_scale_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_ADAPTIVE_SCALE)))
            if cmds.optionVar(exists=self.OP_OV_SEL_SET):
                self.ov_sel_set_cb.setChecked(bool(cmds.optionVar(query=self.OP_OV_SEL_SET)))

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
        cmds.optionVar(floatValue=(self.OP_PB_SCALE, self.pb_scale_spin.value()))
        cmds.optionVar(intValue=(self.OP_PB_VIEWER, int(self.pb_viewer_cb.isChecked())))
        cmds.optionVar(intValue=(self.OP_PB_OVERWRITE, int(self.pb_overwrite_cb.isChecked())))
        cmds.optionVar(intValue=(self.OP_PB_MULTI_CAM, int(self.multi_cam_cb.isChecked())))
        cmds.optionVar(stringValue=(self.OP_PB_CUSTOM_DIR, self.pb_dir_edit.text().strip()))
        
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
        if hasattr(self, 'round_precision_combo'):
            cmds.optionVar(intValue=(self.OP_RT_PRECISION, self.round_precision_combo.currentIndex()))
        elif hasattr(self, 'fav_round_precision_combo'):
            cmds.optionVar(intValue=(self.OP_RT_PRECISION, self.fav_round_precision_combo.currentIndex()))
            
        if hasattr(self, 'round_target_combo'):
            cmds.optionVar(intValue=(self.OP_RT_TARGET, self.round_target_combo.currentIndex()))
        elif hasattr(self, 'fav_round_target_combo'):
            cmds.optionVar(intValue=(self.OP_RT_TARGET, self.fav_round_target_combo.currentIndex()))
            
        # Overlapper Settings
        if hasattr(self, 'ov_softness_spin'):
            cmds.optionVar(floatValue=(self.OP_OV_SOFTNESS, self.ov_softness_spin.value()))
            cmds.optionVar(floatValue=(self.OP_OV_SCALE, self.ov_scale_spin.value()))
            cmds.optionVar(intValue=(self.OP_OV_WIND_ENABLED, int(self.ov_wind_cb.isChecked())))
            cmds.optionVar(floatValue=(self.OP_OV_WIND_SCALE, self.ov_wind_scale_spin.value()))
            cmds.optionVar(floatValue=(self.OP_OV_WIND_SPEED, self.ov_wind_speed_spin.value()))
            cmds.optionVar(intValue=(self.OP_OV_SKIP_FIRST, int(self.ov_skip_first_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_TRANSLATE, int(self.ov_translate_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_HIERARCHY, int(self.ov_hierarchy_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_CYCLE, int(self.ov_cycle_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_BAKE_LAYER, int(self.ov_bake_layer_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_ADAPTIVE_SCALE, int(self.ov_adaptive_scale_cb.isChecked())))
            cmds.optionVar(intValue=(self.OP_OV_SEL_SET, int(self.ov_sel_set_cb.isChecked())))

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
            self.owner_txt.setText(", ".join(sel))
            self.save_settings()
        else:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Hãy chọn ít nhất một đối tượng làm Owner!")

    # --- LOGIC THỰC THI ---

    def on_link(self):
        target = self.target_txt.text().strip()
        owner_raw = self.owner_txt.text().strip()
        
        # Lấy danh sách owner và target
        if not owner_raw:
            # Nếu ô Owner trống, thử lấy từ selection trên viewport
            sel = cmds.ls(sl=True) or []
            if len(sel) >= 2:
                # Nếu chọn ít nhất 2 vật thể: cái đầu là target, còn lại là owner
                target = sel[0]
                owners = sel[1:]
                self.target_txt.setText(target)
                self.owner_txt.setText(", ".join(owners))
                self.save_settings()
            elif len(sel) == 1:
                # Nếu chỉ chọn đúng 1 vật thể, coi nó là Owner và Target sẽ là World
                target = ""
                owners = [sel[0]]
                self.owner_txt.setText(owners[0])
                self.target_txt.setText("")
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Thiếu thông tin",
                    "Vui lòng gán Owner (Vật bị dẫn) hoặc chọn ít nhất 1 đối tượng trên viewport!"
                )
                return
        else:
            owners = [o.strip() for o in owner_raw.split(",") if o.strip()]

        # HỖ TRỢ LINK TO WORLD
        is_world_link = False
        if not target or target.lower() == "world":
            if not target:
                res = QtWidgets.QMessageBox.question(
                    self, "Liên kết vào thế giới (Link to World)",
                    "Bạn chưa gán đối tượng Target. Bạn có muốn liên kết (Link) các đối tượng Owner vào Không gian thế giới (World Space) không?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if res == QtWidgets.QMessageBox.No:
                    return
            target = "world"
            is_world_link = True

        if not is_world_link and not cmds.objExists(target):
            QtWidgets.QMessageBox.critical(self, "Lỗi đối tượng", "Đối tượng Target: %s không tồn tại trong scene!" % target)
            return

        valid_owners = []
        for owner in owners:
            if not cmds.objExists(owner):
                QtWidgets.QMessageBox.critical(self, "Lỗi đối tượng", "Đối tượng Owner: %s không tồn tại trong scene!" % owner)
                return
            if not is_world_link and target == owner:
                QtWidgets.QMessageBox.warning(self, "Lỗi ràng buộc", "Không thể liên kết đối tượng %s với chính nó!" % owner)
                continue
            valid_owners.append(owner)

        if not valid_owners:
            return

        use_locator = True
        self.save_settings()

        if use_locator:
            s_time = cmds.playbackOptions(q=True, minTime=True)
            e_time = cmds.playbackOptions(q=True, maxTime=True)
            curr_time = cmds.currentTime(q=True)

            success_count = 0
            failed_owners = []

            for owner in valid_owners:
                # Kiểm tra xem owner đã có liên kết locator nào chưa
                baker = smart_link.AnimationBaker(owner)
                loc_parent, loc_child = baker.find_locator_names()
                if loc_parent or loc_child:
                    failed_owners.append((owner, "Đã có liên kết locator từ trước."))
                    continue

                try:
                    # Tiến hành tạo Smart Link
                    manager = smart_link.SmartLinkManager(owner, target)
                    has_anim = manager.detect_existing_animation()

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
                    success_count += 1
                except Exception as e:
                    failed_owners.append((owner, smart_link.exception_to_unicode(e)))

            # Báo cáo kết quả
            if success_count > 0 and not failed_owners:
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    "Đã tạo liên kết Locator thành công cho %d đối tượng!" % success_count
                )
            elif success_count > 0 and failed_owners:
                err_msg = "Đã liên kết thành công %d đối tượng.\n❌ Thất bại %d đối tượng:\n" % (success_count, len(failed_owners))
                for f_owner, f_err in failed_owners:
                    err_msg += "  + %s: %s\n" % (f_owner, f_err)
                QtWidgets.QMessageBox.warning(self, "Hoàn thành có lỗi", err_msg)
            else:
                err_msg = "Không thể tạo liên kết cho đối tượng nào:\n"
                for f_owner, f_err in failed_owners:
                    err_msg += "  + %s: %s\n" % (f_owner, f_err)
                QtWidgets.QMessageBox.critical(self, "Thất bại", err_msg)

        else:
            # Gán trực tiếp không qua locator
            for owner in valid_owners:
                try:
                    cmds.parentConstraint(target, owner, maintainOffset=True)
                    try:
                        cmds.scaleConstraint(target, owner, maintainOffset=True)
                    except:
                        pass
                    print(u"[SmartLink] Đã liên kết trực tiếp %s đi theo %s." % (owner, target))
                except Exception as e:
                    print(u"[SmartLink] Không thể liên kết trực tiếp %s: %s" % (owner, str(e)))
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã tạo liên kết trực tiếp thành công!")

    def on_switch_target(self):
        owner_raw = self.owner_txt.text().strip()
        owners = []
        if owner_raw:
            owners = [o.strip() for o in owner_raw.split(",") if o.strip()]
        else:
            sel = cmds.ls(sl=True) or []
            if sel:
                owners = [sel[0]]
                self.owner_txt.setText(owners[0])
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn vật bị dẫn (Owner)!")
                return

        new_target = self.target_txt.text().strip()
        if not new_target or not cmds.objExists(new_target):
            # Nếu trống, thử lấy vật chọn đầu tiên không nằm trong danh sách owners
            sel = cmds.ls(sl=True) or []
            possible = [s for s in sel if s not in owners]
            if possible:
                new_target = possible[0]
                self.target_txt.setText(new_target)
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn hoặc gán Target mới để chuyển đổi!")
                return

        curr_time = cmds.currentTime(q=True)
        success_count = 0
        failed_owners = []
        
        for owner in owners:
            if not cmds.objExists(owner):
                continue
            try:
                switcher = smart_link.SpaceSwitcher(owner, curr_time)
                success = switcher.switch_to_target(new_target)
                if success:
                    success_count += 1
                else:
                    failed_owners.append(owner)
            except Exception:
                failed_owners.append(owner)
                
        if success_count > 0 and not failed_owners:
            QtWidgets.QMessageBox.information(
                self, "Chuyển Driver Thành công",
                "Đã chuyển đổi driver của %d đối tượng sang %s thành công tại frame %d." % (success_count, new_target, curr_time)
            )
        elif success_count > 0 and failed_owners:
            QtWidgets.QMessageBox.warning(
                self, "Hoàn thành có lỗi", 
                "Đã chuyển driver thành công cho %d đối tượng sang %s.\n❌ Thất bại trên các đối tượng: %s" % (success_count, new_target, ", ".join(failed_owners))
            )
        else:
            QtWidgets.QMessageBox.critical(
                self, "Thất bại",
                "Không thể chuyển driver cho đối tượng nào. Vui lòng kiểm tra lại xem các đối tượng đã có liên kết locator chưa."
            )

    def on_bake_clean(self):
        owner_raw = self.owner_txt.text().strip()
        owners = []
        if owner_raw:
            owners = [o.strip() for o in owner_raw.split(",") if o.strip()]
        else:
            sel = cmds.ls(sl=True) or []
            if sel:
                owners = sel
                self.owner_txt.setText(", ".join(owners))
                self.save_settings()
            else:
                QtWidgets.QMessageBox.warning(self, "Thiếu đối tượng", "Vui lòng chọn các đối tượng cần Bake!")
                return

        valid_owners = [o for o in owners if cmds.objExists(o)]
        if not valid_owners:
            QtWidgets.QMessageBox.critical(self, "Lỗi đối tượng", "Không có đối tượng Owner nào tồn tại trong scene!")
            return

        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận Bake & Clean",
            "Sẽ Bake chuyển động từ locator/constraint vào keyframe của %d đối tượng:\n%s\nvà dọn dẹp các liên kết thừa. Bạn có chắc chắn?" % (len(valid_owners), ", ".join(valid_owners)),
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

        success_count = 0
        failed_owners = []
        
        for owner in valid_owners:
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
                success_count += 1
            except Exception as e:
                failed_owners.append((owner, smart_link.exception_to_unicode(e)))
                
        if success_count > 0 and not failed_owners:
            QtWidgets.QMessageBox.information(
                self, "Thành công", 
                "Đã Bake và dọn dẹp thành công chuyển động cho %d đối tượng!" % success_count
            )
        elif success_count > 0 and failed_owners:
            err_msg = "Đã Bake thành công %d đối tượng.\n❌ Thất bại %d đối tượng:\n" % (success_count, len(failed_owners))
            for f_owner, f_err in failed_owners:
                err_msg += "  + %s: %s\n" % (f_owner, f_err)
            QtWidgets.QMessageBox.warning(self, "Hoàn thành có lỗi", err_msg)
        else:
            err_msg = "Lỗi xảy ra khi bake cho các đối tượng:\n"
            for f_owner, f_err in failed_owners:
                err_msg += "  + %s: %s\n" % (f_owner, f_err)
            QtWidgets.QMessageBox.critical(self, "Thất bại", err_msg)

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
            
        # Thêm thư mục chứa tweenMachine vào MAYA_SCRIPT_PATH của Maya
        try:
            current_script_path = os.environ.get("MAYA_SCRIPT_PATH", "")
            if path not in current_script_path:
                os.environ["MAYA_SCRIPT_PATH"] = path + os.pathsep + current_script_path
                # Đồng bộ lại với Maya
                import maya.mel as mel
                mel.eval("rehash;")
        except Exception:
            pass
            
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
                launcher_file = os.path.join(animo_launcher_dir, "Animo_Launcher.py")
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("Animo_Launcher_Module", launcher_file)
                    launcher_module = importlib.util.module_from_spec(spec)
                    sys.modules["Animo_Launcher_Module"] = launcher_module
                    spec.loader.exec_module(launcher_module)
                except ImportError:
                    import imp
                    launcher_module = imp.load_source("Animo_Launcher_Module", launcher_file)
                _tb = launcher_module.toolbar()
                _tb.startUI()
                print("[Animo] Đã khởi chạy Animo thành công.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Lỗi", "Lỗi khởi chạy Animo:\n%s" % str(e))

    def on_launch_anm_hider(self):
        try:
            import sys
            import importlib
            if "animeow_maya_toolboard_v02.core.anm_hider" in sys.modules:
                importlib.reload(sys.modules["animeow_maya_toolboard_v02.core.anm_hider"])
            else:
                import animeow_maya_toolboard_v02.core.anm_hider as anm_hider
            
            from animeow_maya_toolboard_v02.core import anm_hider
            anm_hider.show_hider()
            print("[Animeow] Đã khởi chạy ANM Hider.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Không thể chạy ANM Hider. Vui lòng đảm bảo bạn đã cài đặt anm_hider trong core:\n%s" % str(e)
            )

    def on_toggle_multi_cam(self, checked):
        self.camera_combo.setVisible(not checked)
        self.camera_list_widget.setVisible(checked)

    def on_camera_item_clicked(self, item):
        # Tự động đảo ngược trạng thái check khi click trực tiếp vào dòng camera
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def on_browse_pb_dir(self):
        """Mở hộp thoại chọn thư mục lưu video"""
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Chọn Thư mục lưu Playblast", self.pb_dir_edit.text())
        if dir_path:
            dir_path = os.path.normpath(dir_path).replace("\\", "/")
            self.pb_dir_edit.setText(dir_path)
            self.save_settings()

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
        percent = int(self.pb_scale_spin.value() * 100)
        viewer = self.pb_viewer_cb.isChecked()
        overwrite = self.pb_overwrite_cb.isChecked()
        custom_dir = self.pb_dir_edit.text().strip()
        
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
                    overwrite=overwrite,
                    custom_dir=custom_dir
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
                try:
                    from importlib import reload
                except ImportError:
                    pass
                reload(ml_worldBake)
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
        
        # Bọc toàn bộ các thao tác tạo curve và locator vào một undo chunk duy nhất
        # Tránh làm rác hàng trăm lệnh đơn lẻ trong danh sách Undo của Maya
        cmds.undoInfo(openChunk=True, chunkName="CreateArcTrail")
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
        finally:
            cmds.undoInfo(closeChunk=True)
            
    def on_update_arc_trails(self):
        """Cập nhật các Arc Trail hiện có (nếu chọn thì update chọn, không chọn thì update hết)"""
        sel = cmds.ls(sl=True) or []
        self.save_settings()
        
        show_ticks = self.at_show_ticks_cb.isChecked()
        show_keys = self.at_show_keys_cb.isChecked()
        tick_size = self.at_tick_size_spin.value()
        
        tracker = arc_tracker.ArcTracker()
        
        cmds.undoInfo(openChunk=True, chunkName="UpdateArcTrails")
        try:
            count = tracker.update_trails(
                selected_objs=sel,
                show_ticks=show_ticks,
                show_keys=show_keys,
                tick_size=tick_size
            )
            if count > 0:
                cmds.warning("Đã cập nhật thành công %d Arc Trail!" % count)
            else:
                QtWidgets.QMessageBox.information(
                    self, "Thông báo", 
                    "Không tìm thấy Arc Trail nào hoạt động để cập nhật!"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi cập nhật Trail",
                "Lỗi xảy ra khi cập nhật Arc Trail:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)
            
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
        smart_bake = self.wb_smart_bake_cb.isChecked()
        
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
                    channels=channels,
                    smart_bake=smart_bake
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
        smart_bake = self.wb_smart_bake_cb.isChecked()
        
        wbm = world_bake.WorldBakeManager()
        
        success_objs = []
        try:
            for item in sel:
                obj = wbm.bake_from_locator(
                    locator_or_obj=item,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    step=step,
                    smart_clean=smart_clean,
                    smart_bake=smart_bake
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

    def on_create_custom_shelf(self):
        """Khởi tạo hoặc cập nhật thanh công cụ nhanh Shelf Animeow"""
        try:
            shelf.create_shelf()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi",
                "Không thể tạo hoặc cập nhật Shelf:\n%s" % str(e)
            )

    def on_toggle_graph_editor(self):
        """Bật/Tắt Graph Editor"""
        try:
            shelf.toggle_graph_editor()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể bật/tắt Graph Editor:\n%s" % str(e))

    def on_toggle_reference_editor(self):
        """Bật/Tắt Reference Editor"""
        try:
            shelf.toggle_reference_editor()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể bật/tắt Reference Editor:\n%s" % str(e))

    def on_toggle_outliner(self):
        """Bật/Tắt Outliner"""
        try:
            shelf.toggle_outliner()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể bật/tắt Outliner:\n%s" % str(e))

    def on_run_antivirus(self):
        """Khởi chạy quét và diệt virus trong scene"""
        try:
            shelf.run_anti_virus()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể chạy diệt Virus:\n%s" % str(e))

    def on_save_increment(self):
        """Lưu file tăng dần (Save Increment)"""
        try:
            shelf.save_increment()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể thực hiện Save Increment:\n%s" % str(e))

    def on_save_up_version(self):
        """Lưu file nâng Version"""
        try:
            shelf.save_up_version()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Lỗi xảy ra khi nâng version:\n%s" % str(e))

    def on_clean_folder(self):
        """Dọn dẹp thư mục"""
        try:
            shelf.clean_folder()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Lỗi xảy ra khi dọn dẹp thư mục:\n%s" % str(e))
    def on_round_values(self):
        """Làm tròn số thuộc tính hoặc keyframe"""
        self.save_settings()
        
        # Check sender để lấy đúng combo box của Favorites hoặc Tab 2 chính
        sender = self.sender()
        if sender == getattr(self, 'fav_round_btn', None):
            precision_idx = self.fav_round_precision_combo.currentIndex()
            target_idx = self.fav_round_target_combo.currentIndex()
        else:
            if hasattr(self, 'round_precision_combo') and hasattr(self, 'round_target_combo'):
                precision_idx = self.round_precision_combo.currentIndex()
                target_idx = self.round_target_combo.currentIndex()
            else:
                precision_idx = 0
                target_idx = 0
            
        precision = -1 if precision_idx == 3 else precision_idx
        
        # Lấy môi trường đích
        target_map = {
            0: 'channel_box',
            1: 'graph_editor',
            2: 'current_frame',
            3: 'all_keyframes'
        }
        target = target_map.get(target_idx, 'channel_box')
        
        action_title = "Đặt về 0" if precision == -1 else "Làm tròn số"
        
        # Bọc trong một khối Undo chunk để animator có thể Ctrl + Z hoàn tác nhanh
        cmds.undoInfo(openChunk=True)
        try:
            success, msg = round_tool.round_selected_values(precision, target)
            if success:
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi %s" % action_title,
                "Lỗi xảy ra khi thực hiện %s:\n%s" % (action_title.lower(), str(e))
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_reset_translate(self):
        """Đặt Translate X, Y, Z về 0"""
        self.save_settings()
        target_idx = self.round_target_combo.currentIndex()
        target_map = {
            0: 'channel_box',
            1: 'graph_editor',
            2: 'current_frame',
            3: 'all_keyframes'
        }
        target = target_map.get(target_idx, 'channel_box')
        
        channels = ['translateX', 'translateY', 'translateZ']
        
        cmds.undoInfo(openChunk=True)
        try:
            success, msg = round_tool.round_selected_values(-1, target, channels)
            if success:
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Đặt Translate về 0",
                "Lỗi xảy ra khi đặt Translate về 0:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_reset_rotate(self):
        """Đặt Rotate X, Y, Z về 0"""
        self.save_settings()
        target_idx = self.round_target_combo.currentIndex()
        target_map = {
            0: 'channel_box',
            1: 'graph_editor',
            2: 'current_frame',
            3: 'all_keyframes'
        }
        target = target_map.get(target_idx, 'channel_box')
        
        channels = ['rotateX', 'rotateY', 'rotateZ']
        
        cmds.undoInfo(openChunk=True)
        try:
            success, msg = round_tool.round_selected_values(-1, target, channels)
            if success:
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Đặt Rotate về 0",
                "Lỗi xảy ra khi đặt Rotate về 0:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

        # --- TEMP PIVOT CALLBACKS ---
    def on_tp_create(self):
        """Tạo Temp Locator tại vị trí của control được chọn"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một Rig Control trong Viewport!")
            return
            
        try:
            loc = temp_pivot.create_temp_locator(sel)
            cmds.select(loc)
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã tạo Temp Locator: %s\nHãy di chuyển Locator này tới vị trí Pivot mới, sau đó nhấn 'Kích hoạt Pivot'." % loc
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi",
                "Có lỗi xảy ra khi tạo Temp Locator:\n%s" % str(e)
            )

    def on_tp_active(self):
        """Kích hoạt tâm xoay tạm thời"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Temp Locator hoộc Control tương ứng!")
            return
            
        obj = sel[0]
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        cmds.undoInfo(openChunk=True)
        try:
            loc = temp_pivot.active_temp_pivot(obj, start_frame, end_frame)
            cmds.select(loc)
            cmds.warning("Đã kích hoạt Temp Pivot thành công! Hãy diễn hoạt xoay/dịch chuyển trên locator này.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Kích hoạt Pivot",
                "Không thể kích hoạt Temp Pivot:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_tp_release(self):
        """Nướng ngược lại chuyển động và giải phóng tâm xoay"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Temp Locator hoộc Control tương ứng để giải phóng!")
            return
            
        obj = sel[0]
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        cmds.undoInfo(openChunk=True)
        try:
            control = temp_pivot.release_temp_pivot(obj, start_frame, end_frame)
            cmds.select(control)
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                "Đã nướng trả chuyển động thành công về Control gốc: %s\nLocator tạm thời đã được gỡ bỏ." % control
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Giải phóng Pivot",
                "Có lỗi xảy ra khi giải phóng Temp Pivot:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    # --- MIRROR ANIM CALLBACKS ---
    def on_mir_execute(self):
        """Thực hiện đối xướng chuyển động"""
        scope_idx = self.mir_scope_combo.currentIndex()
        
        selected_objs = cmds.ls(sl=True) or []
        if not selected_objs:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng trong Viewport!")
            return
            
        objects_to_process = []
        if scope_idx == 0:
            objects_to_process = selected_objs
        else:
            parts = selected_objs[0].split(":")
            if len(parts) > 1:
                ns = ":".join(parts[:-1])
                objects_to_process = cmds.ls(ns + ":*", type="transform") or []
            else:
                objects_to_process = cmds.ls(type="transform") or []
                
        if not objects_to_process:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Không tìm thớđ đối tượng nào để xử lý!")
            return
            
        mode_map = {
            0: 'swap',
            1: 'left_to_right',
            2: 'right_to_left',
            3: 'flip_selected'
        }
        mode = mode_map.get(self.mir_mode_combo.currentIndex(), 'swap')
        
        time_idx = self.mir_time_combo.currentIndex()
        time_range = None
        if time_idx == 1:
            time_range_slider = mel.eval("timeControl -q -range $gPlayBackSlider")
            if time_range_slider:
                clean_range = time_range_slider.replace('"', '').split(':')
                if len(clean_range) == 2:
                    time_range = (float(clean_range[0]), float(clean_range[1]))
            
            if not time_range:
                time_range = (cmds.playbackOptions(q=True, minTime=True), cmds.playbackOptions(q=True, maxTime=True))
                
        invert_map = {
            'translateX': self.mir_inv_tx_cb.isChecked(),
            'translateY': self.mir_inv_ty_cb.isChecked(),
            'translateZ': self.mir_inv_tz_cb.isChecked(),
            'rotateX': self.mir_inv_rx_cb.isChecked(),
            'rotateY': self.mir_inv_ry_cb.isChecked(),
            'rotateZ': self.mir_inv_rz_cb.isChecked()
        }
        
        # Naming preset
        preset_idx = self.mir_preset_combo.currentIndex()
        left_pat = None
        right_pat = None
        if preset_idx == 1: # Mixamo
            left_pat = ["Left", "left", "mixamorig:Left"]
            right_pat = ["Right", "right", "mixamorig:Right"]
        elif preset_idx == 2: # Advanced Skeleton
            left_pat = ["L_", "FKArmL", "FKForeArmL", "FKHandL", "FKLegL", "FKAnkleL"]
            right_pat = ["R_", "FKArmR", "FKForeArmR", "FKHandR", "FKLegR", "FKAnkleR"]
        elif preset_idx == 3: # MetaHuman
            left_pat = ["l_", "L_", "_L", "_l", "left", "Left"]
            right_pat = ["r_", "R_", "_R", "_r", "right", "Right"]
        elif preset_idx == 4: # Custom
            left_pat = [self.mir_custom_left_txt.text().strip()]
            right_pat = [self.mir_custom_right_txt.text().strip()]

        cmds.undoInfo(openChunk=True)
        try:
            success, msg = mirror_tool.execute_mirror(
                objects=objects_to_process,
                mode=mode,
                time_range=time_range,
                invert_map=invert_map,
                left_patterns=left_pat,
                right_patterns=right_pat
            )
            if success:
                QtWidgets.QMessageBox.information(self, "Thành công", msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Mirror Animation",
                "Có lỗi xảy ra khi thực hiện đối xướng chuyển động:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

        # --- NEW UI UX UPGRADE CALLBACKS ---
    def on_swap_target_owner(self):
        """Đổi bên Target và Owner cho nhau"""
        tgt = self.target_txt.text()
        own = self.owner_txt.text()
        self.target_txt.setText(own)
        self.owner_txt.setText(tgt)

    def on_mir_preset_changed(self, index):
        """Hiển thị hoặc ẩn các ô nhập Pattern tự định nghĩa"""
        is_custom = (index == 4)
        self.mir_custom_left_label.setVisible(is_custom)
        self.mir_custom_left_txt.setVisible(is_custom)
        self.mir_custom_right_label.setVisible(is_custom)
        self.mir_custom_right_txt.setVisible(is_custom)

    def on_tab_changed(self, index):
        """Cập nhật highlight cho nút tương ứng với Tab đang mở"""
        for i, btn in enumerate(self.compact_buttons):
            if i == index:
                btn.setStyleSheet("background-color: #00BCD4; color: #FFFFFF; font-size: 15px; border: none; border-radius: 4px;")
            else:
                btn.setStyleSheet("background-color: transparent; color: #E0E0E0; font-size: 15px; border: none; border-radius: 4px;")

    def on_toggle_compact_mode(self, checked):
        """Bật/Ẩn chế độ thu gọn Compact Mode"""
        ctrl_name = self.WORKSPACE_CONTROL_NAME
        if checked:
            self.tab_widget.tabBar().hide()
            self.compact_toolbar.show()
            self.compact_toggle_btn.setText("⚡ Rộng")
            self.setMinimumWidth(80)
            
            # Highlight currently selected tab
            self.on_tab_changed(self.tab_widget.currentIndex())
            
            # Try to shrink Maya workspace control width
            if cmds.workspaceControl(ctrl_name, exists=True):
                try:
                    cmds.workspaceControl(ctrl_name, edit=True, resizeWidth=150)
                except Exception:
                    pass
        else:
            self.tab_widget.tabBar().show()
            self.compact_toolbar.hide()
            self.compact_toggle_btn.setText("⚡ Gọn")
            self.setMinimumWidth(320)
            
            # Try to expand Maya workspace control width back
            if cmds.workspaceControl(ctrl_name, exists=True):
                try:
                    cmds.workspaceControl(ctrl_name, edit=True, resizeWidth=350)
                except Exception:
                    pass

    def on_rt_item_changed(self, item):
        """Tự động tô màu trạng thái cho control khi chỉnh sửa trong bảng"""
        self.rt_table.blockSignals(True)
        try:
            text = item.text().strip()
            if text:
                if cmds.objExists(text):
                    item.setForeground(QtGui.QColor("#4CAF50")) # Green
                    item.setToolTip("Vật thể tồn tại trong Scene")
                else:
                    item.setForeground(QtGui.QColor("#F44336")) # Red
                    item.setToolTip("Không tìm thấy vật thể này!")
            else:
                item.setForeground(QtGui.QColor("#AAAAAA"))
        finally:
            self.rt_table.blockSignals(False)

    def refresh_rt_table_colors(self):
        """Làm mới toàn bộ màu sắc trạng thái của các ô trong bảng"""
        self.rt_table.blockSignals(True)
        try:
            for row in range(self.rt_table.rowCount()):
                for col in [0, 1]:
                    item = self.rt_table.item(row, col)
                    if item:
                        text = item.text().strip()
                        if text:
                            if cmds.objExists(text):
                                item.setForeground(QtGui.QColor("#4CAF50"))
                                item.setToolTip("Vật thể tồn tại trong Scene")
                            else:
                                item.setForeground(QtGui.QColor("#F44336"))
                                item.setToolTip("Không tìm thấy vật thể này!")
                        else:
                            item.setForeground(QtGui.QColor("#AAAAAA"))
        finally:
            self.rt_table.blockSignals(False)

    def on_bake_selected_ns(self):
        """Bake đối tượng chọn theo bước 2s, 3s, 4s, 5s hoặc 1s"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng để bake!")
            return
            
        step_idx = self.ns_step_combo.currentIndex()
        steps = [1, 2, 3, 4, 5]
        step = steps[step_idx]
        
        remove_constraints = self.ns_remove_constraints_cb.isChecked()
        
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        cmds.undoInfo(openChunk=True, chunkName="AnimeowBakeOnNs")
        try:
            cmds.bakeResults(
                sel,
                time=(start_frame, end_frame),
                simulation=True,
                sampleBy=step,
                oversamplingRate=1,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False, # Không giữ cực trị thưa, tạo key đều tăm tắp
            )
            
            # Nếu người dùng tích chọn Xóa Constraints, thực hiện xóa thủ công
            if remove_constraints:
                for obj in sel:
                    constraints = []
                    connections = cmds.listConnections(obj, source=True, destination=False) or []
                    for node in connections:
                        if cmds.nodeType(node) in [
                            "parentConstraint", "pointConstraint", "orientConstraint", 
                            "scaleConstraint", "aimConstraint", "poleVectorConstraint"
                        ]:
                            constraints.append(node)
                    if constraints:
                        try:
                            cmds.delete(list(set(constraints)))
                        except Exception:
                            pass
            QtWidgets.QMessageBox.information(
                self, "Thành công", 
                "Đã bake thành công %d đối tượng theo bước %ds." % (len(sel), step)
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi thực hiện bake:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    # --- RETARGET TOOL CALLBACKS ---
    def on_rt_get_source(self):
        """Lấy đối tượng chọn trong Viewport điền vào cột Source"""
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đối tượng trong Viewport!")
            return
            
        obj_name = sel[0]
        selected_ranges = self.rt_table.selectedRanges()
        if selected_ranges:
            row = selected_ranges[0].topRow()
        else:
            row = self.rt_table.rowCount()
            self.rt_table.insertRow(row)
            self.rt_table.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
            
        self.rt_table.setItem(row, 0, QtWidgets.QTableWidgetItem(obj_name))
        self.rt_table.selectRow(row)

    def on_rt_get_target(self):
        """Lấy đối tượng chọn trong Viewport điền vào cột Target"""
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đối tượng trong Viewport!")
            return
            
        obj_name = sel[0]
        selected_ranges = self.rt_table.selectedRanges()
        if selected_ranges:
            row = selected_ranges[0].topRow()
        else:
            row = self.rt_table.rowCount()
            self.rt_table.insertRow(row)
            self.rt_table.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
            
        self.rt_table.setItem(row, 1, QtWidgets.QTableWidgetItem(obj_name))
        self.rt_table.selectRow(row)

    def on_rt_refresh_namespaces(self):
        namespaces = retarget_tool.get_all_namespaces()
        self.rt_source_ns_combo.clear()
        self.rt_target_ns_combo.clear()
        self.rt_source_ns_combo.addItem("")
        self.rt_target_ns_combo.addItem("")
        for ns in namespaces:
            self.rt_source_ns_combo.addItem(ns)
            self.rt_target_ns_combo.addItem(ns)

    def on_rt_auto_map(self):
        source_ns = self.rt_source_ns_combo.currentText()
        target_ns = self.rt_target_ns_combo.currentText()
        if source_ns == target_ns and source_ns != "":
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Namespace Nguồn và Namespace Đích không nên trùng nhau!")
            return
            
        pairs = retarget_tool.auto_map_rigs(source_ns, target_ns)
        self.on_rt_clear_table()
        
        for src, tgt in pairs:
            row = self.rt_table.rowCount()
            self.rt_table.insertRow(row)
            self.rt_table.setItem(row, 0, QtWidgets.QTableWidgetItem(src))
            self.rt_table.setItem(row, 1, QtWidgets.QTableWidgetItem(tgt))
            
        QtWidgets.QMessageBox.information(
            self, "Thành công",
            "Đã tự động tìm và khớp nối thành công %d cặp control!" % len(pairs)
        )
        self.refresh_rt_table_colors()

    def on_rt_add_row(self):
        row = self.rt_table.rowCount()
        self.rt_table.insertRow(row)
        self.rt_table.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
        self.rt_table.setItem(row, 1, QtWidgets.QTableWidgetItem(""))

    def on_rt_del_row(self):
        selected_ranges = self.rt_table.selectedRanges()
        if not selected_ranges:
            return
        rows_to_delete = []
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                rows_to_delete.append(row)
        rows_to_delete = sorted(list(set(rows_to_delete)), reverse=True)
        for r in rows_to_delete:
            self.rt_table.removeRow(r)

    def on_rt_clear_table(self):
        self.rt_table.setRowCount(0)

    def on_rt_load_json(self):
        file_filter = "JSON Files (*.json)"
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Chọn file cấu hình Mapping", "", file_filter
        )
        if not filepath:
            return
            
        import json
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.on_rt_clear_table()
            for item in data:
                row = self.rt_table.rowCount()
                self.rt_table.insertRow(row)
                self.rt_table.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("source", "")))
                self.rt_table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("target", "")))
            print("[Retarget] Đã nạp cấu hình ánh xạ từ file: %s" % filepath)
            self.refresh_rt_table_colors()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Nạp cấu hình",
                "Không thể nạp file cấu hình ánh xạ:\n%s" % str(e)
            )

    def on_rt_save_json(self):
        rowCount = self.rt_table.rowCount()
        if rowCount == 0:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Bảng ánh xạ trống, không có gì để lưu!")
            return
            
        file_filter = "JSON Files (*.json)"
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu cấu hình Mapping", "", file_filter
        )
        if not filepath:
            return
            
        import json
        data = []
        for row in range(rowCount):
            src_item = self.rt_table.item(row, 0)
            tgt_item = self.rt_table.item(row, 1)
            src = src_item.text().strip() if src_item else ""
            tgt = tgt_item.text().strip() if tgt_item else ""
            data.append({"source": src, "target": tgt})
            
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            QtWidgets.QMessageBox.information(self, "Thành công", "Đã lưu cấu hình ánh xạ thành công!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Lưu cấu hình",
                "Không thể lưu file cấu hình ánh xạ:\n%s" % str(e)
            )

    def on_rt_execute(self):
        rowCount = self.rt_table.rowCount()
        if rowCount == 0:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêM hoộc khớp nối ít nhất một cặp control trong bảng!")
            return
            
        mapping_pairs = []
        for row in range(rowCount):
            src_item = self.rt_table.item(row, 0)
            tgt_item = self.rt_table.item(row, 1)
            src = src_item.text().strip() if src_item else ""
            tgt = tgt_item.text().strip() if tgt_item else ""
            if src and tgt:
                mapping_pairs.append((src, tgt))
                
        if not mapping_pairs:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Không có cặp đối tượng hợp lệ nào được điền!")
            return
            
        start_frame = cmds.playbackOptions(q=True, minTime=True)
        end_frame = cmds.playbackOptions(q=True, maxTime=True)
        
        step = self.rt_step_spin.value()
        maintain_offset = self.rt_maintain_offset_cb.isChecked()
        smart_bake = self.rt_smart_bake_cb.isChecked()
        
        idx = self.rt_channels_combo.currentIndex()
        channels = ['both', 'translate', 'rotate'][idx]
        
        cmds.undoInfo(openChunk=True)
        try:
            success, msg = retarget_tool.execute_retarget(
                mapping_pairs=mapping_pairs,
                start_frame=start_frame,
                end_frame=end_frame,
                step=step,
                maintain_offset=maintain_offset,
                channels=channels,
                smart_bake=smart_bake
            )
            if success:
                QtWidgets.QMessageBox.information(self, "Thành công", msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Retarget",
                "Có lỗi xảy ra trong quá trình Retarget:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

        # --- CONSTRAINT MANAGER CALLBACKS ---

    def on_parent_constraint(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 đối tượng (Driver -> Driven)!")
            return
        mo = self.constrain_offset_cb.isChecked()
        
        # Lọc các trục Translate bị bỏ chọn
        skip_t = []
        if not self.tx_cb.isChecked(): skip_t.append("x")
        if not self.ty_cb.isChecked(): skip_t.append("y")
        if not self.tz_cb.isChecked(): skip_t.append("z")
        
        # Lọc các trục Rotate bị bỏ chọn
        skip_r = []
        if not self.rx_cb.isChecked(): skip_r.append("x")
        if not self.ry_cb.isChecked(): skip_r.append("y")
        if not self.rz_cb.isChecked(): skip_r.append("z")
        
        try:
            cmds.parentConstraint(mo=mo, skipTranslate=skip_t, skipRotate=skip_r)
            cmds.warning("Đã tạo Parent Constraint thành công.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗ", "Không thể tạo Parent Constraint: " + str(e))

    def on_point_constraint(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 đối tượng (Driver -> Driven)!")
            return
        mo = self.constrain_offset_cb.isChecked()
        
        # Lọc các trục Translate bị bỏ chọn
        skip = []
        if not self.tx_cb.isChecked(): skip.append("x")
        if not self.ty_cb.isChecked(): skip.append("y")
        if not self.tz_cb.isChecked(): skip.append("z")
        
        try:
            cmds.pointConstraint(mo=mo, skip=skip)
            cmds.warning("Đã tạo Point Constraint thành công.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗ", "Không thể tạo Point Constraint: " + str(e))

    def on_orient_constraint(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 đối tượng (Driver -> Driven)!")
            return
        mo = self.constrain_offset_cb.isChecked()
        
        # Lọc các trục Rotate bị bỏ chọn
        skip = []
        if not self.rx_cb.isChecked(): skip.append("x")
        if not self.ry_cb.isChecked(): skip.append("y")
        if not self.rz_cb.isChecked(): skip.append("z")
        
        try:
            cmds.orientConstraint(mo=mo, skip=skip)
            cmds.warning("Đã tạo Orient Constraint thành công.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗ", "Không thể tạo Orient Constraint: " + str(e))

    def on_scale_constraint(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 đối tượng (Driver -> Driven)!")
            return
        mo = self.constrain_offset_cb.isChecked()
        
        # Dùng các trục Translate làm trục Scale tương ứng
        skip = []
        if not self.tx_cb.isChecked(): skip.append("x")
        if not self.ty_cb.isChecked(): skip.append("y")
        if not self.tz_cb.isChecked(): skip.append("z")
        
        try:
            cmds.scaleConstraint(mo=mo, skip=skip)
            cmds.warning("Đã tạo Scale Constraint thành công.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗ", "Không thể tạo Scale Constraint: " + str(e))

    def on_aim_constraint(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 đối tượng (Driver -> Driven)!")
            return
        mo = self.constrain_offset_cb.isChecked()
        
        # Lọc các trục Rotate bị bỏ chọn
        skip = []
        if not self.rx_cb.isChecked(): skip.append("x")
        if not self.ry_cb.isChecked(): skip.append("y")
        if not self.rz_cb.isChecked(): skip.append("z")
        
        try:
            cmds.aimConstraint(mo=mo, skip=skip)
            cmds.warning("Đã tạo Aim Constraint thành công.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗ", "Không thể tạo Aim Constraint: " + str(e))

    def on_delete_constraints(self):
        import maya.cmds as cmds
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng để xóa Constraint!")
            return
        
        constraint_types = [
            "parentConstraint", "pointConstraint", "orientConstraint",
            "scaleConstraint", "aimConstraint", "poleVectorConstraint",
            "geometryConstraint", "normalConstraint", "tangentConstraint"
        ]
        
        deleted_count = 0
        for obj in sel:
            children = cmds.listRelatives(obj, children=True, fullPath=True) or []
            for child in children:
                node_type = cmds.nodeType(child)
                if node_type in constraint_types:
                    try:
                        cmds.delete(child)
                        deleted_count += 1
                    except Exception:
                        pass
            
            connections = cmds.listConnections(obj, source=True, destination=False) or []
            for conn in connections:
                node_type = cmds.nodeType(conn)
                if node_type in constraint_types:
                    try:
                        cmds.delete(conn)
                        deleted_count += 1
                    except Exception:
                        pass
                        
        if deleted_count > 0:
            cmds.warning("Đã xóa thành công %d Constraint khỏi các đối tượng được chọn!" % deleted_count)
        else:
            cmds.warning("Không tìm thấy Constraint nào trực tiếp trên các đối tượng được chọn.")

    
    def on_clean_redundant_keys(self):
        """Dọn dẹp keyframe có giá trị bằng nhau liên tiếp"""
        from ..core import clean_redundant_keys
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng trên viewport!")
            return
            
        res = QtWidgets.QMessageBox.question(
            self, "Xác nhận dọn dẹp key",
            "Hành động này sẽ dọn dẹp các keyframe thừa có giá trị bằng nhau liên tục trên đối tượng đang chọn (giữ lại key đầu/cuối của chuỗi phẳng).\nBạn có chắc chắn?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if res == QtWidgets.QMessageBox.No:
            return
            
        try:
            total_deleted = clean_redundant_keys.clean_redundant_keys(objects=sel)
            if total_deleted > 0:
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    "Đã dọn dẹp thành công %d keyframe thừa có giá trị bằng nhau!" % total_deleted
                )
            else:
                QtWidgets.QMessageBox.information(
                    self, "Thông tin", 
                    "Không tìm thấy keyframe thừa nào có giá trị bằng nhau để dọn dẹp."
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi dọn dẹp keyframe: %s" % str(e)
            )

    def on_clean_neighborhood(self):
        """Xóa toàn bộ keyframe trong bán kính R xung quanh frame hiện tại (loại trừ frame hiện tại)"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng trên viewport!")
            return
            
        current_time = cmds.currentTime(q=True)
        
        sender = self.sender()
        if sender == getattr(self, 'fav_clean_neighbor_btn', None):
            r = self.fav_clean_radius_spin.value()
        else:
            if hasattr(self, 'clean_radius_spin'):
                r = self.clean_radius_spin.value()
            else:
                r = 3
        
        # Bọc trong undo chunk để hoàn tác dễ dàng
        cmds.undoInfo(openChunk=True, chunkName="AnimeowCleanNeighborhood")
        try:
            # Vùng trước: [current_time - r, current_time - 0.001]
            # Vùng sau: [current_time + 0.001, current_time + r]
            for obj in sel:
                # Xóa keyframe phía trước
                cmds.cutKey(obj, time=(current_time - r, current_time - 0.001))
                # Xóa keyframe phía sau
                cmds.cutKey(obj, time=(current_time + 0.001, current_time + r))
                
            # Ép refresh viewport
            cmds.refresh(force=True)
            print(u"[AnimeowTool] Đã dọn sạch keyframe lân cận bán kính %d tại frame %d." % (r, int(current_time)))
            cmds.warning("Đã dọn sạch keyframe lân cận bán kính %d tại frame %d." % (r, int(current_time)))
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi dọn dẹp keyframe lân cận: %s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_clean_subframe_keys(self):
        """Xóa sạch các keyframe lẻ bằng chỉ số index để tránh sai số float và đảm bảo dọn dẹp triệt để"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đối tượng trên viewport!")
            return
            
        # Quét lấy tất cả animCurves của đối tượng chọn
        curves = cmds.keyframe(sel, query=True, name=True) or []
        if not curves:
            cmds.warning("Không tìm thấy đường cong diễn hoạt nào trên các đối tượng được chọn.")
            return
            
        cmds.undoInfo(openChunk=True, chunkName="AnimeowCleanSubframeKeys")
        deleted_count = 0
        try:
            for curve in curves:
                times = cmds.keyframe(curve, query=True, timeChange=True) or []
                
                # Duyệt ngược từ cuối về đầu để khi xóa bằng index, chỉ số các key phía trước không bị thay đổi
                for i in range(len(times) - 1, -1, -1):
                    t = times[i]
                    # Nâng độ nhạy lên 1e-9 để bắt trọn mọi keyframe lệch cực nhỏ (như 93.0000001) tạo ra hoa thị * trên timeline
                    if abs(t - round(t)) > 1e-9:
                        cmds.cutKey(curve, index=(i, i))
                        deleted_count += 1
            
            if deleted_count > 0:
                cmds.refresh(force=True)
                print(u"[AnimeowTool] Đã dọn sạch %d keyframe lẻ (sub-frame keys) bằng chỉ số index." % deleted_count)
                cmds.warning("Đã dọn sạch %d keyframe lẻ (sub-frame keys) bằng chỉ số index." % deleted_count)
            else:
                cmds.warning("Không tìm thấy keyframe lẻ nào để dọn dẹp.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi dọn key lẻ", 
                "Lỗi xảy ra khi dọn dẹp keyframe lẻ:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_euler_filter(self):
        """Áp dụng Euler Filter cho các đường cong xoay được chọn hoặc các vật thể được chọn"""
        selected = cmds.ls(sl=True) or []
        selected_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        
        # Bọc trong undo chunk để hoàn tác dễ dàng
        cmds.undoInfo(openChunk=True)
        try:
            if selected_curves:
                cmds.filterCurve(selected_curves)
                cmds.warning("Đã áp dụng Euler Filter cho các đường cong được chọn trong Graph Editor.")
            elif selected:
                # Tìm toàn bộ curve keyframe của đối tượng chọn
                curves = cmds.keyframe(selected, query=True, name=True) or []
                # Lọc lấy các curve liên quan tới xoay (rotateX, rotateY, rotateZ, rx, ry, rz)
                rot_curves = [c for c in curves if any(r in c.lower() for r in ['rotate', 'rx', 'ry', 'rz'])]
                if rot_curves:
                    cmds.filterCurve(rot_curves)
                    cmds.warning("Đã áp dụng Euler Filter cho các kênh xoay của đối tượng được chọn.")
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Thông báo", 
                        "Không tìm thấy đường cong xoay (Rotation curves) nào trên vật thể được chọn để áp dụng Euler Filter!"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Cảnh báo", 
                    "Vui lòng chọn các đường cong xoay trong Graph Editor hoặc chọn đối tượng trong viewport!"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Euler Filter", 
                "Lỗi xảy ra khi thực hiện Euler Filter:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_smooth_btn_clicked(self):
        """Làm mượt nhanh 100% các keyframe được chọn (hoạt động như nút bấm cũ)"""
        curves = cmds.keyframe(q=True, name=True) or []
        if not curves:
            QtWidgets.QMessageBox.warning(
                self, "Cảnh báo",
                "Vui lòng chọn ít nhất 3 keyframe trong Graph Editor!"
            )
            return
            
        cmds.undoInfo(openChunk=True, chunkName="AnimeowSmoothButton")
        try:
            total_smoothed = 0
            for curve in curves:
                keys_time = cmds.keyframe(curve, q=True, selected=True, timeChange=True) or []
                keys_value = cmds.keyframe(curve, q=True, selected=True, valueChange=True) or []
                
                size = len(keys_time)
                if size < 3:
                    continue
                    
                # Tạo list chứa các giá trị mới
                new_values = list(keys_value)
                
                # Tính moving average cho các key ở giữa (bỏ qua key đầu và key cuối)
                for i in range(1, size - 1):
                    new_values[i] = (keys_value[i-1] + keys_value[i] + keys_value[i+1]) / 3.0
                    
                # Áp dụng 100% làm mượt lên các keyframe tương ứng
                for i in range(1, size - 1):
                    cmds.keyframe(
                        curve,
                        time=(keys_time[i], keys_time[i]),
                        absolute=True,
                        valueChange=new_values[i]
                    )
                    
                    # Cập nhật thuộc tính trực tiếp (nếu có kết nối) để viewport refresh tức thì
                    connected_plugs = cmds.listConnections(curve + '.output', plugs=True, destination=True) or []
                    for plug in connected_plugs:
                        try:
                            cmds.setAttr(plug, new_values[i])
                        except Exception:
                            pass
                            
                total_smoothed += 1
                
            if total_smoothed > 0:
                # Ép refresh viewport
                cmds.refresh(force=True)
                print(u"[SmoothKeys] Đã làm mượt thành công các keyframe được chọn.")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Thông báo",
                    "Cần chọn ít nhất 3 keyframe trên cùng một đường cong (curve) để làm mượt!"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi Làm mượt",
                "Lỗi xảy ra khi làm mượt keyframe:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_smooth_slider_pressed(self):
        """Khởi tạo cache giá trị gốc (0%) và giá trị mượt tối đa (100%) khi bắt đầu click slider"""
        cmds.undoInfo(openChunk=True, chunkName="AnimeowSmoothDrag")
        self._is_smoothing_drag = True
        self._smooth_cache = []
        
        # Quét các curves có keyframe được chọn trong Graph Editor
        curves = cmds.keyframe(q=True, name=True) or []
        if not curves:
            return
            
        for curve in curves:
            # Lấy các keyframe đang được chọn trên curve này
            keys_time = cmds.keyframe(curve, q=True, selected=True, timeChange=True) or []
            keys_value = cmds.keyframe(curve, q=True, selected=True, valueChange=True) or []
            
            size = len(keys_time)
            if size < 3:
                continue
                
            # Tính toán trước giá trị mượt tối đa 100% bằng thuật toán Moving Average
            # Bỏ qua key đầu và key cuối để bảo toàn biên độ của chuyển động ở 2 đầu
            for i in range(1, size - 1):
                val_goc = keys_value[i]
                val_smooth = (keys_value[i-1] + keys_value[i] + keys_value[i+1]) / 3.0
                
                # Tìm thuộc tính đối tượng được kết nối để gán setAttr trực tiếp (nếu có)
                connected_plugs = cmds.listConnections(curve + '.output', plugs=True, destination=True) or []
                
                self._smooth_cache.append({
                    'curve': curve,
                    'time': keys_time[i],
                    'val_goc': val_goc,
                    'val_smooth': val_smooth,
                    'plugs': connected_plugs
                })

    def on_smooth_slider_changed(self, val):
        """Nội suy trực tiếp cường độ làm mịn theo giá trị slider kéo"""
        sender = self.sender()
        if sender == getattr(self, 'fav_smooth_slider', None):
            lbl = self.fav_smooth_pct_label
        else:
            lbl = getattr(self, 'smooth_pct_label', None)
            
        if lbl:
            lbl.setText("%d%%" % val)
        if getattr(self, '_is_smoothing_drag', False) and hasattr(self, '_smooth_cache'):
            pct = val / 100.0
            for item in self._smooth_cache:
                curve = item['curve']
                time = item['time']
                val_goc = item['val_goc']
                val_smooth = item['val_smooth']
                
                # Nội suy LERP cường độ mượt giữa gốc (0%) và mượt hoàn toàn (100%)
                val_new = val_goc + (val_smooth - val_goc) * pct
                
                # Cập nhật keyframe trên curve
                cmds.keyframe(curve, time=(time, time), absolute=True, valueChange=val_new)
                
                # Ép gán giá trị thuộc tính trực tiếp để cập nhật viewport lập tức
                for plug in item['plugs']:
                    try:
                        cmds.setAttr(plug, val_new)
                    except Exception:
                        pass
                        
            # Ép refresh viewport
            cmds.refresh(force=True)

    def on_smooth_slider_released(self):
        """Đóng Undo chunk và reset slider về 0% để sẵn sàng cho lần kéo tiếp theo"""
        cmds.undoInfo(closeChunk=True)
        self._is_smoothing_drag = False
        
        sender = self.sender()
        if sender == getattr(self, 'fav_smooth_slider', None):
            sld = self.fav_smooth_slider
            lbl = self.fav_smooth_pct_label
        else:
            sld = getattr(self, 'smooth_slider', None)
            lbl = getattr(self, 'smooth_pct_label', None)
            
        # Block signals để set slider về 0% mà không kích hoạt lại thay đổi keyframe
        if sld:
            sld.blockSignals(True)
            sld.setValue(0)
            if lbl:
                lbl.setText("0%")
            sld.blockSignals(False)
        
        # In thông báo trạng thái
        if hasattr(self, '_smooth_cache') and self._smooth_cache:
            print(u"[SmoothSlider] Đã áp dụng làm mượt keyframe thành công.")
        self._smooth_cache = []

    def on_local_scale_tool(self):
        """Khởi chạy công cụ Scale Keyframe Cục Bộ (Local Scale Tool - MEL)"""
        import os
        import maya.mel as mel
        
        # Tìm đường dẫn tệp MEL trong package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mel_file = os.path.join(current_dir, "..", "mel", "NP_curveLocalScale.mel")
        mel_file = mel_file.replace("\\", "/")
        
        if os.path.exists(mel_file):
            try:
                mel.eval('source "%s";' % mel_file)
                print(u"[AnimeowTool] Đã khởi chạy Curve Local Scale Tool từ package.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Lỗi nạp script",
                    "Lỗi xảy ra khi chạy tệp script MEL:\n%s" % str(e)
                )
        else:
            # Fallback nếu không thấy file, thử chạy trực tiếp lệnh source
            try:
                mel.eval('source "NP_curveLocalScale.mel";')
                print(u"[AnimeowTool] Fallback: Đã nạp Curve Local Scale Tool từ MAYA_SCRIPT_PATH.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Lỗi tìm kiếm",
                    "Không tìm thấy tệp NP_curveLocalScale.mel đi kèm package cũng như trong đường dẫn Maya!\nLỗi: %s" % str(e)
                )

    def on_overlapper_execute(self):
        """Khởi chạy công cụ Overlapper chuyển động trễ"""
        self.save_settings()
        
        cmds.undoInfo(openChunk=True, chunkName="AnimeowOverlapper")
        try:
            from ..core import overlapper
            success, msg = overlapper.execute_overlapper(
                softness=self.ov_softness_spin.value(),
                scale=self.ov_scale_spin.value(),
                wind_enabled=self.ov_wind_cb.isChecked(),
                wind_scale=self.ov_wind_scale_spin.value(),
                wind_speed=self.ov_wind_speed_spin.value(),
                first_ctrl_skip=self.ov_skip_first_cb.isChecked(),
                translate_mode=self.ov_translate_cb.isChecked(),
                hierarchy_mode=self.ov_hierarchy_cb.isChecked(),
                cycle_mode=self.ov_cycle_cb.isChecked(),
                bake_on_layer=self.ov_bake_layer_cb.isChecked(),
                adaptive_scale=self.ov_adaptive_scale_cb.isChecked(),
                create_sel_set=self.ov_sel_set_cb.isChecked()
            )
            if success:
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi thực thi",
                "Lỗi xảy ra khi chạy Overlapper:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)
            
    def on_overlapper_cleanup(self):
        """Dọn dẹp các joint và locator nháp của Overlapper"""
        try:
            from ..core import overlapper
            overlapper.clean_up()
            cmds.warning("Đã dọn dẹp sạch sẽ các đối tượng tạm của Overlapper.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi dọn dẹp",
                "Lỗi xảy ra khi dọn dẹp Overlapper:\n%s" % str(e)
            )

    def on_add_inbetween(self):
        """Thêm N frame trống (Inbetween) tại vị trí time slider hiện tại cho các đối tượng đang chọn"""
        import maya.mel as mel
        
        sender = self.sender()
        if sender == getattr(self, 'fav_add_ib_btn', None):
            n = self.fav_ib_count_spin.value()
        else:
            n = self.ib_count_spin.value()
        
        cmds.undoInfo(openChunk=True, chunkName="AnimeowAddInbetween")
        try:
            for _ in range(n):
                mel.eval("timeSliderEditKeys addInbetween;")
            print(u"[AnimeowTool] Đã thêm thành công %d Inbetweens tại frame %d." % (n, int(cmds.currentTime(q=True))))
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi",
                "Lỗi xảy ra khi thêm Inbetween:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_remove_inbetween(self):
        """Bớt N frame trống (Inbetween) tại vị trí time slider hiện tại cho các đối tượng đang chọn"""
        import maya.mel as mel
        
        sender = self.sender()
        if sender == getattr(self, 'fav_remove_ib_btn', None):
            n = self.fav_ib_count_spin.value()
        else:
            n = self.ib_count_spin.value()
        
        cmds.undoInfo(openChunk=True, chunkName="AnimeowRemoveInbetween")
        try:
            for _ in range(n):
                mel.eval("timeSliderEditKeys removeInbetween;")
            print(u"[AnimeowTool] Đã xóa thành công %d Inbetweens tại frame %d." % (n, int(cmds.currentTime(q=True))))
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi",
                "Lỗi xảy ra khi xóa Inbetween:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_fix_lost_shader(self):
        """Mở khóa default shading group và texture list để sửa lỗi mất shader (lưới xanh lá)"""
        try:
            shelf.fix_lost_shader()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Không thể mở khóa các node mặc định:\n%s" % str(e)
            )
    def on_change_rotate_order(self):
        """Thay đổi Rotate Order bảo toàn keyframe"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một vật thể!")
            return
            
        new_order = self.so_order_combo.currentText()
        
        # Chạy trong một undo chunk của Maya
        cmds.undoInfo(openChunk=True, chunkName="ChangeRotateOrder")
        try:
            success_count = 0
            for obj in sel:
                success, msg = space_order_tool.change_rotate_order(obj, new_order)
                if success:
                    success_count += 1
                    print("[SpaceOrder] %s: %s" % (obj, msg))
                    
            if success_count > 0:
                cmds.warning("Đã đổi Rotate Order sang %s cho %d vật thể thành công!" % (new_order, success_count))
            else:
                QtWidgets.QMessageBox.warning(self, "Thất bại", "Không thể thay đổi Rotate Order của các vật thể được chọn.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi thay đổi Rotate Order:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)
    def on_record_world_space(self):
        """Ghi tọa độ thế giới sang locator"""
        sel = cmds.ls(sl=True) or []
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn 1 vật thể muốn ghi nhận Space thế giới!")
            return
            
        # Ta chỉ ghi nhận cho vật thể đầu tiên được chọn
        obj = sel[0]
        cmds.undoInfo(openChunk=True, chunkName="RecordWorldSpace")
        try:
            loc, msg = space_order_tool.record_world_space(obj)
            if loc:
                cmds.warning(msg)
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    "Đã ghi nhận chuyển động sang Locator thế giới:\n%s\n\nBây giờ bạn có thể thay đổi Parent, Space hoặc cấu trúc của vật thể tùy ý, sau đó chọn vật thể và Locator để bấm Khôi phục (Restore)." % loc
                )
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi ghi Space thế giới:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)
            
    def on_restore_world_space(self):
        """Khôi phục tọa độ thế giới từ locator"""
        sel = cmds.ls(sl=True) or []
        if len(sel) < 2:
            # Thử tự động quét xem có locator record nào liên kết với vật thể được chọn không
            if len(sel) == 1:
                obj = sel[0]
                clean_name = obj.replace(":", "_").replace("|", "_")
                possible_loc = "animeow_space_record_%s" % clean_name
                if cmds.objExists(possible_loc):
                    sel = [obj, possible_loc]
                    
            if len(sel) < 2:
                QtWidgets.QMessageBox.warning(
                    self, "Cảnh báo", 
                    "Vui lòng chọn vật thể gốc và Locator lưu trữ (animeow_space_record_...) để khôi phục!"
                )
                return
                
        # Phân biệt đối tượng và locator
        obj = None
        locator = None
        for item in sel:
            if "animeow_space_record_" in item:
                locator = item
            else:
                obj = item
                
        if not obj or not locator:
            QtWidgets.QMessageBox.warning(
                self, "Cảnh báo", 
                "Không tìm thấy đúng cặp vật thể gốc và Locator lưu trữ trong vùng chọn!"
            )
            return
            
        cmds.undoInfo(openChunk=True, chunkName="RestoreWorldSpace")
        try:
            success, msg = space_order_tool.restore_world_space(obj, locator)
            if success:
                cmds.warning(msg)
            else:
                QtWidgets.QMessageBox.warning(self, "Cảnh báo", msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                "Lỗi xảy ra khi khôi phục Space thế giới:\n%s" % str(e)
            )
        finally:
            cmds.undoInfo(closeChunk=True)

    def get_qc_options(self):
        mo = self.qc_mo_cb.isChecked()
        
        # Lấy các trục Translate bỏ qua (skip)
        skipped_t = []
        if not self.qc_tx_cb.isChecked():
            skipped_t.append("x")
        if not self.qc_ty_cb.isChecked():
            skipped_t.append("y")
        if not self.qc_tz_cb.isChecked():
            skipped_t.append("z")
        skip_t = skipped_t if skipped_t else "none"
        
        # Lấy các trục Rotate bỏ qua (skip)
        skipped_r = []
        if not self.qc_rx_cb.isChecked():
            skipped_r.append("x")
        if not self.qc_ry_cb.isChecked():
            skipped_r.append("y")
        if not self.qc_rz_cb.isChecked():
            skipped_r.append("z")
        skip_r = skipped_r if skipped_r else "none"
        
        return mo, skip_t, skip_r

    def on_qc_parent(self):
        from ..core import shelf
        mo, skip_t, skip_r = self.get_qc_options()
        shelf.create_parent_constraint(mo=mo, skip_translate=skip_t, skip_rotate=skip_r)
        
    def on_qc_point(self):
        from ..core import shelf
        mo, skip_t, _ = self.get_qc_options()
        shelf.create_point_constraint(mo=mo, skip_axes=skip_t)
        
    def on_qc_orient(self):
        from ..core import shelf
        mo, _, skip_r = self.get_qc_options()
        shelf.create_orient_constraint(mo=mo, skip_axes=skip_r)
        
    def on_qc_scale(self):
        from ..core import shelf
        mo, skip_t, _ = self.get_qc_options()
        shelf.create_scale_constraint(mo=mo, skip_axes=skip_t)
        
    def on_qc_delete(self):
        from ..core import shelf
        shelf.delete_obj_constraints()

    # ── Tween Machine (Live Slider) ──

    def on_tween_slider_pressed(self):
        """Khởi tạo cache giá trị LERP gốc và mở Undo chunk của Maya khi bắt đầu click slider"""
        cmds.undoInfo(openChunk=True, chunkName="AnimeowTweenDrag")
        self._is_tweening_drag = True
        self._tween_cache = []
        
        sel = cmds.ls(sl=True) or []
        if not sel:
            return
            
        current_time = cmds.currentTime(query=True)
        
        for obj in sel:
            # Lấy trực tiếp toàn bộ animCurves của đối tượng này
            anim_curves = cmds.keyframe(obj, query=True, name=True) or []
            
            # Tìm các thuộc tính (plugs) được kết nối từ các animCurves
            attrs = []
            for curve in anim_curves:
                plugs = cmds.listConnections(curve + '.output', plugs=True, destination=True) or []
                for plug in plugs:
                    if plug.startswith(obj + '.'):
                        attrs.append(plug)
            attrs = list(set(attrs))
            
            for full_attr in attrs:
                # Lấy giá trị hiện tại làm fallback mặc định
                current_val = cmds.getAttr(full_attr)
                
                # Tìm keyframe trước
                prev_time = cmds.findKeyframe(
                    full_attr, 
                    time=(current_time, current_time), 
                    which='previous'
                )
                prev_val = current_val
                if prev_time is not None and abs(prev_time - current_time) > 0.001:
                    prev_vals = cmds.keyframe(
                        full_attr, query=True,
                        time=(prev_time, prev_time),
                        valueChange=True
                    )
                    if prev_vals:
                        prev_val = prev_vals[0]
                
                # Tìm keyframe sau
                next_time = cmds.findKeyframe(
                    full_attr, 
                    time=(current_time, current_time), 
                    which='next'
                )
                next_val = current_val
                if next_time is not None and abs(next_time - current_time) > 0.001:
                    next_vals = cmds.keyframe(
                        full_attr, query=True,
                        time=(next_time, next_time),
                        valueChange=True
                    )
                    if next_vals:
                        next_val = next_vals[0]
                
                # Lưu vào cache để nội suy cực nhanh trong lúc kéo slider
                self._tween_cache.append({
                    'attr': full_attr,
                    'current_time': current_time,
                    'prev_val': prev_val,
                    'next_val': next_val
                })

    def on_tween_slider_changed(self, val):
        """Nội suy trực tiếp từ cache và hiển thị ngay trên viewport khi kéo slider"""
        sender = self.sender()
        if sender == getattr(self, 'fav_tween_slider', None):
            lbl = self.fav_tween_pct_label
        else:
            lbl = getattr(self, 'tween_pct_label', None)
            
        if lbl:
            lbl.setText("%d%%" % val)
        if getattr(self, '_is_tweening_drag', False) and hasattr(self, '_tween_cache'):
            pct = val / 100.0
            for item in self._tween_cache:
                full_attr = item['attr']
                prev_val = item['prev_val']
                next_val = item['next_val']
                current_time = item['current_time']
                
                # Tính giá trị LERP từ mốc ban đầu cố định
                tweened_val = prev_val + (next_val - prev_val) * pct
                
                # Gán trực tiếp vào thuộc tính để viewport làm tươi tức thì
                try:
                    cmds.setAttr(full_attr, tweened_val)
                except Exception:
                    pass
                
                # Cập nhật keyframe
                cmds.setKeyframe(full_attr, time=current_time, value=tweened_val)
                
            # Ép Maya refresh viewport ngay lập tức để cập nhật tư thế trực quan
            cmds.refresh(force=True)

    def on_tween_slider_released(self):
        """Đóng Undo chunk và giải phóng cache khi animator thả chuột ra"""
        cmds.undoInfo(closeChunk=True)
        self._is_tweening_drag = False
        self._tween_cache = []
        
        sender = self.sender()
        if sender == getattr(self, 'fav_tween_slider', None):
            sld = self.fav_tween_slider
            lbl = self.fav_tween_pct_label
        else:
            sld = getattr(self, 'tween_slider', None)
            lbl = getattr(self, 'tween_pct_label', None)
            
        # Reset slider về lại 50%
        if sld:
            sld.blockSignals(True)
            sld.setValue(50)
            if lbl:
                lbl.setText("50%")
            sld.blockSignals(False)
            
            val = sld.value()
            curr_time = cmds.currentTime(query=True)
            print(u"[TweenMachine] Đã áp dụng Tween %.0f%% tại frame %d." % (val, int(curr_time)))

    def on_tween_preset(self, pct):
        """Đặt slider về preset % và tự động áp dụng trực tiếp"""
        # Đồng bộ set giá trị cho cả slider chính và phụ nếu chúng tồn tại
        for sld, lbl in [
            (getattr(self, 'tween_slider', None), getattr(self, 'tween_pct_label', None)),
            (getattr(self, 'fav_tween_slider', None), getattr(self, 'fav_tween_pct_label', None))
        ]:
            if sld and lbl:
                sld.blockSignals(True)
                sld.setValue(pct)
                lbl.setText("%d%%" % pct)
                sld.blockSignals(False)
        
        success, msg = tween_machine.tween_interactive(pct / 100.0)
        if success:
            cmds.refresh(force=True) # Ép refresh viewport
            cmds.inViewMessage(
                amg='<span style="color:#00BCD4;">%s</span>' % msg,
                pos='botCenter', fade=True
            )
        else:
            cmds.warning(msg)


def is_ui_alive(ui_obj):
    """Kiểm tra xem đối tượng Qt UI còn sống ở phía C++ không để tránh lỗi pointer chết"""
    if ui_obj is None:
        return False
    try:
        ui_obj.objectName()
        return True
    except RuntimeError:
        return False


def show_window(tab_index=None, standalone_tab=None):
    import sys
    
    # Xác định key lưu instance trong sys, tên control và tiêu đề cửa sổ
    if standalone_tab is None:
        sys_key = "_animeow_maya_toolboard_ui"
        ctrl_name = AnimeowMayaToolboardUI.WORKSPACE_CONTROL_NAME
        win_title = AnimeowMayaToolboardUI.WINDOW_TITLE
    else:
        sys_key = "_animeow_standalone_%s_ui" % str(standalone_tab)
        if standalone_tab == 0 or standalone_tab == "smart_link":
            ctrl_name = "AnimeowSmartLinkWorkspaceControl"
            win_title = "Constraint & Smart Link"
        elif standalone_tab == "world_bake":
            ctrl_name = "AnimeowWorldBakeWorkspaceControl"
            win_title = "Smart World Bake & Pivot"
        elif standalone_tab == 1:
            ctrl_name = "AnimeowCurveWorkspaceControl"
            win_title = "Curve & Motion"
        elif standalone_tab == 2:
            ctrl_name = "AnimeowRigWorkspaceControl"
            win_title = "Rig & Mirror"
        elif standalone_tab == 3:
            ctrl_name = "AnimeowOutputWorkspaceControl"
            win_title = "Output & Scene"
        elif standalone_tab == "arc_tracker":
            ctrl_name = "AnimeowArcWorkspaceControl"
            win_title = "Arc Tracker"
        elif standalone_tab == "overlapper":
            ctrl_name = "AnimeowOverlapperWorkspaceControl"
            win_title = "Overlapper"
        elif standalone_tab == "round_tool":
            ctrl_name = "AnimeowRoundWorkspaceControl"
            win_title = "Làm tròn số"
        elif standalone_tab == "fav_tools":
            ctrl_name = "AnimeowFavoriteToolsWorkspaceControl"
            win_title = "Favorite Tools"
        elif standalone_tab == "view_layer":
            ctrl_name = "AnimeowViewLayerWorkspaceControl"
            win_title = "Animeow View Layer"
        else:
            ctrl_name = "AnimeowGenericWorkspaceControl"
            win_title = "Animeow Tool"
            
    # 1. Đóng và giải phóng widget cũ (nếu có)
    old_ui = getattr(sys, sys_key, None)
    if is_ui_alive(old_ui):
        try:
            old_ui.close()
            old_ui.deleteLater()
        except Exception:
            pass
        setattr(sys, sys_key, None)

    # 2. Xóa các workspaceControl cũ và dọn dẹp các control rác từ các bản build lỗi trước đó
    for name in [ctrl_name, ctrl_name + "WorkspaceControl"]:
        if cmds.workspaceControl(name, exists=True):
            try:
                cmds.deleteUI(name)
            except Exception:
                pass
            
    # 3. Tạo instance mới
    ui_instance = AnimeowMayaToolboardUI(standalone_tab=standalone_tab)
    setattr(sys, sys_key, ui_instance)
    
    # Thiết lập objectName (không bao gồm hậu tố WorkspaceControl) để Maya tự động ghép thêm hậu tố này
    # tạo thành đúng tên Workspace Control khớp với ctrl_name
    obj_name = ctrl_name.replace("WorkspaceControl", "")
    ui_instance.setObjectName(obj_name)
    
    # 4. Kiểm tra xem người dùng đã từng có tùy biến vị trí (windowPref) được lưu cho workspace control này chưa
    pref_exists = False
    try:
        pref_exists = cmds.windowPref(ctrl_name, exists=True)
    except Exception:
        pass
        
    # 5. Hiển thị dưới dạng dockable panel
    if pref_exists:
        # Nếu đã có tùy chỉnh vị trí trước đó, để Maya tự động tải cấu hình cũ
        ui_instance.show(dockable=True)
    else:
        # Nếu là lần đầu chạy tool, áp dụng docking mặc định
        # Đối với các cửa sổ standalone nhỏ, ta để mặc định floating=True để làm nổi tiện sắp xếp
        is_floating = True if standalone_tab is not None else False
        show_kwargs = {
            "dockable": True,
            "area": "right",
            "floating": is_floating,
            "allowedArea": "left|right"
        }
        if standalone_tab == "quick_const":
            show_kwargs["width"] = 180
            show_kwargs["height"] = 200
        elif standalone_tab == "fav_tools":
            show_kwargs["width"] = 250
            show_kwargs["height"] = 300
        ui_instance.show(**show_kwargs)
    
    # 6. Cập nhật tiêu đề hiển thị cho tab trong Maya
    if cmds.workspaceControl(ctrl_name, exists=True):
        edit_kwargs = {
            "edit": True,
            "label": win_title
        }
        if standalone_tab == "quick_const":
            edit_kwargs["minimumWidth"] = 180
            edit_kwargs["initialWidth"] = 180
        elif standalone_tab == "fav_tools":
            edit_kwargs["minimumWidth"] = 250
            edit_kwargs["initialWidth"] = 250
        cmds.workspaceControl(ctrl_name, **edit_kwargs)
        
    if tab_index is not None and is_ui_alive(ui_instance) and standalone_tab is None:
        try:
            ui_instance.tab_widget.setCurrentIndex(tab_index)
        except Exception:
            pass
            
    return ui_instance
