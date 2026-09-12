# PRD: Tích Hợp Tem Số 3 (Bản Vẽ PD024364) Xuất Xưởng Luxshare NME Cho Khách Hàng A11

> **Feature Slug**: `a11-tem3-luxshare`  
> **Khách hàng**: `A11` (Dự án cáp mạng Amazon eero)  
> **Bản vẽ kỹ thuật**: `PD024364 REV.M` (Tem ngang $100 \times 80\text{ mm}$)  
> **Mẫu BarTender chuẩn hóa**: `D:\PAT\Templates\a11_03.btw`

---

## 1. Bối Cảnh & Mục Tiêu
Khách hàng A11 có dòng sản phẩm cáp mạng xuất cho đối tác lắp ráp Luxshare (立讯 NME) theo bản vẽ kỹ thuật `PD024364 REV.M`. Hệ thống cần tích hợp **Tem Số 3** cho mã hàng cáp mạng:
- **`2M21-00508-0004H`** (CAT5E ETHERNET CABLE, QTY 190, Mã nội bộ xưởng `1LAE0091C2U011NMES`, Dự án `Andy Town/ Firefly`, Giai đoạn `QB/CR`, APN-Rev `/`).

---

## 2. Đặc Tả Nghiệp Vụ Chính
1. **Định danh thùng (Carton SN)**: 17 ký tự theo Ghi chú G bản vẽ `PD024364 REV.M`:
   $$\text{Carton SN} = \mathbf{1012665} + \{\text{YYMMDD}\} + \{\text{Seq:04d}\}$$
   - `1012665`: Mã nhà cung ứng Nien Yi xưởng Việt Nam.
   - `YYMMDD`: Thời gian sản xuất 6 chữ số theo giờ cục bộ của máy chủ nhà máy.
   - `Seq:04d`: Số thứ tự 4 chữ số từ `0001` đến `9999`, **tự động reset về `0001` vào 00:00 mỗi ngày mới**.
2. **Cấu trúc mã 2D QR Code**: Phân cách bằng ký tự `$` theo quy cách:
   `{CartonSN}${SupplierCode}${SupplierName}${PartNo}${APNRev}${LotNo}${DateYYYYMMDD}${QTY}$$$$$$`
3. **Quản lý Sản phẩm & BarTender Template**:
   - Tên template chuẩn hóa: `a11_03.btw` trong `D:\PAT\Templates\`.
   - Mã loại tem: `a11_tem3`.
   - 12 Named SubStrings: `ProjectStage`, `PartNo`, `APNRev`, `QTY`, `Date`, `LotNo`, `PartDesc`, `SupplierCode`, `CartonSN`, `SupplierName`, `Origin`, `QRCode_Content`.
4. **Quy trình Cân & Đóng gói**:
   - Chế độ `weight_scale`.
   - PO Number cho phép để rỗng (bypass popup).
   - Lot Number điền sẵn từ cấu hình, cho phép sửa trực tiếp trên giao diện ca đóng gói.
   - **Tuyệt đối cấm Reprint** theo quyết định `ADR-0005`.
