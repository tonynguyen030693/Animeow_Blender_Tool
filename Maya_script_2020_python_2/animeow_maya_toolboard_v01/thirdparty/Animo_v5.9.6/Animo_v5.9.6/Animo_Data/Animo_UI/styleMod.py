'''
    Animo UI Style Module
'''

import maya.cmds as cmds
import os
import json

try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets


def _get_prefs_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data", "Animo_Prefs")


def get_user_scale():
    """Get user's preferred UI scale (1.0 = default, 1.3 = 30% bigger, etc.)"""
    try:
        prefs_path = _get_prefs_path()
        pref_file = os.path.join(prefs_path, "size_prefs.json")
        if os.path.exists(pref_file):
            with open(pref_file, 'r') as f:
                data = json.load(f)
                return data.get("scale", 1.0)
    except:
        pass
    return 1.0


def set_user_scale(scale):
    """Set user's preferred UI scale"""
    try:
        prefs_path = _get_prefs_path()
        if not os.path.exists(prefs_path):
            os.makedirs(prefs_path)
        pref_file = os.path.join(prefs_path, "size_prefs.json")
        with open(pref_file, 'w') as f:
            json.dump({"scale": scale}, f)
        return True
    except:
        return False


def get_dpi_scale():
    try:
        app = QtWidgets.QApplication.instance()
        if app:
            screen = app.primaryScreen()
            dpi = screen.logicalDotsPerInch()
            base_scale = dpi / 96.0
            
            # Check for HiDPI displays (Retina, high-density laptops, etc.)
            device_pixel_ratio = screen.devicePixelRatio()
            
            # Calculate physical PPI estimate
            # On HiDPI screens, logical DPI is often "normalized" but devicePixelRatio > 1
            geometry = screen.geometry()
            physical_size = screen.physicalSize()  # in mm
            
            if physical_size.width() > 0 and physical_size.height() > 0:
                # Calculate actual PPI
                width_inches = physical_size.width() / 25.4
                height_inches = physical_size.height() / 25.4
                diagonal_pixels = (geometry.width()**2 + geometry.height()**2) ** 0.5
                diagonal_inches = (width_inches**2 + height_inches**2) ** 0.5
                actual_ppi = diagonal_pixels / diagonal_inches if diagonal_inches > 0 else 96
                
                # High PPI screens (>180 PPI) need extra scaling
                # 13.3" 2560x1600 = ~227 PPI -> 227/190 = 1.19x (~20% bigger)
                # Normal screens are ~96-120 PPI
                if actual_ppi > 180:
                    # Scale up proportionally for high density screens
                    hidpi_factor = actual_ppi / 190.0  # 190 PPI as reference for ~20% scaling
                    hidpi_factor = min(hidpi_factor, 2.0)  # Cap at 2.0x
                    return hidpi_factor
            
            # Fallback: Use devicePixelRatio for HiDPI detection
            if device_pixel_ratio > 1.0:
                # HiDPI display - scale based on device pixel ratio
                hidpi_scale = base_scale * device_pixel_ratio * 0.6  # Adjusted for ~20% target
                return max(1.0, min(hidpi_scale, 2.0))
            
            # Standard display adjustment
            adjustment = 1.0 - max(0, (120 - dpi) / 100) * 0.3
            return base_scale * adjustment
    except:
        pass
    return 1.0


USER_SCALE = get_user_scale()
DPI_SCALE = get_dpi_scale() * USER_SCALE


def scaled(value):
    return int(value * DPI_SCALE)


ICON_SIZE_BASE = 24  # 7% smaller
ICON_WIDTH = scaled(ICON_SIZE_BASE)
ICON_HEIGHT = scaled(ICON_SIZE_BASE)
ICON_SPACING = scaled(8)  # Horizontal mode spacing
ICON_SPACING_VERTICAL = scaled(12)  # More space for vertical mode
TOOLBAR_WIDTH = scaled(34)  # For vertical mode
TOOLBAR_HEIGHT = scaled(38)  # For horizontal mode - taller to center icons better

TOOLBAR_BG_COLOR = [0.22, 0.22, 0.22]
TOOLBAR_BG_COLOR_LIGHT = [0.25, 0.25, 0.25]  # For timeline modes
TOOLBAR_BG_COLOR_LIGHTER = [0.27, 0.27, 0.27]  # For shelf/statusline modes