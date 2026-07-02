import sys
import os
import traceback

# Thêm đường dẫn addon vào sys.path để import
addon_dir = r"e:\AI_Work\Blender\blender_addon"
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

import bpy
from animeow_toolkit.anim_linker.ui import ANIMEOW_PT_linker_panel

class DummyLayout:
    def __init__(self):
        self.active = True
    def box(self):
        print("Vẽ Box")
        return DummyLayout()
    def column(self, align=False):
        print("Vẽ Column")
        return DummyLayout()
    def row(self, align=False):
        print("Vẽ Row")
        return DummyLayout()
    def label(self, text="", icon='NONE'):
        print(f"Label: '{text}' (icon='{icon}')")
    def prop(self, data, property, text="", toggle=False):
        print(f"Prop: {property}")
    def operator(self, operator, text="", icon='NONE'):
        print(f"Operator: {operator}")
        return DummyLayout()

class DummyContext:
    def __init__(self):
        self.scene = bpy.context.scene
        # Lấy một object từ database hoặc None
        self.active_object = bpy.context.active_object
        self.active_pose_bone = None

class DummyPanel:
    def __init__(self):
        self.layout = DummyLayout()

try:
    print("--- BẮT ĐẦU CHẠY DRY-RUN UI ---")
    panel = DummyPanel()
    context = DummyContext()
    
    # Giả lập tình huống có active object
    if not context.active_object:
        # Tạo tạm thời một Object rỗng để test
        obj = bpy.data.objects.new("DummyObject", None)
        context.scene.collection.objects.link(obj)
        context.active_object = obj
        print(f"Đã giả lập Active Object: {obj.name}")
        
    ANIMEOW_PT_linker_panel.draw(panel, context)
    print("--- CHẠY DRY-RUN UI THÀNH CÔNG! ---")
except Exception as e:
    print("--- PHÁT HIỆN LỖI CRASH KHI VẼ UI: ---")
    traceback.print_exc()
