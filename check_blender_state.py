import bpy
import sys

# Kiểm tra các class đã đăng ký trong Blender
output_path = r"e:\AI_Work\Blender\blender_state_log.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write("=== KIỂM TRA ĐĂNG KÝ CLASS TRONG BLENDER ===\n\n")
    for name in dir(bpy.types):
        if any(keyword in name for keyword in ["ANIMEOW", "PICKER", "GRAPH_PT"]):
            cls = getattr(bpy.types, name)
            if hasattr(cls, "bl_idname"):
                f.write(f"Class: {name}\n")
                f.write(f"  bl_idname: {getattr(cls, 'bl_idname', 'N/A')}\n")
                f.write(f"  bl_label: {getattr(cls, 'bl_label', 'N/A')}\n")
                f.write(f"  bl_category: {getattr(cls, 'bl_category', 'N/A')}\n")
                f.write(f"  bl_space_type: {getattr(cls, 'bl_space_type', 'N/A')}\n")
                f.write(f"  bl_region_type: {getattr(cls, 'bl_region_type', 'N/A')}\n")
                f.write(f"  bl_parent_id: {getattr(cls, 'bl_parent_id', 'N/A')}\n")
                f.write(f"  has_poll: {hasattr(cls, 'poll')}\n\n")
                
    f.write("\n=== KIỂM TRA SCENE PROPERTIES ===\n")
    for attr in dir(bpy.types.Scene):
        if "animeow" in attr or "bone_picker" in attr:
            f.write(f"Scene Property: {attr}\n")

print("Đã ghi log kiểm tra vào blender_state_log.txt")
