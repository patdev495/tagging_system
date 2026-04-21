# Technology Stack

## Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database ORM**: SQLAlchemy 2.0
- **Database Driver**: pyodbc (ODBC Driver 18 for SQL Server)
- **Environment Management**: python-dotenv
- **Server**: Uvicorn
- **Package Manager**: uv

## Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Icons**: Lucide-Vue-Next
- **Styling**: Vanilla CSS (based on directory contents)

## Client Agent (Print Agent)
- **Language**: Python
- **Automation**: pywin32 (win32com) for BarTender COM automation
- **Communication**: HTTP Server (built-in `http.server`)
- **Printer Management**: win32print

## Infrastructure
- **Web Application Server**: Windows (likely, given BarTender and ODBC usage)
- **Database**: Microsoft SQL Server
- **Labeling**: BarTender Integration / SDK (COM)
