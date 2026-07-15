# AI Agent Backend

Flask backend for authenticated task management, optional OpenAI-assisted planning, Telegram notifications, and team performance tracking.

## Security notice

Credentials were previously committed to this repository. Removing them from the current branch does not revoke them or erase Git history. Rotate the exposed OpenAI key and Telegram bot token, replace the JWT secret, and update the deployment dashboard before using the service.

## What is included

- JWT authentication and role-based API access
- Task CRUD, filtering, pagination, and performance metrics
- Optional OpenAI task generation, assignment suggestions, and aggregate performance analysis
- Optional Telegram notifications
- Database readiness health check at `GET /api/health`
- Validated production configuration, restricted CORS, disabled-by-default public registration, response security headers, and CI secret scanning

## Local setup

```bash
cd backend
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Generate two strong independent secrets and add them to `backend/.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `SECRET_KEY`, `JWT_SECRET_KEY`, and the allowed frontend origin in `CORS_ORIGINS`. OpenAI and Telegram settings are optional.

Run the service:

```bash
python app.py
```

The API listens on `http://localhost:5000` by default.

## Configuration rules

Production startup fails when:

- `JWT_SECRET_KEY` or `SECRET_KEY` is missing, short, or still a placeholder
- `CORS_ORIGINS` is absent, contains `*`, or uses a non-HTTPS origin
- numeric limits fall outside their safe ranges

Public registration is disabled unless `ALLOW_PUBLIC_REGISTRATION=true`. Even when enabled, the public endpoint can create only `team` accounts and requires a password of at least 12 characters.

## Main endpoints

| Area | Endpoint |
|---|---|
| Health | `GET /api/health` |
| Authentication | `POST /api/auth/login`, `POST /api/auth/refresh`, `GET /api/auth/me` |
| Registration | `POST /api/auth/register` when explicitly enabled |
| Tasks | `/api/tasks` |
| AI planning | `/api/chat/generate-tasks`, `/api/chat/analyze-performance`, `/api/chat/suggest-assignment` |
| Telegram | `/api/telegram/status`, `/api/telegram/test`, `/api/telegram/send-message` |

Protected endpoints require `Authorization: Bearer <token>`.

## Tests

From the repository root:

```bash
python -m pip install -r backend/requirements.txt
python -m compileall -q backend scripts
python -m unittest discover -s backend/tests -p "test_*.py" -v
python scripts/secret_check.py
```

The tests cover fail-closed configuration, CORS restrictions, deterministic AI fallback behavior, provider-client compatibility, application startup, route registration, health readiness, registration policy, and security headers.

## Render deployment

`render.yaml` uses `backend/` as the service root and Gunicorn as the production server. Set the following in Render rather than committing values:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`, for example `https://your-frontend.example.com`
- `DATABASE_URL`
- optional `OPENAI_API_KEY`
- optional `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID`

Use persistent managed storage for production data. Render's local filesystem is not a durable database.

## Operational notes

- AI calls have bounded prompts, timeouts, limited retries, validated outputs, and deterministic non-AI fallbacks.
- The health endpoint checks database readiness without making external provider calls.
- Server-side 5xx responses redact internal `details` fields.
- Rotate any credential that has ever appeared in Git history, even after the file is cleaned.
