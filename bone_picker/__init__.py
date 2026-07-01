# ─────────────────────────────────────────────────────────────
# BonePicker – Blender Add-on
# ─────────────────────────────────────────────────────────────
# A visual bone-picker tool for Blender, inspired by DWPicker
# for Maya.  Lets you design a canvas of clickable buttons that
# select pose-bones on an armature.
# ─────────────────────────────────────────────────────────────

bl_info = {
    "name": "BonePicker",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > Sidebar > Picker",
    "description": "Visual bone-picker for animation, inspired by DWPicker (Maya)",
    "category": "Animation",
}

# ── Sub-module imports ──────────────────────────────────────
# Each sub-module exposes its own register() / unregister().

from . import properties
from . import operators
from . import animate_handler
from . import io_handler
from . import panels


_modules = (
    properties,
    operators,
    animate_handler,
    io_handler,
    panels,
)


def register():
    for mod in _modules:
        mod.register()
    print("[BonePicker] Add-on registered")


def unregister():
    # Clean up the draw handler if still running
    from .animate_handler import PICKER_OT_interact
    if PICKER_OT_interact._draw_handler is not None:
        import bpy
        bpy.types.SpaceView3D.draw_handler_remove(
            PICKER_OT_interact._draw_handler, 'WINDOW')
        PICKER_OT_interact._draw_handler = None
        PICKER_OT_interact._is_running = False

    for mod in reversed(_modules):
        mod.unregister()
    print("[BonePicker] Add-on unregistered")


if __name__ == "__main__":
    register()
