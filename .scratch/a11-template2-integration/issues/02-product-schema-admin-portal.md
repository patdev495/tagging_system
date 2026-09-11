# Issue 02: Mở rộng Schema Product & Quản trị Sản phẩm Admin Portal
Status: completed

## What to build
1. Mở rộng model SQLAlchemy `Product` (`backend_v2/src/core/models.py`) và schema Pydantic (`backend_v2/src/features/product/schemas.py`):
   - Thêm cột `factory_pn`: String(100), nullable=True (Mã nội bộ xưởng 厂内料号)
   - Thêm cột `asin`: String(50), nullable=True (Mã Amazon ASIN)
   - Thêm cột `product_desc`: String(255), nullable=True (Chuỗi mô tả cáp đầy đủ)
2. Cập nhật backend Product CRUD Service & Router để hỗ trợ lưu và cập nhật các trường mới.
3. Hỗ trợ tìm kiếm theo `factory_pn` trong API tìm kiếm sản phẩm.
4. Cập nhật giao diện Quản lý Sản phẩm (Frontend Vue / `ProductManagementPage.vue` và `ProductFormModal.vue`):
   - Bổ sung ô nhập `Mã nội bộ xưởng (Factory P/N)`, `ASIN`, `Mô tả sản phẩm (Product Description)` khi chọn template type là `a11_tem2`.
   - Bổ sung `a11_tem2` vào danh sách lựa chọn Template Type.
   - Cho phép tìm kiếm sản phẩm bằng mã `factory_pn` trên thanh tìm kiếm.
5. Tạo script seed hoặc tự động nạp sẵn 2 con hàng chuẩn của Tem 2 vào database:
   - `G012C1B`: factory_pn=`1LAE0009D2U004MAAR`, upc=`852582006785`, asin=`B08G9M4HXS`, mfr_pn=`NYS5998`, packed_qty=190, template_type=`a11_tem2`, template_path=`D:\PAT\Templates\a11_02.btw`, packing_mode=`weight_scale`, min_weight=5.0, max_weight=7.0, target_weight=6.0, product_desc=`ASSY,BAND WRAPPED,CAT5E ETHERNET CABLE 4.0mm OD:91CM,WHITE,RUBBER BAND`
   - `G112C1B`: factory_pn=`1LAE0009D2U002MAAS`, upc=`840268969493`, asin=`B0C32N712K`, mfr_pn=`NYS5996`, packed_qty=190, template_type=`a11_tem2`, template_path=`D:\PAT\Templates\a11_02.btw`, packing_mode=`weight_scale`, min_weight=5.0, max_weight=7.0, target_weight=6.0, product_desc=`ASSY, BAND WRAPPED, CAT6A ETHERNET CABLE 4.7MM OD, 91CM , WHITE,RUBBER BAND`

## Acceptance criteria
- [x] Bảng `products` trong database lưu trữ và truy xuất thành công 3 trường mới `factory_pn`, `asin`, `product_desc`.
- [x] Giao diện Admin hiển thị đúng thông tin và cho phép tạo mới / sửa sản phẩm thuộc template `a11_tem2`.
- [x] Tìm kiếm bằng mã xưởng `1LAE0009D2U004MAAR` trả về đúng sản phẩm `G012C1B`.
- [x] 2 sản phẩm `G012C1B` và `G112C1B` tồn tại trong database với đầy đủ thông số kỹ thuật chuẩn.
- [x] Có bộ unit test tự động (pytest) phủ kín toàn bộ các hàm trên (`tests/test_a11_tem2_product_schema.py`).

## Blocked by
None - can start immediately
