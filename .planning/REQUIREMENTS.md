# REQUIREMENTS.md

## High-Level Requirements

| ID | Title | Description | Priority |
|---|---|---|---|
| R1 | Customers & Products | Quản lý danh sách khách hàng và danh mục hàng hóa theo từng khách hàng. | P0 |
| R2 | Packing Thresholds | Lấy `Packed Qty` cho mỗi sản phẩm và theo dõi số lượng quét thực tế. | P0 |
| R3 | Carton S/N Rule | Sinh mã S/N: `[CN/VN][YYMM][MiddlePart][Sequence]`. | P0 |
| R4 | S/N Uniqueness | Số thứ tự `00001-99999` reset theo mỗi tháng. | P0 |
| R5 | Bartender Printing | In từ client sử dụng mẫu `carton.btw`. | P0 |
| R6 | Carton-Item Link | Lưu liên kết giữa `Carton_SN` và tất cả `Item_SN` trong DB. | P0 |
| R7 | Raw List QR Code | QR Code chứa danh sách mã S/N phân cách bằng dấu xuống dòng để xem trực tiếp khi quét (Zalo/Scanner). | P0 |

## Technical Requirements

| ID | Title | Description |
|---|---|---|
| T1 | FastAPI Backend | Python REST API for logic and database interaction. |
| T2 | Vue 3 Frontend | Modern UI for packing stations. |
| T3 | MSSQL 2008 | Data store for catalogs and packing history. |
| T4 | Bartender Integration | Method to pass data to existing Bartender installation on clients. |

## User- [ ] **Data Management**: Kết nối và quản lý dữ liệu trên MSSQL 2008 (Customers, Products, UPC, Middle Part).
- [ ] **Packing Workflow**: Chọn Customer -> Chọn Product từ danh sách của Customer đó -> Quét từng sản phẩm.
- [ ] **S/N Generation**: Tự động sinh Carton S/N theo định dạng `[CN/VN][YYMM][MiddlePart][Sequence]`.
- [ ] **Automated Printing**: Tự động kích hoạt in tem `carton.btw` khi quét đủ số lượng QTY.
- [ ] **QR Code Content**: QR Code trên tem chứa danh sách text thô (raw list) toàn bộ S/N của sản phẩm bên trong (phân tách bằng dấu xuống dòng).

## User Acceptance Criteria (UAT)

1. Giao diện hiển thị đúng danh sách sản phẩm từ bảng mẫu (1.png).
2. Khi quét đủ QTY (ví dụ 100), hệ thống tự động sinh số nhảy S/N tiếp theo.
3. Tem in ra chứa đầy đủ thông tin: Tên hàng, QTY, Carton S/N, UPC và QR Code.
4. Quét mã QR trên tem trả về danh sách toàn bộ S/N của sản phẩm bên trong.
