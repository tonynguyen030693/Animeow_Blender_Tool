# BÁO CÁO TỔNG HỢP NĂNG LỰC HỆ THỐNG & NHẬT KÝ SỬA LỖI (PROJECT SUMMARY & BUG LESSONS)

---

## 📌 I. TỔNG QUAN HỆ THỐNG BỘ CÔNG CỤ (ANIMEOW TOOLSET)

Dự án bao gồm 2 hệ sinh thái công cụ diễn hoạt chính:
1. **Animeow Toolkit (Blender Addon)**: Bộ công cụ hướng đối tượng (OOP) chạy trực tiếp trên Blender 4.2+, 5.0, 5.1+.
2. **Animeow Maya Toolboard & Enjo Pipeline (Maya Toolkit)**: Bộ công cụ hỗ trợ quy trình quản lý file sản xuất, nướng hoạt hình, liên kết locator và tương thích song song cả **Maya 2020 (Python 2.7)** và **Maya 2022+ (Python 3)**.

---

## 🚀 II. TỔNG HỢP CÁC TÍNH NĂNG ĐÃ HOÀN THÀNH

### 🎨 1. Phân Hệ Blender (`animeow_toolkit`)
- **Snap Similar Parts (`snap_aligner.py`)**: Tự động ghép nối các mảnh mô hình bị rã về đúng vị trí gốc dựa trên Mesh Data, Mesh Name, và Geometry (Local Bounding Box + số đỉnh/cạnh/mặt). Hỗ trợ Absolute Snap và Relative Snap (tìm mốc Z thấp nhất).
- **Anim Linker & Cặp Locator Kép**: Sử dụng cặp Empty lồng nhau `loc_parent_` (Hook) và `loc_child_` (Offset sạch key), tự động chuyển ma trận thế giới (`loc_temp`), nướng animation và hỗ trợ Space Switch giữ nguyên vị trí trực quan.
- **Smart Baker & Thuật toán 2-Pass Bảo vệ Cực trị**: Bake nội bộ ở Step=1 -> **Pass 1** giữ 100% các dáng cực trị (Local Extremes) -> **Pass 2** lọc keyframe tuyến tính theo threshold. Tự động đổi nội suy về `Bezier` và tay cầm `AUTO`. Tương thích chuẩn **Slotted Actions (Blender 5.0+)**.
- **Global Animation Layers**: Quản lý layer không phá hủy trên NLA. Xử lý triệt để lỗi NLA rỗng, lỗi nhầm Base track. Gộp Layer an toàn bằng cách duy trì Pose Mode khi Bake để nhân vật không bị sập về T-pose.
- **Anim Copy (Paste Mirror)**: Bổ sung 6 tùy chọn lật đối xứng độc lập (TX, TY, TZ, RX, RY, RZ).
- **Giao diện N-Panel Ngang**: Thanh Tab Ngang siêu gọn: `[ 🎯 Linker ] [ 📋 Copy ] [ 🔢 Rounder ] [ 🎬 Baker ] [ 🦴 Picker ]`.

### 🎬 2. Phân Hệ Maya (`Maya_script` & `Maya_script_2020_python_2`)
- **Animeow Enjo Pipeline (Quản lý File & Studio Library)**:
  - Tự động gọt tiền tố/hậu tố trùng (`_Anim_Anim`), tự động tăng Version file chuẩn (`_v01`, `_v02`, `_v03`...), xóa file Maya bẩn trực tiếp trên UI.
  - Quy hoạch toàn bộ Thư viện Studio Library về gốc chung: `Z:\Animeow_Production\Enjo_Library`.
  - Tự động unnest con vật ra ngoài và đánh số chuẩn tiếng Việt: `01_Characters`, `02_Animals` (`01_Con_Bo`, `02_Con_Ca`...), `03_Props_Vehicles`, `04_Common_Library`, `05_User_Scratch`.
  - Tự động chuyển các nhân vật chính (`Sammy_Bear`, `Toby_Monkey`, `Woofin`, `Woofin_Wolf`, `Lilly_Bunny`) về `01_Characters`.
  - Nâng cấp UI Tab 2 các nút mở nhanh: `👤 Characters`, `🐾 Animals`, `🚗 Props & Vehicles`, `✋ Common Poses`, `📖 Studio Library Tổng`.
  - Tự động gọi Studio Library API (`mutils.saveAnim`) xuất `all_assets.anim` và file anim lẻ từng Namespace khi Publish File.
- **Smart Link & Cặp Locator Kép**: Tạo cặp locator `Anm_loc_link_parent_` & `Anm_loc_link_child_` trong group `Animeow_locator`. Hỗ trợ **Link to World**. Bake & Clean siêu tốc x10-x50 bằng core C++.
- **Smart World Bake & Fake Constraint**: Nướng không gian thế giới bảo toàn cực trị hoặc nướng ngược về vật thể gốc, hỗ trợ lọc kênh và tùy chọn Không Constraint (`no_constraint`). Fake Constraint tính toán ma trận ma sát tương đối set key trực tiếp không làm rác Scene, hỗ trợ Multi-Follower.
- **Selection Sets Manager & Multi-Camera Playblast**: Quản lý bộ chọn theo cây phân cấp (`QTreeWidget`), tự động gom nhóm dưới `Animeow_sets`, bắt buộc tiền tố `ANM_`, đệ quy ẩn/hiện thành viên, xuất/nhập file JSON kèm Smart Namespace Mapping. Multi-Camera Playblast có tiến trình `QProgressDialog`, quay theo Render Settings (`defaultResolution`), tùy chọn thư mục lưu Custom, tự động nạp audio node không lo mất tiếng.
- **Arc Tracker & Curve Utilities**: Trích xuất Rotate Pivot thế giới khi đóng băng viewport (`cmds.refresh(suspend=True)`), vẽ đường cong NURBS mượt 100%, hiển thị key ticks đỏ (2x) & ticks vàng, hỗ trợ Update Trails 1-click qua message connection. Tích hợp Smooth Keys Slider thời gian thực, Clean Neighborhood, Clean Sub-frame Keys (độ nhạy `1e-9`), Local Scale.
- **Overlapper & Temp Pivot & ANM Hider**: Overlapper trễ chuyển động tự động tạo chuỗi khớp tạm. Temp Pivot tính trung điểm trọng tâm nhóm vật thể. ANM Hider tự tạo và lưu thuộc tính ẩn hiện các bộ phận của Rig.

---

## 🛑 III. TỔNG HỢP SỰ CỐ, LỖI VÀ BÀI HỌC ĐẮT GIÁ

### 🔴 1. Nhóm Lỗi Python 2 (Maya 2020) vs Python 3 (Maya 2022+)
1. **Bẫy "Lỗi Ảo" Traceback (Indirect Error Reporting)**:
   - *Sự cố*: Maya 2020 liên tục báo lỗi `SyntaxError` ở dòng 10 của `window.py` (`from Animeow_Enjo_Pipeline.core import file_manager...`), mặc dù câu lệnh import ở dòng 10 hoàn toàn đúng cú pháp.
   - *Nguyên nhân*: Do file module con `file_manager.py` bị dán đè chuỗi docstring `"""` hỏng bên trong. Python 2 không biên dịch được `file_manager.py` nên ném Traceback báo ngược vị trí lỗi về dòng lệnh `import` ở `window.py`.
   - *Giải pháp*: Dùng công cụ biên dịch tự động quét kiểm tra toàn bộ file: `python -c "import py_compile, glob; [py_compile.compile(f) for f in glob.glob('.../*.py')]"` để chỉ thẳng mặt file lỗi thực sự và sửa triệt để.
2. **Xung đột Cú pháp Relative Import (Dấu chấm `.`)**:
   - *Sự cố*: Dùng `from .core import ...` hoặc `from ..core import ...` trong Python 2.7 bị ném lỗi `SyntaxError: invalid syntax` ngay tại dấu chấm `.`.
   - *Giải pháp*: Chuyển 100% sang **Absolute Import** chuẩn mực (`import Animeow_Enjo_Pipeline.core.file_manager as file_manager`).
3. **Bẫy Cache RAM & Bytecode `.pyc` của Python 2**:
   - *Sự cố*: Code file `.py` đã được sửa đúng trên đĩa nhưng Maya 2020 chạy lại vẫn đọc file compiled `.pyc` cũ trong RAM/đĩa và tiếp tục báo lỗi cũ.
   - *Giải pháp*: Viết lệnh tự động giải phóng `sys.modules` kết hợp quét sạch toàn bộ file `.pyc` trên ổ cứng trước khi `import`.
4. **Lỗi Mã hóa Ký tự Unicode & Tiếng Việt (Python 2.7)**:
   - *Sự cố*: Chuỗi tiếng Việt có dấu gây crash `UnicodeDecodeError` khi ghép chuỗi, hoặc crash `UnicodeEncodeError` khi ném vào `cmds.warning`.
   - *Giải pháp*: Gỡ bỏ `unicode_literals`, viết hàm `safe_warning` tự động encode UTF-8 và thêm tiền tố `u` cho các chuỗi format.
5. **Lỗi Tràn Ngăn Xếp Đệ Quy (`maximum recursion depth exceeded`)**:
   - *Sự cố*: Khi reload module `window.py`, hàm `safe_print` bị lồng lại chính nó trong `__builtin__.print` gây ra vòng lặp gọi đệ quy vô hạn.
   - *Giải pháp*: Sử dụng closure factory `make_safe_print` kiểm tra thuộc tính `__name__` để bảo toàn đường ống in gốc.
6. **Lỗi `'NoneType' object is not callable` khi Reload Module**:
   - *Sự cố*: Khi nạp lại module, các biến global của cửa sổ cũ bị set thành `None`. Nếu animator bấm nút trên cửa sổ cũ chưa đóng sẽ bị crash `NoneType`.
   - *Giải pháp*: Chuyển sang thuộc tính động `@property` để luôn nạp module mới nhất từ `sys.modules` tại thời điểm click nút.

---

### 🔴 2. Nhóm Lỗi Blender & Addon Development (Blender 4.2 / 5.0 / 5.1+)
1. **Lỗi Slotted Actions (Blender 5.0+)**:
   - *Sự cố*: Khi tạo Action mới qua Python trên Blender 5.0+, Action bị thiếu `ActionSlot` khiến Graph Editor bị trống và NLA Editor không hiện F-Curves.
   - *Giải pháp*: Tự động tạo `ActionSlot` tương thích với loại đối tượng (`OBJECT`/`POSE`) và gán `action_slot` cho cả Active Action và `NlaStrip`.
2. **Lỗi Mất Animation khi Gộp Layer (NLA Bake Context Bug)**:
   - *Sự cố*: Khi gộp Layer, hệ thống gọi `bpy.ops.nla.bake` ở Object Mode với `only_selected=True`, làm Blender không thấy xương nào ở Pose Mode -> Nhân vật bị sập về dáng T-pose và mất sạch key.
   - *Giải pháp*: Tự động chuyển sang Pose Mode và chọn toàn bộ xương trước khi bake, sau đó mới khôi phục về Object Mode.
3. **Lỗi NLA Track Rỗng khi Xóa Layer**:
   - *Sự cố*: Đoạn code xóa layer bị lệnh `continue` sớm khi active action bị gỡ, khiến vòng lặp bỏ qua lệnh xóa NLA Track -> NLA Editor bị rác các track rỗng.
   - *Giải pháp*: Loại bỏ lệnh `continue` sớm để đảm bảo quét và xóa triệt me NLA track.
4. **Lỗi UILayout.label Keyword Argument Error (Blender 5.1 API)**:
   - *Sự cố*: Blender 5.1 quy định tham số `text` trong `layout.label()` là Positional-only, gọi `layout.label(text="...")` gây crash `TypeError`.
   - *Giải pháp*: Chuyển toàn bộ về đối số vị trí thuần túy `layout.label("...")`.
5. **Lỗi Tích tụ Locator Rác (`.001`, `.002`, `.003`)**:
   - *Sự cố*: Nhấn Link nhiều lần tạo ra hàng loạt locator rác trùng lặp trong Outliner.
   - *Giải pháp*: Chặn Link đè khi chưa Bake, đồng thời nâng cấp `cleanup_locators()` quét triệt để các locator có tiền tố trùng tên để xóa sạch.

---

### 🔴 3. Nhóm Lỗi Pipeline, Playblast & Quản lý Dự án
1. **Lỗi Lặp Tên File & Trùng Shot (`_Anim_Anim_v01_1.ma`)**:
   - *Sự cố*: Chọn Shot item bị dán thêm `_Anim`, tạo thêm Shot giả `LL_BGOTL_V01_Shot_01_Anim`, đổi tên file bị dán thêm `_1`, `_2`.
   - *Giải pháp*: Viết hàm `clean_shot_code` gọt sạch hậu tố `_Anim`/`_Lay`, cập nhật Regex `SCENE_NAME_PATTERN` hỗ trợ tự động tăng Version chuẩn (`_v01`, `_v02`, `_v03`...).
2. **Thư mục Studio Library Lộn xộn & Đặt tên Sai quy chuẩn**:
   - *Sự cố*: Thư mục 2 dự án Kidsong & Lolo nằm rải rác, các con vật nằm lồng trong folder `Animal`, đặt tên thiếu dấu gạch dưới (`Conheo`, `Conbo`).
   - *Giải pháp*: Gộp về `Z:\Animeow_Production\Enjo_Library`, unnest con vật ra ngoài, tự động di chuyển nhân vật chính (`Sammy`, `Toby`, `Woofin`, `Lilly`) về `01_Characters`, đánh số thứ tự chỉn chu (`01_Con_Bo`, `02_Con_Ca`...).
3. **Lỗi Quay Playblast Video Siêu Nhỏ (1% Scale) & Mất Tiếng**:
   - *Sự cố*: Giá trị scale float (`0.5`) từ UI không được nhân 100 thành phần trăm (`50%`), khiến Maya quay ra video siêu nhỏ vài chục pixel; audio node bị rỗng do `timeControl` bị tắt sound.
   - *Giải pháp*: Nhân 100 cast `int` trước khi truyền vào `cmds.playblast`, tự động quét audio node dự phòng và un-mute nhạc.
4. **Lỗi Đổi tên Locator Tự động làm Hỏng Select (World Bake)**:
   - *Sự cố*: Khi nướng locator thế giới, nếu trong scene đã có locator trùng tên, Maya tự động đổi tên thành `Anm_loc_bake_pCube1_01`, khiến câu lệnh `cmds.select` tiếp theo bị crash do không tìm thấy tên gốc.
   - *Giải pháp*: Trả về long path tuyệt đối từ `parent_to_animeow_group`, đồng thời hiển thị Dialog hỏi người dùng (*Yes: tạo số tăng dần / No: ghi đè xóa cũ / Cancel*).
