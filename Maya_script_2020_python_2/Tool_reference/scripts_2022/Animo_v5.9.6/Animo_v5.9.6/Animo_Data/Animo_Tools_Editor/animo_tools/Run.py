from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import maya.cmds as cmds

try:
    import animo_tools
    if hasattr(animo_tools, 'animo_dialog'):
        dialog = animo_tools.animo_dialog
        if dialog:
            dialog.close()
            dialog.deleteLater()
except Exception:
    pass

modules_to_remove = [m for m in sys.modules.keys() if 'animo' in m.lower()]
for module_name in modules_to_remove:
    del sys.modules[module_name]

maya_scripts_dir = cmds.internalVar(userScriptDir=True)
animo_tools_path = os.path.join(maya_scripts_dir, "Animo_Data", "Animo_Tools_Editor")

if animo_tools_path not in sys.path:
    sys.path.insert(0, animo_tools_path)

import animo_tools
animo_tools.show_animo_tools()
