# Testing

## Current Testing Strategy
The project currently relies on manual verification, developer-led UAT, and standalone utility scripts.

## Available Utility Scripts
- **Backend (`backend_v2/scratch/`)**:
  - `list_routes.py`: Lists all registered FastAPI routes for auditing.
- **Client Agent (`print_agent_v2/`)**:
  - Contains internal logic for verifying COM connections to BarTender.

## Simulation Environment
- **Backend**: Uvicorn with `--reload` for real-time development.
- **Frontend**: Vite dev server with TypeScript type checking (`vue-tsc`).
- **Debugging**: Extensive logging in both `backend_v2` and `print_agent_v2`.

## Verification Loop
1.  **Code Review**: Changes are reviewed for architectural alignment.
2.  **Manual UAT**: Core workflows (Scan -> Pack -> Print) are verified manually after each feature update.
3.  **Static Analysis**: ESLint and TypeScript compiler for frontend quality.

## Future Testing Roadmap
- [ ] **Unit Tests**: Implement Pytest for sequence generation logic in the backend.
- [ ] **Component Tests**: Implement Vitest for critical UI components (e.g., `ScanBuffer`, `SettingsModal`).
- [ ] **E2E Tests**: Use Playwright to simulate full scan-to-print workflows.
