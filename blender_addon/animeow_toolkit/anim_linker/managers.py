"""
managers.py — Animeow Toolkit / Anim Linker
=============================================
Đóng gói toàn bộ logic nghiệp vụ (Business Logic) vào các Class chuyên biệt.
Operators sẽ gọi vào các Manager class này để thực hiện công việc,
giúp tách biệt giữa giao diện (UI/Operator) và xử lý (Logic).
"""

import bpy
from mathutils import Matrix


class SmartLocatorManager:
    """Quản lý vòng đời cặp Locator (Hook & Offset) và chuyển đổi Animation.

    Attributes:
        owner: Object hoặc PoseBone đang được chọn (constrained_target).
        armature_obj: Armature object nếu owner là PoseBone, None nếu là Object.
        loc_parent: Empty object đóng vai trò Hook/Anchor.
        loc_child: Empty object đóng vai trò Offset (con của loc_parent).
    """

    def __init__(self, owner, armature_obj=None):
        self.owner = owner
        self.armature_obj = armature_obj
        self.loc_parent = None
        self.loc_child = None

    def detect_existing_animation(self, scene):
        """Kiểm tra xem owner có sẵn Animation (keyframe) hay không.

        Returns:
            bool: True nếu có animation, False nếu không.
        """
        if self.armature_obj:
            if self.armature_obj.animation_data and self.armature_obj.animation_data.action:
                action = self.armature_obj.animation_data.action
                prefix = f'pose.bones["{self.owner.name}"]'
                return any(fc.data_path.startswith(prefix) for fc in action.fcurves)
        else:
            if self.owner.animation_data and self.owner.animation_data.action:
                return True
        return False

    def record_world_animation(self, context, start_frame, end_frame):
        """Ghi hình chuyển động thế giới của owner sang một Empty tạm thời.

        Returns:
            bpy.types.Object: loc_temp chứa keyframe thế giới đã ghi.
        """
        scene = context.scene
        loc_temp = bpy.data.objects.new(f"loc_temp_{self.owner.name}", None)
        loc_temp.empty_display_type = 'PLAIN_AXES'
        loc_temp.empty_display_size = 0.1
        context.scene.collection.objects.link(loc_temp)

        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)
            context.view_layer.update()

            matrix_world = self._get_world_matrix()
            loc_temp.matrix_world = matrix_world
            loc_temp.keyframe_insert(data_path="location", frame=frame)
            if loc_temp.rotation_mode == 'QUATERNION':
                loc_temp.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            else:
                loc_temp.keyframe_insert(data_path="rotation_euler", frame=frame)

        return loc_temp

    def clear_owner_keyframes(self):
        """Xóa toàn bộ keyframe cũ trên owner để giải phóng toạ độ."""
        if self.armature_obj:
            action = self.armature_obj.animation_data.action
            prefix = f'pose.bones["{self.owner.name}"]'
            fcurves_to_remove = [fc for fc in action.fcurves if fc.data_path.startswith(prefix)]
            for fc in fcurves_to_remove:
                action.fcurves.remove(fc)
        else:
            self.owner.animation_data_clear()

    def create_locator_pair(self, context):
        """Tạo cặp Locator Parent (Hook) và Child (Offset) tại vị trí thế giới hiện tại.

        Returns:
            Tuple (loc_parent, loc_child)
        """
        original_matrix = self._get_world_matrix()

        # Tạo Parent (Hook)
        self.loc_parent = bpy.data.objects.new(f"loc_parent_{self.owner.name}", None)
        self.loc_parent.empty_display_type = 'PLAIN_AXES'
        self.loc_parent.empty_display_size = 0.2
        self.loc_parent.matrix_world = original_matrix

        # Tạo Child (Offset)
        self.loc_child = bpy.data.objects.new(f"loc_child_{self.owner.name}", None)
        self.loc_child.empty_display_type = 'PLAIN_AXES'
        self.loc_child.empty_display_size = 0.15
        self.loc_child.matrix_world = original_matrix

        # Link vào Collection
        col = context.scene.collection
        if not self.armature_obj:
            if self.owner.users_collection:
                col = self.owner.users_collection[0]
        col.objects.link(self.loc_parent)
        col.objects.link(self.loc_child)

        # Thiết lập quan hệ cha-con
        self.loc_child.parent = self.loc_parent
        self.loc_child.matrix_parent_inverse = self.loc_parent.matrix_world.inverted()

        return self.loc_parent, self.loc_child

    def apply_constraint_to_target(self, context, target_obj, bone_name=""):
        """Gán constraint Child Of từ loc_parent tới Target (Object hoặc Bone).

        Args:
            context: Blender context.
            target_obj: Đối tượng đích.
            bone_name: Tên xương đích (nếu target_obj là Armature).
        """
        is_armature = (target_obj.type == 'ARMATURE')
        con_name = f"ChildOf_{bone_name}" if is_armature else f"ChildOf_{target_obj.name}"

        existing = self.loc_parent.constraints.get(con_name)
        if existing:
            self.loc_parent.constraints.remove(existing)

        con = self.loc_parent.constraints.new(type='CHILD_OF')
        con.name = con_name
        con.target = target_obj
        if is_armature:
            con.subtarget = bone_name

        context.view_layer.objects.active = self.loc_parent
        bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='OBJECT')

    def apply_constraint_to_owner(self, context, has_animation=False):
        """Gán constraint Child Of từ owner tới loc_child.

        Args:
            context: Blender context.
            has_animation: Nếu True, ép inverse_matrix về Identity thay vì tính toán.
        """
        con_name = f"ChildOf_loc_child_{self.owner.name}"

        existing = self.owner.constraints.get(con_name)
        if existing:
            self.owner.constraints.remove(existing)

        con = self.owner.constraints.new(type='CHILD_OF')
        con.name = con_name
        con.target = self.loc_child

        if has_animation:
            con.inverse_matrix = Matrix.Identity(4)
        else:
            if self.armature_obj:
                context.view_layer.objects.active = self.armature_obj
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='BONE')
            else:
                context.view_layer.objects.active = self.owner
                bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='OBJECT')

    def match_animation_to_child(self, context, loc_temp, start_frame, end_frame):
        """Khớp chuyển động từ loc_temp sang loc_child theo từng frame.

        Args:
            context: Blender context.
            loc_temp: Empty tạm thời chứa keyframe thế giới đã ghi.
            start_frame: Frame bắt đầu.
            end_frame: Frame kết thúc.
        """
        scene = context.scene
        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)
            context.view_layer.update()

            self.loc_child.matrix_world = loc_temp.matrix_world
            self.loc_child.keyframe_insert(data_path="location", frame=frame)
            if self.loc_child.rotation_mode == 'QUATERNION':
                self.loc_child.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            else:
                self.loc_child.keyframe_insert(data_path="rotation_euler", frame=frame)

    def reset_owner_transforms(self):
        """Đưa toạ độ cục bộ của owner về (0, 0, 0)."""
        self.owner.location = (0, 0, 0)
        if hasattr(self.owner, "rotation_euler"):
            self.owner.rotation_euler = (0, 0, 0)
        if hasattr(self.owner, "rotation_quaternion"):
            self.owner.rotation_quaternion = (1, 0, 0, 0)
        self.owner.scale = (1, 1, 1)

    @staticmethod
    def cleanup_temp(loc_temp):
        """Xóa Empty tạm thời khỏi file Blender."""
        if loc_temp:
            bpy.data.objects.remove(loc_temp, do_unlink=True)

    def _get_world_matrix(self):
        """Lấy ma trận thế giới hiện tại của owner."""
        if self.armature_obj:
            return self.armature_obj.matrix_world @ self.owner.matrix
        return self.owner.matrix_world.copy()


class SpaceSwitcher:
    """Quản lý logic chuyển đổi không gian tay cầm (Switch Parent).

    Cho phép đổi Target của constraint Child Of tại một frame cụ thể
    mà không làm lệch vị trí trực quan của vật thể.

    Attributes:
        owner: Object hoặc PoseBone đang được chọn.
        owner_obj: Active object gốc (để trả lại sau khi xong).
        frame: Frame hiện tại trên Timeline.
    """

    def __init__(self, owner, owner_obj, current_frame):
        self.owner = owner
        self.owner_obj = owner_obj
        self.frame = current_frame

    def find_locator_pair(self):
        """Tìm cặp Locator đang liên kết với owner qua constraint.

        Returns:
            Tuple (loc_parent, loc_child) hoặc (None, None).
        """
        child_ofs = [c for c in self.owner.constraints if c.type == 'CHILD_OF']
        for con in child_ofs:
            if con.target and con.target.name.startswith("loc_child_"):
                loc_child = con.target
                if loc_child.parent and loc_child.parent.name.startswith("loc_parent_"):
                    return loc_child.parent, loc_child
        return None, None

    def get_switch_object(self):
        """Xác định đối tượng thực tế nhận Space Switch.

        Returns:
            Object đóng vai trò switch (loc_parent nếu có, ngược lại là owner).
        """
        loc_parent, _ = self.find_locator_pair()
        return loc_parent if loc_parent else self.owner

    def switch_to_target(self, context, switch_obj, new_target_obj, new_bone_name=""):
        """Thực hiện đổi không gian giữ nguyên vị trí trực quan.

        Args:
            context: Blender context.
            switch_obj: Đối tượng nhận switch (loc_parent hoặc owner).
            new_target_obj: Đối tượng Target mới.
            new_bone_name: Tên xương Target mới (nếu là Armature).

        Returns:
            str: Tên của constraint mới được kích hoạt.
        """
        scene = context.scene
        is_armature = (new_target_obj.type == 'ARMATURE')

        # Lưu ma trận thế giới trước khi đổi
        context.view_layer.update()
        original_matrix = switch_obj.matrix_world.copy()

        # Tạo hoặc tìm constraint mới
        con_name = f"ChildOf_{new_bone_name}" if is_armature else f"ChildOf_{new_target_obj.name}"
        target_con = switch_obj.constraints.get(con_name)

        if not target_con:
            target_con = switch_obj.constraints.new(type='CHILD_OF')
            target_con.name = con_name
            target_con.target = new_target_obj
            if is_armature:
                target_con.subtarget = new_bone_name

            if isinstance(switch_obj, bpy.types.PoseBone):
                context.view_layer.objects.active = context.active_object
                bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='BONE')
            else:
                context.view_layer.objects.active = switch_obj
                bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='OBJECT')
            context.view_layer.update()

        # Đặt keyframe cho trạng thái cũ (frame N-1)
        child_ofs = [c for c in switch_obj.constraints if c.type == 'CHILD_OF']
        scene.frame_set(self.frame - 1)
        for con in child_ofs:
            if con.name != con_name:
                con.keyframe_insert(data_path="influence", frame=self.frame - 1)
            else:
                con.influence = 0.0
                con.keyframe_insert(data_path="influence", frame=self.frame - 1)

        # Đảo ngược Influence tại frame hiện tại (frame N)
        scene.frame_set(self.frame)
        for con in [c for c in switch_obj.constraints if c.type == 'CHILD_OF']:
            if con.name == con_name:
                con.influence = 1.0
            else:
                con.influence = 0.0
            con.keyframe_insert(data_path="influence", frame=self.frame)

        # Ép ma trận thế giới trở lại vị trí ban đầu
        context.view_layer.update()
        switch_obj.matrix_world = original_matrix

        # Đặt lại inverse cho constraint mới
        if isinstance(switch_obj, bpy.types.PoseBone):
            context.view_layer.objects.active = context.active_object
            bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='BONE')
        else:
            context.view_layer.objects.active = switch_obj
            bpy.ops.constraint.childof_set_inverse(constraint=target_con.name, owner='OBJECT')

        # Trả lại active object
        context.view_layer.objects.active = self.owner_obj

        return con_name


class AnimationBaker:
    """Quản lý logic Bake chuyển động và dọn dẹp Constraint/Locator.

    Attributes:
        owner: Object hoặc PoseBone cần Bake.
        owner_obj: Active Object gốc.
    """

    def __init__(self, owner, owner_obj):
        self.owner = owner
        self.owner_obj = owner_obj

    def find_locator_names(self):
        """Tìm tên các Locator đang liên kết với owner.

        Returns:
            Tuple (loc_parent_name, loc_child_name) hoặc (None, None).
        """
        child_ofs = [c for c in self.owner.constraints if c.type == 'CHILD_OF']
        for con in child_ofs:
            if con.target and con.target.name.startswith("loc_child_"):
                loc_child_name = con.target.name
                if con.target.parent and con.target.parent.name.startswith("loc_parent_"):
                    return con.target.parent.name, loc_child_name
                return None, loc_child_name
        return None, None

    def bake(self, context, start_frame, end_frame, clear_parents=False, step=1, smart_clean=False, clean_threshold=0.001):
        """Thực hiện Bake Action với Visual Keying.

        Args:
            context: Blender context.
            start_frame: Frame bắt đầu.
            end_frame: Frame kết thúc.
            clear_parents: Có gỡ bỏ liên kết cha-con sau khi bake hay không.
            step: Bước nhảy khi bake (mặc định là 1).
            smart_clean: Tự động tối ưu/lọc keyframe thừa sau khi bake.
            clean_threshold: Độ nhạy để lọc keyframe thừa.
        """
        is_bone = isinstance(self.owner, bpy.types.PoseBone)

        if is_bone:
            armature_obj = context.active_object
            context.view_layer.objects.active = armature_obj
            # Hỗ trợ cả Blender 4.0+ (PoseBone.select) và các bản cũ hơn (Bone.select)
            if hasattr(self.owner, "select"):
                self.owner.select = True
            elif hasattr(self.owner, "bone") and hasattr(self.owner.bone, "select"):
                self.owner.bone.select = True
            bake_type_set = {'POSE'}
        else:
            context.view_layer.objects.active = self.owner
            self.owner.select_set(True)
            bake_type_set = {'OBJECT'}

        # Nếu bật Smart Clean, ta bắt buộc phải Bake mọi frame (step=1) để ghi nhận đầy đủ tất cả cực trị (extremes).
        # Sau đó trong bộ lọc Smart Clean, ta mới tiến hành dọn các keyframe lệch mốc nhảy frame (step) và giữ lại cực trị.
        bake_step = 1 if smart_clean else step

        # Thực hiện Bake NLA gốc của Blender với tham số step tùy chỉnh
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            step=bake_step,
            only_selected=True,
            visual_keying=True,
            clear_constraints=True,
            clear_parents=clear_parents,
            bake_types=bake_type_set
        )

        # Thiết lập mặc định tangent và thực hiện Smart Clean
        action = None
        if is_bone:
            if armature_obj.animation_data and armature_obj.animation_data.action:
                action = armature_obj.animation_data.action
        else:
            if self.owner.animation_data and self.owner.animation_data.action:
                action = self.owner.animation_data.action

        if action:
            from ..core.utils import get_action_fcurves, clean_fcurve_keyframes
            fcurves = get_action_fcurves(action)
            # Chỉ lọc những F-curves thuộc về xương/vật thể hiện tại
            prefix = f'pose.bones["{self.owner.name}"]' if is_bone else ""
            
            for fc in fcurves:
                if not is_bone or fc.data_path.startswith(prefix):
                    # 1. Nếu có Smart Clean -> Thực hiện dọn dẹp lọc bớt key thừa trước
                    if smart_clean:
                        clean_fcurve_keyframes(fc, clean_threshold, step=step, start_frame=start_frame)
                    
                    # 2. Luôn chuyển đổi tangent thành BEZIER và AUTO để đồ thị cong mượt mà tự động
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO'
                        kp.handle_right_type = 'AUTO'
                    
                    fc.update()

        context.view_layer.objects.active = self.owner_obj

    def cleanup_locators(self, loc_parent_name, loc_child_name):
        """Xóa toàn bộ các locator liên quan khỏi file Blender.

        Args:
            loc_parent_name: Tên Empty loc_parent.
            loc_child_name: Tên Empty loc_child.
        """
        names_to_delete = {loc_child_name, loc_parent_name}

        # Quét toàn bộ objects để tìm locator cũ/mới liên quan đến owner
        base_name = self.owner.name
        prefix_parent = f"loc_parent_{base_name}"
        prefix_child = f"loc_child_{base_name}"

        # Lấy tên sạch không có phần đuôi mở rộng .00x
        clean_base_name = base_name.split('.')[0] if '.' in base_name else base_name
        clean_parent = f"loc_parent_{clean_base_name}"
        clean_child = f"loc_child_{clean_base_name}"

        for obj in bpy.data.objects:
            # Khớp tên chính xác hoặc bản sao (.001, .002...)
            if obj.name.startswith(prefix_parent) or obj.name.startswith(prefix_child):
                names_to_delete.add(obj.name)
            elif obj.name.startswith(clean_parent) or obj.name.startswith(clean_child):
                names_to_delete.add(obj.name)

        # Xóa an toàn khỏi cơ sở dữ liệu Blender
        for name in names_to_delete:
            if name and name in bpy.data.objects:
                try:
                    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
                except Exception:
                    pass
