# Testing

## Current Testing Strategy
The project currently relies on manual verification and standalone utility scripts rather than a comprehensive automated test suite.

## Available Utility Scripts
- **Backend**:
  - `seed.py`: Populates basic master data (Customers, Products).
  - `seed_full.py`: Populates larger datasets for stress testing.
  - `clear_test_data.py`: Wipes transaction data while preserving master data.
  - `debug_print.py`: Simulates printing logic.
- **Client Agent**:
  - `test_bt.py`: Verifies COM connection and BarTender license.
  - `test_bt_parse.py`: Tests XML parsing and data extraction from BTXML.

## Simulation Environment
- Standard Uvicorn reload server for backend development.
- Vite dev server with proxying for frontend.
- Log-based debugging via `agent_activity.log` and backend `logger`.

## Future Testing Needs
- Unit tests for S/N generation logic (FastAPI + Pytest).
- Component testing for scanning workflow (Vue + Vitest).
- Integration tests between Frontend -> Agent -> BarTender.
