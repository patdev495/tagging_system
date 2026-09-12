# PRD: Tích Hợp Tem Số 05 Khách Hàng Erro (Pegatron NN9 - Bản Vẽ PD016906)

## 1. Bối Cảnh & Mục Tiêu

Hệ sinh thái đóng gói nhãn thùng (Carton) của khách hàng Erro đang vận hành các mẫu tem `erro_01` (bản vẽ PD014736), `erro_02` (bản vẽ PD027504), `erro_03` (bản vẽ PD024364 Luxshare), và `erro_04` (bản vẽ PD027032 eero Mỹ). Dự án cáp mạng NN9 hợp tác với Pegatron yêu cầu bổ sung mẫu tem số 5 (`erro_05`) theo bản vẽ kỹ thuật `NY1107103E(PD016906)` Rev I.

Mục tiêu:
- Tích hợp mẫu nhãn thùng ngoài (Carton / 外包装 - Trang 2 bản vẽ, kích thước $102 \times 77\text{ mm}$, tiêu đề `PEGATRON`).
- Cấp phát mã thùng Carton SN chuẩn Pegatron 18 ký tự: `{pkg_prefix}2{YY}{WW}{Seq:05d}` với bộ đếm sê-ri 5 số dải `50001`–`99999` reset về `50001` vào 00:00 ngày mùng 1 hàng tháng theo ADR-0008.
- Tuyệt đối cấm in lại tem cũ (No Reprint theo ADR-0005).
- Tái sử dụng 100% schema bảng `products`, không thêm cột mới.
- Seed sẵn toàn bộ 38 mã sản phẩm thuộc dự án NN9 vào danh mục sản phẩm.

## 2. Đặc Tả Kỹ Thuật Chính

- **Template Code**: `erro_05`
- **Template Path**: `D:\PAT\Templates\erro_05.btw`
- **Packing Mode**: `weight_scale`
- **Carton SN**:
  $$\text{Carton No} = \text{pkg\_prefix (mặc định MC220TW1)} + \text{"2"} + \text{YY (2 số năm)} + \text{WW (2 số tuần)} + \text{Seq:05d (50001..99999)}$$
- **Quy tắc reset sê-ri**: Reset về `50001` vào 00:00 ngày 1 hàng tháng (`YYYY-MM`), dùng chung cho mọi Product `erro_05`.
- **Mã vạch 1D (Code 128)**: Carton No, Item (PEGA P/N), Date Code (`YYWW`), Lot Code (`YYYYMMDD`), QTY.
- **Mã vạch 2D QR Code**: `{CartonNo},{Item},{MPN},{Batch},{QTY},{DateCode},{LotCode}`.
- **Quy trình ca đóng gói**: `Date Code` và `Lot Code` sinh tự động lúc in; `PO Number` và `Batch` cho phép để trống mặc định.

## 3. Danh Sách Vertical Slices

1. `01-erro-05-reference-print-path` (AFK)
2. `02-erro-05-bartender-template-configuration` (AFK)
3. `03-erro-05-catalog-and-38-products-seed` (AFK)
4. `04-erro-05-packing-station-controls` (AFK)
