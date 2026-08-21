# Deployment Guide

Two deployment targets are supported:

1. **Docker Compose** (recommended) — Nginx serves the built SPA and proxies
   `/api` to a Gunicorn + Django container.
2. **Bare metal** — build the SPA, run Gunicorn, and front it with any reverse
   proxy.

## Production environment

Copy `backend/.env.example` and set strong values. In production the app
**fails fast** if placeholders are detected:

| Variable | Requirement |
| -------- | ----------- |
| `SECRET_KEY` | strong random value (`get_random_secret_key`) |
| `JWT_SECRET` | strong random value, distinct from `SECRET_KEY` |
| `ADMIN_PASSWORD` | required, strong |
| `DEBUG` | `False` (transport-security headers auto-enable) |
| `ALLOWED_HOSTS` | your domain(s) |
| `CORS_ALLOWED_ORIGINS` | your frontend origin(s), HTTPS in production |

With `DEBUG=False` the backend enables: `SECURE_SSL_REDIRECT`, HSTS,
`SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_REFERRER_POLICY=same-origin`,
`X_FRAME_OPTIONS=DENY` and secure session/CSRF cookies.

> `SECURE_SSL_REDIRECT` assumes the reverse proxy already terminates TLS and
> sets `X-Forwarded-Proto`. If you do not terminate TLS at the edge, set
> `SECURE_SSL_REDIRECT=False`.

## Docker Compose

```bash
cd studysync-ai
docker compose build
docker compose up -d
```

- Frontend: http://localhost:8080
- API:      http://localhost:8080/api

Set environment variables for the backend service (e.g. via `.env` at the repo
root or your CI secrets). The compose file wires `gunicorn config.wsgi` and
persists the SQLite database on a named volume.

### Migrations

The backend container runs `manage.py migrate` on start. To run it manually:

```bash
docker compose run --rm backend python manage.py migrate
```

## Bare metal

### Frontend

```bash
npm ci
npm run build          # emits dist/
```

Serve `dist/` with SPA fallback so deep links resolve to `index.html`
(e.g. Nginx `try_files $uri /index.html;`).

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000
```

### Example Nginx site

```nginx
server {
  listen 80;
  server_name studysync.example.com;

  location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location / {
    root /var/www/studysync/dist;
    try_files $uri /index.html;
  }
}
```

## Production checks

- `DEBUG=False` with real `SECRET_KEY` / `JWT_SECRET` (verified at startup).
- HTTPS everywhere; HSTS enabled when `SECURE_SSL_REDIRECT` is on.
- Rotating file logs are written to `backend/logs/app.log`.
- Login throttling protects the auth endpoints.
- Password validators require ≥8-char, non-common, non-numeric passwords.
