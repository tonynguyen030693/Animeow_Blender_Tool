# Animeow Maya Toolboard (Smart Link)

Bộ công cụ hỗ trợ ràng buộc nâng cao (**Smart Link - Double Locator System**) giúp artist liên kết nhanh, quản lý locator và nướng chuyển động (Bake Constraint) tối ưu cho **Autodesk Maya 2022+** (tương thích Python 3 và PySide2).

---

## 🚀 Hướng Dẫn Cài Đặt

### Cách 1: Kéo thả trực tiếp (Khuyên dùng)
1. Mở Maya 2022+.
2. Kéo file `install.mel` trong thư mục `animeow_maya_toolboard_v03` thả thẳng vào khung nhìn 3D Viewport.
3. Một nút bấm **ATB** mới sẽ được tạo trên thanh Shelf hiện hành, đồng thời đăng ký thêm mục **Animeow Toolboard** vào menu **Animeow** của bạn.

### Cách 2: Chạy bằng Script Editor (Python)
Mở tab Python trong Script Editor và chạy đoạn mã sau:

```python
import sys
# Thay đổi đường dẫn đến thư mục cha của animeow_maya_toolboard_v03 trên máy bạn
path = r"e:/AI_Work/Blender_Maya_Script/Maya_script_2022_python_3"
if path not in sys.path:
    sys.path.insert(0, path)

import animeow_maya_toolboard_v03
import animeow_maya_toolboard_v03.menu as menu
menu.create_menu()
animeow_maya_toolboard_v03.show()
```

---

## 🛠️ Hướng Dẫn Sử Dụng Tính Năng Smart Link

Tính năng sử dụng hệ thống **Double Locator (Hook & Offset)** lồng nhau để tạo liên kết động linh hoạt giữa các đối tượng (ví dụ: nhân vật cầm nắm đồ vật).

### Các bước thực hiện:
1. **Liên kết (Link):**
   * Chọn đối tượng dẫn đường (ví dụ: xương bàn tay) -> Nhấn nút **Lấy đang chọn** ở ô **Target (Vật dẫn)**.
   * Chọn đối tượng bị dẫn (ví dụ: cái cốc) -> Nhấn nút **Lấy đang chọn** ở ô **Owner (Vật bị dẫn)**.
   * Nhấn **🚀 Gán Liên Kết (Link)**.
   * *Kết quả:* Một cặp locator lồng nhau (`loc_parent` và `loc_child`) sẽ được tạo ra tại vị trí của cốc. `loc_parent` sẽ bị constraint đi theo bàn tay. Cái cốc sẽ bị constraint đi theo `loc_child`. Nếu cái cốc có chuyển động cũ, chuyển động đó sẽ được tự động ghi nhận và chuyển đổi sang `loc_child` mà không làm thay đổi trực quan vị trí.

2. **Thay đổi vật dẫn (Switch Target):**
   * Khi cốc cần chuyển từ tay trái sang tay phải:
   * Chọn xương tay phải -> Nhấn **Lấy đang chọn** ở ô **Target (Vật dẫn)**.
   * Chọn cái cốc -> Nhấn **🔄 Đổi Vật Dẫn (Switch Target)** tại frame chuyển giao.
   * *Kết quả:* Ràng buộc được chuyển đổi sang tay phải tại đúng frame đó mà cốc không bị lệch vị trí trực quan.

3. **Bake & Clean:**
   * Chọn cái cốc -> Nhấn **🎬 Bake & Clean (Giải phóng)**.
   * *Kết quả:* Chuyển động được nướng trực tiếp vào cốc, đồng thời các locator và constraint trung gian được dọn dẹp sạch sẽ khỏi scene.
