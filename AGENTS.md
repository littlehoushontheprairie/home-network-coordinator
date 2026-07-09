# AGENTS.md - Home Network Coordinator

## Overview

Multiple Python services in one repo, both under `src/`:

- **IP Update Orchestration** (`src/IpUpdateOrchestrator.py`): cron-style script that resolves public IP via ipify and updates Linode firewall rules and NGINX IPs.
- **API** (`src/OrchestrationServer.py`): FastAPI server that proxies requests to Nginx Proxy Manager (update allow-list IPs, proxy-host forward IPs, certificates).

## Running

```sh
cd src
# Create venv if it doesn't exist:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Coordinator (one-shot):
python IpUpdateOrchestrator.py
# API server:
fastapi run OrchestrationServer.py   # or: fastapi dev OrchestrationServer.py
```

No test framework, linter, type checker, or CI configured.

## Docker

Two compose files under `docker/`:
- `compose.yml` — runs the coordinator container (builds `Dockerfile`, which is currently empty).
- `api.yml` — runs the API container (builds `api.Dockerfile`, CMD is `fastapi run OrchestrationServer.py`).

## Environment Variables

The code reads these env vars (not all are wired into compose files):

| Variable | Source |
|---|---|
| `NGINX_API_BASE_URL`, `NGINX_API_IDENTITY`, `NGINX_API_SECRET` | `clients/NginxApiClient.py` |
| `HOME_NETWORK_ORCHESTRATION_API_KEY_HASH` | `helpers/AuthenticationHelper.py` (has a dev fallback hash) |
| `LINODE_LABEL_NAME`, `LINODE_API_TOKEN` | `IpUpdateOrchestrator.py` |
| `PORKBUN_API_KEY`, `PORKBUN_SECRET_API_KEY` | `clients/PorkbunApiClient.py` |
| `FROM_EMAIL`, `TO_NAME`, `TO_EMAIL`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | `clients/SmtpClient.py` (unused in current code) |
| `ORCHESTRATION_ALLOWLIST_NAME` | `OrchestrationServer.py` (falls back to `"allowlist"`) |

## Key Architecture

- `clients/` — HTTP/SDK wrappers for external services (Nginx Proxy Manager, Ipify, Porkbun, Linode, SMTP).
- `entities/` — dataclass request/error types.
- `helpers/` — `AuthenticationHelper` (bcrypt Bearer token), `DataclassHelper` (dict→dataclass with nested/optional support), `CacheIpHelper` (creates/deletes/reads local cache of IP).
- Nginx API client auto-manages a JWT token (login → check → refresh).

## External APIs

- Porkbun SSL retrieve endpoint: `POST /ssl/retrieve/{domain}`.
- Ipify: `GET https://api64.ipify.org?format=json`.
