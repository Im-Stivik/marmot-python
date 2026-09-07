# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Identity domain with SQLAlchemy models for users, roles, permissions, groups, and membership.
- Local password login at `POST /api/v1/users/login` issuing JWT bearer tokens.
- SSO login endpoint stub at `POST /api/v1/users/login/sso` (token-shaped request; returns 501 until implemented).
- Current-user profile at `GET /api/v1/users/me` (user, roles, groups, permissions).
- Pluggable group membership providers (`MARMOT_GROUP_SOURCE=local|mirage`; Mirage is an empty stub).
- Separate local vs SSO auth provider interfaces (password vs token; no shared password protocol for SSO).
- First-init `database_populate` for permissions, system roles (`admin` / `user`), and seed admin user.
- Catalog `Asset` model with `material_resource_name` and optional `owner_group_id`.
- Access `TableGrant` model mapping group visibility to assets (`asset_id` + `group_id` composite primary key).
- Nested settings models (`database`, `jwt`, `seed`, `trino`) under `MARMOT_*` env vars.
- `Database` object for engine/session lifecycle (replaces ad-hoc global engine rebinding).
- Dynamic domain model registration via `import_domain_models()`.
- Isolated pytest database helper: create/drop `marmot_test` per DB test; abort if it already exists.
- Project style rules for blank lines, naming, comments, and layering (`.cursor/rules/python-style.mdc`).

### Changed

- Username format is lowercase letter + 7 digits (`^[a-z]\d{7}$`), e.g. `s1234567`.
- Default seed admin username is `s1234567` (password still `admin`, overridable via env).
- Default `user` role permissions reduced to `view_assets` and `view_glossary` only
  (metrics, ingestion, and global team listing remain admin-only).
- Schema bootstrap uses SQLAlchemy `create_all` plus first-init populate only (no Alembic; no rewrite on rollout).

### Removed

- User `active` and `must_change_password` fields and related auth branching.
- Path-based table grant columns (`catalog` / `schema_name` / `table_name`) in favor of asset FKs.
- Shortened asset field name `mrn` (replaced by `material_resource_name`).

### Security

- Local login returns a uniform invalid-credentials error (no inactive-user distinction that enables username probing).
- Password verification runs before any account-state messaging.
- Test DB safety: only names ending in `_test` may be created/dropped; existing `marmot_test` aborts the suite.

### Fixed

- Review feedback from PR #2: config layering, DB object design, populate API, auth abstraction, seed permissions, formatting, and test isolation.

## [0.1.0] - 2026-08-26

### Added

- Initial FastAPI modular-monolith skeleton (Python 3.8).
- Health probes: `GET /health`, `GET /livez`, `GET /readyz`.
- Core config and SQLAlchemy engine wiring.
- Docker Compose lakehouse stack (Postgres, MinIO, Hive Metastore, Trino) and API service.
- Domain package stubs: identity, catalog, access, ingestion, search, gateway.

[Unreleased]: https://github.com/Im-Stivik/marmot-python/compare/develop...HEAD
[0.1.0]: https://github.com/Im-Stivik/marmot-python/releases/tag/v0.1.0
