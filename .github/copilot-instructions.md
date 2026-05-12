---
name: "NORSU Website Workspace Instructions"
description: "Guides Copilot Chat in this Django project with code style, architecture, and common commands. Use when working on backend, frontend templates, data models, serializers, or tests."
applyTo: ["**/*"]
---

## Project Overview
- Django project: `norsu_dashboard` (settings, urls, wsgi/asgi).
- Main app: `dashboard` with models, views, admin, templates, static assets.
- Media-managed directories: `media/*` for uploaded content; `staticfiles/` for collected static.
- Key test suites: `dashboard/tests.py` and `tests/*` (end-to-end regressions, preservation tests).

## Run / Build / Test Commands
- `python manage.py runserver` (local dev server).
- `python manage.py makemigrations` / `python manage.py migrate` (DB migrations).
- `python manage.py test` (run Django tests).
- `python manage.py createsuperuser` (admin user setup).
- `python manage.py collectstatic --noinput` (static file collection).
- `python manage.py dumpdata` / `loaddata` as needed with JSON fixture files in `dashboard/data`.

## Common patterns
- Model fields and relations mostly in `dashboard/models.py`.
- Each content type may have dedicated migration files (`dashboard/migrations/00xx...`).
- Templates are in `dashboard/templates/dashboard/`; use Django template tags and context.
- Static assets are in `dashboard/static/dashboard/` and built for production in `staticfiles/`.
- Admin site customizations in `dashboard/admin.py`.

## Styling & conventions
- Prefer readable, short functions (first-line `def` + docstring if nontrivial).
- Database schema changes require new migration file with `makemigrations`.
- Keep business logic in Django app code (models/managers/services), not in templates.
- Use existing `tests` patterns (setup, assert status codes, content display) for regression coverage.

## Troubleshooting / Guardrails
- Don’t hardcode absolute URLs for static/media; use `static`/`media` template tags and `url` resolvers.
- Sensitive data in source control is disallowed; use env vars (if added) in `settings.py`.
- If tests fail, run with `--verbosity 2` and check `dashboard/tests` and `tests/` for known bug scenarios.

## Quick searches
- `dashboard/views.py`: route handlers and context to templates.
- `dashboard/tests/`: JavaScript/Python preservation tests show nonregression expectations.
- `dashboard/management/commands`: custom commands (e.g., `reset_admin_password`).

## Use when
- Modifying models, views, serialization, admin panels, or dashboards.
- Fixing content rendering in templates or media path issues.
- Improving or adding API endpoints for posts, programs, achievements.
- Writing or updating the regression tests in `tests/`.

## Example assistant prompts
1. "Add a migration for `Program` to store `is_featured` and create REST API filter by featured programs."
2. "Fix the bug where program `slug` collides on duplicate program names and preserve existing URL behavior." 
3. "Create UI unit tests for `ccje` program page links discovered in `tests/test_ccje_program_preservation.test.py`."

## Next customization ideas
- `AGENTS.md` custom agent for guided test triage: start server, run failing test, produce patch.
- `dashboard/tests.instructions.md` (applyTo: `dashboard/tests/**`) with explicit test writing patterns and fixtures.
- Hook to run `python manage.py test --keepdb` before PR checks.
