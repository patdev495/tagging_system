# PRD: Tích Hợp Tem Số 2 (Bản Vẽ PD027504) Cho Khách Hàng A11

> **Feature Slug**: `a11-template2-integration`  
> **Khách hàng**: `A11` (Dự án cáp mạng Amazon eero)  
> **Bản vẽ kỹ thuật**: `PD027504 Rev C` (Tem ngang $152 \times 95\text{ mm}$)  
> **Mẫu BarTender đã cấu hình**: `D:\PAT\Templates\a11_02.btw`

---

## 1. Bối Cảnh & Mục Tiêu
Khách hàng A11 hiện đang có các dòng sản phẩm đóng gói theo tiêu chuẩn Tem 1 (`PD014736`). Để phục vụ xuất xưởng cho các nhà máy lắp ráp (CM) theo hợp đồng mới, hệ thống cần tích hợp thêm **Tem Số 2 (bản vẽ PD027504 Rev C)** cho 2 dòng sản phẩm cáp mạng:
1. **`G012C1B`** (CAT5E, P/N `NYS5998`, ASIN `B08G9M4HXS`, UPC `852582006785`, QTY 190, Mã xưởng `1LAE0009D2U004MAAR`)
2. **`G112C1B`** (CAT6A, P/N `NYS5996`, ASIN `B0C32N712K`, UPC `840268969493`, QTY 190, Mã xưởng `1LAE0009D2U002MAAS`)

---

## 2. Đặc Tả Nghiệp Vụ Chính
1. **Định danh thùng (Carton SN)**: Sử dụng mã chuẩn GS1 Pallet SSCC 18 chữ số:
   $$\text{SSCC} = \mathbf{0} + \mathbf{37033907} + \{\text{Seq:07d}\} + \{\text{Check Digit: 1 số}\}$$
   - Sê-ri 7 chữ số tăng liên tục toàn cục cho toàn bộ con hàng dùng Company Prefix `037033907`, không bao giờ reset.
   - Check Digit tính theo chuẩn Modulo 10 trọng số 3-1 của GS1.
2. **Quản lý Sản phẩm**:
   - Lưu trữ mã SKU khách hàng vào `item_name`.
   - Lưu trữ mã nội bộ xưởng vào `factory_pn` (hỗ trợ tìm kiếm nhanh trên UI).
   - Lưu trữ `asin`, `product_desc`, `upc`, `mfr_pn`, `packed_qty = 190`, `packing_mode = "weight_scale"`, `template_type = "a11_tem2"`.
3. **Quy trình Cân & Đóng gói**:
   - Cho phép bỏ qua (không bắt buộc) PO Number và Lot Number khi mở ca đóng gói các con hàng Tem 2.
   - Kiểm soát dung sai cân (`min_weight`, `max_weight`). Khi cân đạt chuẩn và công nhân nhấn In (`F9`), backend sinh số SSCC tiếp theo, tính Check Digit, tạo bản ghi Carton và xuất lệnh in.
4. **Định dạng in BarTender**:
   - Truyền dữ liệu vào file `D:\PAT\Templates\a11_02.btw` qua 7 Named SubStrings chuẩn:
     `ProductName`, `QTY`, `SSCC_Text`, `SSCC_CD`, `PN`, `ASIN`, `UnitUPC`.
