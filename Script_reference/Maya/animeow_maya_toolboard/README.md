# Animeow Maya Toolboard (Anim Combiner)

Bộ công cụ hỗ trợ ghép nối chuyển động (**Animation Combiner**) từ nhiều cảnh diễn hoạt shot lẻ thành một file master duy nhất cho **Autodesk Maya 2020** (tương thích Python 2.7 và PySide2).

---

## 🚀 Hướng Dẫn Cài Đặt

### Cách 1: Kéo thả trực tiếp (Khuyên dùng)
1. Mở Maya 2020.
2. Kéo file `install.mel` trong thư mục `animeow_maya_toolboard` thả thẳng vào khung nhìn 3D Viewport.
3. Một nút bấm **ATB** mới sẽ được tạo trên thanh Shelf hiện hành, đồng thời đăng ký thêm mục **Anim Combiner Toolboard** vào menu **Animeow** của bạn.

### Cách 2: Chạy bằng Script Editor (Python)
Mở tab Python trong Script Editor và chạy đoạn mã sau:

```python
import sys
# Thay đổi đường dẫn đến thư mục cha của animeow_maya_toolboard trên máy bạn
path = r"e:/AI_Work/Blender/Maya_script"
if path not in sys.path:
    sys.path.insert(0, path)

import animeow_maya_toolboard
import animeow_maya_toolboard.menu as menu
menu.create_menu()
animeow_maya_toolboard.show()
```

---

## 🛠️ Hướng Dẫn Sử Dụng Tính Năng Ghép Anim

Công cụ sử dụng công nghệ xuất/nhập file chuyển động **`.atom`** của Maya để chuyển đổi dữ liệu keyframe cực kỳ an toàn, mượt mà và tối ưu hiệu năng.

### Các bước thực hiện:
1.  **Bước 1: Chọn Thư mục Shot lẻ**: 
    Bấm nút *Browse* tại mục 1 để chọn thư mục chứa các file shot lẻ (ví dụ: `Shot01.ma`, `Shot02.ma`... `Shot10.ma`). Danh sách file lọc được sẽ xuất hiện trên bảng UI, bạn có thể tích chọn/bỏ chọn những file muốn ghép.
2.  **Bước 2: Chọn File Master Mẫu**:
    Bấm nút *Browse* tại mục 2 để chọn file master template (file chứa Rig sạch, đã setup sẵn namespace giống với các file shot lẻ nhưng chưa có diễn hoạt).
3.  **Bước 3: Chọn Đường Dẫn Lưu File Kết Quả**:
    Chọn nơi sẽ lưu file tổng sau khi đã gom toàn bộ animation.
4.  **Bước 4: Cấu Hình Thời Gian (Time Options)**:
    *   **Nối đuôi tự động (Sequential Join)**: Thích hợp khi các file con đều làm việc từ frame 1. Hệ thống sẽ tự tính độ dài từng shot con để đắp nối tiếp nhau trên master timeline (ví dụ: Shot 2 đắp tiếp ngay sau khi Shot 1 hết).
    *   **Giữ nguyên Frame gốc (Keep Original Frames)**: Thích hợp khi các shot con đã được chia mốc timeline thực tế trên đĩa (ví dụ Shot 1 là frame 101-200, Shot 2 là 201-300).
5.  **Bước 5: Nhấn Ghép Nối**:
    Nhấn nút `Bắt Đầu Ghép Nối Animation`. Maya sẽ tiến hành mở ngầm các file con, trích xuất dữ liệu anim ra file `.atom` tạm, sau đó mở file master để dán lần lượt và lưu lại thành quả.
