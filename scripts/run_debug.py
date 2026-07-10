# -*- coding: utf-8 -*-
import os
import sys

script_path = os.environ.get("MAYA_DEBUG_SCRIPT", "")
script_dir = os.path.dirname(os.path.abspath(script_path))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import maya_scene_debugger
maya_scene_debugger.run_from_batch()
