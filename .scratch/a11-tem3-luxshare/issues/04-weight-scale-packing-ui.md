# Issue 04: Tích Hợp Giao Diện Cân Đóng Gói A11 & Kiểm Thử Toàn Trình (E2E)
Status: completed

## What to build
Tích hợp giao diện cân đóng gói và hoàn thiện kiểm thử toàn trình cho Tem 3:
1. Giao diện cân `A11PackingPage.vue` và các composable (`useA11SerialNumber.ts`, `useWeighAndPrint.ts`):
   - Khi chọn mã hàng có `template_type == "a11_tem3"`, hiển thị định dạng sê-ri dự kiến dạng `1012665{YYMMDD}xxxx`.
   - Bỏ qua popup bắt buộc nhập Batch PO (cho phép để rỗng như Tem 2).
   - Lot Number điền sẵn mặc định và cho phép bấm sửa trực tiếp trên giao diện.
   - Hiển thị chỉ dẫn SOP: Không in lại tem cũ, tem lỗi nhấn F9 để cấp sê-ri tiếp theo.
2. Kiểm soát cấm Reprint:
   - Đảm bảo endpoint in lại trả về lỗi từ chối khi gọi với Carton thuộc `a11_tem3` theo đúng `ADR-0005`.
3. Kiểm thử toàn trình (End-to-End integration test):
   - Mô phỏng luồng: Chọn sản phẩm Tem 3 -> Đặt thùng hàng lên cân (giả lập cân đạt chuẩn) -> Nhấn F9 -> Backend cấp phát `1012665{YYMMDD}0001` -> Sinh BTXML -> Gửi sang Print Agent / BarTender COM -> Ghi nhận bản ghi Carton thành công trong History.

## Acceptance criteria
- [ ] Giao diện trạm cân đóng gói A11 hiển thị đúng thông tin mã thùng Tem 3 và cho phép thông luồng không bị chặn bởi PO.
- [ ] Lệnh in F9 sinh tem in đầy đủ các trường và mã QR quét được nội dung chuẩn xác.
- [ ] Hành động Reprint bị chặn 100% ở cả UI và Backend API.
- [ ] Toàn bộ bộ test tự động của backend (`pytest`) chạy xanh 100%.

## Blocked by
- `03-product-catalog-seed.md`
