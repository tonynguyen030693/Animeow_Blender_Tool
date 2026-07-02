# ─────────────────────────────────────────────────────────────
# Graph Toolboard – Property Definitions
# ─────────────────────────────────────────────────────────────
import bpy

def update_tween(self, context):
    from .operators import update_tween_slider
    update_tween_slider(self, context)

def get_loop_before(self):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for mod in selected_fcurves[0].modifiers:
            if mod.type == 'CYCLES':
                items = ['NONE', 'REPEAT', 'REPEAT_OFFSET', 'MIRROR']
                if mod.mode_before in items:
                    return items.index(mod.mode_before)
    return 0

def set_loop_before(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        items = ['NONE', 'REPEAT', 'REPEAT_OFFSET', 'MIRROR']
        val_str = items[value]
        for fcurve in selected_fcurves:
            cycles_mod = None
            for mod in fcurve.modifiers:
                if mod.type == 'CYCLES':
                    cycles_mod = mod
                    break
            if val_str != 'NONE' and not cycles_mod:
                cycles_mod = fcurve.modifiers.new(type='CYCLES')
                cycles_mod.mode_after = 'NONE'
                cycles_mod.cycles_before = 0
                cycles_mod.cycles_after = 0
                cycles_mod.mute = False
                cycles_mod.use_restricted_range = False
            if cycles_mod:
                cycles_mod.mode_before = val_str
                if cycles_mod.mode_before == 'NONE' and cycles_mod.mode_after == 'NONE':
                    fcurve.modifiers.remove(cycles_mod)
            fcurve.update()

def get_loop_after(self):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for mod in selected_fcurves[0].modifiers:
            if mod.type == 'CYCLES':
                items = ['NONE', 'REPEAT', 'REPEAT_OFFSET', 'MIRROR']
                if mod.mode_after in items:
                    return items.index(mod.mode_after)
    return 0

def set_loop_after(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        items = ['NONE', 'REPEAT', 'REPEAT_OFFSET', 'MIRROR']
        val_str = items[value]
        for fcurve in selected_fcurves:
            cycles_mod = None
            for mod in fcurve.modifiers:
                if mod.type == 'CYCLES':
                    cycles_mod = mod
                    break
            if val_str != 'NONE' and not cycles_mod:
                cycles_mod = fcurve.modifiers.new(type='CYCLES')
                cycles_mod.mode_before = 'NONE'
                cycles_mod.cycles_before = 0
                cycles_mod.cycles_after = 0
                cycles_mod.mute = False
                cycles_mod.use_restricted_range = False
            if cycles_mod:
                cycles_mod.mode_after = val_str
                if cycles_mod.mode_before == 'NONE' and cycles_mod.mode_after == 'NONE':
                    fcurve.modifiers.remove(cycles_mod)
            fcurve.update()

def get_active_fcurve():
    context = bpy.context
    active = getattr(context, "active_editable_fcurve", None)
    if active:
        return active
    selected = getattr(context, "selected_editable_fcurves", None)
    if selected:
        return selected[0]
    return None

def get_cycles_mod(fcurve):
    if fcurve:
        for mod in fcurve.modifiers:
            if mod.type == 'CYCLES':
                return mod
    return None

def get_loop_active(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return (not mod.mute) if mod else False

def set_loop_active(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.mute = not value
            fcurve.update()

def get_loop_use_range(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return mod.use_restricted_range if mod else False

def set_loop_use_range(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.use_restricted_range = value
            fcurve.update()

def get_loop_cycles_before(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return mod.cycles_before if mod else 0

def set_loop_cycles_before(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.cycles_before = value
            fcurve.update()

def get_loop_cycles_after(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return mod.cycles_after if mod else 0

def set_loop_cycles_after(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.cycles_after = value
            fcurve.update()

def get_loop_range_start(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return mod.frame_start if mod else 0.0

def set_loop_range_start(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.frame_start = value
            fcurve.update()

def get_loop_range_end(self):
    fc = get_active_fcurve()
    mod = get_cycles_mod(fc)
    return mod.frame_end if mod else 0.0

def set_loop_range_end(self, value):
    context = bpy.context
    selected_fcurves = getattr(context, "selected_editable_fcurves", None)
    if selected_fcurves:
        for fcurve in selected_fcurves:
            mod = get_cycles_mod(fcurve)
            if mod:
                mod.frame_end = value
            fcurve.update()

class GraphToolboardProperties(bpy.types.PropertyGroup):
    tween_slider: bpy.props.FloatProperty(
        name="Tween Slider",
        description="Blend keyframes between previous and next keys",
        default=50.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        update=update_tween
    )

    # Quick settings for panel inputs
    nudge_frames: bpy.props.IntProperty(
        name="Nudge Frames",
        description="Number of frames to shift selected keys",
        default=1,
        min=1,
        max=100
    )
    
    scale_pivot_mode: bpy.props.EnumProperty(
        name="Scale Pivot",
        description="Reference point for scaling key values",
        items=[
            ('AVERAGE', 'Average', 'Scale relative to the average of selected keys'),
            ('NEIGHBOR_LEFT', 'Neighbor Left', 'Scale relative to the keyframe before the selection'),
            ('NEIGHBOR_RIGHT', 'Neighbor Right', 'Scale relative to the keyframe after the selection'),
            ('CURSOR', 'Cursor Value', 'Scale relative to the 2D cursor Y value'),
            ('ZERO', 'Zero Value', 'Scale relative to Y = 0')
        ],
        default='AVERAGE'
    )

    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Factor to scale key values (e.g. 1.1 = +10%, 0.9 = -10%)",
        default=1.0,
        min=-10.0,
        max=10.0
    )

    paste_mode: bpy.props.EnumProperty(
        name="Paste Mode",
        description="Method to paste copied keyframes",
        items=[
            ('MERGE', 'Merge', 'Merge keys, overwriting only overlapping frames'),
            ('INSERT', 'Insert', 'Insert keys and shift existing keys to the right'),
            ('REPLACE', 'Replace', 'Replace all keys within the pasted time range')
        ],
        default='MERGE'
    )
    
    paste_pivot: bpy.props.EnumProperty(
        name="Paste Pivot",
        description="Anchor point for pasting keyframes",
        items=[
            ('CURRENT', 'At Current Frame', 'Paste starting at the current timeline frame'),
            ('CUSTOM', 'At Specific Frame', 'Paste starting at a specific custom frame')
        ],
        default='CURRENT'
    )
    
    paste_custom_frame: bpy.props.FloatProperty(
        name="Target Frame",
        description="Specific frame number to paste keyframes at",
        default=1.0,
        precision=1
    )

    clean_threshold: bpy.props.FloatProperty(
        name="Clean Threshold",
        description="Max deviation for keyframe to be considered redundant",
        default=0.001,
        min=0.0,
        max=1.0,
        precision=4
    )

    loop_mode_before: bpy.props.EnumProperty(
        name="Pre-Infinity",
        description="Looping mode before the first keyframe",
        items=[
            ('NONE', 'Constant', 'No cycle'),
            ('REPEAT', 'Repeat', 'Standard repeat loop'),
            ('REPEAT_OFFSET', 'Offset Repeat', 'Repeat loop adding the offset between start and end values'),
            ('MIRROR', 'Oscillate (Mirror)', 'Mirror/Ping-pong loop')
        ],
        get=get_loop_before,
        set=set_loop_before
    )

    loop_mode_after: bpy.props.EnumProperty(
        name="Post-Infinity",
        description="Looping mode after the last keyframe",
        items=[
            ('NONE', 'Constant', 'No cycle'),
            ('REPEAT', 'Repeat', 'Standard repeat loop'),
            ('REPEAT_OFFSET', 'Offset Repeat', 'Repeat loop adding the offset between start and end values'),
            ('MIRROR', 'Oscillate (Mirror)', 'Mirror/Ping-pong loop')
        ],
        get=get_loop_after,
        set=set_loop_after
    )

    loop_active: bpy.props.BoolProperty(
        name="Active Loop",
        description="Enable/Disable evaluating the Cycles modifier on selected curves",
        get=get_loop_active,
        set=set_loop_active
    )

    loop_use_range: bpy.props.BoolProperty(
        name="Limit Range",
        description="Restrict loop modifier evaluation to a custom frame range",
        get=get_loop_use_range,
        set=set_loop_use_range
    )

    loop_cycles_before: bpy.props.IntProperty(
        name="Pre Cycles",
        description="Number of cycles to evaluate before the first keyframe (0 = infinite)",
        min=0,
        max=1000,
        get=get_loop_cycles_before,
        set=set_loop_cycles_before
    )

    loop_cycles_after: bpy.props.IntProperty(
        name="Post Cycles",
        description="Number of cycles to evaluate after the last keyframe (0 = infinite)",
        min=0,
        max=1000,
        get=get_loop_cycles_after,
        set=set_loop_cycles_after
    )

    loop_range_start: bpy.props.FloatProperty(
        name="Start Frame",
        description="Start frame for restricted range evaluation",
        get=get_loop_range_start,
        set=set_loop_range_start
    )

    loop_range_end: bpy.props.FloatProperty(
        name="End Frame",
        description="End frame for restricted range evaluation",
        get=get_loop_range_end,
        set=set_loop_range_end
    )


def register():
    bpy.utils.register_class(GraphToolboardProperties)
    bpy.types.Scene.graph_toolboard = bpy.props.PointerProperty(type=GraphToolboardProperties)


def unregister():
    bpy.utils.unregister_class(GraphToolboardProperties)
    del bpy.types.Scene.graph_toolboard
