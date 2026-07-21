from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

# Get the directory where this file is located
# __file__ is set by the launcher when executing
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

# Import dialog_main using versioned import
import dialog_main as dialog_main
AnimoToolsDialog = dialog_main.AnimoToolsDialog

animo_dialog = None


def show_animo_tools():
    global animo_dialog
    
    try:
        animo_dialog.close()
        animo_dialog.deleteLater()
    except Exception:
        pass
    
    animo_dialog = AnimoToolsDialog()
    animo_dialog.show()
    
    return animo_dialog


if __name__ == "__main__":
    show_animo_tools()
