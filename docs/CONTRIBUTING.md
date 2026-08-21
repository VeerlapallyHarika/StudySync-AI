# Contributing Guide

Thanks for contributing to StudySync AI. Please read the root
[README](../README.md) first for the product and architecture overview.

## Development setup

Follow [INSTALLATION.md](./INSTALLATION.md). In short:

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate   # (or source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver

# Frontend (second terminal)
npm install
npm run dev
```

## Workflow

1. Create a branch off `main` (e.g. `feat/xxx` or `fix/yyy`).
2. Make focused commits with clear messages.
3. Add or update tests for every change.
4. Run the full checks below before opening a PR.

## Checks

Every PR must pass:

```bash
# Backend
cd backend
.venv\Scripts\python.exe manage.py test        # 85 tests

# Frontend
npm test                                        # 28 Vitest tests
npm run build                                   # strict TypeScript + Vite build
```

## Project layout

```
src/
  components/          glass primitives, charts, dialogs, skeletons
  pages/admin/         admin dashboard, students, groups, reports, analytics, settings
  pages/student/       student dashboard, insights, notifications, profile, settings
  services/            adminService, studentService (fetch + auth headers)
  ml/                  client-side ML fallbacks (k-means, strengths, matching)
backend/
  authentication/      JWT issuance, Principal, permissions, login throttling
  students/            Student model, repository, services, CSV import
  groups/              group generation pipeline + payload serialization
  ml/                  quality (elbow/silhouette), clustering, strength analysis
  reports/             report builder + CSV/Excel/PDF exporters
  notifications/       notifications + activity log
  insights/            analytics, settings singleton, system info
  utils/               logging, throttles, exception handler
```

## Conventions

- **Backend**: service/repository layering — views stay thin, business logic
  lives in services, data access in repositories. Module-scoped
  `get_logger('app')` instead of bare `logging`.
- **Frontend**: typed services per role, `useMemo` for derived data, route
  lazy loading, and the `liquid-glass` design system.
- **Payload shape**: the API is camelCase; keep new fields consistent with the
  existing `AdminStudent` / `AdminGroup` / `ReportData` contracts.
- **Secrets**: never commit `.env`. Copy from `.env.example` and keep secrets
  in your environment.

## Reporting issues

Include the failing command, the exact error, and the browser/OS when relevant.
