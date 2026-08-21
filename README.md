# StudySync AI — Peer-to-Peer Study Group Agent

StudySync AI is an ML-powered platform that profiles students from their academic
scores and automatically assembles **balanced, complementary study groups** using
K-Means clustering, strength/weakness detection and complementary skill matching.

It ships as a cinematic glassmorphism **React + TypeScript** frontend backed by a
**Django REST Framework** API with a scikit-learn grouping pipeline.

---

## Features

- **Student onboarding** — register with subject scores, learning preference and
  availability; live JWT auth with session persistence.
- **AI group generation** — K-Means clustering + complementary matching builds
  balanced groups, picks a team leader, and writes per-group recommendations.
- **Admin dashboard** — live metrics, department/strength/weakness distributions,
  recent activity, latest registrations, at-risk students and report export history.
- **Admin students** — search, department/year/section filters, sort, add/edit/delete,
  CSV import, per-student score tables and pagination.
- **Admin groups** — search by group or member, department filter, sorting, a
  per-member **subject heatmap**, full AI recommendation cards and group analytics charts.
- **Reports** — generate, preview, filter by date/department/group, and export to
  CSV, Excel or PDF.
- **Analytics** — subject averages, department performance, group comparison and
  students requiring improvement.
- **Student experience** — dashboard, personal AI insights, notifications,
  profile, and settings with notification preferences.
- **Error & loading states** — custom 404/500/unauthorized pages, premium
  shimmer skeletons, and a branded route-level loader.
- **Accessibility** — skip links, labelled inputs, focus-visible rings, keyboard
  support and reduced-motion support.
- **Performance** — route-level code splitting, vendor chunk splitting, table
  pagination, memoized filters and memoized chart data.
- **ML quality controls** — automatic best-`k` selection via the elbow
  heuristic and silhouette analysis, feature standardization, complementary
  matching, and duplicate / missing-data detection before generation.
- **Security** — JWT access + revocable refresh tokens, RBAC permissions
  (`IsAdmin` / `IsStudent`), login rate limiting, password validators,
  production TLS headers, hardened CORS, and startup fail-fast on placeholder
  secrets.

---

## Tech Stack

| Layer    | Tech |
| -------- | ---- |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, react-router-dom, lucide-react |
| Backend  | Django 5.1, Django REST Framework, PyJWT, pandas, numpy, scikit-learn, reportlab, openpyxl |

---

## Architecture

```
studysync-ai/
├── src/                       React + TypeScript frontend
│   ├── api/                   API endpoint constants
│   ├── components/            Glass UI primitives, charts, dialogs, skeletons
│   ├── components/admin/      Admin-specific cards, toasts, stat counters, heatmap
│   ├── hooks/                 Page title, group generation flow
│   ├── layouts/               SiteLayout (public) and AdminLayout (app shell)
│   ├── ml/                    Frontend ML fallbacks (kmeans, feature engineering,
│   │                          complementary matching, group balancer, recommendations)
│   ├── pages/                 Routed pages for public, student and admin areas
│   ├── services/              API helpers (adminService, studentService)
│   ├── types/                 Shared TypeScript models (admin.ts, student.ts)
│   ├── utils/                 Constants, storage keys, mock data
│   ├── App.tsx                Route map with lazy loading + guard
│   └── index.css              Liquid glass design system + keyframes
└── backend/                   Django REST API
    ├── authentication/        Admin + student JWT auth
    ├── config/                Settings, URLs, .env.example
    ├── groups/                Group generation service, views, models
    ├── insights/              Analytics, settings, system info
    ├── ml/                    Strength detection, clustering, matching helpers
    ├── notifications/         Activity log + notification dispatch
    ├── reports/               Report generation and CSV/Excel/PDF export
    ├── students/              Student model, repository, services, views
    └── utils/                 Shared logging utilities
```

### ML pipeline

1. **Preprocessing** — clean and normalise raw subject scores.
2. **Quality analysis** — elbow / silhouette checks pick a reliable `k`;
   duplicates and missing scores are reported before clustering.
3. **Feature engineering** — per-student averages, strength/weakness flags,
   standardized feature vectors.
4. **K-Means clustering** — group students into near-homogeneous clusters.
5. **Complementary matching** — pair students whose skills cover each other's gaps.
6. **Group balancing** — rebalance for size and skill coverage; every student
   is assigned, leftovers land in the smallest group.
7. **Recommendations** — overall skill level, leader rationale, meeting pattern,
   improvement suggestions and a learning recommendation string.

---

## Getting Started

### 1. Backend (Django)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                # Windows   (cp .env.example .env on macOS/Linux)
python manage.py migrate
python manage.py runserver            # http://localhost:8000
```

### 2. Frontend (Vite)

```bash
npm install
npm run dev                           # http://localhost:5173
```

The frontend calls the API at `http://localhost:8000` by default. Override it
with a `VITE_API_BASE_URL` environment variable if the backend runs elsewhere.

---

## Environment

Copy `backend/.env.example` to `backend/.env` and adjust:

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `SECRET_KEY` | — | Django secret key |
| `DEBUG` | `True` | Django debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Host allow-list |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Frontend origin(s) |
| `JWT_SECRET` | — | JWT signing secret (change in production) |
| `JWT_ACCESS_MINUTES` | `30` | Access token lifetime |
| `JWT_REFRESH_DAYS` | `7` | Refresh token lifetime |
| `ADMIN_EMAIL` | `admin@studysync.ai` | Admin login email |
| `ADMIN_PASSWORD` | `admin123` | Admin login password |
| `DEFAULT_STUDENT_PASSWORD` | `studysync` | Fallback student password |

---

## Accounts

- **Admin** — sign in at `/admin/login` with `admin@studysync.ai` / `admin123`.
- **Student** — register at `/student/register` (or self-signup from the dashboard).

---

## Key Routes

| Route | Page |
| ----- | ---- |
| `/` | Home |
| `/about`, `/features`, `/contact` | Public pages |
| `/student/register`, `/student/login` | Student auth |
| `/student/dashboard`, `/student/insights`, `/student/notifications`, `/student/profile`, `/student/settings` | Student area |
| `/admin/login` | Admin auth |
| `/admin/dashboard`, `/admin/students`, `/admin/groups`, `/admin/groups/:id`, `/admin/reports`, `/admin/analytics`, `/admin/settings` | Admin area (guarded) |
| `/500`, `/unauthorized` | Error pages |

---

## Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start the Vite dev server |
| `npm run build` | Type-check (`tsc`) and build for production |
| `npm test` | Run the Vitest test suite |
| `npm run preview` | Preview the production build |
| `python manage.py test` | Run the Django test suite |

---

## Testing

- **Backend** — Django `TestCase` suites (85 tests) cover auth, student
  registration/profile/CSV import, group generation and recommendations,
  ML quality helpers, reports (incl. filters and exports), notifications
  and insights.
- **Frontend** — Vitest (28 tests) covers the ML utilities and core
  components; `npm run build` runs strict TypeScript checking across the app.

---

## Documentation

- [INSTALLATION](./docs/INSTALLATION.md) — local setup from scratch
- [API](./docs/API.md) — endpoint reference and auth/rate-limit contract
- [DEPLOYMENT](./docs/DEPLOYMENT.md) — Docker Compose and bare-metal production
- [CONTRIBUTING](./docs/CONTRIBUTING.md) — workflow, conventions, checks

---

## Deployment Notes

The frontend is a static SPA: configure your host for SPA fallback (serve
`index.html` for unknown paths) so deep links do not 404 on refresh. When
deploying the API, set a strong `SECRET_KEY`, a long random `JWT_SECRET`,
`DEBUG=False`, and a production `ALLOWED_HOSTS` + `CORS_ALLOWED_ORIGINS`.
With `DEBUG=False` the app refuses to start on placeholder secrets. See
[DEPLOYMENT](./docs/DEPLOYMENT.md) for Docker Compose and bare-metal options.

---

## Design

The UI follows the MotionSites cinematic glass template: a `liquid-glass` design
system, Instrument Serif display type, gradient orbs and scroll-reveal motion,
preserved exactly from the base template and extended with shimmer skeletons,
focus rings and reduced-motion fallbacks.
