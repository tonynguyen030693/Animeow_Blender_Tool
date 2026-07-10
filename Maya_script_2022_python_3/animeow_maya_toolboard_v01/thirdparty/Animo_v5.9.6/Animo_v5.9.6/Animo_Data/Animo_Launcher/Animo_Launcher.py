import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as mui

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
    QAction = QtWidgets.QAction  # PySide2: QAction is in QtWidgets
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
    QAction = QtGui.QAction  # PySide6: QAction moved to QtGui

import os
import sys
import importlib
import json
import platform

IS_MAC = platform.system() == "Darwin"


def get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


def get_prefs_path():
    """Get the path to the Animo preferences folder"""
    animo_data = get_animo_data_path()
    prefs_dir = os.path.join(animo_data, "Animo_Prefs")
    # Create the folder if it doesn't exist
    if not os.path.exists(prefs_dir):
        try:
            os.makedirs(prefs_dir)
        except:
            pass
    return prefs_dir


def get_prefs_file():
    """Get the full path to the preferences JSON file"""
    return os.path.join(get_prefs_path(), "dock_mode.json")


def enable_usersetup_security():
    if not cmds.optionVar(exists='startupScriptIsEnabled'):
        cmds.optionVar(intValue=('startupScriptIsEnabled', 1))
    elif cmds.optionVar(query='startupScriptIsEnabled') == 0:
        cmds.optionVar(intValue=('startupScriptIsEnabled', 1))


ANIMO_DATA_PATH = get_animo_data_path()
ICONS_PATH = os.path.join(ANIMO_DATA_PATH, "Animo_Launcher")
MAYA_VERSION = int(cmds.about(version=True)[:4])

if ANIMO_DATA_PATH not in sys.path:
    sys.path.insert(0, ANIMO_DATA_PATH)

TOOLTIP_PATH = os.path.join(ANIMO_DATA_PATH, "Animo_Tools_Tip")
if TOOLTIP_PATH not in sys.path:
    sys.path.insert(0, TOOLTIP_PATH)

ANIMO_PREFS_PATH = os.path.join(ANIMO_DATA_PATH, "Animo_Prefs")

def _ensure_prefs_dir():
    """Ensure the prefs directory exists"""
    if not os.path.exists(ANIMO_PREFS_PATH):
        try:
            os.makedirs(ANIMO_PREFS_PATH)
        except OSError:
            pass

def _get_tooltip_pref():
    """Read tooltip preference from JSON file. Returns True if tooltips enabled (default)."""
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "tooltip_prefs.json")
    if os.path.exists(pref_file):
        try:
            with open(pref_file, 'r') as f:
                import json
                data = json.load(f)
                return data.get("tooltips_enabled", True)
        except:
            pass
    return True  # Default: tooltips enabled

def _set_tooltip_pref(enabled):
    """Save tooltip preference to JSON file."""
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "tooltip_prefs.json")
    try:
        import json
        with open(pref_file, 'w') as f:
            json.dump({"tooltips_enabled": enabled}, f, indent=2)
    except:
        pass


def _get_center_pivot_pref():
    """Read center pivot preference from JSON file. Returns False by default."""
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "center_pivot_prefs.json")
    if os.path.exists(pref_file):
        try:
            with open(pref_file, 'r') as f:
                import json
                data = json.load(f)
                return data.get("center_pivot_enabled", False)
        except:
            pass
    return False  # Default: disabled


def _set_center_pivot_pref(enabled):
    """Save center pivot preference to JSON file."""
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "center_pivot_prefs.json")
    try:
        import json
        with open(pref_file, 'w') as f:
            json.dump({"center_pivot_enabled": enabled}, f, indent=2)
    except:
        pass


def _is_center_pivot_active():
    """Check if center pivot mode is currently active by checking node or saved preference."""
    # First check if the node exists and mode is engaged
    try:
        if cmds.objExists("pivotAnchorDataHolder"):
            if cmds.getAttr("pivotAnchorDataHolder.modeEngaged"):
                return True
    except:
        pass
    # Fall back to saved preference (for startup before node is created)
    return _get_center_pivot_pref()


def _get_wrap_icons_pref():
    """Keep Icons Visible is always enabled"""
    return True


def _set_wrap_icons_pref(enabled):
    """Keep Icons Visible is always enabled - kept for compatibility"""
    pass


def _get_show_all_sliders_pref():
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "show_all_sliders.json")
    if os.path.exists(pref_file):
        try:
            with open(pref_file, 'r') as f:
                data = json.load(f)
                return data.get("show_all_sliders", False)
        except:
            pass
    return False


def _set_show_all_sliders_pref(enabled):
    _ensure_prefs_dir()
    pref_file = os.path.join(ANIMO_PREFS_PATH, "show_all_sliders.json")
    try:
        with open(pref_file, 'w') as f:
            json.dump({"show_all_sliders": enabled}, f, indent=2)
    except:
        pass


_show_all_sliders_container = None
_show_all_sliders_visible = False


def _toggle_center_pivot(enable):
    """Toggle the Keep Selections at Center feature on/off."""
    try:
        # Find the script (.py or .pyc)
        script_path = None
        for ext in [".py", ".pyc"]:
            potential_path = os.path.join(ICONS_PATH, "KeepSelectionsCenter" + ext)
            if os.path.exists(potential_path):
                script_path = potential_path
                break
        
        if not script_path:
            cmds.warning("KeepSelectionsCenter script not found in: {}".format(ICONS_PATH))
            return
        
        # Add to path if needed
        if ICONS_PATH not in sys.path:
            sys.path.insert(0, ICONS_PATH)
        
        # Clear cached module
        for mod_name in list(sys.modules.keys()):
            if 'KeepSelectionsCenter' in mod_name:
                del sys.modules[mod_name]
        
        # Import and run appropriate function
        import KeepSelectionsCenter
        
        if enable:
            KeepSelectionsCenter.activateCenterPivot()
            _set_center_pivot_pref(True)
            cmds.inViewMessage(
                amg='<span style="color:#4aa3df;">Keep Selections at Center: ON</span>',
                pos='midCenter', fade=True, fadeStayTime=1000
            )
        else:
            KeepSelectionsCenter.deactivateCenterPivot()
            _set_center_pivot_pref(False)
            cmds.inViewMessage(
                amg='<span style="color:#ff9900;">Keep Selections at Center: OFF</span>',
                pos='midCenter', fade=True, fadeStayTime=1000
            )
    except Exception as e:
        cmds.warning("Failed to toggle Keep Selections at Center: {}".format(str(e)))

enable_usersetup_security()

USERSETUP_ANIMO_CODE = '''# ANIMO_START
from maya import cmds
if not cmds.about(batch=True):
    def _launch_animo():
        import sys
        import os
        maya_version = int(cmds.about(version=True)[:4])
        if maya_version < 2022:
            return
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        animo = os.path.join(script_dir, "Animo_Data")
        if not os.path.exists(animo):
            return
        launcher = os.path.join(animo, "Animo_Launcher")
        for p in [script_dir, animo, launcher]:
            if p not in sys.path:
                sys.path.insert(0, p)
        for m in [k for k in sys.modules if 'Animo' in k]:
            del sys.modules[m]
        import Animo_Launcher
    cmds.evalDeferred(lambda: cmds.evalDeferred(_launch_animo, lowestPriority=True))
# ANIMO_END
'''

def _get_usersetup_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "userSetup.py")

def _is_animo_in_usersetup():
    usersetup_path = _get_usersetup_path()
    if not os.path.exists(usersetup_path):
        return False
    try:
        with open(usersetup_path, 'r') as f:
            content = f.read()
        return '# ANIMO_START' in content and '# ANIMO_END' in content
    except:
        return False

def _add_animo_to_usersetup():
    usersetup_path = _get_usersetup_path()
    try:
        if os.path.exists(usersetup_path):
            with open(usersetup_path, 'r') as f:
                content = f.read()
            if '# ANIMO_START' in content:
                return True
            with open(usersetup_path, 'a') as f:
                f.write("\n\n")
                f.write(USERSETUP_ANIMO_CODE)
        else:
            with open(usersetup_path, 'w') as f:
                f.write(USERSETUP_ANIMO_CODE)
        return True
    except Exception as e:
        cmds.warning("Failed to add Animo to userSetup.py: {}".format(e))
        return False

def _remove_animo_from_usersetup():
    usersetup_path = _get_usersetup_path()
    if not os.path.exists(usersetup_path):
        return True
    try:
        with open(usersetup_path, 'r') as f:
            content = f.read()
        if '# ANIMO_START' not in content:
            return True
        # Remove everything between ANIMO_START and ANIMO_END (inclusive)
        start_idx = content.find('# ANIMO_START')
        end_idx = content.find('# ANIMO_END')
        if start_idx != -1 and end_idx != -1:
            end_idx = end_idx + len('# ANIMO_END')
            # Also remove trailing newline if present
            if end_idx < len(content) and content[end_idx] == '\n':
                end_idx += 1
            new_content = content[:start_idx] + content[end_idx:]
            # Clean up extra newlines
            while '\n\n\n' in new_content:
                new_content = new_content.replace('\n\n\n', '\n\n')
            new_content = new_content.strip()
            if not new_content:
                if os.path.exists(usersetup_path):
                    os.remove(usersetup_path)
            else:
                with open(usersetup_path, 'w') as f:
                    f.write(new_content)
        return True
    except Exception as e:
        cmds.warning("Failed to remove Animo from userSetup.py: {}".format(e))
        return False

def _check_first_run_startup():
    if IS_MAC:
        return
    prefs_path = os.path.join(ANIMO_DATA_PATH, "Animo_Prefs")
    if not os.path.exists(prefs_path):
        try:
            os.makedirs(prefs_path)
        except:
            pass
    startup_pref_file = os.path.join(prefs_path, "startup_configured.txt")
    if not os.path.exists(startup_pref_file):
        _add_animo_to_usersetup()
        try:
            with open(startup_pref_file, 'w') as f:
                f.write("1")
        except:
            pass

_check_first_run_startup()

for mod_name in list(sys.modules.keys()):
    if 'Animo_UI' in mod_name or 'Animo_Sliders' in mod_name:
        del sys.modules[mod_name]

from Animo_UI import styleMod as style
from Animo_UI import barMod as bar
from Animo_UI import shelfMod as shelf
from Animo_Sliders import tween_slider, blend_slider, scale_slider, cascade_slider, slider_utils
from Animo_Selection_Count import selection_counter
from Animo_Selection_Count.selection_counter import SelectionCounter

# Import ease_slider module for Ctrl+TW functionality
try:
    from Animo_Sliders import ease_slider
except ImportError:
    ease_slider = None

# Import tooltip system
try:
    import tooltip_manager as tt_manager
    importlib.reload(tt_manager)
    TOOLTIP_ENABLED = True
except ImportError:
    TOOLTIP_ENABLED = False
    tt_manager = None

importlib.reload(style)
importlib.reload(bar)
importlib.reload(tween_slider)
importlib.reload(blend_slider)
importlib.reload(scale_slider)
importlib.reload(cascade_slider)
importlib.reload(slider_utils)
importlib.reload(selection_counter)
if ease_slider:
    importlib.reload(ease_slider)

# Initialize tooltip manager (only if preference is enabled)
_tooltip_manager = None
_tooltips_user_enabled = _get_tooltip_pref()
if TOOLTIP_ENABLED and _tooltips_user_enabled:
    _tooltip_manager = tt_manager.init_tooltip_manager(ANIMO_DATA_PATH)


class AnimoSizeSettingsDialog(QtWidgets.QDialog):
    """Dialog for adjusting Animo UI size"""
    
    def __init__(self, parent=None):
        super(AnimoSizeSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Animo Size Settings")
        self.setFixedSize(280, 280)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        label = QtWidgets.QLabel("Select UI Size:")
        label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(label)
        
        self.button_group = QtWidgets.QButtonGroup(self)
        
        current_scale = style.get_user_scale()
        
        size_options = [
            ("20% Smaller", 0.8),
            ("10% Smaller", 0.9),
            ("Default", 1.0),
            ("10% Bigger", 1.1),
            ("20% Bigger", 1.2),
            ("30% Bigger", 1.3),
            ("40% Bigger", 1.4),
        ]
        
        for name, scale in size_options:
            radio = QtWidgets.QRadioButton(name)
            radio.setStyleSheet("font-size: 11px;")
            if abs(current_scale - scale) < 0.01:
                radio.setChecked(True)
            radio._scale_value = scale
            self.button_group.addButton(radio)
            layout.addWidget(radio)
        
        layout.addStretch()
        
        btn_layout = QtWidgets.QHBoxLayout()
        
        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.setMinimumWidth(80)
        apply_btn.setMinimumHeight(28)
        apply_btn.clicked.connect(self._apply_size)
        btn_layout.addStretch()
        btn_layout.addWidget(apply_btn)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setMinimumHeight(28)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QDialog { background-color: #3d3d3d; }
            QLabel { color: #ccc; }
            QRadioButton { color: #ccc; }
            QRadioButton::indicator { width: 12px; height: 12px; }
            QPushButton { 
                background-color: #555; 
                color: #ccc; 
                border: 1px solid #666; 
                border-radius: 3px; 
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #666; }
            QPushButton:pressed { background-color: #444; }
        """)
    
    def _apply_size(self):
        for btn in self.button_group.buttons():
            if btn.isChecked():
                new_scale = btn._scale_value
                current_scale = style.get_user_scale()
                
                if abs(new_scale - current_scale) > 0.01:
                    style.set_user_scale(new_scale)
                    self.accept()
                    
                    cmds.inViewMessage(
                        amg='<span style="color:#4aa3df;">Animo size updated - Restarting UI...</span>',
                        pos='midCenter', fade=True, fadeStayTime=1000
                    )
                    
                    def restart_animo():
                        import runpy
                        toggle_py = os.path.join(ANIMO_DATA_PATH, "Animo_Launcher", "toggle.py")
                        if os.path.exists(toggle_py):
                            runpy.run_path(toggle_py, run_name="__main__")
                            def reopen(path=toggle_py):
                                import runpy as rp
                                rp.run_path(path, run_name="__main__")
                            QtCore.QTimer.singleShot(100, reopen)
                    
                    QtCore.QTimer.singleShot(500, restart_animo)
                else:
                    self.reject()
                return
        self.reject()


def _show_size_settings():
    """Show the size settings dialog"""
    dialog = AnimoSizeSettingsDialog(None)
    dialog.exec_()


def run_smooth_keys_plugin():
    """Load and run the AnimoSmoothKeysPlugin"""
    import maya.cmds as cmds
    
    plugin_name = "AnimoSmoothKeysPlugin"
    plugin_folder = os.path.join(ANIMO_DATA_PATH, "Animo_Tools_Editor", "animo_tools", "tools")
    
    # Check if plugin is already loaded
    is_loaded = False
    try:
        is_loaded = cmds.pluginInfo(plugin_name, query=True, loaded=True)
    except:
        pass
    
    if not is_loaded:
        # Try to find and load the plugin (.py or .pyc)
        plugin_path = None
        for ext in [".py", ".pyc"]:
            potential_path = os.path.join(plugin_folder, plugin_name + ext)
            if os.path.exists(potential_path):
                plugin_path = potential_path
                break
        
        if plugin_path:
            try:
                cmds.loadPlugin(plugin_path)
            except Exception as e:
                cmds.warning("Failed to load AnimoSmoothKeysPlugin: {}".format(e))
                return
        else:
            cmds.warning("AnimoSmoothKeysPlugin not found in: {}".format(plugin_folder))
            return
    
    # Run the smooth keys command
    try:
        cmds.smoothKeysAPI(strength=0.5, iterations=1)
    except Exception as e:
        cmds.warning("Failed to run smoothKeysAPI: {}".format(e))


def run_global_tangent(script_name):
    """Run a global tangent script and show confirmation message"""
    bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, script_name, "Animo_Keys_Tangent", None)
    
    # Show confirmation message based on tangent type
    tangent_messages = {
        "auto_tangent_global": "Auto Tangent set as Maya default",
        "linear_tangent_global": "Linear Tangent set as Maya default",
        "step_tangent_global": "Stepped Tangent set as Maya default"
    }
    message = tangent_messages.get(script_name, "Global tangent applied")
    cmds.inViewMessage(
        amg='<span style="color:#4aa3df;">{}</span>'.format(message),
        pos='midCenter', fade=True, fadeStayTime=1000
    )


def run_tracify_arc_track():
    """Run tracify Arc Track toggle - exactly like the Track Arcs button in the UI"""
    try:
        tracify_path = os.path.join(ANIMO_DATA_PATH, "Animo_Launcher")
        if tracify_path not in sys.path:
            sys.path.insert(0, tracify_path)
        
        # Clear cached module for fresh import
        for mod_name in list(sys.modules.keys()):
            if 'tracify' in mod_name.lower():
                del sys.modules[mod_name]
        
        import tracify
        
        # Load saved preferences (same as tracify_launcher.py)
        # Load custom colors
        trail_color = (0.85, 0.12, 0.11)  # Default red
        keys_color = (0.95, 0.45, 0.45)
        
        if cmds.optionVar(exists='TracifyUI_TrailColor'):
            try:
                parts = cmds.optionVar(q='TracifyUI_TrailColor').split(',')
                trail_color = (float(parts[0]), float(parts[1]), float(parts[2]))
            except:
                pass
        
        if cmds.optionVar(exists='TracifyUI_KeysColor'):
            try:
                parts = cmds.optionVar(q='TracifyUI_KeysColor').split(',')
                keys_color = (float(parts[0]), float(parts[1]), float(parts[2]))
            except:
                pass
        
        # Load dot size and line width
        point_size = 5.0  # Default
        if cmds.optionVar(exists='TracifyUI_DotSize'):
            try:
                point_size = float(cmds.optionVar(q='TracifyUI_DotSize'))
            except:
                pass
        
        line_width = 4.0  # Default
        if cmds.optionVar(exists='TracifyUI_LineWidth'):
            try:
                line_width = float(cmds.optionVar(q='TracifyUI_LineWidth'))
            except:
                pass
        
        # Load color mode
        color_mode = 1  # Default: rainbow
        if cmds.optionVar(exists='TracifyUI_ColorMode'):
            try:
                color_mode = cmds.optionVar(q='TracifyUI_ColorMode')
            except:
                pass
        
        # Apply settings to tracify module
        cmds.undoInfo(openChunk=True, chunkName="Tracify Toggle")
        try:
            tracify.COLORS[0] = trail_color
            tracify.KEY_COLOR = keys_color
            tracify.POINT_SIZE = point_size
            tracify.LINE_WIDTH = line_width
            tracify._colorIndex = 0
            
            # Toggle - creates if none exist, clears if they do
            tracify.t()
            
            # Apply saved color mode after creating
            if color_mode > 0:
                tracify.setColorMode(color_mode)
        except Exception as e:
            cmds.warning("Tracify error: {}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            try:
                cmds.setFocus("MayaWindow")
            except:
                pass
    except Exception as e:
        cmds.warning("Failed to run Arc Track: {}".format(str(e)))


# Shelf command for smooth keys plugin
SMOOTH_KEYS_SHELF_COMMAND = '''
import maya.cmds as cmds
import os

plugin_name = "AnimoSmoothKeysPlugin"

# Get Animo_Data path - same as shelfMod.py
animo_data_path = os.path.normpath(os.path.join(cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'))
plugin_folder = os.path.join(animo_data_path, "Animo_Tools_Editor", "animo_tools", "tools")

try:
    is_loaded = False
    try:
        is_loaded = cmds.pluginInfo(plugin_name, query=True, loaded=True)
    except:
        pass
    
    if not is_loaded:
        plugin_loaded = False
        for ext in [".py", ".pyc"]:
            plugin_path = os.path.join(plugin_folder, plugin_name + ext)
            if os.path.exists(plugin_path):
                cmds.loadPlugin(plugin_path)
                plugin_loaded = True
                break
        if not plugin_loaded:
            cmds.warning("AnimoSmoothKeysPlugin not found in: " + plugin_folder)
    
    if cmds.pluginInfo(plugin_name, query=True, loaded=True):
        cmds.smoothKeysAPI(strength=0.5, iterations=1)
    else:
        cmds.warning("Could not load AnimoSmoothKeysPlugin")
except Exception as e:
    cmds.warning("Smooth Keys Error: " + str(e))
'''

def add_smooth_to_shelf(icon_path):
    """Add smooth keys plugin to shelf"""
    import maya.cmds as cmds
    current_shelf = cmds.shelfTabLayout("ShelfLayout", query=True, selectTab=True)
    cmds.shelfButton(
        parent=current_shelf,
        image=icon_path,
        label="Smooth Keys",
        command=SMOOTH_KEYS_SHELF_COMMAND,
        sourceType="python",
        annotation="Smooth Selected Keys"
    )
    cmds.inViewMessage(amg='<span style="color:#4aa3df;">Smooth Keys added to shelf</span>', pos='midCenter', fade=True, fst=200, fad=400)

def assign_smooth_hotkey(icon_path):
    """Assign hotkey for smooth keys plugin"""
    import maya.cmds as cmds
    import sys
    import os
    import importlib
    
    try:
        animo_data_path = os.path.normpath(os.path.join(
            cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'
        ))
        ui_path = os.path.normpath(os.path.join(animo_data_path, 'Animo_UI'))
        
        if ui_path not in sys.path:
            sys.path.insert(0, ui_path)
        
        if 'hotkeyMod' in sys.modules:
            del sys.modules['hotkeyMod']
        
        import hotkeyMod
        
        hotkeyMod.show_hotkey_dialog("Smooth Keys", SMOOTH_KEYS_SHELF_COMMAND, None, None, icon_path)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        cmds.warning("Could not open hotkey dialog: {}".format(str(e)))

def create_smooth_context_menu(button, icon_path):
    """Create context menu for smooth keys button"""
    def show_context_menu(pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
        ''')
        
        shelf_action = menu.addAction("Add to Shelf")
        shelf_action.triggered.connect(lambda: add_smooth_to_shelf(icon_path))
        
        hotkey_action = menu.addAction("Assign Hotkey")
        hotkey_action.triggered.connect(lambda: assign_smooth_hotkey(icon_path))
        
        menu.exec_(button.mapToGlobal(pos))
    
    button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    button.customContextMenuRequested.connect(show_context_menu)

WorkspaceName = 'animo'

# Modern tooltip style - pure black background
TOOLTIP_STYLE = """
    QToolTip {
        background-color: #000000;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
"""


class DelayedTooltipFilter(QtCore.QObject):
    """Event filter to show tooltips after 0.5 second delay"""
    def __init__(self):
        super(DelayedTooltipFilter, self).__init__()
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(500)  # 0.5 second delay
        self._current_widget = None
        self._timer.timeout.connect(self._showTooltip)
    
    def _showTooltip(self):
        if self._current_widget and self._current_widget.toolTip():
            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(),
                self._current_widget.toolTip(),
                self._current_widget
            )
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self._current_widget = obj
            self._timer.start()
        elif event.type() == QtCore.QEvent.Leave:
            self._timer.stop()
            self._current_widget = None
            QtWidgets.QToolTip.hideText()
        return False


# Global filter instance

_tooltip_filter = DelayedTooltipFilter()



class HoverAnimationFilter(QtCore.QObject):
    """Event filter to add pulse animation on hover"""
    def __init__(self):
        super(HoverAnimationFilter, self).__init__()
        self._animations = {}  # Store animations per widget
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self._startAnimation(obj)
        elif event.type() == QtCore.QEvent.Leave:
            self._stopAnimation(obj)
        return False
    
    def _startAnimation(self, widget):
        # Create opacity effect if not exists
        if widget not in self._animations:
            effect = QtWidgets.QGraphicsOpacityEffect(widget)
            effect.setOpacity(1.0)
            widget.setGraphicsEffect(effect)
            
            # Create animation group for ping-pong effect
            anim_group = QtCore.QSequentialAnimationGroup(widget)
            
            anim1 = QtCore.QPropertyAnimation(effect, b"opacity")
            anim1.setDuration(800)  # Slower: 800ms
            anim1.setStartValue(1.0)
            anim1.setEndValue(0.7)  # More subtle: only to 70%
            anim1.setEasingCurve(QtCore.QEasingCurve.InOutSine)
            
            anim2 = QtCore.QPropertyAnimation(effect, b"opacity")
            anim2.setDuration(800)  # Slower: 800ms
            anim2.setStartValue(0.7)
            anim2.setEndValue(1.0)
            anim2.setEasingCurve(QtCore.QEasingCurve.InOutSine)
            
            anim_group.addAnimation(anim1)
            anim_group.addAnimation(anim2)
            anim_group.setLoopCount(-1)
            
            self._animations[widget] = (effect, anim_group)
        
        # Start animation
        effect, anim_group = self._animations[widget]
        anim_group.start()
    
    def _stopAnimation(self, widget):
        if widget in self._animations:
            effect, anim_group = self._animations[widget]
            anim_group.stop()
            effect.setOpacity(1.0)


_hover_animation_filter = HoverAnimationFilter()


class DraggableIconFilter(QtCore.QObject):
    """Event filter to allow dragging icons left/right to reposition them"""
    def __init__(self, parent_ui):
        super(DraggableIconFilter, self).__init__()
        self.parent_ui = parent_ui
        self.dragging = False
        self.drag_start_x = 0
        self.original_offset = 0
        self.current_widget = None
        self.icon_index = None
    
    def eventFilter(self, obj, event):
        if not hasattr(self.parent_ui, '_edit_mode') or not self.parent_ui._edit_mode:
            return False
        
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                self.dragging = True
                self.drag_start_x = event.globalX()
                self.current_widget = obj
                self.icon_index = getattr(obj, '_icon_index', None)
                if self.icon_index is not None:
                    self.original_offset = bar.ICON_OFFSETS.get(self.icon_index, 0)
                return True
        
        elif event.type() == QtCore.QEvent.MouseMove:
            if self.dragging and self.current_widget:
                delta = event.globalX() - self.drag_start_x
                new_offset = self.original_offset + delta
                
                # Update the offset in bar module
                if self.icon_index is not None:
                    bar.ICON_OFFSETS[self.icon_index] = new_offset
                    
                    # Move widget directly for real-time feedback
                    current_pos = self.current_widget.pos()
                    # Calculate new position based on original + delta
                    if not hasattr(self.current_widget, '_original_x'):
                        self.current_widget._original_x = current_pos.x()
                    
                    new_x = self.current_widget._original_x + new_offset
                    self.current_widget.move(new_x, current_pos.y())
                    
                    self.current_widget.setStyleSheet("""
                        QPushButton { border: 2px solid #00ff00; background: rgba(0,255,0,30); }
                        QPushButton:hover { background-color: rgba(0,255,0,50); border-radius: 8px; }
                    """)
                return True
        
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if self.dragging:
                self.dragging = False
                self.current_widget = None
                return True
        
        return False


_draggable_filter = None  # Will be initialized with parent_ui


class FlowLayout(QtWidgets.QLayout):
    """
    A layout that arranges widgets horizontally, wrapping to new rows when needed.
    Each row is centered horizontally, and all rows are centered vertically.
    Used for "Keep Icons Visible" feature to prevent icons from being clipped.
    """
    
    def __init__(self, parent=None, margin=0, h_spacing=4, v_spacing=4):
        super(FlowLayout, self).__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self._item_list.append(item)
    
    def horizontalSpacing(self):
        if self._h_spacing >= 0:
            return self._h_spacing
        return self._smartSpacing(QtWidgets.QStyle.PM_LayoutHorizontalSpacing)
    
    def verticalSpacing(self):
        if self._v_spacing >= 0:
            return self._v_spacing
        return self._smartSpacing(QtWidgets.QStyle.PM_LayoutVerticalSpacing)
    
    def _smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
    
    def count(self):
        return len(self._item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, False)
    
    def sizeHint(self):
        # Return a size hint that allows horizontal expansion
        # Width should be large enough to fit all items in one row (preferred)
        # But minimumSize() allows wrapping when space is limited
        total_width = 0
        max_height = 0
        h_space = self.horizontalSpacing()
        
        for i, item in enumerate(self._item_list):
            if item.widget() is None:
                continue
            size = item.sizeHint()
            if i > 0:
                total_width += h_space
            total_width += size.width()
            max_height = max(max_height, size.height())
        
        margins = self.contentsMargins()
        return QtCore.QSize(
            total_width + margins.left() + margins.right(),
            max_height + margins.top() + margins.bottom()
        )
    
    def minimumSize(self):
        # Minimum size should be the largest single item (to allow wrapping)
        size = QtCore.QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), 
                            margins.top() + margins.bottom())
        return size
    
    def _doLayout(self, rect, test_only):
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(margins.left(), margins.top(), 
                                       -margins.right(), -margins.bottom())
        available_width = effective_rect.width()
        h_space = self.horizontalSpacing()
        v_space = self.verticalSpacing()
        
        # Collect all visible items
        items = [item for item in self._item_list if item.widget() is not None]
        if not items:
            return margins.top() + margins.bottom()
        
        # Calculate widths
        item_widths = [item.sizeHint().width() for item in items]
        
        def calc_row_width(start_idx, end_idx):
            """Calculate total width for items[start_idx:end_idx]"""
            if start_idx >= end_idx:
                return 0
            width = sum(item_widths[start_idx:end_idx])
            width += h_space * (end_idx - start_idx - 1)  # spacing between items
            return width
        
        total_width = calc_row_width(0, len(items))
        
        # Determine rows
        if total_width <= available_width:
            # Everything fits in one row
            rows = [(items, total_width)]
        else:
            # Need to split - find best split point for ~50/50 by width
            best_split = len(items) // 2  # Default to middle by count
            best_diff = float('inf')
            
            # Try each possible split point
            for split in range(1, len(items)):
                row1_width = calc_row_width(0, split)
                row2_width = calc_row_width(split, len(items))
                
                # Both rows must fit
                if row1_width <= available_width and row2_width <= available_width:
                    diff = abs(row1_width - row2_width)
                    if diff < best_diff:
                        best_diff = diff
                        best_split = split
            
            # Build two rows at best split point
            row1_items = items[:best_split]
            row2_items = items[best_split:]
            row1_width = calc_row_width(0, best_split)
            row2_width = calc_row_width(best_split, len(items))
            
            # If split doesn't work (rows still too wide), fall back to greedy fill
            if row1_width > available_width or row2_width > available_width:
                rows = []
                current_row = []
                current_row_width = 0
                for i, item in enumerate(items):
                    item_width = item_widths[i]
                    space_needed = h_space if current_row else 0
                    if current_row and current_row_width + space_needed + item_width > available_width:
                        rows.append((current_row, current_row_width))
                        current_row = [item]
                        current_row_width = item_width
                    else:
                        current_row.append(item)
                        current_row_width += space_needed + item_width
                if current_row:
                    rows.append((current_row, current_row_width))
            else:
                rows = []
                if row1_items:
                    rows.append((row1_items, row1_width))
                if row2_items:
                    rows.append((row2_items, row2_width))
        
        # Calculate row heights
        row_heights = []
        for row_items, row_width in rows:
            row_height = max(item.sizeHint().height() for item in row_items) if row_items else 0
            row_heights.append(row_height)
        
        # Calculate total height
        total_height = sum(row_heights)
        if len(rows) > 1:
            total_height += v_space * (len(rows) - 1)
        
        if test_only:
            return total_height + margins.top() + margins.bottom()
        
        # Position items with centering
        content_height = total_height
        available_height = effective_rect.height()
        if available_height > content_height:
            y = effective_rect.y() + (available_height - content_height) // 2
        else:
            y = effective_rect.y()
        
        for row_idx, (row_items, row_width) in enumerate(rows):
            row_height = row_heights[row_idx]
            
            # Horizontal centering
            x_offset = (available_width - row_width) // 2
            x = effective_rect.x() + x_offset
            
            for item in row_items:
                item_size = item.sizeHint()
                item_y = y + (row_height - item_size.height()) // 2
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, item_y), item_size))
                x += item_size.width() + h_space
            
            y += row_height + v_space
        
        return total_height + margins.top() + margins.bottom()


class AnimoSlider(QtWidgets.QSlider):
    
    statusChanged = QtCore.Signal(str)
    
    def __init__(self, label="TW", handle_color=(80, 200, 120), slider_type="tween", parent=None):
        super(AnimoSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        
        self.label_text = label
        self.original_label = label
        self.handle_color = QtGui.QColor(*handle_color)
        self.icon_color = QtGui.QColor(*handle_color)
        self.slider_type = slider_type
        
        self.mouse_pressed = False
        self.last_update_time = 0
        self.update_throttle_ms = 1
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.needs_cursor_restore = False
        
        self.setMinimumHeight(style.scaled(21))
        self.setMaximumHeight(style.scaled(21))
        self.setMinimumWidth(style.scaled(200))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.valueChanged.connect(self._onValueChanged)
        
        if self.slider_type == "scale" or self.slider_type == "tween":
            QtWidgets.QApplication.instance().installEventFilter(self)
        
    def setLabel(self, label):
        self.label_text = label
        self.update()
    
    def eventFilter(self, obj, event):
        if self.slider_type == "scale":
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Shift:
                    self.shift_pressed = True
                    self._updateScaleLabel()
                elif event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = True
                    self._updateScaleLabel()
            elif event.type() == QtCore.QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Shift:
                    self.shift_pressed = False
                    self._updateScaleLabel()
                elif event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = False
                    self._updateScaleLabel()
        elif self.slider_type == "tween":
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = True
                    self._updateTweenLabel()
            elif event.type() == QtCore.QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Control:
                    self.ctrl_pressed = False
                    self._updateTweenLabel()
        return False
    
    def _updateTweenLabel(self):
        """Update tween slider label based on Ctrl key state"""
        if self.slider_type == "tween":
            if self.ctrl_pressed:
                self.setLabel("EA")
            else:
                self.setLabel("TW")
    
    def _updateScaleLabel(self):
        if self.slider_type == "scale":
            if self.ctrl_pressed:
                self.setLabel("SA")
            elif self.shift_pressed:
                self.setLabel("SR")
            else:
                self.setLabel("SL")
    
    def _onValueChanged(self, value):
        if not self.mouse_pressed:
            return
        
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
        self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
        
        if self.slider_type == "tween":
            self._updateTweenLabel()
            if self.ctrl_pressed and ease_slider:
                # Use ease_slider when Ctrl is held
                ease_slider.update_ease(value)
                status = "Ease: {}".format(value)
                self.statusChanged.emit(status)
            else:
                self.last_update_time, status = tween_slider.slider_logic(
                    value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
                if status:
                    self.statusChanged.emit(status)
        elif self.slider_type == "blend":
            self.last_update_time, status = blend_slider.slider_logic(
                value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_type == "scale":
            self._updateScaleLabel()
            if self.ctrl_pressed:
                self.last_update_time, status = scale_slider.scale_avg_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            elif self.shift_pressed:
                self.last_update_time, status = scale_slider.scale_right_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            else:
                self.last_update_time, status = scale_slider.scale_left_logic(
                    value, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_type == "cascade":
            self.last_update_time, status = cascade_slider.slider_logic(
                value, self.mouse_pressed, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        icon_size = style.scaled(6)
        num_dots = 7
        total_items = num_dots + 2
        
        margin = style.scaled(8)
        # Blend slider gets extra right margin to prevent overlap with tangent icons
        right_margin = style.scaled(12) if self.slider_type == "blend" else margin
        available_width = rect.width() - margin - right_margin
        item_spacing = available_width / (total_items - 1)
        
        icon_left = margin
        icon_y = rect.height() // 2 - icon_size // 2
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_left, icon_y, icon_size, icon_size, 1, 1)
        
        track_start = margin + item_spacing
        track_end = rect.width() - right_margin - item_spacing
        track_y = rect.height() // 2
        
        dot_color = QtGui.QColor(self.handle_color)
        dot_color.setAlpha(220)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        
        dot_spacing = (track_end - track_start) / (num_dots - 1)
        dot_radius = style.scaled(2.15)
        
        for i in range(num_dots):
            dot_x = track_start + i * dot_spacing
            painter.drawEllipse(QtCore.QPointF(dot_x, track_y), dot_radius, dot_radius)
        
        min_val = self.minimum()
        max_val = self.maximum()
        curr_val = self.value()
        
        if max_val != min_val:
            normalized = float(curr_val - min_val) / float(max_val - min_val)
        else:
            normalized = 0.5
            
        handle_x = track_start + normalized * (track_end - track_start)
        handle_y = track_y
        
        handle_size = style.scaled(22)
        handle_rect = QtCore.QRectF(
            handle_x - handle_size / 2,
            handle_y - handle_size / 2,
            handle_size,
            handle_size
        )
        
        painter.setBrush(self.handle_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(handle_rect, 3, 3)
        
        painter.setPen(QtGui.QColor(40, 40, 40))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(handle_rect, QtCore.Qt.AlignCenter, self.label_text)
        
        icon_right = rect.width() - right_margin - icon_size
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_right, icon_y, icon_size, icon_size, 1, 1)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            
            icon_size = style.scaled(6)
            margin = style.scaled(8)
            right_margin = style.scaled(12) if self.slider_type == "blend" else margin
            icon_y = rect.height() // 2 - icon_size // 2
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - margin - right_margin
            item_spacing = available_width / (total_items - 1)
            track_start = margin + item_spacing
            track_end = rect.width() - right_margin - item_spacing
            
            left_icon_rect = QtCore.QRect(margin, icon_y, icon_size, icon_size)
            
            icon_right = rect.width() - right_margin - icon_size
            right_icon_rect = QtCore.QRect(icon_right, icon_y, icon_size, icon_size)
            
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
            self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
            
            getCurves = slider_utils.get_anim_curves()
            anim_curves = getCurves[0]
            if anim_curves and len(anim_curves) > 400:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                self.needs_cursor_restore = True
            else:
                self.needs_cursor_restore = False
            
            self.mouse_pressed = True
            self._updateScaleLabel()
            
            if left_icon_rect.contains(click_pos):
                self.setValue(self.minimum())
                release_delay = 100 if slider_utils.IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            elif right_icon_rect.contains(click_pos):
                self.setValue(self.maximum())
                release_delay = 100 if slider_utils.IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            else:
                normalized = (click_pos.x() - track_start) / (track_end - track_start)
                normalized = max(0.0, min(1.0, normalized))
                new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
                self.setValue(int(new_value))

    def mouseMoveEvent(self, event):
        if self.mouse_pressed and event.buttons() & QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            margin = style.scaled(8)
            right_margin = style.scaled(12) if self.slider_type == "blend" else margin
            icon_size = style.scaled(6)
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - margin - right_margin
            item_spacing = available_width / (total_items - 1)
            
            track_start = margin + item_spacing
            track_end = rect.width() - right_margin - item_spacing
            
            normalized = (click_pos.x() - track_start) / (track_end - track_start)
            normalized = max(0.0, min(1.0, normalized))
            
            new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
            self.setValue(int(new_value))
            
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            self.shift_pressed = bool(modifiers & QtCore.Qt.ShiftModifier)
            self.ctrl_pressed = bool(modifiers & QtCore.Qt.ControlModifier)
            self._updateScaleLabel()
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.mouse_pressed:
            release_delay = 100 if slider_utils.IS_MACOS else 50
            QtCore.QTimer.singleShot(release_delay, self._onRelease)
    
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        
        show_all_action = QAction("Show All Sliders", menu)
        show_all_action.setCheckable(True)
        show_all_action.setChecked(_get_show_all_sliders_pref())
        show_all_action.triggered.connect(self._toggleShowAllSliders)
        menu.addAction(show_all_action)
        
        if self.slider_type == "scale":
            menu.addSeparator()
            info_action = QAction("SL = Scale Left", menu)
            info_action.setEnabled(False)
            menu.addAction(info_action)
            info_action2 = QAction("Shift = Scale Right", menu)
            info_action2.setEnabled(False)
            menu.addAction(info_action2)
            info_action3 = QAction("Ctrl = Scale Average", menu)
            info_action3.setEnabled(False)
            menu.addAction(info_action3)
        elif self.slider_type == "tween":
            menu.addSeparator()
            info_action = QAction("TW = Tween", menu)
            info_action.setEnabled(False)
            menu.addAction(info_action)
            info_action2 = QAction("Ctrl = Ease", menu)
            info_action2.setEnabled(False)
            menu.addAction(info_action2)
        
        menu.exec_(event.globalPos())
    
    def _toggleShowAllSliders(self, checked):
        global _show_all_sliders_visible, _show_all_sliders_container
        _set_show_all_sliders_pref(checked)
        _show_all_sliders_visible = checked
        if _show_all_sliders_container:
            _show_all_sliders_container.setVisible(checked)
            parent_toolbar = _show_all_sliders_container.parent()
            if parent_toolbar:
                extra_height = style.scaled(28) if checked else 0
                base_height = style.TOOLBAR_HEIGHT
                new_height = base_height + extra_height
                parent_toolbar.setFixedHeight(new_height)
                parent_toolbar.updateGeometry()
            if checked:
                cmds.inViewMessage(amg='<span style="color:#4aa3df;">All Sliders Visible</span>', pos='midCenter', fade=True, fst=200, fad=400)
            else:
                cmds.inViewMessage(amg='<span style="color:#ff9900;">All Sliders Hidden</span>', pos='midCenter', fade=True, fst=200, fad=400)
    
    def _onRelease(self):
        self.mouse_pressed = False
        
        if self.slider_type == "tween":
            # Finish ease_slider if it was active
            if ease_slider:
                ease_slider.finish_ease()
            tween_slider.reset_slider(self)
            self.setLabel(self.original_label)
        elif self.slider_type == "blend":
            blend_slider.reset_slider(self)
        elif self.slider_type == "scale":
            scale_slider.reset_slider(self)
            self.setLabel(self.original_label)
        elif self.slider_type == "cascade":
            cascade_slider.reset_slider(self)
        
        self.statusChanged.emit("")
        
        if self.needs_cursor_restore:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.needs_cursor_restore = False


class ExpandedSlider(QtWidgets.QSlider):
    
    statusChanged = QtCore.Signal(str)
    
    def __init__(self, label="EA", handle_color=(225, 175, 45), slider_mode="ease", parent=None):
        super(ExpandedSlider, self).__init__(QtCore.Qt.Horizontal, parent)
        
        self.label_text = label
        self.original_label = label
        self.handle_color = QtGui.QColor(*handle_color)
        self.icon_color = QtGui.QColor(*handle_color)
        self.slider_mode = slider_mode
        
        self.mouse_pressed = False
        self.last_update_time = 0
        self.update_throttle_ms = 1
        self.needs_cursor_restore = False
        
        self.setMinimumHeight(style.scaled(21))
        self.setMaximumHeight(style.scaled(21))
        self.setMinimumWidth(style.scaled(160))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.valueChanged.connect(self._onValueChanged)
    
    def setLabel(self, label):
        self.label_text = label
        self.update()
    
    def _onValueChanged(self, value):
        if not self.mouse_pressed:
            return
        
        if self.slider_mode == "ease":
            if ease_slider:
                ease_slider.update_ease(value)
                status = "Ease: {}".format(value)
                self.statusChanged.emit(status)
        elif self.slider_mode == "scale_right":
            self.last_update_time, status = scale_slider.scale_right_logic(
                value, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
        elif self.slider_mode == "scale_avg":
            self.last_update_time, status = scale_slider.scale_avg_logic(
                value, self.last_update_time, self.update_throttle_ms)
            if status:
                self.statusChanged.emit(status)
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        icon_size = style.scaled(6)
        num_dots = 7
        total_items = num_dots + 2
        
        margin = style.scaled(8)
        right_margin = margin
        available_width = rect.width() - margin - right_margin
        item_spacing = available_width / (total_items - 1)
        
        icon_left = margin
        icon_y = rect.height() // 2 - icon_size // 2
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_left, icon_y, icon_size, icon_size, 1, 1)
        
        track_start = margin + item_spacing
        track_end = rect.width() - right_margin - item_spacing
        track_y = rect.height() // 2
        
        dot_color = QtGui.QColor(self.handle_color)
        dot_color.setAlpha(220)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(dot_color)
        
        dot_spacing = (track_end - track_start) / (num_dots - 1)
        dot_radius = style.scaled(2.15)
        
        for i in range(num_dots):
            dot_x = track_start + i * dot_spacing
            painter.drawEllipse(QtCore.QPointF(dot_x, track_y), dot_radius, dot_radius)
        
        min_val = self.minimum()
        max_val = self.maximum()
        curr_val = self.value()
        
        if max_val != min_val:
            normalized = float(curr_val - min_val) / float(max_val - min_val)
        else:
            normalized = 0.5
            
        handle_x = track_start + normalized * (track_end - track_start)
        handle_y = track_y
        
        handle_size = style.scaled(22)
        handle_rect = QtCore.QRectF(
            handle_x - handle_size / 2,
            handle_y - handle_size / 2,
            handle_size,
            handle_size
        )
        
        painter.setBrush(self.handle_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(handle_rect, 3, 3)
        
        painter.setPen(QtGui.QColor(40, 40, 40))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(handle_rect, QtCore.Qt.AlignCenter, self.label_text)
        
        icon_right = rect.width() - right_margin - icon_size
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.icon_color)
        painter.drawRoundedRect(icon_right, icon_y, icon_size, icon_size, 1, 1)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            
            icon_size = style.scaled(6)
            margin = style.scaled(8)
            right_margin = margin
            icon_y = rect.height() // 2 - icon_size // 2
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - margin - right_margin
            item_spacing = available_width / (total_items - 1)
            track_start = margin + item_spacing
            track_end = rect.width() - right_margin - item_spacing
            
            left_icon_rect = QtCore.QRect(margin, icon_y, icon_size, icon_size)
            icon_right = rect.width() - right_margin - icon_size
            right_icon_rect = QtCore.QRect(icon_right, icon_y, icon_size, icon_size)
            
            getCurves = slider_utils.get_anim_curves()
            anim_curves = getCurves[0]
            if anim_curves and len(anim_curves) > 400:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                self.needs_cursor_restore = True
            else:
                self.needs_cursor_restore = False
            
            self.mouse_pressed = True
            
            if left_icon_rect.contains(click_pos):
                self.setValue(self.minimum())
                release_delay = 100 if slider_utils.IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            elif right_icon_rect.contains(click_pos):
                self.setValue(self.maximum())
                release_delay = 100 if slider_utils.IS_MACOS else 50
                QtCore.QTimer.singleShot(release_delay, self._onRelease)
            else:
                normalized = (click_pos.x() - track_start) / (track_end - track_start)
                normalized = max(0.0, min(1.0, normalized))
                new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
                self.setValue(int(new_value))

    def mouseMoveEvent(self, event):
        if self.mouse_pressed and event.buttons() & QtCore.Qt.LeftButton:
            if hasattr(event, 'position'):
                click_pos = event.position().toPoint()
            else:
                click_pos = event.pos()
            
            rect = self.rect()
            margin = style.scaled(8)
            right_margin = margin
            icon_size = style.scaled(6)
            num_dots = 7
            total_items = num_dots + 2
            available_width = rect.width() - margin - right_margin
            item_spacing = available_width / (total_items - 1)
            
            track_start = margin + item_spacing
            track_end = rect.width() - right_margin - item_spacing
            
            normalized = (click_pos.x() - track_start) / (track_end - track_start)
            normalized = max(0.0, min(1.0, normalized))
            
            new_value = self.minimum() + normalized * (self.maximum() - self.minimum())
            self.setValue(int(new_value))
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.mouse_pressed:
            release_delay = 100 if slider_utils.IS_MACOS else 50
            QtCore.QTimer.singleShot(release_delay, self._onRelease)
    
    def _onRelease(self):
        self.mouse_pressed = False
        
        if self.slider_mode == "ease":
            if ease_slider:
                ease_slider.finish_ease()
            self.setValue(0)
        elif self.slider_mode in ("scale_right", "scale_avg"):
            scale_slider.reset_slider(self)
        
        self.statusChanged.emit("")
        
        if self.needs_cursor_restore:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.needs_cursor_restore = False


def create_all_sliders_container():
    global _show_all_sliders_container
    
    container = QtWidgets.QWidget()
    container.setStyleSheet("background: transparent;")
    container.setFixedHeight(style.scaled(28))
    
    layout = QtWidgets.QHBoxLayout(container)
    layout.setContentsMargins(0, 2, 0, 2)
    layout.setSpacing(style.scaled(8))
    
    layout.addStretch(1)
    
    tween_slider_exp = AnimoSlider("TW", (225, 175, 45), "tween")
    tween_slider_exp.setMinimum(-100)
    tween_slider_exp.setMaximum(100)
    tween_slider_exp.setValue(0)
    tween_slider_exp.setFixedWidth(style.scaled(160))
    tween_slider_exp.setToolTip("Tween")
    layout.addWidget(tween_slider_exp)
    
    ease_slider_widget = ExpandedSlider("EA", (245, 195, 75), "ease")
    ease_slider_widget.setMinimum(-100)
    ease_slider_widget.setMaximum(100)
    ease_slider_widget.setValue(0)
    ease_slider_widget.setFixedWidth(style.scaled(160))
    ease_slider_widget.setToolTip("Ease (Ctrl+TW)")
    layout.addWidget(ease_slider_widget)
    
    layout.addSpacing(style.scaled(12))
    
    blend_slider_exp = AnimoSlider("BN", (220, 140, 60), "blend")
    blend_slider_exp.setMinimum(-100)
    blend_slider_exp.setMaximum(100)
    blend_slider_exp.setValue(0)
    blend_slider_exp.setFixedWidth(style.scaled(160))
    blend_slider_exp.setToolTip("Blend")
    layout.addWidget(blend_slider_exp)
    
    layout.addSpacing(style.scaled(12))
    
    scale_slider_exp = AnimoSlider("SL", (100, 180, 220), "scale")
    scale_slider_exp.setMinimum(-100)
    scale_slider_exp.setMaximum(100)
    scale_slider_exp.setValue(0)
    scale_slider_exp.setFixedWidth(style.scaled(160))
    scale_slider_exp.setToolTip("Scale Left")
    layout.addWidget(scale_slider_exp)
    
    scale_right_slider = ExpandedSlider("SR", (130, 200, 235), "scale_right")
    scale_right_slider.setMinimum(-100)
    scale_right_slider.setMaximum(100)
    scale_right_slider.setValue(0)
    scale_right_slider.setFixedWidth(style.scaled(160))
    scale_right_slider.setToolTip("Scale Right (Shift+SL)")
    layout.addWidget(scale_right_slider)
    
    scale_avg_slider = ExpandedSlider("SA", (80, 160, 200), "scale_avg")
    scale_avg_slider.setMinimum(-100)
    scale_avg_slider.setMaximum(100)
    scale_avg_slider.setValue(0)
    scale_avg_slider.setFixedWidth(style.scaled(160))
    scale_avg_slider.setToolTip("Scale Average (Ctrl+SL)")
    layout.addWidget(scale_avg_slider)
    
    layout.addSpacing(style.scaled(12))
    
    cascade_slider_exp = AnimoSlider("CA", (180, 120, 200), "cascade")
    cascade_slider_exp.setMinimum(0)
    cascade_slider_exp.setMaximum(200)
    cascade_slider_exp.setValue(100)
    cascade_slider_exp.setFixedWidth(style.scaled(160))
    cascade_slider_exp.setToolTip("Cascade")
    layout.addWidget(cascade_slider_exp)
    
    layout.addStretch(1)
    
    container.setVisible(_get_show_all_sliders_pref())
    _show_all_sliders_container = container
    
    return container


class toolbar(object):
    
    def __init__(self):
        self.current_dock_mode = None
        self.qt_toolbar = None  # For embedded timeline mode
        self._ui_building = False  # Prevent duplicate UI builds
        self._scroll_offset = 0
        self._content_width = 0
        self._master_container = None
        self._clip_container = None
        self._left_arrow = None
        self._right_arrow = None
        self._resize_filter = None
        self._clip_resize_filter = None
        self._wrap_resize_filter = None  # For Keep Icons Visible mode
        self._master_resize_filter = None  # For Keep Icons Visible mode
        self._toolbar_resize_filter = None  # For Keep Icons Visible mode
        self._splitter = None  # Store splitter for height adjustments
        self._last_toolbar_height = 0  # Track height changes
        self._edit_mode = False  # Icon repositioning mode
        self._wrap_icons_enabled = False  # Keep Icons Visible mode
        self._draggable_filter = DraggableIconFilter(self)
        
        # Load saved dock mode from JSON prefs file
        self._loadDockMode()
    
    def _loadDockMode(self):
        """Load dock mode from JSON prefs file"""
        prefs_file = get_prefs_file()
        try:
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    prefs = json.load(f)
                    saved_mode = prefs.get('dock_mode', None)
                    if saved_mode in ['channelbox', 'toolbox', 'timeline_top', 'timeline_bottom', 'shelf', 'statusline']:
                        self.current_dock_mode = saved_mode
        except:
            pass
    
    def _saveDockMode(self, mode):
        """Save dock mode to JSON prefs file"""
        prefs_file = get_prefs_file()
        try:
            # Load existing prefs or create new
            prefs = {}
            if os.path.exists(prefs_file):
                try:
                    with open(prefs_file, 'r') as f:
                        prefs = json.load(f)
                except:
                    pass
            
            # Update dock mode
            prefs['dock_mode'] = mode
            
            # Save back to file
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=4)
        except Exception as e:
            cmds.warning("Animo: Could not save preferences - {}".format(str(e)))
    
    def _showToolbarContextMenu(self, pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        
        show_all_action = QAction("Show All Sliders", menu)
        show_all_action.setCheckable(True)
        show_all_action.setChecked(_get_show_all_sliders_pref())
        show_all_action.triggered.connect(self._toggleShowAllSlidersFromMenu)
        menu.addAction(show_all_action)
        
        menu.exec_(self.qt_toolbar.mapToGlobal(pos))
    
    def _toggleShowAllSlidersFromMenu(self, checked):
        global _show_all_sliders_visible, _show_all_sliders_container
        _set_show_all_sliders_pref(checked)
        _show_all_sliders_visible = checked
        if _show_all_sliders_container:
            _show_all_sliders_container.setVisible(checked)
            if self.qt_toolbar:
                extra_height = style.scaled(28) if checked else 0
                base_height = style.TOOLBAR_HEIGHT
                new_height = base_height + extra_height
                self.qt_toolbar.setFixedHeight(new_height)
                self.qt_toolbar.updateGeometry()
            if checked:
                cmds.inViewMessage(amg='<span style="color:#4aa3df;">All Sliders Visible</span>', pos='midCenter', fade=True, fst=200, fad=400)
            else:
                cmds.inViewMessage(amg='<span style="color:#ff9900;">All Sliders Hidden</span>', pos='midCenter', fade=True, fst=200, fad=400)
    
    def toggle(self, *args):
        if self.current_dock_mode in ('timeline_top', 'timeline_bottom') and self.qt_toolbar:
            if self.qt_toolbar.isVisible():
                self.qt_toolbar.hide()
            else:
                self.qt_toolbar.show()
        elif cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            if cmds.workspaceControl(WorkspaceName, query=True, visible=True):
                cmds.workspaceControl(WorkspaceName, edit=True, visible=False)
            else:
                cmds.workspaceControl(WorkspaceName, edit=True, restore=True)
        else:
            self.reload()
    
    def reload(self, *args):
        # Clean up Qt toolbar
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
                self._restoreTimelineArea()
            except:
                pass
        
        for mod in list(sys.modules.keys()):
            if 'Animo' in mod:
                del sys.modules[mod]
        if cmds.workspaceControl(WorkspaceName, q=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        import Animo_Launcher
        Animo_Launcher.tb.startUI()
    
    def getImage(self, image):
        return os.path.join(ICONS_PATH, image)
    
    def isDockTargetAvailable(self, mode):
        if mode == 'channelbox':
            # Check if ChannelBox is visible
            try:
                if cmds.workspaceControl("ChannelBoxLayerEditor", query=True, exists=True):
                    if cmds.workspaceControl("ChannelBoxLayerEditor", query=True, visible=True):
                        return True
            except:
                pass
            # Fallback - check if we can find the widget
            try:
                ptr = mui.MQtUtil.findControl("ChannelBoxLayerEditor")
                if ptr:
                    widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                    return widget.isVisible()
            except:
                pass
            return False
        elif mode == 'toolbox':
            # Check if ToolBox is visible
            try:
                if cmds.workspaceControl("ToolBox", query=True, exists=True):
                    if cmds.workspaceControl("ToolBox", query=True, visible=True):
                        return True
            except:
                pass
            # Fallback - check if we can find the widget
            try:
                ptr = mui.MQtUtil.findControl("ToolBox")
                if ptr:
                    widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                    return widget.isVisible()
            except:
                pass
            return False
        elif mode in ('timeline', 'timeline_top', 'timeline_bottom'):
            # Check if timeline/playback slider is visible
            try:
                time_slider_name = mel.eval('$tmpVar=$gPlayBackSlider')
                if time_slider_name:
                    if cmds.timeControl(time_slider_name, query=True, visible=True):
                        return True
            except:
                pass
            # Fallback - check if we can find the widget
            try:
                ptr = mui.MQtUtil.findControl(mel.eval('$tmpVar=$gPlayBackSlider'))
                if ptr:
                    widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                    return widget.isVisible()
            except:
                pass
            return False
        elif mode == 'bottom_toolbar':
            # Bottom toolbar is always available
            return True
        elif mode == 'shelf':
            # Check if shelf is visible
            try:
                shelf_layout = mel.eval('$tmpVar=$gShelfTopLevel')
                if shelf_layout and cmds.shelfTabLayout(shelf_layout, query=True, exists=True):
                    if cmds.shelfTabLayout(shelf_layout, query=True, visible=True):
                        return True
            except:
                pass
            # Fallback - check Qt widget
            try:
                ptr = mui.MQtUtil.findControl(mel.eval('$tmpVar=$gShelfTopLevel'))
                if ptr:
                    widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                    return widget.isVisible()
            except:
                pass
            return False
        elif mode == 'statusline':
            # Check if status line is visible
            try:
                status_line = mel.eval('$tmpVar=$gStatusLine')
                if status_line:
                    ptr = mui.MQtUtil.findControl(status_line)
                    if ptr:
                        widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                        return widget.isVisible()
            except:
                pass
            return False
        return False
    
    def _refreshDockMenu(self, menu, *args):
        """Refresh dock menu items - called before menu shows"""
        # Clear existing items
        menu_items = cmds.popupMenu(menu, query=True, itemArray=True) or []
        for item in menu_items:
            cmds.deleteUI(item)
        
        cmds.menuItem(l="Reset Animo", c=lambda x: self._resetUI(), p=menu)
        cmds.menuItem(l="Add Animo to Shelf", c=lambda x: self._addToShelf(), p=menu)
    
    def _resetUI(self):
        import runpy
        toggle_py = os.path.join(ANIMO_DATA_PATH, "Animo_Launcher", "toggle.py")
        if os.path.exists(toggle_py):
            runpy.run_path(toggle_py, run_name="__main__")
            def reopen(path=toggle_py):
                import runpy as rp
                rp.run_path(path, run_name="__main__")
            QtCore.QTimer.singleShot(100, reopen)
    
    def _addToShelf(self):
        """Add Animo launcher to current shelf"""
        try:
            current_shelf = cmds.shelfTabLayout("ShelfLayout", query=True, selectTab=True)
            animo_icon_path = os.path.join(ICONS_PATH, "animo.png")
            cmds.shelfButton(
                parent=current_shelf,
                image=animo_icon_path,
                label="Animo",
                command="import runpy; import os; import maya.cmds as cmds; runpy.run_path(os.path.join(os.path.normpath(os.path.join(cmds.internalVar(userScriptDir=True), '..', '..', 'scripts')), 'Animo_Data', 'Animo_Launcher', 'toggle.py'), run_name='__main__')",
                sourceType="python",
                annotation="Animo Toolbar"
            )
            cmds.inViewMessage(amg='<span style="color:#82C99A;">Animo added to shelf</span>', pos='topCenter', fade=True, fadeStayTime=1000)
        except Exception as e:
            cmds.warning("Could not add to shelf: {}".format(str(e)))
    
    def _toggleEditMode(self):
        """Toggle icon repositioning edit mode"""
        self._edit_mode = not self._edit_mode
        
        if self._edit_mode:
            cmds.inViewMessage(amg='<span style="color:#00ff00;">Edit Mode ON</span> - Drag icons to reposition. Click "Save Layout" when done.', pos='topCenter', fade=True, fadeStayTime=2000)
            # Update all icon buttons to show edit mode styling
            self._updateEditModeStyle(True)
        else:
            cmds.inViewMessage(amg='<span style="color:#ffaa00;">Edit Mode OFF</span>', pos='topCenter', fade=True, fadeStayTime=1000)
            self._updateEditModeStyle(False)
    
    def _updateEditModeStyle(self, edit_mode):
        """Update icon button styles for edit mode"""
        if not hasattr(self, '_icon_buttons'):
            return
        
        for btn, icon_index in self._icon_buttons:
            if edit_mode:
                # Store original position if not already stored
                if not hasattr(btn, '_original_x'):
                    btn._original_x = btn.pos().x()
                
                # Apply current offset
                offset = bar.ICON_OFFSETS.get(icon_index, 0)
                new_x = btn._original_x + offset
                btn.move(new_x, btn.pos().y())
                
                btn.setStyleSheet("""
                    QPushButton { border: 2px solid #00ff00; background: rgba(0,255,0,20); }
                    QPushButton:hover { background-color: rgba(0,255,0,50); border-radius: 8px; }
                """)
            else:
                # Keep position but restore normal style
                btn.setStyleSheet("""
                    QPushButton { border: none; background: transparent; }
                    QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                    QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                    QPushButton::menu-indicator { width: 0; height: 0; }
                """)
    
    def _saveIconLayout(self):
        """Save icon offsets to barMod.py"""
        try:
            # Get path to barMod.py
            bar_mod_path = os.path.join(ANIMO_DATA_PATH, 'Animo_UI', 'barMod.py')
            
            if not os.path.exists(bar_mod_path):
                cmds.warning("Could not find barMod.py at: {}".format(bar_mod_path))
                return
            
            # Read the file
            with open(bar_mod_path, 'r') as f:
                content = f.read()
            
            # Build new ICON_OFFSETS string
            new_offsets = "ICON_OFFSETS = {\n"
            new_offsets += "    # Transify group (indices 0, 1, 2)\n"
            new_offsets += "    0: {},   # transify\n".format(bar.ICON_OFFSETS.get(0, 0))
            new_offsets += "    1: {},   # keys_time\n".format(bar.ICON_OFFSETS.get(1, 0))
            new_offsets += "    2: {},   # fast_anim_layers\n".format(bar.ICON_OFFSETS.get(2, 0))
            new_offsets += "    \n"
            new_offsets += "    # Pickify group (indices 5, 3, 4)\n"
            new_offsets += "    5: {},   # pickify\n".format(bar.ICON_OFFSETS.get(5, 0))
            new_offsets += "    3: {},   # tweenify\n".format(bar.ICON_OFFSETS.get(3, 0))
            new_offsets += "    4: {},   # tracify\n".format(bar.ICON_OFFSETS.get(4, 0))
            new_offsets += "    \n"
            new_offsets += "    # Spacify group (indices 6, 7, 8, 9)\n"
            new_offsets += "    6: {},   # spacify\n".format(bar.ICON_OFFSETS.get(6, 0))
            new_offsets += "    7: {},   # xform_align\n".format(bar.ICON_OFFSETS.get(7, 0))
            new_offsets += "    8: {},   # attributes_space_switcher\n".format(bar.ICON_OFFSETS.get(8, 0))
            new_offsets += "    9: {},   # temp_pivot\n".format(bar.ICON_OFFSETS.get(9, 0))
            new_offsets += "    \n"
            new_offsets += "    # Global offset group (indices 10, 11, 12)\n"
            new_offsets += "    10: {},  # global_offset\n".format(bar.ICON_OFFSETS.get(10, 0))
            new_offsets += "    11: {},  # twosify\n".format(bar.ICON_OFFSETS.get(11, 0))
            new_offsets += "    12: {},  # vectorify\n".format(bar.ICON_OFFSETS.get(12, 0))
            new_offsets += "    \n"
            new_offsets += "    # Tangent icons (indices 13, 14, 15)\n"
            new_offsets += "    13: {},  # auto_tangent\n".format(bar.ICON_OFFSETS.get(13, 0))
            new_offsets += "    14: {},  # linear_tangent\n".format(bar.ICON_OFFSETS.get(14, 0))
            new_offsets += "    15: {},  # step_tangent\n".format(bar.ICON_OFFSETS.get(15, 0))
            new_offsets += "    \n"
            new_offsets += "    # Exporter group (indices 16, 17, 18)\n"
            new_offsets += "    16: {},  # quick_exporter\n".format(bar.ICON_OFFSETS.get(16, 0))
            new_offsets += "    17: {},  # tools_editor\n".format(bar.ICON_OFFSETS.get(17, 0))
            new_offsets += "    18: {},  # about\n".format(bar.ICON_OFFSETS.get(18, 0))
            new_offsets += "    \n"
            new_offsets += "    # Left slider icons (indices 19, 20, 21)\n"
            new_offsets += "    19: {},  # reset\n".format(bar.ICON_OFFSETS.get(19, 0))
            new_offsets += "    20: {},  # bake\n".format(bar.ICON_OFFSETS.get(20, 0))
            new_offsets += "    21: {},  # share_keys\n".format(bar.ICON_OFFSETS.get(21, 0))
            new_offsets += "    \n"
            new_offsets += "    # White icons near cascade (indices 22, 23, 24, 25, 26, 27)\n"
            new_offsets += "    22: {},  # SelectOpposite\n".format(bar.ICON_OFFSETS.get(22, 0))
            new_offsets += "    23: {},  # Playblaster\n".format(bar.ICON_OFFSETS.get(23, 0))
            new_offsets += "    24: {},  # CropAnimation\n".format(bar.ICON_OFFSETS.get(24, 0))
            new_offsets += "    25: {},  # DeleteRedundantKeys\n".format(bar.ICON_OFFSETS.get(25, 0))
            new_offsets += "    26: {},  # SmoothSelectedKeys\n".format(bar.ICON_OFFSETS.get(26, 0))
            new_offsets += "    27: {},  # SmartSnapKeys\n".format(bar.ICON_OFFSETS.get(27, 0))
            new_offsets += "}"
            
            # Find and replace the ICON_OFFSETS block
            import re
            pattern = r'ICON_OFFSETS = \{[^}]+\}'
            content = re.sub(pattern, new_offsets, content, flags=re.DOTALL)
            
            # Write back
            with open(bar_mod_path, 'w') as f:
                f.write(content)
            
            cmds.inViewMessage(amg='<span style="color:#82C99A;">Icon layout saved!</span>', pos='topCenter', fade=True, fadeStayTime=1500)
            
            # Turn off edit mode
            if self._edit_mode:
                self._toggleEditMode()
                
        except Exception as e:
            cmds.warning("Could not save icon layout: {}".format(str(e)))
    
    def _applySavedOffsets(self):
        """Apply saved icon offsets after UI is shown"""
        if not hasattr(self, '_icon_buttons'):
            return
        
        def apply_offsets():
            for btn, icon_index in self._icon_buttons:
                offset = bar.ICON_OFFSETS.get(icon_index, 0)
                if offset != 0:
                    # Store original position
                    if not hasattr(btn, '_original_x'):
                        btn._original_x = btn.pos().x()
                    # Apply offset
                    new_x = btn._original_x + offset
                    btn.move(new_x, btn.pos().y())
        
        # Delay to ensure layout is complete
        QtCore.QTimer.singleShot(100, apply_offsets)
    
    def _saveCurrentPosition(self):
        """Save current dock position and show confirmation"""
        if self.current_dock_mode:
            self._saveDockMode(self.current_dock_mode)
            cmds.inViewMessage(amg='<span style="color:#82C99A;">Animo position saved: {}</span>'.format(
                self.current_dock_mode.title()), pos='topCenter', fade=True, fadeStayTime=1000)
    
    def setDockMode(self, mode):
        # If target not available, just return - don't try to restore
        if not self.isDockTargetAvailable(mode):
            return
        
        self.current_dock_mode = mode
        self._saveDockMode(mode)  # Save to JSON prefs file
        self.startUI()
    
    def startUI(self):
        # Ensure timeline is visible before UI opens
        try:
            mel.eval('setTimeSliderVisible 1;')
        except:
            pass
        
        # Prevent duplicate UI builds
        if self._ui_building:
            return
        self._ui_building = True
        
        try:
            # Stop existing dock animation
            if hasattr(self, '_dock_anim_group') and self._dock_anim_group:
                self._dock_anim_group.stop()
            
            # Always use timeline mode
            self.current_dock_mode = 'timeline_top'
            
            dock_mode = self.current_dock_mode
            is_horizontal = True
            
            # Clean up existing UI
            if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
                cmds.deleteUI(WorkspaceName, control=True)
            
            # Clean up Qt toolbar if we have a reference
            if self.qt_toolbar:
                try:
                    self.qt_toolbar.hide()
                    self.qt_toolbar.setParent(None)
                    self.qt_toolbar.deleteLater()
                    self.qt_toolbar = None
                    self._restoreTimelineArea()
                except:
                    pass
            
            # Clean up any existing Maya native toolbar
            if cmds.toolBar("animo_timeline_toolbar", query=True, exists=True):
                try:
                    cmds.deleteUI("animo_timeline_toolbar")
                except:
                    pass
            if cmds.window("animo_toolbar_win", query=True, exists=True):
                try:
                    cmds.deleteUI("animo_toolbar_win")
                except:
                    pass
            
            # Also find and clean up ANY orphaned toolbars in Maya
            try:
                maya_main_ptr = mui.MQtUtil.mainWindow()
                if maya_main_ptr:
                    maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
                    existing_toolbars = maya_main.findChildren(QtWidgets.QWidget, "animo_qt_toolbar")
                    for existing in existing_toolbars:
                        try:
                            existing.hide()
                            existing.setParent(None)
                            existing.deleteLater()
                        except:
                            pass
            except:
                pass
            
            if dock_mode == 'timeline_top':
                self.buildTimelineUI(position='top')
        
        finally:
            self._ui_building = False
    
    def buildSideUI(self, target):
        """Build a pure Qt vertical toolbar embedded next to ChannelBox or ToolBox - no undock header"""
        
        # Clean up existing
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
            except:
                pass
        
        # Clean up any workspaceControl
        if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        
        # Find target widget
        target_widget = None
        target_name = "ChannelBoxLayerEditor" if target == 'channelbox' else "ToolBox"
        
        try:
            ptr = mui.MQtUtil.findControl(target_name)
            if ptr:
                target_widget = wrapInstance(int(ptr), QtWidgets.QWidget)
        except:
            pass
        
        if not target_widget:
            cmds.warning("Animo: Could not find {} - using fallback".format(target_name))
            self._buildSideFallback(target)
            return
        
        # Find parent with layout we can insert into
        insert_parent = None
        insert_widget = target_widget
        insert_side = 'left' if target == 'channelbox' else 'right'
        
        # Walk up to find a suitable parent with QHBoxLayout or QSplitter
        current = target_widget
        for _ in range(10):
            parent = current.parent()
            if not parent:
                break
            
            if parent.__class__.__name__ == 'QSplitter':
                insert_parent = parent
                insert_widget = current
                break
            
            layout = parent.layout()
            if layout and layout.__class__.__name__ == 'QHBoxLayout':
                insert_parent = parent
                insert_widget = current
                break
            
            current = parent
        
        if not insert_parent:
            cmds.warning("Animo: Could not find suitable parent layout - using fallback")
            self._buildSideFallback(target)
            return
        
        # Create our toolbar widget
        self.qt_toolbar = QtWidgets.QWidget()
        self.qt_toolbar.setObjectName("animo_qt_toolbar")
        self.qt_toolbar.setFixedWidth(style.TOOLBAR_WIDTH)
        
        # Style to match Maya
        bg_color = "rgb({}, {}, {})".format(
            int(style.TOOLBAR_BG_COLOR[0] * 255),
            int(style.TOOLBAR_BG_COLOR[1] * 255),
            int(style.TOOLBAR_BG_COLOR[2] * 255)
        )
        self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }} {}".format(bg_color, TOOLTIP_STYLE))
        
        # Create vertical layout
        layout = QtWidgets.QVBoxLayout(self.qt_toolbar)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(0)
        
        # Create a container widget for the icons
        icon_container = QtWidgets.QWidget()
        icon_layout = QtWidgets.QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(style.ICON_SPACING_VERTICAL)
        
        # Add tool icons
        for i, icon_data in enumerate(bar.ICON_DATA):
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            offset = icon_data[6] if len(icon_data) > 6 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            
            margin_style = ""
            if offset:
                margin_left = max(0, offset[0])
                margin_right = max(0, -offset[0])
                margin_style = "margin-left: {}px; margin-right: {}px;".format(margin_left, margin_right)
            
            btn.setStyleSheet("""
                QPushButton {{ border: none; background: transparent; {} }}
                QPushButton:hover {{ background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }}
                QPushButton:pressed {{ background-color: rgba(255,255,255,100); border-radius: 8px; }}
                QPushButton::menu-indicator {{ width: 0; height: 0; }}
            """.format(margin_style))
            
            if menu_options:
                # Create popup menu for this button
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                btn.setMenu(btn_menu)
                # Enable right-click to show same menu
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            else:
                if i == 17:
                    def tools_editor_wip():
                        cmds.inViewMessage(
                            amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                            pos='midCenter', fade=True, fadeStayTime=2000
                        )
                    btn.clicked.connect(tools_editor_wip)
                elif i == 4:
                    def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                        mods = cmds.getModifiers()
                        if mods == 4:
                            run_tracify_arc_track()
                        else:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    btn.clicked.connect(tracify_click_handler)
                else:
                    btn.clicked.connect(
                        lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                        bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    )
            
            if i == 5:
                self.selection_counter = selection_counter.SelectionCounter()
                self.selection_counter.set_scaled_size(style.scaled)
                icon_layout.addWidget(self.selection_counter)
            icon_layout.addWidget(btn)
        
        # Dock mode button at the very bottom
        dock_btn = QtWidgets.QPushButton()
        dock_btn.setFixedSize(int(style.ICON_WIDTH * 1.01), int(style.ICON_HEIGHT * 1.01))
        dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
        dock_btn.setIconSize(QtCore.QSize(int(style.ICON_WIDTH * 1.01) - 2, int(style.ICON_HEIGHT * 1.01) - 2))
        dock_btn.setToolTip("Dock Position")
        dock_btn.installEventFilter(_tooltip_filter)
        dock_btn.setFlat(True)
        dock_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }
        """)
        
        # Layout: [small spacer] [stretch] [icons] [stretch] [dock]
        # Small top spacer to offset icons slightly higher than center
        top_spacer = QtWidgets.QWidget()
        top_spacer.setFixedHeight(8)
        layout.addWidget(top_spacer)
        layout.addStretch(2)
        layout.addWidget(icon_container, 0, QtCore.Qt.AlignCenter)
        layout.addStretch(3)  # Slightly larger bottom stretch pushes icons up a bit
        layout.addWidget(dock_btn, 0, QtCore.Qt.AlignCenter)
        
        # Create popup menu
        dock_menu = QtWidgets.QMenu(dock_btn)
        dock_menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; }
            QMenu::item:disabled { color: #666; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        
        # Refresh menu items every time it's about to show
        def refresh_qt_menu():
            dock_menu.clear()
            reset_action = dock_menu.addAction("Reset Animo")
            reset_action.triggered.connect(lambda: self._resetUI())
            shelf_action = dock_menu.addAction("Add Animo to Shelf")
            shelf_action.triggered.connect(lambda: self._addToShelf())
            dock_menu.addSeparator()
            tooltip_action = QAction("Show Tool Tips", dock_menu)
            tooltip_action.setCheckable(True)
            tooltip_action.setChecked(_get_tooltip_pref())
            def toggle_tooltips(checked):
                global _tooltip_manager
                _set_tooltip_pref(checked)
                if _tooltip_manager:
                    _tooltip_manager.set_enabled(checked)
                if checked:
                    cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                else:
                    cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
            tooltip_action.triggered.connect(toggle_tooltips)
            dock_menu.addAction(tooltip_action)
            center_pivot_action = QAction("Keep Selections at Center", dock_menu)
            center_pivot_action.setCheckable(True)
            center_pivot_action.setChecked(_is_center_pivot_active())
            def toggle_center_pivot_1(checked):
                _toggle_center_pivot(checked)
            center_pivot_action.triggered.connect(toggle_center_pivot_1)
            dock_menu.addAction(center_pivot_action)

        
        if insert_parent.__class__.__name__ == 'QSplitter':
            idx = insert_parent.indexOf(insert_widget)
            if insert_side == 'left':
                insert_parent.insertWidget(idx, self.qt_toolbar)
            else:
                insert_parent.insertWidget(idx + 1, self.qt_toolbar)
        else:
            parent_layout = insert_parent.layout()
            idx = parent_layout.indexOf(insert_widget)
            if idx >= 0:
                if insert_side == 'left':
                    parent_layout.insertWidget(idx, self.qt_toolbar)
                else:
                    parent_layout.insertWidget(idx + 1, self.qt_toolbar)
            else:
                parent_layout.addWidget(self.qt_toolbar)
        
        self.qt_toolbar.show()
    
    def _buildSideFallback(self, target):
        """Fallback to workspaceControl for side dock modes"""
        if target == 'channelbox':
            cmds.workspaceControl(WorkspaceName, l="", iw=style.TOOLBAR_WIDTH, mw=style.TOOLBAR_WIDTH,
                li=True, wp="fixed", floating=False, retain=False, collapse=False,
                dockToMainWindow=["right", True])
            try:
                CHAN_BOX = mel.eval('getUIComponentDockControl("Channel Box / Layer Editor", false)')
                if CHAN_BOX:
                    cmds.workspaceControl(WorkspaceName, edit=True, dtc=(CHAN_BOX, "left"))
            except:
                pass
        else:  # toolbox
            cmds.workspaceControl(WorkspaceName, l="", iw=style.TOOLBAR_WIDTH, mw=style.TOOLBAR_WIDTH,
                li=True, wp="fixed", floating=False, retain=False, collapse=False,
                dockToMainWindow=["left", True])
            try:
                cmds.workspaceControl(WorkspaceName, edit=True, dtc=("ToolBox", "right"))
            except:
                pass
        
        cmds.workspaceControl(WorkspaceName, edit=True, resizeWidth=style.TOOLBAR_WIDTH)
        self.buildUI(False)
        try:
            workspace_ptr = mui.MQtUtil.findControl(WorkspaceName)
            if workspace_ptr:
                workspace_widget = wrapInstance(int(workspace_ptr), QtWidgets.QWidget)
                workspace_widget.setFixedWidth(style.TOOLBAR_WIDTH)
        except:
            pass
        
        # Layout nudge - force refresh by temporarily resizing
        self._layoutNudge(target)
    
    def _layoutNudge(self, target):
        """Force layout refresh by temporarily nudging the workspace size"""
        def do_nudge():
            try:
                # Nudge wider
                cmds.workspaceControl(WorkspaceName, edit=True, resizeWidth=style.TOOLBAR_WIDTH + 30)
            except:
                pass
        
        def revert_nudge():
            try:
                # Revert to original
                cmds.workspaceControl(WorkspaceName, edit=True, resizeWidth=style.TOOLBAR_WIDTH)
            except:
                pass
        
        # Schedule nudge and revert
        QtCore.QTimer.singleShot(100, do_nudge)
        QtCore.QTimer.singleShot(250, revert_nudge)
    
    def buildTimelineUI(self, position='top'):
        """Build a pure Qt toolbar above the timeline - no titlebar"""
        
        # Clean up existing Qt toolbar
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
            except:
                pass
        
        # Delete any existing workspaceControl
        if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        
        # Clean up old toolbar styles
        if cmds.toolBar("animo_timeline_toolbar", query=True, exists=True):
            cmds.deleteUI("animo_timeline_toolbar")
        if cmds.window("animo_toolbar_win", query=True, exists=True):
            cmds.deleteUI("animo_toolbar_win")
        
        # Get the playback slider via MEL - this is the actual timeline widget
        time_slider_widget = None
        try:
            time_slider_name = mel.eval('$tmpVar=$gPlayBackSlider')
            if time_slider_name:
                ptr = mui.MQtUtil.findControl(time_slider_name)
                if ptr:
                    time_slider_widget = wrapInstance(int(ptr), QtWidgets.QWidget)
        except:
            pass
        
        if not time_slider_widget:
            cmds.warning("Animo: Could not find TimeSlider")
            return
        
        # Walk up from timeline widget to find QSplitter parent
        splitter = None
        timeline_container = None
        
        current = time_slider_widget
        for level in range(15):
            parent = current.parent()
            if not parent:
                break
            
            if parent.__class__.__name__ == 'QSplitter':
                splitter = parent
                timeline_container = current
                break
            
            current = parent
        
        if not splitter or not timeline_container:
            cmds.warning("Animo: Could not find QSplitter parent")
            return
        
        # Get timeline container's index in splitter
        timeline_idx = splitter.indexOf(timeline_container)
        if timeline_idx < 0:
            cmds.warning("Animo: Could not find timeline index in splitter")
            return
        
        initial_height = style.TOOLBAR_HEIGHT
        if _get_show_all_sliders_pref():
            initial_height += style.scaled(28)
        
        self.qt_toolbar = QtWidgets.QWidget()
        self.qt_toolbar.setObjectName("animo_qt_toolbar")
        self.qt_toolbar.setFixedHeight(initial_height)
        self.qt_toolbar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.qt_toolbar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qt_toolbar.customContextMenuRequested.connect(self._showToolbarContextMenu)
        
        bg_color = "rgb({}, {}, {})".format(
            int(style.TOOLBAR_BG_COLOR_LIGHT[0] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[1] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[2] * 255)
        )
        self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }} {}".format(bg_color, TOOLTIP_STYLE))
        
        self._buildTimelineToolbarContent(self.qt_toolbar)
        
        self._splitter = splitter
        self._last_toolbar_height = initial_height
        
        if position == 'bottom':
            splitter.insertWidget(timeline_idx + 1, self.qt_toolbar)
        else:
            splitter.insertWidget(timeline_idx, self.qt_toolbar)
        
        self.qt_toolbar.show()
        
        self._adjustSplitterForToolbar(splitter, self.qt_toolbar)
    
    def _adjustSplitterForToolbar(self, splitter, toolbar_widget):
        try:
            toolbar_idx = splitter.indexOf(toolbar_widget)
            if toolbar_idx >= 0:
                sizes = splitter.sizes()
                toolbar_size = sizes[toolbar_idx]
                
                target_height = style.TOOLBAR_HEIGHT
                if _get_show_all_sliders_pref():
                    target_height += style.scaled(28)
                
                if toolbar_size > target_height and toolbar_idx > 0:
                    excess = toolbar_size - target_height
                    sizes[toolbar_idx - 1] += excess
                    sizes[toolbar_idx] = target_height
                    splitter.setSizes(sizes)
        except:
            pass
    
    def _buildTimelineToolbarContent(self, parent_widget):
        """Build the toolbar content widgets"""
        
        wrap_icons_enabled = _get_wrap_icons_pref()
        
        main_vbox = QtWidgets.QVBoxLayout(parent_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)
        
        toolbar_row = QtWidgets.QWidget()
        toolbar_row.setStyleSheet("background: transparent;")
        layout = QtWidgets.QHBoxLayout(toolbar_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        all_sliders_row = create_all_sliders_container()
        all_sliders_row.setStyleSheet("background: rgba(0, 0, 0, 10);")
        
        main_vbox.addWidget(toolbar_row)
        main_vbox.addWidget(all_sliders_row)
        
        icon_container = QtWidgets.QWidget()
        icon_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        icon_layout = QtWidgets.QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(bar.ICON_SPACING_WITHIN_GROUP)
        icon_layout.setAlignment(QtCore.Qt.AlignVCenter)
        
        icon_groups = [
            [0, 1, 2],
            [5, 3, 4],
            [6, 7, 8, 9],
            [10, 11, 12],
        ]
        
        group_spacing = bar.GROUP_SPACING
        
        self._icon_buttons = []
        
        def create_icon_button(icon_data, icon_index=None):
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            offset = icon_data[6] if len(icon_data) > 6 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            icon_path = self.getImage(icon_file)
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(icon_path))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            
            btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                QPushButton::menu-indicator { width: 0; height: 0; }
            """)
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                btn_menu.addSeparator()
                shelf_submenu = btn_menu.addMenu("Add to Shelf")
                shelf_submenu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                hotkey_submenu = btn_menu.addMenu("Assign Hotkey")
                hotkey_submenu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name != "---":
                        shelf_action = shelf_submenu.addAction(option_name)
                        shelf_action.triggered.connect(
                            lambda checked=False, ip=icon_path, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                            shelf.add_tool_to_shelf(ip, tn, ln, tf, None)
                        )
                        hotkey_action = hotkey_submenu.addAction(option_name)
                        hotkey_action.triggered.connect(
                            lambda checked=False, ip=icon_path, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                            shelf.assign_hotkey_to_tool(ip, tn, ln, tf, None)
                        )
                btn.setMenu(btn_menu)
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            else:
                if i == 17:
                    def tools_editor_wip():
                        cmds.inViewMessage(
                            amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                            pos='midCenter', fade=True, fadeStayTime=2000
                        )
                    btn.clicked.connect(tools_editor_wip)
                elif i == 4:
                    def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                        mods = cmds.getModifiers()
                        if mods == 4:
                            run_tracify_arc_track()
                        else:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    btn.clicked.connect(tracify_click_handler)
                else:
                    btn.clicked.connect(
                        lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                        bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    )
                # Add right-click context menu - skip for About icon
                if icon_file != "about_icon.png":
                    if launcher_name == "temp_pivot_launcher":
                        # Special context menu for temp_pivot with Reset Pivot option
                        def create_temp_pivot_menu(button, ip, tt, ln, tf, ef):
                            button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                            def show_menu(pos):
                                menu = QtWidgets.QMenu(button)
                                menu.setStyleSheet('''
                                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                                    QMenu::item { padding: 6px 25px; color: #ccc; }
                                    QMenu::item:selected { background-color: #555; color: #fff; }
                                ''')
                                reset_action = menu.addAction("Reset Pivot")
                                reset_action.triggered.connect(
                                    lambda: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, "reset_pivot", "Animo_Temp_Pivot", None)
                                )
                                menu.addSeparator()
                                shelf_submenu = menu.addMenu("Add to Shelf")
                                shelf_submenu.setStyleSheet('''
                                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                                    QMenu::item { padding: 6px 25px; color: #ccc; }
                                    QMenu::item:selected { background-color: #555; color: #fff; }
                                ''')
                                shelf_temp_pivot = shelf_submenu.addAction("Temp Pivot")
                                shelf_temp_pivot.triggered.connect(lambda: shelf.add_tool_to_shelf(ip, tt, ln, tf, ef))
                                shelf_reset_pivot = shelf_submenu.addAction("Reset Pivot")
                                shelf_reset_pivot.triggered.connect(lambda: shelf.add_tool_to_shelf(ip, "Reset Pivot", "reset_pivot", "Animo_Temp_Pivot", None))
                                hotkey_submenu = menu.addMenu("Assign Hotkey")
                                hotkey_submenu.setStyleSheet('''
                                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                                    QMenu::item { padding: 6px 25px; color: #ccc; }
                                    QMenu::item:selected { background-color: #555; color: #fff; }
                                ''')
                                hotkey_temp_pivot = hotkey_submenu.addAction("Temp Pivot")
                                hotkey_temp_pivot.triggered.connect(lambda: shelf.assign_hotkey_to_tool(ip, tt, ln, tf, ef))
                                hotkey_reset_pivot = hotkey_submenu.addAction("Reset Pivot")
                                hotkey_reset_pivot.triggered.connect(lambda: shelf.assign_hotkey_to_tool(ip, "Reset Pivot", "reset_pivot", "Animo_Temp_Pivot", None))
                                menu.exec_(button.mapToGlobal(pos))
                            button.customContextMenuRequested.connect(show_menu)
                        create_temp_pivot_menu(btn, icon_path, tooltip, launcher_name, tool_folder, entry_func)
                    else:
                        shelf.create_shelf_context_menu(btn, icon_path, tooltip, launcher_name, tool_folder, entry_func)
            
            # Store icon index for edit mode dragging
            if icon_index is not None:
                btn._icon_index = icon_index
                btn.installEventFilter(self._draggable_filter)
                self._icon_buttons.append((btn, icon_index))
            
            # Register with tooltip manager
            if _tooltip_manager:
                # Use launcher_name if available, otherwise map by index
                tooltip_key = launcher_name
                if not tooltip_key and icon_index is not None:
                    # Fallback map for icons without launcher_name
                    tooltip_fallback_map = {
                        20: "fast_bake_launcher",  # Fast Bake
                    }
                    tooltip_key = tooltip_fallback_map.get(icon_index)
                if tooltip_key:
                    _tooltip_manager.register_button(btn, tooltip_key, icon_path)
            
            return btn
        
        # Create SelectOpposite button (index 22) - positioned before selection counter
        selopp_data = bar.ICON_DATA[22]
        selopp_icon_file = selopp_data[0]
        selopp_tooltip = selopp_data[1]
        selopp_tool_folder = selopp_data[3]
        selopp_size = selopp_data[5] if len(selopp_data) > 5 and selopp_data[5] else None
        selopp_menu_options = selopp_data[7] if len(selopp_data) > 7 else None
        
        selopp_w = style.scaled(selopp_size[0]) if selopp_size else style.ICON_WIDTH
        selopp_h = style.scaled(selopp_size[1]) if selopp_size else style.ICON_HEIGHT
        
        selopp_icon_path = os.path.normpath(os.path.join(ANIMO_DATA_PATH, selopp_tool_folder, selopp_icon_file))
        
        selopp_btn = QtWidgets.QPushButton()
        selopp_btn.setFixedSize(selopp_w + 2, selopp_h + 2)
        selopp_btn.setIcon(QtGui.QIcon(selopp_icon_path))
        selopp_btn.setIconSize(QtCore.QSize(selopp_w, selopp_h))
        selopp_btn.setToolTip(selopp_tooltip)
        selopp_btn.installEventFilter(_tooltip_filter)
        selopp_btn.setFlat(True)
        selopp_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
            QPushButton::menu-indicator { width: 0; height: 0; }
        """)
        
        if selopp_menu_options:
            selopp_menu = QtWidgets.QMenu(selopp_btn)
            selopp_menu.setStyleSheet('''
                QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                QMenu::item { padding: 6px 25px; color: #ccc; }
                QMenu::item:selected { background-color: #555; color: #fff; }
            ''')
            for menu_item in selopp_menu_options:
                option_name = menu_item[0]
                option_launcher = menu_item[1]
                option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                action = selopp_menu.addAction(option_name)
                action.triggered.connect(
                    lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                    bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                )
            selopp_menu.addSeparator()
            selopp_shelf_submenu = selopp_menu.addMenu("Add to Shelf")
            selopp_shelf_submenu.setStyleSheet('''
                QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                QMenu::item { padding: 6px 25px; color: #ccc; }
                QMenu::item:selected { background-color: #555; color: #fff; }
            ''')
            selopp_hotkey_submenu = selopp_menu.addMenu("Assign Hotkey")
            selopp_hotkey_submenu.setStyleSheet('''
                QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                QMenu::item { padding: 6px 25px; color: #ccc; }
                QMenu::item:selected { background-color: #555; color: #fff; }
            ''')
            for menu_item in selopp_menu_options:
                option_name = menu_item[0]
                option_launcher = menu_item[1]
                option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                shelf_action = selopp_shelf_submenu.addAction(option_name)
                shelf_action.triggered.connect(
                    lambda checked=False, ip=selopp_icon_path, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                    shelf.add_tool_to_shelf(ip, tn, ln, tf, None)
                )
                hotkey_action = selopp_hotkey_submenu.addAction(option_name)
                hotkey_action.triggered.connect(
                    lambda checked=False, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                    shelf.assign_hotkey_dialog(tn, ln, tf, None)
                )
            selopp_btn.setMenu(selopp_menu)
            selopp_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            selopp_btn.customContextMenuRequested.connect(lambda pos: selopp_menu.exec_(selopp_btn.mapToGlobal(pos)))
        
        # Store icon index for edit mode dragging
        selopp_btn._icon_index = 21
        selopp_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((selopp_btn, 21))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(selopp_btn, "SelectOppositeCtrls", selopp_icon_path)
        
        # Create selection counter widget
        self.selection_counter = selection_counter.SelectionCounter()
        self.selection_counter.set_scaled_size(style.scaled)
        
        # Add grouped icons
        for group_idx, group in enumerate(icon_groups):
            # Add SelectOpposite and selection counter before pickify group (after transify group)
            if group_idx == 1:
                icon_layout.addWidget(selopp_btn)
                icon_layout.addSpacing(4)
                icon_layout.addWidget(self.selection_counter)
                icon_layout.addSpacing(group_spacing)
            
            # Special handling for global_offset/twosify/vectorify group (index 3) - tighter spacing
            if group_idx == 3:
                sub_container = QtWidgets.QWidget()
                sub_layout = QtWidgets.QHBoxLayout(sub_container)
                sub_layout.setContentsMargins(0, 0, 0, 0)
                sub_layout.setSpacing(0)
                for i in group:
                    if i < len(bar.ICON_DATA):
                        icon_data = bar.ICON_DATA[i]
                        icon_file = icon_data[0]
                        tooltip = icon_data[1]
                        launcher_name = icon_data[2]
                        tool_folder = icon_data[3]
                        entry_func = icon_data[4]
                        custom_size = icon_data[5] if len(icon_data) > 5 else None
                        
                        icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
                        icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
                        icon_path = self.getImage(icon_file)
                        
                        btn = QtWidgets.QPushButton()
                        btn.setFixedSize(icon_w + 2, icon_h + 2)  # Reduced padding from +6 to +2
                        btn.setIcon(QtGui.QIcon(icon_path))
                        btn.setIconSize(QtCore.QSize(icon_w, icon_h))
                        btn.setToolTip(tooltip)
                        btn.installEventFilter(_tooltip_filter)
                        btn.setFlat(True)
                        
                        btn.setStyleSheet("""
                            QPushButton { border: none; background: transparent; }
                            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                        """)
                        btn.clicked.connect(
                            lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                        )
                        shelf.create_shelf_context_menu(btn, icon_path, tooltip, launcher_name, tool_folder, entry_func)
                        
                        # Store icon index for edit mode dragging
                        btn._icon_index = i
                        btn.installEventFilter(self._draggable_filter)
                        self._icon_buttons.append((btn, i))
                        
                        # Register with tooltip manager
                        if _tooltip_manager and launcher_name:
                            _tooltip_manager.register_button(btn, launcher_name, icon_path)
                        
                        sub_layout.addWidget(btn)
                icon_layout.addWidget(sub_container)
            else:
                for idx_in_group, i in enumerate(group):
                    if i < len(bar.ICON_DATA):
                        btn = create_icon_button(bar.ICON_DATA[i], i)
                        icon_layout.addWidget(btn)
            
            # Add spacing after each group except the last
            if group_idx < len(icon_groups) - 1:
                icon_layout.addSpacing(group_spacing)
        
        # Set fixed size on icon_container after all icons are added (like sliders use setFixedWidth)
        icon_container.adjustSize()
        icon_container.setFixedSize(icon_container.sizeHint())
        
        # Create tangent icon buttons container (indices 13, 14, 15)
        tangent_indices = [13, 14, 15]
        tangent_container = QtWidgets.QWidget()
        tangent_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        tangent_layout = QtWidgets.QHBoxLayout(tangent_container)
        tangent_layout.setContentsMargins(4, 0, 0, 0)  # Left margin to prevent icon clipping
        tangent_layout.setSpacing(0)
        
        # Map tangent indices to global script names
        tangent_global_scripts = {
            13: "auto_tangent_global",
            14: "linear_tangent_global",
            15: "step_tangent_global"
        }
        
        # Map tangent indices to launcher names for "Selected" and "All Keys" options
        tangent_launcher_map = {
            13: {"selected": "auto_current_launcher", "all": "auto_all_launcher"},
            14: {"selected": "linear_current_launcher", "all": "linear_all_launcher"},
            15: {"selected": "step_current_launcher", "all": "step_all_launcher"}
        }
        
        for i in tangent_indices:
            icon_data = bar.ICON_DATA[i]
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            # Get full icon path for shelf
            tangent_icon_path = self.getImage(icon_file)
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(tangent_icon_path))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            
            btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                QPushButton::menu-indicator { width: 0; height: 0; }
            """)
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                
                # Add "Apply Maya Global Tangents" option after Selected
                if i in tangent_global_scripts:
                    global_script = tangent_global_scripts[i]
                    btn_menu.addSeparator()
                    global_action = btn_menu.addAction("Apply Maya Global Tangents")
                    global_action.triggered.connect(
                        lambda checked=False, gs=global_script:
                        run_global_tangent(gs)
                    )
                
                btn_menu.addSeparator()
                tangent_shelf_submenu = btn_menu.addMenu("Add to Shelf")
                tangent_shelf_submenu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                tangent_hotkey_submenu = btn_menu.addMenu("Assign Hotkey")
                tangent_hotkey_submenu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name != "---":
                        shelf_action = tangent_shelf_submenu.addAction(option_name)
                        shelf_action.triggered.connect(
                            lambda checked=False, ip=tangent_icon_path, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                            shelf.add_tool_to_shelf(ip, tn, ln, tf, None)
                        )
                        hotkey_action = tangent_hotkey_submenu.addAction(option_name)
                        hotkey_action.triggered.connect(
                            lambda checked=False, ip=tangent_icon_path, tn=option_name, ln=option_launcher, tf=option_tool_folder:
                            shelf.assign_hotkey_to_tool(ip, tn, ln, tf, None)
                        )
                
                # Add global tangent to shelf/hotkey submenus
                if i in tangent_global_scripts:
                    global_script = tangent_global_scripts[i]
                    global_shelf_action = tangent_shelf_submenu.addAction("Apply Maya Global Tangents")
                    global_shelf_action.triggered.connect(
                        lambda checked=False, ip=tangent_icon_path, gs=global_script:
                        shelf.add_tool_to_shelf(ip, "Apply Maya Global Tangents", gs, "Animo_Keys_Tangent", None)
                    )
                    global_hotkey_action = tangent_hotkey_submenu.addAction("Apply Maya Global Tangents")
                    global_hotkey_action.triggered.connect(
                        lambda checked=False, ip=tangent_icon_path, gs=global_script:
                        shelf.assign_hotkey_to_tool(ip, "Apply Maya Global Tangents", gs, "Animo_Keys_Tangent", None)
                    )
                
                # Store menu reference on button for modifier click handling
                btn._tangent_menu = btn_menu
                btn._tangent_index = i
                btn._tangent_launchers = tangent_launcher_map.get(i, {})
                
                # Custom click handler that checks modifiers
                def tangent_click_handler(checked=False, button=btn):
                    mods = cmds.getModifiers()
                    idx = button._tangent_index
                    launchers = button._tangent_launchers
                    if mods == 4:  # Ctrl (Cmd on Mac)
                        # Run "Selected" option
                        if "selected" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["selected"], None, None)
                    elif mods == 13:  # Ctrl+Alt+Shift (Cmd+Option+Shift on Mac)
                        # Run "All Keys" option
                        if "all" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["all"], None, None)
                    else:
                        # Show menu
                        button._tangent_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                
                btn.clicked.connect(tangent_click_handler)
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            
            # Store icon index for edit mode dragging
            btn._icon_index = i
            btn.installEventFilter(self._draggable_filter)
            self._icon_buttons.append((btn, i))
            
            # Register with tooltip manager - use icon file name to derive tooltip key
            if _tooltip_manager:
                # Map tangent icon indices to tooltip keys
                tangent_tooltip_map = {
                    13: "auto_tangent",
                    14: "linear_tangent", 
                    15: "step_tangent"
                }
                tooltip_key = tangent_tooltip_map.get(i)
                if tooltip_key:
                    _tooltip_manager.register_button(btn, tooltip_key, tangent_icon_path)
            
            tangent_layout.addWidget(btn)
        tangent_container.adjustSize()
        tangent_container.setFixedSize(tangent_container.sizeHint())
        
        # Create tools icons container (tools_editor, quick_exporter, playblaster) - indices 17, 16, 23
        tools_indices = [17, 16, 23]
        tools_container = QtWidgets.QWidget()
        tools_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        tools_layout = QtWidgets.QHBoxLayout(tools_container)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(0)
        for i in tools_indices:
            if i < len(bar.ICON_DATA):
                btn = create_icon_button(bar.ICON_DATA[i], i)
                tools_layout.addWidget(btn)
        tools_container.adjustSize()
        tools_container.setFixedSize(tools_container.sizeHint())
        
        # Create left slider icons container (reset, bake, share_keys)
        left_slider_indices = [19, 20, 21]
        left_slider_container = QtWidgets.QWidget()
        left_slider_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        left_slider_layout = QtWidgets.QHBoxLayout(left_slider_container)
        left_slider_layout.setContentsMargins(0, 0, 0, 0)
        left_slider_layout.setSpacing(bar.LEFT_SLIDER_SPACING)
        for i in left_slider_indices:
            if i < len(bar.ICON_DATA):
                btn = create_icon_button(bar.ICON_DATA[i], i)
                left_slider_layout.addWidget(btn)
        left_slider_container.adjustSize()
        left_slider_container.setFixedSize(left_slider_container.sizeHint())
        
        # Create sliders
        tween_slider = AnimoSlider("TW", (225, 175, 45), "tween")
        tween_slider.setMinimum(-100)
        tween_slider.setMaximum(100)
        tween_slider.setValue(0)
        tween_slider.setFixedWidth(style.scaled(200))
        
        blend_slider = AnimoSlider("BN", (220, 140, 60), "blend")
        blend_slider.setMinimum(-100)
        blend_slider.setMaximum(100)
        blend_slider.setValue(0)
        blend_slider.setFixedWidth(style.scaled(200))
        
        scale_slider = AnimoSlider("SL", (100, 180, 220), "scale")
        scale_slider.setMinimum(-100)
        scale_slider.setMaximum(100)
        scale_slider.setValue(0)
        scale_slider.setFixedWidth(style.scaled(200))
        
        cascade_slider = AnimoSlider("CA", (180, 120, 200), "cascade")
        cascade_slider.setMinimum(0)
        cascade_slider.setMaximum(200)
        cascade_slider.setValue(100)
        cascade_slider.setFixedWidth(style.scaled(200))
        
        # Register sliders with tooltip manager (1 second delay)
        if _tooltip_manager:
            _tooltip_manager.register_button(tween_slider, "tween_slider", None, hover_delay=1000)
            _tooltip_manager.register_button(blend_slider, "blend_slider", None, hover_delay=1000)
            _tooltip_manager.register_button(scale_slider, "scale_slider", None, hover_delay=1000)
            _tooltip_manager.register_button(cascade_slider, "cascade_slider", None, hover_delay=1000)
        
        # SmoothSelectedKeys button (index 26 in ICON_DATA)
        smooth_data = bar.ICON_DATA[26]
        smooth_icon_file = smooth_data[0]
        smooth_tooltip = smooth_data[1]
        smooth_launcher = smooth_data[2]
        smooth_tool_folder = smooth_data[3]
        smooth_size = smooth_data[5] if len(smooth_data) > 5 and smooth_data[5] else None
        
        smooth_w = int((style.scaled(smooth_size[0]) if smooth_size else style.ICON_WIDTH) * 0.99)
        smooth_h = int((style.scaled(smooth_size[1]) if smooth_size else style.ICON_HEIGHT) * 0.99)
        
        smooth_icon_path = os.path.normpath(os.path.join(ANIMO_DATA_PATH, smooth_tool_folder, smooth_icon_file))
        
        smooth_btn = QtWidgets.QPushButton()
        smooth_btn.setFixedSize(smooth_w + 2, smooth_h + 2)
        smooth_btn.setIcon(QtGui.QIcon(smooth_icon_path))
        smooth_btn.setIconSize(QtCore.QSize(smooth_w, smooth_h))
        smooth_btn.setToolTip(smooth_tooltip)
        smooth_btn.installEventFilter(_tooltip_filter)
        smooth_btn.setFlat(True)
        smooth_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
        """)
        smooth_btn.clicked.connect(run_smooth_keys_plugin)
        create_smooth_context_menu(smooth_btn, smooth_icon_path)
        
        smooth_btn._icon_index = 25
        smooth_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((smooth_btn, 25))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(smooth_btn, "SmoothSelectedKeys", smooth_icon_path)
        
        # SmartSnapKeys button (index 27 in ICON_DATA)
        snap_data = bar.ICON_DATA[27]
        snap_icon_file = snap_data[0]
        snap_tooltip = snap_data[1]
        snap_launcher = snap_data[2]
        snap_tool_folder = snap_data[3]
        snap_size = snap_data[5] if len(snap_data) > 5 and snap_data[5] else None
        
        snap_w = int((style.scaled(snap_size[0]) if snap_size else style.ICON_WIDTH) * 0.99)
        snap_h = int((style.scaled(snap_size[1]) if snap_size else style.ICON_HEIGHT) * 0.99)
        
        snap_icon_path = os.path.normpath(os.path.join(ANIMO_DATA_PATH, snap_tool_folder, snap_icon_file))
        
        snap_btn = QtWidgets.QPushButton()
        snap_btn.setFixedSize(snap_w + 2, snap_h + 2)
        snap_btn.setIcon(QtGui.QIcon(snap_icon_path))
        snap_btn.setIconSize(QtCore.QSize(snap_w, snap_h))
        snap_btn.setToolTip(snap_tooltip)
        snap_btn.installEventFilter(_tooltip_filter)
        snap_btn.setFlat(True)
        snap_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
        """)
        snap_btn.clicked.connect(
            lambda: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, snap_launcher, snap_tool_folder, None)
        )
        shelf.create_shelf_context_menu(snap_btn, snap_icon_path, snap_tooltip, snap_launcher, snap_tool_folder, None)
        
        snap_btn._icon_index = 26
        snap_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((snap_btn, 26))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(snap_btn, "SmartSnapKeys", snap_icon_path)
        
        # CropAnimation button (index 24 in ICON_DATA)
        crop_data = bar.ICON_DATA[24]
        crop_icon_file = crop_data[0]
        crop_tooltip = crop_data[1]
        crop_launcher = crop_data[2]
        crop_tool_folder = crop_data[3]
        crop_size = crop_data[5] if len(crop_data) > 5 and crop_data[5] else None
        
        crop_w = int((style.scaled(crop_size[0]) if crop_size else style.ICON_WIDTH) * 0.99)
        crop_h = int((style.scaled(crop_size[1]) if crop_size else style.ICON_HEIGHT) * 0.99)
        
        # Icon is in tool folder, not icons folder
        crop_icon_path = os.path.normpath(os.path.join(ANIMO_DATA_PATH, crop_tool_folder, crop_icon_file))
        
        crop_btn = QtWidgets.QPushButton()
        crop_btn.setFixedSize(crop_w + 2, crop_h + 2)
        crop_btn.setIcon(QtGui.QIcon(crop_icon_path))
        crop_btn.setIconSize(QtCore.QSize(crop_w, crop_h))
        crop_btn.setToolTip(crop_tooltip)
        crop_btn.installEventFilter(_tooltip_filter)
        crop_btn.setFlat(True)
        crop_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
        """)
        crop_btn.clicked.connect(
            lambda: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, crop_launcher, crop_tool_folder, None)
        )
        # Add right-click "Add to Shelf" for crop
        shelf.create_shelf_context_menu(crop_btn, crop_icon_path, crop_tooltip, crop_launcher, crop_tool_folder, None)
        
        # Store icon index for edit mode dragging
        crop_btn._icon_index = 23
        crop_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((crop_btn, 23))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(crop_btn, "CropAnimation", crop_icon_path)
        
        # DeleteRedundantKeys button (index 25 in ICON_DATA)
        delkeys_data = bar.ICON_DATA[25]
        delkeys_icon_file = delkeys_data[0]
        delkeys_tooltip = delkeys_data[1]
        delkeys_launcher = delkeys_data[2]
        delkeys_tool_folder = delkeys_data[3]
        delkeys_size = delkeys_data[5] if len(delkeys_data) > 5 and delkeys_data[5] else None
        
        delkeys_w = int((style.scaled(delkeys_size[0]) if delkeys_size else style.ICON_WIDTH) * 0.99)
        delkeys_h = int((style.scaled(delkeys_size[1]) if delkeys_size else style.ICON_HEIGHT) * 0.99)
        
        # Icon is in tool folder, not icons folder
        delkeys_icon_path = os.path.normpath(os.path.join(ANIMO_DATA_PATH, delkeys_tool_folder, delkeys_icon_file))
        
        delkeys_btn = QtWidgets.QPushButton()
        delkeys_btn.setFixedSize(delkeys_w + 2, delkeys_h + 2)
        delkeys_btn.setIcon(QtGui.QIcon(delkeys_icon_path))
        delkeys_btn.setIconSize(QtCore.QSize(delkeys_w, delkeys_h))
        delkeys_btn.setToolTip(delkeys_tooltip)
        delkeys_btn.installEventFilter(_tooltip_filter)
        delkeys_btn.setFlat(True)
        delkeys_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
        """)
        delkeys_btn.clicked.connect(
            lambda: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, delkeys_launcher, delkeys_tool_folder, None)
        )
        # Add right-click "Add to Shelf" for delkeys
        shelf.create_shelf_context_menu(delkeys_btn, delkeys_icon_path, delkeys_tooltip, delkeys_launcher, delkeys_tool_folder, None)
        
        # Store icon index for edit mode dragging
        delkeys_btn._icon_index = 24
        delkeys_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((delkeys_btn, 24))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(delkeys_btn, "DeleteRedundantKeys", delkeys_icon_path)
        
        # About button - next to dock
        about_small_size = int(style.scaled(22) * 0.99)
        
        about_btn = QtWidgets.QPushButton()
        about_btn.setFixedSize(about_small_size + 2, about_small_size + 2)
        about_btn.setIcon(QtGui.QIcon(self.getImage("about_icon.png")))
        about_btn.setIconSize(QtCore.QSize(about_small_size, about_small_size))
        about_btn.setToolTip("About")
        about_btn.installEventFilter(_tooltip_filter)
        about_btn.setFlat(True)
        about_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
        """)
        about_btn.clicked.connect(
            lambda: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, "about_launcher", None, None)
        )
        about_icon_path = self.getImage("about_icon.png")
        shelf.create_shelf_context_menu(about_btn, about_icon_path, "About", "about_launcher", None, None)
        
        # Store icon index for edit mode dragging
        about_btn._icon_index = 17
        about_btn.installEventFilter(self._draggable_filter)
        self._icon_buttons.append((about_btn, 17))
        
        # Register with tooltip manager
        if _tooltip_manager:
            _tooltip_manager.register_button(about_btn, "about_launcher", about_icon_path)
        
        # Dock mode button - smaller size
        dock_btn = QtWidgets.QPushButton()
        dock_small_size = style.scaled(23)
        dock_btn.setFixedSize(int((dock_small_size + 2) * 1.01), int((dock_small_size + 2) * 1.01))
        dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
        dock_btn.setIconSize(QtCore.QSize(int(dock_small_size * 1.01), int(dock_small_size * 1.01)))
        dock_btn.setToolTip("Dock Position")
        dock_btn.installEventFilter(_tooltip_filter)
        dock_btn.setFlat(True)
        dock_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; }
            QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
            QPushButton::menu-indicator { width: 0; height: 0; }
        """)
        
        dock_menu = QtWidgets.QMenu(dock_btn)
        dock_menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        dock_menu.addAction("Reset Animo", lambda: self._resetUI())
        dock_menu.addAction("Add Animo to Shelf", lambda: self._addToShelf())
        dock_menu.addSeparator()
        
        tooltip_action = QAction("Show Tool Tips", dock_menu)
        tooltip_action.setCheckable(True)
        tooltip_action.setChecked(_get_tooltip_pref())
        def toggle_tooltips_h(checked):
            global _tooltip_manager
            _set_tooltip_pref(checked)
            if _tooltip_manager:
                _tooltip_manager.set_enabled(checked)
            if checked:
                cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
            else:
                cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
        tooltip_action.triggered.connect(toggle_tooltips_h)
        dock_menu.addAction(tooltip_action)
        center_pivot_action = QAction("Keep Selections at Center", dock_menu)
        center_pivot_action.setCheckable(True)
        center_pivot_action.setChecked(_is_center_pivot_active())
        def toggle_center_pivot_h(checked):
            _toggle_center_pivot(checked)
        center_pivot_action.triggered.connect(toggle_center_pivot_h)
        dock_menu.addAction(center_pivot_action)
        

        dock_menu.addSeparator()
        size_action_h = dock_menu.addAction("Animo Size Settings...")
        size_action_h.triggered.connect(_show_size_settings)
        
        dock_btn.setMenu(dock_menu)
        dock_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        dock_btn.customContextMenuRequested.connect(lambda pos: dock_menu.exec_(dock_btn.mapToGlobal(pos)))
        
        TOOLBAR_CONTENT_WIDTH = style.scaled(bar.TOOLBAR_CONTENT_WIDTH)
        
        # Check if wrap icons mode is enabled
        wrap_icons_enabled = _get_wrap_icons_pref()
        
        # Create master container
        master_container = QtWidgets.QWidget()
        
        if wrap_icons_enabled:
            # Wrap mode: allow container to expand both ways and wrap content
            # Use Ignored for horizontal so it fills available space regardless of content
            master_container.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.MinimumExpanding)
            master_layout = FlowLayout(master_container, margin=4, h_spacing=6, v_spacing=4)
        else:
            # Fixed width with horizontal layout (default behavior)
            master_container.setFixedWidth(TOOLBAR_CONTENT_WIDTH)
            master_layout = QtWidgets.QHBoxLayout(master_container)
            master_layout.setContentsMargins(0, 0, 0, 0)
            master_layout.setSpacing(0)
        
        if wrap_icons_enabled:
            # With FlowLayout, add widgets directly (they will wrap)
            master_layout.addWidget(left_slider_container)
            master_layout.addWidget(tween_slider)
            master_layout.addWidget(blend_slider)
            master_layout.addWidget(tangent_container)
            master_layout.addWidget(icon_container)
            master_layout.addWidget(scale_slider)
            master_layout.addWidget(cascade_slider)
            master_layout.addWidget(tools_container)
            master_layout.addWidget(smooth_btn)
            master_layout.addWidget(snap_btn)
            master_layout.addWidget(crop_btn)
            master_layout.addWidget(delkeys_btn)
            master_layout.addWidget(about_btn)
            master_layout.addWidget(dock_btn)
        else:
            # Add all widgets to master container with spacing
            master_layout.addWidget(left_slider_container, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_LEFT_SLIDER_TO_TWEEN)
            master_layout.addWidget(tween_slider, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_TWEEN_TO_BLEND)
            master_layout.addWidget(blend_slider, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_BLEND_TO_TANGENT)
            master_layout.addWidget(tangent_container, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_TANGENT_TO_ICONS)
            master_layout.addWidget(icon_container, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_ICONS_TO_SCALE)
            master_layout.addWidget(scale_slider, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_SCALE_TO_CASCADE)
            master_layout.addWidget(cascade_slider, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_CASCADE_TO_COUNTER)
            master_layout.addWidget(tools_container, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_CASCADE_TO_COUNTER)
            master_layout.addWidget(smooth_btn, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_WHITE_ICONS)
            master_layout.addWidget(snap_btn, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_WHITE_ICONS)
            master_layout.addWidget(crop_btn, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_WHITE_ICONS)
            master_layout.addWidget(delkeys_btn, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(bar.SPACING_DELKEYS_TO_DOCK)
            master_layout.addWidget(about_btn, 0, QtCore.Qt.AlignVCenter)
            master_layout.addSpacing(8)
            master_layout.addWidget(dock_btn, 0, QtCore.Qt.AlignVCenter)
        
        # Create left arrow button (hidden by default)
        left_arrow = QtWidgets.QPushButton("<")
        left_arrow.setFixedSize(20, style.TOOLBAR_HEIGHT - 4)
        left_arrow.setStyleSheet("""
            QPushButton {
                background: rgba(45, 45, 45, 230);
                color: #bbb;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 240);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(80, 80, 80, 250);
            }
        """)
        left_arrow.hide()
        
        # Create right arrow button (hidden by default)
        right_arrow = QtWidgets.QPushButton(">")
        right_arrow.setFixedSize(20, style.TOOLBAR_HEIGHT - 4)
        right_arrow.setStyleSheet("""
            QPushButton {
                background: rgba(45, 45, 45, 230);
                color: #bbb;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 240);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(80, 80, 80, 250);
            }
        """)
        right_arrow.hide()
        
        # Store scroll state
        self._scroll_offset = 0
        self._content_width = TOOLBAR_CONTENT_WIDTH
        self._master_container = master_container
        self._left_arrow = left_arrow
        self._right_arrow = right_arrow
        self._wrap_icons_enabled = wrap_icons_enabled
        
        # Connect arrow buttons
        left_arrow.clicked.connect(lambda: self._scrollToolbar(-200))
        right_arrow.clicked.connect(lambda: self._scrollToolbar(200))
        
        if wrap_icons_enabled:
            # Wrap mode: no scroll area needed, add master container directly
            # and hide the arrows permanently
            left_arrow.hide()
            right_arrow.hide()
            left_arrow.setVisible(False)
            right_arrow.setVisible(False)
            
            # Add master container with stretch to fill available width
            # FlowLayout inside handles centering of content
            layout.addWidget(master_container, 1)  # stretch=1 to expand
            
            self._clip_container = None
            
        else:
            # Normal mode: use scroll area as clip container
            clip_container = QtWidgets.QScrollArea()
            clip_container.setWidgetResizable(False)
            clip_container.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            clip_container.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            clip_container.setFrameShape(QtWidgets.QFrame.NoFrame)
            clip_container.setStyleSheet("QScrollArea { background: transparent; border: none; }")
            clip_container.viewport().setStyleSheet("background: transparent;")
            clip_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            clip_container.setAlignment(QtCore.Qt.AlignCenter)  # Center content when it fits
            
            # Put master_container inside clip_container
            clip_container.setWidget(master_container)
            
            self._clip_container = clip_container
            
            # Add to main layout with arrows on edges
            layout.addWidget(left_arrow, 0, QtCore.Qt.AlignVCenter)
            layout.addWidget(clip_container, 1)  # Takes available space
            layout.addWidget(right_arrow, 0, QtCore.Qt.AlignVCenter)
        
        # Create event filter for resize events
        class ResizeFilter(QtCore.QObject):
            def __init__(self, callback, parent=None):
                super(ResizeFilter, self).__init__(parent)
                self._callback = callback
            
            def eventFilter(self, obj, event):
                if event.type() == QtCore.QEvent.Resize:
                    self._callback()
                return False
        
        if wrap_icons_enabled:
            def update_wrap_height():
                try:
                    if not self._master_container or not self.qt_toolbar:
                        return
                    container_width = self._master_container.width()
                    if container_width <= 0:
                        container_width = toolbar_row.width()
                    if container_width > 0:
                        layout = self._master_container.layout()
                        if layout and hasattr(layout, 'heightForWidth'):
                            required_height = layout.heightForWidth(container_width)
                            if required_height > 0:
                                if required_height <= style.TOOLBAR_HEIGHT:
                                    new_height = style.TOOLBAR_HEIGHT
                                else:
                                    new_height = required_height + 2
                                
                                if _show_all_sliders_container and _show_all_sliders_container.isVisible():
                                    new_height += style.scaled(28)
                                
                                layout.invalidate()
                                self._master_container.updateGeometry()
                                self._master_container.update()
                                
                                old_height = self._last_toolbar_height
                                if new_height != old_height:
                                    self._last_toolbar_height = new_height
                                    
                                    self.qt_toolbar.setFixedHeight(new_height)
                                    
                                    def adjust_splitter():
                                        try:
                                            if self._splitter and self.qt_toolbar:
                                                toolbar_idx = self._splitter.indexOf(self.qt_toolbar)
                                                if toolbar_idx >= 0:
                                                    sizes = self._splitter.sizes()
                                                    current_toolbar_size = sizes[toolbar_idx]
                                                    
                                                    if current_toolbar_size > new_height and toolbar_idx > 0:
                                                        excess = current_toolbar_size - new_height
                                                        sizes[toolbar_idx - 1] += excess
                                                        sizes[toolbar_idx] = new_height
                                                        self._splitter.setSizes(sizes)
                                                    elif current_toolbar_size < new_height and toolbar_idx > 0:
                                                        needed = new_height - current_toolbar_size
                                                        sizes[toolbar_idx - 1] -= needed
                                                        sizes[toolbar_idx] = new_height
                                                        self._splitter.setSizes(sizes)
                                        except (RuntimeError, ReferenceError):
                                            pass
                                    
                                    QtCore.QTimer.singleShot(50, adjust_splitter)
                except (RuntimeError, ReferenceError):
                    pass
            
            self._wrap_resize_filter = ResizeFilter(update_wrap_height, toolbar_row)
            toolbar_row.installEventFilter(self._wrap_resize_filter)
            
            self._master_resize_filter = ResizeFilter(update_wrap_height, master_container)
            master_container.installEventFilter(self._master_resize_filter)
            
            self._toolbar_resize_filter = ResizeFilter(update_wrap_height, self.qt_toolbar)
            self.qt_toolbar.installEventFilter(self._toolbar_resize_filter)
            
            QtCore.QTimer.singleShot(100, update_wrap_height)
            QtCore.QTimer.singleShot(300, update_wrap_height)
            QtCore.QTimer.singleShot(500, update_wrap_height)
            QtCore.QTimer.singleShot(1000, update_wrap_height)
        else:
            self._resize_filter = ResizeFilter(self._updateScrollArrows, toolbar_row)
            toolbar_row.installEventFilter(self._resize_filter)
            
            self._clip_resize_filter = ResizeFilter(self._onClipResize, clip_container)
            clip_container.installEventFilter(self._clip_resize_filter)
            
            QtCore.QTimer.singleShot(100, self._onClipResize)
        
        # Apply saved icon offsets after layout is complete
        self._applySavedOffsets()
    
    def _onClipResize(self):
        """Handle clip container resize - update height and scroll arrows"""
        if not self._master_container:
            return
        
        # In wrap mode, no clip container to handle
        if hasattr(self, '_wrap_icons_enabled') and self._wrap_icons_enabled:
            return
            
        if not self._clip_container:
            return
        
        clip_width = self._clip_container.viewport().width()
        content_width = self._content_width
        
        # Update master container height to match viewport
        self._master_container.setFixedHeight(self._clip_container.viewport().height())
        
        if content_width <= clip_width:
            # Content fits - reset scroll
            self._scroll_offset = 0
            self._clip_container.horizontalScrollBar().setValue(0)
        else:
            # Content doesn't fit - clamp scroll offset to valid range
            max_offset = content_width - clip_width
            if self._scroll_offset > max_offset:
                self._scroll_offset = max_offset
                self._applyScrollOffset()
        
        self._updateScrollArrows()
    
    def _updateScrollArrows(self):
        """Update scroll arrow visibility based on content vs viewport"""
        # In wrap mode, arrows are not used
        if hasattr(self, '_wrap_icons_enabled') and self._wrap_icons_enabled:
            return
            
        if not self._master_container or not self._left_arrow or not self._right_arrow:
            return
        
        if not hasattr(self, '_clip_container') or not self._clip_container:
            return
        
        clip_width = self._clip_container.viewport().width()
        content_width = self._content_width
        
        if content_width > clip_width:
            # Content is clipped, show appropriate arrows
            max_offset = content_width - clip_width
            self._left_arrow.setVisible(self._scroll_offset > 0)
            self._right_arrow.setVisible(self._scroll_offset < max_offset)
        else:
            # Content fits, hide arrows and reset offset
            self._left_arrow.hide()
            self._right_arrow.hide()
            if self._scroll_offset != 0:
                self._scroll_offset = 0
                self._applyScrollOffset()
    
    def _scrollToolbar(self, delta):
        """Scroll toolbar content by delta pixels"""
        if not self._master_container or not hasattr(self, '_clip_container') or not self._clip_container:
            return
        
        clip_width = self._clip_container.viewport().width()
        content_width = self._content_width
        max_offset = max(0, content_width - clip_width)
        
        self._scroll_offset = max(0, min(max_offset, self._scroll_offset + delta))
        self._applyScrollOffset()
        self._updateScrollArrows()
    
    def _applyScrollOffset(self):
        """Apply current scroll offset using QScrollArea's scrollbar"""
        if not hasattr(self, '_clip_container') or not self._clip_container:
            return
        
        # Use the QScrollArea's horizontal scrollbar
        self._clip_container.horizontalScrollBar().setValue(self._scroll_offset)

    def _restoreTimelineArea(self):
        """Clean up toolbar UI elements"""
        # Clean up the new toolbar style
        if cmds.toolBar("animo_timeline_toolbar", query=True, exists=True):
            try:
                cmds.deleteUI("animo_timeline_toolbar")
            except:
                pass
        
        if cmds.window("animo_toolbar_win", query=True, exists=True):
            try:
                cmds.deleteUI("animo_toolbar_win")
            except:
                pass
    
    def buildShelfUI(self):
        """Build horizontal toolbar under the shelf using pure Qt embedding"""
        # Clean up existing
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
            except:
                pass
        
        if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        
        try:
            # Find the shelf widget
            shelf_layout = mel.eval('$tmpVar=$gShelfTopLevel')
            ptr = mui.MQtUtil.findControl(shelf_layout)
            if not ptr:
                cmds.warning("Animo: Could not find shelf widget")
                return
            shelf_widget = wrapInstance(int(ptr), QtWidgets.QWidget)
            
            # Get the shelf's parent
            target_parent = shelf_widget.parent()
            if not target_parent:
                cmds.warning("Animo: Could not find shelf parent")
                return
            
            # Build the toolbar widget - use lighter color for shelf mode
            bg_color = "rgb({}, {}, {})".format(
                int(style.TOOLBAR_BG_COLOR_LIGHTER[0] * 255),
                int(style.TOOLBAR_BG_COLOR_LIGHTER[1] * 255),
                int(style.TOOLBAR_BG_COLOR_LIGHTER[2] * 255)
            )
            
            self.qt_toolbar = QtWidgets.QWidget()
            self.qt_toolbar.setObjectName("animo_qt_toolbar")
            self.qt_toolbar.setFixedHeight(style.TOOLBAR_HEIGHT)
            self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }} {}".format(bg_color, TOOLTIP_STYLE))
            
            # Create horizontal layout
            layout = QtWidgets.QHBoxLayout(self.qt_toolbar)
            layout.setContentsMargins(8, 0, 8, 0)
            layout.setSpacing(0)
            
            # Create icon container
            icon_container = QtWidgets.QWidget()
            icon_layout = QtWidgets.QHBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setSpacing(style.ICON_SPACING + 4)
            icon_layout.setAlignment(QtCore.Qt.AlignVCenter)
            
            # Tangent icon indices to skip from main loop
            tangent_indices = [13, 14, 15]
            
            # Create selection counter for shelf mode
            self.selection_counter = selection_counter.SelectionCounter()
            self.selection_counter.set_scaled_size(style.scaled)
            
            # Add tool icons (skip tangent icons)
            for i, icon_data in enumerate(bar.ICON_DATA):
                if i in tangent_indices:
                    continue
                
                if i == 5:
                    icon_layout.addWidget(self.selection_counter)
                    
                icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
                custom_size = icon_data[5] if len(icon_data) > 5 else None
                offset = icon_data[6] if len(icon_data) > 6 else None
                menu_options = icon_data[7] if len(icon_data) > 7 else None
                
                icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
                icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
                
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(icon_w + 6, icon_h + 6)
                btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
                btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
                btn.setToolTip(tooltip)
                btn.installEventFilter(_tooltip_filter)
                btn.setFlat(True)
                
                margin_style = ""
                if offset:
                    margin_left = max(0, offset[0])
                    margin_right = max(0, -offset[0])
                    margin_style = "margin-left: {}px; margin-right: {}px;".format(margin_left, margin_right)
                
                btn.setStyleSheet("""
                    QPushButton {{ border: none; background: transparent; {} }}
                    QPushButton:hover {{ background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }}
                    QPushButton:pressed {{ background-color: rgba(255,255,255,100); border-radius: 8px; }}
                QPushButton::menu-indicator {{ width: 0; height: 0; }}
                """.format(margin_style))
                
                if menu_options:
                    btn_menu = QtWidgets.QMenu(btn)
                    btn_menu.setStyleSheet('''
                        QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                        QMenu::item { padding: 6px 25px; color: #ccc; }
                        QMenu::item:selected { background-color: #555; color: #fff; }
                    ''')
                    for menu_item in menu_options:
                        option_name = menu_item[0]
                        option_launcher = menu_item[1]
                        option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                        if option_name == "---":
                            btn_menu.addSeparator()
                        else:
                            action = btn_menu.addAction(option_name)
                            action.triggered.connect(
                                lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                            )
                    btn.setMenu(btn_menu)
                    # Enable right-click to show same menu
                    btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
                else:
                    if i == 17:
                        def tools_editor_wip():
                            cmds.inViewMessage(
                                amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                                pos='midCenter', fade=True, fadeStayTime=2000
                            )
                        btn.clicked.connect(tools_editor_wip)
                    elif i == 4:
                        def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                            mods = cmds.getModifiers()
                            if mods == 4:
                                run_tracify_arc_track()
                            else:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                        btn.clicked.connect(tracify_click_handler)
                    else:
                        btn.clicked.connect(
                            lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                        )
                
                icon_layout.addWidget(btn)
            
            # Create tangent icon buttons
            tangent_launcher_map = {
                13: {"selected": "auto_current_launcher", "all": "auto_all_launcher"},
                14: {"selected": "linear_current_launcher", "all": "linear_all_launcher"},
                15: {"selected": "step_current_launcher", "all": "step_all_launcher"}
            }
            tangent_buttons = []
            for i in tangent_indices:
                icon_data = bar.ICON_DATA[i]
                icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
                custom_size = icon_data[5] if len(icon_data) > 5 else None
                menu_options = icon_data[7] if len(icon_data) > 7 else None
                
                icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
                icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
                
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(icon_w + 6, icon_h + 6)
                btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
                btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
                btn.setToolTip(tooltip)
                btn.installEventFilter(_tooltip_filter)
                btn.setFlat(True)
                btn.setStyleSheet("""
                    QPushButton { border: none; background: transparent; }
                    QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                    QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                    QPushButton::menu-indicator { width: 0; height: 0; }
                """)
                
                if menu_options:
                    btn_menu = QtWidgets.QMenu(btn)
                    btn_menu.setStyleSheet('''
                        QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                        QMenu::item { padding: 6px 25px; color: #ccc; }
                        QMenu::item:selected { background-color: #555; color: #fff; }
                    ''')
                    for menu_item in menu_options:
                        option_name = menu_item[0]
                        option_launcher = menu_item[1]
                        option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                        if option_name == "---":
                            btn_menu.addSeparator()
                        else:
                            action = btn_menu.addAction(option_name)
                            action.triggered.connect(
                                lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                            )
                    
                    # Add global tangent option
                    tangent_global_map = {13: "auto_tangent_global", 14: "linear_tangent_global", 15: "step_tangent_global"}
                    if i in tangent_global_map:
                        global_script = tangent_global_map[i]
                        btn_menu.addSeparator()
                        global_action = btn_menu.addAction("Apply Maya Global Tangents")
                        global_action.triggered.connect(
                            lambda checked=False, gs=global_script:
                            run_global_tangent(gs)
                        )
                    
                    btn._tangent_menu = btn_menu
                    btn._tangent_index = i
                    btn._tangent_launchers = tangent_launcher_map.get(i, {})
                    
                    def tangent_click_handler_2(checked=False, button=btn):
                        mods = cmds.getModifiers()
                        launchers = button._tangent_launchers
                        if mods == 4:
                            if "selected" in launchers:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["selected"], None, None)
                        elif mods == 13:
                            if "all" in launchers:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["all"], None, None)
                        else:
                            button._tangent_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                    
                    btn.clicked.connect(tangent_click_handler_2)
                    btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
                
                tangent_buttons.append(btn)
            
            # Dock mode button
            dock_btn = QtWidgets.QPushButton()
            dock_btn.setFixedSize(int(style.ICON_WIDTH * 1.01), int(style.ICON_HEIGHT * 1.01))
            dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
            dock_btn.setIconSize(QtCore.QSize(int(style.ICON_WIDTH * 1.01) - 2, int(style.ICON_HEIGHT * 1.01) - 2))
            dock_btn.setToolTip("Dock Position")
            dock_btn.installEventFilter(_tooltip_filter)
            dock_btn.setFlat(True)
            dock_btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }
            """)
            
            # Create popup menu
            dock_menu = QtWidgets.QMenu(dock_btn)
            dock_menu.setStyleSheet('''
                QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                QMenu::item { padding: 6px 25px; color: #ccc; }
                QMenu::item:selected { background-color: #555; }
                QMenu::item:disabled { color: #666; }
                QMenu::indicator { width: 13px; height: 13px; }
                QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
                QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
            ''')
            
            def refresh_qt_menu():
                dock_menu.clear()
                reset_action = dock_menu.addAction("Reset Animo")
                reset_action.triggered.connect(lambda: self._resetUI())
                shelf_action = dock_menu.addAction("Add Animo to Shelf")
                shelf_action.triggered.connect(lambda: self._addToShelf())
                dock_menu.addSeparator()
                tooltip_action = QAction("Show Tool Tips", dock_menu)
                tooltip_action.setCheckable(True)
                tooltip_action.setChecked(_get_tooltip_pref())
                def toggle_tooltips(checked):
                    global _tooltip_manager
                    _set_tooltip_pref(checked)
                    if _tooltip_manager:
                        _tooltip_manager.set_enabled(checked)
                    if checked:
                        cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                    else:
                        cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                tooltip_action.triggered.connect(toggle_tooltips)
                dock_menu.addAction(tooltip_action)
                center_pivot_action = QAction("Keep Selections at Center", dock_menu)
                center_pivot_action.setCheckable(True)
                center_pivot_action.setChecked(_is_center_pivot_active())
                def toggle_center_pivot_3(checked):
                    _toggle_center_pivot(checked)
                center_pivot_action.triggered.connect(toggle_center_pivot_3)
                dock_menu.addAction(center_pivot_action)

                dock_menu.addSeparator()
                size_action = dock_menu.addAction("Animo Size Settings...")
                size_action.triggered.connect(_show_size_settings)
            
            dock_menu.aboutToShow.connect(refresh_qt_menu)
            dock_btn.setMenu(dock_menu)
            
            tween_slider = AnimoSlider("TW", (225, 175, 45), "tween")
            tween_slider.setMinimum(-100)
            tween_slider.setMaximum(100)
            tween_slider.setValue(0)
            tween_slider.setFixedWidth(style.scaled(200))
            
            blend_slider = AnimoSlider("BN", (220, 140, 60), "blend")
            blend_slider.setMinimum(-100)
            blend_slider.setMaximum(100)
            blend_slider.setValue(0)
            blend_slider.setFixedWidth(style.scaled(200))
            
            # Right side sliders
            scale_slider = AnimoSlider("SL", (100, 180, 220), "scale")
            scale_slider.setMinimum(-100)
            scale_slider.setMaximum(100)
            scale_slider.setValue(0)
            scale_slider.setFixedWidth(style.scaled(200))
            
            cascade_slider = AnimoSlider("CA", (180, 120, 200), "cascade")
            cascade_slider.setMinimum(0)
            cascade_slider.setMaximum(200)
            cascade_slider.setValue(100)
            cascade_slider.setFixedWidth(style.scaled(200))
            
            # Layout: [stretch] [TW] [BN] [tangent icons] [spacing] [icons] [spacing] [SL] [CA] [stretch] [dock]
            layout.addStretch(1)
            layout.addWidget(tween_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(16)
            layout.addWidget(blend_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(18)
            for tbtn in tangent_buttons:
                layout.addWidget(tbtn, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(20)
            layout.addWidget(icon_container, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(20)
            layout.addWidget(scale_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(16)
            layout.addWidget(cascade_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addStretch(1)
            layout.addWidget(dock_btn)
            
            # Walk up to find a parent with a QVBoxLayout we can insert into
            current = shelf_widget
            inserted = False
            for _ in range(15):
                parent = current.parent()
                if not parent:
                    break
                parent_layout = parent.layout()
                if parent_layout and hasattr(parent_layout, 'insertWidget'):
                    idx = parent_layout.indexOf(current)
                    if idx >= 0:
                        parent_layout.insertWidget(idx + 1, self.qt_toolbar)
                        inserted = True
                        break
                current = parent
            
            if not inserted:
                # Fallback - just parent to shelf's parent
                self.qt_toolbar.setParent(target_parent)
            
            self.qt_toolbar.show()
            
        except Exception as e:
            cmds.warning("Animo: Could not build shelf toolbar - {}".format(str(e)))
    
    def buildStatusLineUI(self):
        """Build horizontal toolbar ABOVE the status line using pure Qt embedding"""
        # Clean up existing
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
            except:
                pass
        
        if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        
        try:
            # Find the status line widget
            status_line = mel.eval('$tmpVar=$gStatusLine')
            ptr = mui.MQtUtil.findControl(status_line)
            if not ptr:
                cmds.warning("Animo: Could not find status line widget")
                return
            status_widget = wrapInstance(int(ptr), QtWidgets.QWidget)
            
            # Get the status line's parent
            target_parent = status_widget.parent()
            if not target_parent:
                cmds.warning("Animo: Could not find status line parent")
                return
            
            # Build the toolbar widget - use lighter color for status line mode
            bg_color = "rgb({}, {}, {})".format(
                int(style.TOOLBAR_BG_COLOR_LIGHTER[0] * 255),
                int(style.TOOLBAR_BG_COLOR_LIGHTER[1] * 255),
                int(style.TOOLBAR_BG_COLOR_LIGHTER[2] * 255)
            )
            
            self.qt_toolbar = QtWidgets.QWidget()
            self.qt_toolbar.setObjectName("animo_qt_toolbar")
            self.qt_toolbar.setFixedHeight(style.TOOLBAR_HEIGHT)
            self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }} {}".format(bg_color, TOOLTIP_STYLE))
            
            # Create horizontal layout
            layout = QtWidgets.QHBoxLayout(self.qt_toolbar)
            layout.setContentsMargins(8, 0, 8, 0)
            layout.setSpacing(0)
            
            # Create icon container
            icon_container = QtWidgets.QWidget()
            icon_layout = QtWidgets.QHBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setSpacing(style.ICON_SPACING + 4)
            icon_layout.setAlignment(QtCore.Qt.AlignVCenter)
            
            # Tangent icon indices to skip from main loop
            tangent_indices = [13, 14, 15]
            
            # Create selection counter for statusline mode
            self.selection_counter = selection_counter.SelectionCounter()
            self.selection_counter.set_scaled_size(style.scaled)
            
            # Add tool icons (skip tangent icons)
            for i, icon_data in enumerate(bar.ICON_DATA):
                if i in tangent_indices:
                    continue
                
                if i == 5:
                    icon_layout.addWidget(self.selection_counter)
                    
                icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
                custom_size = icon_data[5] if len(icon_data) > 5 else None
                offset = icon_data[6] if len(icon_data) > 6 else None
                menu_options = icon_data[7] if len(icon_data) > 7 else None
                
                icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
                icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
                
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(icon_w + 6, icon_h + 6)
                btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
                btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
                btn.setToolTip(tooltip)
                btn.installEventFilter(_tooltip_filter)
                btn.setFlat(True)
                
                margin_style = ""
                if offset:
                    margin_left = max(0, offset[0])
                    margin_right = max(0, -offset[0])
                    margin_style = "margin-left: {}px; margin-right: {}px;".format(margin_left, margin_right)
                
                btn.setStyleSheet("""
                    QPushButton {{ border: none; background: transparent; {} }}
                    QPushButton:hover {{ background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }}
                    QPushButton:pressed {{ background-color: rgba(255,255,255,100); border-radius: 8px; }}
                QPushButton::menu-indicator {{ width: 0; height: 0; }}
                """.format(margin_style))
                
                if menu_options:
                    btn_menu = QtWidgets.QMenu(btn)
                    btn_menu.setStyleSheet('''
                        QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                        QMenu::item { padding: 6px 25px; color: #ccc; }
                        QMenu::item:selected { background-color: #555; color: #fff; }
                    ''')
                    for menu_item in menu_options:
                        option_name = menu_item[0]
                        option_launcher = menu_item[1]
                        option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                        if option_name == "---":
                            btn_menu.addSeparator()
                        else:
                            action = btn_menu.addAction(option_name)
                            action.triggered.connect(
                                lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                            )
                    btn.setMenu(btn_menu)
                    # Enable right-click to show same menu
                    btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
                else:
                    if i == 17:
                        def tools_editor_wip():
                            cmds.inViewMessage(
                                amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                                pos='midCenter', fade=True, fadeStayTime=2000
                            )
                        btn.clicked.connect(tools_editor_wip)
                    elif i == 4:
                        def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                            mods = cmds.getModifiers()
                            if mods == 4:
                                run_tracify_arc_track()
                            else:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                        btn.clicked.connect(tracify_click_handler)
                    else:
                        btn.clicked.connect(
                            lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                        )
                
                icon_layout.addWidget(btn)
            
            # Create tangent icon buttons
            tangent_launcher_map = {
                13: {"selected": "auto_current_launcher", "all": "auto_all_launcher"},
                14: {"selected": "linear_current_launcher", "all": "linear_all_launcher"},
                15: {"selected": "step_current_launcher", "all": "step_all_launcher"}
            }
            tangent_buttons = []
            for i in tangent_indices:
                icon_data = bar.ICON_DATA[i]
                icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
                custom_size = icon_data[5] if len(icon_data) > 5 else None
                menu_options = icon_data[7] if len(icon_data) > 7 else None
                
                icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
                icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
                
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(icon_w + 6, icon_h + 6)
                btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
                btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
                btn.setToolTip(tooltip)
                btn.installEventFilter(_tooltip_filter)
                btn.setFlat(True)
                btn.setStyleSheet("""
                    QPushButton { border: none; background: transparent; }
                    QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                    QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                    QPushButton::menu-indicator { width: 0; height: 0; }
                """)
                
                if menu_options:
                    btn_menu = QtWidgets.QMenu(btn)
                    btn_menu.setStyleSheet('''
                        QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                        QMenu::item { padding: 6px 25px; color: #ccc; }
                        QMenu::item:selected { background-color: #555; color: #fff; }
                    ''')
                    for menu_item in menu_options:
                        option_name = menu_item[0]
                        option_launcher = menu_item[1]
                        option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                        if option_name == "---":
                            btn_menu.addSeparator()
                        else:
                            action = btn_menu.addAction(option_name)
                            action.triggered.connect(
                                lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                            )
                    
                    # Add global tangent option
                    tangent_global_map = {13: "auto_tangent_global", 14: "linear_tangent_global", 15: "step_tangent_global"}
                    if i in tangent_global_map:
                        global_script = tangent_global_map[i]
                        btn_menu.addSeparator()
                        global_action = btn_menu.addAction("Apply Maya Global Tangents")
                        global_action.triggered.connect(
                            lambda checked=False, gs=global_script:
                            run_global_tangent(gs)
                        )
                    
                    btn._tangent_menu = btn_menu
                    btn._tangent_index = i
                    btn._tangent_launchers = tangent_launcher_map.get(i, {})
                    
                    def tangent_click_handler_3(checked=False, button=btn):
                        mods = cmds.getModifiers()
                        launchers = button._tangent_launchers
                        if mods == 4:
                            if "selected" in launchers:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["selected"], None, None)
                        elif mods == 13:
                            if "all" in launchers:
                                bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["all"], None, None)
                        else:
                            button._tangent_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                    
                    btn.clicked.connect(tangent_click_handler_3)
                    btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
                
                tangent_buttons.append(btn)
            
            # Dock mode button
            dock_btn = QtWidgets.QPushButton()
            dock_btn.setFixedSize(int(style.ICON_WIDTH * 1.01), int(style.ICON_HEIGHT * 1.01))
            dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
            dock_btn.setIconSize(QtCore.QSize(int(style.ICON_WIDTH * 1.01) - 2, int(style.ICON_HEIGHT * 1.01) - 2))
            dock_btn.setToolTip("Dock Position")
            dock_btn.installEventFilter(_tooltip_filter)
            dock_btn.setFlat(True)
            dock_btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }
            """)
            
            # Create popup menu
            dock_menu = QtWidgets.QMenu(dock_btn)
            dock_menu.setStyleSheet('''
                QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                QMenu::item { padding: 6px 25px; color: #ccc; }
                QMenu::item:selected { background-color: #555; }
                QMenu::item:disabled { color: #666; }
                QMenu::indicator { width: 13px; height: 13px; }
                QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
                QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
            ''')
            
            def refresh_qt_menu():
                dock_menu.clear()
                reset_action = dock_menu.addAction("Reset Animo")
                reset_action.triggered.connect(lambda: self._resetUI())
                shelf_action = dock_menu.addAction("Add Animo to Shelf")
                shelf_action.triggered.connect(lambda: self._addToShelf())
                dock_menu.addSeparator()
                tooltip_action = QAction("Show Tool Tips", dock_menu)
                tooltip_action.setCheckable(True)
                tooltip_action.setChecked(_get_tooltip_pref())
                def toggle_tooltips(checked):
                    global _tooltip_manager
                    _set_tooltip_pref(checked)
                    if _tooltip_manager:
                        _tooltip_manager.set_enabled(checked)
                    if checked:
                        cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                    else:
                        cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                tooltip_action.triggered.connect(toggle_tooltips)
                dock_menu.addAction(tooltip_action)
                center_pivot_action = QAction("Keep Selections at Center", dock_menu)
                center_pivot_action.setCheckable(True)
                center_pivot_action.setChecked(_is_center_pivot_active())
                def toggle_center_pivot_4(checked):
                    _toggle_center_pivot(checked)
                center_pivot_action.triggered.connect(toggle_center_pivot_4)
                dock_menu.addAction(center_pivot_action)

                dock_menu.addSeparator()
                size_action = dock_menu.addAction("Animo Size Settings...")
                size_action.triggered.connect(_show_size_settings)
            
            dock_menu.aboutToShow.connect(refresh_qt_menu)
            dock_btn.setMenu(dock_menu)
            
            tween_slider = AnimoSlider("TW", (225, 175, 45), "tween")
            tween_slider.setMinimum(-100)
            tween_slider.setMaximum(100)
            tween_slider.setValue(0)
            tween_slider.setFixedWidth(style.scaled(200))
            
            blend_slider = AnimoSlider("BN", (220, 140, 60), "blend")
            blend_slider.setMinimum(-100)
            blend_slider.setMaximum(100)
            blend_slider.setValue(0)
            blend_slider.setFixedWidth(style.scaled(200))
            
            # Right side sliders
            scale_slider = AnimoSlider("SL", (100, 180, 220), "scale")
            scale_slider.setMinimum(-100)
            scale_slider.setMaximum(100)
            scale_slider.setValue(0)
            scale_slider.setFixedWidth(style.scaled(200))
            
            cascade_slider = AnimoSlider("CA", (180, 120, 200), "cascade")
            cascade_slider.setMinimum(0)
            cascade_slider.setMaximum(200)
            cascade_slider.setValue(100)
            cascade_slider.setFixedWidth(style.scaled(200))
            
            # Layout: [stretch] [TW] [BN] [tangent icons] [spacing] [icons] [spacing] [SL] [CA] [stretch] [dock]
            layout.addStretch(1)
            layout.addWidget(tween_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(16)
            layout.addWidget(blend_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(18)
            for tbtn in tangent_buttons:
                layout.addWidget(tbtn, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(20)
            layout.addWidget(icon_container, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(20)
            layout.addWidget(scale_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addSpacing(16)
            layout.addWidget(cascade_slider, 0, QtCore.Qt.AlignVCenter)
            layout.addStretch(1)
            layout.addWidget(dock_btn)
            
            # Walk up to find a parent with a layout we can insert into
            current = status_widget
            inserted = False
            for _ in range(15):
                parent = current.parent()
                if not parent:
                    break
                parent_layout = parent.layout()
                if parent_layout and hasattr(parent_layout, 'insertWidget'):
                    idx = parent_layout.indexOf(current)
                    if idx >= 0:
                        # Insert ABOVE the status line (at idx, not idx+1)
                        parent_layout.insertWidget(idx, self.qt_toolbar)
                        inserted = True
                        break
                current = parent
            
            if not inserted:
                # Fallback - just parent to status line's parent
                self.qt_toolbar.setParent(target_parent)
            
            self.qt_toolbar.show()
            
        except Exception as e:
            cmds.warning("Animo: Could not build status line toolbar - {}".format(str(e)))
    
    def buildBottomToolbar(self):
        """Build horizontal toolbar at bottom of Maya using cmds.toolBar"""
        # Clean up existing Qt toolbar
        if self.qt_toolbar:
            try:
                self.qt_toolbar.hide()
                self.qt_toolbar.setParent(None)
                self.qt_toolbar.deleteLater()
                self.qt_toolbar = None
            except:
                pass
        
        if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            cmds.deleteUI(WorkspaceName, control=True)
        
        # Clean up existing bottom toolbar
        if cmds.toolBar("animo_bottom_toolbar", query=True, exists=True):
            cmds.deleteUI("animo_bottom_toolbar")
        if cmds.window("animo_bottom_win", query=True, exists=True):
            cmds.deleteUI("animo_bottom_win")
        
        # Create window to hold toolbar content (like aTools)
        self.bottom_win = cmds.window("animo_bottom_win", sizeable=True)
        cmds.frameLayout(labelVisible=False, borderVisible=False, w=10, marginHeight=0, marginWidth=0, collapsable=False)
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach=([2, 'right', 0]), h=style.TOOLBAR_HEIGHT)
        cmds.text(label="")
        main_row = cmds.rowLayout("animo_main_row", numberOfColumns=50)
        
        # Add icons
        tangent_indices = [13, 14, 15]
        for i, icon_data in enumerate(bar.ICON_DATA):
            if i in tangent_indices:
                continue
            
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = cmds.iconTextButton(style='iconOnly', w=icon_w, h=icon_h,
                image=self.getImage(icon_file), ann=tooltip)
            
            if menu_options:
                popup = cmds.popupMenu(parent=btn, button=1)
                popup_right = cmds.popupMenu(parent=btn, button=3)
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        cmds.menuItem(divider=True, parent=popup)
                        cmds.menuItem(divider=True, parent=popup_right)
                    else:
                        cmds.menuItem(label=option_name, parent=popup,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
                        cmds.menuItem(label=option_name, parent=popup_right,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
            else:
                cmds.iconTextButton(btn, edit=True,
                    c=lambda ln=launcher_name, tf=tool_folder, ef=entry_func:
                    bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef))
            
            cmds.separator(style='none', width=style.ICON_SPACING + 4)
        
        # Add dock button
        dock_btn = cmds.iconTextButton(style='iconOnly', w=style.scaled(16), h=style.scaled(16),
            image=self.getImage("dock_icon.png"), ann="Dock Position")
        dock_menu = cmds.popupMenu(button=1, parent=dock_btn,
            postMenuCommand=lambda menu, *args: self._refreshDockMenu(menu))
        
        # Create toolbar at bottom
        cmds.toolBar("animo_bottom_toolbar", area='bottom', content=self.bottom_win, allowedArea=['bottom'])
    
    def _buildWorkspaceContent(self):
        """Build horizontal toolbar content inside a workspaceControl"""
        # Get the workspaceControl's Qt widget
        ptr = mui.MQtUtil.findControl(WorkspaceName)
        if not ptr:
            return
        workspace_widget = wrapInstance(int(ptr), QtWidgets.QWidget)
        
        # Force the workspace to be small
        workspace_widget.setFixedHeight(style.TOOLBAR_HEIGHT)
        workspace_widget.setMaximumHeight(style.TOOLBAR_WIDTH)
        
        # Build the toolbar - lighter for horizontal modes
        bg_color = "rgb({}, {}, {})".format(
            int(style.TOOLBAR_BG_COLOR_LIGHT[0] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[1] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[2] * 255)
        )
        
        self.qt_toolbar = QtWidgets.QWidget(workspace_widget)
        self.qt_toolbar.setObjectName("animo_qt_toolbar")
        self.qt_toolbar.setFixedHeight(style.TOOLBAR_HEIGHT)
        self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }} {}".format(bg_color, TOOLTIP_STYLE))
        
        # Create horizontal layout
        layout = QtWidgets.QHBoxLayout(self.qt_toolbar)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)
        
        # Create icon container
        icon_container = QtWidgets.QWidget()
        icon_layout = QtWidgets.QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(style.ICON_SPACING + 4)
        
        # Tangent icon indices to skip from main loop
        tangent_indices = [13, 14, 15]
        
        # Create selection counter for workspace mode
        self.selection_counter = selection_counter.SelectionCounter()
        self.selection_counter.set_scaled_size(style.scaled)
        
        # Add tool icons (skip tangent icons)
        for i, icon_data in enumerate(bar.ICON_DATA):
            if i in tangent_indices:
                continue
            
            if i == 5:
                icon_layout.addWidget(self.selection_counter)
                
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            offset = icon_data[6] if len(icon_data) > 6 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            
            margin_style = ""
            if offset:
                margin_left = max(0, offset[0])
                margin_right = max(0, -offset[0])
                margin_style = "margin-left: {}px; margin-right: {}px;".format(margin_left, margin_right)
            
            btn.setStyleSheet("""
                QPushButton {{ border: none; background: transparent; {} }}
                QPushButton:hover {{ background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }}
                QPushButton:pressed {{ background-color: rgba(255,255,255,100); border-radius: 8px; }}
                QPushButton::menu-indicator {{ width: 0; height: 0; }}
            """.format(margin_style))
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                btn.setMenu(btn_menu)
                # Enable right-click to show same menu
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            else:
                if i == 17:
                    def tools_editor_wip():
                        cmds.inViewMessage(
                            amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                            pos='midCenter', fade=True, fadeStayTime=2000
                        )
                    btn.clicked.connect(tools_editor_wip)
                elif i == 4:
                    def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                        mods = cmds.getModifiers()
                        if mods == 4:
                            run_tracify_arc_track()
                        else:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    btn.clicked.connect(tracify_click_handler)
                else:
                    btn.clicked.connect(
                        lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                        bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    )
            
            icon_layout.addWidget(btn)
        
        # Create tangent icon buttons
        tangent_launcher_map = {
            13: {"selected": "auto_current_launcher", "all": "auto_all_launcher"},
            14: {"selected": "linear_current_launcher", "all": "linear_all_launcher"},
            15: {"selected": "step_current_launcher", "all": "step_all_launcher"}
        }
        tangent_buttons = []
        for i in tangent_indices:
            icon_data = bar.ICON_DATA[i]
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                QPushButton::menu-indicator { width: 0; height: 0; }
            """)
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                
                # Add global tangent option
                tangent_global_map = {13: "auto_tangent_global", 14: "linear_tangent_global", 15: "step_tangent_global"}
                if i in tangent_global_map:
                    global_script = tangent_global_map[i]
                    btn_menu.addSeparator()
                    global_action = btn_menu.addAction("Apply Maya Global Tangents")
                    global_action.triggered.connect(
                        lambda checked=False, gs=global_script:
                        run_global_tangent(gs)
                    )
                
                btn._tangent_menu = btn_menu
                btn._tangent_index = i
                btn._tangent_launchers = tangent_launcher_map.get(i, {})
                
                def tangent_click_handler_4(checked=False, button=btn):
                    mods = cmds.getModifiers()
                    launchers = button._tangent_launchers
                    if mods == 4:
                        if "selected" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["selected"], None, None)
                    elif mods == 13:
                        if "all" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["all"], None, None)
                    else:
                        button._tangent_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                
                btn.clicked.connect(tangent_click_handler_4)
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            
            tangent_buttons.append(btn)
        
        # Dock mode button
        dock_btn = QtWidgets.QPushButton()
        dock_btn.setFixedSize(int(style.ICON_WIDTH * 1.01), int(style.ICON_HEIGHT * 1.01))
        dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
        dock_btn.setIconSize(QtCore.QSize(int(style.ICON_WIDTH * 1.01) - 2, int(style.ICON_HEIGHT * 1.01) - 2))
        dock_btn.setToolTip("Dock Position")
        dock_btn.installEventFilter(_tooltip_filter)
        dock_btn.setFlat(True)
        dock_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }
        """)
        
        # Create popup menu
        dock_menu = QtWidgets.QMenu(dock_btn)
        dock_menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; }
            QMenu::item:disabled { color: #666; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        
        def refresh_qt_menu():
            dock_menu.clear()
            reset_action = dock_menu.addAction("Reset Animo")
            reset_action.triggered.connect(lambda: self._resetUI())
            shelf_action = dock_menu.addAction("Add Animo to Shelf")
            shelf_action.triggered.connect(lambda: self._addToShelf())
            dock_menu.addSeparator()
            tooltip_action = QAction("Show Tool Tips", dock_menu)
            tooltip_action.setCheckable(True)
            tooltip_action.setChecked(_get_tooltip_pref())
            def toggle_tooltips(checked):
                global _tooltip_manager
                _set_tooltip_pref(checked)
                if _tooltip_manager:
                    _tooltip_manager.set_enabled(checked)
                if checked:
                    cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                else:
                    cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
            tooltip_action.triggered.connect(toggle_tooltips)
            dock_menu.addAction(tooltip_action)
            center_pivot_action = QAction("Keep Selections at Center", dock_menu)
            center_pivot_action.setCheckable(True)
            center_pivot_action.setChecked(_is_center_pivot_active())
            def toggle_center_pivot_5(checked):
                _toggle_center_pivot(checked)
            center_pivot_action.triggered.connect(toggle_center_pivot_5)
            dock_menu.addAction(center_pivot_action)

            dock_menu.addSeparator()
            size_action = dock_menu.addAction("Animo Size Settings...")
            size_action.triggered.connect(_show_size_settings)
        
        dock_menu.aboutToShow.connect(refresh_qt_menu)
        dock_btn.setMenu(dock_menu)
        
        tween_slider = AnimoSlider("TW", (225, 175, 45), "tween")
        tween_slider.setMinimum(-100)
        tween_slider.setMaximum(100)
        tween_slider.setValue(0)
        tween_slider.setFixedWidth(style.scaled(200))
        
        blend_slider = AnimoSlider("BN", (220, 140, 60), "blend")
        blend_slider.setMinimum(-100)
        blend_slider.setMaximum(100)
        blend_slider.setValue(0)
        blend_slider.setFixedWidth(style.scaled(200))
        
        # Right side sliders
        scale_slider = AnimoSlider("SL", (100, 180, 220), "scale")
        scale_slider.setMinimum(-100)
        scale_slider.setMaximum(100)
        scale_slider.setValue(0)
        scale_slider.setFixedWidth(style.scaled(200))
        
        cascade_slider = AnimoSlider("CA", (180, 120, 200), "cascade")
        cascade_slider.setMinimum(0)
        cascade_slider.setMaximum(200)
        cascade_slider.setValue(100)
        cascade_slider.setFixedWidth(style.scaled(200))
        
        # Layout: [stretch] [TW] [BN] [tangent icons] [spacing] [icons] [spacing] [SL] [CA] [stretch] [dock]
        layout.addStretch(1)
        layout.addWidget(tween_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(16)
        layout.addWidget(blend_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(18)
        for tbtn in tangent_buttons:
            layout.addWidget(tbtn, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(20)
        layout.addWidget(icon_container, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(20)
        layout.addWidget(scale_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(16)
        layout.addWidget(cascade_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addStretch(1)
        layout.addWidget(dock_btn)
        
        # Set layout on workspace widget
        if workspace_widget.layout():
            workspace_widget.layout().addWidget(self.qt_toolbar)
        else:
            workspace_layout = QtWidgets.QVBoxLayout(workspace_widget)
            workspace_layout.setContentsMargins(0, 0, 0, 0)
            workspace_layout.addWidget(self.qt_toolbar)
        
        self.qt_toolbar.show()
    
    def _buildHorizontalToolbarDirect(self, target_parent, target_widget, below=True):
        """Build a horizontal toolbar and insert it relative to target widget"""
        # Build the toolbar widget - lighter for horizontal modes
        bg_color = "rgb({}, {}, {})".format(
            int(style.TOOLBAR_BG_COLOR_LIGHT[0] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[1] * 255),
            int(style.TOOLBAR_BG_COLOR_LIGHT[2] * 255)
        )
        
        self.qt_toolbar = QtWidgets.QWidget()
        self.qt_toolbar.setObjectName("animo_qt_toolbar")
        self.qt_toolbar.setFixedHeight(style.TOOLBAR_HEIGHT)
        self.qt_toolbar.setStyleSheet("QWidget#animo_qt_toolbar {{ background-color: {}; }}".format(bg_color))
        
        # Create horizontal layout
        layout = QtWidgets.QHBoxLayout(self.qt_toolbar)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(style.ICON_SPACING + 4)
        
        # Create icon container
        icon_container = QtWidgets.QWidget()
        icon_layout = QtWidgets.QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(style.ICON_SPACING + 4)
        
        # Tangent icon indices to skip from main loop
        tangent_indices = [13, 14, 15]
        
        # Create selection counter for horizontal direct mode
        self.selection_counter = selection_counter.SelectionCounter()
        self.selection_counter.set_scaled_size(style.scaled)
        
        # Add tool icons (skip tangent icons)
        for i, icon_data in enumerate(bar.ICON_DATA):
            if i in tangent_indices:
                continue
            
            if i == 5:
                icon_layout.addWidget(self.selection_counter)
                
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            offset = icon_data[6] if len(icon_data) > 6 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            
            margin_style = ""
            if offset:
                margin_left = max(0, offset[0])
                margin_right = max(0, -offset[0])
                margin_style = "margin-left: {}px; margin-right: {}px;".format(margin_left, margin_right)
            
            btn.setStyleSheet("""
                QPushButton {{ border: none; background: transparent; {} }}
                QPushButton:hover {{ background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }}
                QPushButton:pressed {{ background-color: rgba(255,255,255,100); border-radius: 8px; }}
                QPushButton::menu-indicator {{ width: 0; height: 0; }}
            """.format(margin_style))
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                btn.setMenu(btn_menu)
                # Enable right-click to show same menu
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            else:
                if i == 17:
                    def tools_editor_wip():
                        cmds.inViewMessage(
                            amg='<span style="color:#ffaa00;">This feature is currently under development.</span>',
                            pos='midCenter', fade=True, fadeStayTime=2000
                        )
                    btn.clicked.connect(tools_editor_wip)
                elif i == 4:
                    def tracify_click_handler(checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func):
                        mods = cmds.getModifiers()
                        if mods == 4:
                            run_tracify_arc_track()
                        else:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    btn.clicked.connect(tracify_click_handler)
                else:
                    btn.clicked.connect(
                        lambda checked=False, ln=launcher_name, tf=tool_folder, ef=entry_func:
                        bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef)
                    )
            
            icon_layout.addWidget(btn)
        
        # Create tangent icon buttons
        tangent_launcher_map = {
            13: {"selected": "auto_current_launcher", "all": "auto_all_launcher"},
            14: {"selected": "linear_current_launcher", "all": "linear_all_launcher"},
            15: {"selected": "step_current_launcher", "all": "step_all_launcher"}
        }
        tangent_buttons = []
        for i in tangent_indices:
            icon_data = bar.ICON_DATA[i]
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(icon_w + 6, icon_h + 6)
            btn.setIcon(QtGui.QIcon(self.getImage(icon_file)))
            btn.setIconSize(QtCore.QSize(icon_w - 2, icon_h - 2))
            btn.setToolTip(tooltip)
            btn.installEventFilter(_tooltip_filter)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton { border: none; background: transparent; }
                QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px; }
                QPushButton:pressed { background-color: rgba(255,255,255,100); border-radius: 8px; }
                QPushButton::menu-indicator { width: 0; height: 0; }
            """)
            
            if menu_options:
                btn_menu = QtWidgets.QMenu(btn)
                btn_menu.setStyleSheet('''
                    QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
                    QMenu::item { padding: 6px 25px; color: #ccc; }
                    QMenu::item:selected { background-color: #555; color: #fff; }
                ''')
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        btn_menu.addSeparator()
                    else:
                        action = btn_menu.addAction(option_name)
                        action.triggered.connect(
                            lambda checked=False, ln=option_launcher, tf=option_tool_folder:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None)
                        )
                
                # Add global tangent option
                tangent_global_map = {13: "auto_tangent_global", 14: "linear_tangent_global", 15: "step_tangent_global"}
                if i in tangent_global_map:
                    global_script = tangent_global_map[i]
                    btn_menu.addSeparator()
                    global_action = btn_menu.addAction("Apply Maya Global Tangents")
                    global_action.triggered.connect(
                        lambda checked=False, gs=global_script:
                        run_global_tangent(gs)
                    )
                
                btn._tangent_menu = btn_menu
                btn._tangent_index = i
                btn._tangent_launchers = tangent_launcher_map.get(i, {})
                
                def tangent_click_handler_5(checked=False, button=btn):
                    mods = cmds.getModifiers()
                    launchers = button._tangent_launchers
                    if mods == 4:
                        if "selected" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["selected"], None, None)
                    elif mods == 13:
                        if "all" in launchers:
                            bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, launchers["all"], None, None)
                    else:
                        button._tangent_menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
                
                btn.clicked.connect(tangent_click_handler_5)
                btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, m=btn_menu, b=btn: m.exec_(b.mapToGlobal(pos)))
            
            tangent_buttons.append(btn)
        
        # Dock mode button
        dock_btn = QtWidgets.QPushButton()
        dock_btn.setFixedSize(int(style.ICON_WIDTH * 1.01), int(style.ICON_HEIGHT * 1.01))
        dock_btn.setIcon(QtGui.QIcon(self.getImage("dock_icon.png")))
        dock_btn.setIconSize(QtCore.QSize(int(style.ICON_WIDTH * 1.01) - 2, int(style.ICON_HEIGHT * 1.01) - 2))
        dock_btn.setToolTip("Dock Position")
        dock_btn.installEventFilter(_tooltip_filter)
        dock_btn.setFlat(True)
        dock_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255,255,255,80); border-radius: 8px; padding: 2px;  }
        """)
        
        # Create popup menu
        dock_menu = QtWidgets.QMenu(dock_btn)
        dock_menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; }
            QMenu::item:disabled { color: #666; }
            QMenu::indicator { width: 13px; height: 13px; }
            QMenu::indicator:checked { background-color: #4aa3df; border: 1px solid #4aa3df; border-radius: 2px; }
            QMenu::indicator:unchecked { background-color: transparent; border: 1px solid #666; border-radius: 2px; }
        ''')
        
        # Refresh menu
        def refresh_qt_menu():
            dock_menu.clear()
            reset_action = dock_menu.addAction("Reset Animo")
            reset_action.triggered.connect(lambda: self._resetUI())
            shelf_action = dock_menu.addAction("Add Animo to Shelf")
            shelf_action.triggered.connect(lambda: self._addToShelf())
            dock_menu.addSeparator()
            tooltip_action = QAction("Show Tool Tips", dock_menu)
            tooltip_action.setCheckable(True)
            tooltip_action.setChecked(_get_tooltip_pref())
            def toggle_tooltips(checked):
                global _tooltip_manager
                _set_tooltip_pref(checked)
                if _tooltip_manager:
                    _tooltip_manager.set_enabled(checked)
                if checked:
                    cmds.inViewMessage(amg='<span style="color:#4aa3df;">Tool Tips Enabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
                else:
                    cmds.inViewMessage(amg='<span style="color:#ff9900;">Tool Tips Disabled</span>', pos='midCenter', fade=True, fst=200, fad=400)
            tooltip_action.triggered.connect(toggle_tooltips)
            dock_menu.addAction(tooltip_action)
            center_pivot_action = QAction("Keep Selections at Center", dock_menu)
            center_pivot_action.setCheckable(True)
            center_pivot_action.setChecked(_is_center_pivot_active())
            def toggle_center_pivot_6(checked):
                _toggle_center_pivot(checked)
            center_pivot_action.triggered.connect(toggle_center_pivot_6)
            dock_menu.addAction(center_pivot_action)

            dock_menu.addSeparator()
            size_action = dock_menu.addAction("Animo Size Settings...")
            size_action.triggered.connect(_show_size_settings)
        
        dock_menu.aboutToShow.connect(refresh_qt_menu)
        dock_btn.setMenu(dock_menu)
        
        tween_slider = AnimoSlider("TW", (225, 175, 45), "tween")
        tween_slider.setMinimum(-100)
        tween_slider.setMaximum(100)
        tween_slider.setValue(0)
        tween_slider.setFixedWidth(style.scaled(200))
        
        blend_slider = AnimoSlider("BN", (220, 140, 60), "blend")
        blend_slider.setMinimum(-100)
        blend_slider.setMaximum(100)
        blend_slider.setValue(0)
        blend_slider.setFixedWidth(style.scaled(200))
        
        # Right side sliders
        scale_slider = AnimoSlider("SL", (100, 180, 220), "scale")
        scale_slider.setMinimum(-100)
        scale_slider.setMaximum(100)
        scale_slider.setValue(0)
        scale_slider.setFixedWidth(style.scaled(200))
        
        cascade_slider = AnimoSlider("CA", (180, 120, 200), "cascade")
        cascade_slider.setMinimum(0)
        cascade_slider.setMaximum(200)
        cascade_slider.setValue(100)
        cascade_slider.setFixedWidth(style.scaled(200))
        
        # Layout: [stretch] [TW] [BN] [tangent icons] [spacing] [icons] [spacing] [SL] [CA] [stretch] [dock]
        layout.addStretch(1)
        layout.addWidget(tween_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(16)
        layout.addWidget(blend_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(18)
        for tbtn in tangent_buttons:
            layout.addWidget(tbtn, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(20)
        layout.addWidget(icon_container, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(20)
        layout.addWidget(scale_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addSpacing(16)
        layout.addWidget(cascade_slider, 0, QtCore.Qt.AlignVCenter)
        layout.addStretch(1)
        layout.addWidget(dock_btn)
        
        # Insert into parent layout
        parent_layout = target_parent.layout()
        if parent_layout:
            idx = parent_layout.indexOf(target_widget)
            if idx >= 0:
                if below:
                    parent_layout.insertWidget(idx + 1, self.qt_toolbar)
                else:
                    parent_layout.insertWidget(idx, self.qt_toolbar)
                self.qt_toolbar.show()
                return
            else:
                # Try adding to layout if widget not found in it
                parent_layout.addWidget(self.qt_toolbar)
                self.qt_toolbar.show()
                return
        
        # Fallback - just parent to target_parent and show
        self.qt_toolbar.setParent(target_parent)
        self.qt_toolbar.show()
    
    def _buildTimelineFallback(self):
        """Fallback to workspaceControl for timeline mode"""
        cmds.workspaceControl(WorkspaceName, l="", 
            ih=style.TOOLBAR_WIDTH,
            mh=style.TOOLBAR_WIDTH,
            li=True, 
            hp="fixed",
            floating=False, 
            retain=False, 
            collapse=False,
            dockToMainWindow=["bottom", True])
        try:
            mel.eval('workspaceControl -e -dtc "TimeSlider" "top" "{}";'.format(WorkspaceName))
        except:
            pass
        
        # Build horizontal UI using Maya commands
        cmds.setParent(WorkspaceName)
        
        icon_count = len(bar.ICON_DATA)
        cmds.formLayout("animo_formtoolbar", bgc=style.TOOLBAR_BG_COLOR_LIGHT)
        cmds.rowLayout("animo_rowtoolbar", numberOfColumns=(icon_count * 2) + 3,
            bgc=style.TOOLBAR_BG_COLOR_LIGHT, p="animo_formtoolbar")
        
        for i, icon_data in enumerate(bar.ICON_DATA):
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = cmds.iconTextButton(l="", style="iconOnly", w=icon_w, h=icon_h,
                image=self.getImage(icon_file), ann=tooltip)
            
            if menu_options:
                popup = cmds.popupMenu(parent=btn, button=1)
                popup_right = cmds.popupMenu(parent=btn, button=3)
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        cmds.menuItem(divider=True, parent=popup)
                        cmds.menuItem(divider=True, parent=popup_right)
                    else:
                        cmds.menuItem(label=option_name, parent=popup,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
                        cmds.menuItem(label=option_name, parent=popup_right,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
            else:
                cmds.iconTextButton(btn, edit=True,
                    c=lambda ln=launcher_name, tf=tool_folder, ef=entry_func: 
                    bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef))
            
            if i < icon_count - 1:
                cmds.separator(style='none', width=style.ICON_SPACING + 4, p="animo_rowtoolbar")
        
        cmds.separator(style='none', width=style.ICON_SPACING + 10, p="animo_rowtoolbar")
        
        dock_btn = cmds.iconTextButton(l="", style="iconOnly", w=style.scaled(16), h=style.scaled(16),
            image=self.getImage("dock_icon.png"), ann="Dock Position")
        dock_menu = cmds.popupMenu(button=1, parent=dock_btn, 
            postMenuCommand=lambda menu, *args: self._refreshDockMenu(menu))
        
        cmds.formLayout("animo_formtoolbar", edit=True,
            attachForm=[("animo_rowtoolbar", "top", 0), ("animo_rowtoolbar", "bottom", 0)],
            attachPosition=[("animo_rowtoolbar", "left", 0, 50)],
            attachNone=[("animo_rowtoolbar", "right")])
        
        spacing_total = (style.ICON_SPACING + 4) * (icon_count - 1) + (style.ICON_SPACING + 10) + style.scaled(16)
        total_width = (style.ICON_WIDTH * icon_count) + spacing_total
        
        cmds.formLayout("animo_formtoolbar", edit=True,
            attachPosition=[("animo_rowtoolbar", "left", -(total_width // 2), 50)])
        
        cmds.workspaceControl(WorkspaceName, edit=True, resizeHeight=style.TOOLBAR_HEIGHT)
    
    def buildUI(self, is_horizontal=False):
        """Build vertical UI for side dock modes (channelbox/toolbox)"""
        if not cmds.workspaceControl(WorkspaceName, query=True, exists=True):
            return
        
        cmds.setParent(WorkspaceName)
        
        for layout_name in ["animo_formtoolbar", "animo_columntoolbar"]:
            try:
                if cmds.layout(layout_name, exists=True):
                    cmds.deleteUI(layout_name)
            except:
                pass
        
        icon_count = len(bar.ICON_DATA)
        
        cmds.formLayout("animo_formtoolbar", bgc=style.TOOLBAR_BG_COLOR)
        cmds.columnLayout("animo_columntoolbar", adj=True, cat=["both", 4],
            bgc=style.TOOLBAR_BG_COLOR, p="animo_formtoolbar")
        
        for i, icon_data in enumerate(bar.ICON_DATA):
            icon_file, tooltip, launcher_name, tool_folder, entry_func = icon_data[:5]
            custom_size = icon_data[5] if len(icon_data) > 5 else None
            offset = icon_data[6] if len(icon_data) > 6 else None
            menu_options = icon_data[7] if len(icon_data) > 7 else None
            
            icon_w = style.scaled(custom_size[0]) if custom_size else style.ICON_WIDTH
            icon_h = style.scaled(custom_size[1]) if custom_size else style.ICON_HEIGHT
            
            btn = cmds.iconTextButton(l="", style="iconOnly", w=icon_w, h=icon_h,
                image=self.getImage(icon_file), ann=tooltip, p="animo_columntoolbar")
            
            if menu_options:
                # Create popup menu for this button
                popup = cmds.popupMenu(parent=btn, button=1)
                popup_right = cmds.popupMenu(parent=btn, button=3)
                for menu_item in menu_options:
                    option_name = menu_item[0]
                    option_launcher = menu_item[1]
                    option_tool_folder = menu_item[2] if len(menu_item) > 2 else None
                    if option_name == "---":
                        cmds.menuItem(divider=True, parent=popup)
                        cmds.menuItem(divider=True, parent=popup_right)
                    else:
                        cmds.menuItem(label=option_name, parent=popup,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
                        cmds.menuItem(label=option_name, parent=popup_right,
                            c=lambda x, ln=option_launcher, tf=option_tool_folder: bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, None))
            else:
                cmds.iconTextButton(btn, edit=True,
                    c=lambda ln=launcher_name, tf=tool_folder, ef=entry_func:
                    bar.run_launcher(ANIMO_DATA_PATH, ICONS_PATH, MAYA_VERSION, ln, tf, ef))
            
            try:
                btn_widget = wrapInstance(int(mui.MQtUtil.findControl(btn)), QtWidgets.QWidget)
                btn_widget.setToolTip(tooltip)
                btn_widget.installEventFilter(_tooltip_filter)
                btn_widget.setFixedSize(icon_w, icon_h)
                if offset:
                    btn_widget.setStyleSheet("margin-left: {}px; margin-right: {}px;".format(
                        max(0, offset[0]), max(0, -offset[0])))
            except:
                pass
            
            cmds.separator(style='none', height=style.ICON_SPACING_VERTICAL, p="animo_columntoolbar")
        
        dock_btn = cmds.iconTextButton(l="", style="iconOnly", w=style.scaled(16), h=style.scaled(16),
            image=self.getImage("dock_icon.png"), ann="Dock Position", p="animo_columntoolbar")
        dock_menu = cmds.popupMenu(button=1, parent=dock_btn,
            postMenuCommand=lambda menu, *args: self._refreshDockMenu(menu))
        
        cmds.formLayout("animo_formtoolbar", edit=True,
            attachForm=[("animo_columntoolbar", "left", 0), ("animo_columntoolbar", "right", 0)],
            attachPosition=[("animo_columntoolbar", "top", 0, 50)],
            attachNone=[("animo_columntoolbar", "bottom")])
        
        total_h = (style.ICON_HEIGHT * icon_count) + (style.ICON_SPACING_VERTICAL * (icon_count + 1)) + style.scaled(16)
        cmds.formLayout("animo_formtoolbar", edit=True,
            attachPosition=[("animo_columntoolbar", "top", -(total_h // 2), 50)])


try:
    from PySide2.QtCore import QTimer
except ImportError:
    from PySide6.QtCore import QTimer

# Clean up existing workspace control
if cmds.workspaceControl(WorkspaceName, query=True, exists=True):
    cmds.deleteUI(WorkspaceName, control=True)

# Clean up ALL existing Qt toolbars (not just one)
maya_main_ptr = mui.MQtUtil.mainWindow()
if maya_main_ptr:
    maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
    # Find ALL widgets with this object name
    existing_toolbars = maya_main.findChildren(QtWidgets.QWidget, "animo_qt_toolbar")
    for existing in existing_toolbars:
        try:
            existing.hide()
            existing.setParent(None)
            existing.deleteLater()
        except:
            pass

# Module-level quit handler - cleans up Animo when Maya quits
_animo_quit_job = None

def _animo_quit_cleanup():
    """Clean up Animo when Maya quits"""
    try:
        # Check if Animo is visible
        animo_visible = False
        qt_toolbar_visible = False
        
        if cmds.workspaceControl('animo', exists=True):
            animo_visible = cmds.workspaceControl('animo', query=True, visible=True)
        
        # Check Qt toolbar
        existing_qt_toolbar = None
        try:
            maya_main_ptr = mui.MQtUtil.mainWindow()
            if maya_main_ptr:
                maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
                existing_qt_toolbar = maya_main.findChild(QtWidgets.QWidget, "animo_qt_toolbar")
                if existing_qt_toolbar and existing_qt_toolbar.isVisible():
                    qt_toolbar_visible = True
        except:
            pass
        
        # Only do cleanup if Animo is actually running
        if not (animo_visible or qt_toolbar_visible):
            return
        
        # Hide the toolbar
        if existing_qt_toolbar:
            try:
                existing_qt_toolbar.hide()
            except:
                pass
        
        if cmds.workspaceControl('animo', exists=True):
            cmds.workspaceControl('animo', edit=True, visible=False)
    except:
        pass

def _animo_startup():
    """Deferred startup to ensure Maya is fully ready"""
    global _animo_quit_job
    try:
        _animo_quit_job = cmds.scriptJob(event=["quitApplication", _animo_quit_cleanup])
    except:
        pass
    
    # Restore Keep Selections at Center if it was enabled (silent restore)
    try:
        if _get_center_pivot_pref():
            def restore_center_pivot():
                try:
                    if ICONS_PATH not in sys.path:
                        sys.path.insert(0, ICONS_PATH)
                    for mod_name in list(sys.modules.keys()):
                        if 'KeepSelectionsCenter' in mod_name:
                            del sys.modules[mod_name]
                    import KeepSelectionsCenter
                    KeepSelectionsCenter.activateCenterPivot()
                except:
                    pass
            QTimer.singleShot(500, restore_center_pivot)
    except:
        pass
    
    tb = toolbar()
    QTimer.singleShot(200, tb.startUI)


# Defer startup to ensure Maya is fully initialized (critical for Mac)
try:
    cmds.evalDeferred(_animo_startup, lowestPriority=True)
except:
    # Fallback for edge cases
    _animo_startup()