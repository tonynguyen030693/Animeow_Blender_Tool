from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import maya.cmds as cmds


def get_animo_data_path():
    maya_scripts = cmds.internalVar(userScriptDir=True)
    animo_data_dir = os.path.join(maya_scripts, "Animo_Data", "Animo_Tools_Editor")
    
    if not os.path.exists(animo_data_dir):
        os.makedirs(animo_data_dir)
    
    return animo_data_dir


def get_tools_data_file():
    return os.path.join(get_animo_data_path(), "animo_tools.json")


def get_hotkeys_data_file():
    return os.path.join(get_animo_data_path(), "animo_hotkeys.json")


def save_tools_data(data):
    try:
        file_path = get_tools_data_file()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False


def load_tools_data():
    try:
        file_path = get_tools_data_file()
        if not os.path.exists(file_path):
            return {'custom_tools': [], 'custom_categories': []}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {'custom_tools': [], 'custom_categories': []}


def save_hotkeys_data(hotkeys_dict):
    try:
        file_path = get_hotkeys_data_file()
        with open(file_path, 'w') as f:
            json.dump(hotkeys_dict, f, indent=4)
        return True
    except Exception:
        return False


def load_hotkeys_data():
    try:
        file_path = get_hotkeys_data_file()
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def export_hotkeys(export_path, hotkeys_dict):
    try:
        with open(export_path, 'w') as f:
            json.dump(hotkeys_dict, f, indent=4)
        return True
    except Exception:
        return False


def import_hotkeys(import_path):
    try:
        if not os.path.exists(import_path):
            return None
        
        with open(import_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None
