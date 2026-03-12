# AI Campaign MVP

Production-oriented MVP AI SaaS platform for agencies: website analysis -> campaign generation -> usage control in a single multi-tenant workspace.

## Product Goal
- Reduce campaign production cycle time for SMB agencies.
- Keep generation pipeline transparent and auditable.
- Provide stable API + frontend that can be shipped to real clients.

## What This MVP Delivers
- Multi-tenant architecture (`workspaces`, `memberships`, role model `owner/member`).
- Auth + team access (`JWT`, register/login/me).
- End-to-end pipeline:
  - create project
  - run analysis
  - generate campaign versions
  - compare campaigns
  - track usage and limits
- Async job orchestration with resilient local fallback in dev.
- RU-first frontend dashboard for daily operations.

## Architecture (DOE-style execution)
```text
Client Website URL
   -> Scraper
   -> Chunking + Embeddings
   -> RAG Retrieval
   -> LLM Analysis (structured output)
   -> Campaign Orchestrator (multi-agent)
   -> Evaluation/Comparison
   -> Usage & Audit ledger
```

## Engineering Highlights
- Versioned API layer: `/api/v1/*` with backward-compatible legacy routes.
- Workspace-scoped data isolation in routers/services.
- Unified job model and polling (`queued | running | completed | failed`).
- Request tracing (`request_id`), centralized error envelope, security headers, CORS, rate limiting.
- Audit trail for critical actions and scraping policy disclaimer logging.
- Stable frontend runtime mode (`next build + next start`) to avoid broken chunk issues in local demos.

## Tech Stack (Used)
### Backend
- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### AI / Data
- LLM API (OpenAI-compatible)
- Polza.ai integration (OpenAI-compatible endpoint)
- Embeddings + RAG retrieval pipeline
- Multi-agent orchestration for campaign generation

### Queue / Infra
- Celery + Redis (production path)
- Local background fallback (dev reliability)
- JWT auth (`python-jose`)
- Passlib (password hashing)

### Frontend
- Next.js 15
- React 19
- TypeScript
- Node.js runtime

### Testing
- Pytest
- E2E smoke checks for critical path

## API Surface (Core)
### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Workspaces
- `GET /api/v1/workspaces`
- `POST /api/v1/workspaces`
- `POST /api/v1/workspaces/{id}/members`

### Projects / Analysis
- `GET /api/v1/projects?workspace_id=...`
- `POST /api/v1/projects`
- `POST /api/v1/projects/{id}/analyze?workspace_id=...`
- `GET /api/v1/projects/{id}/analyses?workspace_id=...`
- `GET /api/v1/analyses/{id}?workspace_id=...`

### Campaigns
- `POST /api/v1/campaigns/{analysis_id}?workspace_id=...`
- `GET /api/v1/campaigns/{id}?workspace_id=...`
- `GET /api/v1/campaigns/{id}/compare/{other_id}?workspace_id=...`

### Usage / Billing Controls
- `GET /api/v1/usage?workspace_id=...`
- `GET /api/v1/plan?workspace_id=...`
- `GET /api/v1/limits?workspace_id=...`

## Local Run
## 1) Backend
```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 2) Frontend
```bash
cd frontend
npm install
npm run build
npm run start
```

Frontend URL: `http://127.0.0.1:3000`
Backend URL: `http://127.0.0.1:8000`

## Environment Notes
- For Polza.ai use OpenAI-compatible config in `.env`:
  - `OPENAI_API_KEY=pza_...`
  - `OPENAI_BASE_URL=https://polza.ai/api/v1`
- For local reliability:
  - `RUN_TASKS_LOCALLY=1`

## MVP Acceptance Path
1. Register user + workspace.
2. Create project with client URL.
3. Run analysis and wait for `success`.
4. Generate campaign and wait for `completed`.
5. Open usage/plan/limits and verify metrics update.

## Current Status
- Final MVP is operational.
- Backend + frontend validated on critical flow.
- Repository includes production-shaped architecture with clear next step to deploy.
