# 02. Database Schema Additions & UX Product Catalog

Status: ready-for-agent

## What to build
Mở rộng Schema Database không phá vỡ dữ liệu cũ (Additive Migration) và khởi tạo dữ liệu cho khách hàng UX:
- Bổ sung các cột mới vào bảng `products`:
  - `packing_mode`: String (mặc định `'item_scan'`).
  - `target_weight`: Float, nullable (kg).
  - `min_weight`: Float, nullable (kg).
  - `max_weight`: Float, nullable (kg).
  - `weight_unit`: String (mặc định `'kg'`).
  - `mfr_pn`: String(50), nullable (Mã chứng nhận / NYS Spec No).
  - `pkg_prefix`: String(20), nullable (Tiền tố mã sê-ri thùng, VD: `VHK0010237`).
  - `revision`: String(10), default `'B'`.
- Bổ sung các cột mới vào bảng `cartons`:
  - `weight`: Float, nullable (Trọng lượng thực tế lúc in tem).
  - `po_number`: String(100), nullable (Mã đơn hàng PO).
  - `lot_number`: String(100), nullable (Mã số lô sản xuất).
  - `date_code`: String(20), nullable (Mã tuần năm YYWW).
- Khởi tạo Customer `UX` và 3 sản phẩm ban đầu:
  - `840-00083`: qty=190, pkg_prefix="VHK0010237", mfr_pn="NYS5998", template_type="a11", packing_mode="weight_scale"
  - `840-00091`: qty=190, pkg_prefix="VHK0010237", mfr_pn="NYS5998", template_type="a11", packing_mode="weight_scale"
  - `840-00092`: qty=190, pkg_prefix="VHK0010237", mfr_pn="NYS5998", template_type="a11", packing_mode="weight_scale"

## Acceptance criteria
- [x] Schema database được cập nhật thành công mà không ảnh hưởng hoặc làm mất bất kỳ bản ghi nào của khách hàng UI.
- [x] Model `Product` và `Carton` trong SQLAlchemy có đầy đủ các trường mới với kiểu dữ liệu chuẩn xác.
- [x] API lấy danh sách sản phẩm theo khách hàng (`/api/v1/products?customer_code=UX`) trả về đúng 3 sản phẩm với cấu hình trọng lượng và tiền tố.
- [x] Đơn vị test kiểm tra việc tạo Carton mới cho cả 2 khách hàng UI và UX đều pass 100%.

## Blocked by
None - can start immediately
