# 04. UX Yearly-Reset SN Allocator & A11 BTXML Generator

Status: ready-for-agent

## What to build
Xây dựng logic sinh mã sê-ri reset theo năm và tạo lệnh in BarTender định dạng A11:
- `UXCartonSNAllocator`:
  - Định dạng: `{pkg_prefix}{YYMM}{sequence:06d}` (Ví dụ: `VHK00102372608000081`).
  - Quy tắc reset: Tìm số thứ tự lớn nhất trong năm hiện tại (`YY`) của sản phẩm/tiền tố để tăng tiếp. Reset về `000001` vào ngày `01/01` hàng năm.
- Tính toán `Date Code`: Định dạng chuẩn ISO `YYWW` (Ví dụ: Tuần 34 năm 2026 ➔ `2634`).
- `A11_BTXMLDocument`:
  - Tạo XML với 7 trường 1D barcode: `CPN`, `QTY`, `MfrPN`, `DateCode`, `LotNo`, `PONo`, `CartonSN`.
  - Sinh chuỗi QR 2D nối 7 trường bằng dấu phẩy `,`: `P{CPN},Q{QTY},M{MfrPN},D{DateCode},L{LotNo},K{PONo},S{CartonSN}`.
  - Ánh xạ `Rev` và `Origin` (`Made in Vietnam` / `Made in China`).
- API Endpoint `POST /api/v1/carton/weigh-pack`:
  - Nhận vào: `product_id`, `weight`, `po_number`, `lot_number`, `printer_name`.
  - Kiểm tra dải trọng lượng: `min_weight <= weight <= max_weight`. Nếu vi phạm ➔ Trả HTTP 400 kèm thông báo sai số.
  - Nếu hợp lệ ➔ Cấp phát `Carton SN`, lưu bản ghi `Carton` (kèm `weight`, `po_number`, `lot_number`, `date_code`), sinh BTXML và trả về cho client.

## Acceptance criteria
- [x] Dãy sê-ri thùng của khách hàng UX tăng tuần tự 6 số (`000001`, `000002`...) và độc lập hoàn toàn với dãy sê-ri 5 số của khách hàng UI.
- [x] Date code được sinh chính xác theo năm và tuần ISO.
- [x] Chuỗi QR code chứa đúng định dạng phân tách bằng dấu phẩy theo tiêu chuẩn bản vẽ A11.
- [x] Lệnh weigh-pack từ chối cấp mã nếu trọng lượng nằm ngoài dải `[min_weight, max_weight]`.
- [x] Lệnh in được tạo đầy đủ và tương thích hoàn toàn với BarTender template `第1.btw`.


## Blocked by
- `.scratch/ux-customer-weight-scale/issues/02-db-schema-and-ux-product-catalog.md`
