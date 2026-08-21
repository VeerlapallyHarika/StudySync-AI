# API Reference

The backend is a Django REST Framework app served under `/api/`. All JSON
requests must send `Content-Type: application/json`. Response payloads use the
camelCase shapes the React frontend consumes.

Base URL (local): `http://localhost:8000`

## Authentication

Two principal types exist: **admin** and **student**.

- Login returns a JWT **access** token (short-lived, default 30 min) and an
  **opaque refresh** token (default 7 days).
- Send the access token as `Authorization: Bearer <token>` on protected
  endpoints.
- Refresh endpoints rotate the token pair.
- Logout revokes the refresh token server-side.

### Error format

Non-2xx responses use:

```json
{ "error": "code", "message": "human readable message" }
```

401/403 from DRF permissions may use DRF's default `detail` shape.

### Rate limiting

| Scope   | Default rate | Applied to                       |
| ------- | ------------ | -------------------------------- |
| `anon`  | 120/hour     | unauthenticated requests         |
| `user`  | 1200/hour    | authenticated requests           |
| `login` | 10/minute    | all login / refresh / logout     |

## Admin authentication

### `POST /api/admin/login/`

Bootstraps the admin account on first use from environment variables.

```json
{ "email": "admin@studysync.ai", "password": "admin123" }
```

→ `200` `{ "access": "...", "refresh": "...", "profile": {...} }`

### `POST /api/admin/refresh/`

Body: `{ "refresh": "..." }` → `200` `{ "access": "...", "refresh": "..." }`

### `POST /api/admin/logout/`

Body: `{ "refresh": "..." }` → `204`

## Student authentication

### `POST /api/student/register/`

```json
{
  "studentId": "STU-001",
  "fullName": "Aarav Kumar",
  "email": "aarav@studysync.ai",
  "password": "optional-password",
  "department": "Computer Science",
  "year": "2nd Year",
  "section": "A",
  "learningPreference": "Visual",
  "availability": "Morning",
  "scores": { "Mathematics": 88, "Physics": 74, "Programming": 92, "Database": 81, "Operating Systems": 69 }
}
```

→ `201` profile + `{ access, refresh }`

### `POST /api/student/login/` · `POST /api/student/refresh/` · `POST /api/student/logout/`

Same contract as the admin equivalents.

### `GET /api/student/profile/` (Bearer)

Returns the full student profile, insights and current group.

### `PUT /api/student/profile/` (Bearer)

Update fields and/or `scores`; recomputes strengths, weaknesses and average.

### `GET /api/student/dashboard/` (Bearer)

Dashboard aggregate: stats, group, insights and notifications.

### `GET /api/student/insights/` (Bearer)

Personal AI insights: strengths, weaknesses, focus recommendations,
suggested study sessions and subject status.

### `POST /api/student/change-password/` (Bearer)

Body: `{ "currentPassword": "...", "newPassword": "..." }` → `200`

## Admin: students

All admin endpoints require an admin Bearer token.

### `GET /api/admin/students/`

Query params: `search`, `department`, `year`, `section`, `status`,
`sort`, `page`, `limit`. Paginated (`page`/`limit`, default page size 50).

### `GET /api/admin/student/<student_id>/`

Full detail including per-subject scores.

### `PUT /api/admin/student/<student_id>/`

Update fields or scores.

### `DELETE /api/admin/student/<student_id>/`

→ `204`

### `POST /api/admin/import-csv/`

`multipart/form-data` file field `file`. Accepts standard headers
(`student_id`, `name`, `email`, `department`, `year`, `section` and the five
subjects). Skips existing IDs/emails and all-zero score rows. Optionally
auto-generates groups when the `generate_groups` form field is `true`.

## Admin: dashboard, analytics, groups, reports

### `GET /api/admin/dashboard/`

Aggregate metrics, distributions, recent activity, latest registrations,
at-risk students and report export history.

### `GET /api/admin/analytics/`

Subject averages, department performance, group comparison, strength and
weakness distributions, students requiring improvement.

### `GET /api/admin/settings/`

Global settings singleton (`default_group_size`, K-Means parameters).

### `PUT /api/admin/settings/`

Update settings.

### `GET /api/admin/system-info/`

Runtime info (Python, Django, scikit-learn versions, database).

### `GET /api/admin/activities/`

Activity feed, `?limit=`.

### `POST /api/groups/generate/`

Body: `{ "group_size": 4 }` (3–4). Runs the ML pipeline:

1. standardize scores (`StandardScaler`)
2. pick `k` via elbow heuristic (silhouette when possible)
3. K-Means clustering
4. complementary matching
5. balancing (every student assigned; leftovers placed into the smallest group)
6. leader + recommendations

Returns `{ groups: [...], summary: {...} }` where `summary` includes
`quality` (elbow inertias, silhouette, best k), `duplicatesDetected` and
`missingData`.

### `GET /api/groups/`

Query params: `search`, `department`, `minPerformance`.

### `GET /api/groups/<id>/` · `PUT /api/groups/<id>/` · `DELETE /api/groups/<id>/`

### `DELETE /api/groups/delete-all/`

Removes every group and releases students.

### `GET /api/reports/`

Stored report payloads; filter with `from`, `to` (ISO dates), `department`,
`group`.

### `POST /api/reports/` · `POST /api/reports/generate/`

Builds and persists a fresh report (`generatedAt`, `generatedBy`, totals,
analytics and 7 sections including group performance).

### `POST /api/reports/<format>/`

Where `format` is `csv`, `excel` or `pdf`. Returns the file attachment.

## Notifications

### `GET /api/notifications/`

Role-scoped list (student notifications for students, admin for admins).

### `POST /api/notifications/<id>/read/`

### `POST /api/notifications/read-all/` → `{ "marked": n }`

### `DELETE /api/notifications/`

Clears the caller's notifications → `{ "deleted": n }`
