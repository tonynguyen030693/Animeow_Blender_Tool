from __future__ import division
from __future__ import absolute_import

import json
import os
import glob
import sys
import platform
import copy
import time as time_module
import math

from maya import cmds
from maya import mel
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

try:
    import maya.api.OpenMaya as om2
    import maya.api.OpenMayaAnim as oma2
    API2_AVAILABLE = True
except ImportError:
    API2_AVAILABLE = False

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    _max = builtins.max
    _min = builtins.min
    _int = builtins.int
    _str = builtins.str
    _range = builtins.range
except Exception:
    _max = max
    _min = min
    _int = int
    _str = str
    _range = range

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtGui, QtCore
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1


# DPI Scaling Utility
# RULES:
# - Use dpi() for: heights, widths, margins, padding, spacing, icon sizes
# - Do NOT use dpi() for: font-size (pt), border-radius, border-width
#   These look best at fixed pixel values regardless of DPI.

# Base DPI (100% scaling on Windows)
BASE_DPI = 96.0

# Scale factor - set once when UI is created, then frozen
_scale_factor = None


def get_screen_for_widget(widget):
    """Get the screen that contains the widget's center point."""
    if widget is None:
        return None
    
    try:
        app = QtWidgets.QApplication.instance()
        if not app:
            return None
        
        # Get the window's global position and size
        pos = widget.pos()
        size = widget.size()
        
        # Calculate center point in global coordinates
        center_x = pos.x() + size.width() // 2
        center_y = pos.y() + size.height() // 2
        center_point = QtCore.QPoint(center_x, center_y)
        
        # Find which screen contains this point
        screen = app.screenAt(center_point)
        if screen:
            return screen
        
        # Fallback to primary screen
        return app.primaryScreen()
    except:
        return None


def get_scale_factor_for_screen(screen=None):
    """Get the scale factor for a specific screen (always fresh, no caching)."""
    try:
        if screen:
            return screen.logicalDotsPerInch() / BASE_DPI
        
        app = QtWidgets.QApplication.instance()
        if app:
            primary = app.primaryScreen()
            if primary:
                return primary.logicalDotsPerInch() / BASE_DPI
    except:
        pass
    
    return 1.0


def get_scale_factor():
    """Get the scale factor used for building UI."""
    global _scale_factor
    
    # Check for manual override first
    if cmds.optionVar(exists="esnTransifyScale"):
        override = cmds.optionVar(q="esnTransifyScale")
        if override:
            return _max(0.5, _min(override, 3.0))
    
    if _scale_factor is not None:
        return _scale_factor
    
    # First time - detect from primary screen
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                _scale_factor = screen.logicalDotsPerInch() / BASE_DPI
            else:
                _scale_factor = 1.0
        else:
            _scale_factor = 1.0
    except:
        _scale_factor = 1.0
    
    return _scale_factor


def set_scale_factor(value):
    """Explicitly set the scale factor (call before building UI)."""
    global _scale_factor
    _scale_factor = value


def reset_scale_factor():
    """Reset scale factor so it will be recalculated."""
    global _scale_factor
    _scale_factor = None


def dpi(value):
    """Scale a PIXEL value by the screen DPI.
    
    Use for: heights, widths, margins, padding, spacing, icon sizes
    Do NOT use for: font-size, border-radius, border-width
    """
    return int(value * get_scale_factor())


def dpif(value):
    """Scale a pixel value by the screen DPI, return as float."""
    return value * get_scale_factor()


# Keep old function name for compatibility
def scale_size(size):
    return dpi(size)


def is_macos():
    return platform.system() == "Darwin"


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(_int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def get_dialog_stylesheet():
    """Return the common stylesheet for styled dialogs with DPI scaling."""
    return """
        QDialog {{
            background-color: rgb(38, 38, 38);
            color: #E0E0E0;
        }}
        QLabel {{
            color: #E0E0E0;
            background: transparent;
        }}
        QPushButton {{
            background-color: #3A3A3A;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #E0E0E0;
            padding: {0}px {1}px;
            font-size: 8pt;
        }}
        QPushButton:hover {{
            background-color: #4A4A4A;
        }}
        QPushButton:pressed {{
            background-color: #2A2A2A;
        }}
        QPushButton#primaryBtn {{
            background-color: #3A7BC8;
            border: none;
        }}
        QPushButton#primaryBtn:hover {{
            background-color: #4A8BD8;
        }}
    """.format(dpi(8), dpi(16))


def show_styled_error(title, message):
    """Show a styled error dialog with OK button."""
    parent = get_maya_main_window()
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    dialog.setModal(True)
    dialog.setMinimumWidth(dpi(300))
    dialog.setStyleSheet(get_dialog_stylesheet())
    
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(dpi(20), dpi(20), dpi(20), dpi(20))
    layout.setSpacing(dpi(12))
    
    msg_label = QtWidgets.QLabel(message)
    msg_label.setWordWrap(True)
    layout.addWidget(msg_label)
    
    layout.addSpacing(dpi(8))
    
    btn_layout = QtWidgets.QHBoxLayout()
    btn_layout.addStretch()
    
    ok_btn = QtWidgets.QPushButton("OK")
    ok_btn.setObjectName("primaryBtn")
    ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
    ok_btn.setMinimumWidth(dpi(70))
    ok_btn.clicked.connect(dialog.accept)
    
    btn_layout.addWidget(ok_btn)
    layout.addLayout(btn_layout)
    
    dialog.exec_() if PYSIDE_VERSION == 2 else dialog.exec()


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=("TransifyUI_WindowPos", pos_str))


def load_window_position():
    if cmds.optionVar(exists="TransifyUI_WindowPos"):
        try:
            pos_str = cmds.optionVar(q="TransifyUI_WindowPos")
            x, y = pos_str.split(",")
            return QtCore.QPoint(_int(x), _int(y))
        except Exception:
            pass
    return None


def get_all_screens():
    """Get list of all available screens."""
    screens = []
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            if hasattr(app, 'screens'):
                screens = app.screens()
            elif hasattr(app, 'desktop'):
                desktop = app.desktop()
                for i in range(desktop.screenCount()):
                    screens.append(desktop.screenGeometry(i))
    except:
        pass
    return screens


def get_combined_screen_geometry():
    """Get the bounding rect of all screens combined."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return QtCore.QRect(0, 0, 1920, 1080)
    
    try:
        screens = get_all_screens()
        if not screens:
            return QtCore.QRect(0, 0, 1920, 1080)
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for screen in screens:
            if hasattr(screen, 'geometry'):
                geo = screen.geometry()
            else:
                geo = screen  # Already a QRect
            
            min_x = _min(min_x, geo.x())
            min_y = _min(min_y, geo.y())
            max_x = _max(max_x, geo.x() + geo.width())
            max_y = _max(max_y, geo.y() + geo.height())
        
        return QtCore.QRect(_int(min_x), _int(min_y), _int(max_x - min_x), _int(max_y - min_y))
    except:
        return QtCore.QRect(0, 0, 1920, 1080)


def is_position_visible(pos, window_width, window_height, margin=50):
    """Check if a window position would be at least partially visible on any screen."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return False
    
    try:
        screens = get_all_screens()
        if not screens:
            return False
        
        # Window rect
        window_rect = QtCore.QRect(pos.x(), pos.y(), window_width, window_height)
        
        for screen in screens:
            if hasattr(screen, 'geometry'):
                screen_geo = screen.geometry()
            else:
                screen_geo = screen
            
            # Check if at least 'margin' pixels of the window are visible on this screen
            intersection = window_rect.intersected(screen_geo)
            if intersection.width() >= margin and intersection.height() >= margin:
                return True
        
        return False
    except:
        return False


def get_screen_at_position(pos):
    """Get the screen that contains the given position."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return None
    
    try:
        if hasattr(app, 'screenAt'):
            return app.screenAt(pos)
        else:
            # Fallback for older Qt
            screens = get_all_screens()
            for screen in screens:
                if hasattr(screen, 'geometry'):
                    geo = screen.geometry()
                else:
                    geo = screen
                if geo.contains(pos):
                    return screen
    except:
        pass
    return None


def get_center_of_primary_screen():
    """Get the center point of the primary screen."""
    app = QtWidgets.QApplication.instance()
    if not app:
        return QtCore.QPoint(960, 540)
    
    try:
        if hasattr(app, 'primaryScreen'):
            screen = app.primaryScreen()
            if screen:
                geo = screen.geometry()
                return QtCore.QPoint(geo.x() + geo.width() // 2, geo.y() + geo.height() // 2)
        elif hasattr(app, 'desktop'):
            desktop = app.desktop()
            geo = desktop.screenGeometry()
            return QtCore.QPoint(geo.width() // 2, geo.height() // 2)
    except:
        pass
    return QtCore.QPoint(960, 540)


if API2_AVAILABLE:
    TANGENT_ENUM_MAP = {
        "global": oma2.MFnAnimCurve.kTangentGlobal,
        "fixed": oma2.MFnAnimCurve.kTangentFixed,
        "linear": oma2.MFnAnimCurve.kTangentLinear,
        "flat": oma2.MFnAnimCurve.kTangentFlat,
        "smooth": oma2.MFnAnimCurve.kTangentSmooth,
        "spline": oma2.MFnAnimCurve.kTangentSmooth,
        "step": oma2.MFnAnimCurve.kTangentStep,
        "stepped": oma2.MFnAnimCurve.kTangentStep,
        "slow": oma2.MFnAnimCurve.kTangentSlow,
        "fast": oma2.MFnAnimCurve.kTangentFast,
        "clamped": oma2.MFnAnimCurve.kTangentClamped,
        "plateau": oma2.MFnAnimCurve.kTangentPlateau,
        "stepnext": oma2.MFnAnimCurve.kTangentStepNext,
        "stepNext": oma2.MFnAnimCurve.kTangentStepNext,
        "auto": oma2.MFnAnimCurve.kTangentAuto,
    }
    INFINITY_ENUM_MAP = {
        "constant": oma2.MFnAnimCurve.kConstant,
        "linear": oma2.MFnAnimCurve.kLinear,
        "cycle": oma2.MFnAnimCurve.kCycle,
        "cycleRelative": oma2.MFnAnimCurve.kCycleRelative,
        "oscillate": oma2.MFnAnimCurve.kOscillate,
    }
    
    # Reverse map: API enum to string
    TANGENT_ENUM_TO_STRING = {
        oma2.MFnAnimCurve.kTangentGlobal: "global",
        oma2.MFnAnimCurve.kTangentFixed: "fixed",
        oma2.MFnAnimCurve.kTangentLinear: "linear",
        oma2.MFnAnimCurve.kTangentFlat: "flat",
        oma2.MFnAnimCurve.kTangentSmooth: "spline",
        oma2.MFnAnimCurve.kTangentStep: "step",
        oma2.MFnAnimCurve.kTangentSlow: "slow",
        oma2.MFnAnimCurve.kTangentFast: "fast",
        oma2.MFnAnimCurve.kTangentClamped: "clamped",
        oma2.MFnAnimCurve.kTangentPlateau: "plateau",
        oma2.MFnAnimCurve.kTangentStepNext: "stepnext",
        oma2.MFnAnimCurve.kTangentAuto: "auto",
    }
else:
    TANGENT_ENUM_MAP = {}
    INFINITY_ENUM_MAP = {}
    TANGENT_ENUM_TO_STRING = {}


class OpenMayaAnimHelper(object):
    
    @staticmethod
    def get_mobj_from_name(name):
        sel = om.MSelectionList()
        try:
            sel.add(name)
            mobj = om.MObject()
            sel.getDependNode(0, mobj)
            return mobj
        except Exception:
            return None
    
    @staticmethod
    def get_plug_from_attr(obj_attr):
        try:
            sel = om.MSelectionList()
            sel.add(obj_attr)
            plug = om.MPlug()
            sel.getPlug(0, plug)
            return plug
        except Exception:
            return None
    
    @staticmethod
    def get_anim_curve_from_plug(plug):
        if plug is None or plug.isNull():
            return None
        
        try:
            if plug.isConnected():
                connections = om.MPlugArray()
                plug.connectedTo(connections, True, False)
                
                for i in _range(connections.length()):
                    node = connections[i].node()
                    if node.hasFn(om.MFn.kAnimCurve):
                        return oma.MFnAnimCurve(node)
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_curve_data_fast(curve_fn):
        if curve_fn is None:
            return None
        
        try:
            num_keys = curve_fn.numKeys()
            if num_keys == 0:
                return None
            
            times = []
            values = []
            
            for i in _range(num_keys):
                time_val = curve_fn.time(i)
                times.append(time_val.value())
                values.append(curve_fn.value(i))
            
            return {"times": times, "values": values, "num_keys": num_keys}
        except Exception:
            return None
    
    @staticmethod
    def get_selected_objects():
        sel = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(sel)
        
        objects = []
        for i in _range(sel.length()):
            try:
                dag_path = om.MDagPath()
                sel.getDagPath(i, dag_path)
                objects.append(dag_path.fullPathName())
            except Exception:
                try:
                    mobj = om.MObject()
                    sel.getDependNode(i, mobj)
                    dep_fn = om.MFnDependencyNode(mobj)
                    objects.append(dep_fn.name())
                except Exception:
                    pass
        
        return objects
    
    @staticmethod
    def get_attribute_value_fast(obj_attr):
        plug = OpenMayaAnimHelper.get_plug_from_attr(obj_attr)
        if plug is None:
            return None
        
        try:
            attr_obj = plug.attribute()
            api_type = attr_obj.apiType()
            
            if api_type in (om.MFn.kNumericAttribute, om.MFn.kDoubleLinearAttribute, 
                           om.MFn.kDoubleAngleAttribute, om.MFn.kTimeAttribute):
                return plug.asDouble()
            elif api_type == om.MFn.kTypedAttribute:
                return plug.asString()
            else:
                return plug.asDouble()
        except Exception:
            return None
    
    @staticmethod
    def set_attribute_value_fast(obj_attr, value):
        plug = OpenMayaAnimHelper.get_plug_from_attr(obj_attr)
        if plug is None:
            return False
        
        try:
            if plug.isLocked():
                return False
            
            plug.setDouble(float(value))
            return True
        except Exception:
            return False
    
    @staticmethod
    def set_attribute_value_api2(obj_attr, value):
        """Set attribute value using API 2.0 - faster than cmds"""
        if not API2_AVAILABLE:
            return False
        try:
            sel = om2.MSelectionList()
            sel.add(obj_attr)
            plug = sel.getPlug(0)
            
            if plug.isLocked:
                return False
            
            plug.setDouble(float(value))
            return True
        except:
            return False
    
    @staticmethod
    def get_plug_api2(obj_attr):
        if not API2_AVAILABLE:
            return None
        try:
            sel = om2.MSelectionList()
            sel.add(obj_attr)
            return sel.getPlug(0)
        except Exception:
            return None
    
    @staticmethod
    def get_or_create_anim_curve_api2(obj_attr):
        if not API2_AVAILABLE:
            return None
        try:
            plug = OpenMayaAnimHelper.get_plug_api2(obj_attr)
            if plug is None:
                return None
            
            if plug.isConnected:
                source = plug.source()
                if not source.isNull:
                    node = source.node()
                    if node.hasFn(om2.MFn.kAnimCurve):
                        return oma2.MFnAnimCurve(node)
            
            attr_obj = plug.attribute()
            if attr_obj.hasFn(om2.MFn.kDoubleLinearAttribute):
                curve_type = oma2.MFnAnimCurve.kAnimCurveTL
            elif attr_obj.hasFn(om2.MFn.kDoubleAngleAttribute):
                curve_type = oma2.MFnAnimCurve.kAnimCurveTA
            elif attr_obj.hasFn(om2.MFn.kTimeAttribute):
                curve_type = oma2.MFnAnimCurve.kAnimCurveTT
            else:
                curve_type = oma2.MFnAnimCurve.kAnimCurveTU
            
            curve_fn = oma2.MFnAnimCurve()
            curve_fn.create(plug, curve_type)
            return curve_fn
        except Exception:
            return None
    
    @staticmethod
    def get_anim_curve_fn_api2(curve_name):
        """Get MFnAnimCurve from anim curve node name using API 2.0"""
        if not API2_AVAILABLE:
            return None
        try:
            sel = om2.MSelectionList()
            sel.add(curve_name)
            node = sel.getDependNode(0)
            if node.hasFn(om2.MFn.kAnimCurve):
                return oma2.MFnAnimCurve(node)
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_curve_data_api2(curve_name, key_times=None):
        """Read keyframe and tangent data from curve using API 2.0
        
        Returns: (keyframe_data, tangent_data, weighted, is_angle) or None
        keyframe_data: [[time, value, breakdown], ...]
        tangent_data: [[in_type, out_type, in_angle, in_weight, out_angle, out_weight, lock, weight_lock], ...]
        """
        if not API2_AVAILABLE:
            return None
        
        try:
            curve_fn = OpenMayaAnimHelper.get_anim_curve_fn_api2(curve_name)
            if curve_fn is None:
                return None
            
            num_keys = curve_fn.numKeys
            if num_keys == 0:
                return None
            
            weighted = curve_fn.isWeighted
            is_angle = curve_fn.animCurveType == oma2.MFnAnimCurve.kAnimCurveTA
            
            keyframe_data = []
            tangent_data = []
            
            # Build set of times to copy (if key_times specified)
            if key_times is not None:
                key_times_set = set(key_times)
            else:
                key_times_set = None
            
            for i in range(num_keys):
                time_val = curve_fn.input(i).value
                
                # Skip if not in requested key times
                if key_times_set is not None and time_val not in key_times_set:
                    continue
                
                value = curve_fn.value(i)
                # Convert radians to degrees for rotation curves (to match cmds format)
                if is_angle:
                    value = math.degrees(value)
                
                breakdown = curve_fn.isBreakdown(i)
                
                # Get tangent types
                in_type_enum = curve_fn.inTangentType(i)
                out_type_enum = curve_fn.outTangentType(i)
                
                # Get tangent angle/weight using API 2.0 (matches cmds exactly!)
                in_angle_obj, in_weight = curve_fn.getTangentAngleWeight(i, True)
                out_angle_obj, out_weight = curve_fn.getTangentAngleWeight(i, False)
                
                # Convert MAngle to degrees
                in_angle = in_angle_obj.asDegrees()
                out_angle = out_angle_obj.asDegrees()
                
                lock = curve_fn.tangentsLocked(i)
                weight_lock = curve_fn.weightsLocked(i)
                
                # Convert enum to string
                in_type_str = TANGENT_ENUM_TO_STRING.get(in_type_enum, "auto")
                out_type_str = TANGENT_ENUM_TO_STRING.get(out_type_enum, "auto")
                
                keyframe_data.append([time_val, value, breakdown])
                # Store: [in_type, out_type, in_angle, in_weight, out_angle, out_weight, lock, weight_lock]
                tangent_data.append([in_type_str, out_type_str, in_angle, in_weight, out_angle, out_weight, lock, weight_lock])
            
            return (keyframe_data, tangent_data, weighted, is_angle)
        except Exception:
            return None
    
    @staticmethod
    def get_curve_name_from_attr(obj_attr):
        """Get anim curve node name from attribute string"""
        if not API2_AVAILABLE:
            return None
        try:
            plug = OpenMayaAnimHelper.get_plug_api2(obj_attr)
            if plug is None or not plug.isConnected:
                return None
            source = plug.source()
            if source.isNull:
                return None
            node = source.node()
            if node.hasFn(om2.MFn.kAnimCurve):
                return om2.MFnDependencyNode(node).name()
            return None
        except Exception:
            return None
    
    @staticmethod
    def apply_curve_batch_api2(obj_attr, keyframe_data, tangent_data, weighted, infinity, time_offset):
        if not API2_AVAILABLE or not keyframe_data:
            return False
        
        try:
            curve_fn = OpenMayaAnimHelper.get_or_create_anim_curve_api2(obj_attr)
            if curve_fn is None:
                return False
            
            curve_fn.setIsWeighted(weighted if weighted else False)
            
            if infinity:
                pre_inf = INFINITY_ENUM_MAP.get(infinity[0], oma2.MFnAnimCurve.kConstant)
                post_inf = INFINITY_ENUM_MAP.get(infinity[1], oma2.MFnAnimCurve.kConstant) if len(infinity) > 1 else oma2.MFnAnimCurve.kConstant
                curve_fn.setPreInfinityType(pre_inf)
                curve_fn.setPostInfinityType(post_inf)
            
            # Add keys - use cmds.setKeyframe for proper undo support
            for kf in keyframe_data:
                time_val = kf[0] + time_offset
                value = float(kf[1])
                try:
                    cmds.setKeyframe(obj_attr, time=time_val, value=value)
                except:
                    pass
            
            # Collect all tangent data
            all_times = []
            in_types = []
            out_types = []
            in_angles = []
            in_weights = []
            out_angles = []
            out_weights = []
            breakdown_times = []
            lock_times = []
            weight_lock_times = []
            
            for i, tangent in enumerate(tangent_data):
                if i >= len(keyframe_data):
                    break
                
                time_val = keyframe_data[i][0] + time_offset
                all_times.append(time_val)
                
                in_type = tangent[0] if len(tangent) > 0 else "auto"
                out_type = tangent[1] if len(tangent) > 1 else "auto"
                
                in_types.append(in_type)
                out_types.append(out_type)
                in_angles.append(float(tangent[2]) if len(tangent) > 2 else 0.0)
                in_weights.append(float(tangent[3]) if len(tangent) > 3 else 1.0)
                out_angles.append(float(tangent[4]) if len(tangent) > 4 else 0.0)
                out_weights.append(float(tangent[5]) if len(tangent) > 5 else 1.0)
                
                lock = tangent[6] if len(tangent) > 6 else False
                weight_lock = tangent[7] if len(tangent) > 7 else False
                
                if len(keyframe_data[i]) > 2 and keyframe_data[i][2]:
                    breakdown_times.append(time_val)
                if lock:
                    lock_times.append(time_val)
                if weight_lock:
                    weight_lock_times.append(time_val)
            
            # Check if all tangents are same type (can batch entire curve)
            unique_in_types = set(in_types)
            unique_out_types = set(out_types)
            
            # IMPORTANT: First unlock ALL keys, then set tangents, then re-lock only the ones that need it
            # This prevents Maya from auto-locking when setting fixed tangents
            for time_val in all_times:
                try:
                    cmds.keyTangent(obj_attr, time=(time_val, time_val), lock=False)
                except:
                    pass
            
            # BATCH: If all keys have same non-fixed type, one call for whole curve
            if len(unique_in_types) == 1 and list(unique_in_types)[0] != "fixed":
                try:
                    cmds.keyTangent(obj_attr, inTangentType=list(unique_in_types)[0])
                except:
                    pass
            else:
                # Mixed types - set per key
                for i, time_val in enumerate(all_times):
                    t = (time_val, time_val)
                    try:
                        if in_types[i] == "fixed":
                            cmds.keyTangent(obj_attr, time=t, inTangentType="fixed",
                                           inAngle=in_angles[i], inWeight=in_weights[i])
                        else:
                            cmds.keyTangent(obj_attr, time=t, inTangentType=in_types[i])
                    except:
                        pass
            
            if len(unique_out_types) == 1 and list(unique_out_types)[0] != "fixed":
                try:
                    cmds.keyTangent(obj_attr, outTangentType=list(unique_out_types)[0])
                except:
                    pass
            else:
                # Mixed types - set per key
                for i, time_val in enumerate(all_times):
                    t = (time_val, time_val)
                    try:
                        if out_types[i] == "fixed":
                            cmds.keyTangent(obj_attr, time=t, outTangentType="fixed",
                                           outAngle=out_angles[i], outWeight=out_weights[i])
                        else:
                            cmds.keyTangent(obj_attr, time=t, outTangentType=out_types[i])
                    except:
                        pass
            
            # Set breakdowns
            for t in breakdown_times:
                try:
                    cmds.keyframe(obj_attr, time=(t, t), breakdown=True)
                except:
                    pass
            
            # Set locks (only if any locked)
            if lock_times:
                for t in lock_times:
                    try:
                        cmds.keyTangent(obj_attr, time=(t, t), lock=True)
                    except:
                        pass
            
            if weight_lock_times:
                for t in weight_lock_times:
                    try:
                        cmds.keyTangent(obj_attr, time=(t, t), weightLock=True)
                    except:
                        pass
            
            return True
        except Exception:
            return False


class AnimationCopyPasteJson(object):
    
    def __init__(self):
        self.documents_path = self.get_documents_path()
        self.om_helper = OpenMayaAnimHelper()
    
    def get_documents_path(self):
        if sys.platform.startswith("win"):
            try:
                from ctypes import windll, wintypes, create_unicode_buffer
                CSIDL_PERSONAL = 5
                SHGFP_TYPE_CURRENT = 0
                buf = create_unicode_buffer(wintypes.MAX_PATH)
                windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
                docs_dir = buf.value
            except Exception:
                docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        
        anim_tools_folder = os.path.join(docs_dir, "animTools", "animationData")
        if not os.path.exists(anim_tools_folder):
            os.makedirs(anim_tools_folder)
        return anim_tools_folder
    
    def get_rotation_order_name(self, value):
        rot_order_names = {0: "xyz", 1: "yzx", 2: "zxy", 3: "xzy", 4: "yxz", 5: "zyx"}
        return rot_order_names.get(value, "xyz")
    
    def get_rotation_orders_from_objects(self, objects):
        rotation_orders = {}
        for obj in objects:
            if not obj or not cmds.objExists(obj):
                continue
            try:
                short_name = obj.split("|")[-1]
                if ":" in short_name:
                    base_name = short_name.split(":")[-1]
                else:
                    base_name = short_name
                rot_order_value = cmds.getAttr(obj + ".rotateOrder")
                rotation_orders[base_name] = {"short_name": short_name, "rotation_order": self.get_rotation_order_name(rot_order_value), "rotation_order_value": rot_order_value}
            except Exception:
                pass
        return rotation_orders
    
    def check_rotation_order_differences(self, saved_rotation_orders, target_objects):
        if not saved_rotation_orders:
            return []
        differences = []
        for obj in target_objects:
            if not obj or not cmds.objExists(obj):
                continue
            try:
                short_name = obj.split("|")[-1]
                if ":" in short_name:
                    base_name = short_name.split(":")[-1]
                else:
                    base_name = short_name
                saved_data = saved_rotation_orders.get(base_name)
                if not saved_data:
                    continue
                current_order = cmds.getAttr(obj + ".rotateOrder")
                saved_order = saved_data.get("rotation_order_value", 0)
                if current_order != saved_order:
                    differences.append({"object": obj, "current_order": current_order, "saved_order": saved_order, "current_order_name": self.get_rotation_order_name(current_order), "saved_order_name": self.get_rotation_order_name(saved_order)})
            except Exception:
                pass
        return differences
    
    def show_rotation_order_warning(self, differences):
        if not differences:
            return "continue"
        
        obj_list = "\n".join(["{}: {} -> {}".format(d["object"].split("|")[-1], d["current_order_name"].upper(), d["saved_order_name"].upper()) for d in differences[:10]])
        if len(differences) > 10:
            obj_list += "\n... and {} more".format(len(differences) - 10)
        
        # Create custom styled dialog
        parent = get_maya_main_window()
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Rotation Order Mismatch")
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dialog.setModal(True)
        dialog.setMinimumWidth(dpi(420))
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: rgb(38, 38, 38);
                color: #E0E0E0;
            }}
            QLabel {{
                color: #E0E0E0;
                background: transparent;
            }}
            QPushButton {{
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #E0E0E0;
                padding: {0}px {1}px;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
            QPushButton#changeBtn {{
                background-color: #3A7BC8;
                border: none;
            }}
            QPushButton#changeBtn:hover {{
                background-color: #4A8BD8;
            }}
        """.format(dpi(8), dpi(16)))
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(dpi(20), dpi(20), dpi(20), dpi(20))
        layout.setSpacing(dpi(12))
        
        # Message
        msg_label = QtWidgets.QLabel("The following objects have different rotation orders:")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        # Object list
        list_label = QtWidgets.QLabel(obj_list)
        list_label.setStyleSheet("color: #AAAAAA; font-family: monospace; padding: {0}px; background-color: #2A2A2A; border-radius: 4px;".format(dpi(8)))
        list_label.setWordWrap(True)
        layout.addWidget(list_label)
        
        # Question
        question_label = QtWidgets.QLabel("Change rotation order to match saved animation?")
        question_label.setWordWrap(True)
        layout.addWidget(question_label)
        
        layout.addSpacing(dpi(8))
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(12))
        
        change_btn = QtWidgets.QPushButton("Change and Paste")
        change_btn.setObjectName("changeBtn")
        change_btn.setCursor(QtCore.Qt.PointingHandCursor)
        change_btn.setMinimumWidth(dpi(110))
        
        keep_btn = QtWidgets.QPushButton("Keep and Paste")
        keep_btn.setCursor(QtCore.Qt.PointingHandCursor)
        keep_btn.setMinimumWidth(dpi(100))
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.setMinimumWidth(dpi(70))
        
        btn_layout.addWidget(change_btn)
        btn_layout.addWidget(keep_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Store result
        dialog.result_choice = "cancel"
        
        def on_change():
            dialog.result_choice = "change"
            dialog.accept()
        
        def on_keep():
            dialog.result_choice = "continue"
            dialog.accept()
        
        def on_cancel():
            dialog.result_choice = "cancel"
            dialog.reject()
        
        change_btn.clicked.connect(on_change)
        keep_btn.clicked.connect(on_keep)
        cancel_btn.clicked.connect(on_cancel)
        
        dialog.exec_() if PYSIDE_VERSION == 2 else dialog.exec()
        
        return dialog.result_choice
    
    def change_rotation_order(self, obj, target_order):
        if not cmds.objExists(obj):
            return False
        try:
            target_order_name = self.get_rotation_order_name(target_order)
            current_time = cmds.currentTime(query=True)
            keys = cmds.keyframe(obj, attribute=["rx", "ry", "rz"], query=True, timeChange=True)
            if keys:
                keys = sorted(list(set(keys)))
                temp_loc = cmds.spaceLocator(name="roo_tempLoc")[0]
                try:
                    cmds.refresh(suspend=True)
                    cmds.evaluationManager(mode="off")
                    
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.matchTransform(temp_loc, obj, rotation=True)
                        cmds.setKeyframe(temp_loc, attribute=["rx", "ry", "rz"])
                    
                    cmds.cutKey(obj, attribute="rotateOrder", clear=True)
                    cmds.xform(obj, rotateOrder=target_order_name, preserve=True)
                    
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.matchTransform(obj, temp_loc, rotation=True)
                        cmds.setKeyframe(obj, attribute=["rx", "ry", "rz"])
                    
                    cmds.currentTime(current_time)
                    cmds.filterCurve(obj + ".rx", obj + ".ry", obj + ".rz")
                    cmds.selectKey(clear=True)
                finally:
                    # ALWAYS restore refresh and evaluation manager
                    try:
                        cmds.refresh(suspend=False)
                    except:
                        pass
                    try:
                        cmds.evaluationManager(mode="parallel")
                    except:
                        pass
                    if cmds.objExists(temp_loc):
                        cmds.delete(temp_loc)
            else:
                cmds.cutKey(obj, attribute="rotateOrder", clear=True)
                cmds.xform(obj, rotateOrder=target_order_name, preserve=True)
            return True
        except Exception:
            return False
    
    def apply_rotation_order_changes(self, differences):
        for diff in differences:
            self.change_rotation_order(diff["object"], diff["saved_order"])
    
    def check_objects_in_animation_layers(self, objects_to_check):
        anim_layers = cmds.ls(type="animLayer")
        root_layer = cmds.animLayer(q=True, root=True)
        if root_layer and root_layer in anim_layers:
            anim_layers.remove(root_layer)
        
        if not anim_layers:
            return False
        
        objects_in_layers = []
        all_affected_layers = set()
        
        for anim_lyr in anim_layers:
            attrs = cmds.animLayer(anim_lyr, q=True, attribute=True)
            if attrs:
                for attr in attrs:
                    obj_from_attr = attr.split(".")[0]
                    for checked_obj in objects_to_check:
                        checked_short = checked_obj.split("|")[-1]
                        attr_short = obj_from_attr.split("|")[-1]
                        if checked_short == attr_short:
                            if checked_obj not in objects_in_layers:
                                objects_in_layers.append(checked_obj)
                            all_affected_layers.add(anim_lyr)
                            break
        
        if not objects_in_layers:
            return False
        
        cmds.waitCursor(state=False)
        
        # Custom styled dialog
        parent = get_maya_main_window()
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Animation Layer Detected")
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dialog.setModal(True)
        dialog.setMinimumWidth(dpi(350))
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: rgb(38, 38, 38);
                color: #E0E0E0;
            }}
            QLabel {{
                color: #E0E0E0;
                background: transparent;
            }}
            QPushButton {{
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #E0E0E0;
                padding: {0}px {1}px;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
            QPushButton#mergeBtn {{
                background-color: #3A7BC8;
                border: none;
            }}
            QPushButton#mergeBtn:hover {{
                background-color: #4A8BD8;
            }}
        """.format(dpi(8), dpi(16)))
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(dpi(20), dpi(20), dpi(20), dpi(20))
        layout.setSpacing(dpi(12))
        
        msg_label = QtWidgets.QLabel("The selected controls are part of an animation layer, you need to merge the layers first.")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        layout.addSpacing(dpi(8))
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(12))
        btn_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.setMinimumWidth(dpi(70))
        
        merge_btn = QtWidgets.QPushButton("Merge")
        merge_btn.setObjectName("mergeBtn")
        merge_btn.setCursor(QtCore.Qt.PointingHandCursor)
        merge_btn.setMinimumWidth(dpi(70))
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(merge_btn)
        
        layout.addLayout(btn_layout)
        
        cancel_btn.clicked.connect(dialog.reject)
        merge_btn.clicked.connect(dialog.accept)
        
        result = dialog.exec_() if PYSIDE_VERSION == 2 else dialog.exec()
        
        if result:
            self.bake_all_objects_from_layers(objects_in_layers, list(all_affected_layers))
            return False
        else:
            return True
    
    def bake_all_objects_from_layers(self, objects_to_bake, affected_layers):
        try:
            all_anim_layers = cmds.ls(type="animLayer")
            root_layer = cmds.animLayer(q=True, root=True)
            if root_layer and root_layer in all_anim_layers:
                all_anim_layers.remove(root_layer)
            
            original_mute_states = {}
            for layer in all_anim_layers:
                original_mute_states[layer] = cmds.animLayer(layer, q=True, mute=True)
            
            for layer in all_anim_layers:
                if layer not in affected_layers:
                    cmds.animLayer(layer, edit=True, mute=True)
            
            for layer in affected_layers:
                cmds.animLayer(layer, edit=True, mute=False)
            
            try:
                cmds.refresh(suspend=True)
                cmds.evaluationManager(mode="off")
                
                min_time = cmds.playbackOptions(q=True, animationStartTime=True)
                max_time = cmds.playbackOptions(q=True, animationEndTime=True)
                
                cmds.bakeResults(objects_to_bake, sm=True, pok=True, t=(min_time, max_time))
                
                for layer in affected_layers:
                    if cmds.objExists(layer):
                        layer_attrs = cmds.animLayer(layer, q=True, attribute=True)
                        if layer_attrs:
                            for attr in layer_attrs:
                                obj_from_attr = attr.split(".")[0]
                                obj_short = obj_from_attr.split("|")[-1]
                                for obj in objects_to_bake:
                                    obj_check_short = obj.split("|")[-1]
                                    if obj_short == obj_check_short:
                                        try:
                                            cmds.animLayer(layer, edit=True, removeAttribute=attr)
                                        except Exception:
                                            pass
                                        break
                
                for layer in all_anim_layers:
                    if layer not in affected_layers and cmds.objExists(layer):
                        cmds.animLayer(layer, edit=True, mute=original_mute_states[layer])
                
                layers_to_delete = []
                for layer in all_anim_layers:
                    if cmds.objExists(layer):
                        attrs = cmds.animLayer(layer, q=True, attribute=True)
                        if not attrs:
                            layers_to_delete.append(layer)
                
                if layers_to_delete:
                    cmds.delete(layers_to_delete)
            
            except Exception:
                pass
            finally:
                # ALWAYS restore refresh and evaluation manager - viewport should never stay frozen
                try:
                    cmds.refresh(suspend=False)
                except:
                    pass
                try:
                    cmds.evaluationManager(mode="parallel")
                except:
                    pass
        
        except Exception:
            pass
    
    def get_anim_curves(self, force_graph_editor=False):
        anim_curves = cmds.keyframe(query=True, name=True, selected=True)
        visible_panels = cmds.getPanel(visiblePanels=True)
        graph_editor = "graphEditor1" in visible_panels
        get_from = "graphEditor"
        
        if not anim_curves or not graph_editor and not force_graph_editor:
            get_from = "timeline"
            try:
                playback_slider = mel.eval("$temp=$gPlayBackSlider")
                anim_curves = cmds.timeControl(playback_slider, query=True, animCurveNames=True)
            except Exception:
                sel = cmds.ls(selection=True)
                if sel:
                    anim_curves = cmds.keyframe(sel, query=True, name=True)
                else:
                    anim_curves = []
        
        return [anim_curves, get_from]
    
    def get_timeline_range(self, float_val=True):
        try:
            playback_slider = mel.eval("$temp=$gPlayBackSlider")
            range_val = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            if float_val:
                range_val[1] -= 0.0001
            return range_val
        except Exception:
            start = cmds.playbackOptions(query=True, minTime=True)
            end = cmds.playbackOptions(query=True, maxTime=True)
            if float_val:
                end -= 0.0001
            return [start, end]
    
    def get_objects_and_attributes(self, anim_curves):
        if not anim_curves:
            return [[], []]
        
        objects = []
        attributes = []
        
        for node in anim_curves:
            if not cmds.objExists(node):
                objects.append(None)
                attributes.append(None)
                continue
            
            try:
                mobj = self.om_helper.get_mobj_from_name(node.split(".")[0])
                if mobj:
                    curve_fn = oma.MFnAnimCurve(mobj)
                    
                    plug_array = om.MPlugArray()
                    try:
                        curve_fn.getDestinations(plug_array)
                        if plug_array.length() > 0:
                            dest_plug = plug_array[0]
                            obj_name = om.MFnDependencyNode(dest_plug.node()).name()
                            attr_name = dest_plug.partialName(False, False, False, False, False, True)
                            objects.append(obj_name)
                            attributes.append(attr_name)
                            continue
                    except Exception:
                        pass
                
                connections = cmds.listConnections("{}.output".format(node.split(".")[0]),
                                                   source=False, destination=True,
                                                   plugs=True, skipConversionNodes=True)
                if connections:
                    target = connections[0]
                    obj = target.split(".")[0]
                    attr = target.split(".")[-1]
                    objects.append(obj)
                    attributes.append(attr)
                else:
                    objects.append(None)
                    attributes.append(None)
            except Exception:
                objects.append(None)
                attributes.append(None)
        
        return [objects, attributes]
    
    def get_keys_in_range(self, anim_curves, get_from, range_all=None):
        if not anim_curves:
            return []
        
        keys_sel = []
        
        if get_from == "graphEditor":
            for node in anim_curves:
                selected_keys = cmds.keyframe(node, selected=True, query=True, timeChange=True)
                keys_sel.append(selected_keys if selected_keys else [])
        else:
            if range_all is None:
                timeline_range = self.get_timeline_range()
            else:
                timeline_range = None
            
            for node in anim_curves:
                if not cmds.objExists(node):
                    keys_sel.append([])
                    continue
                
                mobj = self.om_helper.get_mobj_from_name(node)
                if mobj:
                    try:
                        curve_fn = oma.MFnAnimCurve(mobj)
                        num_keys = curve_fn.numKeys()
                        all_keys = [curve_fn.time(i).value() for i in _range(num_keys)]
                    except Exception:
                        all_keys = cmds.keyframe(node, query=True, timeChange=True)
                else:
                    all_keys = cmds.keyframe(node, query=True, timeChange=True)
                
                if not all_keys:
                    keys_sel.append([])
                    continue
                
                if range_all or not timeline_range:
                    keys_sel.append(all_keys)
                else:
                    range_keys = [key for key in all_keys
                                  if timeline_range[0] <= key < timeline_range[1]]
                    keys_sel.append(range_keys)
        
        return keys_sel
    
    def get_all_animatable_attributes(self, objects):
        all_obj_attrs = []
        
        common_attrs = [
            "translateX", "translateY", "translateZ",
            "rotateX", "rotateY", "rotateZ",
            "scaleX", "scaleY", "scaleZ",
            "visibility"
        ]
        
        for obj in objects:
            if not cmds.objExists(obj):
                continue
            
            obj_attrs = []
            
            for attr in common_attrs:
                full_attr = "{}.{}".format(obj, attr)
                if cmds.objExists(full_attr) and cmds.getAttr(full_attr, keyable=True):
                    obj_attrs.append(full_attr)
            
            try:
                keyable_attrs = cmds.listAttr(obj, keyable=True) or []
                for attr in keyable_attrs:
                    if attr not in common_attrs:
                        full_attr = "{}.{}".format(obj, attr)
                        if cmds.objExists(full_attr):
                            obj_attrs.append(full_attr)
            except Exception:
                pass
            
            all_obj_attrs.extend(obj_attrs)
        
        return all_obj_attrs
    
    def copy_animation(self, range_mode="selected"):
        cmds.waitCursor(state=True)
        
        try:
            if range_mode == "all":
                selected_objects = self.om_helper.get_selected_objects()
                if not selected_objects:
                    selected_objects = cmds.ls(selection=True)
                
                if not selected_objects:
                    cmds.warning("No objects selected. Please select controls to copy all their animation.")
                    return None
                
                all_obj_attrs = self.get_all_animatable_attributes(selected_objects)
                
                if not all_obj_attrs:
                    cmds.warning("No animatable attributes found on selected objects.")
                    return None
                
                anim_data = self.get_anim_data_from_attributes(all_obj_attrs, range_all=True)
            else:
                anim_data = self.get_anim_data()
            
            return anim_data
        
        finally:
            cmds.waitCursor(state=False)
    
    def get_anim_data_from_attributes(self, obj_attrs, range_all=False):
        if not obj_attrs:
            cmds.warning("No object attributes found.")
            return None
        
        current_time = cmds.currentTime(query=True)
        
        anim_data = {
            "objects": [],
            "animData": []
        }
        
        objects_added = set()
        
        for obj_attr in obj_attrs:
            if not cmds.objExists(obj_attr):
                continue
            
            obj_name = obj_attr.split(".")[0]
            
            if obj_name not in objects_added:
                anim_data["objects"].append(obj_name)
                objects_added.add(obj_name)
            
            plug = self.om_helper.get_plug_from_attr(obj_attr)
            curve_fn = self.om_helper.get_anim_curve_from_plug(plug) if plug else None
            
            if curve_fn and curve_fn.numKeys() > 0:
                try:
                    weighted = cmds.keyTangent(obj_attr, query=True, weightedTangents=True)
                    if weighted:
                        weighted = weighted[0]
                    else:
                        weighted = False
                    
                    infinity = cmds.setInfinity(obj_attr, query=True,
                                                preInfinite=True, postInfinite=True)
                except Exception:
                    weighted = False
                    infinity = ["constant", "constant"]
                
                curve_data = {
                    "objAttr": obj_attr,
                    "curveData": [weighted, infinity],
                    "keyframeData": [],
                    "tangentData": []
                }
                
                try:
                    if range_all:
                        # Use API 2.0 for fast tangent reading
                        curve_name = OpenMayaAnimHelper.get_curve_name_from_attr(obj_attr)
                        if curve_name and API2_AVAILABLE:
                            api_data = OpenMayaAnimHelper.get_curve_data_api2(curve_name, None)
                            if api_data:
                                curve_data["keyframeData"] = api_data[0]
                                curve_data["tangentData"] = api_data[1]
                            else:
                                raise Exception("API 2.0 failed, use fallback")
                        else:
                            raise Exception("No curve name, use fallback")
                
                except Exception:
                    # Fallback to cmds
                    try:
                        num_keys = curve_fn.numKeys()
                        time_change = [curve_fn.time(i).value() for i in _range(num_keys)]
                        value_change = [curve_fn.value(i) for i in _range(num_keys)]
                        breakdowns = cmds.keyframe(obj_attr, query=True, breakdown=True)
                        
                        in_tangent_type = cmds.keyTangent(obj_attr, query=True, inTangentType=True)
                        out_tangent_type = cmds.keyTangent(obj_attr, query=True, outTangentType=True)
                        in_angle = cmds.keyTangent(obj_attr, query=True, inAngle=True)
                        in_weight = cmds.keyTangent(obj_attr, query=True, inWeight=True)
                        out_angle = cmds.keyTangent(obj_attr, query=True, outAngle=True)
                        out_weight = cmds.keyTangent(obj_attr, query=True, outWeight=True)
                        lock = cmds.keyTangent(obj_attr, query=True, lock=True)
                        weight_lock = cmds.keyTangent(obj_attr, query=True, weightLock=True)
                        
                        for j, key_time in enumerate(time_change):
                            breakdown = (key_time in breakdowns) if breakdowns else False
                            
                            keyframe = [time_change[j], value_change[j], breakdown]
                            tangent = [
                                in_tangent_type[j], out_tangent_type[j],
                                in_angle[j], in_weight[j], out_angle[j], out_weight[j],
                                lock[j], weight_lock[j]
                            ]
                            
                            curve_data["keyframeData"].append(keyframe)
                            curve_data["tangentData"].append(tangent)
                    except Exception:
                        continue
                
                anim_data["animData"].append(curve_data)
            
            else:
                try:
                    current_value = self.om_helper.get_attribute_value_fast(obj_attr)
                    if current_value is None:
                        current_value = cmds.getAttr(obj_attr)
                    
                    curve_data = {
                        "objAttr": obj_attr,
                        "curveData": [False, ["constant", "constant"]],
                        "keyframeData": [[current_time, current_value, False]],
                        "tangentData": [["auto", "auto", 0, 0, 0, 0, False, False]]
                    }
                    
                    anim_data["animData"].append(curve_data)
                
                except Exception:
                    continue
        
        return anim_data
    
    def get_anim_data(self, anim_curves=None, range_all=False):
        if anim_curves is None:
            get_curves = self.get_anim_curves(True)
            anim_curves = get_curves[0]
            get_from = get_curves[1]
        else:
            get_from = None
        
        if not anim_curves:
            cmds.warning("No animation curves found.")
            return None
        
        if get_from is None:
            keys_sel = self.get_keys_in_range(anim_curves, "timeline", range_all=True)
        else:
            keys_sel = self.get_keys_in_range(anim_curves, get_from)
        
        if not keys_sel or all(not keys for keys in keys_sel):
            cmds.warning("No keys found to copy.")
            return None
        
        objs_attrs = self.get_objects_and_attributes(anim_curves)
        objects = objs_attrs[0]
        attributes = objs_attrs[1]
        
        anim_data = {
            "objects": objects,
            "animData": []
        }
        
        for i, curve in enumerate(anim_curves):
            if objects[i] is None or not keys_sel[i]:
                continue
            
            obj_attr = "{}.{}".format(objects[i], attributes[i])
            
            try:
                weighted = cmds.keyTangent(curve, query=True, weightedTangents=True)
                if weighted:
                    weighted = weighted[0]
                else:
                    weighted = False
                
                infinity = cmds.setInfinity(obj_attr, query=True,
                                            preInfinite=True, postInfinite=True)
            except Exception:
                weighted = False
                infinity = ["constant", "constant"]
            
            curve_data = {
                "objAttr": obj_attr,
                "curveData": [weighted, infinity],
                "keyframeData": [],
                "tangentData": []
            }
            
            try:
                # Use API 2.0 for fast tangent reading
                if API2_AVAILABLE:
                    api_data = OpenMayaAnimHelper.get_curve_data_api2(curve, keys_sel[i])
                    if api_data:
                        curve_data["keyframeData"] = api_data[0]
                        curve_data["tangentData"] = api_data[1]
                    else:
                        raise Exception("API 2.0 failed, use fallback")
                else:
                    raise Exception("API 2.0 not available, use fallback")
            
            except Exception:
                # Fallback to cmds
                time_range = (keys_sel[i][0], keys_sel[i][-1])
                try:
                    time_change = cmds.keyframe(curve, query=True, time=time_range, timeChange=True)
                    value_change = cmds.keyframe(curve, query=True, time=time_range, valueChange=True)
                    breakdowns = cmds.keyframe(curve, query=True, time=time_range, breakdown=True)
                    
                    in_tangent_type = cmds.keyTangent(curve, query=True, time=time_range, inTangentType=True)
                    out_tangent_type = cmds.keyTangent(curve, query=True, time=time_range, outTangentType=True)
                    in_angle = cmds.keyTangent(curve, query=True, time=time_range, inAngle=True)
                    in_weight = cmds.keyTangent(curve, query=True, time=time_range, inWeight=True)
                    out_angle = cmds.keyTangent(curve, query=True, time=time_range, outAngle=True)
                    out_weight = cmds.keyTangent(curve, query=True, time=time_range, outWeight=True)
                    lock = cmds.keyTangent(curve, query=True, time=time_range, lock=True)
                    weight_lock = cmds.keyTangent(curve, query=True, time=time_range, weightLock=True)
                    
                    for j, key_time in enumerate(keys_sel[i]):
                        if key_time in time_change:
                            idx = time_change.index(key_time)
                            breakdown = (key_time in breakdowns) if breakdowns else False
                            
                            keyframe = [time_change[idx], value_change[idx], breakdown]
                            tangent = [
                                in_tangent_type[idx], out_tangent_type[idx],
                                in_angle[idx], in_weight[idx], out_angle[idx], out_weight[idx],
                                lock[idx], weight_lock[idx]
                            ]
                            
                            curve_data["keyframeData"].append(keyframe)
                            curve_data["tangentData"].append(tangent)
                except Exception:
                    continue
            
            anim_data["animData"].append(curve_data)
        
        return anim_data
    
    def save_to_json(self, anim_data, filename=None, selected_objects=None):
        if not anim_data:
            cmds.warning("No animation data to save.")
            return None
        
        if selected_objects:
            anim_data["rotationOrders"] = self.get_rotation_orders_from_objects(selected_objects)
            anim_data["allSelectedObjects"] = [obj.split("|")[-1] for obj in selected_objects]
        elif "objects" in anim_data and anim_data["objects"]:
            anim_data["rotationOrders"] = self.get_rotation_orders_from_objects(anim_data["objects"])
        
        anim_data["timelineRange"] = [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)]
        
        if not filename:
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                base_name = ".".join(scene_name.split(".")[:-1])
            else:
                base_name = "untitled_scene"
            
            timestamp = time_module.strftime("%Y%m%d_%H%M%S")
            filename = "{}_animation_{}.json".format(base_name, timestamp)
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        filepath = os.path.join(self.documents_path, filename)
        
        try:
            with open(filepath, "w") as f:
                json.dump(anim_data, f, indent=2)
            
            return filepath
        
        except Exception as e:
            error_msg = "Failed to save animation data: {}".format(e)
            show_styled_error("Error", error_msg)
            return None
    
    def copy_all_animation_to_json(self):
        cmds.waitCursor(state=True)
        
        try:
            selected_objects = cmds.ls(selection=True)
            
            if not selected_objects:
                cmds.warning("No objects selected. Please select controls to copy all their animation.")
                return None
            
            cmds.waitCursor(state=False)
            if self.check_objects_in_animation_layers(selected_objects):
                cmds.waitCursor(state=True)  # Restore so finally block can turn it off
                return None
            cmds.waitCursor(state=True)
            
            all_anim_curves = []
            objects_with_curves = set()
            for obj in selected_objects:
                curves = cmds.keyframe(obj, query=True, name=True)
                if curves:
                    all_anim_curves.extend(curves)
                    objects_with_curves.add(obj)
            
            if all_anim_curves:
                anim_data = self.get_anim_data(anim_curves=all_anim_curves, range_all=True)
            else:
                anim_data = {"objects": [], "animData": []}
            
            if anim_data is None:
                anim_data = {"objects": [], "animData": []}
            
            current_time = cmds.currentTime(query=True)
            for obj in selected_objects:
                if obj in objects_with_curves:
                    continue
                short_name = obj.split("|")[-1]
                if short_name not in anim_data["objects"]:
                    anim_data["objects"].append(short_name)
                attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []
                for attr in attrs:
                    obj_attr = "{}.{}".format(obj, attr)
                    short_obj_attr = "{}.{}".format(short_name, attr)
                    try:
                        if not cmds.objExists(obj_attr):
                            continue
                        value = cmds.getAttr(obj_attr)
                        if value is None or isinstance(value, (list, tuple)):
                            continue
                        anim_data["animData"].append({
                            "objAttr": short_obj_attr,
                            "curveData": [False, ["constant", "constant"]],
                            "keyframeData": [[current_time, value, False]],
                            "tangentData": [["auto", "auto", 1.0, 0.0, 1.0, 0.0, False, False]]
                        })
                    except Exception:
                        continue
            
            if not anim_data["animData"]:
                cmds.warning("No animation or attribute data found on selected objects.")
                return None
            
            return self.save_to_json(anim_data, selected_objects=selected_objects)
        
        finally:
            cmds.waitCursor(state=False)
    
    def copy_selected_animation_to_json(self):
        selected_objects = cmds.ls(selection=True)
        anim_data = self.copy_animation(range_mode="selected")
        if anim_data:
            return self.save_to_json(anim_data, selected_objects=selected_objects)
        return None
    
    def get_latest_json_file(self):
        pattern = os.path.join(self.documents_path, "*_animation_*.json")
        json_files = glob.glob(pattern)
        
        if not json_files:
            return None
        
        json_files.sort(key=os.path.getmtime, reverse=True)
        return json_files[0]
    
    def get_all_json_files(self):
        pattern = os.path.join(self.documents_path, "*_animation_*.json")
        json_files = glob.glob(pattern)
        
        if not json_files:
            return []
        
        json_files.sort(key=os.path.getmtime, reverse=True)
        return json_files
    
    def load_animation_data(self, filepath):
        try:
            with open(filepath, "r") as f:
                anim_data = json.load(f)
            
            return anim_data
        
        except Exception as e:
            error_msg = "Failed to load animation data: {}".format(e)
            show_styled_error("Error", error_msg)
            return None
    
    def create_dummy_key(self, objects):
        if not objects:
            return
        
        valid_objects = [obj for obj in objects if obj and cmds.objExists(obj)]
        if valid_objects:
            cmds.setKeyframe(valid_objects, time=(-50000, -50000), insert=False)
    
    def delete_dummy_key(self, objects):
        if not objects:
            return
        
        valid_objects = [obj for obj in objects if obj and cmds.objExists(obj)]
        if valid_objects:
            cmds.cutKey(valid_objects, time=(-50000, -50000), clear=True)
    
    def get_all_namespaces(self):
        remove_list = ["UI", "shared"]
        try:
            namespaces = list(set(cmds.namespaceInfo(listOnlyNamespaces=True)) - set(remove_list))
            namespaces.insert(0, "")
            if namespaces:
                namespaces.sort()
            return namespaces
        except Exception:
            return [""]
    
    def remap_namespace_in_data(self, anim_data, source_namespace, target_namespace):
        if not anim_data or "animData" not in anim_data:
            return anim_data
        
        remapped_data = copy.deepcopy(anim_data)
        
        if source_namespace is None:
            source_namespace = self.detect_source_namespace(anim_data)
        
        source_ns = source_namespace + ":" if source_namespace else ""
        target_ns = target_namespace + ":" if target_namespace else ""
        
        if source_ns == target_ns:
            return remapped_data
        
        for anim_item in remapped_data["animData"]:
            if "objAttr" in anim_item and anim_item["objAttr"]:
                obj_attr = anim_item["objAttr"]
                
                if obj_attr.startswith(source_ns):
                    new_obj_attr = obj_attr.replace(source_ns, target_ns, 1)
                    anim_item["objAttr"] = new_obj_attr
                elif not source_ns and target_ns:
                    anim_item["objAttr"] = target_ns + obj_attr
        
        return remapped_data
    
    def detect_multiple_namespaces_from_selection(self, selected_objects):
        if not selected_objects:
            return []
        
        namespaces = set()
        
        for obj in selected_objects:
            obj_short = obj.split("|")[-1]
            if ":" in obj_short:
                namespace = obj_short.split(":")[0]
                namespaces.add(namespace)
            else:
                namespaces.add("")
        
        return list(namespaces)
    
    def select_objects_from_json(self):
        latest_file = self.get_latest_json_file()
        if not latest_file:
            cmds.warning("No animation JSON files found.")
            return
        
        self.select_objects_from_json_file(latest_file)
    
    def select_objects_from_json_file(self, filepath):
        if not filepath:
            cmds.warning("No file specified.")
            return
        
        anim_data = self.load_animation_data(filepath)
        if not anim_data or "animData" not in anim_data:
            cmds.warning("Invalid animation data.")
            return
        
        json_objects = []
        for anim_item in anim_data["animData"]:
            if "objAttr" in anim_item and anim_item["objAttr"]:
                obj_name = anim_item["objAttr"].split(".")[0]
                if obj_name not in json_objects:
                    json_objects.append(obj_name)
        
        if not json_objects:
            cmds.warning("No objects found in JSON file.")
            return
        
        selected_objects = cmds.ls(selection=True)
        has_selection = bool(selected_objects)
        
        objects_to_select = []
        
        if not has_selection:
            objects_to_select = json_objects
        else:
            target_namespaces = self.detect_multiple_namespaces_from_selection(selected_objects)
            
            if target_namespaces:
                source_ns = self.detect_source_namespace(anim_data)
                
                for target_ns_item in target_namespaces:
                    if target_ns_item != source_ns:
                        remapped_data = self.remap_namespace_in_data(anim_data, source_ns, target_ns_item)
                        
                        for anim_item in remapped_data["animData"]:
                            if "objAttr" in anim_item and anim_item["objAttr"]:
                                obj_name = anim_item["objAttr"].split(".")[0]
                                if obj_name not in objects_to_select:
                                    objects_to_select.append(obj_name)
                    else:
                        for obj_name in json_objects:
                            if obj_name not in objects_to_select:
                                objects_to_select.append(obj_name)
            else:
                objects_to_select = json_objects
        
        existing_objects = []
        for obj in objects_to_select:
            if cmds.objExists(obj):
                existing_objects.append(obj)
            else:
                obj_short = obj.split("|")[-1]
                matching = cmds.ls(obj_short, long=True)
                if matching:
                    existing_objects.extend(matching)
        
        if existing_objects:
            cmds.select(existing_objects, replace=True)
        else:
            cmds.warning("No matching objects found in scene.")
    
    def apply_animation_to_multiple_namespaces(self, paste_in_place, only_selected, source_namespaces, target_namespaces, filepath=None):
        try:
            success_count = 0
            
            if filepath:
                anim_data = self.load_animation_data(filepath)
            else:
                latest_file = self.get_latest_json_file()
                if latest_file:
                    anim_data = self.load_animation_data(latest_file)
                else:
                    anim_data = None
            
            if not anim_data:
                return False
            
            for target_ns in target_namespaces:
                result = self.apply_animation_data(
                    anim_data,
                    paste_in_place=paste_in_place,
                    only_selected_nodes=only_selected,
                    target_namespace=target_ns,
                    skip_undo_chunk=True
                )
                
                if result:
                    success_count += 1
            
            return success_count > 0
        
        except Exception:
            return False
    
    def detect_most_common_namespace_from_selection(self, selected_objects):
        if not selected_objects:
            return ""
        
        namespace_counts = {}
        
        for obj in selected_objects:
            if ":" in obj:
                namespace = obj.split(":")[0]
                namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
            else:
                namespace_counts[""] = namespace_counts.get("", 0) + 1
        
        if namespace_counts:
            most_common = _max(namespace_counts, key=namespace_counts.get)
            return most_common
        
        return ""
    
    def detect_source_namespace(self, anim_data):
        if not anim_data or "animData" not in anim_data:
            return ""
        
        namespace_counts = {}
        
        for anim_item in anim_data["animData"]:
            if "objAttr" in anim_item and anim_item["objAttr"]:
                obj_attr = anim_item["objAttr"]
                if ":" in obj_attr:
                    namespace = obj_attr.split(":")[0]
                    namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
                else:
                    namespace_counts[""] = namespace_counts.get("", 0) + 1
        
        if namespace_counts:
            most_common = _max(namespace_counts, key=namespace_counts.get)
            return most_common
        
        return ""
    
    def apply_animation_data(self, anim_data, paste_in_place=True, only_selected_nodes=False, target_namespace=None, skip_undo_chunk=False):
        if not anim_data or "animData" not in anim_data:
            cmds.warning("Invalid animation data.")
            return False
        
        try:
            if target_namespace is not None:
                source_namespace = self.detect_source_namespace(anim_data)
                anim_data = self.remap_namespace_in_data(anim_data, source_namespace, target_namespace)
            
            if only_selected_nodes:
                selected_objects = cmds.ls(selection=True)
                if not selected_objects:
                    cmds.warning("No objects selected for paste operation.")
                    return False
                
                # PRE-COMPUTE: Build set of all valid object names (fast lookup)
                valid_objects = set()
                for sel_obj in selected_objects:
                    valid_objects.add(sel_obj)
                    short_name = sel_obj.split("|")[-1]
                    valid_objects.add(short_name)
                    # Add all descendants
                    try:
                        descendants = cmds.listRelatives(sel_obj, allDescendents=True) or []
                        valid_objects.update(descendants)
                    except:
                        pass
                
                # PRE-COMPUTE: Build set of existing attributes (fast lookup)
                existing_attrs = set()
                for sel_obj in selected_objects:
                    try:
                        attrs = cmds.listAttr(sel_obj, keyable=True) or []
                        for attr in attrs:
                            existing_attrs.add("{}.{}".format(sel_obj, attr))
                            short_name = sel_obj.split("|")[-1]
                            existing_attrs.add("{}.{}".format(short_name, attr))
                    except:
                        pass
                
                # Fast filter using sets
                filtered_anim_data = []
                for anim_item in anim_data["animData"]:
                    obj_attr = anim_item["objAttr"]
                    if obj_attr:
                        obj_name = obj_attr.split(".")[0]
                        # Fast set lookup instead of slow function calls
                        if obj_name in valid_objects or obj_attr in existing_attrs:
                            # Quick existence check
                            if cmds.objExists(obj_attr) or cmds.objExists(obj_name):
                                filtered_anim_data.append(anim_item)
                
                if not filtered_anim_data:
                    cmds.warning("None of the selected objects have matching animation data in the JSON file.")
                    return False
                
                anim_data["animData"] = filtered_anim_data
                objects = selected_objects
            
            else:
                objects = []
                for item in anim_data["animData"]:
                    if item["objAttr"]:
                        obj_name = item["objAttr"].split(".")[0]
                        if cmds.objExists(obj_name) and obj_name not in objects:
                            objects.append(obj_name)
            
            if not objects:
                cmds.warning("No valid objects to apply animation to.")
                return False
            
            if "rotationOrders" in anim_data and anim_data["rotationOrders"]:
                rot_differences = self.check_rotation_order_differences(anim_data["rotationOrders"], objects)
                if rot_differences:
                    cmds.waitCursor(state=False)
                    rot_choice = self.show_rotation_order_warning(rot_differences)
                    if rot_choice == "cancel":
                        cmds.waitCursor(state=True)  # Restore so finally block can turn it off
                        return False
                    if rot_choice == "change":
                        self.apply_rotation_order_changes(rot_differences)
                    cmds.waitCursor(state=True)
            
            # Select objects AFTER user confirms (not on cancel)
            if objects:
                cmds.select(objects)
            
            # Wrap all modifications in a single undo chunk BEFORE refresh suspend
            if not skip_undo_chunk:
                cmds.undoInfo(openChunk=True, chunkName="Paste Animation")
            
            try:
                cmds.refresh(suspend=True)
                cmds.evaluationManager(mode="off")
                
                first_key = None
                all_keys = []
                if paste_in_place:
                    curr_key = cmds.currentTime(query=True)
                    
                    for anim_item in anim_data["animData"]:
                        for keyframe in anim_item["keyframeData"]:
                            all_keys.append(keyframe[0])
                    
                    if all_keys:
                        first_key = _min(all_keys)
                        time_offset = curr_key - first_key
                    else:
                        time_offset = 0
                else:
                    for anim_item in anim_data["animData"]:
                        for keyframe in anim_item["keyframeData"]:
                            all_keys.append(keyframe[0])
                    time_offset = 0
                
                existing_obj_attrs = []
                for anim_item in anim_data["animData"]:
                    obj_attr = anim_item["objAttr"]
                    # Simple existence check - we already filtered in setup
                    if obj_attr and cmds.objExists(obj_attr.split(".")[0]):
                        existing_obj_attrs.append(obj_attr)
                
                if not existing_obj_attrs:
                    cmds.warning("No matching object attributes found in scene.")
                    return False
                
                self.create_dummy_key(existing_obj_attrs)
                
                if paste_in_place and first_key is not None:
                    cut_in = curr_key
                    cut_out = curr_key + (_max(all_keys) - first_key)
                    cmds.cutKey(existing_obj_attrs, time=(cut_in, cut_out), clear=True)
                else:
                    cmds.cutKey(existing_obj_attrs, time=(-49999, 50000), clear=True)
                
                for anim_item in anim_data["animData"]:
                    obj_attr = anim_item["objAttr"]
                    
                    # Skip empty attrs (already filtered, just quick null check)
                    if not obj_attr:
                        continue
                    
                    curve_data = anim_item["curveData"]
                    weighted = curve_data[0] if len(curve_data) > 0 else False
                    infinity = curve_data[1] if len(curve_data) > 1 else ["constant", "constant"]
                    
                    keyframe_data = anim_item["keyframeData"]
                    tangent_data = anim_item["tangentData"]
                    
                    self.om_helper.apply_curve_batch_api2(obj_attr, keyframe_data, tangent_data, weighted, infinity, time_offset)
                
                self.delete_dummy_key(existing_obj_attrs)
            
            finally:
                # ALWAYS restore refresh and evaluation manager - viewport should never stay frozen
                try:
                    cmds.refresh(suspend=False)
                except:
                    pass
                try:
                    cmds.evaluationManager(mode="parallel")
                except:
                    pass
                if not skip_undo_chunk:
                    cmds.undoInfo(closeChunk=True)
            
            # Only show timeline range dialog for replace mode (not paste_in_place/insert)
            if not paste_in_place and "timelineRange" in anim_data and anim_data["timelineRange"]:
                saved_range = anim_data["timelineRange"]
                pasted_min = saved_range[0] + time_offset
                pasted_max = saved_range[1] + time_offset
                current_min = cmds.playbackOptions(query=True, minTime=True)
                current_max = cmds.playbackOptions(query=True, maxTime=True)
                if int(pasted_min) != int(current_min) or int(pasted_max) != int(current_max):
                    # Turn off wait cursor before showing dialog
                    cmds.waitCursor(state=False)
                    
                    # Custom styled dialog
                    parent = get_maya_main_window()
                    dialog = QtWidgets.QDialog(parent)
                    dialog.setWindowTitle("Adjust timeline range?")
                    dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                    dialog.setModal(True)
                    dialog.setMinimumWidth(dpi(280))
                    
                    dialog.setStyleSheet("""
                        QDialog {{
                            background-color: rgb(38, 38, 38);
                            color: #E0E0E0;
                        }}
                        QLabel {{
                            color: #E0E0E0;
                            background: transparent;
                        }}
                        QPushButton {{
                            background-color: #3A3A3A;
                            border: 1px solid #555555;
                            border-radius: 4px;
                            color: #E0E0E0;
                            padding: {0}px {1}px;
                            font-size: 8pt;
                        }}
                        QPushButton:hover {{
                            background-color: #4A4A4A;
                        }}
                        QPushButton:pressed {{
                            background-color: #2A2A2A;
                        }}
                        QPushButton#yesBtn {{
                            background-color: #3A7BC8;
                            border: none;
                        }}
                        QPushButton#yesBtn:hover {{
                            background-color: #4A8BD8;
                        }}
                    """.format(dpi(8), dpi(16)))
                    
                    layout = QtWidgets.QVBoxLayout(dialog)
                    layout.setContentsMargins(dpi(20), dpi(20), dpi(20), dpi(20))
                    layout.setSpacing(dpi(12))
                    
                    msg_label = QtWidgets.QLabel("Animation range pasted: {} - {}?".format(int(pasted_min), int(pasted_max)))
                    msg_label.setWordWrap(True)
                    layout.addWidget(msg_label)
                    
                    layout.addSpacing(dpi(8))
                    
                    btn_layout = QtWidgets.QHBoxLayout()
                    btn_layout.setSpacing(dpi(12))
                    btn_layout.addStretch()
                    
                    yes_btn = QtWidgets.QPushButton("Yes")
                    yes_btn.setObjectName("yesBtn")
                    yes_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    yes_btn.setMinimumWidth(dpi(60))
                    
                    no_btn = QtWidgets.QPushButton("No")
                    no_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    no_btn.setMinimumWidth(dpi(60))
                    
                    btn_layout.addWidget(yes_btn)
                    btn_layout.addWidget(no_btn)
                    
                    layout.addLayout(btn_layout)
                    
                    yes_btn.clicked.connect(dialog.accept)
                    no_btn.clicked.connect(dialog.reject)
                    
                    if dialog.exec_() if PYSIDE_VERSION == 2 else dialog.exec():
                        cmds.playbackOptions(minTime=pasted_min, maxTime=pasted_max)
            
            return True
        
        except Exception:
            # Safety fallback - ensure viewport is never left frozen
            try:
                cmds.refresh(suspend=False)
            except:
                pass
            try:
                cmds.evaluationManager(mode="parallel")
            except:
                pass
            return False
    
    def attribute_exists_and_keyable(self, obj_attr):
        if not obj_attr or "." not in obj_attr:
            return False
        
        if cmds.objExists(obj_attr):
            try:
                return cmds.getAttr(obj_attr, keyable=True) is not False
            except Exception:
                try:
                    cmds.getAttr(obj_attr)
                    return True
                except Exception:
                    return False
        
        obj_name = obj_attr.split(".")[0]
        attr_name = obj_attr.split(".")[-1]
        
        if not cmds.objExists(obj_name):
            return False
        
        try:
            cmds.getAttr(obj_attr)
            return True
        except Exception:
            pass
        
        try:
            all_attrs = cmds.listAttr(obj_name) or []
            if attr_name in all_attrs:
                return True
        except Exception:
            pass
        
        return False
    
    def is_object_or_transform_selected(self, obj_name, selected_objects):
        if obj_name in selected_objects:
            return True
        
        try:
            if cmds.objectType(obj_name) != "transform":
                parents = cmds.listRelatives(obj_name, parent=True, type="transform")
                if parents and parents[0] in selected_objects:
                    return True
        except Exception:
            pass
        
        for sel_obj in selected_objects:
            try:
                if cmds.objExists(sel_obj):
                    relatives = cmds.listRelatives(sel_obj, allDescendents=True) or []
                    if obj_name in relatives:
                        return True
                    relatives = cmds.listRelatives(obj_name, allDescendents=True) or []
                    if sel_obj in relatives:
                        return True
            except Exception:
                continue
        
        return False
    
    def paste_latest_animation(self, paste_in_place=True, only_selected=False, target_namespace=None, skip_undo_chunk=False):
        latest_file = self.get_latest_json_file()
        
        if not latest_file:
            cmds.warning("No animation JSON files found in Documents folder.")
            return False
        
        anim_data = self.load_animation_data(latest_file)
        if anim_data:
            return self.apply_animation_data(anim_data, paste_in_place, only_selected, target_namespace, skip_undo_chunk)
        
        return False
    
    def paste_from_file(self, filepath, paste_in_place=True, only_selected=False, target_namespace=None, skip_undo_chunk=False):
        anim_data = self.load_animation_data(filepath)
        if anim_data:
            return self.apply_animation_data(anim_data, paste_in_place, only_selected, target_namespace, skip_undo_chunk)
        
        return False
    
    def copy_pose_to_json(self):
        cmds.waitCursor(state=True)
        
        try:
            selected_objects = self.om_helper.get_selected_objects()
            if not selected_objects:
                selected_objects = cmds.ls(selection=True, long=True)
            
            if not selected_objects:
                cmds.warning("No objects selected. Please select controls to copy their pose.")
                return None
            
            current_time = cmds.currentTime(query=True)
            pose_data = {}
            anim_data_list = []
            
            for obj in selected_objects:
                short_name = obj.split("|")[-1]
                pose_data[short_name] = {}
                
                attrs = cmds.listAttr(obj, keyable=True, unlocked=True)
                if not attrs:
                    continue
                
                for attr in attrs:
                    full_attr = obj + "." + attr
                    try:
                        value = self.om_helper.get_attribute_value_fast(full_attr)
                        if value is None:
                            value = cmds.getAttr(full_attr)
                        
                        pose_data[short_name][attr] = value
                        
                        anim_data_list.append({
                            "objAttr": short_name + "." + attr,
                            "curveData": [False, ["constant", "constant"]],
                            "keyframeData": [[current_time, value, False]],
                            "tangentData": [["auto", "auto", 0, 0, 0, 0, False, False]]
                        })
                    except Exception:
                        continue
            
            if not pose_data or all(not attrs for attrs in pose_data.values()):
                cmds.warning("No keyable attributes found on selected objects.")
                return None
            
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                base_name = ".".join(scene_name.split(".")[:-1])
            else:
                base_name = "untitled_scene"
            
            timestamp = time_module.strftime("%Y%m%d_%H%M%S")
            filename = "{}_animation_{}.json".format(base_name, timestamp)
            filepath = os.path.join(self.documents_path, filename)
            
            save_data = {
                "pose": pose_data,
                "animData": anim_data_list,
                "rotationOrders": self.get_rotation_orders_from_objects(selected_objects)
            }
            
            with open(filepath, "w") as f:
                json.dump(save_data, f, indent=4)
            
            return filepath
        
        finally:
            cmds.waitCursor(state=False)
    
    def paste_pose_from_json(self, filepath=None, target_namespace=None, selected_objects=None, skip_undo_chunk=False):
        cmds.waitCursor(state=True)
        
        try:
            if not filepath:
                json_files = glob.glob(os.path.join(self.documents_path, "*_animation_*.json"))
                pose_files = glob.glob(os.path.join(self.documents_path, "pose_*.json"))
                all_files = json_files + pose_files
                
                if not all_files:
                    cmds.warning("No pose or animation files found.")
                    return
                
                all_files.sort(key=os.path.getmtime, reverse=True)
                filepath = all_files[0]
            
            if not os.path.exists(filepath):
                cmds.warning("File not found: {}".format(filepath))
                return
            
            with open(filepath, "r") as f:
                data = json.load(f)
            
            if not data:
                cmds.warning("No pose data found in file.")
                return
            
            if "pose" in data:
                pose_data = data["pose"]
            else:
                pose_data = data
            
            if "rotationOrders" in data and data["rotationOrders"]:
                target_objs = []
                if selected_objects:
                    target_objs = selected_objects
                else:
                    for obj_name in pose_data.keys():
                        if cmds.objExists(obj_name):
                            target_objs.append(obj_name)
                        else:
                            matching = cmds.ls("*:" + obj_name.split(":")[-1], long=True) or cmds.ls(obj_name.split(":")[-1], long=True)
                            if matching:
                                target_objs.append(matching[0])
                if target_objs:
                    rot_differences = self.check_rotation_order_differences(data["rotationOrders"], target_objs)
                    if rot_differences:
                        cmds.waitCursor(state=False)
                        rot_choice = self.show_rotation_order_warning(rot_differences)
                        if rot_choice == "cancel":
                            cmds.waitCursor(state=True)  # Restore so finally block can turn it off
                            return
                        if rot_choice == "change":
                            self.apply_rotation_order_changes(rot_differences)
                        cmds.waitCursor(state=True)
            
            try:
                # PRE-COMPUTE: Build object name mapping for fast lookup
                obj_name_map = {}  # short_name -> full_path
                
                if selected_objects:
                    # Map selected objects by short name
                    for sel_obj in selected_objects:
                        short = sel_obj.split("|")[-1]
                        short_no_ns = short.split(":")[-1]
                        obj_name_map[short] = sel_obj
                        obj_name_map[short_no_ns] = sel_obj
                        if ":" in short:
                            obj_name_map[short.split(":")[-1]] = sel_obj
                else:
                    # Build map from pose data objects that exist in scene
                    for obj_name in pose_data.keys():
                        if cmds.objExists(obj_name):
                            obj_name_map[obj_name] = obj_name
                            obj_name_map[obj_name.split(":")[-1]] = obj_name
                        else:
                            # Try to find matching object
                            short = obj_name.split(":")[-1]
                            matching = cmds.ls("*:" + short, long=True) or cmds.ls(short, long=True)
                            if matching:
                                obj_name_map[obj_name] = matching[0]
                                obj_name_map[short] = matching[0]
                
                # Apply namespace remapping if needed
                if target_namespace is not None:
                    remapped = {}
                    for obj_name in pose_data.keys():
                        if target_namespace:
                            target_obj = target_namespace + ":" + obj_name.split(":")[-1]
                        else:
                            target_obj = obj_name.split(":")[-1]
                        
                        if cmds.objExists(target_obj):
                            remapped[obj_name] = target_obj
                        elif target_obj in obj_name_map:
                            remapped[obj_name] = obj_name_map[target_obj]
                    
                    # Update map with remapped names
                    for src, dst in remapped.items():
                        obj_name_map[src] = dst
                
                # FAST APPLY: Set all values using API 2.0
                # Wrap in single undo chunk
                if not skip_undo_chunk:
                    cmds.undoInfo(openChunk=True, chunkName="Paste Pose")
                
                try:
                    for obj_name, attrs in pose_data.items():
                        # Find target object from pre-computed map
                        target_obj_full = None
                        
                        if obj_name in obj_name_map:
                            target_obj_full = obj_name_map[obj_name]
                        else:
                            short = obj_name.split(":")[-1]
                            if short in obj_name_map:
                                target_obj_full = obj_name_map[short]
                        
                        if not target_obj_full:
                            continue
                        
                        # Set all attributes for this object
                        for attr_name, value in attrs.items():
                            full_attr = target_obj_full + "." + attr_name
                            
                            try:
                                # Try API 2.0 first (fastest)
                                if not self.om_helper.set_attribute_value_api2(full_attr, value):
                                    # Try API 1.0
                                    if not self.om_helper.set_attribute_value_fast(full_attr, value):
                                        # Fallback to cmds
                                        if cmds.objExists(full_attr) and not cmds.getAttr(full_attr, lock=True):
                                            cmds.setAttr(full_attr, value)
                            except:
                                pass
                finally:
                    if not skip_undo_chunk:
                        cmds.undoInfo(closeChunk=True)
            
            except Exception:
                pass
        
        finally:
            cmds.waitCursor(state=False)
    
    def get_latest_pose_file(self):
        json_files = glob.glob(os.path.join(self.documents_path, "*_animation_*.json"))
        pose_files = glob.glob(os.path.join(self.documents_path, "pose_*.json"))
        all_files = json_files + pose_files
        
        if not all_files:
            return None
        
        latest_file = _max(all_files, key=os.path.getmtime)
        return latest_file


class TransifyUI(QtWidgets.QDialog):
    option_var_name = "TransifyUI_lastPos"
    
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(TransifyUI, self).__init__(parent)
        self.setObjectName("TransifyUIWindow")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        self.current_mode = "Insert"
        self.selected_file = None
        
        # Track current screen for DPI changes
        self._current_screen = None
        self._current_scale_factor = get_scale_factor()
        
        self.tool = AnimationCopyPasteJson()
        
        self.setup_ui()
        self.apply_theme()
        self.restore_position()
        self.apply_rounded_corners()
        self.update_file_info()
        
        self.fade_to(0.87)
    
    def setup_ui(self):
        window_width = dpi(280)
        window_height = dpi(560)
        self.setFixedSize(window_width, window_height)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(16), dpi(16), dpi(16), dpi(16))
        main_layout.setSpacing(dpi(8))
        
        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(0)
        
        spacer_left = QtWidgets.QWidget()
        spacer_left.setFixedSize(dpi(26), dpi(26))
        title_bar.addWidget(spacer_left)
        
        title_bar.addStretch()
        
        self.title_label = QtWidgets.QLabel("Transify")
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #4A90E2; background: transparent;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_bar.addWidget(self.title_label)
        
        title_bar.addStretch()
        
        close_button = QtWidgets.QPushButton()
        close_button.setFixedSize(dpi(26), dpi(26))
        close_button.setText(u"\u00D7")
        close_button.setCursor(QtCore.Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
                color: #666666;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        main_layout.addLayout(title_bar)
        main_layout.addSpacing(dpi(14))
        
        copy_label = QtWidgets.QLabel("COPY ANIMATION")
        copy_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(copy_label)
        main_layout.addSpacing(dpi(8))
        
        self.copy_all_button = QtWidgets.QPushButton("C O P Y   A L L   A N I M A T I O N")
        self.copy_all_button.setFixedHeight(dpi(35))
        self.copy_all_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_all_button.setStyleSheet("""
            QPushButton {
                background-color: #3A7BC8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4A8BD8;
            }
            QPushButton:pressed {
                background-color: #2A6BB8;
            }
        """)
        self.copy_all_button.clicked.connect(self.copy_all_action)
        main_layout.addWidget(self.copy_all_button)
        main_layout.addSpacing(dpi(6))
        
        self.copy_selected_button = QtWidgets.QPushButton("C O P Y   S E L E C T E D   C U R V E S")
        self.copy_selected_button.setFixedHeight(dpi(35))
        self.copy_selected_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_selected_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.copy_selected_button.clicked.connect(self.copy_action)
        main_layout.addWidget(self.copy_selected_button)
        main_layout.addSpacing(dpi(14))
        
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("background-color: #3A3A3A; border: none;")
        main_layout.addWidget(separator1)
        main_layout.addSpacing(dpi(10))
        
        self.file_info_label = QtWidgets.QLabel("No files found")
        self.file_info_label.setStyleSheet("""
            QLabel {
                font-size: 7pt;
                color: #888888;
                font-style: italic;
                background: transparent;
            }
        """)
        self.file_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.file_info_label.setWordWrap(True)
        main_layout.addWidget(self.file_info_label)
        main_layout.addSpacing(dpi(10))
        
        paste_label = QtWidgets.QLabel("PASTE ANIMATION")
        paste_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(paste_label)
        main_layout.addSpacing(dpi(8))
        
        self.select_button = QtWidgets.QPushButton("S E L E C T   O B J E C T S")
        self.select_button.setFixedHeight(dpi(33))
        self.select_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9BD5;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #6BABE5;
            }
            QPushButton:pressed {
                background-color: #4B8BC5;
            }
        """)
        self.select_button.clicked.connect(self.select_objects_action)
        main_layout.addWidget(self.select_button)
        main_layout.addSpacing(dpi(8))
        
        paste_container = QtWidgets.QWidget()
        paste_layout = QtWidgets.QHBoxLayout(paste_container)
        paste_layout.setContentsMargins(0, 0, 0, 0)
        paste_layout.setSpacing(dpi(8))
        
        self.replace_button = QtWidgets.QPushButton("R E P L A C E")
        self.replace_button.setFixedHeight(dpi(38))
        self.replace_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.replace_button.setStyleSheet("""
            QPushButton {
                background-color: #2E6BA8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #3E7BB8;
            }
            QPushButton:pressed {
                background-color: #1E5B98;
            }
        """)
        self.replace_button.clicked.connect(self.replace_action)
        paste_layout.addWidget(self.replace_button)
        
        self.insert_button = QtWidgets.QPushButton("I N S E R T")
        self.insert_button.setFixedHeight(dpi(38))
        self.insert_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.insert_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.insert_button.clicked.connect(self.insert_action)
        paste_layout.addWidget(self.insert_button)
        
        main_layout.addWidget(paste_container)
        main_layout.addSpacing(dpi(8))
        
        self.browse_button = QtWidgets.QPushButton("B R O W S E   F I L E S")
        self.browse_button.setFixedHeight(dpi(30))
        self.browse_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3D4045;
                border: 1px solid #505560;
                color: #CCCCCC;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4A4E55;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2D3035;
            }
        """)
        self.browse_button.clicked.connect(self.browse_action)
        main_layout.addWidget(self.browse_button)
        main_layout.addSpacing(dpi(14))
        
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: #3A3A3A; border: none;")
        main_layout.addWidget(separator2)
        main_layout.addSpacing(dpi(10))
        
        pose_label = QtWidgets.QLabel("POSE")
        pose_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        main_layout.addWidget(pose_label)
        main_layout.addSpacing(dpi(8))
        
        pose_container = QtWidgets.QWidget()
        pose_layout = QtWidgets.QHBoxLayout(pose_container)
        pose_layout.setContentsMargins(0, 0, 0, 0)
        pose_layout.setSpacing(dpi(8))
        
        self.copy_pose_button = QtWidgets.QPushButton("C O P Y")
        self.copy_pose_button.setFixedHeight(dpi(35))
        self.copy_pose_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.copy_pose_button.setStyleSheet("""
            QPushButton {
                background-color: #3A7BC8;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4A8BD8;
            }
            QPushButton:pressed {
                background-color: #2A6BB8;
            }
        """)
        self.copy_pose_button.clicked.connect(self.copy_pose_action)
        pose_layout.addWidget(self.copy_pose_button)
        
        self.paste_pose_button = QtWidgets.QPushButton("P A S T E")
        self.paste_pose_button.setFixedHeight(dpi(35))
        self.paste_pose_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.paste_pose_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: #FFFFFF;
                border-radius: 6px;
                font-size: 8pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
        """)
        self.paste_pose_button.clicked.connect(self.paste_pose_action)
        pose_layout.addWidget(self.paste_pose_button)
        
        main_layout.addWidget(pose_container)
        
        main_layout.addStretch()
    
    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                color: white;
                border-radius: 14px;
            }
        """)
    
    def apply_rounded_corners(self):
        try:
            radius = dpi(14)
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
            if PYSIDE_VERSION >= 2:
                polygon = path.toFillPolygon().toPolygon()
            else:
                polygon = path.toFillPolygon().toPolygon()
            region = QtGui.QRegion(polygon)
            self.setMask(region)
        except Exception:
            pass
    
    def resizeEvent(self, event):
        super(TransifyUI, self).resizeEvent(event)
        self.apply_rounded_corners()
    
    def fade_to(self, target_opacity, duration=300, easing=None):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        if easing is None:
            self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        else:
            self.anim.setEasingCurve(easing)
        self.anim.start()
    
    def update_file_info(self):
        if self.selected_file:
            filename = os.path.basename(self.selected_file)
            self.file_info_label.setText(filename)
        else:
            latest = self.tool.get_latest_json_file()
            if latest:
                filename = os.path.basename(latest)
                self.file_info_label.setText(filename)
            else:
                self.file_info_label.setText("No files found")
    
    def has_selection(self):
        return bool(cmds.ls(selection=True))
    
    def get_target_namespace(self):
        selected = cmds.ls(selection=True)
        if selected:
            return self.tool.detect_most_common_namespace_from_selection(selected)
        return ""
    
    def copy_all_action(self):
        cmds.undoInfo(openChunk=True, chunkName="Copy All Animation")
        try:
            self.tool.copy_all_animation_to_json()
            self.selected_file = None
            self.update_file_info()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def copy_action(self):
        cmds.undoInfo(openChunk=True, chunkName="Copy Animation")
        try:
            result = self.tool.copy_selected_animation_to_json()
            if result is None:
                show_styled_error("No Keys Selected", "You need to have keys selected in the Graph Editor.")
            else:
                self.selected_file = None
                self.update_file_info()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def insert_action(self):
        try:
            self.paste_animation(paste_in_place=True)
        except Exception:
            pass
        finally:
            self.clear_focus()
    
    def replace_action(self):
        try:
            self.paste_animation(paste_in_place=False)
        except Exception:
            pass
        finally:
            self.clear_focus()
    
    def paste_animation(self, paste_in_place=True):
        only_selected = self.has_selection()
        target_ns = self.get_target_namespace()
        
        cmds.waitCursor(state=True)
        cmds.undoInfo(openChunk=True, chunkName="Paste Animation")
        try:
            if only_selected:
                selected_objects = cmds.ls(selection=True)
                target_namespaces = self.tool.detect_multiple_namespaces_from_selection(selected_objects)
                
                if len(target_namespaces) > 1:
                    if self.selected_file:
                        anim_data = self.tool.load_animation_data(self.selected_file)
                        filepath = self.selected_file
                    else:
                        latest_file = self.tool.get_latest_json_file()
                        if latest_file:
                            anim_data = self.tool.load_animation_data(latest_file)
                            filepath = latest_file
                        else:
                            anim_data = None
                            filepath = None
                    
                    if anim_data:
                        source_ns = self.tool.detect_source_namespace(anim_data)
                        self.tool.apply_animation_to_multiple_namespaces(
                            paste_in_place, True, source_ns, target_namespaces, filepath
                        )
                    return
                else:
                    target_ns_from_selection = target_namespaces[0] if target_namespaces else ""
                    
                    if self.selected_file:
                        anim_data = self.tool.load_animation_data(self.selected_file)
                    else:
                        latest_file = self.tool.get_latest_json_file()
                        if latest_file:
                            anim_data = self.tool.load_animation_data(latest_file)
                        else:
                            anim_data = None
                    
                    if anim_data:
                        source_ns = self.tool.detect_source_namespace(anim_data)
                        if source_ns != target_ns_from_selection:
                            target_ns = target_ns_from_selection
                        else:
                            target_ns = None
            else:
                if target_ns == "":
                    target_ns = None
            
            if self.selected_file:
                self.tool.paste_from_file(
                    self.selected_file,
                    paste_in_place=paste_in_place,
                    only_selected=only_selected,
                    target_namespace=target_ns,
                    skip_undo_chunk=True
                )
            else:
                self.tool.paste_latest_animation(
                    paste_in_place=paste_in_place,
                    only_selected=only_selected,
                    target_namespace=target_ns,
                    skip_undo_chunk=True
                )
        finally:
            cmds.undoInfo(closeChunk=True)
            cmds.waitCursor(state=False)
    
    def copy_pose_action(self):
        cmds.undoInfo(openChunk=True, chunkName="Copy Pose")
        try:
            self.tool.copy_pose_to_json()
            self.selected_file = None
            self.update_file_info()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def paste_pose_action(self):
        cmds.undoInfo(openChunk=True, chunkName="Paste Pose")
        try:
            target_ns = self.get_target_namespace()
            selected = cmds.ls(selection=True)
            
            if self.selected_file:
                self.tool.paste_pose_from_json(
                    filepath=self.selected_file,
                    target_namespace=target_ns if target_ns else None,
                    selected_objects=selected if selected else None,
                    skip_undo_chunk=True
                )
            else:
                self.tool.paste_pose_from_json(
                    target_namespace=target_ns if target_ns else None,
                    selected_objects=selected if selected else None,
                    skip_undo_chunk=True
                )
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def select_objects_action(self):
        cmds.undoInfo(openChunk=True, chunkName="Select Objects")
        try:
            if self.selected_file:
                self.tool.select_objects_from_json_file(self.selected_file)
            else:
                self.tool.select_objects_from_json()
        except Exception:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
            self.clear_focus()
    
    def browse_action(self):
        json_files = self.tool.get_all_json_files()
        
        if not json_files:
            show_styled_error("No Files Found", "No animation JSON files found in Documents folder.")
            return
        
        result = cmds.fileDialog2(
            fileMode=1,
            caption="Select Animation File",
            fileFilter="JSON Files (*.json)",
            startingDirectory=self.tool.documents_path
        )
        
        if result:
            self.selected_file = result[0]
            self.update_file_info()
        
        self.clear_focus()
    
    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass
    
    def restore_position(self):
        """Restore window position, checking if it's visible on any screen."""
        saved_pos = load_window_position()
        window_width = self.width()
        window_height = self.height()
        
        if saved_pos and is_position_visible(saved_pos, window_width, window_height):
            # Position is valid and visible on some screen
            self.move(saved_pos)
        else:
            # Position invalid or off-screen - center on primary screen
            center = get_center_of_primary_screen()
            new_x = center.x() - window_width // 2
            new_y = center.y() - window_height // 2
            self.move(new_x, new_y)
        
        # Initialize screen tracking after positioning
        try:
            center = QtCore.QPoint(
                self.x() + window_width // 2,
                self.y() + window_height // 2
            )
            self._current_screen = get_screen_at_position(center)
            if self._current_screen:
                self._current_scale_factor = get_scale_factor_for_screen(self._current_screen)
        except:
            pass
    
    def closeEvent(self, event):
        save_window_position(self.pos())
        super(TransifyUI, self).closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if hasattr(event, "globalPosition"):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            if hasattr(event, "globalPosition"):
                self.show_context_menu(event.globalPosition().toPoint())
            else:
                self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #2E2E2E;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #E0E0E0;
                font-size: 8pt;
            }}
            QMenu::item {{
                padding: {0}px {1}px;
                border-radius: 2px;
                margin: 1px;
            }}
            QMenu::item:selected {{
                background-color: #4A90E2;
                color: white;
            }}
        """.format(dpi(6), dpi(12)))
        
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_ui)
        
        if self.selected_file:
            clear_action = menu.addAction("Use Latest File")
            clear_action.triggered.connect(self.clear_selected_file)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Close")
        if PYSIDE_VERSION == 6:
            action = menu.exec(pos)
        else:
            action = menu.exec_(pos)
        if action == exit_action:
            self.close()
    
    def clear_selected_file(self):
        self.selected_file = None
        self.update_file_info()
    
    def refresh_ui(self):
        self.update_file_info()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            if hasattr(event, "globalPosition"):
                delta = event.globalPosition().toPoint() - self.old_pos
                self.old_pos = event.globalPosition().toPoint()
            else:
                delta = event.globalPos() - self.old_pos
                self.old_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
        # Check for screen change when drag ends
        self.check_screen_change()
    
    def moveEvent(self, event):
        """Called when window position changes."""
        super(TransifyUI, self).moveEvent(event)
        # Only check on significant moves to avoid constant checks
        # The main check happens on mouse release
    
    def check_screen_change(self):
        """Check if window moved to a different screen and rebuild UI if DPI changed."""
        try:
            # Get the screen at the window's center
            center = QtCore.QPoint(
                self.x() + self.width() // 2,
                self.y() + self.height() // 2
            )
            
            new_screen = get_screen_at_position(center)
            if new_screen is None:
                return
            
            # Get scale factor for the new screen
            new_scale = get_scale_factor_for_screen(new_screen)
            
            # Check if scale factor changed significantly (more than 1%)
            if abs(new_scale - self._current_scale_factor) > 0.01:
                self._current_screen = new_screen
                self._current_scale_factor = new_scale
                
                # Reset and rebuild UI with new scale
                self.rebuild_for_new_screen(new_scale)
        except Exception:
            pass
    
    def rebuild_for_new_screen(self, new_scale):
        """Rebuild the UI for a new screen with different DPI."""
        # Save current position
        current_pos = self.pos()
        
        # Update the global scale factor
        set_scale_factor(new_scale)
        
        # Delete all child widgets
        for child in self.findChildren(QtWidgets.QWidget):
            child.deleteLater()
        
        # Remove the existing layout
        old_layout = self.layout()
        if old_layout:
            # Delete all items from the layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())
            
            # Delete the layout itself
            QtWidgets.QWidget().setLayout(old_layout)
        
        # Process events to ensure widgets are deleted
        QtWidgets.QApplication.processEvents()
        
        # Rebuild UI
        self.setup_ui()
        self.apply_theme()
        self.apply_rounded_corners()
        self.update_file_info()
        
        # Restore position
        self.move(current_pos)
    
    def _clear_layout(self, layout):
        """Recursively clear a layout."""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def enterEvent(self, event):
        self.fade_to(0.95, 50, QtCore.QEasingCurve.OutQuad)
        super(TransifyUI, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.fade_to(0.75, 300)
        super(TransifyUI, self).leaveEvent(event)


transify_ui_instance = None


def create_transify_ui():
    global transify_ui_instance
    
    if transify_ui_instance is not None:
        try:
            transify_ui_instance.close()
            transify_ui_instance.deleteLater()
        except Exception:
            pass
        transify_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        if child.objectName() == "TransifyUIWindow":
            try:
                child.close()
                child.deleteLater()
            except Exception:
                pass
    
    transify_ui_instance = TransifyUI()
    transify_ui_instance.show()
    return transify_ui_instance


def ui():
    return create_transify_ui()


def show_modern_animation_copy_paste_ui():
    return create_transify_ui()


def create_complete_animation_ui():
    return create_transify_ui()


def create_animation_paste_ui():
    return create_transify_ui()


def create_animation_copy_ui():
    return create_transify_ui()


def copy_selected_animation_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_selected_animation_to_json()


def copy_all_animation_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_all_animation_to_json()


def paste_latest_animation_in_place():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=False)


def paste_latest_animation_original():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=False, only_selected=False)


def paste_to_selected_only():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=True)


create_transify_ui()