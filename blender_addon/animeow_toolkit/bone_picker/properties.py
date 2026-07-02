# ─────────────────────────────────────────────────────────────
# BonePicker – Data model (PropertyGroups)
# ─────────────────────────────────────────────────────────────
import bpy
from bpy.props import (
    BoolProperty, CollectionProperty, EnumProperty,
    FloatProperty, FloatVectorProperty, IntProperty,
    PointerProperty, StringProperty,
)


def _sync_selected_buttons(self, context, prop_name):
    # Avoid recursive loops
    if getattr(_sync_selected_buttons, "_updating", False):
        return
    _sync_selected_buttons._updating = True
    try:
        picker = context.scene.bone_picker
        if picker.tabs:
            tab = picker.tabs[picker.active_tab_index]
            if self.selected:
                val = getattr(self, prop_name)
                for b in tab.buttons:
                    if b.selected and b != self:
                        if hasattr(val, "copy"):
                            setattr(b, prop_name, val.copy())
                        elif isinstance(val, (list, tuple)) or hasattr(val, "__len__"):
                            for idx_val in range(len(val)):
                                getattr(b, prop_name)[idx_val] = val[idx_val]
                        else:
                            setattr(b, prop_name, val)
    except Exception as e:
        print(f"[BonePicker] Error syncing property {prop_name}: {e}")
    finally:
        _sync_selected_buttons._updating = False

# Individual update callbacks
def update_width(self, context): _sync_selected_buttons(self, context, 'width')
def update_height(self, context): _sync_selected_buttons(self, context, 'height')
def update_shape(self, context): _sync_selected_buttons(self, context, 'shape')
def update_corner_radius(self, context): _sync_selected_buttons(self, context, 'corner_radius')
def update_color_normal(self, context): _sync_selected_buttons(self, context, 'color_normal')
def update_color_hover(self, context): _sync_selected_buttons(self, context, 'color_hover')
def update_color_selected(self, context): _sync_selected_buttons(self, context, 'color_selected')
def update_border_color(self, context): _sync_selected_buttons(self, context, 'border_color')
def update_text_color(self, context): _sync_selected_buttons(self, context, 'text_color')


class PickerButtonItem(bpy.types.PropertyGroup):
    """A single button on the picker canvas."""

    # ── Edit Mode Selection ─────────────────────────────────
    selected: BoolProperty(name="Selected", default=False)

    # ── Position & Size ─────────────────────────────────────
    pos_x: FloatProperty(name="X", default=0.0)
    pos_y: FloatProperty(name="Y", default=0.0)
    width: FloatProperty(name="Width", default=80.0, min=10.0, update=update_width)
    height: FloatProperty(name="Height", default=25.0, min=10.0, update=update_height)

    # ── Shape ───────────────────────────────────────────────
    shape: EnumProperty(
        name="Shape",
        items=[
            ('RECT', "Rectangle", "Rectangular button"),
            ('ROUND', "Ellipse", "Elliptical button"),
            ('ROUNDED_RECT', "Rounded Rect", "Rectangle with rounded corners"),
        ],
        default='ROUNDED_RECT',
        update=update_shape,
    )
    corner_radius: FloatProperty(
        name="Corner Radius", default=4.0, min=0.0, max=50.0, update=update_corner_radius)

    # ── Colors ──────────────────────────────────────────────
    color_normal: FloatVectorProperty(
        name="Normal Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.35, 0.35, 0.35, 1.0),
        update=update_color_normal,
    )
    color_hover: FloatVectorProperty(
        name="Hover Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.50, 0.50, 0.50, 1.0),
        update=update_color_hover,
    )
    color_selected: FloatVectorProperty(
        name="Selected Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.90, 0.70, 0.15, 1.0),
        update=update_color_selected,
    )
    border_color: FloatVectorProperty(
        name="Border Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
        update=update_border_color,
    )
    text_color: FloatVectorProperty(
        name="Text Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_text_color,
    )

    # ── Label ───────────────────────────────────────────────
    label: StringProperty(name="Label", default="Button")

    # ── Bone targets (comma-separated names) ────────────────
    bone_targets: StringProperty(
        name="Bone Targets", default="",
        description="Comma-separated list of bone names assigned to this button",
    )

    # ── Armature reference ──────────────────────────────────
    armature_name: StringProperty(
        name="Armature", default="",
        description="Name of the armature object these bones belong to",
    )

    def get_bone_list(self):
        """Parse bone_targets string into a list of names."""
        if not self.bone_targets:
            return []
        return [n.strip() for n in self.bone_targets.split(',') if n.strip()]

    def set_bone_list(self, names):
        """Set bone_targets from a list of names."""
        self.bone_targets = ', '.join(names)


class PickerTabItem(bpy.types.PropertyGroup):
    """One tab / page of the picker (a named collection of buttons)."""

    name: StringProperty(name="Tab Name", default="Untitled")
    canvas_width: FloatProperty(name="Canvas Width", default=600.0, min=100.0)
    canvas_height: FloatProperty(name="Canvas Height", default=400.0, min=100.0)
    background_image: StringProperty(
        name="Background Image", subtype='FILE_PATH', default="")

    buttons: CollectionProperty(type=PickerButtonItem)
    active_button_index: IntProperty(name="Active Button", default=-1)


class PickerSceneProperties(bpy.types.PropertyGroup):
    """Root property group attached to bpy.types.Scene."""

    tabs: CollectionProperty(type=PickerTabItem)
    active_tab_index: IntProperty(name="Active Tab", default=0)

    edit_mode: BoolProperty(
        name="Edit Mode",
        description="Toggle between Edit mode (design) and Animate mode (use)",
        default=False,
    )

    # ── Viewport mapping (zoom / pan) ───────────────────────
    zoom: FloatProperty(name="Zoom", default=1.0, min=0.1, max=5.0)
    pan_x: FloatProperty(name="Pan X", default=0.0)
    pan_y: FloatProperty(name="Pan Y", default=0.0)

    # ── Armature link ───────────────────────────────────────
    armature_name: StringProperty(
        name="Armature",
        description="Name of the armature this picker is linked to",
        default="",
    )


# ── Registration ────────────────────────────────────────────

classes = (
    PickerButtonItem,
    PickerTabItem,
    PickerSceneProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bone_picker = PointerProperty(type=PickerSceneProperties)


def unregister():
    del bpy.types.Scene.bone_picker
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
