"""
Tools Editor Launcher
Launches the Animo Tools Editor from the Animo Launcher
Works with both .py files and versioned .pyc files (e.g., _py2026.pyc)
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import re
import marshal
import importlib.abc
import importlib.machinery
import importlib.util
import maya.cmds as cmds


def get_maya_version():
    return int(cmds.about(version=True)[:4])


MAYA_VERSION = get_maya_version()


class VersionedModuleFinder(importlib.abc.MetaPathFinder):
    """Custom finder that redirects imports to version-specific .pyc files"""
    
    def __init__(self, search_paths, maya_version):
        self.search_paths = search_paths
        self.maya_version = maya_version
    
    def find_spec(self, fullname, path, target=None):
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            # First check if .py exists (priority)
            py_path = os.path.join(search_path, fullname + ".py")
            if os.path.exists(py_path):
                return None  # Let normal import handle it
            
            # Check for exact version .pyc
            versioned_pyc = os.path.join(search_path, "{0}_py{1}.pyc".format(fullname, self.maya_version))
            if os.path.exists(versioned_pyc):
                loader = importlib.machinery.SourcelessFileLoader(fullname, versioned_pyc)
                return importlib.util.spec_from_loader(fullname, loader, origin=versioned_pyc)
            
            # Check for generic .pyc
            generic_pyc = os.path.join(search_path, fullname + ".pyc")
            if os.path.exists(generic_pyc):
                loader = importlib.machinery.SourcelessFileLoader(fullname, generic_pyc)
                return importlib.util.spec_from_loader(fullname, loader, origin=generic_pyc)
        
        return None


_versioned_finder = None

def install_versioned_finder(search_paths):
    """Install the versioned module finder"""
    global _versioned_finder
    
    if _versioned_finder is not None:
        try:
            sys.meta_path.remove(_versioned_finder)
        except ValueError:
            pass
    
    _versioned_finder = VersionedModuleFinder(search_paths, MAYA_VERSION)
    sys.meta_path.insert(0, _versioned_finder)


def get_animo_tools_path():
    """Get the path to animo_tools folder in Maya scripts directory"""
    # Always use Maya's scripts folder - works on all machines
    maya_scripts_dir = cmds.internalVar(userScriptDir=True)
    # Go from maya/2026/scripts to maya/scripts (global scripts folder)
    global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
    
    return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")


def find_versioned_file(folder, base_name):
    """Find the best matching file for current Maya version"""
    # Check for .py first
    py_path = os.path.join(folder, base_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    
    # Check for exact version .pyc
    versioned_pyc = os.path.join(folder, "{0}_py{1}.pyc".format(base_name, MAYA_VERSION))
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    
    # Scan for other versioned .pyc files (find closest compatible version)
    pattern = re.compile(r'^' + re.escape(base_name) + r'_py(\d{4})\.pyc$', re.IGNORECASE)
    available_versions = []
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            match = pattern.match(filename)
            if match:
                file_version = int(match.group(1))
                available_versions.append((file_version, filename))
    
    if available_versions:
        available_versions.sort(key=lambda x: x[0], reverse=True)
        
        # Find closest version <= current Maya version
        for file_version, filename in available_versions:
            if file_version <= MAYA_VERSION:
                return os.path.join(folder, filename), "pyc"
        
        # Fall back to oldest available
        return os.path.join(folder, available_versions[-1][1]), "pyc"
    
    # Check for generic .pyc
    generic_pyc = os.path.join(folder, base_name + ".pyc")
    if os.path.exists(generic_pyc):
        return generic_pyc, "pyc"
    
    return None, None


def show():
    # Get path to animo_tools folder - ALWAYS from Maya scripts folder
    animo_tools_path = get_animo_tools_path()
    
    # Store in sys so other modules can access it
    sys._animo_tools_path = animo_tools_path
    
    # Add to sys.path
    if animo_tools_path not in sys.path:
        sys.path.insert(0, animo_tools_path)
    
    # IMPORTANT: Install versioned finder BEFORE importing any modules
    install_versioned_finder([animo_tools_path])
    
    # Find the manager file
    filepath, filetype = find_versioned_file(animo_tools_path, "animo_tools_manager")
    
    if filepath is None:
        cmds.warning("Could not find animo_tools_manager in: {0}".format(animo_tools_path))
        return
    
    try:
        exec_globals = {
            '__name__': '__main__',
            '__file__': filepath,
            '__builtins__': __builtins__,
        }
        
        if filetype == "py":
            with open(filepath, 'r') as f:
                code = compile(f.read(), filepath, 'exec')
        else:
            with open(filepath, 'rb') as f:
                f.read(16)
                code = marshal.load(f)
        
        exec(code, exec_globals)
        
        if 'show_animo_tools' in exec_globals:
            exec_globals['show_animo_tools']()
        else:
            cmds.warning("show_animo_tools not found in module")
            
    except Exception as e:
        cmds.warning("Error launching Tools Editor: {0}".format(str(e)))
        import traceback
        traceback.print_exc()


def main():
    show()


if __name__ == "__main__":
    show()