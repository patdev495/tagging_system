Status: completed

# Erro 05 BarTender template configuration and integration acceptance

## What to build

Cấu hình file template BarTender [erro_05.btw](file:///d:/Workspace/NY_tagging_sys/templates/erro/erro_05.btw) chuẩn hóa đầy đủ 12 Named SubStrings để tương thích với động cơ in tự động qua BarTender COM / BTXML, triển khai vào đường dẫn runtime `D:\PAT\Templates\erro_05.btw`, và viết bài test nghiệm thu tích hợp.

Danh sách 12 Named SubStrings cần gán vào các đối tượng trên tem:
1. `CartonNo`: Gán cho text hiển thị và mã vạch Barcode 128 của Carton No
2. `Item`: Gán cho text hiển thị và mã vạch Barcode 128 của PEGA P/N
3. `DESC`: Gán cho text quy cách DESC
4. `DateCode`: Gán cho text hiển thị và mã vạch Barcode 128 của Date Code (YYWW)
5. `LotCode`: Gán cho text hiển thị và mã vạch Barcode 128 của Lot Code (YYYYMMDD)
6. `QTY`: Gán cho text hiển thị và mã vạch Barcode 128 của QTY
7. `QRCode_Content`: Gán trực tiếp làm Data Source cho mã vạch 2D QR Code
8. `MPN`: Gán cho text hiển thị trường MPN (sau chữ `MPN:`)
9. `Rev`: Gán cho text hiển thị trường Rev (sau chữ `Rev:`)
10. `Config`: Gán cho text hiển thị trường Config (sau chữ `Config:`)
11. `Batch`: Gán cho text hiển thị trường Batch (sau chữ `Batch:`)
12. `Stage`: Gán cho text hiển thị trường Stage (sau chữ `Stage:`)

Xây dựng bài kiểm thử tự động `tests/test_erro_05_bartender_integration.py` sử dụng win32com mở file template, gán 12 trường giá trị thực tế, xuất ảnh kiểm chứng và giải mã barcode để nghiệm thu không có suy hao dữ liệu.

## Acceptance criteria

- [x] File `erro_05.btw` tại cả hai vị trí `templates/erro/erro_05.btw` và `D:\PAT\Templates\erro_05.btw` chứa chính xác 12 Named SubStrings.
- [x] Mở template bằng BarTender COM qua Python và nạp giá trị qua `SetNamedSubStringValue` thành công 100% không phát sinh lỗi COM.
- [x] Xuất ảnh test nhãn in và kiểm chứng đọc ngược barcode:
  - Mã vạch 1D `Carton No`, `Item`, `Date Code`, `Lot Code`, `QTY` đọc lại khớp từng ký tự với dữ liệu nạp.
  - Mã 2D QR Code đọc lại ra đúng chuỗi 7 trường: `{CartonNo},{Item},{MPN},{Batch},{QTY},{DateCode},{LotCode}`.

## Blocked by

- [01-erro-05-reference-print-path](file:///d:/Workspace/NY_tagging_sys/.scratch/erro-05-integration/issues/01-erro-05-reference-print-path.md)
