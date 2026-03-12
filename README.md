# AI Campaign MVP

AI Campaign is an AI SaaS MVP for agency teams that need to turn a client website into a structured marketing analysis and a campaign draft without jumping between disconnected tools. The product combines scraping, RAG-based context retrieval, LLM analysis, campaign generation, and workspace-level operational controls in one flow.

AI Campaign - это AI SaaS MVP для агентских команд, которым нужен цельный процесс: взять сайт клиента, получить структурный маркетинговый анализ и собрать черновик кампании без переключения между разрозненными инструментами. Продукт объединяет скрапинг, RAG-поиск контекста, LLM-анализ, генерацию кампаний и операционные controls на уровне workspace в одном сценарии.

## Product / Продукт

The current MVP is built around one practical use case: `workspace -> project -> analysis -> campaign -> compare -> usage`. A user creates a workspace, adds a client project, runs analysis for the client website, generates campaign artifacts, and tracks job state and consumption through the same interface and API.

Текущий MVP построен вокруг одного прикладного сценария: `workspace -> project -> analysis -> campaign -> compare -> usage`. Пользователь создает workspace, добавляет проект клиента, запускает анализ сайта, генерирует артефакты кампании и отслеживает состояние задач и расход ресурсов через тот же интерфейс и API.

The emphasis is not on “instant magic”, but on controllable output quality: versioned API, job statuses, audit logs, usage visibility, and a backend structure that can be extended toward production without rewriting the core flow.

Акцент здесь не на “магии в один клик”, а на управляемом качестве результата: versioned API, статусы задач, audit-логи, видимость usage и такая структура backend, которую можно расширять в сторону production без переписывания основного пайплайна.

## What Is Implemented / Что реализовано

- Workspace-scoped multi-tenant model with users, memberships, and owner/member access.
- JWT auth flow: register, login, current user profile.
- Project creation and workspace isolation.
- Website analysis pipeline with scraping, embeddings, retrieval, and structured LLM output.
- Campaign generation pipeline with compare flow.
- Unified async job model with polling-friendly statuses and progress hints.
- Usage, plan, and limits endpoints for monetizable SaaS operations.
- Audit logging and request tracing for operational transparency.
- Legacy routes preserved alongside `/api/v1`.

- Multi-tenant модель с workspace, пользователями, membership и ролями owner/member.
- JWT-аутентификация: register, login, профиль текущего пользователя.
- Создание проектов и изоляция данных по workspace.
- Пайплайн анализа сайта со scraping, embeddings, retrieval и структурированным LLM-выводом.
- Пайплайн генерации кампаний и compare flow.
- Единая async-модель задач со статусами и progress hint для polling.
- Endpoints usage, plan и limits для SaaS-монетизации.
- Audit logging и request tracing для прозрачной эксплуатации.
- Legacy-роуты сохранены параллельно с `/api/v1`.

## Architecture / Архитектура

```text
Client URL
  -> Scraper
  -> Chunking + Embeddings
  -> Retrieval (RAG)
  -> Structured LLM Analysis
  -> Campaign Orchestrator
  -> Compare / Evaluation
  -> Job Tracking + Usage + Audit
```

Backend is organized so that the commercial SaaS concerns are already visible in the codebase: workspace isolation, async jobs, usage accounting, audit trail, and API versioning. That makes the project look less like a single demo script and more like an actual product foundation.

Backend организован так, чтобы в кодовой базе уже были видны коммерческие SaaS-задачи: изоляция workspace, async jobs, учет usage, audit trail и versioned API. За счет этого проект выглядит не как одиночный demo-скрипт, а как заготовка под реальный продукт.

## Tech Stack / Технологический стек

- Backend (`Бэкенд`): Python 3.13, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- AI (`ИИ-слой`): OpenAI-compatible API, Polza.ai (`OPENAI_BASE_URL=https://polza.ai/api/v1`), embeddings, RAG pipeline, multi-agent orchestration
- Queue & Infra (`Очереди и инфраструктура`): Celery, Redis, local background fallback, JWT (`python-jose`), password hashing (`passlib`)
- Frontend (`Фронтенд`): Next.js 15, React 19, TypeScript, Node.js
- QA (`Тестирование`): Pytest, API smoke tests

## API Surface / Основные API

- Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Workspaces: `GET /api/v1/workspaces`, `POST /api/v1/workspaces`, `POST /api/v1/workspaces/{id}/members`
- Projects: `GET /api/v1/projects?workspace_id=...`, `POST /api/v1/projects`, `POST /api/v1/projects/{id}/analyze?workspace_id=...`, `GET /api/v1/projects/{id}/analyses?workspace_id=...`
- Analyses: `GET /api/v1/analyses/{id}?workspace_id=...`
- Campaigns: `POST /api/v1/campaigns/{analysis_id}?workspace_id=...`, `GET /api/v1/campaigns/{id}?workspace_id=...`, `GET /api/v1/campaigns/{id}/compare/{other_id}?workspace_id=...`
- Jobs: `GET /api/v1/jobs/{job_id}?workspace_id=...`
- Usage & Limits: `GET /api/v1/usage?workspace_id=...`, `GET /api/v1/plan?workspace_id=...`, `GET /api/v1/limits?workspace_id=...`

## Quick Start / Быстрый старт

### Backend

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run build
npm run start
```

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:3000`

## Environment / Переменные окружения

- `OPENAI_API_KEY=pza_...`
- `OPENAI_BASE_URL=https://polza.ai/api/v1`
- `OPENAI_MODEL=openai/gpt-4o-mini`
- `DATABASE_URL=sqlite:///./app.db` or PostgreSQL DSN
- `JWT_SECRET=...`
- `RUN_TASKS_LOCALLY=1`
- `CELERY_BROKER_URL=redis://localhost:6379/0`
- `CELERY_RESULT_BACKEND=redis://localhost:6379/1`
- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`

## Local Notes / Локальные замечания

By default the project can run entirely in local fallback mode. If Redis/Celery are not configured, analysis and campaign jobs still work through in-process background execution.

По умолчанию проект может работать полностью в локальном fallback-режиме. Если Redis/Celery не настроены, задачи анализа и генерации кампаний все равно выполняются через in-process background execution.

The main frontend issue encountered during development was stale Next.js build cache. If you see `Cannot find module './xxx.js'`, remove `frontend/.next` and rebuild the frontend.

Главная практическая проблема фронтенда в разработке была связана с устаревшим кэшем сборки Next.js. Если появляется `Cannot find module './xxx.js'`, нужно удалить `frontend/.next` и пересобрать фронтенд.

## Status / Статус

The repository is in a working MVP state: the critical path is implemented, the backend contract exists, the frontend is connected, and the architecture already includes the pieces needed for the next step toward production.

Репозиторий находится в рабочем состоянии MVP: критический путь реализован, backend-контракт существует, фронтенд подключен, а архитектура уже включает элементы, нужные для следующего шага в сторону production.
