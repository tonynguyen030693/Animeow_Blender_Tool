"""
operators.py - Animeow Anim Linker
==================================
Chứa toàn bộ logic xử lý (Operators) cho việc tạo Constraint,
chuyển đổi không gian (Space/Parent Switching) và Bake Keyframes.
"""

import bpy
from mathutils import Matrix

def get_active_pose_bone(context):
    """Lấy xương đang được chọn hoạt động trong Pose Mode."""
    if context.active_object and context.active_object.type == 'ARMATURE':
        if context.active_pose_bone:
            return context.active_object, context.active_pose_bone
    return None, None

class ANIMEOW_OT_quick_link(bpy.types.Operator):
    """Gán nhanh Constraint 'Child Of' từ Object sang Bone hoặc giữa các Bone"""
    bl_idname = "animeow.quick_link"
    bl_label = "Quick Link"
    bl_description = "Gán ràng buộc Child Of cho vật thể đi theo xương được chọn"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        
        # 1. Xác định Target (Object và Bone)
        target_obj = scene.animeow_target_object
        
        if not target_obj:
            self.report({'WARNING'}, "Vui lòng chọn Target Object!")
            return {'CANCELLED'}
            
        is_armature = (target_obj.type == 'ARMATURE')
        target_bone_name = scene.animeow_target_bone if is_armature else ""
        
        if is_armature and not target_bone_name:
            self.report({'WARNING'}, "Vui lòng chọn Target Bone cho Armature!")
            return {'CANCELLED'}
        
        # Kiểm tra xem bone có tồn tại không
        if is_armature and target_bone_name not in target_obj.pose.bones:
            self.report({'ERROR'}, f"Xương '{target_bone_name}' không tồn tại trong {target_obj.name}!")
            return {'CANCELLED'}

        # 2. Xác định Owner (Vật thể hoặc Xương đang được chọn)
        owner_obj = context.active_object
        if not owner_obj:
            self.report({'WARNING'}, "Vui lòng chọn vật thể cần ràng buộc (Owner)!")
            return {'CANCELLED'}
            
        if owner_obj == target_obj:
            self.report({'WARNING'}, "Không thể tự ràng buộc đối tượng vào chính nó!")
            return {'CANCELLED'}
            
        # Xác định đối tượng thực tế nhận constraint từ locator
        # (Có thể là Active Pose Bone nếu đang ở Pose Mode, ngược lại là Active Object)
        constrained_target = None
        if context.active_object and context.active_object.type == 'ARMATURE' and context.active_pose_bone:
            constrained_target = context.active_pose_bone
            armature_obj = context.active_object
        else:
            constrained_target = owner_obj
            armature_obj = None
            
        use_locator = scene.animeow_use_locator
        
        if use_locator:
            # 1. Kiểm tra xem constrained_target có sẵn Animation hay không
            has_animation = False
            start_frame = scene.frame_start
            end_frame = scene.frame_end
            
            if armature_obj:
                if armature_obj.animation_data and armature_obj.animation_data.action:
                    action = armature_obj.animation_data.action
                    data_path_prefix = f'pose.bones["{constrained_target.name}"]'
                    has_animation = any(fc.data_path.startswith(data_path_prefix) for fc in action.fcurves)
            else:
                if constrained_target.animation_data and constrained_target.animation_data.action:
                    has_animation = True
            
            # Ghi lại frame hiện tại để khôi phục sau này
            original_frame = scene.frame_current
            
            # Nếu có chuyển động sẵn, tạo Locator tạm thời để ghi hình thế giới trước
            loc_temp = None
            if has_animation:
                loc_temp = bpy.data.objects.new(f"loc_temp_{constrained_target.name}", None)
                loc_temp.empty_display_type = 'PLAIN_AXES'
                loc_temp.empty_display_size = 0.1
                context.scene.collection.objects.link(loc_temp)
                
                # Ghi hình chuyển động sang loc_temp dưới dạng keyframe thế giới
                for frame in range(start_frame, end_frame + 1):
                    scene.frame_set(frame)
                    context.view_layer.update()
                    
                    if armature_obj:
                        matrix_world_curr = armature_obj.matrix_world @ constrained_target.matrix
                    else:
                        matrix_world_curr = constrained_target.matrix_world.copy()
                        
                    loc_temp.matrix_world = matrix_world_curr
                    loc_temp.keyframe_insert(data_path="location", frame=frame)
                    if loc_temp.rotation_mode == 'QUATERNION':
                        loc_temp.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                    else:
                        loc_temp.keyframe_insert(data_path="rotation_euler", frame=frame)
                
                # Xóa toàn bộ keyframe cũ trên constrained_target để giải phóng toạ độ
                if armature_obj:
                    action = armature_obj.animation_data.action
                    data_path_prefix = f'pose.bones["{constrained_target.name}"]'
                    fcurves_to_remove = [fc for fc in action.fcurves if fc.data_path.startswith(data_path_prefix)]
                    for fc in fcurves_to_remove:
                        action.fcurves.remove(fc)
                else:
                    constrained_target.animation_data_clear()
                    
                # Trả hệ thống về frame gốc
                scene.frame_set(original_frame)
                context.view_layer.update()

            # Lấy vị trí thế giới hiện tại của constrained_target (sau khi đã xóa anim hoặc nếu không có anim)
            if armature_obj:
                original_matrix = armature_obj.matrix_world @ constrained_target.matrix
            else:
                original_matrix = constrained_target.matrix_world.copy()
            
            # 2. Tạo Locator Parent (Hook)
            loc_parent = bpy.data.objects.new(f"loc_parent_{constrained_target.name}", None)
            loc_parent.empty_display_type = 'PLAIN_AXES'
            loc_parent.empty_display_size = 0.2
            loc_parent.matrix_world = original_matrix
            
            # 3. Tạo Locator Child (Offset)
            loc_child = bpy.data.objects.new(f"loc_child_{constrained_target.name}", None)
            loc_child.empty_display_type = 'PLAIN_AXES'
            loc_child.empty_display_size = 0.15
            loc_child.matrix_world = original_matrix
            
            # Đưa cả 2 Empty vào Collection của Object hoặc Scene Collection
            col = context.scene.collection
            if not armature_obj:
                if constrained_target.users_collection:
                    col = constrained_target.users_collection[0]
            col.objects.link(loc_parent)
            col.objects.link(loc_child)
            
            # 4. Làm cha của loc_child -> loc_parent
            loc_child.parent = loc_parent
            loc_child.matrix_parent_inverse = loc_parent.matrix_world.inverted()
            
            # 5. Gán constraint Child Of từ loc_parent -> Target (Object hoặc Bone)
            constraint_name = f"ChildOf_{target_bone_name}" if is_armature else f"ChildOf_{target_obj.name}"
            
            # Xóa trùng tên nếu có
            existing = loc_parent.constraints.get(constraint_name)
            if existing:
                loc_parent.constraints.remove(existing)
                
            con_parent = loc_parent.constraints.new(type='CHILD_OF')
            con_parent.name = constraint_name
            con_parent.target = target_obj
            if is_armature:
                con_parent.subtarget = target_bone_name
                
            # Set inverse cho loc_parent
            context.view_layer.objects.active = loc_parent
            bpy.ops.constraint.childof_set_inverse(constraint=con_parent.name, owner='OBJECT')
            
            # 6. Gán constraint Child Of từ constrained_target -> loc_child
            con_owner_name = f"ChildOf_loc_child_{constrained_target.name}"
            
            existing_owner = constrained_target.constraints.get(con_owner_name)
            if existing_owner:
                constrained_target.constraints.remove(existing_owner)
                
            con_owner = constrained_target.constraints.new(type='CHILD_OF')
            con_owner.name = con_owner_name
            con_owner.target = loc_child
            
            # Set inverse cho constrained_target
            if has_animation:
                con_owner.inverse_matrix = Matrix.Identity(4)
            else:
                if armature_obj:
                    context.view_layer.objects.active = armature_obj
                    bpy.ops.constraint.childof_set_inverse(constraint=con_owner.name, owner='BONE')
                else:
                    context.view_layer.objects.active = constrained_target
                    bpy.ops.constraint.childof_set_inverse(constraint=con_owner.name, owner='OBJECT')
                
            # 7. Match chuyển động từ loc_temp sang loc_child
            if has_animation and loc_temp:
                for frame in range(start_frame, end_frame + 1):
                    scene.frame_set(frame)
                    context.view_layer.update()
                    
                    # Cập nhật vị trí thế giới của loc_child bằng loc_temp
                    loc_child.matrix_world = loc_temp.matrix_world
                    
                    # Insert keyframe cho loc_child
                    loc_child.keyframe_insert(data_path="location", frame=frame)
                    if loc_child.rotation_mode == 'QUATERNION':
                        loc_child.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                    else:
                        loc_child.keyframe_insert(data_path="rotation_euler", frame=frame)
                
                # Trả về frame gốc và dọn dẹp loc_temp
                scene.frame_set(original_frame)
                context.view_layer.update()
                bpy.data.objects.remove(loc_temp, do_unlink=True)
                
                # Đưa toạ độ cục bộ của constrained_target về 0-0-0
                constrained_target.location = (0, 0, 0)
                if hasattr(constrained_target, "rotation_euler"):
                    constrained_target.rotation_euler = (0, 0, 0)
                if hasattr(constrained_target, "rotation_quaternion"):
                    constrained_target.rotation_quaternion = (1, 0, 0, 0)
                constrained_target.scale = (1, 1, 1)
                context.view_layer.update()
                
            # Trả lại active object ban đầu
            context.view_layer.objects.active = owner_obj
            
            self.report({'INFO'}, f"Đã tạo cặp Locator (Hook & Offset) và đồng bộ chuyển động cũ thành công!")
        else:
            # Gán trực tiếp lên constrained_target
            constraint_name = f"ChildOf_{target_bone_name}" if is_armature else f"ChildOf_{target_obj.name}"
            
            existing = constrained_target.constraints.get(constraint_name)
            if existing:
                constrained_target.constraints.remove(existing)
                
            con = constrained_target.constraints.new(type='CHILD_OF')
            con.name = constraint_name
            con.target = target_obj
            if is_armature:
                con.subtarget = target_bone_name
                
            # Set inverse
            if isinstance(constrained_target, bpy.types.PoseBone):
                context.view_layer.objects.active = context.active_object
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='BONE')
            else:
                context.view_layer.objects.active = constrained_target
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='OBJECT')
                
            # Trả lại active object ban đầu
            context.view_layer.objects.active = owner_obj
            
            self.report({'INFO'}, f"Đã liên kết trực tiếp {constrained_target.name} -> {target_bone_name if is_armature else target_obj.name} thành công!")
            
        return {'FINISHED'}

class ANIMEOW_OT_get_active_bone(bpy.types.Operator):
    """Lấy nhanh thông tin xương hoặc vật thể đang chọn làm Target"""
    bl_idname = "animeow.get_active_bone"
    bl_label = "Lấy đối tượng đang chọn"
    bl_description = "Lấy Bone hoặc Object đang được chọn trong Viewport làm Target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Thử lấy xương trong Pose Mode trước
        armature, bone = get_active_pose_bone(context)
        if armature and bone:
            context.scene.animeow_target_object = armature
            context.scene.animeow_target_bone = bone.name
            self.report({'INFO'}, f"Đã chọn Target: {armature.name} -> {bone.name}")
            return {'FINISHED'}
        else:
            # Nếu không ở Pose Mode, lấy Active Object thông thường
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
        current_frame = scene.frame_current
        
        # Xác định đối tượng đang được chọn
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Hãy chọn vật thể đang có Constraint!")
            return {'CANCELLED'}
            
        # Xác định đối tượng thực tế nhận điều khiển
        constrained_target = None
        if context.active_object and context.active_object.type == 'ARMATURE' and context.active_pose_bone:
            constrained_target = context.active_pose_bone
        else:
            constrained_target = obj
            
        # Tìm xem có dùng cặp locator hay không bằng cách quét constraint của constrained_target
        child_ofs_owner = [c for c in constrained_target.constraints if c.type == 'CHILD_OF']
        if not child_ofs_owner:
            self.report({'WARNING'}, f"Vật thể {constrained_target.name} không có constraint 'Child Of' nào!")
            return {'CANCELLED'}
            
        loc_parent_obj = None
        loc_child_obj = None
        
        for con in child_ofs_owner:
            if con.target and con.target.name.startswith("loc_child_"):
                loc_child_obj = con.target
                if loc_child_obj.parent and loc_child_obj.parent.name.startswith("loc_parent_"):
                    loc_parent_obj = loc_child_obj.parent
                    break
                    
        # Nếu có cặp locator, đối tượng nhận Space Switch thực sự sẽ là loc_parent_obj!
        # Ngược lại, đối tượng nhận Space Switch chính là constrained_target!
        switch_obj = loc_parent_obj if loc_parent_obj else constrained_target
        
        child_ofs = [c for c in switch_obj.constraints if c.type == 'CHILD_OF']
        if not child_ofs:
            self.report({'WARNING'}, f"Không tìm thấy constraint 'Child Of' nào trên {switch_obj.name}!")
            return {'CANCELLED'}
            
        # Target mới
        new_target_obj = scene.animeow_target_object
        
        if not new_target_obj:
            self.report({'WARNING'}, "Hãy chọn đầy đủ Target mới trước khi Switch!")
            return {'CANCELLED'}
            
        is_armature = (new_target_obj.type == 'ARMATURE')
        new_bone_name = scene.animeow_target_bone if is_armature else ""
        
        if is_armature and not new_bone_name:
            self.report({'WARNING'}, "Hãy chọn Target Bone cho Armature mới trước khi Switch!")
            return {'CANCELLED'}
            
        # 1. Lưu giữ ma trận vị trí thế giới hiện tại (trước khi đổi)
        context.view_layer.update()
        original_matrix = switch_obj.matrix_world.copy()
        
        # 2. Tạo hoặc kích hoạt constraint mới trên switch_obj
        target_con_name = f"ChildOf_{new_bone_name}" if is_armature else f"ChildOf_{new_target_obj.name}"
        target_con = switch_obj.constraints.get(target_con_name)
        
        if not target_con:
            # Tạo mới nếu chưa có
            target_con = switch_obj.constraints.new(type='CHILD_OF')
            target_con.name = target_con_name
            target_con.target = new_target_obj
            if is_armature:
                target_con.subtarget = new_bone_name
            # Set inverse tạm thời
            if isinstance(switch_obj, bpy.types.PoseBone):
                context.view_layer.objects.active = context.active_object
                bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='BONE')
            else:
                context.view_layer.objects.active = switch_obj
                bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='OBJECT')
            context.view_layer.update()

        # 3. Đặt Keyframe cho trạng thái cũ ở frame trước đó (N-1)
        scene.frame_set(current_frame - 1)
        for con in child_ofs:
            # Nếu là con cũ thì giữ 1.0, con khác giữ 0.0
            if con.name != target_con_name:
                con.keyframe_insert(data_path="influence", frame=current_frame - 1)
            else:
                con.influence = 0.0
                con.keyframe_insert(data_path="influence", frame=current_frame - 1)
                
        # 4. Trở lại frame hiện tại (N), đảo ngược Influence
        scene.frame_set(current_frame)
        for con in [c for c in switch_obj.constraints if c.type == 'CHILD_OF']:
            if con.name == target_con_name:
                con.influence = 1.0
            else:
                con.influence = 0.0
            con.keyframe_insert(data_path="influence", frame=current_frame)
            
        # 5. Cập nhật hệ thống và ép ma trận thế giới trở lại đúng vị trí ban đầu
        context.view_layer.update()
        switch_obj.matrix_world = original_matrix
        
        # Đặt lại inverse matrix cho constraint mới để khớp vị trí thế giới
        if isinstance(switch_obj, bpy.types.PoseBone):
            context.view_layer.objects.active = context.active_object
            bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='BONE')
        else:
            context.view_layer.objects.active = switch_obj
            bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='OBJECT')
            
        # Trả lại active object ban đầu
        context.view_layer.objects.active = obj
        
        self.report({'INFO'}, f"Đã chuyển sang {new_bone_name if is_armature else new_target_obj.name} tại frame {current_frame}!")
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
            
        # Xác định đối tượng thực tế cần Bake (Object hoặc Pose Bone)
        constrained_target = None
        if context.active_object and context.active_object.type == 'ARMATURE' and context.active_pose_bone:
            constrained_target = context.active_pose_bone
        else:
            constrained_target = obj
            
        # Tìm các locators liên quan trước khi bake
        loc_parent_name = None
        loc_child_name = None
        
        child_ofs = [c for c in constrained_target.constraints if c.type == 'CHILD_OF']
        for con in child_ofs:
            if con.target and con.target.name.startswith("loc_child_"):
                loc_child_name = con.target.name
                if con.target.parent and con.target.parent.name.startswith("loc_parent_"):
                    loc_parent_name = con.target.parent.name
                break
                
        # Xác định khoảng frame từ timeline
        start_frame = scene.frame_start
        end_frame = scene.frame_end
        
        is_bone = isinstance(constrained_target, bpy.types.PoseBone)
        
        # Thiết lập đối tượng được chọn hoạt động trước khi bake
        if is_bone:
            armature_obj = context.active_object
            context.view_layer.objects.active = armature_obj
            constrained_target.bone.select = True
            bake_type_set = {'POSE'}
        else:
            context.view_layer.objects.active = constrained_target
            constrained_target.select_set(True)
            bake_type_set = {'OBJECT'}
            
        # Chạy Bake Action của Blender với các tham số tối ưu cho animator
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints=True,
            clear_parents=scene.animeow_clear_parents,
            bake_types=bake_type_set
        )
        
        # Trả lại active object ban đầu
        context.view_layer.objects.active = obj
        
        # Xóa các locators nếu có
        for name in [loc_child_name, loc_parent_name]:
            if name and name in bpy.data.objects:
                obj_to_del = bpy.data.objects[name]
                bpy.data.objects.remove(obj_to_del, do_unlink=True)
                
        self.report({'INFO'}, f"Đã bake thành công và dọn dẹp locators cho {constrained_target.name}!")
        return {'FINISHED'}
