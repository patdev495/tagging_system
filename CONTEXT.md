# NY Tagging System

Hệ thống quản lý đóng gói và in ấn nhãn thùng hàng (Carton) tích hợp với phần mềm BarTender qua giao thức COM Automation.

## Language

**Customer**:
Tổ chức hoặc đối tác sở hữu các sản phẩm cần được đóng gói và dán nhãn.
_Avoid_: Client, đối tác, đối tác mua hàng

**Product**:
Một loại sản phẩm thuộc về một Customer, định nghĩa các quy tắc đóng gói (như số lượng mỗi thùng, đường dẫn file tem nhãn, tiền tố số sê-ri).
_Avoid_: SKU, mã hàng

**Carton**:
Một thùng hàng vật lý chứa các sản phẩm (Product), được đại diện bởi một mã số sê-ri thùng duy nhất (Carton SN).
_Avoid_: Hộp, thùng chứa, kiện hàng

**Carton SN**:
Mã số sê-ri duy nhất của Carton, thường bắt đầu bằng tiền tố `CN` (viết tắt của Carton Number), theo sau là ngày tháng (YYMM), ký tự phân biệt sản phẩm và số thứ tự tự tăng năm chữ số.
_Avoid_: Box SN, mã vạch thùng

**Carton Item**:
Một sản phẩm con riêng lẻ được quét bằng máy quét sê-ri để xếp vào thùng (Carton), được định danh bởi một mã sê-ri sản phẩm (Item SN).
_Avoid_: Serial sản phẩm, sê-ri quét

**Job Order**:
Mã lệnh sản xuất hoặc lệnh đóng gói dùng để nhóm nhiều Carton lại với nhau trong cùng một đợt chạy.
_Avoid_: Lệnh sản xuất, mã lô, Work order

**Job Order Carton Slot**:
Một vị trí thùng được cấp phát trước cho một Job Order, tương ứng với số thứ tự thùng từ 1 đến N (trong đó N là tổng số thùng tính toán được từ tổng số lượng sản phẩm của Job Order chia cho số lượng đóng gói tối đa của Product). Mỗi vị trí thùng có trạng thái là chờ quét hoặc đã quét.
_Avoid_: Số thùng thứ tự, slot thùng, vị trí hộp

**Print Agent**:
Ứng dụng chạy cục bộ trên máy tính client kết nối trực tiếp với động cơ BarTender COM để thực hiện lệnh in nhãn vật lý hoặc xuất PDF.
_Avoid_: Client app, ứng dụng máy in, máy in dịch vụ

**Printer**:
Thiết bị in nhãn vật lý (hoặc thiết bị ảo xuất PDF) nhận lệnh in từ Print Agent.
_Avoid_: Máy in, print device

**Origin Country**:
Quốc gia sản xuất thực tế của thùng hàng (ví dụ: `VN` - Việt Nam hoặc `CN` - Trung Quốc), quyết định xuất xứ in trên nhãn là "MADE IN VIETNAM" hay "MADE IN CHINA".
_Avoid_: Quốc gia sê-ri

**Reprint**:
Hành động in lại nhãn của một Carton đã được đóng gói trước đó. Hệ thống sẽ tạo một bản ghi Carton mới nhân bản từ Carton cũ với cờ `is_reprint` đặt là 1, giữ nguyên số Carton SN ban đầu để không làm tăng số thứ tự tự động của lô hàng.
_Avoid_: In bù, in mới, in đè

**Station ID**:
Mã định danh duy nhất của máy tính client hoặc trạm đóng gói thực hiện lệnh in (thường được lưu dưới dạng địa chỉ MAC hoặc địa chỉ IP của Client).
_Avoid_: MAC ID (trừ phi nói về phần cứng), IP máy, Terminal ID

**Template Type**:
Kiểu định dạng nhãn in được cấu hình cho Product. Hệ thống hỗ trợ hai loại chính: `standard` (chỉ hiển thị thông tin Carton và mã vạch chung) và `detailed` (hiển thị lưới sê-ri chi tiết của từng Carton Item bên trong, tối đa 40 dòng).
_Avoid_: Cấu hình tem, kiểu mẫu

**UPC**:
Mã vạch sản phẩm tiêu chuẩn (Universal Product Code) tương ứng với từng Product, được in trực tiếp lên nhãn Carton để nhận diện sản phẩm ở cấp độ bán lẻ.
_Avoid_: Mã vạch thùng, barcode sản phẩm


## Relationships

- Một **Customer** có thể có nhiều **Products** khác nhau.
- Một **Product** xác định số lượng đóng gói tối đa (`packed_qty`) và được đóng thành nhiều **Cartons**.
- Một **Carton** chứa nhiều **Carton Items** với số lượng bằng đúng `packed_qty` của Product (hoặc ít hơn nếu sản phẩm đó cho phép đóng thiếu `allow_partial`). Số lượng items trong một **Carton** tuyệt đối không được vượt quá `packed_qty`.
- Một **Carton** có thể thuộc về một **Job Order**.

## Example dialogue

> **Developer:** "Khi quét sản phẩm con vào **Carton**, nếu chưa đủ số lượng `packed_qty` quy định của **Product** thì hệ thống có cho phép xuất mã **Carton SN** để in nhãn không?"
> **Domain expert:** "Mặc định là không. Tuy nhiên, nếu cấu hình của **Product** đó cho phép `allow_partial`, chúng ta vẫn cho đóng thùng thiếu và in nhãn **Carton** bình thường."

## Flagged ambiguities

- **packed_by**: Trường `packed_by` trong bảng cartons thực chất đang lưu tên của **Printer** (Thiết bị in) chứ không phải thông tin của người đóng gói (Packer/Operator).
- **CN**: Ký tự `CN` ở tiền tố số sê-ri (`start_part`) là viết tắt của **Carton Number**, hoàn toàn độc lập với ký tự `CN` đại diện cho Trung Quốc (China) trong trường quốc gia sản xuất (`Origin Country` / `carton_origin`).
