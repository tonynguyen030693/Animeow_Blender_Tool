'''
    Animo Bar Module
'''

import maya.cmds as cmds
import os
import sys
import importlib
import importlib.abc
import importlib.machinery
import importlib.util


class VersionedModuleFinder(importlib.abc.MetaPathFinder):
    """Finder for versioned .pyc files (e.g., module_py2024.pyc)"""
    
    def __init__(self, search_paths, maya_version):
        self.search_paths = search_paths
        self.maya_version = maya_version
    
    def find_spec(self, fullname, path, target=None):
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            # Skip if .py exists
            py_path = os.path.join(search_path, fullname + ".py")
            if os.path.exists(py_path):
                return None
            
            # Look for versioned .pyc
            versioned_name = "{}_py{}".format(fullname, self.maya_version)
            pyc_path = os.path.join(search_path, versioned_name + ".pyc")
            
            if os.path.exists(pyc_path):
                loader = importlib.machinery.SourcelessFileLoader(fullname, pyc_path)
                return importlib.util.spec_from_loader(fullname, loader, origin=pyc_path)
        
        return None


_versioned_finder = None

def install_versioned_finder(search_paths, maya_version):
    """Install the versioned module finder"""
    global _versioned_finder
    
    if _versioned_finder is not None:
        try:
            sys.meta_path.remove(_versioned_finder)
        except ValueError:
            pass
    
    _versioned_finder = VersionedModuleFinder(search_paths, maya_version)
    sys.meta_path.insert(0, _versioned_finder)


ICON_DATA = [
    ("transify_icon.png", "Anim Transfer", "transify_launcher", None, None, (26, 26), (0, 0), None),
    ("keys_time_icon.png", "Keys Time", "keys_time_launcher", None, None, (23, 23), (0, 0), None),
    ("fast_anim_layers_icon.png", "Fast Merge animLayers", "fast_anim_layer_launcher", None, None, (23, 23), (0, 0), [("All Layers - Merge", "merge_all_anim_layers", "Animo_Animation_Layers"), ("All Layers - Smart", "smart_merge_all_anim_layers", "Animo_Animation_Layers"), ("---", None, None), ("Selected Layers - Merge", "merge_selected_anim_layers", "Animo_Animation_Layers"), ("Selected Layers - Smart", "smart_merge_selected_anim_layers", "Animo_Animation_Layers"), ("---", None, None), ("animLayer UI", "fast_anim_layer_launcher", None)]),
    ("tweenify_icon.png", "Anim Sliders", "tweenify_launcher", None, None, (24, 24), (0, 0), None),
    ("tracify_icon.png", "Arc Tracker", "tracify_launcher", None, "ui", (24, 24), (0, 0), None),
    ("pickify_icon.png", "Selection Sets", "pickify_launcher", None, None, (26, 26), (0, 0), None),
    ("spacify_icon.png", "Temp Controls", "spacify_launcher", "Animo_Space_Switcher", None, (23, 23), (0, 0), None),
    ("xform_align_icon.png", "Xform - Align", "xform_align_launcher", None, None, (23, 23), (0, 0), None),
    ("attributes_space_switcher_icon.png", "Attributes Space Switcher", "attributes_space_switcher_launcher", None, None, (23, 23), (0, 0), None),
    ("temp_pivot_icon.png", "Temp Pivot", "temp_pivot_launcher", None, None, (23, 23), (0, 0), None),
    ("global_offset_icon.png", "Global Offset", "global_offset_launcher", None, None, (28, 28), (0, 0), None),
    ("twosify_icon.png", "Twosify", "twosify_launcher", None, None, (30, 30), (0, 0), None),
    ("vectorify_icon.png", "Vectorify", "vectorify_launcher", None, None, (25, 25), (0, 0), None),
    ("auto_tangent_icon.png", "Auto Tangent", None, None, None, (24, 24), (0, 0), [("All Keys", "auto_all_launcher"), ("Selected", "auto_current_launcher")]),
    ("linear_tangent_icon.png", "Linear Tangent", None, None, None, (24, 24), (0, 0), [("All Keys", "linear_all_launcher"), ("Selected", "linear_current_launcher")]),
    ("step_tangent_icon.png", "Step Tangent", None, None, None, (24, 24), (0, 0), [("All Keys", "step_all_launcher"), ("Selected", "step_current_launcher")]),
    ("quick_exporter_icon.png", "Quick Exporter", "quick_exporer_launcher", None, None, (24, 24), (0, 0), None),
    ("tools_editor_icon.png", "Tools Editor", "tools_editor_launcher", None, None, (24, 24), (0, 0), None),
    ("about_icon.png", "About", "about_launcher", None, None, (23, 23), (0, 0), None),
    ("reset_icon.png", "Reset Pose", "reset_pose_launcher", None, None, (23, 23), (0, 0), None),
    ("bake_icon.png", "Fast Bake", None, None, None, (23, 23), (0, 0), [("Bake - 7s", "fast_bake_7s", "Animo_Fast_Bake"), ("Bake - 6s", "fast_bake_6s", "Animo_Fast_Bake"), ("Bake - 5s", "fast_bake_5s", "Animo_Fast_Bake"), ("Bake - 4s", "fast_bake_4s", "Animo_Fast_Bake"), ("Bake - 3s", "fast_bake_3s", "Animo_Fast_Bake"), ("Bake - 2s", "fast_bake_2s", "Animo_Fast_Bake"), ("Bake - 1s", "fast_bake_1s", "Animo_Fast_Bake")]),
    ("share_keys.png", "Share Keys", "share_keys_launcher", None, None, (23, 23), (0, 0), None),
    ("SelectOpposite.png", "Select Opposite", None, "Animo_Tools_Editor/animo_tools/tools", None, (22, 22), (0, 0), [("Add Opposite", "SelectAddOppositeCtrls", "Animo_Tools_Editor/animo_tools/tools"), ("Select Opposite", "SelectOppositeCtrls", "Animo_Tools_Editor/animo_tools/tools")]),
    ("fast_multi_view_playblaster_icon.png", "Multi-View Playblaster", "fast_multi_view_playblaster_launcher", None, None, (23, 23), (0, 0), None),
    ("CropAnimation.png", "Crop Animation", "CropAnimation", "Animo_Tools_Editor/animo_tools/tools", None, (20, 20), (0, 0), None),
    ("DeleteRedundantKeys.png", "Delete Redundant Keys", "DeleteRedundantKeys", "Animo_Tools_Editor/animo_tools/tools", None, (20, 20), (0, 0), None),
    ("SmoothSelectedKeys.png", "Smooth Selected Keys", None, "Animo_Tools_Editor/animo_tools/tools", None, (20, 20), (0, 0), None),
    ("SmartSnapKeys.png", "Smart Snap Keys", "SmartSnapKeys", "Animo_Tools_Editor/animo_tools/tools", None, (20, 20), (0, 0), None),
]


def run_launcher(animo_data_path, icons_path, maya_version, launcher_name, tool_folder=None, entry_func=None):
    cmds.undoInfo(openChunk=True)
    try:
        # Add common dependency folders to sys.path
        common_folders = [
            "Animo_Space_Switcher", 
            "Animo_Tools_Editor", 
            "Animo_Tools_Editor/animo_tools",
            "Animo_Temp_Pivot"
        ]
        for folder in common_folders:
            folder_path = os.path.normpath(os.path.join(animo_data_path, folder))
            if os.path.exists(folder_path) and folder_path not in sys.path:
                sys.path.insert(0, folder_path)
        
        # Clear potentially conflicting cached modules
        conflicting_modules = ['compat', 'dpi_utils']
        for mod_name in list(sys.modules.keys()):
            if mod_name in conflicting_modules:
                del sys.modules[mod_name]
        
        if tool_folder:
            tool_path = os.path.normpath(os.path.join(animo_data_path, tool_folder))
            if tool_path not in sys.path:
                sys.path.insert(0, tool_path)
            
            # Install versioned finder for this tool
            install_versioned_finder([tool_path, icons_path], maya_version)
            
            for mod in list(sys.modules.keys()):
                if launcher_name in mod:
                    del sys.modules[mod]
            
            # Try .py file first
            py_path = os.path.normpath(os.path.join(tool_path, launcher_name + ".py"))
            if os.path.exists(py_path):
                with open(py_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                exec(compile(script_content, py_path, 'exec'), {'__name__': '__main__', '__file__': py_path})
                return
            
            # Try versioned .pyc
            pyc_versioned = os.path.normpath(os.path.join(tool_path, "{}_py{}.pyc".format(launcher_name, maya_version)))
            if os.path.exists(pyc_versioned):
                _run_pyc(pyc_versioned, launcher_name)
                return
            
            # Try regular .pyc
            pyc_path = os.path.normpath(os.path.join(tool_path, launcher_name + ".pyc"))
            if os.path.exists(pyc_path):
                _run_pyc(pyc_path, launcher_name)
                return
            
            # File not found - warn and return
            cmds.warning("Could not find {} in {}. Looked for: {}.py, {}_py{}.pyc, {}.pyc".format(
                launcher_name, tool_path, launcher_name, launcher_name, maya_version, launcher_name))
            return
        else:
            # No tool_folder - check if we need to import and run a function
            if entry_func:
                # Import module and call entry function
                _import_and_run(icons_path, launcher_name, maya_version, entry_func)
                return
            
            # Look for launcher script in icons_path
            py_path = os.path.normpath(os.path.join(icons_path, launcher_name + ".py"))
            if os.path.exists(py_path):
                with open(py_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                exec(compile(script_content, py_path, 'exec'), {'__name__': '__main__', '__file__': py_path})
                return
            
            # Try versioned .pyc
            pyc_versioned = os.path.normpath(os.path.join(icons_path, "{}_py{}.pyc".format(launcher_name, maya_version)))
            if os.path.exists(pyc_versioned):
                _run_pyc(pyc_versioned, launcher_name)
                return
            
            # Try regular .pyc
            pyc_path = os.path.normpath(os.path.join(icons_path, launcher_name + ".pyc"))
            if os.path.exists(pyc_path):
                _run_pyc(pyc_path, launcher_name)
                return
            
            cmds.warning("Could not find launcher: {}".format(launcher_name))
                
    except Exception as e:
        cmds.warning("Failed to run {}: {}".format(launcher_name, str(e)))
        import traceback
        traceback.print_exc()
    finally:
        cmds.undoInfo(closeChunk=True)


def _import_and_run(icons_path, module_name, maya_version, entry_func=None):
    """Import a module and run its entry function"""
    if icons_path not in sys.path:
        sys.path.insert(0, icons_path)
    
    # Install versioned finder
    install_versioned_finder([icons_path], maya_version)
    
    try:
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        module = __import__(module_name)
        
        if entry_func and hasattr(module, entry_func):
            getattr(module, entry_func)()
        elif hasattr(module, 'show'):
            module.show()
        elif hasattr(module, 'main'):
            module.main()
        elif hasattr(module, 'ui'):
            module.ui()
    except Exception as e:
        cmds.warning("Failed to launch {}: {}".format(module_name, str(e)))


def _run_pyc(pyc_path, module_name):
    """Execute a .pyc file"""
    import marshal
    
    try:
        with open(pyc_path, 'rb') as f:
            f.read(16)  # Skip header
            code = marshal.load(f)
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': pyc_path,
            '__builtins__': __builtins__,
        }
        
        exec(code, exec_globals)
        
    except Exception as e:
        cmds.warning("Failed to launch {}: {}".format(module_name, str(e)))


# ============================================================================
# SPACING CONFIGURATION - Adjust these values to fine-tune icon positions
# ============================================================================

# Individual icon offsets (negative = nudge left, positive = nudge right)
# Format: icon_index: (left_offset, right_offset) - only horizontal offset used
ICON_OFFSETS = {
    # Transify group (indices 0, 1, 2)
    0: -4,   # transify
    1: -3,   # keys_time
    2: -1,   # fast_anim_layers
    
    # Pickify group (indices 5, 3, 4)
    5: 0,   # pickify
    3: -1,   # tweenify
    4: 0,   # tracify
    
    # Spacify group (indices 6, 7, 8, 9)
    6: 0,   # spacify
    7: 0,   # xform_align
    8: 0,   # attributes_space_switcher
    9: 0,   # temp_pivot
    
    # Global offset group (indices 10, 11, 12)
    10: 1,  # global_offset
    11: 0,  # twosify
    12: 0,  # vectorify
    
    # Tangent icons (indices 13, 14, 15)
    13: 2,  # auto_tangent
    14: 2,  # linear_tangent
    15: 0,  # step_tangent
    
    # Exporter group (indices 16, 17, 18)
    16: 0,  # quick_exporter
    17: 3,  # tools_editor
    18: 0,  # about
    
    # Left slider icons (indices 19, 20, 21)
    19: 2,  # reset
    20: 3,  # bake
    21: 3,  # share_keys
    
    # White icons near cascade (indices 22, 23, 24, 25, 26, 27)
    22: 0,  # SelectOpposite
    23: 0,  # Playblaster
    24: 0,  # CropAnimation
    25: 0,  # DeleteRedundantKeys
    26: 0,  # SmoothSelectedKeys
    27: 0,  # SmartSnapKeys
}

# Group spacing (space between icon groups)
GROUP_SPACING = 9

# Icon spacing within groups
ICON_SPACING_WITHIN_GROUP = 2

# Left slider icons spacing
LEFT_SLIDER_SPACING = 4

# Master layout spacings
SPACING_LEFT_SLIDER_TO_TWEEN = 10
SPACING_TWEEN_TO_BLEND = 14
SPACING_BLEND_TO_TANGENT = 0
SPACING_TANGENT_TO_ICONS = 8
SPACING_ICONS_TO_SCALE = 12
SPACING_SCALE_TO_CASCADE = 12
SPACING_CASCADE_TO_COUNTER = 10
SPACING_COUNTER_TO_SELOPP = 10
SPACING_WHITE_ICONS = 6  # Between smooth, snap, crop, delkeys
SPACING_DELKEYS_TO_DOCK = 20

# Toolbar content width
TOOLBAR_CONTENT_WIDTH = 1860