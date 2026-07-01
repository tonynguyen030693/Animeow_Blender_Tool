import bpy

def clean_empty_vertex_groups():
    # Lấy object đang được chọn (active object)
    ob = bpy.context.object

    if not ob:
        print("Không có object nào được chọn!")
        return

    if ob.type != 'MESH':
        print(f"Object '{ob.name}' không phải là Mesh!")
        return

    print(f"Đang quét các Vertex Group của: {ob.name}...")
    
    # Khởi tạo trạng thái trống cho tất cả các group
    vgroup_used = {i: False for i, k in enumerate(ob.vertex_groups)}
    
    # Kiểm tra xem có vertex nào được gán weight > 0 hay không
    for v in ob.data.vertices:
        for g in v.groups:
            if g.weight > 0.0:
                vgroup_used[g.group] = True
                
    deleted_count = 0
    # Xóa các group trống (duyệt ngược từ dưới lên để tránh lệch chỉ số index)
    for i, used in sorted(vgroup_used.items(), reverse=True):
        if not used:
            group_name = ob.vertex_groups[i].name
            ob.vertex_groups.remove(ob.vertex_groups[i])
            deleted_count += 1
            print(f"Đã xóa Vertex Group trống: {group_name}")

    print(f"Hoàn thành! Đã xóa tổng cộng {deleted_count} Vertex Group trống.")

# Chạy hàm
clean_empty_vertex_groups()
