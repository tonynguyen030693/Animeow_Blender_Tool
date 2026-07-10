# Nâng Cấp UI/UX Maya Toolboard v02 — Phong Cách AnimBot

Thiết kế lại toàn bộ giao diện và bộ icon của Animeow Maya Toolboard v02 (Python 3) lấy cảm hứng từ AnimBot — plugin animation chuyên nghiệp hàng đầu cho Maya.

## Phân Tích Thiết Kế AnimBot vs Hiện Tại

### AnimBot (Mẫu tham khảo):
- **Nền tối chuyên nghiệp** `#3C3C3C` → `#4A4A4A` (xám ấm, không quá tối)
- **Icon vector phẳng** (flat design), **monochrome xanh lá** `#6ABF4B` trên nền trong suốt
- **Bố cục dạng danh sách dọc** — mỗi hàng gồm: icon nhỏ (20-24px) + text label ngang hàng
- **Font** sạch sẽ, không in đậm, khoảng cách giữa các mục đều đặn
- **Không có GroupBox viền cứng** — các nhóm phân tách bằng separator mỏng hoặc khoảng trắng
- **Scrollbar siêu mỏng** khớp với nền
- **Không có emoji/icon 3D lòe loẹt** — tất cả đều tinh tế, chuyên nghiệp

### Animeow Hiện tại:
- **Nền** `#2D2D2D` (quá tối)
- **Icon 3D Clay Render** rất cute nhưng **quá to** (600KB+/icon) và phong cách cartoon, không hợp với công cụ chuyên nghiệp cho animator
- **GroupBox viền cứng** với title màu cyan `#00BCD4`
- **Emoji Unicode** làm tab icon (🔗📈🎯🎬🚀) — không chuyên nghiệp
- **Nút bấm viền cứng** với padding to

---

## User Review Required

> [!IMPORTANT]
> **Lựa chọn màu chủ đạo (Accent Color):**
> AnimBot dùng **xanh lá** (`#6ABF4B`). Animeow hiện dùng **cyan** (`#00BCD4`).
> Plan này đề xuất chuyển sang **xanh lá tươi** giống AnimBot để tạo cảm giác chuyên nghiệp hơn.
> Nếu bạn muốn giữ cyan hoặc dùng màu khác, hãy cho tôi biết.

> [!IMPORTANT]
> **Về bộ icon 3D Clay hiện tại trên Shelf Maya:**
> Plan này sẽ tạo bộ icon **SVG-style mới** (flat, monochrome, chuyên nghiệp) cho giao diện **bên trong Toolboard** (QPushButton, QGroupBox title...). 
> Bộ icon 3D Clay trên **Shelf Maya** (thanh ngang phía trên viewport) sẽ **được giữ nguyên** vì Shelf sử dụng ảnh PNG riêng biệt.
> Nếu bạn muốn thay icon trên Shelf Maya luôn, hãy xác nhận.

> [!WARNING]
> **Đây là thay đổi toàn diện file `window.py` (3489 dòng).** Logic code sẽ không thay đổi, chỉ thay đổi:
> - QSS stylesheet
> - Layout spacing/margins
> - Widget styling (GroupBox → Section header)
> - Icon rendering (emoji → QPainter SVG-path icons)

---

## Proposed Changes

### Phase 1: Thiết Kế Hệ Thống Design System Mới (QSS Overhaul)

#### [MODIFY] [window.py](file:///e:/AI_Work/Blender_Maya_Script/Maya_script_2022_python_3/animeow_maya_toolboard_v02/ui/window.py)

**1.1 — Bảng Màu Mới (Color Palette)**

```python
# AnimBot-inspired Professional Color Palette
COLORS = {
    "bg_primary":    "#3C3C3C",   # Nền chính (ấm hơn)
    "bg_secondary":  "#333333",   # Nền phụ (panels, inputs)
    "bg_tertiary":   "#2B2B2B",   # Nền sâu (scroll area)
    "bg_hover":      "#4A4A4A",   # Hover state
    "bg_pressed":    "#2A2A2A",   # Pressed state
    "accent":        "#6ABF4B",   # Xanh lá chủ đạo (AnimBot green)
    "accent_hover":  "#7DD35C",   # Accent hover
    "accent_dim":    "#4A8A35",   # Accent mờ (disabled)
    "text_primary":  "#D4D4D4",   # Text chính
    "text_secondary":"#999999",   # Text phụ/label
    "text_accent":   "#6ABF4B",   # Text highlight
    "border":        "#4A4A4A",   # Viền nhẹ
    "separator":     "#444444",   # Đường kẻ phân tách
    "danger":        "#E04848",   # Nút xóa/nguy hiểm
    "warning":       "#E0A030",   # Cảnh báo
}
```

**1.2 — QSS Stylesheet Toàn Diện**

Thay thế hoàn toàn `QSS_STYLE` hiện tại bằng stylesheet mới:

- **QWidget**: Nền `#3C3C3C`, font `Segoe UI` 11px (nhỏ hơn 1px), không bold mặc định
- **QPushButton**: Nền `#4A4A4A`, border `1px solid #555`, border-radius `4px`, padding `5px 10px`. Hover: border-color accent, text sáng hơn. Pressed: nền tối hơn
- **QPushButton#accent_btn**: Nền gradient nhẹ từ `#5AAF3B` → `#6ABF4B`, text trắng
- **QGroupBox**: **Bỏ viền cứng** → border: none, chỉ dùng title làm section header (text xanh lá `#6ABF4B`, font-weight bold, font-size 11px, kẻ gạch dưới mỏng `1px solid #444`)
- **QTabBar::tab**: Nền trong suốt, text `#888`. Selected: text `#6ABF4B`, bottom border `2px solid #6ABF4B`. Hover: text trắng
- **QTabWidget::pane**: Border top `1px solid #444` — tinh tế
- **QLineEdit, QComboBox, QSpinBox**: Nền `#2E2E2E`, border `1px solid #444`, border-radius `3px`. Focus: border `#6ABF4B`
- **QCheckBox**: Indicator `14x14`, nền `#2E2E2E`, checked: nền `#6ABF4B` + checkmark trắng
- **QScrollBar:vertical**: Width `6px`, handle `#555`, handle:hover `#6ABF4B`
- **QSlider**: Groove `#2E2E2E`, handle `#6ABF4B` 10x10 circle

**1.3 — Bỏ Emoji, Thay Bằng Text Icon Chuyên Nghiệp**

Thay thế emoji tab title:
- `"🔗 Space & Bake  "` → `"Space & Bake"`
- `"📈 Curve & Motion  "` → `"Curve & Motion"`
- `"🎯 Rig & Mirror  "` → `"Rig & Mirror"`
- `"🎬 Output & Scene  "` → `"Output & Scene"`
- `"🚀 Launchers  "` → `"Launchers"`

**1.4 — GroupBox → Section Headers**

Chuyển GroupBox sang kiểu section header phẳng:
- **Trước**: GroupBox viền cứng bo tròn + title cyan nổi
- **Sau**: Không viền, title là text `#6ABF4B` bold 11px + separator ngang `1px solid #444` bên dưới + padding-top nhỏ gọn

**1.5 — Header Bar Mới**

- Bỏ title `ANIMEOW TOOLBOARD v5.0` dạng label to
- Thay bằng thanh header nhỏ gọn: icon nhỏ (text "A") + version nhỏ + nút compact toggle gọn hơn
- Tổng chiều cao header ≤ 24px

**1.6 — Nút Bấm Gọn Hơn**

- Giảm `fixedHeight` từ `28-30px` xuống `24-26px`
- Giảm padding ngang
- Viền nhạt hơn, chỉ highlight khi hover

---

### Phase 2: Tạo Bộ Icon SVG-Path Inline (Không Cần File Ngoài)

#### [MODIFY] [window.py](file:///e:/AI_Work/Blender_Maya_Script/Maya_script_2022_python_3/animeow_maya_toolboard_v02/ui/window.py)

Tạo class `AnimeowIcons` sử dụng `QPainter` + `QPainterPath` để vẽ icon vector trực tiếp trong code Python, không cần file ảnh bên ngoài. Mỗi icon là hàm tĩnh trả về `QIcon` hoặc `QPixmap`:

```python
class AnimeowIcons:
    """Bộ icon SVG-path inline phong cách AnimBot"""
    ACCENT = QColor("#6ABF4B")
    
    @staticmethod
    def link_icon(size=20):
        """Icon mắt xích (Smart Link)"""
        # Vẽ 2 vòng tròn liên kết bằng QPainterPath
        ...
    
    @staticmethod
    def bake_icon(size=20):
        """Icon lò nướng nhỏ (Bake)"""
        ...
    
    @staticmethod  
    def curve_icon(size=20):
        """Icon đường cong S (Curve)"""
        ...
    
    @staticmethod
    def key_icon(size=20):
        """Icon chìa khóa (Keyframe)"""
        ...
    
    @staticmethod
    def mirror_icon(size=20):
        """Icon gương phản chiếu (Mirror)"""
        ...
    
    # ... ~15-20 icon cho các chức năng chính
```

Danh sách icon cần vẽ (ước lượng):
1. **link** — 2 mắt xích lồng nhau
2. **bake** — hình vuông có sóng nhiệt
3. **curve** — đường cong S mượt
4. **key** — hình thoi (keyframe diamond)
5. **mirror** — 2 mũi tên đối xứng
6. **play** — tam giác play
7. **arc** — đường cong 3 chấm motion trail
8. **round** — hình tròn với số thập phân
9. **constraint** — ổ khóa + mũi tên
10. **pivot** — chữ thập tâm xoay
11. **euler** — biểu tượng xoay 3D
12. **star** — ngôi sao (favorite)
13. **graph** — biểu đồ sóng (graph editor)
14. **folder** — thư mục
15. **shield** — khiên (antivirus)
16. **save** — đĩa mềm
17. **reset** — mũi tên xoay vòng
18. **clean** — chổi quét
19. **tween** — 2 chấm tròn nối nhau (interpolation)
20. **world** — quả cầu (world space)

Tất cả icon đều:
- **Monochrome** xanh lá `#6ABF4B`
- **Kích thước** 20x20px (cho nút), 16x16px (cho label)
- **Nét vẽ** 1.5-2px, bo tròn đầu nét

---

### Phase 3: Tối Ưu Layout & Spacing

#### [MODIFY] [window.py](file:///e:/AI_Work/Blender_Maya_Script/Maya_script_2022_python_3/animeow_maya_toolboard_v02/ui/window.py)

- **Giảm margins** của `tab_layout.setContentsMargins` từ `(6, 10, 6, 6)` → `(4, 6, 4, 4)`
- **Giảm spacing** giữa các widget từ `10px` → `6px`
- **Nút bấm compact hơn**: `fixedHeight 24px`, padding `4px 8px`
- **Input fields nhỏ hơn**: padding `3px 5px`
- **Compact toolbar icons**: sử dụng icon vector thay emoji

---

### Phase 4: Đồng Bộ Sang Python 2

#### [MODIFY] [window.py](file:///e:/AI_Work/Blender_Maya_Script/Maya_script_2020_python_2/animeow_maya_toolboard/ui/window.py)

Sau khi hoàn thành Phase 1-3, sao chép và điều chỉnh tương thích Python 2 cho bản `Maya_script_2020_python_2`.

---

## Open Questions

> [!IMPORTANT]
> **1. Màu accent**: Bạn muốn giữ **cyan (#00BCD4)** hiện tại hay chuyển sang **xanh lá (#6ABF4B)** giống AnimBot? Hoặc một màu khác?

> [!IMPORTANT]
> **2. Icon trên Shelf Maya**: Có muốn thay bộ icon 3D Clay trên thanh Shelf Maya bằng bộ icon flat mới không? Hay chỉ thay icon bên trong giao diện Toolboard?

> [!NOTE]
> **3. Compact toolbar bên trái**: AnimBot không có sidebar — họ dùng menu dropdown. Bạn có muốn giữ compact toolbar sidebar hay bỏ?

> [!NOTE]
> **4. GroupBox**: AnimBot dùng flat section headers (chỉ text + separator). Bạn ok với việc bỏ hoàn toàn viền GroupBox?

---

## Verification Plan

### Manual Verification
1. Mở Maya 2022+, load Toolboard v02, kiểm tra giao diện mới
2. So sánh trực quan với screenshot AnimBot
3. Kiểm tra tất cả icon hiển thị đúng
4. Test hover/pressed states trên các nút
5. Test standalone windows (ATB, Bake, Curve, Arc, Round, Fav)
6. Kiểm tra compact mode toggle
7. Kiểm tra scrollbar ở các tab dài
