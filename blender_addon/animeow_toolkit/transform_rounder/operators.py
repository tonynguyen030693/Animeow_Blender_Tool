"""
operators.py — Animeow Toolkit / Transform Rounder
====================================================
Logic làm tròn Location, Rotation, Scale của Object hoặc Pose Bone.
"""

import bpy
import math
from mathutils import Euler, Quaternion, Vector
from ..core.utils import insert_auto_keyframe


class ANIMEOW_OT_round_transforms(bpy.types.Operator):
    """Làm tròn các thông số transform của Object hoặc Pose Bone được chọn"""
    bl_idname = "animeow.round_transforms"
    bl_label = "Round Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        decimals = scene.animeow_round_decimals
        round_loc = scene.animeow_round_location
        round_rot = scene.animeow_round_rotation
        round_scale = scene.animeow_round_scale

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
                if round_loc:
                    bone.location = [round(v, decimals) for v in bone.location]
                    insert_auto_keyframe(context, bone, "location", armature_obj=bone.id_data)

                if round_scale:
                    bone.scale = [round(v, decimals) for v in bone.scale]
                    insert_auto_keyframe(context, bone, "scale", armature_obj=bone.id_data)

                if round_rot:
                    rot_path = self._round_rotation(bone, decimals)
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
                if round_loc:
                    obj.location = [round(v, decimals) for v in obj.location]
                    insert_auto_keyframe(context, obj, "location")

                if round_scale:
                    obj.scale = [round(v, decimals) for v in obj.scale]
                    insert_auto_keyframe(context, obj, "scale")

                if round_rot:
                    rot_path = self._round_rotation(obj, decimals)
                    insert_auto_keyframe(context, obj, rot_path)
        else:
            self.report({'WARNING'}, "Hãy chuyển sang Object Mode hoặc Pose Mode")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Đã làm tròn thông số về {decimals} chữ số thập phân.")
        return {'FINISHED'}

    @staticmethod
    def _round_rotation(target, decimals):
        """Làm tròn Rotation theo chế độ xoay hiện tại (Euler/Quaternion/Axis Angle).

        Returns:
            str: data_path của rotation đã được làm tròn.
        """
        if target.rotation_mode == 'QUATERNION':
            euler = target.rotation_quaternion.to_euler()
            rounded = Euler(
                [math.radians(round(math.degrees(v), decimals)) for v in euler],
                euler.order
            )
            target.rotation_quaternion = rounded.to_quaternion()
            return "rotation_quaternion"
        elif target.rotation_mode == 'AXIS_ANGLE':
            angle_deg = math.degrees(target.rotation_axis_angle[0])
            rounded_angle = math.radians(round(angle_deg, decimals))
            rounded_axis = [round(v, decimals) for v in target.rotation_axis_angle[1:]]
            target.rotation_axis_angle = [rounded_angle] + rounded_axis
            return "rotation_axis_angle"
        else:
            euler = target.rotation_euler
            rounded = Euler(
                [math.radians(round(math.degrees(v), decimals)) for v in euler],
                euler.order
            )
            target.rotation_euler = rounded
            return "rotation_euler"
