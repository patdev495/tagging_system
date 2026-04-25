# ROADMAP.md

## Milestone 1: Foundation & Packing Station MVP
**Goal**: Build a functional packing station that can scan items, generate S/Ns, and record data to MSSQL 2008.
- [x] Phase 1-3: Completed

## Milestone 2: Feature-Based Architecture Refactoring (v2.0)
**Goal**: Modularize the codebase into feature-based modules.
- [x] Phase 11-14: Completed

---
## Milestone 3: Admin Dashboard & Statistics (v3.0)
**Goal**: Xây dựng hệ thống quản lý và thống kê dữ liệu toàn diện.

### Phase 21: Admin UI Shell & Navigation
**Goal**: Thiết lập khung giao diện Admin và hệ thống điều hướng.
**Requirements**: ADMIN-01, ADMIN-02
**Success Criteria**:
1. Có Sidebar cho phép chuyển đổi giữa "Packing Station" và "Admin Dashboard".
2. Hệ thống routing (Vue Router) hoạt động ổn định.
3. Giao diện khung (Layout) đồng nhất và hiện đại.

### Phase 22: Customer & Product Management
**Goal**: Triển khai các tính năng CRUD cho Khách hàng và Sản phẩm.
**Requirements**: DATA-01, DATA-02, DATA-04
**Success Criteria**:
1. Backend hỗ trợ các phương thức POST, PUT, DELETE cho Customer/Product.
2. Frontend có các form thêm/sửa và bảng danh sách.
3. Dữ liệu được cập nhật trực tiếp vào MSSQL 2008.

### Phase 23: Carton Explorer & Advanced Search
**Goal**: Quản lý lịch sử đóng gói và tra cứu chi tiết.
**Requirements**: DATA-03, DATA-04, STATS-03
**Success Criteria**:
1. Trang tra cứu Carton cho phép xem chi tiết nội dung (Item S/Ns) bên trong.
2. Công cụ tìm kiếm S/N sản phẩm hoạt động chính xác (tìm ra Carton chứa S/N đó).
3. Hiệu suất truy vấn SQL được tối ưu hóa cho dữ liệu lớn.

### Phase 24: Statistics Dashboard & Reports
**Goal**: Hiển thị báo cáo và đồ thị thống kê.
**Requirements**: ADMIN-03, STATS-01, STATS-02, STATS-04
**Success Criteria**:
1. Dashboard hiển thị các biểu đồ (Bar/Pie chart) về lượng carton theo sản phẩm.
2. Thống kê năng suất theo ngày/tháng được hiển thị trực quan.
3. Chức năng Export CSV/Excel hoạt động cho các báo cáo.

---
## Milestone 999: Backlog
- [ ] Auto-update product catalog from remote ERP if needed.
- [ ] Support for multiple locations (VN vs CN selection).
- [ ] Phân quyền người dùng chi tiết (RBAC).
