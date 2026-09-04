# 01. User Authentication & Role-Based Access Control (Admin vs QA)

Status: ready-for-agent

## Parent
.scratch/admin-portal-enhancement/PRD.md

## What to build
Xây dựng phân hệ xác thực người dùng và phân quyền 2 vai trò (`Admin` và `QA`) xuyên suốt từ Backend đến Frontend:
- **Cơ sở dữ liệu & Backend:**
  - Bảng `users` (`id`, `username`, `password_hash`, `role`, `full_name`, `is_active`, `created_at`).
  - Khởi tạo (seed) sẵn 2 tài khoản mặc định: `admin` (role `admin`) và `qa` (role `qa`).
  - Endpoint đăng nhập `POST /auth/login` tiếp nhận `username` và `password`, trả về auth token và thông tin user/role.
  - Endpoint `GET /auth/me` trả về thông tin người dùng hiện tại.
  - Middleware/Dependency bảo vệ các endpoint ghi/sửa/xóa/reprint: Nếu tài khoản có `role == 'qa'` thực hiện thao tác tạo/sửa/xóa Customer, Product, xóa Carton hoặc kích hoạt Reprint thì Backend chặn lại và trả về HTTP `403 Forbidden`.
- **Giao diện Frontend:**
  - Cập nhật `LoginPage.vue` tiếp nhận Username và Password, gọi API `/auth/login`, lưu token và role vào Auth store / Session.
  - Cập nhật `AdminLayout.vue` và `Sidebar.vue` hiển thị tên người dùng và huy hiệu vai trò (`Admin` hoặc `QA`), có nút Đăng xuất (Logout).
  - Tự động ẩn toàn bộ các nút hành động nhạy cảm (Thêm/Sửa/Xóa Customer, Thêm/Sửa/Xóa Product, Xóa Thùng, In lại Thùng) khi người dùng đăng nhập với vai trò `QA`.

## Acceptance criteria
- [x] Bảng `users` được khởi tạo với mật khẩu băm bảo mật, tự động seed tài khoản `admin` và `qa` khi khởi động nếu chưa tồn tại.
- [x] Đăng nhập với `username` và `password` sai trả về thông báo lỗi thích hợp; đăng nhập đúng trả về token và lưu phiên làm việc.
- [x] Tài khoản có vai trò `QA` khi gọi trực tiếp API tạo/sửa/xóa hoặc reprint qua HTTP client/curl bị chặn với mã lỗi `403 Forbidden`.
- [x] Giao diện `AdminLayout` hiển thị rõ vai trò hiện tại (`Admin` màu tím/xanh, `QA` màu xanh ngọc/xám).
- [x] Khi đăng nhập bằng `qa`, các trang Quản lý Khách hàng, Sản phẩm, Lịch sử chỉ ở chế độ xem; các nút "Add", "Edit", "Delete", "Reprint" bị ẩn hoàn toàn.
- [x] Đăng xuất xóa sạch phiên làm việc và điều hướng về trang đăng nhập.


## Blocked by
None - can start immediately
