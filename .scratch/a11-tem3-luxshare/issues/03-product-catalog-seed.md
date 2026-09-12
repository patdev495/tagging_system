# Issue 03: Quản Trị Sản Phẩm, Khởi Tạo Dữ Liệu Seed & Template Resolver
Status: completed

## What to build
Mở rộng phân hệ Catalog / Quản trị sản phẩm để hỗ trợ `a11_tem3`:
1. `TemplateResolver` trong `backend_v2/src/core/utils.py` và `frontend_v2`:
   - Bổ sung ánh xạ `a11_tem3` -> `a11_03.btw`.
   - Bổ sung metadata tem vào danh sách templates hỗ trợ: `{"filename": "a11_03.btw", "customer": "A11", "type": "a11_tem3", "name": "A11 Tem 3 (Luxshare NME PD024364)"}`.
2. Seed dữ liệu sản phẩm trong script / database:
   - Sản phẩm `2M21-00508-0004H`:
     - `customer_id`: ID của A11
     - `item_name`: `2M21-00508-0004H`
     - `factory_pn`: `1LAE0091C2U011NMES`
     - `pkg_prefix`: `1012665`
     - `packed_qty`: `190`
     - `packing_mode`: `"weight_scale"`
     - `template_type`: `"a11_tem3"`
     - `template_path`: `a11_03.btw`
     - `product_desc`: `CAT5E ETHERNET CABLE`
     - `revision`: `/` (APN-Rev)
     - `min_weight`: `5.0`, `max_weight`: `7.0`, `target_weight`: `6.0`
3. Frontend `ProductFormModal.vue` và composable `useProductForm.ts`:
   - Thêm lựa chọn `A11 - Tem 3 (Luxshare NME — a11_03.btw)`.
   - Tự động điền `template_path = 'a11_03.btw'` khi chọn template này.

## Acceptance criteria
- [ ] API `GET /catalog/products` và `GET /template/diagnostics` nhận diện `a11_03.btw` hợp lệ.
- [ ] Bản ghi sản phẩm `2M21-00508-0004H` được tạo đầy đủ các trường thông tin kỹ thuật của Tem 3.
- [ ] Form tạo/sửa sản phẩm trên Web Admin hiển thị tùy chọn Tem 3 và cho phép lưu trữ trơn tru.

## Blocked by
- `02-daily-sequence-allocator.md`
