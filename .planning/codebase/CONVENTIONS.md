# Conventions

## Coding Standards
- **Python**: PEP 8 followed (mostly). Uses 4 spaces for indentation.
- **JavaScript**: Vue 3 Composition API style. Use ES modules.
- **HTML/CSS**: BEM-like naming for classes where possible, otherwise standard Vue scoped styling.

## Naming Conventions
- **Database Tables**: `dbo.tableName` (PascalCase or camelCase observed).
- **API Routes**: `/api/{resource}` plural for collections, singular for instances.
- **File Names**: `snake_case.py` for Python, `camelCase.js` or `PascalCase.vue` for frontend.

## Database Patterns
- Uses SQLAlchemy `declarative_base`.
- Manual sequence generation using `func.max()` with `with_for_update()` to ensure uniqueness.
- Relationships defined via `back_populates`.

## UI/UX Patterns
- Dark mode primary theme (based on rich aesthetics goal).
- Focus on keyboard efficiency (auto-focus on scan inputs).
- Toast notifications for feedback (Success/Error).
