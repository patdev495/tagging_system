# Concerns and Technical Debt

## Monolithic Backend
- **Issue**: `main.py` handles everything: API routing, business logic, SN generation, and static file serving.
- **Risk**: Becomes unmaintainable as more features (inventory, reports) are added.
- **Recommendation**: Refactor to a modular/feature-based structure (e.g., `api/v1/endpoints/`, `core/`, `crud/`).

## Hardcoded Paths and Configuration
- **Issue**: Many paths like `C:\print_jobs` or BarTender template paths are hardcoded or defaults.
- **Risk**: Deployment errors across different station configurations.
- **Recommendation**: Move all environment-specific settings to `.env` or a database-backed configuration table.

## Printing Dependencies
- **Issue**: Complete reliance on BarTender and `pywin32`.
- **Risk**: Hard to port to other labeling systems or OS platforms.
- **Recommendation**: Abstract the printer interface so other engines (ZPL direct, Dymo) could be added.

## UI Response Time
- **Issue**: No immediate feedback during the async relay of BTXML to the local agent.
- **Risk**: Operator might scan twice if response is slow.
- **Recommendation**: Implement optimistic UI updates or clear visual loaders during the print handoff.

## Data Fragmentation
- **Issue**: Some logic for origin ("MADE IN VIETNAM") is hardcoded in Python strings.
- **Risk**: Inconsistency if labels change.
- **Recommendation**: Move static label text into a database-managed `labels` or `metadata` table.
