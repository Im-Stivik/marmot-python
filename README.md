This is a Python + React rewrite of the [Marmot](https://github.com/marmotdata/marmot) data catalog.

## Backend (Python 3.8 only)

This API targets **CPython 3.8**. Do not use the system Python on Fedora (currently 3.14) — `pip` will try to compile `pydantic-core` from source and fail.

You need a `python3.8` binary on `PATH`.

```bash
cd backend

python3.8 -m venv .venv
source .venv/bin/activate

python -c "import sys; assert sys.version_info[:2] == (3, 8), sys.version"

pip install -U pip setuptools wheel
pip install -e ".[dev]"

python main.py
```

Layout:

```
backend/
  main.py                 # FastAPI entrypoint
  src/
    core/                 # config, db
    health/               # router + service
    identity|catalog|access|ingestion|search|gateway/
      router.py
      service.py
      repository.py
      model.py
  tests/
```

- Health: `GET /health`, `GET /livez`, `GET /readyz`
- Identity: `POST /api/v1/users/login`, `POST /api/v1/users/login/sso` (stub), `GET /api/v1/users/me`
- OpenAPI: http://localhost:8000/docs

Login (dev admin defaults to `s1234567` / `admin`):

```bash
curl -s -X POST http://localhost:8000/api/v1/users/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"s1234567","password":"admin"}'
```

Both login endpoints are always available:

- `POST /api/v1/users/login` — username + password (username format: lowercase letter + 7 digits)
- `POST /api/v1/users/login/sso` — SSO token (not implemented yet; returns 501)

Group membership is pluggable via `MARMOT_GROUP_SOURCE=local|mirage` (Mirage is a stub).

```bash
pytest
```

Environment variables use the `MARMOT_` prefix with nested groups (e.g. `MARMOT_DATABASE_HOST`, `MARMOT_JWT_SECRET`, `MARMOT_SEED_ADMIN_USERNAME` — see `src/core/config.py`).

Schema changes use SQLAlchemy models + `Base.metadata.create_all()` for now (no Alembic).
First-init `database_populate` runs only when the permissions table is empty — later rollouts do **not** rewrite roles/users.

## Tests

Pytest creates a throwaway database named `marmot_test` (override with `MARMOT_TEST_DATABASE_NAME`) for each DB test, seeds it, then drops it. If `marmot_test` already exists, tests **abort** instead of dropping it — leftover DBs must be removed manually.

## Docker Compose

Starts the Python API plus Postgres, MinIO, Hive Metastore, and Trino:

```bash
docker compose up --build -d
```

- API: http://localhost:8000/docs
- Trino: http://localhost:8081
- MinIO console: http://localhost:9001

## Reference

Original Go + SvelteKit project: https://github.com/marmotdata/marmot (also `../marmot/`).
