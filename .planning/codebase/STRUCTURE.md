# Project Structure

## Root Directory
- `backend/`: FastAPI source code, database models, and build scripts.
- `frontend/`: Vue 3 source code, components, and assets.
- `client_agent/`: Standalone Python print agent.
- `print_jobs/`: Default local directory for logging print XMLs.
- `.planning/`: GSD workflow state and codebase mapping.

## Backend Layout
- `main.py`: Main entry point, API routes, and static file serving.
- `models.py`: SQLAlchemy database models.
- `schemas.py`: Pydantic models for request/response validation.
- `database.py`: DB engine setup and session management.
- `build_backend.bat`: Scripts for packaging the backend into an executable.

## Frontend Layout (src/)
- `components/`: Reusable UI components.
- `layouts/`: Page layouts (e.g., standard layout).
- `services/`: API client logic (axios wrappers).
- `App.vue`: Root component.
- `main.js`: App initialization.

## Client Agent Layout
- `print_agent.py`: The core agent logic.
- `test_bt.py`: Utility for testing BarTender COM connection.
- `build/`, `dist/`: PyInstaller output directories.
