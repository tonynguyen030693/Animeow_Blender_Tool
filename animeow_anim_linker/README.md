# 😸 Animeow Anim Linker

Addon hỗ trợ đắc lực cho các 3D Animator trong việc quản lý, gán nhanh và bake các **Object Constraints** (đặc biệt là `Child Of`) trực tiếp trong chế độ Pose Mode của Blender.

---

## 🎯 Tính năng nổi bật

1.  **Quick Link:**
    *   Tự động gán constraint `Child Of` từ một Object (như cốc nước, vũ khí...) vào xương (Bone) đang chọn.
    *   Tự động gọi lệnh **Set Inverse** ẩn giúp đối tượng giữ nguyên vị trí cũ (không bị bay lệch trục).
    *   **Smart Locator (Empty):** Tự động tạo một Empty làm trung gian tại tâm của Object để làm cha của nó. Giúp giữ cho Transform gốc của Object luôn sạch sẽ `(0, 0, 0)`.
2.  **Space/Parent Switcher:**
    *   Hỗ trợ chuyển đổi tay cầm vật thể (hoặc gán vật thể từ tay đặt xuống bàn) tại một Frame cụ thể.
    *   **Tự động tính toán ma trận thế giới (World Matrix):** Giúp giữ nguyên vị trí trực quan của vật thể tại frame chuyển đổi (không bị nhảy giật vị trí khi đổi tay).
3.  **One-Click Bake:**
    *   Bake toàn bộ chuyển động của vật thể thành các keyframe cứng độc lập trên Timeline.
    *   Tự động dọn dẹp các Constraint và Empty phụ trợ để file sạch sẽ khi xuất sang các Engine khác.

---

## 📂 Cấu trúc mã nguồn

*   **`__init__.py`**: File khởi tạo, đăng ký các lớp UI/Operator và định nghĩa thuộc tính trên Scene.
*   **`operators.py`**: Chứa toàn bộ logic xử lý chính bao gồm tạo ràng buộc, chuyển đổi không gian và bake keyframes.
*   **`ui.py`**: Thiết kế Panel giao diện nằm ở Sidebar (`N` panel) -> tab **`Animeow`**.

---

## 🛠️ Hướng dẫn sử dụng

### 1. Cài đặt Addon
1.  Nén thư mục `animeow_anim_linker` thành file `.zip`.
2.  Mở Blender -> **Edit** -> **Preferences** -> **Addons** -> **Install...**
3.  Chọn file `.zip` vừa nén và kích hoạt addon **Animation: Animeow Anim Linker**.

### 2. Thao tác thực tế
1.  Nhấn phím **`N`** trong 3D Viewport, chọn tab **`Animeow`**.
2.  **Đặt Target Bone:**
    *   Chuyển sang **Pose Mode** của bộ xương nhân vật, chọn xương bàn tay.
    *   Trên panel, nhấn nút **Lấy xương đang chọn** (biểu tượng Eyedropper) để tự điền tên Armature và Xương.
3.  **Gán Ràng Buộc (Quick Link):**
    *   Trở lại **Object Mode**, chọn vật thể (ví dụ: cái ly).
    *   Tích chọn hoặc bỏ chọn *Sử dụng Smart Locator*.
    *   Nhấn nút **Link Object to Bone**.
4.  **Bake Animation:**
    *   Chọn vật thể đã liên kết, nhấn **Bake & Clean Constraint** để chuyển đổi toàn bộ chuyển động sang keyframe cứng.
