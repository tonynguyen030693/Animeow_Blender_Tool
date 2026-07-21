"""
Tooltip Manager for Animo Launcher
Handles tooltip display with hover delay, GIF loading, and positioning
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

import compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

from tooltip_widget import AnimoTooltip
from tooltip_data import get_tooltip_data


class TooltipEventFilter(QtCore.QObject):
    """Event filter that tracks hover time and triggers tooltip display"""
    
    def __init__(self, manager):
        super(TooltipEventFilter, self).__init__()
        self._manager = manager
        self._hover_timer = QtCore.QTimer()
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._on_hover_timeout)
        self._default_delay = 500  # 0.5 seconds
        self._current_widget = None
        self._widget_delays = {}  # Custom delays per widget
    
    def set_widget_delay(self, widget, delay_ms):
        """Set a custom hover delay for a specific widget"""
        self._widget_delays[widget] = delay_ms
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self._current_widget = obj
            # Use custom delay if set, otherwise default
            delay = self._widget_delays.get(obj, self._default_delay)
            self._hover_timer.start(delay)
        elif event.type() == QtCore.QEvent.Leave:
            self._hover_timer.stop()
            self._current_widget = None
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            self._hover_timer.stop()
            self._manager.hide_current_tooltip()
        
        return False
    
    def _on_hover_timeout(self):
        if self._current_widget:
            self._manager.show_tooltip_for_widget(self._current_widget)


class TooltipManager(QtCore.QObject):
    """Manages tooltip display for Animo Launcher buttons"""
    
    def __init__(self, animo_data_path):
        super(TooltipManager, self).__init__()
        
        self._animo_data_path = animo_data_path
        self._gif_folder = os.path.join(animo_data_path, "Animo_Tools_Tip", "gif")
        self._icons_path = os.path.join(animo_data_path, "icons")
        
        self._event_filter = TooltipEventFilter(self)
        self._current_tooltip = None
        self._widget_data = {}  # Maps widget to (launcher_name, icon_path)
        self._enabled = True  # Tooltips enabled by default
    
    def set_enabled(self, enabled):
        """Enable or disable tooltip display"""
        self._enabled = enabled
        if not enabled:
            self.hide_current_tooltip()
    
    def is_enabled(self):
        """Check if tooltips are enabled"""
        return self._enabled
    
    def register_button(self, widget, launcher_name, icon_path=None, hover_delay=None):
        """
        Register a button to show tooltip on hover
        
        Args:
            widget: QPushButton or similar widget
            launcher_name: Name used to look up tooltip data
            icon_path: Optional path to icon image
            hover_delay: Optional custom hover delay in milliseconds (default 500ms)
        """
        widget.installEventFilter(self._event_filter)
        self._widget_data[widget] = (launcher_name, icon_path)
        
        # Set custom delay if provided
        if hover_delay is not None:
            self._event_filter.set_widget_delay(widget, hover_delay)
        
        # Disable native tooltip if we're handling it
        widget.setToolTip("")
    
    def unregister_button(self, widget):
        """Remove tooltip handling from a button"""
        widget.removeEventFilter(self._event_filter)
        if widget in self._widget_data:
            del self._widget_data[widget]
    
    def show_tooltip_for_widget(self, widget):
        """Display tooltip for the specified widget"""
        if not self._enabled:
            return
        
        if widget not in self._widget_data:
            return
        
        # Hide any existing tooltip
        self.hide_current_tooltip()
        
        launcher_name, icon_path = self._widget_data[widget]
        data = get_tooltip_data(launcher_name)
        
        # Get GIF paths (main + numbered variants)
        gif_name = data.get("gif", "")
        gif_paths = []
        if gif_name:
            main_gif = os.path.join(self._gif_folder, gif_name + ".gif")
            if os.path.exists(main_gif):
                gif_paths.append(main_gif)
            
            for i in range(1, 100):
                numbered_gif = os.path.join(self._gif_folder, gif_name + str(i) + ".gif")
                if os.path.exists(numbered_gif):
                    gif_paths.append(numbered_gif)
        
        # Get icon pixmap
        icon_pixmap = None
        if icon_path and os.path.exists(icon_path):
            icon_pixmap = QtGui.QPixmap(icon_path)
        
        # Create and configure tooltip
        self._current_tooltip = AnimoTooltip()
        self._current_tooltip.set_source_widget(widget)
        self._current_tooltip.set_trigger_button(widget)
        
        self._current_tooltip.set_content(
            title=data.get("title", ""),
            description=data.get("description", ""),
            gif_paths=gif_paths,
            info_lines=data.get("info_lines", []),
            shortcut=data.get("shortcut", ""),
            icon_pixmap=icon_pixmap,
            title_color=data.get("title_color", "#4aa3df")
        )
        
        # Show at widget position
        self._current_tooltip.show_at_widget(widget)
    
    def hide_current_tooltip(self):
        """Hide and clean up the current tooltip"""
        if self._current_tooltip:
            try:
                self._current_tooltip.hide_tooltip()
            except RuntimeError:
                pass  # Widget already deleted
            self._current_tooltip = None
    
    def set_hover_delay(self, milliseconds):
        """Set the hover delay before tooltip appears"""
        self._event_filter._hover_delay = milliseconds


# Global manager instance (will be set by Animo_Launcher)
_tooltip_manager = None


def get_tooltip_manager():
    """Get the global tooltip manager instance"""
    return _tooltip_manager


def init_tooltip_manager(animo_data_path):
    """Initialize the global tooltip manager"""
    global _tooltip_manager
    _tooltip_manager = TooltipManager(animo_data_path)
    return _tooltip_manager
