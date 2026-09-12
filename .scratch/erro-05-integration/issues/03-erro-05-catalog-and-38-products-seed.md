Status: completed

# Erro 05 catalog and 38 products seed

## What to build

Khởi tạo và nạp toàn bộ danh mục 38 sản phẩm dự án NN9 từ Trang 3 bản vẽ kỹ thuật `PD016906` vào cơ sở dữ liệu cho Customer `ERRO`.

Mỗi sản phẩm được gán:
- `customer_id`: ID của Customer `ERRO`
- `item_name`: Mã PEGA P/N (Cột 2 bản vẽ, ví dụ `1414-0GDA0BV`, `1412-04T50W3`)
- `factory_item_code`: Mã liệu thành phẩm của xưởng (Cột 3 bản vẽ, ví dụ `1HWU3023C1XX02NN9`)
- `product_desc`: Mô tả quy cách chi tiết (Cột 4 bản vẽ, ví dụ `X LED CABLE 30AWG 230mm`)
- `pkg_prefix`: `MC220TW1`
- `template_type`: `erro_05`
- `template_path`: `D:\PAT\Templates\erro_05.btw`
- `packing_mode`: `weight_scale`
- `packed_qty`: `1000` (mặc định cho tất cả các mã, khớp file mẫu)
- `min_weight`: `0.0`
- `max_weight`: `10.0`
- `target_weight`: `5.0`
- `revision`: `""`

Đồng thời bảo đảm phân hệ Quản trị (Admin) hỗ trợ xem, tìm kiếm và cập nhật `pkg_prefix`, `packed_qty`, cùng các ngưỡng cân nặng của 38 sản phẩm này, trong khi giao diện trạm đóng gói bị khóa không cho phép sửa đổi `pkg_prefix`.

## Acceptance criteria

- [x] Hàm khởi tạo / seed cơ sở dữ liệu tạo đủ 38 sản phẩm `erro_05` thuộc Customer `ERRO`, bảo đảm idempotent (chạy lại không tạo trùng).
- [x] Mọi sản phẩm đều chứa đầy đủ thông tin: `item_name`, `factory_item_code`, `product_desc`, `pkg_prefix="MC220TW1"`.
- [x] API Product và màn hình Quản trị (Admin) hiển thị danh sách 38 mã hàng này, cho phép Admin chỉnh sửa số lượng và dung sai trọng lượng.
- [x] Không thêm bất kỳ cột mới nào vào bảng `products` (tái sử dụng 100% schema hiện có).

## Blocked by

- [01-erro-05-reference-print-path](file:///d:/Workspace/NY_tagging_sys/.scratch/erro-05-integration/issues/01-erro-05-reference-print-path.md)
