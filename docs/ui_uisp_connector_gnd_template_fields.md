# Quy ước trường tem UI UISP-Connector-GND

Khi tạo Product, chọn `template_type=detailed`, `template_path=carton_UISP_Connector_GND.btw`, `packing_mode=item_scan` và `packed_qty=50`. Backend gửi 50 Item SN theo đúng thứ tự quét. Nếu Product cho phép đóng thiếu, các ô còn lại nhận một dấu cách.

Đổi tên các Named Data Source trong mẫu BarTender như sau:

| Tên hiện tại | Tên mới | Giá trị hệ thống gửi |
| --- | --- | --- |
| `uvc` | `ItemName` | Tên Product ở dòng trên |
| `udop` | `ItemName2` | Tên Product ở dòng dưới |
| `name2` | `QTY` | Số lượng thực tế ở dạng `N PCS`, giống các tem UI detailed khác |
| `zxname` | `CartonSN` | Carton SN thuần cho barcode |
| `zxname1` | Dùng chung `CartonSN` | Liên kết với nguồn `CartonSN`, thêm chữ `Carton S/N:` cố định trước giá trị |
| `name1.2` | `MAC_ID` | `MAC ID (N)` với N là số lượng thực tế |
| `ewmname` | `QR_Content` | Danh sách Item SN, ngăn cách bằng dấu xuống dòng |
| `cpname1`…`cpname50` | `SN_1`…`SN_50` | Item SN tương ứng, hoặc một dấu cách nếu ô trống |

Backend còn gửi `UPC` theo Product, `Origin` là `Made in Vietnam` hoặc `Made in China`, và `ItemName3` là tên Product. Trong mẫu được cung cấp, UPC `810010075802` và dòng `MADE IN VIETNAM` là nội dung cố định, chưa phải Named Data Source. Nếu muốn hai giá trị này thay đổi theo Product/Carton, hãy sửa chúng thành trường động `UPC` và `Origin`.

Giữ chữ `QTY:` nhưng bỏ chữ `PCS` cố định trong mẫu GND, vì giá trị `QTY` đã chứa ` PCS`. Carton SN mẫu `CN25033500010` gợi ý `start_part=CN`, `middle_part=35`; cần xác nhận quy tắc số thùng trước khi tạo Carton thật. Sau khi đổi tên, hãy xuất một tem thử và quét đối chiếu đủ 50 barcode cùng QR.
