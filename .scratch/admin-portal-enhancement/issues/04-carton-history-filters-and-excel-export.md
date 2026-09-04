# 04. Carton History Advanced Filtering & Dual-Level Excel Export

Status: completed

## Parent
.scratch/admin-portal-enhancement/PRD.md

## What to build
Nâng cấp trang Lịch sử đóng thùng (`CartonHistoryPage.vue`) với bộ lọc đa chiều và chức năng xuất báo cáo Excel chuyên nghiệp:
- **Backend API:**
  - Cập nhật endpoint `GET /cartons`: Bổ sung các query parameters:
    - `start_date` và `end_date` (định dạng `YYYY-MM-DD`).
    - `customer_id` (lọc theo khách hàng).
    - `job_order` (lọc theo mã công lệnh).
    - `po_number` (lọc theo số PO).
  - Tạo mới endpoint `GET /cartons/export`: Tiếp nhận toàn bộ các tham số lọc trên, cùng tham số `mode`:
    - `mode=summary` (Báo cáo tổng hợp cấp thùng): Xuất file `.xlsx` gồm các cột: STT, Mã Carton SN, Thời gian đóng, Khách hàng, Sản phẩm, Chế độ đóng gói, Job Order / PO, Lot#, Trọng lượng, Trạng thái (SUCCESS/FAILED), In lại (Có/Không), Trạm in.
    - `mode=detailed` (Bảng kê chi tiết sê-ri con - Traceability): Xuất file `.xlsx` gồm 2 sheet hoặc chi tiết từng dòng mã sê-ri con (`CartonItem.item_sn`) kèm Carton SN tương ứng, phục vụ đối soát giao hàng cho khách.
- **Giao diện Frontend (`CartonHistoryPage.vue`):**
  - Mở rộng thanh bộ lọc:
    - Date Range: Từ ngày - Đến ngày.
    - Dropdown chọn Khách hàng (Customer).
    - Ô nhập lọc theo Job Order / PO Number.
  - Thêm nút "Xuất Excel" (Export to Excel) với menu chọn:
    1. *Xuất Tổng hợp Thùng (Carton Summary)*
    2. *Xuất Bảng kê Chi tiết Sê-ri con (Detailed Traceability)*
  - Xử lý tải file trực tiếp về máy tính người dùng kèm chỉ báo loading khi đang kết xuất.
  - Phân quyền: Cả Admin và QA đều được phép lọc và xuất Excel. Quyền xóa thùng hoặc Reprint chỉ khả dụng cho tài khoản Admin (ẩn nút đối với QA).

## Acceptance criteria
- [x] Bộ lọc ngày tháng hoạt động chính xác, cho phép tra cứu thùng đóng trong bất kỳ khoảng thời gian nào.
- [x] Lọc kết hợp đa điều kiện (Khoảng ngày + Khách hàng + Sản phẩm + Trạng thái) trả về đúng tập dữ liệu tương ứng.
- [x] Xuất báo cáo `summary` tạo ra file Excel `.xlsx` mở được bình thường trên Microsoft Excel/WPS, đúng cấu trúc cột và định dạng dữ liệu.
- [x] Xuất báo cáo `detailed` bao gồm đầy đủ toàn bộ danh sách mã sê-ri con (`item_sn`) của từng thùng hàng.
- [x] Tài khoản QA xuất được báo cáo bình thường nhưng không nhìn thấy nút Xóa thùng hoặc In lại.

## Blocked by
.scratch/admin-portal-enhancement/issues/01-user-authentication-and-rbac.md
