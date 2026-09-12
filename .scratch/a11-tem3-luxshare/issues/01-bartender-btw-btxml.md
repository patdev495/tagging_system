# Issue 01: Chuẩn Hóa BarTender BTW & Xây Dựng BTXML Contract Cho Tem 3
Status: completed

## What to build
Xây dựng và chuẩn hóa file mẫu BarTender `a11_03.btw` kèm theo template BTXML serialization:
1. Sao chép và cấu hình file `templates/a11/第3 2M21-00508-0004 Tem NGOÀI.btw` thành `D:\PAT\Templates\a11_03.btw` (và lưu bản gốc vào `templates/a11/a11_03.btw`).
2. Gán 12 Named SubStrings chuẩn cho file BTW:
   - `ProjectStage`: Dòng dự án và giai đoạn sản xuất (VD: `项目: Andy Town/ Firefly         生产阶段：QB/CR`)
   - `PartNo`: Dòng mã liệu Luxshare (VD: `料号:                        2M21-00508-0004H`)
   - `APNRev`: Dòng phiên bản APN (VD: `APN-Rev :             /`)
   - `QTY`: Dòng số lượng đóng gói (VD: `数量:                    190`)
   - `Date`: Dòng ngày sản xuất YYYYMMDD (VD: `生产日期:                20260911`)
   - `LotNo`: Dòng số lô sản xuất (VD: ` 生产批号:                   92607933`)
   - `PartDesc`: Dòng mô tả linh kiện (VD: ` 料件描述:        CAT5E ETHERNET CABLE`)
   - `SupplierCode`: Dòng mã nhà cung ứng (VD: `供应商代码:                          1012665`)
   - `CartonSN`: Dòng mã thùng 17 ký tự (VD: `箱号:                                   10126652609110001`)
   - `SupplierName`: Dòng tên nhà cung ứng (VD: `供应商名称：  NIENYI VIETNAM INDUSTRIAL COMPANY LIMITED`)
   - `Origin`: Dòng xuất xứ (VD: `原产地：VIETNAM                                     型号：                              品牌：`)
   - `QRCode_Content`: Dữ liệu mã vạch 2D QR Code:
     `{carton_sn}${supplier_code}${supplier_name}${part_no}${apn_rev}${lot_no}${date_ymd}${qty}$$$$$$`
3. Tạo file template `backend_v2/src/features/print/templates/a11_tem3.xml` cho BTXML Script 2.0.
4. Bổ sung nhánh `template_type == "a11_tem3"` trong `BTXMLDocument.from_carton_data` để tự động serialize đúng các trường trên.

## Acceptance criteria
- [x] File `a11_03.btw` mở qua BarTender COM nhận đầy đủ 12 Named SubStrings và hiển thị nội dung chính xác.
- [x] `BTXMLDocument.from_carton_data` tạo ra XML chứa đầy đủ 12 thẻ `<NamedSubString>` tương ứng với mẫu `a11_tem3.xml`.
- [x] Chuỗi `QRCode_Content` sinh đúng định dạng phân cách bởi `$` theo quy cách bản vẽ.
- [x] Có bộ unit test tự động (pytest) kiểm thử XML serialization và BarTender COM integration cho `a11_tem3`.

## Blocked by
None - can start immediately
