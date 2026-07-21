from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

# Get directory - use sys._animo_tools_path set by launcher, fallback to __file__
def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size
get_dpi_scale = dpi_utils.get_dpi_scale

class AnimoTooltip(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(AnimoTooltip, self).__init__(parent)
        
        self.setWindowFlags(
            QtCore.Qt.ToolTip |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        
        self._movie = None
        self._hide_timer = QtCore.QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_tooltip)
        self._hide_delay = 4000
        self._mouse_inside = False
        self._mouse_over_button = False
        self._trigger_button = None
        self._dpi_scale = get_dpi_scale()
        self._source_widget = None
        
        self._distance_check_timer = QtCore.QTimer(self)
        self._distance_check_timer.timeout.connect(self._check_mouse_distance)
        self._distance_check_timer.setInterval(100)
        
        self._setup_ui()
        self._apply_style()
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.applicationStateChanged.connect(self._on_app_state_changed)

    def _on_app_state_changed(self, state):
        if state != QtCore.Qt.ApplicationActive:
            self.hide_tooltip()

    def set_source_widget(self, widget):
        self._source_widget = widget

    def _check_mouse_distance(self):
        if not self.isVisible():
            self._distance_check_timer.stop()
            return
        
        cursor_pos = QtGui.QCursor.pos()
        tooltip_rect = self.geometry()
        
        margin = 50
        expanded_rect = tooltip_rect.adjusted(-margin, -margin, margin, margin)
        
        if self._source_widget:
            try:
                source_rect = QtCore.QRect(
                    self._source_widget.mapToGlobal(QtCore.QPoint(0, 0)),
                    self._source_widget.size()
                )
                expanded_rect = expanded_rect.united(source_rect)
            except RuntimeError:
                pass
        
        if self._trigger_button:
            try:
                button_rect = QtCore.QRect(
                    self._trigger_button.mapToGlobal(QtCore.QPoint(0, 0)),
                    self._trigger_button.size()
                )
                expanded_rect = expanded_rect.united(button_rect)
            except RuntimeError:
                pass
        
        if not expanded_rect.contains(cursor_pos):
            self.hide_tooltip()

    def set_trigger_button(self, button):
        self._trigger_button = button
        if button:
            button.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self._trigger_button:
            if event.type() == QtCore.QEvent.Enter:
                self._mouse_over_button = True
                self._hide_timer.stop()
            elif event.type() == QtCore.QEvent.Leave:
                self._mouse_over_button = False
                if not self._mouse_inside:
                    self._hide_timer.start(self._hide_delay)
        return super(AnimoTooltip, self).eventFilter(obj, event)

    def enterEvent(self, event):
        self._mouse_inside = True
        self._hide_timer.stop()
        super(AnimoTooltip, self).enterEvent(event)

    def leaveEvent(self, event):
        self._mouse_inside = False
        if not self._mouse_over_button:
            self._hide_timer.start(self._hide_delay)
        super(AnimoTooltip, self).leaveEvent(event)

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("tooltipContainer")
        self.main_layout.addWidget(self.container)
        
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(
            scale_size(12), scale_size(10), scale_size(12), scale_size(10)
        )
        self.container_layout.setSpacing(0)
        
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(scale_size(10))
        
        icon_size = scale_size(28)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(icon_size, icon_size)
        self.icon_label.setObjectName("iconLabel")
        self.icon_label.hide()
        self.header_layout.addWidget(self.icon_label)
        
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("titleLabel")
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        self.shortcut_label = QtWidgets.QLabel()
        self.shortcut_label.setObjectName("shortcutLabel")
        self.header_layout.addWidget(self.shortcut_label)
        
        self.container_layout.addLayout(self.header_layout)
        
        self.separator1 = QtWidgets.QFrame()
        self.separator1.setFixedHeight(1)
        self.separator1.setObjectName("separator")
        self.container_layout.addWidget(self.separator1)
        
        self.description_label = QtWidgets.QLabel()
        self.description_label.setObjectName("descriptionLabel")
        self.description_label.setWordWrap(True)
        self.container_layout.addWidget(self.description_label)
        
        self.gif_label = QtWidgets.QLabel()
        self.gif_label.setObjectName("gifLabel")
        self.gif_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gif_label.hide()
        self.container_layout.addWidget(self.gif_label)
        
        self.info_frame = QtWidgets.QFrame()
        self.info_frame.setObjectName("infoFrame")
        self.info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(scale_size(2))
        self.container_layout.addWidget(self.info_frame)

    def _apply_style(self):
        title_font = scale_font_size(14)
        shortcut_font = scale_font_size(12)
        desc_font = scale_font_size(11)
        info_font = scale_font_size(11)
        border_radius = scale_size(5)
        top_padding = scale_size(6)
        
        style = """
            QFrame#tooltipContainer {{
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
            }}
            QLabel#iconLabel {{
                background: transparent;
            }}
            QLabel#titleLabel {{
                color: #4aa3df;
                font-size: {title_font}px;
                font-weight: bold;
                background: transparent;
            }}
            QLabel#shortcutLabel {{
                color: #888888;
                font-size: {shortcut_font}px;
                background: transparent;
            }}
            QLabel#descriptionLabel {{
                color: #b0b0b0;
                font-size: {desc_font}px;
                background: transparent;
                padding-top: {top_padding}px;
                padding-bottom: 2px;
            }}
            QFrame#separator {{
                background-color: #555555;
                border: none;
            }}
            QLabel#gifLabel {{
                background: transparent;
                padding-top: {top_padding}px;
            }}
            QFrame#infoFrame {{
                background: transparent;
            }}
        """.format(
            border_radius=border_radius,
            title_font=title_font,
            shortcut_font=shortcut_font,
            desc_font=desc_font,
            top_padding=top_padding
        )
        self.setStyleSheet(style)
        self._info_font_size = info_font

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def set_content(self, title="", description="", gif_path="", 
                    info_lines=None, shortcut="", icon_pixmap=None):
        
        self.title_label.setText(title)
        self.title_label.setVisible(bool(title))
        
        self.shortcut_label.setText(shortcut)
        self.shortcut_label.setVisible(bool(shortcut))
        
        icon_size = scale_size(28)
        if icon_pixmap and not icon_pixmap.isNull():
            self.icon_label.setPixmap(icon_pixmap.scaled(
                icon_size, icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            ))
            self.icon_label.show()
        else:
            self.icon_label.hide()
        
        self.description_label.setText(description)
        self.description_label.setVisible(bool(description))
        
        self.separator1.setVisible(bool(title) and bool(description or gif_path or info_lines))
        
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        if gif_path and os.path.exists(gif_path):
            self._movie = QtGui.QMovie(gif_path)
            self._movie.setCacheMode(QtGui.QMovie.CacheAll)
            
            self._movie.jumpToFrame(0)
            gif_size = self._movie.currentImage().size()
            gif_width = gif_size.width()
            gif_height = gif_size.height()
            
            if gif_width > 0 and gif_height > 0:
                self.gif_label.setFixedSize(gif_width, gif_height)
            
            self.gif_label.setMovie(self._movie)
            self._movie.start()
            self.gif_label.show()
        else:
            self.gif_label.clear()
            self.gif_label.hide()
        
        self._clear_layout(self.info_layout)
        
        if info_lines:
            spacer = QtWidgets.QWidget()
            spacer.setFixedHeight(scale_size(8))
            self.info_layout.addWidget(spacer)
            for line in info_lines:
                info_label = QtWidgets.QLabel("• " + line)
                info_label.setStyleSheet(
                    "color: #909090; font-size: {0}px; background: transparent;".format(
                        self._info_font_size
                    )
                )
                self.info_layout.addWidget(info_label)
            self.info_frame.show()
        else:
            self.info_frame.hide()
        
        self.adjustSize()

    def show_at_widget(self, widget):
        widget_pos = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        
        screen = QtWidgets.QApplication.screenAt(widget_pos)
        if screen:
            screen_geo = screen.availableGeometry()
        else:
            screen_geo = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        x = widget_pos.x()
        y = widget_pos.y() + scale_size(5)
        
        if x + self.width() > screen_geo.right():
            x = screen_geo.right() - self.width() - scale_size(10)
        
        if y + self.height() > screen_geo.bottom():
            y = widget.mapToGlobal(QtCore.QPoint(0, 0)).y() - self.height() - scale_size(5)
        
        self.move(x, y)
        self.show()
        self.raise_()
        self._hide_timer.start(self._hide_delay)
        self._distance_check_timer.start()
    
    def show_at_cursor(self, offset_x=15, offset_y=15):
        cursor_pos = QtGui.QCursor.pos()
        
        screen = QtWidgets.QApplication.screenAt(cursor_pos)
        if screen:
            screen_geo = screen.availableGeometry()
        else:
            screen_geo = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        x = cursor_pos.x() + scale_size(offset_x)
        y = cursor_pos.y() + scale_size(offset_y)
        
        if x + self.width() > screen_geo.right():
            x = cursor_pos.x() - self.width() - scale_size(offset_x)
        
        if y + self.height() > screen_geo.bottom():
            y = cursor_pos.y() - self.height() - scale_size(offset_y)
        
        self.move(x, y)
        self.show()
        self.raise_()
        self._hide_timer.start(self._hide_delay)
        self._distance_check_timer.start()

    def hide_tooltip(self):
        self._hide_timer.stop()
        self._distance_check_timer.stop()
        if self._movie:
            self._movie.stop()
        self.hide()
        self.deleteLater()

