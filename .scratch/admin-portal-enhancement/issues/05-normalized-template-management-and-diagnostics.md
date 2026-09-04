# 05. Normalized Template Management & BarTender Diagnostic Tooling

Status: completed

## Parent
.scratch/admin-portal-enhancement/PRD.md

## What to build
Chuẩn hóa cách thức quản lý file mẫu in BarTender (`.btw`) và bổ sung công cụ chẩn đoán/phục hồi BarTender Engine trực tiếp trên giao diện Admin:
- **Backend API:**
  - Endpoint `GET /print/templates`: Quét thư mục template chuẩn của server (`resources/templates/`) và thư mục gốc, trả về danh sách các file `.btw` khả dụng kèm kích thước và ngày cập nhật.
  - Endpoint `POST /print/validate-template`: Tiếp nhận tên file template, kiểm tra sự tồn tại của file và kiểm tra khả năng mở định dạng nhãn qua BarTender COM Engine.
  - Endpoint `POST /print/restart-engine`: Thực hiện kill tiến trình `bartend.exe` nếu bị treo và khởi động lại kết nối COM một cách an toàn.
- **Giao diện Frontend:**
  - Cập nhật modal thêm/sửa sản phẩm trên `ProductManagementPage.vue`:
    - Thay thế ô nhập text tự do của `template_path` bằng Dropdown chọn file `.btw` từ danh sách trả về từ `/print/templates`.
    - Thêm nút "Kiểm tra file" (Check File): Kiểm tra xem file có hợp lệ và đọc được không, hiển thị badge xanh/đỏ tức thì.
  - Thêm khu vực "Chẩn đoán Thiết bị & BarTender" (Device & Engine Diagnostics) trong phần Cài đặt Admin:
    - Hiển thị trạng thái kết nối BarTender Engine.
    - Danh sách máy in khả dụng được phát hiện bởi hệ điều hành.
    - Nút "Khởi động lại BarTender Engine" (Restart COM Engine) cho phép Admin phục hồi nhanh khi xảy ra lỗi kẹt lệnh in.
  - Phân quyền: Thao tác sửa sản phẩm và khởi động lại engine chỉ khả dụng cho tài khoản `Admin`.

## Acceptance criteria
- [x] Giao diện cấu hình Product hiển thị dropdown danh sách các file `.btw` thực tế có trên hệ thống, không còn phải gõ đường dẫn thủ công.
- [x] Bấm "Kiểm tra file" phản hồi chính xác trạng thái tồn tại và tính hợp lệ của mẫu tem.
- [x] Bấm nút "Khởi động lại BarTender Engine" gọi API giải phóng tiến trình kẹt thành công và tái lập kết nối COM mà không làm sập server Backend.
- [x] Tài khoản `QA` chỉ xem thông tin cấu hình sản phẩm, các nút chỉnh sửa/lưu và nút khởi động lại engine đều bị vô hiệu hóa hoặc ẩn đi.

## Blocked by
.scratch/admin-portal-enhancement/issues/01-user-authentication-and-rbac.md
