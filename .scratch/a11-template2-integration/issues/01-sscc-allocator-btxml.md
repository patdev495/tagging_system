# Issue 01: Thuật toán GS1 SSCC Allocator & BTXML Serialization Engine
Status: completed

## What to build
Xây dựng module cấp phát mã thùng Pallet SSCC 18 chữ số và module sinh tài liệu in BTXML cho Tem 2:
1. Module tính Check Digit chuẩn GS1 Modulo 10 (trọng số 3-1 luân phiên từ phải qua trái).
2. Bộ cấp phát sê-ri SSCC 7 chữ số liên tục toàn cục theo Company Prefix (`037033907`), bắt đầu từ `0000001` đến `9999999`, không bao giờ reset theo năm hay tháng.
3. Template XML `backend_v2/src/features/print/templates/a11_tem2.xml` định nghĩa cấu trúc lệnh in BarTender XMLScript với 7 Named SubStrings chuẩn:
   - `ProductName`: `Product name:{product_desc}`
   - `QTY`: `{qty}` (mặc định 190)
   - `SSCC_Text`: `(00) 0 37033907 {seq:07d}`
   - `SSCC_CD`: `{cd}`
   - `PN`: `{mfr_pn}`
   - `ASIN`: `{asin}`
   - `UnitUPC`: `{upc}`
4. Logic trong `BTXMLDocument.from_carton_data` xử lý khi `product.template_type == "a11_tem2"` tự động trích xuất các trường trên và tính toán Check Digit.

## Acceptance criteria
- [x] Hàm tính Check Digit Modulo 10 GS1 trả về kết quả chính xác tuyệt đối:
  - Input `0370339071000286` -> Check Digit = `1`
  - Input `0370339070000001` -> Check Digit = `3`
- [x] Bộ cấp phát SSCC tự tăng chuỗi 7 số và sinh chuỗi SSCC 18 số đúng chuẩn: `037033907{seq:07d}{cd}`.
- [x] Template XML `a11_tem2.xml` serialize ra BTXML hợp lệ và `BTXMLDocument.from_xml` parse ngược lại nguyên vẹn đầy đủ 7 trường.
- [x] Có bộ unit test tự động (pytest) phủ kín toàn bộ các hàm trên (`tests/test_sscc_allocator.py`, `tests/test_a11_tem2_btxml.py`).

## Blocked by
None - can start immediately
