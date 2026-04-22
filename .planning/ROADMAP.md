# ROADMAP.md

## Milestone 1: Foundation & Packing Station MVP

**Goal**: Build a functional packing station that can scan items, generate S/Ns, and record data to MSSQL 2008.

### Phase 1: Tech Stack & Database (1-3)
- [x] 1. Backend: Initialize FastAPI and setup MSSQL 2008 connection (`pyodbc` or `ceODBC`).
- [x] 2. Database: Create/Verify tables for Customers, Products, Carton_History, and Item_History.
- [x] 3. Frontend: Initialize Vue 3 project and setup basic layout.

### Phase 2: Packing Logic (4-6)
- [ ] 4. Logic: Implement Carton S/N generator according to rules.
- [ ] 5. UI: Develop the Customer/Product selection and Scanning interface.
- [ ] 6. State: Implement real-time item counting and threshold detection (QTY reached).

### Phase 3: Printing & QR Integration (7-9)
- [x] 7. Printing: Research and implement Bartender Integration (e.g., via XML file generation).
- [x] 8. QR Code: Implement logic to encode/decode carton contents.
- [x] 9. UAT: End-to-end test from scan to printed label.

---
## Milestone 2: Feature-Based Architecture Refactoring (v2.0)
**Goal**: Modularize the codebase into feature-based modules to support scalability and maintainability.

### Phase 11: Backend Scaffold & Read-Only Features
**Goal**: Thiết lập cấu trúc lõi backend và tách các tính năng đọc dữ liệu.
**Requirements**: BACK-01, BACK-02, BACK-05
**Success Criteria**:
1. Thư mục `src/features/` và `src/core/` được tạo.
2. Các endpoint `/customers`, `/products`, `/cartons/search` hoạt động thông qua router mới.
3. Chạy được UI cũ mà không bị lỗi đối với các endpoint này.

### Phase 12: Backend Core Workflow
**Goal**: Tách hoàn toàn logic tạo Box và Print XML.
**Requirements**: BACK-03, BACK-04, BACK-06
**Success Criteria**:
1. Logic `get_next_carton_sn` và `create_carton` chuyển sang thư mục `box`.
2. Logic `generate_btxml` và `reprint_carton` chuyển sang thư mục `print`.
3. Giao dịch lưu dữ liệu và khóa `with_for_update` hoạt động an toàn.

### Phase 13: Frontend Logic Extraction
**Goal**: Tách layer API và logic (composables) trên frontend.
**Requirements**: FRONT-01, FRONT-04, FRONT-06
**Success Criteria**:
1. `api.js` được chia nhỏ thành các file trong `features/*/api.js`.
2. Logic buffer quét và validate được tách thành `useScanLogic`.
3. Logic gọi Agent được tách thành `usePrintAgent`.

### Phase 14: Frontend UI Extraction
**Goal**: Tách PackingStation.vue thành các UI components nhỏ gọn và ghép nối bằng Orchestrator.
**Requirements**: FRONT-02, FRONT-03, FRONT-05, FRONT-07, FRONT-08, FRONT-09
**Success Criteria**:
1. Không còn tồn tại `PackingStation.vue` nguyên khối, thay vào đó là `PackingStationPage.vue` đóng vai trò nhạc trưởng.
2. Tất cả tính năng hiện tại (chọn khách, quét, hiển thị lỗi, in lại khẩn cấp, cài đặt) đều hoạt động trơn tru trên cấu trúc mới.

---
## Milestone 999: Backlog
- [ ] Auto-update product catalog from remote ERP if needed.
- [ ] Support for multiple locations (VN vs CN selection).
