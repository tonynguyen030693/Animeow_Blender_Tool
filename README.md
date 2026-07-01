# Snap Similar Parts (Blender Addon)

Add-on Blender giúp tự động ghép nối và lắp ráp các bộ phận của mô hình bị rã rời về đúng vị trí dựa trên mô hình gốc nguyên vẹn.

## Tính năng nổi bật

1. **Định vị tâm thông minh (Pivot Origin Alignment):**
   * Tự động đưa tâm các vật thể về cùng một hệ quy chiếu trước khi snap (ví dụ: **Tâm hình học - Median**, **Trọng tâm Bounding Box**, **Volume**, hoặc **Surface**).
   * Giúp việc căn chỉnh hình học chính xác 100% ngay cả khi tâm gốc của các mảnh bị đặt lệch nhau.

2. **Cơ chế Nhận diện Hình học Nâng cao:**
   * So khớp các bộ phận duplicate dựa trên cấu trúc mesh (số lượng đỉnh, cạnh, mặt) kết hợp với **kích thước hộp bao cục bộ (Local Bounding Box)**.
   * Ngăn chặn việc nhận diện nhầm giữa các bộ phận khác nhau nhưng vô tình có cùng số lượng đỉnh (ví dụ: bánh răng nhỏ và vòng đệm).

3. **Phân nhóm Thủ công (Manual Grouping):**
   * Cho phép người dùng quét chọn và gắn nhãn nhóm **Gốc (Targets)** và nhóm **Rã (Sources)** trực tiếp trên giao diện UI.
   * Giải quyết hoàn toàn lỗi phân nhóm bằng tọa độ khi các mảnh bị rã rời quá rộng hoặc xen kẽ nhau.

4. **Hai chế độ căn chỉnh linh hoạt:**
   * **Snap trực tiếp (Absolute Snap):** Đưa các mảnh bị rã bay thẳng về khớp đè lên mô hình gốc.
   * **Lắp ráp tại chỗ (Relative Snap):** Lắp ráp các mảnh bị rã thành mô hình hoàn chỉnh ngay tại vị trí hiện tại dựa trên một điểm neo (Anchor) được chọn hoặc tự động nhận diện (ví dụ: chân đế).

5. **Hoàn tác an toàn:**
   * Hỗ trợ đầy đủ tính năng hoàn tác (`Ctrl + Z`) trong Blender.

---

## Hướng dẫn cài đặt

1. Trong Blender, vào **Edit > Preferences > Add-ons**.
2. Nhấp vào nút **Install...** (hoặc mũi tên ở góc phải trên các phiên bản mới) và chọn file `snap_aligner.py`.
3. Tìm kiếm **"Snap Similar Parts"** trong danh sách và tích chọn để kích hoạt.
4. Mở thanh Sidebar trong 3D Viewport (phím **N**) và chọn tab **`Snap Tool`** để sử dụng.

---

## Cách sử dụng

### Cách 1: Phân nhóm thủ công (Khuyên dùng cho mô hình phức tạp)
1. Quét chọn toàn bộ các bộ phận của mô hình nguyên vẹn -> Nhấp **Gốc (Targets)** trên panel.
2. Quét chọn toàn bộ các bộ phận của mô hình bị rã rời -> Nhấp **Rã (Sources)** trên panel.
3. Chọn chế độ căn chỉnh (Ví dụ: `Snap trực tiếp` hoặc `Lắp ráp tại chỗ`).
4. Nhấp **Căn chỉnh ngay**.

### Cách 2: Tự động phân chia (Dành cho trường hợp đơn giản)
1. Quét chọn tất cả các đối tượng của cả 2 mô hình.
2. Trên panel, chọn trục phân chia (mặc định là Trục X).
3. Nhấp **Căn chỉnh ngay**.
