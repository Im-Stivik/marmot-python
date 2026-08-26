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
- OpenAPI: http://localhost:8000/docs

```bash
pytest
```

Environment variables use the `MARMOT_` prefix (see `src/core/config.py`).

Schema changes use SQLAlchemy models + `Base.metadata.create_all()` for now (no Alembic).

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
