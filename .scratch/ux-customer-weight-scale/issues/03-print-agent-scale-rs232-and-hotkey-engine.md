# 03. Print Agent Scale RS-232 & Hotkey Engine

Status: ready-for-agent

## What to build
Tích hợp động cơ giao tiếp Cân điện tử và Bắt phím tắt toàn cục vào `print_agent_v2`:
- Nhúng `SerialEngine` đọc luồng byte liên tục từ cổng COM RS-232 với cơ chế `auto_reconnect = 2.0s`.
- Parser bóc tách gói tin trọng lượng: trích xuất giá trị số `weight`, đơn vị `kg`/`g`, cờ ổn định `is_stable`, cờ trừ bì `is_tare`, lọc bỏ các dòng header nhiễu.
- Nhúng `GlobalHotkeyListener` sử dụng Win32 `RegisterHotKey` (mặc định `F9`) với cơ chế chống dội phím `debounce = 400ms`.
- Mở các REST API trên Print Agent (port 8080):
  - `GET /scale/status`: Trạng thái kết nối COM (`connected`, `port`, `baudrate`, `is_streaming`).
  - `GET /scale/current`: Trọng lượng tức thời mới nhất, đơn vị, và cờ ổn định.
  - `POST /scale/tare`: Gửi lệnh trừ bì `b"T\r\n"`.
  - `POST /scale/zero`: Gửi lệnh zero `b"Z\r\n"`.
  - `POST /scale/config`: Cập nhật cấu hình cổng COM, baudrate, và hotkey.
- Hỗ trợ cơ chế Mock Mode trên môi trường không có cổng COM vật lý để phục vụ kiểm thử.

## Acceptance criteria
- [x] Print Agent khởi động thành công và tự động kết nối cổng COM cấu hình trong `config.json`.
- [x] Endpoint `GET /scale/current` trả về dữ liệu cân dạng JSON đúng cấu trúc và thời gian thực (< 100ms độ trễ).
- [x] Bấm phím tắt `F9` kích hoạt sự kiện trigger ngay cả khi cửa sổ web hoặc ứng dụng khác đang unfocus.
- [x] Khi rút cáp COM, engine tự động chuyển trạng thái reconnecting và phục hồi ngay khi cắm lại cáp.

## Blocked by
None - can start immediately
