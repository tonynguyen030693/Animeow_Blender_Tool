import bpy

bl_info = {
    "name": "Rigify Simple Picker",
    "author": "Antigravity",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Rig Picker",
    "description": "Bảng chọn nhanh các xương điều khiển của Rigify",
    "category": "Animation",
}

class RIG_PICKER_OT_select_bone(bpy.types.Operator):
    bl_idname = "rig_picker.select_bone"
    bl_label = "Select Bone"
    bl_options = {'UNDO'}
    
    bone_name: bpy.props.StringProperty()
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Vui lòng chọn bộ xương (Rig) trước!")
            return {'CANCELLED'}
        
        # Đảm bảo đang ở chế độ Pose Mode
        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
            
        pose_bones = obj.pose.bones
        if self.bone_name not in pose_bones:
            self.report({'WARNING'}, f"Không tìm thấy xương '{self.bone_name}' trong rig này!")
            return {'CANCELLED'}
            
        bone = pose_bones[self.bone_name]
        
        # Bỏ chọn toàn bộ xương khác và chọn xương này
        for pb in pose_bones:
            pb.select = False
            
        bone.select = True
        obj.data.bones.active = bone.bone
        
        return {'FINISHED'}

class RIG_PICKER_OT_select_all(bpy.types.Operator):
    bl_idname = "rig_picker.select_all"
    bl_label = "Select All Controls"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            return {'CANCELLED'}
        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
            
        for pb in obj.pose.bones:
            # Chỉ chọn xương điều khiển chính (bỏ qua xương kỹ thuật MCH, DEF, ORG)
            if not any(prefix in pb.name for prefix in ["MCH-", "DEF-", "ORG-"]):
                pb.select = True
        return {'FINISHED'}

class RIG_PICKER_OT_clear_selection(bpy.types.Operator):
    bl_idname = "rig_picker.clear_selection"
    bl_label = "Clear Selection"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            return {'CANCELLED'}
        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
            
        for pb in obj.pose.bones:
            pb.select = False
        return {'FINISHED'}

class VIEW3D_PT_rigify_picker(bpy.types.Panel):
    bl_label = "Rigify Picker"
    bl_idname = "VIEW3D_PT_rigify_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig Picker'
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if not obj or obj.type != 'ARMATURE':
            layout.label(text="Hãy chọn bộ xương (Rig)", icon='INFO')
            return
            
        # Nút chọn nhanh/Xóa chọn
        row = layout.row(align=True)
        row.operator("rig_picker.select_all", text="Chọn tất cả")
        row.operator("rig_picker.clear_selection", text="Bỏ chọn")
        
        layout.separator()
        
        # PHẦN THÂN GIỮA (Đầu & Cột sống)
        box = layout.box()
        box.label(text="Đầu & Thân (Center)", icon='USER')
        col = box.column(align=True)
        col.operator("rig_picker.select_bone", text="Đầu (Head)").bone_name = "head"
        col.operator("rig_picker.select_bone", text="Cổ (Neck)").bone_name = "neck"
        col.operator("rig_picker.select_bone", text="Ngực (Chest)").bone_name = "chest"
        col.operator("rig_picker.select_bone", text="Bụng (Spine)").bone_name = "spine"
        col.operator("rig_picker.select_bone", text="Hông (Hips)").bone_name = "hips"
        col.operator("rig_picker.select_bone", text="Trọng tâm (Torso)").bone_name = "torso"
        
        # TAY (Trái & Phải)
        box = layout.box()
        box.label(text="Hai Cánh Tay (Arms)", icon='ARMATURE_DATA')
        split = box.split(factor=0.5)
        
        # Tay Trái (.L)
        col_l = split.column(align=True)
        col_l.label(text="Bên Trái (L)")
        col_l.operator("rig_picker.select_bone", text="Vai L").bone_name = "shoulder.L"
        col_l.operator("rig_picker.select_bone", text="Cổ tay IK L").bone_name = "hand_ik.L"
        col_l.operator("rig_picker.select_bone", text="Bắp tay FK L").bone_name = "upper_arm_fk.L"
        col_l.operator("rig_picker.select_bone", text="Cẳng tay FK L").bone_name = "forearm_fk.L"
        col_l.operator("rig_picker.select_bone", text="Bàn tay FK L").bone_name = "hand_fk.L"
        
        # Tay Phải (.R)
        col_r = split.column(align=True)
        col_r.label(text="Bên Phải (R)")
        col_r.operator("rig_picker.select_bone", text="Vai R").bone_name = "shoulder.R"
        col_r.operator("rig_picker.select_bone", text="Cổ tay IK R").bone_name = "hand_ik.R"
        col_r.operator("rig_picker.select_bone", text="Bắp tay FK R").bone_name = "upper_arm_fk.R"
        col_r.operator("rig_picker.select_bone", text="Cẳng tay FK R").bone_name = "forearm_fk.R"
        col_r.operator("rig_picker.select_bone", text="Bàn tay FK R").bone_name = "hand_fk.R"
        
        # CHÂN (Trái & Phải)
        box = layout.box()
        box.label(text="Hai Chân (Legs)", icon='MOD_ARMATURE')
        split = box.split(factor=0.5)
        
        # Chân Trái (.L)
        col_l = split.column(align=True)
        col_l.label(text="Bên Trái (L)")
        col_l.operator("rig_picker.select_bone", text="Cổ chân IK L").bone_name = "foot_ik.L"
        col_l.operator("rig_picker.select_bone", text="Đùi FK L").bone_name = "thigh_fk.L"
        col_l.operator("rig_picker.select_bone", text="Cẳng chân FK L").bone_name = "shin_fk.L"
        col_l.operator("rig_picker.select_bone", text="Bàn chân FK L").bone_name = "foot_fk.L"
        
        # Chân Phải (.R)
        col_r = split.column(align=True)
        col_r.label(text="Bên Phải (R)")
        col_r.operator("rig_picker.select_bone", text="Cổ chân IK R").bone_name = "foot_ik.R"
        col_r.operator("rig_picker.select_bone", text="Đùi FK R").bone_name = "thigh_fk.R"
        col_r.operator("rig_picker.select_bone", text="Cẳng chân FK R").bone_name = "shin_fk.R"
        col_r.operator("rig_picker.select_bone", text="Bàn chân FK R").bone_name = "foot_fk.R"

def register():
    bpy.utils.register_class(RIG_PICKER_OT_select_bone)
    bpy.utils.register_class(RIG_PICKER_OT_select_all)
    bpy.utils.register_class(RIG_PICKER_OT_clear_selection)
    bpy.utils.register_class(VIEW3D_PT_rigify_picker)

def unregister():
    bpy.utils.unregister_class(RIG_PICKER_OT_select_bone)
    bpy.utils.unregister_class(RIG_PICKER_OT_select_all)
    bpy.utils.unregister_class(RIG_PICKER_OT_clear_selection)
    bpy.utils.unregister_class(VIEW3D_PT_rigify_picker)

if __name__ == "__main__":
    register()
