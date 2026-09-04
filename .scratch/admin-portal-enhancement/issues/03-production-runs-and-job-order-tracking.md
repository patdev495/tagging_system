# 03. Production Runs & Job Order Progress Tracking

Status: closed

## Parent
.scratch/admin-portal-enhancement/PRD.md

## What to build
Xây dựng phân hệ Quản lý Đợt Sản Xuất mới (`/admin/production-runs`) trên thanh điều hướng Admin, tích hợp theo dõi tiến độ đóng gói theo 2 chế độ:
- **Backend API:**
  - Endpoint `GET /admin/production-runs/job-orders`: Liệt kê danh sách các **Job Order** đã cấp phát slot trong hệ thống, bao gồm: Mã Job Order, Tên sản phẩm, Tổng số slot, Số slot đã quét (`SCANNED`), Số slot chờ (`PENDING`), Số slot đã xuất kho (`shipped`), Tỷ lệ hoàn thành (%).
  - Endpoint `GET /admin/production-runs/job-orders/{job_order}/slots`: Trả về danh sách chi tiết các **Job Order Carton Slot** từ 1 đến N kèm mã Carton SN và thời gian quét.
  - Endpoint `GET /admin/production-runs/po-runs`: Liệt kê danh sách các đợt đóng hàng theo cặp `PO Number` và `Lot Number` (chế độ `weight_scale`), bao gồm: PO Number, Lot Number, Mã sản phẩm, Date Code, Tổng số thùng đã cân đóng, Tổng khối lượng (kg), Thùng đóng gần nhất.
- **Giao diện Frontend (`ProductionRunsPage.vue`):**
  - Thêm mục "Production Runs" (hoặc "Lệnh Sản Xuất") vào `Sidebar.vue` với biểu đồ tiến độ.
  - Giao diện gồm 2 Tab rõ ràng:
    - **Tab 1 - Job Orders (Khách hàng UI / `item_scan`):**
      - Bảng danh sách các Job Order với thanh Progress Bar trực quan thể hiện tiến độ (ví dụ: `85/100 thùng - 85%`).
      - Nút "Xem chi tiết Slots": Mở Drawer/Modal hiển thị danh sách toàn bộ các slot thùng từ 1 đến N, đánh dấu màu trực quan (`PENDING` màu xám, `SCANNED` màu xanh lá, `shipped` màu xanh dương).
    - **Tab 2 - PO / Lot Runs (Khách hàng A11 / `weight_scale`):**
      - Bảng thống kê các đợt đóng hàng theo PO & Lot, hiển thị tổng thùng, tổng cân nặng và thời điểm đóng gần nhất.

## Acceptance criteria
- [x] Bổ sung route `/admin/production-runs` và mục điều hướng tương ứng trên thanh Sidebar.
- [x] Tab Job Orders hiển thị đầy đủ danh sách các công lệnh đang hoặc đã chạy, tính toán chính xác số lượng slot đã quét so với tổng slot.
- [x] Nhấp xem chi tiết Job Order hiển thị chính xác toàn bộ vị trí thùng (Slot 1..N), trạng thái và mã Carton SN tương ứng.
- [x] Tab PO / Lot Runs gom nhóm chính xác các thùng thuộc cùng cặp PO Number & Lot Number kèm tổng khối lượng thực tế.
- [x] Cả Admin và QA đều có thể xem và tra cứu dữ liệu trên màn hình này.


## Blocked by
.scratch/admin-portal-enhancement/issues/01-user-authentication-and-rbac.md
