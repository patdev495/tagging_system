# 06. Unified History & Reprint Support for UX Cartons

Status: ready-for-agent

## What to build
Tích hợp tra cứu lịch sử và In lại (Reprint) cho các thùng hàng thuộc khách hàng UX:
- Trang Lịch sử & In lại (`/admin/history` hoặc Modal Reprint trên giao diện đóng hàng) chấp nhận mã sê-ri thùng của cả 2 khách hàng:
  - Khách hàng UI: `CN...`
  - Khách hàng UX: `VHK...`
- Khi thực hiện Reprint cho một Carton UX:
  - Backend nhận diện `template_type = "a11"`.
  - Tái tạo dữ liệu in giữ nguyên: `Carton SN`, `PO Number`, `Lot Number`, `Date Code`, `Weight`, `Origin`.
  - Đánh dấu cờ `is_reprint = 1` mà không làm tăng số nhảy tự động của lô hàng.
  - Gửi lệnh in đúng template `a11`.

## Acceptance criteria
- [x] Tra cứu mã thùng UX (VD: `VHK00102372608000081`) hiển thị đầy đủ thông tin số cân, PO, LOT, ngày giờ in.
- [x] Thực hiện Reprint in ra đúng mẫu tem A11 với thông tin nguyên bản.
- [x] Không làm sai lệch hay nhảy số thứ tự tự tăng của năm hiện tại.


## Blocked by
- `.scratch/ux-customer-weight-scale/issues/04-ux-yearly-sn-allocator-and-a11-btxml-generator.md`
- `.scratch/ux-customer-weight-scale/issues/05-ux-packing-station-view-and-tolerance-gate.md`
