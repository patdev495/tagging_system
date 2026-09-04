# 02. Real-time Operational Dashboard (KPIs, Hourly Throughput & Live Feed)

Status: ready-for-agent

## Parent
.scratch/admin-portal-enhancement/PRD.md

## What to build
Xây dựng Dashboard giám sát vận hành đóng gói thời gian thực thay thế toàn bộ số liệu giả lập hiện tại:
- **Backend API:**
  - Endpoint `GET /admin/dashboard/stats` với tham số lọc thời gian (`time_range`: `today`, `7d`, `30d`, mặc định là `today` tính theo giờ cục bộ của server).
  - Trả về dữ liệu tổng hợp:
    1. **Chỉ số KPI chính:** Tổng số thùng đã đóng (`total_cartons`), số thùng thành công (`success_cartons`), số thùng lỗi (`failed_cartons`), số thùng in lại (`reprint_cartons`), tổng số sản phẩm con (`total_items`), tỷ lệ lỗi (`error_rate_%`), tỷ lệ in lại (`reprint_rate_%`).
    2. **Sản lượng theo giờ (Hourly Throughput):** Phân bổ số lượng thùng qua các khung giờ trong ngày (từ 06:00 đến 22:00).
    3. **Tỷ trọng theo sản phẩm (Product Breakdown):** Top các sản phẩm đóng nhiều nhất.
    4. **Dòng dữ liệu đóng gói trực tiếp (Live Feed):** 15 thùng đóng gần nhất (Carton SN, Product Name, Customer Code, Thời gian đóng, Trọng lượng, Trạng thái SUCCESS/FAILED, Trạm in).
- **Giao diện Frontend (`DashboardPage.vue`):**
  - Thanh trên: Bộ chọn dải thời gian (Hôm nay / 7 ngày qua / Tháng này) + Nút "Làm mới dữ liệu" (Refresh).
  - Khối KPI: 4 thẻ thống kê trực quan với màu sắc tương ứng (Xanh lá cho thành công, Đỏ cho lỗi, Vàng cam cho in lại, Xanh dương cho sản phẩm con).
  - Khối Biểu đồ:
    - Biểu đồ thanh (Bar Chart) thể hiện sản lượng theo từng giờ trong ca làm việc.
    - Biểu đồ phân bổ theo sản phẩm/khách hàng.
  - Khối Widget Kỹ thuật: Hiển thị tình trạng BarTender COM Engine (Ready / Error) và số lượng máy in đang online.
  - Khối Live Feed: Bảng danh sách 15 thùng mới đóng gần nhất với badge trạng thái nhấp nháy/sinh động.

## Acceptance criteria
- [ ] Truy cập trang Dashboard hiển thị 100% số liệu thực từ cơ sở dữ liệu thay cho số liệu giả lập.
- [ ] Thẻ KPI hiển thị chính xác tổng số thùng, phân loại thành công / thất bại / in lại và tổng số sản phẩm con đóng gói.
- [ ] Biểu đồ phân bổ theo giờ thể hiện đúng khung giờ sản xuất thực tế trong ngày theo giờ địa phương của nhà máy.
- [ ] Bảng Live Feed hiển thị đúng các thùng vừa được quét/in từ các trạm, cập nhật dữ liệu ngay khi bấm nút Refresh.
- [ ] Widget trạng thái BarTender hiển thị chính xác tình trạng kết nối của engine.
- [ ] Cả tài khoản Admin và QA đều có quyền truy cập và xem dữ liệu đầy đủ trên trang này.

## Blocked by
.scratch/admin-portal-enhancement/issues/01-user-authentication-and-rbac.md
