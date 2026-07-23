# 📘 Quy Tắc Đặt Tên & Cấu Trúc Thư Viện Studio Library (Enjo Project)

Tài liệu này quy định chuẩn hóa cấu trúc thư mục và quy tắc đặt tên cho bộ **Studio Library** của dự án Enjo, giúp animator nhanh chóng tra cứu, lưu trữ và tái sử dụng Pose / Anim một cách nhất quán.

---

## 1. Quy Tắc Đặt Tên Thư Mục Nhân Vật (`01_Characters/`)
Thư mục chứa các nhân vật phải được đánh số thứ tự 2 chữ số kèm gạch dưới `_` để sắp xếp ưu tiên theo bảng chữ cái:

* **Cú pháp**: `[STT_2_chữ_số]_[Tên_Nhân_Vật]`
* **Ví dụ mẫu**:
  * `01_Baby` *(Nhân vật chuẩn mẫu)*
  * `02_Baby_Leo`
  * `03_Brother`
  * `04_Dad`
  * `05_Donal`
  * `06_Lilly_Bunny`
  * `07_Mom`
  * `08_Sammy_Bear`
  * `09_Sister`
  * `10_Toby_Monkey`
  * `11_Woofin`

---

## 2. Cấu Trúc Chuẩn Bên Trong Thư Mục Nhân Vật (Lấy `01_Baby` Làm Mẫu)

Mỗi thư mục nhân vật bắt buộc chia làm **3 nhóm chính**:

```text
01_Baby/
├── 01_Anim/         # Chứa các file chuyển động (Animation clips)
├── 02_Pose/         # Chứa các tư thế tĩnh, biểu cảm, dáng tay, selection sets
└── 99_Trash/        # Chứa dữ liệu nháp / hỏng / chờ xóa
```

---

## 3. Chi Tiết Phân Loại Thư Mục Con Trong `Anim/`

Toàn bộ file diễn hoạt (.anim) cần đưa vào đúng nhóm động tác tương ứng:

* 📁 **`Arm/`**: Động tác tay (khoanh tay, vẫy tay, giơ tay...).
* 📁 **`Cycle/`**: Chuỗi chuyển động lặp (Idle cycle, Breathing cycle...).
* 📁 **`Dance/`**: Động tác nhảy múa.
* 📁 **`Facial_Animation/`**: Diễn hoạt cơ mặt / cảm xúc dạng clip.
* 📁 **`Jump/`**: Động tác bật nhảy / đáp đất.
* 📁 **`Knee/`**: Động tác quỳ, tì gối.
* 📁 **`Lay/`**: Động tác nằm (nằm ngửa, nằm sấp, nằm nghiêng).
* 📁 **`LipSync/`**: Diễn hoạt cử động môi / nhép giọng thoại theo nhạc.
* 📁 **`Sit/`**: Động tác ngồi (ngồi ghế, ngồi sàn...).
* 📁 **`Stand/`**: Động tác đứng (đứng nghỉ, đứng chờ...).
* 📁 **`Swim/`**: Động tác bơi lội.
* 📁 **`Turn/`**: Động tác quay người / xoay 90-180 độ.
* 📁 **`Walk_run/`**: Động tác đi bộ / chạy.

---

## 4. Chi Tiết Phân Loại Thư Mục Con Trong `Pose/`

Toàn bộ file pose tĩnh (.pose) và selection (.selection) được phân loại như sau:

* 📁 **`Body/`**: Dáng pose toàn thân tĩnh.
* 📁 **`Expression/`**: Biểu cảm khuôn mặt tĩnh (Vui, Buồn, Tức giận, Ngạc nhiên...).
* 📁 **`Finger/`**: Dáng bàn tay / ngón tay (Nắm đấm, Chỉ tay, Xòe tay...).
* 📁 **`lipsync/`**: Các khẩu hình miệng tĩnh (A, O, E, M...).
* 📁 **`Mir_selection/`**: File Selection Sets hỗ trợ Mirror (đối xứng).

---

## 5. Quy Tắc Đặt Tên File Item (`.pose`, `.anim`, `.selection`)

* Không dùng tiếng Việt có dấu hay ký tự đặc biệt.
* Phân cách bằng dấu gạch dưới `_`.
* **Quy tắc số thứ tự (BẮT BỘC 3 CHỮ SỐ)**:
  * Tất cả các số thứ tự trong tên item (folder `.pose`, `.anim`, `.selection`) **phải luôn có đủ 3 chữ số** (zero-padded: `001`, `002`, `010`, `100`...).
  * **Lý do**: Giúp Studio Library và Hệ điều hành sắp xếp chuẩn theo thứ tự alphabet/tự nhiên (tránh lỗi `10.pose` đứng trước `2.pose`).
* **Cú pháp mẫu**:
  * **Chỉ có số thứ tự**: `001.pose`, `002.pose`, `010.pose`, `100.pose`
  * **Có tên chi tiết kèm số**: `Stand_001.pose`, `Stand_010.pose`, `happy_smile_001.pose`, `fist_left_001.pose`
  * **Diễn hoạt (.anim)**: `walk_normal_cycle_001.anim`, `talk_happy_002.anim`
