# LOT theo ngày cấp Carton SN

## Mục tiêu

Mọi Carton của năm tem Erro (`erro_01`–`erro_05`) phải lưu LOT `YYYYMMDD` theo Local Server Time tại thời điểm hệ thống cấp Carton SN.

## Yêu cầu

- Backend là nguồn sự thật; không dùng LOT gửi từ giao diện hoặc LOT đã lưu cho Job Order.
- Hai Carton cùng Job Order được cấp mã ở các ngày khác nhau phải có LOT khác nhau tương ứng.
- Áp dụng cho cả luồng cân-in và tạo Carton Erro bởi Admin.
- LOT vẫn được lưu trên Carton; các quy tắc hiển thị tem hiện có không đổi.
