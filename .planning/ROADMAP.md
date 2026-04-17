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
- [ ] 7. Printing: Research and implement Bartender Integration (e.g., via XML file generation).
- [ ] 8. QR Code: Implement logic to encode/decode carton contents.
- [ ] 9. UAT: End-to-end test from scan to printed label.

---
## Milestone 999: Backlog
- [ ] Auto-update product catalog from remote ERP if needed.
- [ ] Support for multiple locations (VN vs CN selection).
