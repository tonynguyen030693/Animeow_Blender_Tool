# Animeow Blender & Maya Tools Repository

Kho lưu trữ các công cụ, addon hỗ trợ diễn hoạt (animation) và dựng hình (modeling) cho Blender và Maya.

## Cấu trúc thư mục kho lưu trữ

```
Animeow_Blender_Tool/
├── blender_addon/
│   └── animeow_toolkit/        # [Blender Extension] Bộ công cụ diễn hoạt hợp nhất
│
├── Maya_script/
│   ├── aTools_python3-master   # [Maya Script] Bộ công cụ aTools cho Python 3
│   └── dwpicker                # [Maya Script] Giao diện chọn xương DWPicker
│
├── scripts/
│   ├── snap_aligner.py         # [Blender Addon] Công cụ lắp ráp mô hình rã
│   ├── clean_empty_vertex_groups.py
│   └── rigify_picker.py
│
├── releases/                   # Chứa các file đóng gói phát hành (.zip, .rar)
└── assets/                     # Tài nguyên hình ảnh, logo
```

---

## 1. Blender Extension: Animeow Toolkit
Bộ công cụ hoạt hình chuyên nghiệp hợp nhất dành cho Blender 4.2+ / 5.1+:
* **Anim Linker**: Tạo ràng buộc cặp locator thông minh, chuyển giao animation, Space Switch và Bake.
* **Graph Toolboard**: Trình hỗ trợ căn chỉnh đường cong Graph Editor (Tween, Ease, Scale, Time Nudge).
* **Bone Picker**: Giao diện chọn xương bằng Canvas trực quan.
* **Transform Rounder**: Làm tròn nhanh toạ độ biến đổi của vật thể/xương.

👉 Chi tiết hướng dẫn cài đặt và sử dụng xem tại [blender_addon/animeow_toolkit/README.md](file:///e:/AI_Work/Blender/blender_addon/animeow_toolkit/README.md).

---

## 2. Blender Addon: Snap Similar Parts
Công cụ hỗ trợ ráp các mảnh vỡ của mô hình bị rã rời về đúng vị trí dựa trên mesh gốc nguyên vẹn.
* Sử dụng so khớp hình học nâng cao (đỉnh, cạnh, mặt,bounding box).
* Hỗ trợ phân nhóm thủ công và căn chỉnh tuyệt đối/tương đối.

👉 Chi tiết hướng dẫn xem tại [README_snap_similar.md](file:///e:/AI_Work/Blender/README_snap_similar.md) (đã đổi tên từ file cũ).

---

## Nhật ký phát triển (Development Logs)
Các ghi chú chi tiết và nhật ký thay đổi hàng ngày được lưu trữ trong thư mục [takenote/](file:///e:/AI_Work/Blender/takenote):
* [Nhật ký phát triển ngày 01/07/2026](file:///e:/AI_Work/Blender/takenote/2026-07-01.md) - Khởi tạo công cụ Snap Similar Parts, sửa lỗi ghép đôi hình học và phân nhóm thủ công.
* [Nhật ký phát triển ngày 02/07/2026](file:///e:/AI_Work/Blender/takenote/2026-07-02.md) - Hỗ trợ Object-to-Object, nâng cấp hệ thống Double Locator, tự động chuyển giao chuyển động (Animation Transfer) và hợp nhất toàn bộ công cụ thành **Animeow Toolkit**.
