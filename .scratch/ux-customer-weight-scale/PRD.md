# PRD: Khách Hàng UX & Quy Trình Đóng Gói Theo Cân (Weight-Based Packaging)

## 1. Mục tiêu (Objective)
Mở rộng hệ thống NY Tagging hỗ trợ đa khách hàng (Multi-Customer) với 2 chế độ đóng gói song song:
1. **Khách hàng UI** (Hiện tại): Đóng gói theo chế độ quét sê-ri con (`item_scan`), cấp phát slot theo Job Order, reset sê-ri hàng tháng.
2. **Khách hàng UX** (Mới): Đóng gói theo cân trọng lượng (`weight_scale`), không quét mã con, reset sê-ri hàng năm, in tem tiêu chuẩn A11 (3" x 5") với 7 mã vạch 1D và 1 mã QR 2D.

## 2. Cam Kết An Toàn Dữ Liệu (Zero-Impact Safety Invariant)
- **100% dữ liệu cũ không bị ảnh hưởng**: Mọi thay đổi schema là Additive (chỉ thêm cột nullable/default, không xóa, không sửa kiểu dữ liệu hiện có).
- **100% luồng UI giữ nguyên**: Route `/packing/ui` bảo toàn toàn bộ logic quét công lệnh, đệm quét serial con, phân bổ slot, và mẫu in `carton.ui.btw`.

## 3. Kiến Trúc Giải Pháp (Architecture)
- **Frontend**: Cổng chọn khách hàng tại `/` chuyển tiếp tới `/packing/ui` hoặc `/packing/ux`.
- **Print Agent**: Nhúng `SerialEngine` đọc cân RS-232 và Win32 `RegisterHotKey` (`F9`).
- **Backend**: Áp dụng Strategy Pattern cho `CartonSNAllocator` (Yearly reset) và `BTXMLDocument` (A11 format).

## 4. Tài Liệu Kỹ Thuật Tham Chiếu
- [CONTEXT.md](../../CONTEXT.md)
- [docs/customer_ux_label_spec.md](../../docs/customer_ux_label_spec.md)
- [docs/weighing_scale_integration.md](../../docs/weighing_scale_integration.md)
- [docs/adr/0001-multi-customer-weight-scale-architecture.md](../../docs/adr/0001-multi-customer-weight-scale-architecture.md)
