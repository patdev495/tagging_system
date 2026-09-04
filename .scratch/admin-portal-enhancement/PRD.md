# PRD: Nâng cấp Toàn diện Phân hệ Quản trị (Admin Portal Enhancement)

## 1. Bối cảnh & Mục tiêu
Phân hệ Quản trị (Admin) của hệ thống đóng gói và in tem NY Tagging System hiện tại còn đơn giản:
- Màn hình đăng nhập chỉ kiểm tra mật khẩu tĩnh `admin123` ở phía trình duyệt, không có kiểm soát quyền truy cập ở tầng API.
- Dashboard chỉ hiển thị các con số giả (mock data), không phản ánh tình trạng sản xuất thực tế.
- Thiếu hoàn toàn màn hình theo dõi tiến độ các Lệnh sản xuất (Job Order) và đợt đóng hàng theo cân (PO / Lot Runs).
- Lịch sử đóng thùng (Carton History) thiếu bộ lọc dải ngày, không có tính năng xuất báo cáo Excel cho kho/QC.
- Cấu hình file mẫu BarTender (`.btw`) còn nhập chuỗi thủ công, dễ phát sinh lỗi dừng chuyền.

Mục tiêu của đợt nâng cấp này là đưa phân hệ Admin thành trung tâm điều hành chuyên nghiệp cho xưởng đóng gói, hỗ trợ phân quyền rõ ràng giữa **Admin** (toàn quyền) và **QA** (chỉ đọc & xuất báo cáo), cung cấp dữ liệu sản xuất thời gian thực và công cụ đối soát dữ liệu mạnh mẽ.

---

## 2. Các Phân hệ Cốt lõi

### 2.1. Phân quyền Người dùng (RBAC: Admin vs QA)
- Quản lý tài khoản trong bảng `users` với 2 vai trò: `Admin` và `QA`.
- API Backend kiểm soát quyền hạn nghiêm ngặt qua token/session (trả về `403 Forbidden` đối với các thao tác ghi/xóa/reprint của tài khoản QA).
- Frontend hiển thị thông tin người dùng, tự động ẩn các nút thao tác nhạy cảm khi đăng nhập bằng tài khoản QA.

### 2.2. Dashboard Vận hành Thời gian thực (Real-time Dashboard)
- Hiển thị các chỉ số KPI: Tổng thùng thành công/thất bại/reprint, tổng sản phẩm con, tỷ lệ lỗi in và tỷ lệ reprint.
- Biểu đồ sản lượng theo từng khung giờ trong ca (Hourly Throughput).
- Biểu đồ tỷ trọng sản lượng theo từng sản phẩm.
- Live feed 15 thùng đóng gần nhất và widget giám sát trạng thái BarTender COM Engine / Máy in.

### 2.3. Quản lý Đợt Sản Xuất (Job Orders & Production Runs)
- **Tab Job Orders (cho `item_scan` / Khách hàng UI):** Theo dõi danh sách lệnh, thanh tiến độ %, trạng thái các slot (PENDING, SCANNED, shipped).
- **Tab PO / Lot Runs (cho `weight_scale` / Khách hàng A11):** Thống kê sản lượng theo từng cặp PO Number & Lot Number, tổng khối lượng đã cân.

### 2.4. Báo cáo & Xuất dữ liệu Excel (Reporting & Data Export)
- Bộ lọc đa chiều: Từ ngày - Đến ngày, Khách hàng, Sản phẩm, Job Order / PO Number, Trạng thái.
- Xuất file Excel (`.xlsx`):
  1. Báo cáo tổng hợp cấp thùng (Carton Summary).
  2. Bảng kê chi tiết sê-ri con (Traceability Report) phục vụ kiểm định và bàn giao.

### 2.5. Chuẩn hóa Quản lý Mẫu tem BarTender (Template Management)
- Dropdown chọn file `.btw` từ thư mục template chuẩn trên server (`resources/templates/`).
- Công cụ kiểm tra hợp lệ đường dẫn template và chẩn đoán/khởi động lại BarTender COM Engine.

---

## 3. Danh sách Implementation Issues
- `01-user-authentication-and-rbac.md`
- `02-real-time-operational-dashboard.md`
- `03-production-runs-and-job-order-tracking.md`
- `04-carton-history-filters-and-excel-export.md`
- `05-normalized-template-management-and-diagnostics.md`
