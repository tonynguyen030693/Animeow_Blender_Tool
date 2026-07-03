# Animeow Maya Pipeline

Bộ công cụ hỗ trợ quản lý File cảnh diễn hoạt (Open/Save/Auto-versioning) và tự động xuất **Playblast** sạch sẽ cho **Autodesk Maya 2020** (tương thích Python 2.7 và PySide2).

---

## 🚀 Hướng Dẫn Cài Đặt

Có hai cách để cài đặt công cụ vào Maya:

### Cách 1: Kéo thả trực tiếp (Khuyên dùng)
1. Mở phần mềm Maya 2020.
2. Mở thư mục chứa pipeline bằng Explorer của Windows.
3. Kéo file `install.mel` thả thẳng vào trong khung nhìn 3D (Viewport) của Maya.
4. Hệ thống sẽ tự động tạo một nút bấm mang tên **AMP** trên thanh Shelf hiện tại của bạn và kích hoạt menu **Animeow** trên thanh công cụ chính.

### Cách 2: Chạy thủ công bằng mã Python
Nếu bạn không muốn kéo thả, bạn có thể copy đoạn mã dưới đây dán vào tab **Python** trong **Script Editor** của Maya rồi nhấn Ctrl+Enter:

```python
import sys
# Thay đổi đường dẫn dưới đây thành thư mục chứa "animeow_Maya_pipeline" trên máy của bạn
path = r"e:/AI_Work/Blender/Maya_script"
if path not in sys.path:
    sys.path.insert(0, path)

import animeow_Maya_pipeline
import animeow_Maya_pipeline.menu as menu
menu.create_menu()
animeow_Maya_pipeline.show()
```

---

## 🛠️ Các Tính Năng Chính & Cách Sử Dụng

### 1. Cấu trúc thư mục tiêu chuẩn
Công cụ được xây dựng để hoạt động hiệu quả nhất với cấu trúc thư mục dự án chuẩn hóa sau:
```text
Project_Root/
├── Shots/
│   └── [Sequence_Name]/
│       └── [Shot_Name]/
│           └── Anim/
│               ├── Work/       # Chứa các file làm việc (.ma, .mb)
│               └── Playblast/  # Chứa các video playblast (.mov, .avi)
```

### 2. Quản lý File làm việc (Shot Manager)
* **Browse Project**: Chọn thư mục gốc dự án của bạn (ví dụ: `D:/Maya_Projects/MyProject`). Thư mục này sẽ được ghi nhớ tự động cho các lần khởi động Maya sau.
* **Sequence & Shot Dropdowns**: Lọc nhanh các phân đoạn và cảnh quay tương ứng.
* **Work Files List**: Hiển thị danh sách toàn bộ các version của cảnh quay được chọn. Chỉ cần **Double Click (Nhấp đúp chuột)** vào một file bất kỳ để mở.
  * *Lưu ý*: Nếu file hiện tại của bạn có thay đổi chưa lưu, Maya sẽ hiển thị cảnh báo yêu cầu bạn xác nhận để bảo vệ công sức làm việc.
* **Tạo Shot Mới**: Nhấn nút `Tạo Shot Mới (v001)` để khởi tạo nhanh cảnh quay đầu tiên kèm theo cấu trúc thư mục tương ứng.
* **Lưu Phiên Bản Mới**: Nhấn `Lưu Phiên Bản Mới (+1)`. Hệ thống tự động phân tích tên file hiện tại, tăng số hiệu phiên bản lên (ví dụ: `v001` -> `v002`) và lưu lại dưới dạng file sạch `.ma`.

### 3. Auto Playblast (Xuất video review nhanh)
* Tự động ẩn toàn bộ xương (joints), curves điều khiển, locators, lưới nền (grid)... để cho ra video review sạch nhất.
* Tự động đặt tên video trùng khớp với phiên bản file Maya đang mở và lưu thẳng vào thư mục `Playblast/`.
* Tự động phát hiện và đính kèm âm thanh (Audio Track) đang active trên Time Slider.
* Tự động khôi phục lại toàn bộ trạng thái hiển thị của Viewport ngay sau khi quá trình Playblast hoàn tất để bạn có thể tiếp tục làm việc bình thường.
