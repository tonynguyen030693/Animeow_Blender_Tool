# ─────────────────────────────────────────────────────────────
# BonePicker – Animate Mode handler (Modal Operator)
# ─────────────────────────────────────────────────────────────
"""
A modal operator that intercepts mouse events in the picker region,
handles bone selection via button clicks, drag-move in edit mode,
and zoom/pan navigation.
"""
import bpy
from bpy.props import BoolProperty

from .canvas import ViewportMapper, draw_picker_callback
from .utils import (
    get_active_armature,
    get_selected_bone_names,
    hit_test_button,
    select_bones_by_names,
)

def fit_canvas_to_region(picker, tab, region_width, region_height):
    """Compute optimal zoom and pan coordinates to center and frame the canvas."""
    if region_width <= 0 or region_height <= 0:
        return
    w = tab.canvas_width
    h = tab.canvas_height
    if w <= 0 or h <= 0:
        return

    ui_scale = bpy.context.preferences.system.ui_scale
    header_h = 24 * ui_scale
    margin = 15 * ui_scale

    # Available width and height for fitting
    avail_w = region_width - (margin * 2)
    avail_h = region_height - (margin * 2) - header_h

    zoom_x = avail_w / w
    zoom_y = avail_h / h
    zoom = min(zoom_x, zoom_y)

    # Clamp zoom to picker limits [0.1, 5.0]
    zoom = max(0.1, min(5.0, zoom))

    vw = w * zoom
    vh = h * zoom

    pan_x = (region_width - vw) / 2.0
    pan_y = (region_height - (vh + header_h)) / 2.0

    picker.zoom = zoom
    picker.pan_x = pan_x
    picker.pan_y = pan_y



class PICKER_OT_interact(bpy.types.Operator):
    """Interactive picker – click to select bones, middle-drag to pan, scroll to zoom"""
    bl_idname = "picker.interact"
    bl_label = "Picker Interact"
    bl_options = {'REGISTER'}

    _draw_handler = None
    _is_running = False
    _last_region_w = 0
    _last_region_h = 0
    _sidebar_closed = False

    # ── Transient state ─────────────────────────────────────
    _vm = None               # ViewportMapper
    _dragging = False         # edit-mode button drag
    _panning = False          # middle-mouse pan
    _resizing = False         # window resize
    _box_selecting = False    # box selection active
    _box_select_shift = False
    _box_select_active = False
    _box_select_start_mx = 0
    _box_select_start_my = 0
    _box_select_current_mx = 0
    _box_select_current_my = 0
    _drag_btn_idx = -1
    _drag_offset_x = 0.0
    _drag_offset_y = 0.0
    _drag_start_mx = 0
    _drag_start_my = 0
    _drag_last_dx = 0.0
    _drag_last_dy = 0.0
    _pan_last_x = 0
    _pan_last_y = 0
    _resize_start_w = 0.0
    _resize_start_h = 0.0
    _resize_start_pan_y = 0.0
    _resize_start_mx = 0
    _resize_start_my = 0

    @classmethod
    def poll(cls, context):
        return (
            context.area and
            context.area.type == 'VIEW_3D' and
            hasattr(context.scene, 'bone_picker')
        )

    def invoke(self, context, event):
        if PICKER_OT_interact._is_running:
            PICKER_OT_interact._is_running = False
            return {'FINISHED'}

        picker = context.scene.bone_picker

        # Initialize viewport mapper
        PICKER_OT_interact._vm = ViewportMapper()
        PICKER_OT_interact._vm.update_from_props(picker)
        PICKER_OT_interact._last_region_w = 0
        PICKER_OT_interact._last_region_h = 0
        PICKER_OT_interact._sidebar_closed = False

        # Install draw handler, passing target area pointer
        PICKER_OT_interact._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_picker_callback, (context, context.area.as_pointer()), 'WINDOW', 'POST_PIXEL')
        PICKER_OT_interact._is_running = True

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._cleanup(context)

    def _cleanup(self, context):
        if PICKER_OT_interact._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(
                PICKER_OT_interact._draw_handler, 'WINDOW')
            PICKER_OT_interact._draw_handler = None
        PICKER_OT_interact._is_running = False
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        if not PICKER_OT_interact._is_running:
            self._cleanup(context)
            return {'CANCELLED'}

        # Bail if the area was closed
        if context.area is None:
            self._cleanup(context)
            return {'CANCELLED'}

        picker = context.scene.bone_picker
        vm = PICKER_OT_interact._vm
        if vm is None:
            self._cleanup(context)
            return {'CANCELLED'}

        # Sync viewport mapper
        vm.update_from_props(picker)

        if not picker.tabs:
            context.area.tag_redraw()
            return {'PASS_THROUGH'}

        if picker.active_tab_index < 0 or picker.active_tab_index >= len(picker.tabs):
            return {'PASS_THROUGH'}

        tab = picker.tabs[picker.active_tab_index]

        # Check if this is a dedicated float viewport
        is_dedicated = False
        space = context.space_data
        if space and space.type == 'VIEW_3D':
            if not space.overlay.show_overlays and not space.show_region_toolbar and not space.show_region_header:
                is_dedicated = True

        # Force hide sidebar once in dedicated window on startup
        if is_dedicated and not PICKER_OT_interact._sidebar_closed:
            if space.show_region_ui:
                space.show_region_ui = False
            PICKER_OT_interact._sidebar_closed = True

        # Monitor size changes for auto-fitting
        region = context.region
        if region:
            w_changed = (region.width != PICKER_OT_interact._last_region_w)
            h_changed = (region.height != PICKER_OT_interact._last_region_h)
            if w_changed or h_changed:
                if PICKER_OT_interact._last_region_w == 0 or is_dedicated:
                    fit_canvas_to_region(picker, tab, region.width, region.height)
                    vm.update_from_props(picker)
                PICKER_OT_interact._last_region_w = region.width
                PICKER_OT_interact._last_region_h = region.height

        # Check if mouse is in overlay panel regions (Sidebar, Toolbar, Header)
        in_sidebar = False
        in_toolbar = False
        in_header = False
        
        def is_mouse_in_region_bounds(ev, reg):
            if not reg or reg.width <= 1 or reg.height <= 1:
                return False
            return (reg.x <= ev.mouse_x <= reg.x + reg.width) and \
                   (reg.y <= ev.mouse_y <= reg.y + reg.height)

        for r in context.area.regions:
            if r.type == 'UI' and is_mouse_in_region_bounds(event, r):
                in_sidebar = True
            elif r.type == 'TOOLS' and is_mouse_in_region_bounds(event, r):
                in_toolbar = True
            elif r.type == 'HEADER' and is_mouse_in_region_bounds(event, r):
                in_header = True

        # Check if mouse is in the WINDOW region of the View3D area
        window_region = next((r for r in context.area.regions if r.type == 'WINDOW'), None)
        mouse_in_viewport = False
        if window_region:
            if (window_region.x <= event.mouse_x <= window_region.x + window_region.width) and \
               (window_region.y <= event.mouse_y <= window_region.y + window_region.height):
                if not in_sidebar and not in_toolbar and not in_header:
                    mouse_in_viewport = True

        # Check if we are actively dragging/panning/resizing
        is_active_drag = self._dragging or self._panning or self._resizing

        if not mouse_in_viewport and not is_active_drag:
            draw_picker_callback._hovered_index = -1
            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self._dragging = False
                self._panning = False
                self._resizing = False
            return {'PASS_THROUGH'}

        # Get mouse position in region
        mx = event.mouse_region_x
        my = event.mouse_region_y

        # Convert to data coords
        dx, dy = vm.to_data(mx, my)

        # ── Hover detection ─────────────────────────────────
        hovered_idx = -1
        for i, btn in enumerate(tab.buttons):
            if hit_test_button(dx, dy, btn):
                hovered_idx = i
                break  # topmost first (last added)
        # Check from the end for top-most
        for i in range(len(tab.buttons) - 1, -1, -1):
            if hit_test_button(dx, dy, tab.buttons[i]):
                hovered_idx = i
                break

        draw_picker_callback._hovered_index = hovered_idx

        # Check if mouse is inside the canvas background
        ui_scale = bpy.context.preferences.system.ui_scale
        vx, vy = vm.to_viewport(0, 0)
        vw = tab.canvas_width * vm.zoom
        vh = tab.canvas_height * vm.zoom
        
        # 24px header bar on top of the canvas, scaled by UI Scale
        HEADER_HEIGHT = 24 * ui_scale
        RESIZE_HANDLE_SIZE = 14 * ui_scale
        
        on_header = (vx <= mx <= vx + vw) and (vy + vh <= my <= vy + vh + HEADER_HEIGHT)
        on_resize = (vx + vw - RESIZE_HANDLE_SIZE <= mx <= vx + vw) and (vy <= my <= vy + RESIZE_HANDLE_SIZE)
        inside_canvas = (vx <= mx <= vx + vw) and (vy <= my <= vy + vh)
        inside_window = on_header or inside_canvas

        # ── Frame Canvas Hotkey ─────────────────────────────
        if event.type in {'HOME', 'F'} and event.value == 'PRESS':
            if inside_window or mouse_in_viewport:
                fit_canvas_to_region(picker, tab, region.width, region.height)
                vm.update_from_props(picker)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

        # ── Scroll wheel = Zoom ─────────────────────────────
        if event.type == 'WHEELUPMOUSE':
            if inside_window:
                vm.zoom_at(0.15, mx, my)
                vm.store_to_props(picker)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            else:
                return {'PASS_THROUGH'}
        elif event.type == 'WHEELDOWNMOUSE':
            if inside_window:
                vm.zoom_at(-0.15, mx, my)
                vm.store_to_props(picker)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            else:
                return {'PASS_THROUGH'}

        # Disable Middle Mouse Button panning entirely to lock the canvas!
        # Middle mouse events pass through so they can rotate 3D view anywhere!
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        # ── Left click ──────────────────────────────────────
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if on_header:
                # Dragging the entire canvas
                self._panning = True
                self._pan_last_x = mx
                self._pan_last_y = my
                return {'RUNNING_MODAL'}
            
            elif on_resize:
                # Resizing the canvas
                self._resizing = True
                self._resize_start_w = tab.canvas_width
                self._resize_start_h = tab.canvas_height
                self._resize_start_pan_y = picker.pan_y
                self._resize_start_mx = mx
                self._resize_start_my = my
                return {'RUNNING_MODAL'}
            
            elif hovered_idx >= 0:
                if picker.edit_mode:
                    # Edit mode: select button & start drag
                    btn = tab.buttons[hovered_idx]
                    
                    if event.shift:
                        # Toggle selection
                        btn.selected = not btn.selected
                    else:
                        # If not already selected, select only this
                        if not btn.selected:
                            for b in tab.buttons:
                                b.selected = False
                            btn.selected = True
                    
                    tab.active_button_index = hovered_idx
                    self._dragging = True
                    self._drag_btn_idx = hovered_idx
                    self._drag_start_mx = mx
                    self._drag_start_my = my
                    self._drag_last_dx = dx
                    self._drag_last_dy = dy
                    context.area.tag_redraw()
                    return {'RUNNING_MODAL'}
                else:
                    # Animate mode: handle button action based on type
                    btn = tab.buttons[hovered_idx]
                    btn_type = btn.button_type if hasattr(btn, 'button_type') else 'SELECT'
                    arm_name = btn.armature_name or picker.armature_name
                    arm_obj = context.scene.objects.get(arm_name)
                    namespace = getattr(picker, 'namespace', '')

                    if btn_type == 'SELECT':
                        bone_list = btn.get_bone_list()
                        # Apply namespace prefix
                        if namespace:
                            bone_list = [namespace + n for n in bone_list]
                        if arm_obj and bone_list:
                            if event.shift and event.ctrl:
                                mode = 'INVERT'
                            elif event.shift:
                                mode = 'ADD'
                            elif event.ctrl:
                                mode = 'REMOVE'
                            else:
                                mode = 'REPLACE'
                            select_bones_by_names(arm_obj, bone_list, mode=mode)

                    elif btn_type == 'RESET_POSE':
                        bone_list = btn.get_bone_list()
                        if namespace:
                            bone_list = [namespace + n for n in bone_list]
                        if arm_obj and bone_list:
                            # Ensure pose mode
                            if bpy.context.view_layer.objects.active != arm_obj:
                                bpy.context.view_layer.objects.active = arm_obj
                            if arm_obj.mode != 'POSE':
                                bpy.ops.object.mode_set(mode='POSE')
                            for name in bone_list:
                                pb = arm_obj.pose.bones.get(name)
                                if pb:
                                    pb.location = (0, 0, 0)
                                    pb.rotation_quaternion = (1, 0, 0, 0)
                                    pb.rotation_euler = (0, 0, 0)
                                    pb.scale = (1, 1, 1)

                    elif btn_type == 'KEY_ALL':
                        if arm_obj:
                            # Ensure pose mode
                            if bpy.context.view_layer.objects.active != arm_obj:
                                bpy.context.view_layer.objects.active = arm_obj
                            if arm_obj.mode != 'POSE':
                                bpy.ops.object.mode_set(mode='POSE')
                            # Collect all bone names from all buttons in the tab
                            all_bones = set()
                            for b in tab.buttons:
                                for n in b.get_bone_list():
                                    full_name = (namespace + n) if namespace else n
                                    all_bones.add(full_name)
                            for name in all_bones:
                                pb = arm_obj.pose.bones.get(name)
                                if pb:
                                    pb.keyframe_insert(data_path="location", frame=context.scene.frame_current)
                                    pb.keyframe_insert(data_path="rotation_quaternion", frame=context.scene.frame_current)
                                    pb.keyframe_insert(data_path="rotation_euler", frame=context.scene.frame_current)
                                    pb.keyframe_insert(data_path="scale", frame=context.scene.frame_current)

                    elif btn_type == 'RUN_SCRIPT':
                        script = getattr(btn, 'script_text', '')
                        if script:
                            try:
                                exec(script)
                            except Exception as e:
                                print(f"[BonePicker] Script error: {e}")

                    context.area.tag_redraw()
                    return {'RUNNING_MODAL'}
            else:
                if picker.edit_mode:
                    # Start marquee box select inside canvas background
                    if inside_canvas:
                        self._box_selecting = True
                        self._box_select_shift = event.shift
                        self._box_select_start_mx = mx
                        self._box_select_start_my = my
                        self._box_select_current_mx = mx
                        self._box_select_current_my = my
                        
                        PICKER_OT_interact._box_select_active = True
                        PICKER_OT_interact._box_select_start_mx = mx
                        PICKER_OT_interact._box_select_start_my = my
                        PICKER_OT_interact._box_select_current_mx = mx
                        PICKER_OT_interact._box_select_current_my = my
                        context.area.tag_redraw()
                        return {'RUNNING_MODAL'}
                    else:
                        # Clicked outside canvas in Edit Mode
                        for b in tab.buttons:
                            b.selected = False
                        tab.active_button_index = -1
                        context.area.tag_redraw()
                else:
                    # Animate Mode empty space click
                    pass
                
                if inside_canvas:
                    return {'RUNNING_MODAL'}
                else:
                    return {'PASS_THROUGH'}

        # ── Left mouse release ──────────────────────────────
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self._panning:
                self._panning = False
                return {'RUNNING_MODAL'}
            if self._resizing:
                self._resizing = False
                return {'RUNNING_MODAL'}
            if self._dragging:
                # If they didn't move the mouse much (less than 4 pixels in screen space), treat as click-select
                drag_dist_sq = (mx - self._drag_start_mx) ** 2 + (my - self._drag_start_my) ** 2
                if drag_dist_sq < 16.0 and not event.shift:
                    for b in tab.buttons:
                        b.selected = False
                    tab.buttons[self._drag_btn_idx].selected = True
                
                self._dragging = False
                self._drag_btn_idx = -1
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if self._box_selecting:
                self._box_selecting = False
                PICKER_OT_interact._box_select_active = False
                
                # Perform marquee selection check
                x1, y1 = vm.to_data(self._box_select_start_mx, self._box_select_start_my)
                x2, y2 = vm.to_data(self._box_select_current_mx, self._box_select_current_my)
                min_x, max_x = min(x1, x2), max(x1, x2)
                min_y, max_y = min(y1, y2), max(y1, y2)
                
                drag_dist_sq = (mx - self._box_select_start_mx) ** 2 + (my - self._box_select_start_my) ** 2
                if drag_dist_sq < 16.0:
                    # Simple click on background: deselect all if Shift is not held
                    if not self._box_select_shift:
                        for b in tab.buttons:
                            b.selected = False
                        tab.active_button_index = -1
                else:
                    # Box selection drag: select overlapping buttons
                    if not self._box_select_shift:
                        for b in tab.buttons:
                            b.selected = False
                    
                    last_selected_idx = -1
                    for idx_btn, btn in enumerate(tab.buttons):
                        overlap = (btn.pos_x <= max_x) and (btn.pos_x + btn.width >= min_x) and \
                                  (btn.pos_y <= max_y) and (btn.pos_y + btn.height >= min_y)
                        if overlap:
                            btn.selected = True
                            last_selected_idx = idx_btn
                            
                    if last_selected_idx >= 0:
                        tab.active_button_index = last_selected_idx
                
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

        # ── Mouse move (drag) ───────────────────────────────
        if event.type == 'MOUSEMOVE':
            if self._panning:
                delta_x = mx - self._pan_last_x
                delta_y = my - self._pan_last_y
                vm.origin_x += delta_x
                vm.origin_y += delta_y
                vm.store_to_props(picker)
                self._pan_last_x = mx
                self._pan_last_y = my
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
                
            elif self._resizing:
                delta_x = mx - self._resize_start_mx
                delta_y = my - self._resize_start_my
                
                # Width increases as we drag right
                tab.canvas_width = max(150.0, self._resize_start_w + delta_x / vm.zoom)
                
                # Height increases as we drag down (Y decreases)
                delta_h = -delta_y / vm.zoom
                tab.canvas_height = max(150.0, self._resize_start_h + delta_h)
                picker.pan_y = self._resize_start_pan_y + delta_y / vm.zoom
                
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
                
            elif self._dragging and picker.edit_mode:
                # Multi-drag move based on delta change in data coordinates
                current_dx, current_dy = vm.to_data(mx, my)
                delta_dx = current_dx - self._drag_last_dx
                delta_dy = current_dy - self._drag_last_dy
                
                for b in tab.buttons:
                    if b.selected:
                        b.pos_x += delta_dx
                        b.pos_y += delta_dy
                        
                self._drag_last_dx = current_dx
                self._drag_last_dy = current_dy
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
                
            elif self._box_selecting:
                self._box_select_current_mx = mx
                self._box_select_current_my = my
                PICKER_OT_interact._box_select_current_mx = mx
                PICKER_OT_interact._box_select_current_my = my
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            
            context.area.tag_redraw()

        # ── ESC to stop the modal ───────────────────────────
        if event.type == 'ESC' and event.value == 'PRESS':
            self._cleanup(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


# ═════════════════════════════════════════════════════════════
#  Registration
# ═════════════════════════════════════════════════════════════

classes = (
    PICKER_OT_interact,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
