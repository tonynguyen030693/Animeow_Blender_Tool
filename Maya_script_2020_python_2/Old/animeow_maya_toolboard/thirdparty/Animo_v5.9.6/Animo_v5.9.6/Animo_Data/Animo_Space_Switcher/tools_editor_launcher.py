import sys
import os
import maya.cmds as cmds

# Clear any old cached modules
modules_to_remove = [m for m in sys.modules.keys() if 'animo' in m.lower()]
for module_name in modules_to_remove:
    del sys.modules[module_name]

# Add the path
animo_path = r"C:\Users\Zephyrus\Documents\maya\scripts\Animo_Data\Animo_Tools_Editor"
if animo_path not in sys.path:
    sys.path.insert(0, animo_path)

# Import and show
import animo_tools
animo_tools.show_animo_tools()