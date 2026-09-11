# Issue 03: Quy trình Cân Đóng Gói Tem 2 (Weight Scale Gatekeeper & PO/Lot Bypass)
Status: ready-for-agent

## What to build
1. Cập nhật schema `CartonWeighPackCreate` và service `weigh_pack_carton` (`backend_v2/src/features/carton/`):
   - Cho phép `po_number` và `lot_number` nhận giá trị rỗng/None (`Optional[str] = None`).
   - Khi sản phẩm có `template_type == "a11_tem2"`, gọi module cấp phát mã SSCC của Issue 01 để sinh `carton_sn` (18 chữ số).
   - Lưu bản ghi `Carton` với `carton_sn`, `weight`, `po_number` (nếu có), `lot_number` (nếu có) và sinh BTXML tương ứng với 7 Named SubStrings.
2. Cập nhật logic Frontend Cân Đóng Gói (`frontend_v2/src/features/packing/weight_scale/`):
   - Trong `useWeighAndPrint.ts`: Khi `selectedProduct.template_type === 'a11_tem2'`, không chặn in nếu `activePO` hoặc `activeLot` rỗng (bỏ qua thông báo bắt buộc nhập).
   - Vẫn hiển thị ô Batch PO / Lot trên giao diện để công nhân có thể bấm vào chỉnh sửa nếu muốn.
   - Khi trọng lượng nằm trong dung sai và nhấn In (`F9`), gọi API `/cartons/weigh-pack` tạo thùng hàng và in tem.

## Acceptance criteria
- [ ] API `/cartons/weigh-pack` chấp thuận đóng gói thành công sản phẩm Tem 2 ngay cả khi `po_number` và `lot_number` truyền lên là rỗng.
- [ ] Màn hình Cân không hiện cảnh báo lỗi "Vui lòng nhập PO và LOT trước khi in" khi chọn sản phẩm Tem 2.
- [ ] Carton được lưu vào DB với mã sê-ri chuẩn SSCC 18 số (ví dụ: `03703390700000013`).
- [ ] Cơ chế Gatekeeper dung sai cân (Weight Tolerance) vẫn hoạt động nghiêm ngặt: cân thiếu hoặc cân thừa đều chặn in.

## Blocked by
- .scratch/a11-template2-integration/issues/01-sscc-allocator-btxml.md
- .scratch/a11-template2-integration/issues/02-product-schema-admin-portal.md
