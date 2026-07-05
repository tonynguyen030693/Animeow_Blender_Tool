# Brainstorming: Tích hợp Quy trình Tách/Gộp Shot (Split & Combine) vào Pipeline

Dựa trên mã nguồn của công cụ `Smart Bookmark` hiện tại và quy trình làm việc thực tế của dự án **Enjo**, chúng tôi đề xuất phương án tích hợp và tự động hóa quy trình **Tách (Split) và Gộp (Combine) Shot** đồng bộ trực tiếp với hệ thống thư mục của **Animeow Enjo Pipeline**.

---

## 🔄 Luồng Công Việc Đề Xuất (Workflow)

```mermaid
graph TD
    A["🎬 File Layout Tổng (Chứa Bookmarks)"] -->|🚀 Tách Shot Tự Động| B["📂 Hệ thống thư mục Pipeline"]
    B -->|Tách file| C1["📁 Shot 01-25 File & Video nháp"]
    B -->|Tách file| C2["📁 Shot 26-50 File & Video nháp"]
    B -->|Tách file| C3["📁 Shot 51-60 File & Video nháp"]
    
    C1 -->|Làm Animation lẻ| D1["👤 Anim Shot 01-25 (Published)"]
    C2 -->|Làm Animation lẻ| D2["👤 Anim Shot 26-50 (Published)"]
    C3 -->|Làm Animation lẻ| D3["👤 Anim Shot 51-60 (Published)"]
    
    D1 & D2 & D3 -->|🔗 Gộp Anim Tự Động| E["📦 File Anim Tổng Hoàn Chỉnh (Bàn giao)"]
```

---

## 💡 Các Ý Tưởng Triển Khai Chi Tiết

### 1. Tách (Split) Layout Tổng Tự Động Theo Đúng Pipeline
* **Vấn đề của Tool cũ:** Artist phải chọn thư mục lưu thủ công (`cmds.fileDialog2`), dễ dẫn đến việc chọn sai thư mục hoặc đặt tên file shot lẻ lệch quy chuẩn của server.
* **Giải pháp Pipeline:** Tích hợp nút **"Tách Shot từ Layout Tổng"** trong công cụ:
  * Tool tự động quét toàn bộ các `timeSliderBookmark` trên timeline của file Layout tổng.
  * Tự động tạo ra các thư mục con tương ứng trên Pipeline (ví dụ: `WorkingFile/Layout/[Shot_Name]/file/`).
  * Thực hiện cắt keyframes ngoài khoảng bookmark (`cmds.cutKey`) và thiết lập playback range cho từng shot.
  * Tự động lưu file thành đúng tên quy chuẩn (ví dụ: `KS_ESS_V02_Shot_31-60_Lay_v01.ma`) trực tiếp vào thư mục con của shot đó mà không cần bất kỳ sự can thiệp thủ công nào từ artist.

---

### 2. Gộp (Combine) Linh Hoạt Theo Cụm / Block Tùy Chỉnh
Đây là yêu cầu vô cùng thực tế và thông minh để giải quyết vấn đề file scene quá nặng khi làm việc với các tập phim dài (ví dụ 60 shot). Tool sẽ hỗ trợ **3 chế độ gộp cụm** linh hoạt:
* **Chế độ A: Nhập chuỗi phân nhóm thủ công (Linh hoạt nhất):** Nhập `1-10, 11-20, ...` tool sẽ tự động xuất ra các file gộp cụm tương ứng.
* **Chế độ B: Chia đều tự động** theo số lượng shot chỉ định.
* **Chế độ C: Tích chọn trực quan** các shot trên bảng danh sách của tool.

---

### 3. Giải Pháp Tận Dụng Studio Library & Tự Động Bake Constrains

Để đảm bảo việc chuyển giao chuyển động (copy/paste anim) diễn ra siêu tốc và không bị lỗi lệch khớp vị trí do các ràng buộc ràng buộc (constrains) khác nhau giữa các file:

#### 3.1. Tự động Phát hiện và Bake Constrains (Locator & Object Constrains)
* **Thông tin dự án:** Các artist sử dụng **Reference Rig** để làm việc, chỉ tạo Keyframe trên các Control Curve của Rig đó. Trong quá trình làm, họ thường tạo thêm **Locator** (đồ vật định vị trung gian cục bộ trong file lẻ) để làm điểm neo constrain cho control (ví dụ tay bám theo locator).
* **Vấn đề:** Locator và constrain này chỉ tồn tại trong file Anim lẻ, hoàn toàn không có trong file tổng. Nếu chỉ copy key thô của control, control đó sẽ mất vị trí chính xác khi sang file tổng.
* **Giải pháp tự động hóa:** 
  1. Tool tự động quét toàn bộ các control curve của các **Reference Rig** đang được chọn.
  2. Phát hiện các node constrain liên kết control của Rig với các Locator ngoài (hoặc các vật thể khác).
  3. Tự động gọi lệnh **Bake Simulation** của Maya trên chính các control curve của Reference Rig:
     ```python
     cmds.bakeResults(
         rig_controls_to_bake,
         time=(start_frame, end_frame),
         simulation=True,
         removeConstraint=True  # Rút phích cắm constrain sau khi bake
     )
     ```
  4. **Kết quả:** Toàn bộ chuyển động do Locator constrain tạo ra sẽ được chuyển đổi thành các keyframe tuyệt đối trên các control curve của Rig. Các Locator rác và constrain lúc này có thể được bỏ qua một cách an toàn. File cụm tổng chỉ việc nạp anim của các control curve này là khớp chuyển động chuẩn 100% mà không cần dựng lại bất kỳ constrain hay locator nào!

#### 3.2. Dọn dẹp keyframe lố ngoài timeline (Clean Keys)
* **Quy trình xử lý:**
  * **Xuất lấn biên an toàn (Safety Padding):** Để đảm bảo quán tính chuyển động mượt mà tại điểm giao thoa giữa các shot, tool sẽ tự động xuất lấn biên thêm **+/- 5 hoặc 10 frames** (ví dụ xuất từ 95 đến 205).
  * **Clean Keys (Dọn dẹp):** Sau khi import vào file cụm tổng, tool sẽ tự động chạy lệnh `cmds.cutKey` để cắt bỏ hoàn toàn các key ngoài khoảng biên của cụm đó, đảm bảo file cụm tổng luôn sạch sẽ.

#### 3.3. Tận dụng API Studio Library cho việc Copy/Paste siêu tốc
* **Studio Library** chạy rất nhanh vì nó xuất dữ liệu anim trực tiếp thành các file text dictionary có cấu trúc cực nhẹ (lưu tangent, weight, values của key) thay vì ghi file Maya nặng.
* Do Studio Library đã được tích hợp sẵn trong source của bạn tại `AnimeowTool/SourceTool/studiolibrary`, tool Pipeline có thể **gọi trực tiếp API Python của Studio Library chạy ngầm (API Mode)** để thực hiện việc export/import anim nhanh chóng mà không cần artist phải mở giao diện Studio Library lên bấm tay.

---

## 🛠️ Đề Xuất Giao Diện Tích Hợp (UI Tab mới)

Chúng ta có thể thêm một Tab mới bên cạnh Tab **Quản Lý File** hiện tại gọi là **"Tách/Gộp Cảnh (Split & Merge)"**:

| Giao Diện Thiết Kế Đề Xuất |
| :--- |
| **TAB: TÁCH / GỘP CẢNH**<br><br>  **[ Khu vực 1: Tách Shot Layout Tổng ]**<br>  * Đọc bookmarks từ scene hiện tại: **[Quét Bookmarks]**<br>  * Danh sách bookmark tìm thấy: *Shot_01-25 (1-100), Shot_26-50 (101-250)...*<br>  * Chọn các control nhân vật cần giữ key: `[ Chọn Control Nhân Vật ]`<br>  * **[ 🚀 Bắt đầu Tách và đồng bộ Pipeline (1 Click) ]**<br><br>  **[ Khu vực 2: Gộp Animation Cảnh Tổng ]**<br>  * Phương thức gộp: `(o) Studio Library API`  hoặc  `( ) Import ATOM`<br>  * Cấu hình an toàn: `[x]` Tự động Bake Constrains (Locator/Rig)  `[x]` Thêm +/- `5` frame đệm (Padding)<br>  * Chọn kiểu chia Block:<br>    - `[x]` Tự gõ Block: `1-10, 11-20, 21-30, 31-45, 46-60`<br>    - `[ ] Chia đều`: `10` shot một file<br>  * **[ 📦 Tiến hành Gộp Cảnh & Xuất File Cụm Bàn Giao ]** |
