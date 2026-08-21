# Installation Guide

This guide covers a from-scratch local setup of StudySync AI on Windows,
macOS and Linux. Production deployment is covered in
[DEPLOYMENT.md](./DEPLOYMENT.md).

## Prerequisites

| Tool      | Version          |
| --------- | ---------------- |
| Node.js   | 18+ (20 LTS recommended) |
| npm       | 9+              |
| Python    | 3.10 – 3.12     |
| git       | optional        |

## 1. Clone and prepare

```bash
git clone <your-repository-url> studysync-ai
cd studysync-ai
```

## 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# Create local environment (never commit this file)
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux

python manage.py migrate
python manage.py runserver    # http://localhost:8000
```

The first request to `POST /api/admin/login/` bootstraps the admin account
from the `ADMIN_EMAIL` / `ADMIN_PASSWORD` environment values.

### Backend tests

```bash
python manage.py test
```

The suite covers auth, students, groups, reports, notifications, insights
and the ML quality helpers (85 tests).

## 3. Frontend

Open a second terminal:

```bash
npm install
npm run dev       # http://localhost:5173
```

The frontend calls the API at `http://localhost:8000` by default. Point it
elsewhere with a `.env.local`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Frontend tests and build

```bash
npm test            # Vitest (28 tests)
npm run build       # strict TypeScript check + production build
npm run preview     # preview the built app
```

## 4. Verify

1. Open http://localhost:5173 — the marketing site loads.
2. Sign in at `/admin/login` with your `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
3. Import students via **Students → Import CSV** (see the template under
   `docs/` or the admin UI hint) or register a student from `/student/register`.
4. Open **Groups → Generate Groups** to run the ML pipeline.
5. Export a report from **Reports**.

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `ModuleNotFoundError: no module named 'sklearn'` | Reinstall backend deps: `pip install -r requirements.txt` |
| CORS errors in the browser | Add your frontend origin to `CORS_ALLOWED_ORIGINS` in `backend/.env` |
| `ImproperlyConfigured: Production requires...` | You started with `DEBUG=False` and placeholder secrets — set real `SECRET_KEY` / `JWT_SECRET` / `ADMIN_PASSWORD` |
| Login requests return 429 | You hit the login rate limit (`THROTTLE_RATE_LOGIN`, default 10/minute per IP) — wait a minute |
