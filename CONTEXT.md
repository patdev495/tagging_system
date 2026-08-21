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

**Packing Mode**:
Chế độ xác thực và đóng gói của Product để kích hoạt in tem Carton:
- `item_scan`: Quét từng mã sê-ri con (Carton Item) cho đến khi đủ số lượng `packed_qty`.
- `weight_scale`: Đóng gói theo trọng lượng, đọc giá trị cân từ Scale; khi trọng lượng thực tế nằm trong dải `Weight Tolerance` và công nhân kích hoạt lệnh in, hệ thống sẽ sinh mã Carton SN và in tem.
_Avoid_: Kiểu đóng gói, loại scan, scan method

**Scale**:
Thiết bị cân điện tử kết nối với trạm đóng gói qua cổng truyền thông nối tiếp RS-232 / USB-to-Serial.
_Avoid_: Cân bàn, máy cân, bộ cảm biến

**Weight Reading**:
Giá trị trọng lượng thực tế đo được từ Scale tại thời điểm cân và in tem cho Carton.
_Avoid_: Số cân, trọng lượng đọc, scale value

**Weight Tolerance**:
Dải trọng lượng hợp lệ của Product (gồm trọng lượng chuẩn `target_weight` kèm sai số `min_weight` và `max_weight`), là điều kiện tiên quyết để hệ thống chấp thuận in tem cho Carton ở chế độ `weight_scale`.
_Avoid_: Biên độ cân, khoảng cân cho phép, dải sai số

**UPC**:
Mã vạch sản phẩm tiêu chuẩn (Universal Product Code) tương ứng với từng Product, được in trực tiếp lên nhãn Carton để nhận diện sản phẩm ở cấp độ bán lẻ.
_Avoid_: Mã vạch thùng, barcode sản phẩm


**Shipped Job Order Carton Slot**:
Một **Job Order Carton Slot** đã được hệ thống xuất hàng bên ngoài xác nhận là đã xuất. NY Tagging chỉ sử dụng trạng thái này để áp dụng các quy tắc nghiệp vụ, không quyết định việc xác nhận xuất hàng. Một Carton gắn với Job Order Carton Slot đã xuất hàng không được phép xóa.
_Avoid_: Carton đã in, Carton đã quét, Carton hoàn tất


## Relationships

- Một **Customer** có thể có nhiều **Products** khác nhau.
- Một **Product** xác định chế độ đóng gói (**Packing Mode**), số lượng đóng gói quy chuẩn (`packed_qty`), mẫu tem nhãn, và quy tắc sinh sê-ri (**Carton SN**).
- Với Product ở chế độ `item_scan`, một **Carton** chứa nhiều **Carton Items** với số lượng bằng đúng `packed_qty` (hoặc ít hơn nếu `allow_partial`).
- Với Product ở chế độ `weight_scale`, một **Carton** không lưu **Carton Items** riêng lẻ (số lượng items = 0) mà lưu trữ giá trị **Weight Reading** và thời gian in. Lệnh in chỉ được thực thi khi **Weight Reading** thỏa mãn **Weight Tolerance**.
- Một **Carton** được đóng mới trong hệ thống thuộc về một **Job Order** thông qua một **Job Order Carton Slot** đã được cấp phát trước.
- Một **Carton** gắn với **Shipped Job Order Carton Slot** không được phép xóa.

## Example dialogue

> **Developer:** "Khi quét sản phẩm con vào **Carton**, nếu chưa đủ số lượng `packed_qty` quy định của **Product** thì hệ thống có cho phép xuất mã **Carton SN** để in nhãn không?"
> **Domain expert:** "Mặc định là không. Tuy nhiên, nếu cấu hình của **Product** đó cho phép `allow_partial`, chúng ta vẫn cho đóng thùng thiếu và in nhãn **Carton** bình thường."
> 
> **Developer:** "Với sản phẩm đóng gói theo cân (**weight_scale**), nếu số cân không nằm trong dải **Weight Tolerance** thì hệ thống xử lý thế nào?"
> **Domain expert:** "Hệ thống phải chặn lệnh in, cảnh báo lỗi trọng lượng trên màn hình và không cấp phát số **Carton SN**."

## Flagged ambiguities

- **packed_by**: Trường `packed_by` trong bảng cartons thực chất đang lưu tên của **Printer** (Thiết bị in) chứ không phải thông tin của người đóng gói (Packer/Operator).
- **CN**: Ký tự `CN` ở tiền tố số sê-ri (`start_part`) là viết tắt của **Carton Number**, hoàn toàn độc lập với ký tự `CN` đại diện cho Trung Quốc (China) trong trường quốc gia sản xuất (`Origin Country` / `carton_origin`).
