# Hướng dẫn Deploy NY Tagging System lên Render

Tài liệu này hướng dẫn cách triển khai hệ thống lên **Render** sử dụng gói Miễn phí (Free Tier) với cấu hình dịch vụ hợp nhất (Unified Service).

## 1. Chuẩn bị dữ liệu (Local)
Bạn đã thực hiện bước này thành công. Đảm bảo file `backend_v2/database.db` đã có dữ liệu demo (5 bản ghi mỗi loại sản phẩm).

```powershell
cd backend_v2
uv run python export_to_sqlite.py
```

## 2. Đẩy mã nguồn lên GitHub
Hệ thống Render sẽ lấy code trực tiếp từ GitHub. Bạn cần:
1. Tạo một Repository mới trên GitHub.
2. Commit toàn bộ mã nguồn (bao gồm cả file `database.db` và `render.yaml`).
3. Push lên GitHub.

```powershell
git add .
git commit -m "feat: chuẩn bị deploy lên render với dữ liệu demo"
git push origin master
```

## 3. Triển khai lên Render (Sử dụng Blueprint)
Chúng ta đã có file `render.yaml`, giúp việc cấu hình trở nên cực kỳ đơn giản:

1. Đăng nhập vào [Render Dashboard](https://dashboard.render.com/).
2. Nhấn nút **New +** và chọn **Blueprint**.
3. Kết nối với tài khoản GitHub của bạn và chọn Repository `NY_tagging_sys`.
4. Render sẽ tự động phát hiện file `render.yaml` và hiển thị các dịch vụ cần tạo.
5. Nhấn **Apply**.

## 4. Sau khi triển khai thành công
- Render sẽ cung cấp cho bạn một URL có dạng `https://ny-tagging-sys.onrender.com`.
- Bạn có thể truy cập URL này để sử dụng hệ thống.
- Cả Backend (API) và Frontend (UI) đều chạy trên cùng một URL này.

## Các lưu ý quan trọng (Render Free Tier):
1. **Dữ liệu không bền vững (Ephemeral Storage)**: 
   - Vì sử dụng gói Miễn phí, ổ đĩa của Render sẽ bị xóa sạch mỗi khi service restart hoặc deploy mới.
   - Dữ liệu bạn đã đính kèm trong `database.db` khi push code sẽ luôn tồn tại.
   - Tuy nhiên, bất kỳ dữ liệu mới nào bạn thêm trực tiếp trên web (như tạo thêm khách hàng mới) sẽ bị mất khi service restart.
2. **Tự động ngủ (Spin down)**:
   - Nếu không có lượt truy cập trong 15 phút, service sẽ tự động "ngủ" để tiết kiệm tài nguyên.
   - Lượt truy cập đầu tiên sau khi ngủ sẽ mất khoảng 30s - 1 phút để hệ thống khởi động lại.
3. **Giới hạn Docker**:
   - Quá trình build Docker có thể mất vài phút vì hệ thống cần cài đặt các driver MSSQL (để tương thích ngược) và build Frontend Vue 3.

---
*Chúc bạn triển khai thành công!*
