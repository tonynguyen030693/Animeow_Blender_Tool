# Project-Scoped Rules for Animeow Blender Tool

## 1. Đồng bộ hóa Addon & Blender Extensions
* **Hiện tượng**: Khi phát triển Addon trong workspace `e:\AI_Work\Blender\blender_addon\animeow_toolkit`, Blender 5.0+ thực tế sẽ tải và chạy Addon từ thư mục Extensions trong AppData của người dùng:
  `C:\Users\Animeow\AppData\Roaming\Blender Foundation\Blender\5.1\extensions\user_default\animeow_toolkit`
* **Quy tắc**: Khi thay đổi bất kỳ code Python nào trong workspace dự án, **BẮT BUỘC** phải sao chép (đồng bộ) file thay đổi đó sang thư mục Extensions tương ứng trong AppData, sau đó yêu cầu người dùng chạy lệnh **Reload Scripts** (`F3 -> Reload Scripts` hoặc `Alt + R`) hoặc khởi động lại Blender để áp dụng thay đổi.

## 2. Quản lý NLA Tracks khi xóa Animation Layer
* **Hiện tượng**: Khi xóa một Animation Layer (hoặc gỡ bỏ vật thể khỏi Layer) mà Layer đó đang active, nếu action của nó đang được gán trực tiếp làm active action trên object thì sau khi xóa action, NLA track trống vẫn có thể tồn tại nếu không bị xóa triệt để.
* **Quy tắc**:
  * Tránh sử dụng lệnh `continue` sớm trong vòng lặp xử lý object khi xóa Layer / gỡ Object.
  * Cần đảm bảo đoạn code tìm kiếm NLA track (`_find_track_for_layer`) và loại bỏ track (`nla_tracks.remove(track)`) luôn được thực thi đầy đủ cho tất cả objects liên quan.
