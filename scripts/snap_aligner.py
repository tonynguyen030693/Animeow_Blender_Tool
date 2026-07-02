bl_info = {
    "name": "Snap Similar Parts",
    "author": "Antigravity",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Snap Tool Tab",
    "description": "Align and snap disassembled model parts to their original reference model",
    "category": "Object",
}

import bpy
import mathutils

# ─────────────────────────────────────────────────────────────
# Core Logic Functions
# ─────────────────────────────────────────────────────────────

def get_clean_name(name):
    """Strip Blender suffix like .001, .002 from name."""
    if '.' in name:
        parts = name.split('.')
        if parts[-1].isdigit():
            return '.'.join(parts[:-1])
    return name

def get_geometry_signature(obj):
    """Return a signature tuple: ((verts, edges, polys), (local_bbox_dx, dy, dz))."""
    if obj.type != 'MESH' or not obj.data:
        return None
    mesh = obj.data
    counts = (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))
    
    # Calculate local bounding box dimensions
    if not mesh.vertices:
        bbox = (0.0, 0.0, 0.0)
    else:
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        bbox = (
            round(max(xs) - min(xs), 4),
            round(max(ys) - min(ys), 4),
            round(max(zs) - min(zs), 4)
        )
    return (counts, bbox)

def is_compatible_pair(src, tgt, method):
    """Check if src and tgt are matching parts based on the method."""
    if src.type != 'MESH' or tgt.type != 'MESH':
        return False
        
    if method == 'MESH_DATA':
        return src.data == tgt.data
    elif method == 'MESH_NAME':
        return get_clean_name(src.data.name) == get_clean_name(tgt.data.name)
    elif method == 'GEOMETRY':
        return get_geometry_signature(src) == get_geometry_signature(tgt)
        
    return False

def find_matched_pairs(context, split_axis, match_method):
    """Find pairs using either manual tags (snap_role) or spatial partitioning."""
    scene = context.scene
    all_objs = scene.objects
    
    # Check manual tags
    tagged_targets = [obj for obj in all_objs if obj.get("snap_role") == "TARGET" and obj.type == 'MESH']
    tagged_sources = [obj for obj in all_objs if obj.get("snap_role") == "SOURCE" and obj.type == 'MESH']
    
    if tagged_targets and tagged_sources:
        targets = tagged_targets
        sources = tagged_sources
    else:
        # Fallback to coordinate-based partition
        mesh_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if len(mesh_objs) < 2:
            return [], [], []

        # Find split coordinate along chosen axis
        coords = []
        for obj in mesh_objs:
            if split_axis == 'X':
                coords.append(obj.location.x)
            elif split_axis == 'Y':
                coords.append(obj.location.y)
            else:
                coords.append(obj.location.z)
                
        min_c = min(coords)
        max_c = max(coords)
        mid_c = (min_c + max_c) / 2.0

        targets = []
        sources = []
        
        for obj in mesh_objs:
            val = obj.location.x if split_axis == 'X' else (obj.location.y if split_axis == 'Y' else obj.location.z)
            if val < mid_c:
                targets.append(obj)
            else:
                sources.append(obj)

    if not targets or not sources:
        return [], targets, sources

    # Calculate average offsets for point projection
    avg_src = mathutils.Vector((
        sum(s.location.x for s in sources) / len(sources),
        sum(s.location.y for s in sources) / len(sources),
        sum(s.location.z for s in sources) / len(sources)
    ))
    avg_tgt = mathutils.Vector((
        sum(t.location.x for t in targets) / len(targets),
        sum(t.location.y for t in targets) / len(targets),
        sum(t.location.z for t in targets) / len(targets)
    ))
    offset = avg_src - avg_tgt

    paired = []
    used_targets = set()

    for src in sources:
        compatibles = []
        for tgt in targets:
            if tgt in used_targets:
                continue
            if is_compatible_pair(src, tgt, match_method):
                compatibles.append(tgt)
                
        if compatibles:
            # Project source into target space and find the closest matching target
            proj_loc = src.location - offset
            compatibles.sort(key=lambda t: (t.location - proj_loc).length)
            best_target = compatibles[0]
            
            paired.append((src, best_target))
            used_targets.add(best_target)
            
    return paired, targets, sources

def set_objects_origin(objects, origin_mode, context):
    if origin_mode == 'KEEP' or not objects:
        return
        
    # Save active object and selection state
    original_active = context.view_layer.objects.active
    original_selected = list(context.selected_objects)
    
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select our objects
    for obj in objects:
        obj.select_set(True)
    context.view_layer.objects.active = objects[0]
    
    # Apply origin change
    if origin_mode == 'BOUNDS':
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    elif origin_mode == 'MEDIAN':
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    elif origin_mode == 'VOLUME':
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='VOLUME')
    elif origin_mode == 'SURFACE':
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='SURFACE')
        
    # Restore original selection and active object
    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selected:
        try:
            obj.select_set(True)
        except ReferenceError:
            pass
            
    if original_active:
        try:
            context.view_layer.objects.active = original_active
        except ReferenceError:
            pass

# ─────────────────────────────────────────────────────────────
# Operators
# ─────────────────────────────────────────────────────────────

class OBJECT_OT_snap_similar_parts(bpy.types.Operator):
    """Align and snap disassembled parts back to their original reference positions"""
    bl_idname = "object.snap_similar_parts"
    bl_label = "Align Similar Parts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        split_axis = scene.snap_split_axis
        match_method = scene.snap_match_method
        align_mode = scene.snap_align_mode
        
        # Determine which objects are being processed
        # If manual grouping is used, we process all tagged objects. Otherwise, currently selected.
        all_objs = context.scene.objects
        has_tags = (any(obj.get("snap_role") == "TARGET" for obj in all_objs) and 
                    any(obj.get("snap_role") == "SOURCE" for obj in all_objs))
                    
        if has_tags:
            process_objs = [obj for obj in all_objs if obj.get("snap_role") in ("TARGET", "SOURCE") and obj.type == 'MESH']
        else:
            process_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
            
        if not process_objs:
            self.report({'WARNING'}, "Vui lòng chọn các đối tượng hoặc thiết lập phân nhóm trước!")
            return {'CANCELLED'}

        # Align origins if requested
        set_objects_origin(process_objs, scene.snap_origin_mode, context)

        # Find pairs
        paired, targets, sources = find_matched_pairs(context, split_axis, match_method)
        
        if not paired:
            self.report({'WARNING'}, "Không tìm thấy cặp đối tượng tương thích nào để ghép nối!")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Đã tìm thấy {len(paired)} cặp bộ phận tương thích.")

        # Execute snapping
        if align_mode == 'ABSOLUTE':
            # Absolute snap
            for src, tgt in paired:
                src.matrix_world = tgt.matrix_world.copy()
            self.report({'INFO'}, f"Đã snap {len(paired)} đối tượng trực tiếp về mô hình gốc.")
            
        elif align_mode == 'RELATIVE':
            # Relative snap
            tgt_anchor = None
            src_anchor = None

            if scene.snap_auto_detect_anchor:
                # Find pair with lowest Z
                lowest_z = float('inf')
                best_pair = None
                for src, tgt in paired:
                    if tgt.location.z < lowest_z:
                        lowest_z = tgt.location.z
                        best_pair = (src, tgt)
                if best_pair:
                    src_anchor, tgt_anchor = best_pair
            else:
                tgt_anchor = scene.snap_tgt_anchor
                src_anchor = scene.snap_src_anchor

            if not tgt_anchor or not src_anchor:
                self.report({'ERROR'}, "Thiếu đối tượng điểm neo! Hãy chọn Anchor hoặc bật tự động nhận diện.")
                return {'CANCELLED'}

            self.report({'INFO'}, f"Sử dụng Anchor Gốc: {tgt_anchor.name} -> Anchor Rã: {src_anchor.name}")

            inv_tgt_anchor_matrix = tgt_anchor.matrix_world.inverted()
            src_anchor_matrix = src_anchor.matrix_world

            for src, tgt in paired:
                if src == src_anchor:
                    continue
                relative_matrix = inv_tgt_anchor_matrix @ tgt.matrix_world
                src.matrix_world = src_anchor_matrix @ relative_matrix

            self.report({'INFO'}, f"Đã lắp ráp {len(paired)} đối tượng tại chỗ dựa trên Anchor.")

        # Update viewport
        context.view_layer.update()
        return {'FINISHED'}


class OBJECT_OT_snap_assign_role_target(bpy.types.Operator):
    """Set selected objects as Reference Targets (Intact clock parts)"""
    bl_idname = "object.snap_assign_role_target"
    bl_label = "Set as Targets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            obj["snap_role"] = "TARGET"
            count += 1
        self.report({'INFO'}, f"Đã đặt {count} đối tượng làm nhóm Gốc (Targets).")
        return {'FINISHED'}


class OBJECT_OT_snap_assign_role_source(bpy.types.Operator):
    """Set selected objects as Disassembled Sources (Scattered clock parts)"""
    bl_idname = "object.snap_assign_role_source"
    bl_label = "Set as Sources"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            obj["snap_role"] = "SOURCE"
            count += 1
        self.report({'INFO'}, f"Đã đặt {count} đối tượng làm nhóm Rã (Sources).")
        return {'FINISHED'}


class OBJECT_OT_snap_clear_roles(bpy.types.Operator):
    """Clear all Target/Source groupings in the current scene"""
    bl_idname = "object.snap_clear_roles"
    bl_label = "Clear Groupings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        count = 0
        for obj in context.scene.objects:
            if "snap_role" in obj:
                del obj["snap_role"]
                count += 1
        self.report({'INFO'}, f"Đã xóa phân nhóm của {count} đối tượng.")
        return {'FINISHED'}

# ─────────────────────────────────────────────────────────────
# UI Panel
# ─────────────────────────────────────────────────────────────

class VIEW3D_PT_snap_aligner_panel(bpy.types.Panel):
    """Panel in Sidebar under 'Snap Tool' tab"""
    bl_label = "Snap Similar Parts"
    bl_idname = "VIEW3D_PT_snap_aligner_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Snap Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        all_objs = context.scene.objects
        
        # Manual grouping box
        box_grp = layout.box()
        box_grp.label(text="Phân nhóm thủ công (Bảo đảm 100%):", icon='GROUP')
        
        t_count = sum(1 for obj in all_objs if obj.get("snap_role") == "TARGET")
        s_count = sum(1 for obj in all_objs if obj.get("snap_role") == "SOURCE")
        
        row = box_grp.row(align=True)
        row.operator("object.snap_assign_role_target", text=f"Gốc ({t_count})", icon='ADD')
        row.operator("object.snap_assign_role_source", text=f"Rã ({s_count})", icon='ADD')
        
        if t_count > 0 or s_count > 0:
            box_grp.operator("object.snap_clear_roles", text="Xóa phân nhóm", icon='X')
            
        # Selection info (shows if no manual tags are active)
        if t_count == 0 and s_count == 0:
            selected_count = len(context.selected_objects)
            box_sel = layout.box()
            box_sel.label(text=f"Đang chọn: {selected_count} (Tự chia trục)", icon='OBJECT_DATA')
            
            # Partition settings
            col = layout.column(align=True)
            col.label(text="Trục tự động phân chia:")
            col.prop(scene, "snap_split_axis", expand=True)

        # Pivot origin settings
        layout.separator()
        layout.label(text="Định vị tâm (Pivot):")
        layout.prop(scene, "snap_origin_mode", text="")
        
        # Matching settings
        layout.separator()
        layout.label(text="Phương pháp nhận diện:")
        layout.prop(scene, "snap_match_method", text="")
        
        # Alignment settings
        layout.separator()
        layout.label(text="Chế độ căn chỉnh:")
        layout.prop(scene, "snap_align_mode", text="")
        
        # Anchor settings for relative alignment
        if scene.snap_align_mode == 'RELATIVE':
            box = layout.box()
            box.label(text="Cài đặt điểm neo (Anchor):", icon='CONSTRAINT')
            box.prop(scene, "snap_auto_detect_anchor", text="Tự động nhận diện (Thấp nhất)")
            
            if not scene.snap_auto_detect_anchor:
                box.prop(scene, "snap_tgt_anchor", text="Neo Gốc (Trái)")
                box.prop(scene, "snap_src_anchor", text="Neo Rã (Phải)")

        # Run Button
        layout.separator()
        layout.operator("object.snap_similar_parts", text="Căn chỉnh ngay", icon='SNAP_ON')

# ─────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────

classes = (
    OBJECT_OT_snap_similar_parts,
    OBJECT_OT_snap_assign_role_target,
    OBJECT_OT_snap_assign_role_source,
    OBJECT_OT_snap_clear_roles,
    VIEW3D_PT_snap_aligner_panel,
)

def register():
    # Register properties
    bpy.types.Scene.snap_origin_mode = bpy.props.EnumProperty(
        name="Định vị tâm (Pivot)",
        description="Cách đồng bộ tâm (pivot origin) của các đối tượng trước khi snap",
        items=[
            ('MEDIAN', "Tâm hình học (Median - Khuyên dùng)", "Đặt tâm về trọng tâm hình học của mesh (Origin to Geometry)"),
            ('BOUNDS', "Trọng tâm Bounding Box", "Đặt tâm về giữa hộp bao (Origin to Geometry - Bounds)"),
            ('VOLUME', "Trọng tâm thể tích (Mass)", "Đặt tâm về trọng tâm thể tích (Center of Mass - Volume)"),
            ('SURFACE', "Trọng tâm bề mặt (Surface)", "Đặt tâm về trọng tâm diện tích bề mặt (Center of Mass - Surface)"),
            ('KEEP', "Giữ nguyên tâm hiện tại", "Không thay đổi vị trí tâm")
        ],
        default='MEDIAN'
    )
    
    bpy.types.Scene.snap_split_axis = bpy.props.EnumProperty(
        name="Trục phân chia",
        description="Trục dùng để phân chia mô hình gốc (tọa độ nhỏ) và mô hình bị rã (tọa độ lớn)",
        items=[
            ('X', "Trục X", "Phân chia theo chiều ngang"),
            ('Y', "Trục Y", "Phân chia theo chiều sâu"),
            ('Z', "Trục Z", "Phân chia theo chiều dọc")
        ],
        default='X'
    )
    
    bpy.types.Scene.snap_match_method = bpy.props.EnumProperty(
        name="Nhận diện bằng",
        description="Cách so sánh các bộ phận để ghép đôi",
        items=[
            ('GEOMETRY', "Cấu trúc hình học (Chính xác)", "So sánh cả số lượng đỉnh và kích thước bounding box nội bộ"),
            ('MESH_NAME', "Tên Mesh", "Tên mesh giống nhau (ví dụ: Gear và Gear.001)"),
            ('MESH_DATA', "Mesh Data", "Sử dụng chung dữ liệu mesh (Alt+D)")
        ],
        default='GEOMETRY'
    )
    
    bpy.types.Scene.snap_align_mode = bpy.props.EnumProperty(
        name="Chế độ align",
        description="Cách di chuyển các bộ phận",
        items=[
            ('ABSOLUTE', "Snap trực tiếp", "Snap thẳng về vị trí của mô hình gốc (đè lên nhau)"),
            ('RELATIVE', "Lắp ráp tại chỗ", "Lắp ráp lại ngay tại vị trí hiện tại dựa trên điểm neo")
        ],
        default='ABSOLUTE'
    )
    
    bpy.types.Scene.snap_auto_detect_anchor = bpy.props.BoolProperty(
        name="Tự động tìm điểm neo",
        description="Tự động chọn bộ phận có cao độ Z thấp nhất làm điểm neo (ví dụ: chân đế)",
        default=True
    )
    
    bpy.types.Scene.snap_tgt_anchor = bpy.props.PointerProperty(
        name="Neo Gốc",
        type=bpy.types.Object,
        description="Đối tượng gốc làm mốc ở mô hình nguyên vẹn (trái)"
    )
    
    bpy.types.Scene.snap_src_anchor = bpy.props.PointerProperty(
        name="Neo Rã",
        type=bpy.types.Object,
        description="Đối tượng tương ứng làm mốc ở mô hình bị rã (phải)"
    )

    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    # Delete properties
    del bpy.types.Scene.snap_origin_mode
    del bpy.types.Scene.snap_split_axis
    del bpy.types.Scene.snap_match_method
    del bpy.types.Scene.snap_align_mode
    del bpy.types.Scene.snap_auto_detect_anchor
    del bpy.types.Scene.snap_tgt_anchor
    del bpy.types.Scene.snap_src_anchor

if __name__ == "__main__":
    register()
