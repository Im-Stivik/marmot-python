# Marmot Migration Checklist

Track rewriting Marmot from the Go monolith + SvelteKit UI to **Python 3.8 + FastAPI + SQLAlchemy** microservices and a **React** frontend, feature by feature, using TDD.

**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done

Suggested order: foundation → auth → assets/search → lineage → glossary → ingestion → products/rules → notifications → MCP/agents → UI/CLI/SDKs → deploy.

---

## 0. Foundation

- [ ] Project scaffolding (Python 3.8, FastAPI, SQLAlchemy, pytest, shared libs)
- [ ] Shared config / settings (`MARMOT_*` env parity)
- [ ] Postgres schema / Alembic migrations (core tables)
- [ ] Health probes (`/health`, `/livez`, `/readyz`)
- [ ] OpenAPI / Swagger
- [ ] Rate limiting middleware
- [ ] Encryption at rest for secrets (plugin/schedule configs)
- [ ] TLS support (server + IdP / ES)
- [ ] Background worker / singleton coordination
- [ ] WebSocket hub (job runs, search reindex)

---

## 1. Auth & Identity Service

- [ ] Local users (CRUD, must-change-password, profile picture, active flag)
- [ ] Roles & RBAC permissions
  - [ ] Permissions: `view_users`, `manage_users`, `view_assets`, `manage_assets`, `preview_assets`, `manage_roles`, `view_metrics`, `view_glossary`, `manage_glossary`, `view_teams`, `manage_teams`, `manage_sso_mappings`, `view_ingestion`, `manage_ingestion`, `emit_agent_runs`, `service_accounts_view`, `service_accounts_manage`
  - [ ] Default roles: `admin`, `user` (system roles protected)
- [ ] User API keys (`X-API-Key`)
- [ ] Service accounts (roles + dedicated API keys)
- [ ] SSO / OIDC / OAuth providers
  - [ ] Okta
  - [ ] Google
  - [ ] Generic OIDC
  - [ ] GitHub
  - [ ] GitLab
  - [ ] Keycloak
  - [ ] Slack
  - [ ] Auth0
- [ ] SSO group → role mapping
- [ ] SSO group → team sync (claim / filter / strip_prefix)
- [ ] Link / unlink OAuth identities
- [ ] Anonymous access (optional anonymous role)
- [ ] OAuth2 authorization server for MCP clients (metadata, DCR, authorize, token, token exchange)
- [ ] Kubernetes SA token auth (TokenReview)
- [ ] User notification preferences

---

## 2. Teams Service

- [ ] Teams CRUD
- [ ] Team members (add / remove / change role)
- [ ] Convert SSO-synced member to manual
- [ ] Team tags & search
- [ ] SSO team mappings (IdP group → team)
- [ ] Owners search (users + teams)

---

## 3. Assets Service (core catalog)

- [ ] Asset CRUD & identity (MRN, stubs, parent hierarchy)
- [ ] Asset fields: type, service, name, schema, metadata, tags, sources, environments, external links, descriptions, query / query_language, last_sync_at, has_run_history
- [ ] Asset tags (add / remove / suggestions)
- [ ] Asset ownership (users + teams)
- [ ] Asset ↔ glossary term links
- [ ] Asset documentation (legacy / plugin docs)
- [ ] Asset summary & “my assets”
- [ ] Asset run history (OpenLineage-style events + histograms)
- [ ] Asset metadata / tag suggestions (autocomplete)
- [ ] Table preview (experimental; gated by permission + config)
- [ ] Manual asset creation (API + UI parity later)

---

## 4. Search Service

- [ ] Query language parser (fields, operators, boolean `AND`/`OR`/`NOT`, wildcards, ranges)
- [ ] Unified search (assets, glossary, teams, users)
- [ ] Asset search API (`/assets/search` + pattern match)
- [ ] Postgres FTS + trigram backend
- [ ] Optional Elasticsearch backend (index sync, bulk, reindex-on-start, TLS)
- [ ] Search index materialization
- [ ] Admin reindex (trigger / status / WebSocket progress)
- [ ] Visual query builder parity (UI later)

---

## 5. Lineage Service

- [ ] Interactive lineage graph (upstream / downstream, depth)
- [ ] Direct lineage edge CRUD
- [ ] Batch edge create
- [ ] Typed edges; origin `declared` vs `observed`
- [ ] Observation count / last_seen_at
- [ ] OpenLineage event ingestion → assets + edges + run history + stubs
- [ ] OpenLineage auth config
- [ ] Lineage events store
- [ ] Mapped OL types: DAG, Task, Model, Project, Table, File, Topic

---

## 6. Glossary Service

- [ ] Hierarchical glossary terms (parent / children / ancestors)
- [ ] Term CRUD, list, search
- [ ] Term owners
- [ ] Term tags
- [ ] Link terms to assets

---

## 7. Data Products Service

- [ ] Data products CRUD
- [ ] Tags & owners
- [ ] Manual asset membership
- [ ] Dynamic query rules + rule preview
- [ ] Resolved assets
- [ ] Product images (upload / get / delete / list by purpose)
- [ ] Background membership evaluation + reconciler (~30 min)

---

## 8. Asset Rules Service (governance enrichment)

- [ ] Asset rules CRUD (enable / disable)
- [ ] Preview matches / list matched assets
- [ ] Search rules
- [ ] Auto-apply enrichments (external links, glossary terms)
- [ ] Rule targets from query (`asset_type`, `provider`, `tag`, `metadata_key`)
- [ ] Membership workers + reconciler (~30 min)

---

## 9. Documentation Pages Service

- [ ] Nested doc pages on assets & data products
- [ ] Page CRUD, move / reorder, parent hierarchy
- [ ] Emoji / title / content
- [ ] Image upload / serve / delete
- [ ] Image processing (resize)
- [ ] Search pages
- [ ] Storage stats

---

## 10. Ingestion / Pipelines Service

- [ ] Plugin host / registry
- [ ] OCI plugin autoinstall
- [ ] Encrypted plugin credentials
- [ ] Plugin filters / tags / external links (base config)
- [ ] Load-state tracking
- [ ] Ingestion schedules CRUD (cron)
- [ ] Validate schedule config
- [ ] Manual trigger / cancel runs
- [ ] Worker pool with leases / claims
- [ ] Asset ↔ schedule linkage
- [ ] Pipeline runs lifecycle (start / complete / batch assets / cleanup / destroy)
- [ ] Run checkpoints & entities
- [ ] Run statuses: running / completed / failed / cancelled
- [ ] WebSocket live run updates
- [ ] List plugins API + AWS credential status

### Ingestion plugins (port one by one)

#### Databases
- [ ] PostgreSQL
- [ ] MySQL
- [ ] MongoDB
- [ ] ClickHouse
- [ ] DuckDB
- [ ] Trino
- [ ] BigQuery
- [ ] DynamoDB
- [ ] Redis

#### Lake / warehouse / catalog
- [ ] Glue
- [ ] Iceberg
- [ ] Delta Lake
- [ ] Elasticsearch
- [ ] OpenSearch

#### Object storage
- [ ] S3
- [ ] GCS
- [ ] Azure Blob

#### Messaging
- [ ] Kafka
- [ ] Redpanda
- [ ] Confluent Cloud
- [ ] NATS
- [ ] SNS
- [ ] SQS

#### Compute / orchestration
- [ ] Lambda
- [ ] Airflow
- [ ] Kubernetes
- [ ] EKS
- [ ] GKE

#### Specs / transforms
- [ ] OpenAPI
- [ ] AsyncAPI
- [ ] dbt

---

## 11. Notifications & Webhooks Service

- [ ] In-app notifications feed (types, mark read, clear, summary)
- [ ] Notification types: `system`, `schema_change`, `asset_change`, `team_invite`, `mention`, `job_complete`, `upstream_schema_change`, `downstream_schema_change`, `lineage_change`, `asset_deleted`
- [ ] Aggregator / batching / prune / per-user cap / preference filtering
- [ ] Asset subscriptions
- [ ] Team webhooks (Slack, Discord, generic)
- [ ] Webhook test endpoint
- [ ] Async webhook dispatcher with retries

---

## 12. Metrics & Telemetry Service

- [ ] Catalog metrics (totals, by type / provider / owner, with-schemas)
- [ ] Top assets / top queries
- [ ] Metrics timeseries
- [ ] Asset statistics from plugins
- [ ] Prometheus-style metrics port
- [ ] Lookup counters (MCP / API usage)
- [ ] Optional install telemetry

---

## 13. MCP & Agents Service

- [ ] Built-in MCP server (`/api/v1/mcp`)
- [ ] MCP tools: `discover_data`, `find_ownership`, `lookup_term`, `explore_data_products`, `explore_teams`, `trace_lineage`
- [ ] Agent run telemetry (runs + tool calls)
- [ ] Agent activity / stats APIs
- [ ] Agent framework integrations (LangChain, Claude Agent SDK)
- [ ] Cursor skill / MCP client docs parity

---

## 14. Web UI (SvelteKit → React)

- [ ] React app scaffolding (Vite + React + TypeScript, routing, auth client, API client)
- [ ] Design system / shared layout (nav, theme, banner from `GET /api/v1/ui/config`)
- [ ] Home / dashboard
- [ ] Asset discover / detail
- [ ] Search + visual query builder
- [ ] Glossary
- [ ] Data products
- [ ] Asset rules
- [ ] Pipelines & runs
- [ ] Lineage graph
- [ ] Metrics
- [ ] Notifications
- [ ] Teams / users / roles admin
- [ ] Service accounts
- [ ] Profile / API keys
- [ ] Login / SSO
- [ ] Admin (search reindex)
- [ ] Manual asset creation (`/assets/new`)
- [ ] WebSocket live updates (job runs, search reindex)
- [ ] Retire SvelteKit app once React parity is reached

---

## 15. CLI

- [ ] `login` / `logout` (OAuth PKCE)
- [ ] `context` (multi-host)
- [ ] `config` (init / set / get / list)
- [ ] `assets` (list / get / search / delete / summary / tags / owners)
- [ ] `search`
- [ ] `glossary`
- [ ] `lineage`
- [ ] `runs`
- [ ] `ingest` / `run`
- [ ] `users`
- [ ] `teams`
- [ ] `apikeys`
- [ ] `service-accounts`
- [ ] `metrics`
- [ ] `admin` (reindex)
- [ ] `operator`
- [ ] `generate-encryption-key`
- [ ] `version`
- [ ] Output formats: table / json / yaml
- [ ] Auth priority: `--api-key` → context OAuth → env → K8s SA

---

## 16. Client SDKs

- [ ] Python SDK (primary for new stack)
- [ ] TypeScript SDK
- [ ] Go SDK (optional / parity)
- [ ] SDK coverage: assets, glossary, lineage, runs, search, teams, users, metrics, owners, admin, apikeys, dataproducts, ingestion, service accounts, auth

---

## 17. Kubernetes Operator & Deploy

- [ ] Marmot Run CRD + controller
- [ ] Helm chart
- [ ] Docker / Docker Compose
- [ ] Install script
- [ ] Custom response headers
- [ ] Embedded / static UI serving (if kept)

---

## Suggested microservice boundaries

| Service | Owns |
|---------|------|
| **auth** | Users, roles, API keys, SSO, OAuth2 AS, service accounts |
| **teams** | Teams, members, SSO team mappings, owners search |
| **assets** | Assets, tags, owners, terms links, run history, docs (legacy), preview |
| **search** | Query language, FTS / ES index, reindex |
| **lineage** | Edges, OpenLineage ingest, lineage events |
| **glossary** | Terms hierarchy |
| **data-products** | Products, rules, memberships, images |
| **asset-rules** | Governance rules + enrichment workers |
| **docs** | Nested wiki pages + images |
| **ingestion** | Plugins, schedules, runs, workers |
| **notifications** | Feed, subscriptions, webhooks |
| **metrics** | Catalog metrics, telemetry counters |
| **mcp** | MCP tools + agent run telemetry |
| **gateway** (optional) | Routing, rate limit, TLS, UI static |

Adjust boundaries as you learn; keep each feature’s tests independent of the old Go service.
