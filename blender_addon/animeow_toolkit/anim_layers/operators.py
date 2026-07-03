"""
operators.py — Animeow Toolkit / Anim Layers
================================================
Định nghĩa các Operator cho hệ thống Global Animation Layers.
Mỗi operator gọi phương thức tương ứng của LayerManager.
"""

import bpy
from .layer_manager import LayerManager


# ══════════════════════════════════════════
#  ADD LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_add(bpy.types.Operator):
    """Thêm Animation Layer mới vào danh sách toàn cục"""
    bl_idname = "animeow.layer_add"
    bl_label = "Add Animation Layer"
    bl_description = "Tạo layer animation mới (trống, chưa gán object)"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(
        name="Tên Layer",
        default="New Layer",
        description="Tên hiển thị của layer mới"
    )
    blend_type: bpy.props.EnumProperty(
        name="Blend Mode",
        items=[
            ('ADD', "Additive", "Cộng thêm chuyển động lên các layer bên dưới"),
            ('REPLACE', "Override", "Ghi đè chuyển động của các layer bên dưới"),
            ('COMBINE', "Combine", "Kết hợp thông minh dựa trên loại kênh"),
        ],
        default='ADD'
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "blend_type")

    def execute(self, context):
        scene = context.scene
        layer = LayerManager.add_layer(scene, self.name, self.blend_type)
        if layer:
            new_index = len(scene.animeow_global_layers) - 1
            
            # Tự động thêm các đối tượng đang chọn vào layer mới tạo
            selected_objs = list(context.selected_objects)
            if selected_objs:
                # Lúc này active index vẫn là index của layer cũ, giúp push active action chính xác vào track cũ
                LayerManager.add_objects_to_layer(scene, selected_objs, new_index)

            # Sau khi đã push xong, mới cập nhật index hoạt động sang layer mới tạo
            scene.animeow_global_active_index = new_index

            self.report({'INFO'}, f"Đã tạo layer '{self.name}'")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Không thể tạo layer!")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  SELECT LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_select(bpy.types.Operator):
    """Chuyển sang layer được chọn để diễn hoạt"""
    bl_idname = "animeow.layer_select"
    bl_label = "Select Animation Layer"
    bl_description = "Chuyển sang layer này để chỉnh sửa animation"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        success = LayerManager.select_layer(scene, self.index)
        if success:
            # Force redraw of Graph Editor, NLA Editor, Dope Sheet and 3D Viewport to match slot change
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type in {'GRAPH_EDITOR', 'NLA_EDITOR', 'DOPESHEET_EDITOR', 'VIEW_3D'}:
                        area.tag_redraw()

            layers = scene.animeow_global_layers
            if self.index < len(layers):
                self.report({'INFO'}, f"Đã chuyển sang layer '{layers[self.index].name}'")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Không thể chuyển layer!")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  DELETE LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_delete(bpy.types.Operator):
    """Xóa layer animation đang chọn"""
    bl_idname = "animeow.layer_delete"
    bl_label = "Delete Animation Layer"
    bl_description = "Xóa layer và dữ liệu animation của nó trên tất cả objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return LayerManager.has_layers(context.scene)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index
        layers = scene.animeow_global_layers

        if index < len(layers):
            layer_name = layers[index].name
        else:
            layer_name = "Unknown"

        success = LayerManager.delete_layer(scene, index)
        if success:
            self.report({'INFO'}, f"Đã xóa layer '{layer_name}'")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Không thể xóa layer! (Không được xóa Base layer)")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  MUTE LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_mute(bpy.types.Operator):
    """Bật/tắt hiển thị layer (Mute/Unmute)"""
    bl_idname = "animeow.layer_mute"
    bl_label = "Mute/Unmute Layer"
    bl_description = "Bật/tắt ảnh hưởng của layer lên chuyển động (tất cả objects)"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        layers = scene.animeow_global_layers

        if self.index < 0 or self.index >= len(layers):
            return {'CANCELLED'}

        target = layers[self.index]
        if self.index == scene.animeow_global_active_index:
            self.report({'WARNING'}, "Không thể mute layer đang chỉnh sửa!")
            return {'CANCELLED'}

        new_mute = not target.mute
        success = LayerManager.set_mute(scene, self.index, new_mute)
        if success:
            state = "Muted" if new_mute else "Unmuted"
            self.report({'INFO'}, f"Layer '{target.name}': {state}")
            return {'FINISHED'}
        return {'CANCELLED'}


# ══════════════════════════════════════════
#  SOLO LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_solo(bpy.types.Operator):
    """Solo layer — chỉ hiển thị layer này và tắt tất cả layer khác"""
    bl_idname = "animeow.layer_solo"
    bl_label = "Solo Layer"
    bl_description = "Chỉ hiển thị layer này, tắt tiếng tất cả layer khác (tất cả objects)"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        success = LayerManager.set_solo(scene, self.index)
        if success:
            self.report({'INFO'}, "Đã toggle solo layer")
            return {'FINISHED'}
        return {'CANCELLED'}


# ══════════════════════════════════════════
#  MERGE DOWN
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_merge_down(bpy.types.Operator):
    """Gộp layer hiện tại xuống layer bên dưới"""
    bl_idname = "animeow.layer_merge_down"
    bl_label = "Merge Layer Down"
    bl_description = "Gộp layer đang chọn xuống layer ngay bên dưới (trên tất cả objects)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        layers = scene.animeow_global_layers
        index = scene.animeow_global_active_index
        # Phải có ít nhất 2 layers và không phải layer đáy
        return len(layers) > 1 and index > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index

        success = LayerManager.merge_down(scene, index)
        if success:
            self.report({'INFO'}, "Đã gộp layer xuống layer bên dưới")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Không thể gộp layer!")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  MERGE ALL
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_merge_all(bpy.types.Operator):
    """Gộp tất cả layers thành 1 Action duy nhất"""
    bl_idname = "animeow.layer_merge_all"
    bl_label = "Merge All Layers"
    bl_description = "Gộp toàn bộ layer stack thành 1 animation duy nhất (trên tất cả objects)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return LayerManager.has_layers(context.scene)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene
        smart_clean = scene.animeow_layers_smart_clean
        threshold = scene.animeow_layers_clean_threshold

        success = LayerManager.merge_all(scene, smart_clean, threshold)
        if success:
            self.report({'INFO'}, "Đã gộp tất cả layers thành công!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Không thể gộp layers!")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  MOVE LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_move(bpy.types.Operator):
    """Di chuyển layer lên hoặc xuống trong stack"""
    bl_idname = "animeow.layer_move"
    bl_label = "Move Layer"
    bl_description = "Di chuyển layer lên hoặc xuống để thay đổi thứ tự xếp chồng"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", "Di chuyển lên trên"),
            ('DOWN', "Down", "Di chuyển xuống dưới"),
        ]
    )

    @classmethod
    def poll(cls, context):
        return LayerManager.has_layers(context.scene)

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index

        new_index = LayerManager.move_layer(scene, index, self.direction)
        if new_index >= 0:
            self.report({'INFO'}, f"Đã di chuyển layer {'lên' if self.direction == 'UP' else 'xuống'}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Không thể di chuyển layer!")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  KEYFRAME WEIGHT
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_keyframe_weight(bpy.types.Operator):
    """Chèn keyframe cho weight (influence) của layer tại frame hiện tại"""
    bl_idname = "animeow.layer_keyframe_weight"
    bl_label = "Keyframe Layer Weight"
    bl_description = "Chèn keyframe cho trọng số layer tại frame hiện tại (tất cả objects)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return LayerManager.has_layers(context.scene)

    def execute(self, context):
        scene = context.scene
        frame = scene.frame_current
        index = scene.animeow_global_active_index

        layers = scene.animeow_global_layers
        if index < 0 or index >= len(layers):
            return {'CANCELLED'}

        weight = layers[index].influence
        success = LayerManager.keyframe_weight(scene, index, frame, weight)
        if success:
            self.report({'INFO'}, f"Đã keyframe weight = {weight:.2f} tại frame {frame}")
            return {'FINISHED'}
        return {'CANCELLED'}


# ══════════════════════════════════════════
#  ADD SELECTED OBJECTS TO LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_add_objects(bpy.types.Operator):
    """Thêm các objects đang chọn vào layer hiện tại"""
    bl_idname = "animeow.layer_add_objects"
    bl_label = "Add Selected to Layer"
    bl_description = "Thêm tất cả objects đang được chọn vào layer đang active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not LayerManager.has_layers(context.scene):
            return False
        return len(context.selected_objects) > 0

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index
        objects = list(context.selected_objects)

        count = LayerManager.add_objects_to_layer(scene, objects, index)
        if count > 0:
            layer_name = scene.animeow_global_layers[index].name
            self.report({'INFO'}, f"Đã thêm {count} object(s) vào layer '{layer_name}'")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Không có object nào được thêm (đã có sẵn hoặc lỗi)")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  REMOVE SELECTED OBJECTS FROM LAYER
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_remove_objects(bpy.types.Operator):
    """Gỡ các objects đang chọn khỏi layer hiện tại"""
    bl_idname = "animeow.layer_remove_objects"
    bl_label = "Remove Selected from Layer"
    bl_description = "Gỡ tất cả objects đang được chọn khỏi layer đang active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not LayerManager.has_layers(context.scene):
            return False
        # Không cho gỡ khỏi Base layer
        scene = context.scene
        layers = scene.animeow_global_layers
        index = scene.animeow_global_active_index
        if index < len(layers) and layers[index].is_base:
            return False
        return len(context.selected_objects) > 0

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index
        objects = list(context.selected_objects)

        count = LayerManager.remove_objects_from_layer(scene, objects, index)
        if count > 0:
            layer_name = scene.animeow_global_layers[index].name
            self.report({'INFO'}, f"Đã gỡ {count} object(s) khỏi layer '{layer_name}'")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Không có object nào được gỡ")
            return {'CANCELLED'}


# ══════════════════════════════════════════
#  SELECT MEMBER OBJECTS
# ══════════════════════════════════════════

class ANIMEOW_OT_layer_select_members(bpy.types.Operator):
    """Chọn tất cả objects thuộc layer đang hoạt động"""
    bl_idname = "animeow.layer_select_members"
    bl_label = "Select Layer Objects"
    bl_description = "Chọn tất cả các đối tượng tham gia vào layer này"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not LayerManager.has_layers(scene):
            return False
        index = scene.animeow_global_active_index
        layers = scene.animeow_global_layers
        if index < 0 or index >= len(layers):
            return False
        return True

    def execute(self, context):
        scene = context.scene
        index = scene.animeow_global_active_index
        layers = scene.animeow_global_layers
        layer = layers[index]

        members = LayerManager.get_member_objects(scene, layer.name)
        if not members:
            self.report({'WARNING'}, "Không có đối tượng nào thuộc layer này!")
            return {'CANCELLED'}

        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')

        # Select members
        for obj in members:
            obj.select_set(True)

        # Set active object to the first member
        context.view_layer.objects.active = members[0]

        self.report({'INFO'}, f"Đã chọn {len(members)} đối tượng trong layer '{layer.name}'")
        return {'FINISHED'}

