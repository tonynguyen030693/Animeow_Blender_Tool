import sys
import os
import maya.cmds as cmds
import maya.mel as mel
import shutil


ENABLE_USERSETUP = False


ENABLE_TIMELINE_HEIGHT_ADJUST = True


TIMELINE_HEIGHT_OPEN = 0    
TIMELINE_HEIGHT_CLOSE = 0  

CLOSE_TIMER_MS = 100
OPEN_TIMER_MS = 500

version_script_dir = cmds.internalVar(userScriptDir=True)
script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
animo_data_path = os.path.join(script_dir, "Animo_Data")

if ENABLE_USERSETUP:
    try:
       cmds.optionVar(intValue=("SafeModeExecUserSetupScript", 1))
    except:
       pass

if os.path.exists(animo_data_path):
    for subfolder in ["Animo_UI", "Animo_Launcher"]:
        pycache = os.path.join(animo_data_path, subfolder, "__pycache__")
        if os.path.exists(pycache):
            shutil.rmtree(pycache)

animo_visible = False
qt_toolbar_visible = False
existing_qt_toolbar = None

if cmds.workspaceControl('animo', exists=True):
    animo_visible = cmds.workspaceControl('animo', query=True, visible=True)

try:
    import maya.OpenMayaUI as mui
    try:
        from PySide2 import QtWidgets, QtCore
        from shiboken2 import wrapInstance
    except ImportError:
        from PySide6 import QtWidgets, QtCore
        from shiboken6 import wrapInstance
    
    maya_main_ptr = mui.MQtUtil.mainWindow()
    if maya_main_ptr:
        maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
        existing_qt_toolbar = maya_main.findChild(QtWidgets.QWidget, "animo_qt_toolbar")
        if existing_qt_toolbar and existing_qt_toolbar.isVisible():
            qt_toolbar_visible = True
except:
    pass

stored_timeline_height = None
try:
    if animo_data_path not in sys.path:
        sys.path.insert(0, animo_data_path)
    from Animo_UI import get_timeline_height
    stored_timeline_height = get_timeline_height.queryTimelineHeight()
except:
    pass

if animo_visible or qt_toolbar_visible:
    if cmds.workspaceControl('animo', exists=True):
        cmds.workspaceControl('animo', edit=True, visible=False)
    
    if existing_qt_toolbar:
        try:
            existing_qt_toolbar.hide()
        except:
            pass
    
    if ENABLE_TIMELINE_HEIGHT_ADJUST and stored_timeline_height is not None:
        def apply_height_close():
            try:
                import maya.mel as mel
                original_height = stored_timeline_height + TIMELINE_HEIGHT_CLOSE
                time_slider_name = mel.eval('$tmpVar=$gPlayBackSlider')
                ptr = mui.MQtUtil.findControl(time_slider_name)
                if ptr:
                    time_slider = wrapInstance(int(ptr), QtWidgets.QWidget)
                    current = time_slider
                    for _ in range(20):
                        if not current:
                            break
                        parent = current.parent()
                        if parent and parent.__class__.__name__ == 'QSplitter':
                            splitter = parent
                            idx = splitter.indexOf(current)
                            if idx >= 0:
                                sizes = splitter.sizes()
                                current_size = sizes[idx]
                                if current_size != original_height:
                                    difference = current_size - original_height
                                    if idx > 0:
                                        sizes[idx - 1] += difference
                                    sizes[idx] = original_height
                                    splitter.setSizes(sizes)
                                break
                        current = parent
            except:
                pass
        
        QtCore.QTimer.singleShot(CLOSE_TIMER_MS, apply_height_close)
else:
    if cmds.workspaceControl('animo', exists=True):
        cmds.deleteUI('animo', control=True)
    
    if existing_qt_toolbar:
        try:
            existing_qt_toolbar.hide()
            existing_qt_toolbar.setParent(None)
            existing_qt_toolbar.deleteLater()
        except:
            pass
    
    mods_to_delete = [mod for mod in list(sys.modules.keys()) 
                      if 'Animo' in mod or 'animo' in mod or 'styleMod' in mod or 'barMod' in mod]
    for mod in mods_to_delete:
        del sys.modules[mod]
    
    sys.path = [p for p in sys.path if 'Animo' not in p and 'animo' not in p]
    
    if os.path.exists(animo_data_path):
        animo_launcher_dir = os.path.join(animo_data_path, "Animo_Launcher")
        
        for p in [script_dir, animo_data_path, animo_launcher_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)
    
    if os.path.exists(animo_data_path):
        launcher_file = os.path.join(animo_data_path, "Animo_Launcher", "Animo_Launcher.py")
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