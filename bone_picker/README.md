# 🦴 BonePicker – Blender Add-on

Công cụ chọn xương trực quan cho Blender, lấy cảm hứng từ **DWPicker** (Maya).  
Cho phép bạn thiết kế bảng nút bấm tùy chỉnh để chọn nhanh các xương khi diễn hoạt.

---

## 📋 Yêu cầu

- **Blender 3.0** trở lên (đã test trên Blender 5.1.2)

---

## 🔧 Cách cài đặt

### Cách 1: Cài đặt dưới dạng Extension (Khuyên dùng cho Blender 4.2+ / 5.x)

1. Nén toàn bộ thư mục **`bone_picker`** thành file **`bone_picker.zip`**  
   *(Lưu ý: file ZIP phải chứa thư mục `bone_picker` bên trong, không được nén rời các file .py).*

2. Mở Blender → **Edit** → **Preferences** → Chọn tab **Extensions**.

3. Click vào biểu tượng menu (mũi tên hoặc bánh răng) ở góc trên cùng bên phải của tab Extensions.

4. Chọn **Install from Disk...** → Chọn file **`bone_picker.zip`** bạn vừa nén. Blender sẽ tự động nạp và kích hoạt add-on.

### Cách 2: Copy thủ công (Cho Blender cũ hơn hoặc thủ công)

1. Copy toàn bộ thư mục **`bone_picker`** vào thư mục extensions hoặc addons của Blender:
   
   - **Đối với Blender 4.2+ và 5.x:**
     ```
     %APPDATA%\Blender Foundation\Blender\<phiên_bản>\extensions\user_default\
     ```
   - **Đối với Blender 4.1 trở xuống:**
     ```
     %APPDATA%\Blender Foundation\Blender\<phiên_bản>\scripts\addons\
     ```

2. Mở Blender → **Edit** → **Preferences** → Tìm kiếm **"BonePicker"** và kích hoạt.

---

## 🚀 Cách sử dụng

### Mở Panel

1. Trong **3D Viewport**, nhấn phím **N** để mở Sidebar
2. Chọn tab **"Picker"** ở cạnh bên phải

### Thiết kế Picker (Edit Mode)

1. Nhấn nút **🎨 Edit Mode**
2. Chọn Armature (Rig) từ dropdown **Armature**
3. Tạo tab mới trong phần **Tabs** → nhấn **+**
4. Nhấn nút **▶** để bật Interactive Picker trên viewport
5. Tạo nút bấm:
   - **Thủ công:** Nhấn **+** trong phần Buttons → chọn xương trong Pose Mode → nhấn **Assign Selected Bones**
   - **Tự động:** Chọn các xương trong Pose Mode → nhấn **Auto-Create from Bones**
6. Tùy chỉnh nút: đổi tên, đổi màu, thay đổi hình dạng, kéo thả di chuyển trên canvas

### Diễn hoạt (Animate Mode)

1. Nhấn nút **🎬 Animate Mode**
2. Click vào nút trên canvas → xương tương ứng được chọn
3. **Shift + Click** → thêm xương vào selection
4. **Ctrl + Click** → bỏ chọn xương
5. **Lăn chuột** → zoom canvas
6. **Giữ chuột giữa + kéo** → pan canvas

### Lưu & Chia sẻ

- Picker data tự động lưu cùng file **.blend**
- Export ra file **.json**: mở phần **Import / Export** → nhấn **Export**
- Import từ file **.json**: nhấn **Import Picker** → chọn file

---

## 📁 Cấu trúc file

```
bone_picker/
├── __init__.py          # Đăng ký add-on
├── properties.py        # Data model
├── canvas.py            # Vẽ giao diện bằng GPU
├── operators.py         # Các thao tác (thêm/xóa/gán xương...)
├── animate_handler.py   # Xử lý tương tác chuột
├── panels.py            # Giao diện Panel (Sidebar)
├── io_handler.py        # Import/Export JSON
├── utils.py             # Hàm tiện ích
└── README.md            # File này
```

---

## ⌨️ Phím tắt trên Canvas

| Thao tác                  | Chức năng              |
| ------------------------- | ---------------------- |
| Click trái                | Chọn xương / Chọn nút |
| Shift + Click             | Thêm vào selection     |
| Ctrl + Click              | Bỏ chọn               |
| Ctrl + Shift + Click      | Đảo ngược selection    |
| Lăn chuột                 | Zoom in/out            |
| Giữ chuột giữa + kéo     | Pan canvas             |
| ESC                       | Tắt Interactive Picker |

---

## 📝 Ghi chú

- Add-on này được thiết kế để hoạt động tương tự **DWPicker** trong Maya
- Hỗ trợ nhiều tab picker cho các bộ phận khác nhau (Body, Face, Hands...)
- Màu nút tự động phân biệt Left (Đỏ) / Right (Xanh) khi dùng Auto-Create
- File JSON export có thể chia sẻ cho người khác hoặc dùng lại cho nhân vật khác
