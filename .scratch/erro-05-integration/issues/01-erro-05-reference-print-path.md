Status: completed

# Erro 05 reference print path

## What to build

Xây dựng luồng đóng gói cân và in ấn hoàn chỉnh từ đầu đến cuối cho sản phẩm đại diện thuộc mẫu tem `erro_05` (Bản vẽ PD016906 Pegatron NN9). 

Khi trạm cân nhận giá trị trọng lượng hợp lệ trong dải Weight Tolerance, hệ thống thực hiện:
1. Cấp phát sê-ri tiếp theo từ bộ đếm chung `Erro 05 Carton Sequence` dải `50001`–`99999` cho xưởng Việt Nam, dùng chung cho mọi Product `erro_05`.
2. Sê-ri tự động reset về `50001` vào 00:00:00 ngày đầu tiên của mỗi tháng (`YYYY-MM` theo giờ cục bộ máy chủ nhà máy). Nếu đã có Carton `erro_05` trong tháng hiện tại, cấp số lớn nhất cộng 1; nếu chưa có thì bắt đầu từ `50001`.
3. Sinh Carton SN 18 ký tự: `{pkg_prefix}2{YY}{WW}{Seq:05d}` (mặc định `{pkg_prefix}` là `MC220TW1`, lấy từ `Product.pkg_prefix`).
4. Sinh lệnh in BTXML với 12 Named SubStrings (`CartonNo`, `Item`, `DESC`, `DateCode`, `LotCode`, `QTY`, `QRCode_Content`, `MPN`, `Rev`, `Config`, `Batch`, `Stage`).
5. Mã 2D QR Code tổng hợp chuẩn 7 trường: `{CartonNo},{Item},{MPN},{Batch},{QTY},{DateCode},{LotCode}`.
6. Lưu bản ghi Carton vào CSDL, tuyệt đối cấm in lại (No Reprint theo ADR-0005).

## Acceptance criteria

- [x] Product với `template_type = "erro_05"` có thể thực hiện thành công lệnh cân và in tại service `weigh_pack_carton`.
- [x] Mã Carton SN tuân thủ chính xác định dạng 18 ký tự: `{pkg_prefix}2{YY}{WW}{Seq:05d}`.
- [x] Bộ đếm sê-ri nằm trong dải `50001`–`99999`, dùng chung cho mọi Product `erro_05` và tự động reset về `50001` vào đầu mỗi tháng (`YYYY-MM`).
- [x] Chuỗi BTXML sinh ra chứa đầy đủ 12 Named SubStrings, giá trị `DateCode` là `YYWW`, `LotCode` mặc định là `YYYYMMDD`, và `QRCode_Content` chứa đúng 7 trường phân cách bởi dấu phẩy.
- [x] Carton lưu trữ snapshot chính xác của dữ liệu in; hành động Reprint bị chặn theo chính sách kiểm soát tem Erro.
- [x] Toàn bộ unit tests bao phủ: cấp phát sê-ri theo tháng, nhảy số liên tục, reset đầu tháng, sinh BTXML, và từ chối ngoài dải cân.

## Blocked by

None - can start immediately.
