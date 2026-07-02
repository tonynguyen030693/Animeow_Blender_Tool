# Animeow Toolkit (Blender Extension)

Bộ công cụ diễn hoạt (animation) chuyên nghiệp dành cho Blender 4.2+ và 5.1+, hợp nhất các tính năng hỗ trợ đắc lực cho animator dưới một giao diện duy nhất.

## Các module tích hợp trong bộ Toolkit

1. **🎯 Anim Linker (Double Locator System):**
   * Gán nhanh constraint `Child Of` cho đối tượng/xương rig.
   * Sử dụng hệ thống **Double Locator (Hook & Offset)** giúp tương thích hoàn hảo với Rig dạng Linked / Library Overrides.
   * Hỗ trợ **Animation Transfer** (chuyển giao và giữ nguyên chuyển động cũ sang locator khi bắt đầu link).
   * **Space Switcher (Chuyển đổi không gian)**: Đổi tay cầm của nhân vật mà không làm giật vị trí trực quan.
   * **Bake & Clean**: Khóa Action keyframe thực tế và tự động xóa sạch Empty trung gian.

2. **📈 Graph Toolboard:**
   * Các công cụ Tween, Ease, Scale, Time Nudge, Mirror, Snap, và Clean keyframe nâng cao cho **Graph Editor**.
   * Hiển thị HUD tương tác trực tiếp giúp tinh chỉnh tốc độ chuyển động trực quan.

3. **🦴 Bone Picker:**
   * Giao diện vẽ Canvas trực quan để chọn nhanh các xương rig nhân vật (tương tự như DWPicker trong Maya).

4. **🔢 Transform Rounder:**
   * Làm tròn nhanh toạ độ Location, Rotation (độ), và Scale của các đối tượng hoặc xương đang chọn về số thập phân mong muốn, hỗ trợ Auto Keying.

5. **📋 Anim Copy & Paste (Advanced Copy/Paste):**
   * **Copy Anim**: Sao chép keyframe và đường cong Bezier của xương/object vào bộ nhớ tạm.
   * **Paste Normal**: Dán keyframe bắt đầu tại vị trí frame hiện tại của con trỏ Timeline.
   * **Paste Connect**: Dán nối tiếp mượt mà khử giật chuyển động (tự động bù đắp khoảng lệch offset giữa hai chuỗi).
   * **Mirror (Lật đối xứng)**: Sao chép chuyển động và lật đối xứng từ bên này sang bên kia của cơ thể.

---

## Phím tắt nhanh (Pie Menu)

* Nhấn tổ hợp phím **`Alt + Shift + A`** trong cửa sổ 3D Viewport để mở Pie Menu hình tròn ngay tại vị trí con trỏ chuột.
* Giúp gọi nhanh các lệnh: **Link Object**, **Switch Parent**, **Bake & Clean**, và các lệnh **Copy/Paste/Connect Anim**.

---

## Giao diện hiển thị

* **Trong 3D Viewport (Sidebar - phím N)**: Tab **Animeow** chứa các bảng điều khiển cho:
  * `🎯 Anim Linker`
  * `📋 Anim Copy & Paste`
  * `🔢 Transform Rounder`
  * `🦴 Picker`
* **Trong Graph Editor (Sidebar - phím N)**: Tab **Animeow** chứa bảng:
  * `⚡ Animeow Graph Toolboard`

---

## Hướng dẫn cài đặt

1. Tải file đóng gói [releases/animeow_toolkit.zip](file:///e:/AI_Work/Blender/releases/animeow_toolkit.zip).
2. Trong Blender, truy cập **Edit > Preferences > Get Extensions**.
3. Bấm vào biểu tượng mũi tên/dấu 3 chấm ở góc trên bên phải bảng Preferences -> Chọn **`Install from Disk...`**
4. Chọn file `.zip` đã tải và bấm cài đặt. Addon sẽ tự động kích hoạt.
