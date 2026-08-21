# 05. UX Packing Station View & Tolerance Gatekeeper

Status: ready-for-agent

## What to build
Xây dựng giao diện đóng gói theo cân hoàn chỉnh cho khách hàng UX tại route `/packing/ux`:
- **Khởi tạo phiên đóng hàng**:
  - Modal chọn 1 trong 3 sản phẩm (`840-00083`, `840-00091`, `840-00092`).
  - Modal nhập `PO Number` và `Lot Number` cho đợt đóng hàng.
- **Trạm cân thời gian thực (Live Weight Gauge)**:
  - Polling hoặc kết nối nhận dữ liệu liên tục từ Print Agent (`GET /scale/current`).
  - Hiển thị số cân to rõ kèm dải chuẩn `[Min, Target, Max]`.
  - Hiển thị trạng thái màu trực quan:
    - **Xanh lá**: Đủ cân và ổn định ➔ Nút In sáng, sẵn sàng in.
    - **Vàng**: Cân đang dao động / Chưa ổn định.
    - **Đỏ**: Thừa cân / Thiếu cân ➔ Nút In bị khóa, cảnh báo âm thanh/visual.
- **Kích hoạt in**:
  - Nhấn `F9` (hoặc Click "Cân & In Tem"):
    - Gọi API `/api/v1/carton/weigh-pack`.
    - Gửi XML nhận được tới Print Agent `/print`.
    - Nhận phản hồi in thành công ➔ Tăng bộ đếm *"Đã đóng X thùng trong phiên này"*.
- **Điều khiển phiên**:
  - Nút *"Đổi PO / LOT"* và *"Đổi sản phẩm"* cho phép chuyển lô nhanh chóng mà không cần tải lại trang.

## Acceptance criteria
- [x] Giao diện `/packing/ux` hiển thị đồng hồ cân thời gian thực cập nhật mượt mà.
- [x] Khi cân chưa đủ trọng lượng quy chuẩn (190 con), nút in bị vô hiệu hóa và phím `F9` bị chặn.
- [x] Khi cân đạt chuẩn và ổn định, nhấn `F9` kích hoạt in tem A11 ngay lập tức.
- [x] Bộ đếm thùng đóng trong phiên hiển thị chính xác và cập nhật sau mỗi lần in thành công.
- [x] Công nhân có thể đổi PO/LOT hoặc đổi mã sản phẩm bất kỳ lúc nào.


## Blocked by
- `.scratch/ux-customer-weight-scale/issues/01-customer-selection-portal-and-routing.md`
- `.scratch/ux-customer-weight-scale/issues/03-print-agent-scale-rs232-and-hotkey-engine.md`
- `.scratch/ux-customer-weight-scale/issues/04-ux-yearly-sn-allocator-and-a11-btxml-generator.md`
