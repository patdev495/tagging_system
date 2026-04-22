# REQUIREMENTS.md

## Milestone v2.0 Requirements

### Backend Refactoring
- [ ] **BACK-01**: Tách Customer router và service
- [ ] **BACK-02**: Tách Product router và service
- [ ] **BACK-03**: Tách Scan validation và Box orchestration router/service
- [ ] **BACK-04**: Tách Print XML generation router/service
- [ ] **BACK-05**: Tách History (Search/Reprint) router/service
- [ ] **BACK-06**: Tách Agent healthcheck router/service

### Frontend Refactoring
- [ ] **FRONT-01**: Tạo feature API modules riêng biệt (axios clients)
- [ ] **FRONT-02**: Tách CustomerSelect component
- [ ] **FRONT-03**: Tách ProductGrid component
- [ ] **FRONT-04**: Xây dựng useScanLogic composable (buffer, validation)
- [ ] **FRONT-05**: Tách BoxProgress và ScannedList components
- [ ] **FRONT-06**: Xây dựng usePrintAgent composable (Agent communication)
- [ ] **FRONT-07**: Tách History/EmergencyReprintModal component
- [ ] **FRONT-08**: Tách SettingsModal component
- [ ] **FRONT-09**: Tạo PackingStationPage orchestrator

## Future Requirements
- [ ] Auto-update product catalog from remote ERP
- [ ] Quản lý cấu hình Settings tại Backend (hiện tại lưu ở LocalStorage của Frontend)

## Out of Scope
- [ ] **Rewrite business logic**: This milestone focuses purely on structural refactoring.
- [ ] **Inventory Management**: Focus remains on packing/tagging.

## Traceability
(To be updated by roadmap)
