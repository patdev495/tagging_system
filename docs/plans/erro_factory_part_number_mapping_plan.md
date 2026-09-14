# Kế hoạch: Mapping Factory P/N cho tem Erro

**Trạng thái:** Sẵn sàng bàn giao để triển khai tiếp  
**Ngày:** 2026-09-14  
**Nguồn dữ liệu:** `D:/PAT/Templates/ERRO_ITEM_list.xlsx` — chỉ năm sheet PD cuối; bỏ qua `EERO产品清单` và `格式贴纸`.

## 1. Mục tiêu

Công nhân tại trạm Erro nhập hoặc quét **Factory P/N** (`internal_factory_part_number`, 厂内料号, ví dụ `1LAE0009D2U004MAAR`). Hệ thống phải xác định chính xác Product và loại tem cần in.

Không được chọn tem từ SKU như `840-00092`, cũng không được dùng **Factory Item Code** legacy (`115-...`) để chọn tem.

Loại tem được suy ra từ Product sau khi Factory P/N đã được resolve:

| Bản vẽ nguồn | Erro template type |
|---|---|
| `PD014736` | `erro_01` |
| `PD027504` | `erro_02` |
| `PD024364` | `erro_03` |
| `PD027032` | `erro_04` |
| `PD016906` | `erro_05` |

## 2. Phát hiện quyết định kiến trúc

Năm sheet PD chỉ có ảnh nhúng, không có bảng dữ liệu Excel thông thường. Đọc các ảnh cho thấy **một Product có nhiều Factory P/N hợp lệ**. Ví dụ:

- `G111D1A` có ít nhất `1LAX0005F2U001MAAP` và `1LAX0005F2U001MAAR` trong `PD027032`.
- `2M21-00508-0004H` có nhiều mã `1LAE...` trong `PD024364`.

Vì vậy, một cột duy nhất `products.internal_factory_part_number` không đủ: chọn một mã sẽ làm mất các mã còn lại. Không được tự ý chỉ lấy mã đầu tiên làm dữ liệu chính.

## 3. Mô hình dữ liệu đích

Tạo bảng `product_internal_factory_part_numbers` (tên có thể điều chỉnh theo convention repo):

| Cột | Kiểu/qui tắc | Mục đích |
|---|---|---|
| `id` | PK | Khoá kỹ thuật |
| `product_id` | FK → `products.id`, NOT NULL | Product được nhận diện |
| `customer_id` | FK → `customers.id`, NOT NULL | Phân vùng theo khách hàng |
| `internal_factory_part_number` | `VARCHAR(100)`, NOT NULL | Mã được nhập/quét |
| `source_drawing_code` | `VARCHAR(20)`, NOT NULL | `PD014736`… để audit nguồn |
| `created_at`, `updated_at` | theo chuẩn model hiện hữu | Audit |

Ràng buộc và index:

- `UNIQUE(customer_id, internal_factory_part_number)` — một Factory P/N của Erro chỉ trỏ tới một Product.
- Index `(customer_id, internal_factory_part_number)` phục vụ lookup trạm in.
- Chuẩn hoá trước khi lưu và lookup: `trim`, sau đó `uppercase`.
- Với release này, chỉ tạo/quản lý mapping cho Customer **Erro**.

Quan hệ nghiệp vụ:

```text
Factory P/N (nhiều mã) ──> một Product ──> một Erro template type
```

`Factory Item Code` legacy vẫn có thể giữ trên Product như thông tin tham chiếu, nhưng không tham gia lookup hoặc chọn mẫu tem.

## 4. Xử lý phần triển khai đã tồn tại

Một phần implementation đang có trong working tree đã giả định quan hệ 1-1:

- Cột `products.internal_factory_part_number`.
- Unique constraint/index trên `(customer_id, internal_factory_part_number)` của Product.
- Endpoint `GET /api/v1/products/resolve-internal-factory-part-number` lookup trực tiếp trên Product.
- Form admin bắt buộc một Factory P/N cho Product Erro.
- UI trạm in đã dùng lookup Factory P/N thay vì chọn Product bằng tay.

Giữ UI lookup tại trạm in, nhưng thay backend và form admin để dùng bảng mapping. Không được tiếp tục import dữ liệu vào cột Product 1-1.

Migration chuyển tiếp:

1. Tạo bảng mapping và unique constraint/index mới.
2. Chép mỗi giá trị không rỗng hiện có từ `products.internal_factory_part_number` sang bảng mapping, gắn `product_id` và `customer_id`; dùng `source_drawing_code = 'LEGACY'` hoặc nullable nếu team không muốn giá trị giả.
3. Chạy idempotent: không tạo bản ghi trùng khi chạy lại.
4. Chuyển lookup/API sang bảng mới.
5. Bỏ validate “mỗi Erro Product phải có đúng một Factory P/N”. Một Product có thể có 0 mapping trong giai đoạn data cleanup, hoặc nhiều mapping khi đã cấu hình.
6. Chỉ xoá cột cũ và unique index cũ trong migration sau khi production đã chạy ổn và dữ liệu legacy được xác nhận.

## 5. Backend work breakdown

### 5.1 Model và migration

- Thêm SQLAlchemy model mapping, relationship `Product.internal_factory_part_numbers`.
- Viết migration SQLite và SQL Server theo cơ chế migration tự quản trong `backend_v2/src/core/database.py`.
- Dùng partial/regular unique index phù hợp database hiện tại.
- Xử lý collision legacy có kiểm soát: nếu cùng Customer/cùng mã nhưng trỏ hai Product khác nhau, dừng migration/import với lỗi rõ ràng, không chọn ngẫu nhiên.

### 5.2 Service và API

- Chuyển `resolve_erro_product_by_internal_factory_part_number` sang join mapping → Product → Customer.
- Vẫn trả Product đầy đủ để UI hiện tên hàng, SKU và template type.
- `404`: mã chưa cấu hình cho Erro.
- `409`: mapping trùng/phá vỡ unique data (phòng thủ cho database cũ).
- API quản trị cần hỗ trợ:
  - lấy mapping theo Product;
  - thêm một hay nhiều mã;
  - cập nhật mã và nguồn PD;
  - xoá mapping có xác nhận;
  - validate trùng theo Customer.
- Quyền API quản trị phải theo RBAC hiện có; endpoint trạm in giữ phạm vi read-only cần thiết.

### 5.3 Schema

- Bổ sung DTO riêng cho mapping, không nhồi danh sách mapping vào payload Product nếu ảnh hưởng các client khác.
- Nếu có thêm nested response trong Product, duy trì tương thích ngược với client cũ.
- Tài liệu API phải xác định `internal_factory_part_number` là mã worker scan, không phải SKU hay `factory_item_code`.

## 6. Giao diện

### 6.1 Trạm đóng gói Erro

- Giữ trường nhập/quét Factory P/N hiện có.
- Khi resolve thành công: hiện Product/SKU/loại tem chỉ đọc.
- Không tự chọn Product đầu tiên, không cho worker chọn tay để tránh in nhầm.
- Chỉ bật in khi mapping resolve thành công và dữ liệu in khác hợp lệ.
- Nút “Đổi mã hàng” xoá Product đang chọn và yêu cầu quét/nhập lại.

### 6.2 Quản trị Product

- Thay ô bắt buộc duy nhất `internal_factory_part_number` bằng phần “Factory P/N áp dụng”.
- Hỗ trợ thêm từng dòng và dán nhiều dòng; mỗi mã có nguồn PD.
- Hiện danh sách mapping đang thuộc Product; hỗ trợ xoá có xác nhận.
- Hiện lỗi trùng ngay trong form; không dùng mã `115-...` để chọn template.
- Giữ các trường legacy hiện hữu chỉ với vai trò reference/audit.

## 7. Chuẩn bị dữ liệu từ workbook ảnh

Không nạp trực tiếp OCR vào DB. Tạo một staging file có review workflow, ví dụ `docs/data/erro_factory_part_number_mapping_review.csv`, gồm:

| source_drawing_code | internal_factory_part_number | source_product_identifier | resolved_product_id | template_type | status | confidence | notes |
|---|---|---|---|---|---|---|---|

Quy trình:

1. Chỉ dùng ảnh trong năm sheet PD; không đọc/không suy luận từ hai sheet đầu.
2. Trích Factory P/N và Product identifier/SKU hiển thị cùng dòng ảnh.
3. Chuẩn hoá mã Factory P/N.
4. Resolve Product hiện hữu bằng identifier chính xác.
5. Gắn template type theo sheet nguồn, sau đó kiểm tra Product có template type khớp.
6. Phân loại:
   - `READY`: đọc rõ, Product duy nhất, template đúng;
   - `MISSING_PRODUCT`: chưa có Product tương ứng;
   - `CONFLICT`: một Factory P/N dẫn tới nhiều Product hoặc template không khớp;
   - `NEEDS_REVIEW`: OCR/ảnh không đủ chắc chắn.
7. Chỉ import `READY` sau khi người phụ trách duyệt file staging.

Lưu ý: các Product không có UPC hoặc chưa xuất hiện trong catalog không được tự tạo dựa trên OCR nếu thiếu dữ liệu bắt buộc của Product. Chúng phải ở `MISSING_PRODUCT` và được bổ sung qua luồng admin chuẩn.

## 8. Import có kiểm soát

Tạo script/import service idempotent từ staging CSV:

- Mặc định chạy `--dry-run`, in tổng số theo `source_drawing_code` và `status`.
- Chỉ cho `--apply` sau khi staging đã duyệt.
- Từ chối toàn bộ row `CONFLICT`, `MISSING_PRODUCT`, `NEEDS_REVIEW`.
- Ghi log/audit: file nguồn, thời điểm, người chạy, số create/skip/fail.
- Có rollback rõ ràng theo batch/import run nếu môi trường có audit model phù hợp; tối thiểu export danh sách IDs vừa tạo để xoá có mục tiêu khi cần.

## 9. Kiểm thử theo TDD

### Backend

- Một Factory P/N resolve Product/template đúng.
- Nhiều Factory P/N resolve về cùng một Product.
- Cùng Customer + cùng mã không thể map sang hai Product.
- Mã không tồn tại trả `404` với thông điệp vận hành rõ ràng.
- Case/whitespace được chuẩn hoá giống nhau ở create và lookup.
- Mã Customer khác không được resolve dưới Erro.
- Legacy migration chép đúng một mapping, chạy lại không duplicate.
- Import dry-run/apply và các trạng thái `READY`, `MISSING_PRODUCT`, `CONFLICT`, `NEEDS_REVIEW`.

### Frontend

- Quét mã hợp lệ hiển thị Product đúng và cho phép in.
- Mã không hợp lệ không set Product và không cho in.
- Nút đổi mã xoá trạng thái resolve.
- Admin thêm nhiều mapping; lỗi trùng được hiển thị.

### Regression

- Chạy full backend pytest và frontend test/build.
- Kiểm thử tay một mã đã xác nhận cho từng loại `erro_01` đến `erro_05` trước khi in production.
- Không sửa các thay đổi Erro 03 không liên quan khi xử lý mapping; working tree hiện đã có thay đổi chưa commit.

## 10. Tiêu chí nghiệm thu

1. Worker chỉ cần Factory P/N để ra Product và đúng loại tem.
2. Mọi Factory P/N đã duyệt trong năm PD sheets được lookup duy nhất.
3. Một Product chứa được nhiều Factory P/N.
4. Hai sheet đầu workbook không có dữ liệu nào được import.
5. Không còn luồng chọn template dựa trên SKU hoặc Factory Item Code legacy.
6. Các mã chưa chắc chắn/thiếu Product không thể lặng lẽ đi vào production mapping.
7. Bảng báo cáo import nêu rõ tổng mã theo từng PD và toàn bộ ngoại lệ.

## 11. Thứ tự thực hiện khuyến nghị

1. Viết test RED cho mapping 1-n và migration legacy.
2. Thêm bảng/model/migration, làm test backend xanh.
3. Chuyển endpoint lookup sang mapping table.
4. Cập nhật form admin thành quản lý danh sách mapping.
5. Chạy regression backend/frontend.
6. Trích workbook ảnh vào staging CSV; review và bổ sung Product còn thiếu.
7. Dry-run import, duyệt kết quả, rồi apply.
8. UAT tại trạm bằng đại diện của cả năm loại tem.
9. Chỉ sau giai đoạn ổn định mới lên migration xoá/deprecate cột Product 1-1 cũ.

## 12. Điểm cần xác nhận trước khi agent triển khai

- Bảng mapping là nguồn xác thực duy nhất cho lookup Erro (khuyến nghị: **có**).
- Có giữ cột `products.internal_factory_part_number` trong một release chuyển tiếp hay loại khỏi schema ngay sau khi migration hoàn tất.
- Người/phòng ban nào duyệt các dòng `NEEDS_REVIEW` và `MISSING_PRODUCT` trước `--apply`.
- `source_drawing_code` có bắt buộc cho cả mapping legacy hay cho phép `NULL`.
