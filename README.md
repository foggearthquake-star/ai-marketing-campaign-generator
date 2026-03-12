# AI Campaign MVP

## English
Production-oriented AI SaaS MVP for agencies: website analysis -> campaign generation -> usage/limits in one multi-tenant workspace.

### Product Goal
- Reduce campaign production cycle time for SMB agencies.
- Keep generation pipeline transparent and auditable.
- Provide stable API + frontend ready for real client pilots.

### What This MVP Delivers
- Multi-tenant model (`workspaces`, `memberships`, roles `owner/member`).
- Auth and team access (`JWT`, register/login/me).
- End-to-end flow: project -> analysis -> campaign -> compare -> usage/limits.
- Async job orchestration with resilient local fallback in development.
- RU-first operational dashboard on Next.js.

### Architecture
```text
Client Website URL
   -> Scraper
   -> Chunking + Embeddings
   -> RAG Retrieval
   -> LLM Analysis (structured output)
   -> Campaign Orchestrator (multi-agent)
   -> Evaluation / Comparison
   -> Usage + Audit ledger
```

### Tech Stack (Used)
- Backend: Python 3.13, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- AI/Data: OpenAI-compatible LLM API, Polza.ai, Embeddings, RAG, Multi-agent orchestration
- Queue/Infra: Celery + Redis (prod path), local fallback (`RUN_TASKS_LOCALLY=1`), JWT, Passlib
- Frontend: Next.js 15, React 19, TypeScript, Node.js
- Testing: Pytest + E2E smoke checks

### Core API
- Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Workspaces: `GET/POST /api/v1/workspaces`, `POST /api/v1/workspaces/{id}/members`
- Projects/Analysis: `GET/POST /api/v1/projects`, `POST /api/v1/projects/{id}/analyze`, `GET /api/v1/projects/{id}/analyses`, `GET /api/v1/analyses/{id}`
- Campaigns: `POST /api/v1/campaigns/{analysis_id}`, `GET /api/v1/campaigns/{id}`, `GET /api/v1/campaigns/{id}/compare/{other_id}`
- Usage/Billing controls: `GET /api/v1/usage`, `GET /api/v1/plan`, `GET /api/v1/limits`

### Local Run
#### Backend
```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build
npm run start
```

- Frontend: `http://127.0.0.1:3000`
- Backend: `http://127.0.0.1:8000`

### Environment Notes
- Polza.ai config:
  - `OPENAI_API_KEY=pza_...`
  - `OPENAI_BASE_URL=https://polza.ai/api/v1`
- Local queue reliability:
  - `RUN_TASKS_LOCALLY=1`

### Troubleshooting
- `Cannot find module './xxx.js'` in frontend:
  1. Stop Node processes
  2. Remove `frontend/.next`
  3. Run `npm run build && npm run start`
- `Нет соединения с API`:
  1. Check backend health `http://127.0.0.1:8000/health`
  2. Ensure frontend env uses `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
- Analysis stuck in `queued` locally:
  1. Set `RUN_TASKS_LOCALLY=1`
  2. Restart backend

### Status
Final MVP is operational and validated on critical path.

---

## Русский
Production-ready MVP AI SaaS для агентств: анализ сайта -> генерация кампаний -> контроль usage/лимитов в одном multi-tenant workspace.

### Цель продукта
- Сократить цикл подготовки кампаний для SMB-агентств.
- Сделать генерацию прозрачной и управляемой.
- Дать стабильный backend+frontend для пилотов с реальными клиентами.

### Что уже реализовано
- Multi-tenant модель (`workspaces`, `memberships`, роли `owner/member`).
- Авторизация и командный доступ (`JWT`, register/login/me).
- Сквозной процесс: проект -> анализ -> кампания -> сравнение -> usage/лимиты.
- Асинхронные задачи с надежным локальным fallback в dev.
- RU-first интерфейс операционной работы на Next.js.

### Как запустить локально
#### Backend
```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build
npm run start
```

- Frontend: `http://127.0.0.1:3000`
- Backend: `http://127.0.0.1:8000`

### Важные env
- Для Polza.ai:
  - `OPENAI_API_KEY=pza_...`
  - `OPENAI_BASE_URL=https://polza.ai/api/v1`
- Для стабильного локального выполнения задач:
  - `RUN_TASKS_LOCALLY=1`

### Частые проблемы
- `Cannot find module './xxx.js'`:
  1. Остановить Node
  2. Удалить `frontend/.next`
  3. Запустить `npm run build && npm run start`
- Нет связи фронта с API:
  1. Проверить `http://127.0.0.1:8000/health`
  2. Проверить `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
- Анализ зависает в `queued`:
  1. Включить `RUN_TASKS_LOCALLY=1`
  2. Перезапустить backend

### Статус
Финальный MVP готов и проверен на критическом пути.
