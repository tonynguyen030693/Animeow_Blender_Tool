# ─────────────────────────────────────────────────────────────
# Graph Toolboard – Panels
# ─────────────────────────────────────────────────────────────
import bpy

class GRAPH_PT_toolboard_main(bpy.types.Panel):
    """Main Panel for Graph Toolboard"""
    bl_label = "⚡ Graph Toolboard"
    bl_idname = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool Board"

    def draw(self, context):
        layout = self.layout
        has_selection = bool(context.selected_editable_fcurves)
        if not has_selection:
            layout.label(text="Please select keyframes to edit.", icon='INFO')


class GRAPH_PT_toolboard_tween(bpy.types.Panel):
    """Tween Slider Subpanel"""
    bl_label = "Tween Slider"
    bl_idname = "GRAPH_PT_toolboard_tween"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        
        col_tween = layout.column(align=True)
        col_tween.prop(props, "tween_slider", text="", slider=True)
        
        row_pres = col_tween.row(align=True)
        row_pres.operator("graph.toolboard_quick_tween", text="0%").factor = 0.0
        row_pres.operator("graph.toolboard_quick_tween", text="25%").factor = 0.25
        row_pres.operator("graph.toolboard_quick_tween", text="50%").factor = 0.50
        row_pres.operator("graph.toolboard_quick_tween", text="75%").factor = 0.75
        row_pres.operator("graph.toolboard_quick_tween", text="100%").factor = 1.0


class GRAPH_PT_toolboard_interactive(bpy.types.Panel):
    """Interactive Sliders Subpanel"""
    bl_label = "Interactive Sliders"
    bl_idname = "GRAPH_PT_toolboard_interactive"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        
        col_drag = layout.column(align=True)
        
        row_drag = col_drag.row(align=True)
        row_drag.scale_y = 1.3
        op = row_drag.operator("graph.toolboard_modal_slider", text="Push / Pull", icon='ARROW_LEFTRIGHT')
        op.mode = 'PUSH_PULL'

        col_drag.separator()
        col_drag.label(text="Scale Value & Pivot:")
        
        row_scale_pivot = col_drag.row(align=True)
        row_scale_pivot.prop(props, "scale_pivot_mode", text="Pivot")
        
        row_scale = col_drag.row(align=True)
        row_scale.prop(props, "scale_factor", text="Factor")
        
        row_scale2 = col_drag.row(align=True)
        row_scale2.scale_y = 1.2
        op = row_scale2.operator("graph.toolboard_modal_slider", text="Interactive Scale", icon='FULLSCREEN_ENTER')
        op.mode = 'SCALE'
        op.pivot_mode = props.scale_pivot_mode


class GRAPH_PT_toolboard_nudge(bpy.types.Panel):
    """Nudge Keys Subpanel"""
    bl_label = "Nudge Keys"
    bl_idname = "GRAPH_PT_toolboard_nudge"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        
        col_time = layout.column(align=True)
        row = col_time.row(align=True)
        row.prop(props, "nudge_frames", text="Frames")
        row.operator("graph.toolboard_nudge_keys", text="", icon='TRIA_LEFT').direction = 'LEFT'
        row.operator("graph.toolboard_nudge_keys", text="", icon='TRIA_RIGHT').direction = 'RIGHT'


class GRAPH_PT_toolboard_mirror(bpy.types.Panel):
    """Mirror Keys Subpanel"""
    bl_label = "Mirror Keys"
    bl_idname = "GRAPH_PT_toolboard_mirror"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        
        col_mirror = layout.column(align=True)
        
        row1 = col_mirror.row(align=True)
        row1.operator("graph.toolboard_mirror_keys", text="Time Over Left", icon='TRACKING_BACKWARDS').mode = 'TIME_LEFT'
        row1.operator("graph.toolboard_mirror_keys", text="Value Over Left", icon='TRIA_LEFT').mode = 'VALUE_LEFT'
        
        row2 = col_mirror.row(align=True)
        row2.operator("graph.toolboard_mirror_keys", text="Time Over Right", icon='TRACKING_FORWARDS').mode = 'TIME_RIGHT'
        row2.operator("graph.toolboard_mirror_keys", text="Value Over Right", icon='TRIA_RIGHT').mode = 'VALUE_RIGHT'
        
        row3 = col_mirror.row(align=True)
        row3.operator("graph.toolboard_mirror_keys", text="Time Over Avg", icon='ALIGN_CENTER').mode = 'TIME_AVG'
        row3.operator("graph.toolboard_mirror_keys", text="Value Over Avg", icon='ALIGN_JUSTIFY').mode = 'VALUE_AVG'
        
        row4 = col_mirror.row(align=True)
        row4.operator("graph.toolboard_mirror_keys", text="Time Over Zero", icon='TIME').mode = 'TIME_ZERO'
        row4.operator("graph.toolboard_mirror_keys", text="Value Over Zero", icon='EMPTY_SINGLE_ARROW').mode = 'VALUE_ZERO'


class GRAPH_PT_toolboard_snap_clean(bpy.types.Panel):
    """Snap & Clean Subpanel"""
    bl_label = "Snap & Clean"
    bl_idname = "GRAPH_PT_toolboard_snap_clean"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        
        col_snap = layout.column(align=True)
        col_snap.label(text="Snap Keys To:")
        
        row = col_snap.row(align=True)
        row.operator("graph.toolboard_snap_keys", text="Nearest Frame").target = 'FRAME'
        row.operator("graph.toolboard_snap_keys", text="Zero Value").target = 'VALUE_ZERO'
        
        row2 = col_snap.row(align=True)
        row2.operator("graph.toolboard_snap_keys", text="Cursor Time").target = 'CURSOR_X'
        row2.operator("graph.toolboard_snap_keys", text="Cursor Value").target = 'CURSOR_Y'
        
        col_snap.separator()
        col_snap.label(text="Clean Curves:")
        row_clean = col_snap.row(align=True)
        row_clean.prop(props, "clean_threshold", text="Threshold")
        row_clean.operator("graph.toolboard_clean_redundant", text="Clean", icon='TRASH')


class GRAPH_PT_toolboard_copy_paste(bpy.types.Panel):
    """Copy & Paste Keys Subpanel"""
    bl_label = "Copy & Paste Keys"
    bl_idname = "GRAPH_PT_toolboard_copy_paste"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        
        col_cp = layout.column(align=True)
        
        row_btns = col_cp.row(align=True)
        row_btns.scale_y = 1.3
        row_btns.operator("graph.toolboard_copy_keys", text="Copy Keys", icon='COPYDOWN')
        row_btns.operator("graph.toolboard_paste_keys", text="Paste Keys", icon='PASTEDOWN')
        
        col_cp.separator()
        row_opts = col_cp.row(align=True)
        row_opts.prop(props, "paste_mode", text="Mode")
        row_opts.prop(props, "paste_pivot", text="Pivot")
        
        if props.paste_pivot == 'CUSTOM':
            row_custom = col_cp.row(align=True)
            row_custom.prop(props, "paste_custom_frame", text="Frame")


class GRAPH_PT_toolboard_infinity(bpy.types.Panel):
    """Infinity Curves (Loop) Subpanel"""
    bl_label = "Infinity Curves (Loop)"
    bl_idname = "GRAPH_PT_toolboard_infinity"
    bl_parent_id = "GRAPH_PT_toolboard_main"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return bool(context.selected_editable_fcurves)

    def draw(self, context):
        layout = self.layout
        props = context.scene.graph_toolboard
        selected_fcurves = context.selected_editable_fcurves
        
        # Base Extrapolation Settings
        col_ext = layout.column(align=True)
        col_ext.label(text="Base Extrapolation:")
        row_ext = col_ext.row(align=True)
        row_ext.operator("graph.toolboard_toggle_cycles", text="Constant").action = 'CONSTANT'
        row_ext.operator("graph.toolboard_toggle_cycles", text="Linear").action = 'LINEAR'
        
        layout.separator()
        
        has_cycles = False
        if selected_fcurves:
            for mod in selected_fcurves[0].modifiers:
                if mod.type == 'CYCLES':
                    has_cycles = True
                    break
                    
        col_cycle = layout.column(align=True)
        col_cycle.label(text="Infinity Cycles (Loop):")
        col_cycle.prop(props, "loop_mode_before", text="Pre-Infinity")
        col_cycle.prop(props, "loop_mode_after", text="Post-Infinity")
        
        if has_cycles:
            col_cycle.separator()
            row_chk = col_cycle.row(align=True)
            row_chk.prop(props, "loop_active", text="Active Loop")
            row_chk.prop(props, "loop_use_range", text="Limit Range")
            
            if props.loop_use_range:
                row_range = col_cycle.row(align=True)
                row_range.prop(props, "loop_range_start", text="Start")
                row_range.prop(props, "loop_range_end", text="End")
            
            row_cnt = col_cycle.row(align=True)
            row_cnt.prop(props, "loop_cycles_before", text="Pre Cycles")
            row_cnt.prop(props, "loop_cycles_after", text="Post Cycles")

        col_cycle.separator()
        if not has_cycles:
            col_cycle.operator("graph.toolboard_toggle_cycles", text="Make Cyclic Loop", icon='OUTLINER_OB_FORCE_FIELD').action = 'ADD'
        else:
            col_cycle.operator("graph.toolboard_toggle_cycles", text="Remove Cyclic Loop", icon='X').action = 'REMOVE'
            
        # Match loop start/end values section
        layout.separator()
        col_match = layout.column(align=True)
        col_match.label(text="Match Loop Values (Start/End):")
        row_match = col_match.row(align=True)
        row_match.operator("graph.toolboard_match_loop_values", text="Start to End").direction = 'START_TO_END'
        row_match.operator("graph.toolboard_match_loop_values", text="End to Start").direction = 'END_TO_START'
        col_match.operator("graph.toolboard_match_loop_values", text="Average Value").direction = 'AVERAGE'


_classes = (
    GRAPH_PT_toolboard_main,
    GRAPH_PT_toolboard_tween,
    GRAPH_PT_toolboard_interactive,
    GRAPH_PT_toolboard_nudge,
    GRAPH_PT_toolboard_mirror,
    GRAPH_PT_toolboard_snap_clean,
    GRAPH_PT_toolboard_copy_paste,
    GRAPH_PT_toolboard_infinity,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
