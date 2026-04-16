# REQUIREMENTS.md

## High-Level Requirements

| ID | Title | Description | Priority |
|---|---|---|---|
| R1 | Select Customer & Item | Web UI to choose customer and then narrow down to item via dropdown. | P0 |
| R2 | Packing Thresholds | Fetch `Packed Qty` for each item and track scanned counts. | P0 |
| R3 | Carton S/N Rule | Generate S/N: `[CN/VN][YYMM][MiddlePart][Sequence]`. | P0 |
| R4 | S/N Uniqueness | Monthly sequence `00001-99999` reset every month. | P0 |
| R5 | Bartender Printing | Client-side printing trigger using Bartender template `carton.btw`. | P0 |
| R6 | Carton-Item Relationship | Database link between `Carton_SN` and all scanned `Item_SN`s. | P0 |
| R7 | Details QR Code | QR code on label that, when scanned, shows all item S/Ns in the carton. | P1 |

## Technical Requirements

| ID | Title | Description |
|---|---|---|
| T1 | FastAPI Backend | Python REST API for logic and database interaction. |
| T2 | Vue 3 Frontend | Modern UI for packing stations. |
| T3 | MSSQL 2008 | Data store for catalogs and packing history. |
| T4 | Bartender Integration | Method to pass data to existing Bartender installation on clients. |

## User Acceptance Criteria (UAT)

1. Giao diện hiển thị đúng danh sách sản phẩm từ bảng mẫu (1.png).
2. Khi quét đủ QTY (ví dụ 100), hệ thống tự động sinh số nhảy S/N tiếp theo.
3. Tem in ra chứa đầy đủ thông tin: Tên hàng, QTY, Carton S/N, UPC và QR Code.
4. Quét mã QR trên tem trả về danh sách toàn bộ S/N của sản phẩm bên trong.
