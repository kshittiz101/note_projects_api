# note_projects_api

A production-oriented **Django REST Framework** backend for a Google Keep–style notes application. It provides JWT-based authentication, owner-scoped CRUD for notes, pagination, filtering/search, and auto-generated OpenAPI documentation. The project follows 12‑factor configuration via `.env` with `python-decouple` and `dj-database-url`.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Database](#database)
- [API Reference](#api-reference)
- [Quality and Tooling](#quality-and-tooling)
- [Deployment Notes](#deployment-notes)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

`note_projects_api` is a clean, extensible DRF codebase for building a personal notes service similar to Google Keep. It is designed for learning and real-world use: secure defaults, operational endpoints, documentation, and developer tooling.

---

## Features

- JWT authentication (access/refresh) with SimpleJWT
- Owner-only permissions for notes (object-level access control)
- Cursor pagination for scalable listings
- Filtering, ordering and search on note fields
- OpenAPI schema with Swagger/Redoc via drf-spectacular
- Unified error response model
- Health check endpoint for DB/cache readiness
- 12‑factor configuration using `.env`

---

## Architecture

```
Client  ──(JWT)──>  Django REST Framework API
                     ├─ PostgreSQL / SQLite (dj-database-url)
                     ├─ Redis (optional, cache / Celery broker)
                     └─ Celery worker (optional, async jobs)
```

---

## Tech Stack

- **Language**: Python 3.11+
- **Frameworks**: Django 5.x, Django REST Framework
- **Auth**: djangorestframework-simplejwt
- **Docs**: drf-spectacular (OpenAPI/Swagger/Redoc)
- **Config**: python-decouple, dj-database-url
- **Filtering**: django-filter
- **Dev Tooling**: Pipenv, pytest, black, ruff, isort, pre-commit
- **Optional**: Redis (cache/throttling), Celery (async tasks)

---

## Project Structure

```
note_projects_api/
  config/                 # Django settings, URLs, ASGI/WSGI
    __init__.py
    settings.py
    urls.py
    asgi.py
    wsgi.py
  notes/                  # Notes app (models, serializers, views, tests)
    __init__.py
    admin.py
    apps.py
    models.py
    serializers.py
    views.py
    urls.py
    tests/
  users/                  # User-related customizations (optional)
  manage.py
  Pipfile
  Pipfile.lock
  .env.example
  .pre-commit-config.yaml
  README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Pipenv
- (Optional) PostgreSQL and Redis installed locally

### Setup

```bash
# Clone the repository
git clone <your-repo-url> note_projects_api
cd note_projects_api

# Create environment and install dependencies
pip install --user pipenv
pipenv --python 3.11
pipenv install django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular python-decouple dj-database-url
pipenv install --dev pytest pytest-django black ruff isort pre-commit

# Environment variables
cp .env.example .env
# Edit .env as needed

# Database and admin user
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser

# Run the development server
pipenv run python manage.py runserver
```

Open admin at `http://127.0.0.1:8000/admin/` to manage notes and users.

---

## Configuration

Configuration is managed via environment variables loaded by `python-decouple`.

`.env.example`:

```
# Security
SECRET_KEY=change-this
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
# If unset, SQLite is used by default via dj-database-url
# DATABASE_URL=postgres://user:password@localhost:5432/notes_db

# Timezone
TIME_ZONE=Asia/Kathmandu
```

The project reads `DATABASE_URL` if provided; otherwise it falls back to SQLite for local development.

---

## Database

The core domain model is `Note`:

- `title: CharField(200)`
- `content: TextField`
- `owner: ForeignKey(User)`
- `created_at: DateTimeField(auto_now_add=True)`
- `updated_at: DateTimeField(auto_now=True)`

Default ordering is by `-updated_at`.

---

## API Reference

Base path: `/api/v1/`

### Authentication (JWT)

- `POST /api/v1/auth/token/` – obtain access & refresh tokens
- `POST /api/v1/auth/token/refresh/` – refresh access token
- `POST /api/v1/auth/token/verify/` – verify a token

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/   -H "Content-Type: application/json"   -d '{"username":"alice","password":"secret"}'
```

### Notes

- `GET /api/v1/notes/` – list the authenticated user’s notes
  - Query params: `search`, `ordering` (e.g., `updated_at` or `-updated_at`)
  - Pagination: cursor-based
- `POST /api/v1/notes/` – create a note
- `GET /api/v1/notes/{id}/` – retrieve a note (owner-only)
- `PATCH /api/v1/notes/{id}/` – partial update (owner-only)
- `DELETE /api/v1/notes/{id}/` – delete (owner-only)

Create example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/notes/   -H "Authorization: Bearer <ACCESS_TOKEN>"   -H "Content-Type: application/json"   -d '{"title":"Buy groceries","content":"Milk, eggs, apples"}'
```

### Documentation and Ops

- `GET /api/schema/` – OpenAPI schema (JSON)
- `GET /api/docs/` – Swagger/Redoc UI
- `GET /healthz` – Health check (DB/cache ping)

### Error Model (example)

```json
{
  "error": {
    "type": "ValidationError",
    "detail": { "title": ["This field is required."] },
    "status": 400
  }
}
```

---

## Quality and Tooling

- **Testing**: `pytest`, `pytest-django`

  ```bash
  pipenv run pytest -q
  ```

- **Code style / Linting**: `black`, `ruff`, `isort` via `pre-commit`

  ```bash
  pipenv run pre-commit install
  pipenv run pre-commit run --all-files
  ```

- **Recommended settings**:
  - Use `CursorPagination` for large, frequently updated lists
  - Validate all inputs via DRF serializers
  - Use `select_related`/`prefetch_related` to avoid N+1 queries
  - Add throttling (user/ip) for public endpoints

---

## Deployment Notes

- Use PostgreSQL in production with `DATABASE_URL` and `DEBUG=False`
- Run behind a reverse proxy (nginx or Caddy) and enable HTTPS
- Consider Redis for caching and Celery for background jobs
- Add error tracking (Sentry) and metrics (Prometheus) as needed
- Provide a `/healthz` endpoint for readiness and liveness checks

---

## Roadmap

- Attachments (images/files) using presigned uploads
- Labels/tags and bulk operations
- Sharing and per-note access control lists
- Full-text search
- SDK generation from OpenAPI

---

## Contributing

Issues and pull requests are welcome. Please run formatting and tests before submitting:

```bash
pipenv run pre-commit run --all-files
pipenv run pytest -q
```

---
