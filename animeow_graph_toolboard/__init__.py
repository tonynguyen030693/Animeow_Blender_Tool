# ─────────────────────────────────────────────────────────────
# Graph Toolboard – Blender Add-on
# ─────────────────────────────────────────────────────────────
# An animation tool board for Blender's Graph Editor.
# Inspired by AnimBot and aTools, providing Tween, Ease, Scale,
# Time Nudge, Mirror, Snap, and Clean tools with interactive HUD.
# ─────────────────────────────────────────────────────────────

bl_info = {
    "name": "Animeow Graph Toolboard",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Graph Editor > Sidebar > Tool Board",
    "description": "Professional animation helper tools for the Graph Editor, inspired by AnimBot and aTools",
    "category": "Animation",
}

from . import properties
from . import operators
from . import panels

_modules = (
    properties,
    operators,
    panels,
)

def register():
    for mod in _modules:
        mod.register()
    print("[Animeow Graph Toolboard] Registered successfully")

def unregister():
    for mod in reversed(_modules):
        mod.unregister()
    print("[Animeow Graph Toolboard] Unregistered successfully")

if __name__ == "__main__":
    register()
