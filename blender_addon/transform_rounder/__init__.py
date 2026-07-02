# ─────────────────────────────────────────────────────────────
# Transform Rounder – Blender Add-on
# ─────────────────────────────────────────────────────────────
# An animation utility to round Location, Rotation (degrees),
# and Scale values of selected Objects or Pose Bones.
# Supports Blender Auto Keying and "Only Insert Available".
# ─────────────────────────────────────────────────────────────

import bpy
import math
from bpy.props import IntProperty, BoolProperty
from mathutils import Euler, Quaternion, Vector

bl_info = {
    "name": "Transform Rounder",
    "author": "Antigravity",
    "version": (1, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Item Tab",
    "description": "Làm tròn các thông số Location, Rotation (độ), và Scale của Object hoặc Bone được chọn",
    "category": "Animation",
}

def insert_auto_keyframe(context, target, data_path, armature_obj=None):
    """Tự động chèn keyframe nếu tính năng Auto Keying đang bật"""
    ts = context.scene.tool_settings
    if not ts.use_keyframe_insert_auto:
        return
        
    anim_target = armature_obj if armature_obj else target
    pref_edit = context.preferences.edit
    
    # Nếu bật chế độ "Only Insert Available" (chỉ chèn vào kênh đã có key)
    if pref_edit.use_keyframe_insert_available:
        if not anim_target.animation_data or not anim_target.animation_data.action:
            return
            
        if armature_obj:
            # Đường dẫn data_path của bone đối với Armature
            full_path = f'pose.bones["{target.name}"].{data_path}'
        else:
            full_path = data_path
            
        # Kiểm tra xem đã có F-Curve nào cho thuộc tính này chưa
        has_fcurve = any(fc.data_path == full_path for fc in anim_target.animation_data.action.fcurves)
        if not has_fcurve:
            return
            
    # Chèn keyframe
    target.keyframe_insert(data_path=data_path)

class VIEW3D_OT_round_transforms(bpy.types.Operator):
    """Làm tròn các thông số transform của Object hoặc Pose Bone được chọn"""
    bl_idname = "view3d.round_transforms"
    bl_label = "Round Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        decimals = scene.round_decimals
        round_loc = scene.round_location
        round_rot = scene.round_rotation
        round_scale = scene.round_scale

        mode = context.mode
        
        # 1. XỬ LÝ TRONG POSE MODE (BONE)
        if mode == 'POSE':
            targets = context.selected_pose_bones
            if not targets and context.active_pose_bone:
                targets = [context.active_pose_bone]
            
            if not targets:
                self.report({'WARNING'}, "Chưa chọn Bone nào!")
                return {'CANCELLED'}
                
            for bone in targets:
                # Làm tròn Location (mét)
                if round_loc:
                    bone.location = [round(v, decimals) for v in bone.location]
                    insert_auto_keyframe(context, bone, "location", armature_obj=bone.id_data)
                
                # Làm tròn Scale
                if round_scale:
                    bone.scale = [round(v, decimals) for v in bone.scale]
                    insert_auto_keyframe(context, bone, "scale", armature_obj=bone.id_data)
                    
                # Làm tròn Rotation (Đổi sang Độ -> Làm tròn -> Đổi lại Radian)
                if round_rot:
                    rot_path = "rotation_euler"
                    if bone.rotation_mode == 'QUATERNION':
                        rot_path = "rotation_quaternion"
                        euler = bone.rotation_quaternion.to_euler()
                        rounded_euler = Euler(
                            [math.radians(round(math.degrees(v), decimals)) for v in euler],
                            euler.order
                        )
                        bone.rotation_quaternion = rounded_euler.to_quaternion()
                    elif bone.rotation_mode == 'AXIS_ANGLE':
                        rot_path = "rotation_axis_angle"
                        angle_deg = math.degrees(bone.rotation_axis_angle[0])
                        rounded_angle = math.radians(round(angle_deg, decimals))
                        rounded_axis = [round(v, decimals) for v in bone.rotation_axis_angle[1:]]
                        bone.rotation_axis_angle = [rounded_angle] + rounded_axis
                    else:  # Euler
                        rot_path = "rotation_euler"
                        euler = bone.rotation_euler
                        rounded_euler = Euler(
                            [math.radians(round(math.degrees(v), decimals)) for v in euler],
                            euler.order
                        )
                        bone.rotation_euler = rounded_euler
                        
                    insert_auto_keyframe(context, bone, rot_path, armature_obj=bone.id_data)
                        
        # 2. XỬ LÝ TRONG OBJECT MODE
        elif mode in {'OBJECT', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL', 'VERTEX_GPENCIL'}:
            targets = context.selected_objects
            if not targets and context.active_object:
                targets = [context.active_object]
                
            if not targets:
                self.report({'WARNING'}, "Chưa chọn Object nào!")
                return {'CANCELLED'}
                
            for obj in targets:
                # Làm tròn Location
                if round_loc:
                    obj.location = [round(v, decimals) for v in obj.location]
                    insert_auto_keyframe(context, obj, "location")
                
                # Làm tròn Scale
                if round_scale:
                    obj.scale = [round(v, decimals) for v in obj.scale]
                    insert_auto_keyframe(context, obj, "scale")
                    
                # Làm tròn Rotation
                if round_rot:
                    rot_path = "rotation_euler"
                    if obj.rotation_mode == 'QUATERNION':
                        rot_path = "rotation_quaternion"
                        euler = obj.rotation_quaternion.to_euler()
                        rounded_euler = Euler(
                            [math.radians(round(math.degrees(v), decimals)) for v in euler],
                            euler.order
                        )
                        obj.rotation_quaternion = rounded_euler.to_quaternion()
                    elif obj.rotation_mode == 'AXIS_ANGLE':
                        rot_path = "rotation_axis_angle"
                        angle_deg = math.degrees(obj.rotation_axis_angle[0])
                        rounded_angle = math.radians(round(angle_deg, decimals))
                        rounded_axis = [round(v, decimals) for v in obj.rotation_axis_angle[1:]]
                        obj.rotation_axis_angle = [rounded_angle] + rounded_axis
                    else:  # Euler
                        rot_path = "rotation_euler"
                        euler = obj.rotation_euler
                        rounded_euler = Euler(
                            [math.radians(round(math.degrees(v), decimals)) for v in euler],
                            euler.order
                        )
                        obj.rotation_euler = rounded_euler
                        
                    insert_auto_keyframe(context, obj, rot_path)
        else:
            self.report({'WARNING'}, "Hãy chuyển sang Object Mode hoặc Pose Mode")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Đã làm tròn thông số về {decimals} chữ số thập phân.")
        return {'FINISHED'}

class VIEW3D_PT_transform_rounder(bpy.types.Panel):
    """Tạo bảng điều khiển trong N-Panel (Tab Item)"""
    bl_label = "Transform Rounder"
    bl_idname = "VIEW3D_PT_transform_rounder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'  # Nằm chung Tab "Item" với bảng Transform mặc định

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.prop(scene, "round_decimals", text="Chữ số thập phân")
        
        col.separator()
        col.label(text="Mục tiêu làm tròn:")
        row = col.row(align=True)
        row.prop(scene, "round_location", text="Loc", toggle=True)
        row.prop(scene, "round_rotation", text="Rot", toggle=True)
        row.prop(scene, "round_scale", text="Scale", toggle=True)

        col.separator()
        col.operator("view3d.round_transforms", text="Làm tròn đối tượng chọn", icon='FILE_REFRESH')

classes = (
    VIEW3D_OT_round_transforms,
    VIEW3D_PT_transform_rounder,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.round_decimals = IntProperty(
        name="Decimals",
        description="Số chữ số sau dấu phẩy",
        default=2,
        min=0,
        max=6
    )
    bpy.types.Scene.round_location = BoolProperty(
        name="Location",
        default=True
    )
    bpy.types.Scene.round_rotation = BoolProperty(
        name="Rotation",
        default=True
    )
    bpy.types.Scene.round_scale = BoolProperty(
        name="Scale",
        default=True
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.round_decimals
    del bpy.types.Scene.round_location
    del bpy.types.Scene.round_rotation
    del bpy.types.Scene.round_scale

if __name__ == "__main__":
    register()
