# Student Attendance Login

This Django app verifies student email existence in `kbc_users_data` and records attendance once per 24 hours.

## Local Setup

1. Create virtual environment and install requirements:
   - `python -m venv .venv`
   - `.\\.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
2. Create your env file from template:
   - `copy .env.example .env`
3. Update `.env` values (database, secret key, table/column names).
4. Run migrations:
   - `python manage.py migrate`
5. Run app:
   - `python manage.py runserver`
6. Open:
   - `http://127.0.0.1:8000/`

## API

- `POST /api/auth/student-login/`
- JSON body:
  - `{"email":"student@example.com"}`

## Health Check

- `GET /healthz/` returns:
  - `{"status":"ok"}`

## Deployment (Linux/PaaS)

This repo is ready for `gunicorn` using `Procfile`:

- `web: gunicorn email_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile -`

Recommended deploy steps:

1. Set environment variables from `.env.example` on your platform.
2. Ensure:
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS` contains your domain
   - `DJANGO_CSRF_TRUSTED_ORIGINS` contains `https://...` domain(s)
3. Run:
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
4. Serve only over HTTPS with a trusted certificate on your public domain.
