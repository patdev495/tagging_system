# Issue 04: Tích hợp BarTender In Ấn Thực Tế & Xuất PDF Verification
Status: completed

## What to build
1. Đảm bảo BarTender COM / Print Agent v2 nạp và in thành công file mẫu `D:\PAT\Templates\a11_02.btw` với 7 Named SubStrings đã cấu hình.
2. Viết integration test tự động hóa quy trình in / xuất file PDF cho 2 con hàng `G012C1B` và `G112C1B`.
3. Kiểm tra tính toàn vẹn của file PDF xuất ra (hoặc lệnh in gửi đến BarTender engine):
   - Mã vạch SSCC đọc ra đúng chuỗi chuẩn GS1 với Check Digit.
   - Text SSCC hiển thị: `Pallet SSCC  (00) 0 37033907 {seq:07d} {cd}`.
   - P/N text và barcode đọc ra đúng `NYS5998` (cho G012C1B) hoặc `NYS5996` (cho G112C1B).
   - ASIN hiển thị đúng `B08G9M4HXS` hoặc `B0C32N712K`.
   - Unit UPC hiển thị đúng `852582006785` hoặc `840268969493`.
   - Product Name dài hiển thị đầy đủ quy cách cáp.
   - Xuất xứ hiển thị đủ 3 dòng (`ASSEMBLED IN VIETNAM / ASSEMBLE AU VIETNAM / HECHO EN VIETNAM`).

## Acceptance criteria
- [x] Lệnh in từ hệ thống chuyển tới BarTender không gây lỗi COM hay lỗi thiếu Named SubString.
- [x] Xuất thành công file PDF/ảnh tem nhãn mẫu cho cả 2 sản phẩm `G012C1B` và `G112C1B`.
- [x] Hình ảnh tem in ra khớp 100% với bản vẽ kỹ thuật PD027504 Rev C.
- [x] Có bộ test tự động phủ kín (`tests/test_a11_tem2_bartender_integration.py`).

## Blocked by
- .scratch/a11-template2-integration/issues/03-weight-scale-packing-workflow.md

