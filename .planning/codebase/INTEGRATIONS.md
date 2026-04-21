# Integrations

## Backend <-> MSSQL
- Connected via `sqlalchemy` and `pyodbc`.
- Uses `ODBC Driver 18 for SQL Server`.
- Connection string includes `Encrypt=no;TrustServerCertificate=yes`.
- Database schema managed via `models.py` (SQLAlchemy models).

## Backend <-> Client Agent (Print Agent)
- The backend generates BTXML (BarTender XML) scripts.
- The backend *does not* trigger printing directly; it returns the BTXML to the frontend.
- The frontend (Axios) sends the BTXML to the local Print Agent running on `localhost:1234`.

## Client Agent <-> BarTender
- The Print Agent uses `win32com.client` to automate BarTender.
- It opens `.btw` template files and injects data into Named SubStrings.
- It triggers `PrintOut()` to send jobs to Windows printers.
- It also logs XML jobs to `C:\print_jobs` as a backup/audit trail.

## Frontend <-> Backend
- Standard REST API integration.
- Backend serves the static frontend files from `frontend/dist`.
- CORS is enabled for development (`allow_origins=["*"]`).
