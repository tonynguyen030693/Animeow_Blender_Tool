"""
operators.py — Animeow Toolkit / Anim Linker
==============================================
Các Blender Operator cho tính năng liên kết vật thể (Anim Linker).
Operators đóng vai trò điều phối (Controller), gọi vào các Manager class
để thực hiện logic nghiệp vụ.
"""

import bpy
from ..core.utils import get_active_pose_bone, get_constrained_target
from .managers import SmartLocatorManager, SpaceSwitcher, AnimationBaker


class ANIMEOW_OT_quick_link(bpy.types.Operator):
    """Gán nhanh Constraint 'Child Of' từ Object sang Bone hoặc giữa các Bone"""
    bl_idname = "animeow.quick_link"
    bl_label = "Quick Link"
    bl_description = "Gán ràng buộc Child Of cho vật thể đi theo xương được chọn"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # 1. Xác định Target
        target_obj = scene.animeow_target_object
        if not target_obj:
            self.report({'WARNING'}, "Vui lòng chọn Target Object!")
            return {'CANCELLED'}

        is_armature = (target_obj.type == 'ARMATURE')
        target_bone_name = scene.animeow_target_bone if is_armature else ""

        if is_armature and not target_bone_name:
            self.report({'WARNING'}, "Vui lòng chọn Target Bone cho Armature!")
            return {'CANCELLED'}

        if is_armature and target_bone_name not in target_obj.pose.bones:
            self.report({'ERROR'}, f"Xương '{target_bone_name}' không tồn tại trong {target_obj.name}!")
            return {'CANCELLED'}

        # 2. Xác định Owner
        owner_obj = context.active_object
        if not owner_obj:
            self.report({'WARNING'}, "Vui lòng chọn vật thể cần ràng buộc (Owner)!")
            return {'CANCELLED'}

        if owner_obj == target_obj:
            self.report({'WARNING'}, "Không thể tự ràng buộc đối tượng vào chính nó!")
            return {'CANCELLED'}

        constrained_target, armature_obj = get_constrained_target(context)
        use_locator = scene.animeow_use_locator

        if use_locator:
            manager = SmartLocatorManager(constrained_target, armature_obj)
            start_frame = scene.frame_start
            end_frame = scene.frame_end
            original_frame = scene.frame_current

            # Kiểm tra và chuyển đổi animation có sẵn
            has_animation = manager.detect_existing_animation(scene)
            loc_temp = None

            if has_animation:
                loc_temp = manager.record_world_animation(context, start_frame, end_frame)
                manager.clear_owner_keyframes()
                scene.frame_set(original_frame)
                context.view_layer.update()

            # Tạo cặp Locator và gán constraint
            manager.create_locator_pair(context)
            manager.apply_constraint_to_target(context, target_obj, target_bone_name)
            manager.apply_constraint_to_owner(context, has_animation)

            # Match animation nếu có
            if has_animation and loc_temp:
                manager.match_animation_to_child(context, loc_temp, start_frame, end_frame)
                scene.frame_set(original_frame)
                context.view_layer.update()
                SmartLocatorManager.cleanup_temp(loc_temp)
                manager.reset_owner_transforms()
                context.view_layer.update()

            context.view_layer.objects.active = owner_obj
            self.report({'INFO'}, "Đã tạo cặp Locator (Hook & Offset) và đồng bộ chuyển động cũ thành công!")

        else:
            # Gán trực tiếp (không dùng Locator)
            constraint_name = f"ChildOf_{target_bone_name}" if is_armature else f"ChildOf_{target_obj.name}"

            existing = constrained_target.constraints.get(constraint_name)
            if existing:
                constrained_target.constraints.remove(existing)

            con = constrained_target.constraints.new(type='CHILD_OF')
            con.name = constraint_name
            con.target = target_obj
            if is_armature:
                con.subtarget = target_bone_name

            if isinstance(constrained_target, bpy.types.PoseBone):
                context.view_layer.objects.active = context.active_object
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='BONE')
            else:
                context.view_layer.objects.active = constrained_target
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='OBJECT')

            context.view_layer.objects.active = owner_obj
            self.report({'INFO'}, f"Đã liên kết trực tiếp {constrained_target.name} -> {target_bone_name if is_armature else target_obj.name}!")

        return {'FINISHED'}


class ANIMEOW_OT_get_active_bone(bpy.types.Operator):
    """Lấy nhanh thông tin xương hoặc vật thể đang chọn làm Target"""
    bl_idname = "animeow.get_active_bone"
    bl_label = "Lấy đối tượng đang chọn"
    bl_description = "Lấy Bone hoặc Object đang được chọn trong Viewport làm Target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature, bone = get_active_pose_bone(context)
        if armature and bone:
            context.scene.animeow_target_object = armature
            context.scene.animeow_target_bone = bone.name
            self.report({'INFO'}, f"Đã chọn Target: {armature.name} -> {bone.name}")
            return {'FINISHED'}
        else:
            active_obj = context.active_object
            if active_obj:
                context.scene.animeow_target_object = active_obj
                context.scene.animeow_target_bone = ""
                self.report({'INFO'}, f"Đã chọn Target Object: {active_obj.name}")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Hãy chọn một đối tượng hoặc một xương làm Target!")
                return {'CANCELLED'}


class ANIMEOW_OT_switch_parent(bpy.types.Operator):
    """Chuyển đổi không gian / tay cầm mà không thay đổi vị trí trực quan"""
    bl_idname = "animeow.switch_parent"
    bl_label = "Switch Parent"
    bl_description = "Chuyển sang Target mới tại frame hiện tại và giữ nguyên vị trí vật thể"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Hãy chọn vật thể đang có Constraint!")
            return {'CANCELLED'}

        constrained_target, _ = get_constrained_target(context)

        child_ofs = [c for c in constrained_target.constraints if c.type == 'CHILD_OF']
        if not child_ofs:
            self.report({'WARNING'}, f"Vật thể {constrained_target.name} không có constraint 'Child Of' nào!")
            return {'CANCELLED'}

        switcher = SpaceSwitcher(constrained_target, obj, scene.frame_current)
        switch_obj = switcher.get_switch_object()

        child_ofs_switch = [c for c in switch_obj.constraints if c.type == 'CHILD_OF']
        if not child_ofs_switch:
            self.report({'WARNING'}, f"Không tìm thấy constraint 'Child Of' nào trên {switch_obj.name}!")
            return {'CANCELLED'}

        new_target_obj = scene.animeow_target_object
        if not new_target_obj:
            self.report({'WARNING'}, "Hãy chọn đầy đủ Target mới trước khi Switch!")
            return {'CANCELLED'}

        is_armature = (new_target_obj.type == 'ARMATURE')
        new_bone_name = scene.animeow_target_bone if is_armature else ""

        if is_armature and not new_bone_name:
            self.report({'WARNING'}, "Hãy chọn Target Bone cho Armature mới trước khi Switch!")
            return {'CANCELLED'}

        con_name = switcher.switch_to_target(context, switch_obj, new_target_obj, new_bone_name)
        self.report({'INFO'}, f"Đã chuyển sang {new_bone_name if is_armature else new_target_obj.name} tại frame {scene.frame_current}!")
        return {'FINISHED'}


class ANIMEOW_OT_quick_bake(bpy.types.Operator):
    """Bake chuyển động của vật thể và dọn dẹp constraint/locator"""
    bl_idname = "animeow.quick_bake"
    bl_label = "Bake & Clean"
    bl_description = "Bake chuyển động thành Keyframe thực tế và xóa bỏ các Constraint/Locators"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Vui lòng chọn vật thể cần Bake!")
            return {'CANCELLED'}

        constrained_target, _ = get_constrained_target(context)
        baker = AnimationBaker(constrained_target, obj)

        loc_parent_name, loc_child_name = baker.find_locator_names()
        baker.bake(context, scene.frame_start, scene.frame_end, scene.animeow_clear_parents)
        baker.cleanup_locators(loc_parent_name, loc_child_name)

        self.report({'INFO'}, f"Đã bake thành công và dọn dẹp locators cho {constrained_target.name}!")
        return {'FINISHED'}
