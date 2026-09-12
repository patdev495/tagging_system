# NY Tagging System

Hệ thống quản lý đóng gói và in ấn nhãn thùng hàng (Carton) tích hợp với phần mềm BarTender qua giao thức COM Automation.

## Language

**Customer**:
Tổ chức hoặc đối tác sở hữu các sản phẩm cần được đóng gói và dán nhãn. Mỗi Customer có mã định danh kỹ thuật (`code`, ví dụ: `UI`, `ERRO`) và tên hiển thị chính thức (`name`, ví dụ: `Universal Instruments`, `Erro`). Erro là Customer duy nhất cho năm mẫu tem `erro_01`–`erro_05`; A11 chỉ là tên lịch sử cần nhận diện khi chuyển dữ liệu, không phải Customer hoặc nhánh cần hiển thị/lọc báo cáo.
_Avoid_: Client, đối tác, đối tác mua hàng

**Erro Label Template Code**:
Mã kỹ thuật ổn định xác định một trong năm mẫu tem của Customer Erro: `erro_01`, `erro_02`, `erro_03`, `erro_04`, hoặc `erro_05`. Ba mã đang hoạt động ánh xạ từ hệ thống cũ theo thứ tự: `a11` → `erro_01`, `a11_tem2` → `erro_02`, và `a11_tem3` → `erro_03`. `erro_04` và `erro_05` chưa có cấu hình hoặc mẫu tem. Cả năm mã đều cấm in lại và chỉ được cấp số tem tự động, tăng tuần tự.
_Avoid_: Tem A11, loại tem A11

**Product**:
Một loại sản phẩm thuộc về một Customer, định nghĩa các quy tắc đóng gói (như số lượng mỗi thùng, đường dẫn file tem nhãn, tiền tố số sê-ri).
_Avoid_: SKU, mã hàng

**Carton**:
Một thùng hàng vật lý chứa các sản phẩm (Product), được đại diện bởi một mã số sê-ri thùng duy nhất (Carton SN).
_Avoid_: Hộp, thùng chứa, kiện hàng

**Carton SN**:
Mã số sê-ri duy nhất của Carton, được sinh theo quy tắc cấu hình của từng Customer/Product:
- Với khách hàng UI: Tiền tố `start_part` (mặc định `CN` - Carton Number), theo sau là ngày tháng (`YYMM`), ký tự phân biệt sản phẩm và số thứ tự 5 chữ số reset hàng tháng.
- Với khách hàng Erro - `erro_01` (`PD014736`): Tiền tố định danh sản phẩm (VD: `VHK0010237`), theo sau là ngày tháng (`YYMM`) và số thứ tự 6 chữ số reset hàng năm (PKG ID).
- Với khách hàng Erro - `erro_02` (`PD027504`): Mã SSCC 18 chữ số theo chuẩn GS1 `037033907{seq:07d}{cd}` với số thứ tự sê-ri 7 chữ số tăng liên tục không reset, mã kiểm tra tính theo Modulo 10.
- Với khách hàng Erro - `erro_03` (`PD024364`): Mã định danh thùng xuất xưởng Luxshare NME gồm 17 ký tự: mã nhà cung ứng 7 chữ số (mặc định xưởng Việt Nam là `1012665`), thời gian sản xuất 6 chữ số (`YYMMDD`), và số thứ tự 4 chữ số reset theo ngày.
_Avoid_: Box SN, mã vạch thùng, PKG ID (trừ phi gọi theo tên trường trên tem Erro 01)

**Erro 04 Carton Sequence**:
Bộ đếm chung, tăng đơn điệu và không reset cho mọi Product dùng Erro Label Template Code `erro_04`. Bộ đếm được biểu diễn bằng bốn ký tự base-32 từ `0001` đến `ZZZZ`, dùng `0`-`9` và chữ cái trừ `I`, `L`, `O`, `U`; tiền tố `H` (CAT6A) hoặc `K` (CAT5E) không tạo bộ đếm riêng.
_Avoid_: Số thứ tự theo ngày, bộ đếm H/K riêng, số thập phân bốn chữ số

**Erro 04 Carton ID Prefix**:
Ký tự đầu của Carton SN thuộc Product `erro_04`, được cấu hình bắt buộc theo Product: `H` cho CAT6A và `K` cho CAT5E. Đây là metadata ổn định, không được suy luận từ SKU hay SKU Description.
_Avoid_: Tự nhận diện loại cáp từ tên sản phẩm, pkg_prefix

**SSCC**:
Mã định danh công-ten-nơ vận chuyển duy nhất theo tiêu chuẩn GS1 (Serial Shipping Container Code, 18 chữ số), bắt đầu bằng `(00)`, dùng làm mã định danh Carton SN cho tem thùng xuất xưởng CM của khách hàng Erro (`erro_02`).
_Avoid_: Pallet code, mã công-ten-nơ, mã vận đơn

**ASIN**:
Mã số định danh tiêu chuẩn của Amazon (Amazon Standard Identification Number) gồm 10 ký tự chữ và số, được cấu hình cố định theo từng Product của khách hàng Erro xuất khẩu cho hệ thống Amazon eero.
_Avoid_: Mã Amazon, mã sàn, product ASIN

**Date Code**:
Mã thời gian sản xuất gồm 2 chữ số cuối của năm và 2 chữ số của tuần trong năm theo chuẩn ISO (`YYWW`, ví dụ tuần 34 năm 2026 là `2634`).
_Avoid_: Tuần sản xuất, mã tuần, date text

**Manufacturing Date**:
Ngày sản xuất của Carton, lấy theo Local Server Time tại thời điểm in. Với `erro_04`, trường `Date` in theo `YYMMDD` và các thành phần ngày trong Carton SN được mã hóa từ chính ngày này theo bảng PD027032.
_Avoid_: Date Code, ngày nhập tay, ngày đơn hàng

**Lot Number**:
Mã số lô sản xuất (Lot# / 批號) áp dụng cho đợt đóng hàng của Job Order, được nhập một lần khi bắt đầu phiên đóng gói và áp dụng cho toàn bộ các Carton trong cùng lô. Với `erro_04`, Lot Number là bắt buộc cho Production Run để phục vụ truy xuất nguồn gốc, nhưng không được in trên tem.
_Avoid_: Mã mẻ, mã batch, số lô con

**PO Number**:
Mã đơn đặt hàng của khách hàng (Purchase Order / 訂單號) tương ứng với đợt sản xuất, được cấu hình hoặc nhập khi mở ca đóng hàng. Với Erro Label Template Code `erro_04`, đây là trường bắt buộc, được nhập một lần khi mở Production Run và áp dụng cho toàn bộ Carton của đợt đó.
_Avoid_: Mã PO, order ref, mã hợp đồng

**Mfr P/N**:
Mã số chứng nhận sản xuất hoặc tiêu chuẩn nội bộ (承认书编号 / NYS Spec No, ví dụ: `NYS5998`), được cấu hình cố định cho từng Product.
_Avoid_: Mã chứng nhận, mã spec, internal part number

**Revision**:
Phiên bản khách hàng áp dụng cho Product, được in tại trường `Rev` của tem `erro_04`. Revision là metadata bắt buộc theo Product `erro_04`, không có giá trị mặc định dùng chung.
_Avoid_: Revision mặc định, revision của file tem

**Factory P/N**:
Mã số thành phẩm hoặc vật tư nội bộ nhà máy (厂内料号, ví dụ: `1LAE0009D2U004MAAR`), dùng để đối chiếu với hệ thống ERP/BOM của Nien Yi và phục vụ tra cứu sản phẩm trên Web UI.
_Avoid_: Mã xưởng, ERP code, material code, part number nội bộ

**Factory Item Code**:
Mã ITEM nội bộ của nhà máy dùng để đối chiếu Product với bảng nguồn, ví dụ `115-00020` của `erro_04`. Đây là metadata riêng không in trên tem và không đồng nhất với SKU hoặc Supplier PN.
_Avoid_: SKU, Supplier PN, mã in nhãn

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
Hành động in lại nhãn của một Carton đã được đóng gói trước đó. Hệ thống sẽ tạo một bản ghi Carton mới nhân bản từ Carton cũ với cờ `is_reprint` đặt là 1, giữ nguyên số Carton SN ban đầu để không làm tăng số thứ tự tự động của lô hàng. Quy trình này áp dụng cho Customer UI; đối với Customer Erro, hành động Reprint bị cấm hoàn toàn theo quy định kiểm soát tem nhãn chống trùng lặp.
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
Thiết bị cân điện tử kết nối với trạm đóng gói qua cổng truyền thông nối tiếp RS-232 / USB-to-Serial ở chế độ phát luồng liên tục (Continuous Streaming). Các thao tác định chuẩn điểm không (Zero) và trừ bì (Tare) được thực hiện trực tiếp trên bàn phím vật lý của đầu cân.
_Avoid_: Cân bàn, máy cân, bộ cảm biến

**Weight Reading**:
Giá trị trọng lượng thực tế đo được từ Scale tại thời điểm cân và in tem cho Carton.
_Avoid_: Số cân, trọng lượng đọc, scale value

**Weight Tolerance**:
Dải trọng lượng hợp lệ của Product (xác định bởi ngưỡng tối thiểu `min_weight` và tối đa `max_weight`), là điều kiện tiên quyết để hệ thống chấp thuận in tem cho Carton ở chế độ `weight_scale`. Các Product `erro_04` được khởi tạo với dải 0–10 kg và có thể được Admin điều chỉnh theo thông số thực tế.
_Avoid_: Biên độ cân, khoảng cân cho phép, dải sai số

**UPC**:
Mã vạch sản phẩm tiêu chuẩn (Universal Product Code) tương ứng với từng Product, được in trực tiếp lên nhãn Carton để nhận diện sản phẩm ở cấp độ bán lẻ.
_Avoid_: Mã vạch thùng, barcode sản phẩm

**Role**:
Vai trò phân quyền của tài khoản truy cập vào phân hệ Quản trị (Admin):
- `Admin`: Toàn quyền thao tác hệ thống (tạo/sửa/xóa Customer, Product, xóa Carton, kích hoạt Reprint, cấu hình).
- `QA`: Quyền chỉ đọc (Read-only). Được phép xem Dashboard, danh mục Customer/Product, theo dõi tiến độ Job Order/PO, tra cứu sê-ri, xem lịch sử và xuất báo cáo dữ liệu. Bị chặn toàn bộ thao tác ghi/sửa/xóa và in lại.
_Avoid_: Phân quyền động, user type, level, cấp bậc

**Production Run**:
Đợt sản xuất gom nhóm các Carton được đóng trong ca làm việc, được nhận diện qua **Job Order** (ở chế độ `item_scan`) hoặc bộ đôi **PO Number** & **Lot Number** (ở chế độ `weight_scale`). Với `erro_04`, người vận hành có thể sửa PO Number và Lot Number trong khi chạy; mỗi Carton giữ snapshot của hai giá trị tại lúc in, không hồi tố các Carton đã in.
_Avoid_: Phiên làm việc, ca chạy, mẻ hàng

**Shipped Job Order Carton Slot**:
Một **Job Order Carton Slot** đã được hệ thống xuất hàng bên ngoài xác nhận là đã xuất. NY Tagging chỉ sử dụng trạng thái này để áp dụng các quy tắc nghiệp vụ, không quyết định việc xác nhận xuất hàng. Một Carton gắn với Job Order Carton Slot đã xuất hàng không được phép xóa.
_Avoid_: Carton đã in, Carton đã quét, Carton hoàn tất


## Relationships

- Một **Customer** có thể có nhiều **Products** khác nhau.
- Một **Product** xác định chế độ đóng gói (**Packing Mode**), số lượng đóng gói quy chuẩn (`packed_qty`), mẫu tem nhãn, và quy tắc sinh sê-ri (**Carton SN**).
- Với Product ở chế độ `item_scan` (khách hàng UI), một **Carton** thuộc về một **Job Order** thông qua một **Job Order Carton Slot** đã được cấp phát trước. Sau khi một Carton hoàn tất in tem và xác thực, hệ thống phải dừng ở trạng thái chờ mở thùng mới. Công nhân bắt buộc phải xác nhận chuyển sang Job Order Carton Slot tiếp theo (bấm nút "Thùng tiếp theo" hoặc nhấn phím Space) mới được quét hàng tiếp; nếu trạm đang tồn tại lỗi quét thì không được phép chuyển thùng cho đến khi lỗi được xóa.
- Với Product ở chế độ `weight_scale` (khách hàng Erro), một **Carton** được đóng liên tục trong **Production Run** gắn với **PO Number** và **Lot Number** mà không bắt buộc phải cấp phát Job Order Carton Slot trước. Đối với `erro_02` và `erro_03`, **PO Number** cho phép để rỗng mặc định và người vận hành có thể tùy chọn chỉnh sửa trên giao diện ca đóng gói.
- Một **Carton** gắn với **Shipped Job Order Carton Slot** không được phép xóa.
- Người dùng đăng nhập vào phân hệ Quản trị (Admin) mang một **Role** (`Admin` hoặc `QA`). Tài khoản `QA` chỉ có quyền đọc và xuất báo cáo; các thao tác tạo/sửa/xóa Customer/Product, xóa Carton và kích hoạt Reprint bị chặn ở cả tầng giao diện lẫn API backend.
- Mọi mốc thời gian đóng gói (**Carton** `created_at`, **Job Order Carton Slot** `scanned_at`, **Date Code** `YYWW`, sê-ri `YYMM`) đều được ghi nhận theo **Giờ Cục bộ (Local Server Time)** của máy chủ nhà máy để đảm bảo tính nhất quán giữa màn hình vận hành, báo cáo thống kê ca sản xuất và nhãn in BarTender.

## Example dialogue

> **Developer:** "Khi quét sản phẩm con vào **Carton**, nếu chưa đủ số lượng `packed_qty` quy định của **Product** thì hệ thống có cho phép xuất mã **Carton SN** để in nhãn không?"
> **Domain expert:** "Mặc định là không. Tuy nhiên, nếu cấu hình của **Product** đó cho phép `allow_partial`, chúng ta vẫn cho đóng thùng thiếu và in nhãn **Carton** bình thường."
> 
> **Developer:** "Với sản phẩm đóng gói theo cân (**weight_scale**), nếu số cân không nằm trong dải **Weight Tolerance** thì hệ thống xử lý thế nào?"
> **Domain expert:** "Hệ thống phải chặn lệnh in, cảnh báo lỗi trọng lượng trên màn hình và không cấp phát số **Carton SN**."
> 
> **Developer:** "Khi một **Carton** trong chế độ `item_scan` đã đóng đủ và in tem xong, công nhân có thể quét ngay sản phẩm của thùng tiếp theo không?"
> **Domain expert:** "Không, hệ thống phải yêu cầu bấm xác nhận sang thùng tiếp theo (qua nút trên màn hình hoặc phím tắt Space) để tránh quét nhầm vào thùng cũ hoặc chưa kịp chuẩn bị thùng mới. Đặc biệt, nếu trạm đang có lỗi quét chưa được xóa thì không cho phép chuyển thùng."


## Flagged ambiguities

- **packed_by**: Trường `packed_by` trong bảng cartons thực chất đang lưu tên của **Printer** (Thiết bị in) chứ không phải thông tin của người đóng gói (Packer/Operator).
- **CN**: Ký tự `CN` ở tiền tố số sê-ri (`start_part`) là viết tắt của **Carton Number**, hoàn toàn độc lập với ký tự `CN` đại diện cho Trung Quốc (China) trong trường quốc gia sản xuất (`Origin Country` / `carton_origin`).
- **NYS6248**: Dòng sản phẩm NYS6248 trong Bảng 1 của bản vẽ PD027032 thiếu thông tin UPC và SKU nên chưa được tạo vào danh mục Erro 04; được ghi nhận là dữ liệu chờ bổ sung từ khách hàng (pending source data).
