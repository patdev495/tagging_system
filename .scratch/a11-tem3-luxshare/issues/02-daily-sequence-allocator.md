# Issue 02: Bộ Cấp Phát Số Sê-Ri Thùng Reset Theo Ngày (Daily Sequence Allocator)
Status: completed

## What to build
Xây dựng service cấp phát mã thùng Carton SN theo ngày cho Tem 3:
1. Tạo module `backend_v2/src/features/carton/a11_tem3_allocator.py`:
   - Hàm `format_a11_tem3_carton_sn(supplier_code: str, yymmdd: str, sequence: int) -> str`: Ghép chuỗi 17 ký tự `{supplier_code:7}{yymmdd:6}{sequence:04d}`.
   - Hàm `parse_a11_tem3_sequence(carton_sn: str, supplier_code: str, yymmdd: str) -> int`: Trích xuất số thứ tự 4 chữ số từ mã thùng tương ứng với ngày `yymmdd`.
   - Hàm `next_a11_tem3_sequence(db: Session, supplier_code: str, yymmdd: str, lock: bool = False) -> int`: Truy vấn số sê-ri lớn nhất đã cấp phát trong ngày `yymmdd` (áp dụng `with_for_update()`). Nếu chưa có thùng nào trong ngày, trả về `1`. Nếu đã có, trả về `max_seq + 1`.
   - Hàm `plan_next_a11_tem3_carton_sn(db: Session, product: models.Product, ...)`: Trả về dataclass `A11Tem3CartonPlan`.
2. Tích hợp vào hàm `weigh_pack_carton` trong `backend_v2/src/features/carton/service.py`:
   - Khi `product.template_type == "a11_tem3"`, gọi `plan_next_a11_tem3_carton_sn`.
   - Lưu trữ `carton_sn`, `date_code = yymmdd`, `weight`, `lot_number`, `po_number` vào bản ghi `Carton`.

## Acceptance criteria
- [x] Hàm sinh sê-ri trả về đúng cấu trúc 17 ký tự: `1012665` + `YYMMDD` + `Seq:04d`.
- [x] Thùng đầu tiên của ngày mới tự động bắt đầu từ `0001`. Thùng tiếp theo trong cùng ngày tăng lên `0002`, `0003`...
- [x] Cơ chế khóa `with_for_update()` ngăn chặn hoàn toàn race-condition khi có nhiều request đồng thời.
- [x] Unit tests (pytest) kiểm thử cấp phát bình thường, rollover qua ngày mới, và validation độ dài 17 ký tự.

## Blocked by
- `01-bartender-btw-btxml.md`
