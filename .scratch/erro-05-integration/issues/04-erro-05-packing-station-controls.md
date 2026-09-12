Status: completed

# Erro 05 packing station controls and production run flow

## What to build

Xây dựng và kiểm thử end-to-end quy trình vận hành tại Trạm Cân Đóng Gói (Packing Station / Weight Scale UI) cho các sản phẩm dòng `erro_05`.

Quy trình trạm cân cho `erro_05`:
1. Công nhân chọn một trong các mã sản phẩm `erro_05` tại trạm cân.
2. Popup bắt buộc nhập PO Number và Lot Number được bypass (cho phép để trống mặc định tương tự `erro_02` và `erro_03`). Nếu công nhân có nhập PO hoặc Batch, hệ thống ghi nhận vào bản ghi Carton và trường tương ứng.
3. Trường `Date Code` tự động hiển thị và tính toán theo tuần hiện tại `YYWW`.
4. Trường `Lot Code` tự động hiển thị và tính theo ngày hiện tại `YYYYMMDD`, cho phép công nhân chỉnh sửa linh hoạt trên giao diện ca nếu xưởng có quy định mã lô riêng.
5. Khi đặt thùng lên bàn cân, hệ thống đọc trọng lượng từ Scale. Nếu nằm trong dải Weight Tolerance, công nhân nhấn In (`F9`), hệ thống cấp phát sê-ri tháng tiếp theo và gửi lệnh in.
6. Lệnh in hoàn tất, hệ thống sẵn sàng cho thùng tiếp theo.

## Acceptance criteria

- [x] Trạm đóng gói nhận diện đúng chế độ `weight_scale` cho Product `erro_05`.
- [x] Cho phép hoàn tất đóng gói và in tem khi `po_number` để rỗng.
- [x] `Date Code` và `Lot Code` tự động sinh chuẩn xác theo giờ máy chủ địa phương.
- [x] Kiểm thử nhiều lần cân liên tiếp xác nhận số sê-ri tăng đều đặn trong tháng (`50001`, `50002`, ...), không bị nhảy cóc hoặc trùng số.
- [x] Giao diện khóa cứng không cho phép sửa đổi `pkg_prefix` của sản phẩm.

## Blocked by

- [02-erro-05-bartender-template-configuration](file:///d:/Workspace/NY_tagging_sys/.scratch/erro-05-integration/issues/02-erro-05-bartender-template-configuration.md)
- [03-erro-05-catalog-and-38-products-seed](file:///d:/Workspace/NY_tagging_sys/.scratch/erro-05-integration/issues/03-erro-05-catalog-and-38-products-seed.md)
