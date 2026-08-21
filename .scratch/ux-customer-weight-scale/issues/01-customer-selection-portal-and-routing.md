# 01. Customer Selection Portal & Route Isolation

Status: ready-for-agent

## What to build
Xây dựng màn hình chọn Khách hàng tại trang chủ (`/`) và phân luồng điều hướng:
- Khi truy cập `/`, nếu chưa có khách hàng ghi nhớ trong `localStorage`, hiển thị Cổng chọn Khách hàng với 2 tùy chọn trực quan:
  - **Khách hàng UI**: Điều hướng sang `/packing/ui` (giữ nguyên 100% mã nguồn và giao diện quét công lệnh hiện tại).
  - **Khách hàng UX**: Điều hướng sang `/packing/ux` (giao diện đóng gói theo cân của khách hàng UX).
- Trên thanh Header của cả 2 màn hình, bổ sung nút bấm *"Đổi khách hàng"* để cho phép quay lại màn hình chọn bất kỳ lúc nào.
- Trình duyệt lưu lựa chọn gần nhất vào `localStorage` của máy trạm để tự động vào thẳng giao diện đóng hàng khi tải lại trang.

## Acceptance criteria
- [x] Truy cập `/` hiển thị màn hình chọn Khách hàng `UI` và `UX` nếu chưa chọn lần nào.
- [x] Chọn `UI` điều hướng sang `/packing/ui`, đảm bảo toàn bộ luồng quét Job Order, slot thùng và quét serial con hoạt động nguyên vẹn.
- [x] Chọn `UX` điều hướng sang `/packing/ux`.
- [x] Nút *"Đổi khách hàng"* ở Header xóa cache chọn và đưa người dùng về màn hình chọn khách hàng.
- [x] Reload trang (F5) tự động giữ nguyên trạm khách hàng đã chọn trước đó.

## Blocked by
None - can start immediately
