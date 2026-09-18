# AI Job Application Tracker

A portfolio-ready full-stack application for managing an entire job search. It includes a responsive Kanban dashboard, pipeline analytics, a cross-application AI assistant, secure account settings, private CV extraction, explainable AI matching, tailored application toolkits, a FastAPI API, PostgreSQL persistence, automated tests, and Docker setup.

## Quick start (recommended)

Requirements: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

Open:

- App: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

The backend applies pending Alembic database migrations and creates optional demo applications automatically. To stop it, run `docker compose down`. Your PostgreSQL data remains in the `postgres_data` Docker volume.

### Demo account

```text
Email:    demo@applyflow.dev
Password: demo1234
```

You can also register a fresh account. Each account sees only its own applications.

### Optional OpenAI enhancement

The matching, application-toolkit, and assistant features work without a paid API key using built-in local generators. To add richer structured extraction, recommendations, cover letters, interview preparation, and cross-application coaching, put an OpenAI API key in `.env`:

```text
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-6-astra
```

The API key stays in the backend and is never sent to the browser. Match percentages remain deterministic even when OpenAI extraction is enabled. When OpenAI mode is enabled, relevant CV/job-description text or a compact application summary is sent to the OpenAI API only when the user requests an AI feature.

## Open in VS Code

1. Extract the ZIP.
2. Double-click `ai-job-application-tracker.code-workspace`, or use **File → Open Folder** and select `ai-job-application-tracker`.
3. Accept the recommended VS Code extensions if prompted.
4. Copy `.env.example` to `.env`.
5. Open the integrated terminal and run `docker compose up --build`.

## Run without Docker

The backend falls back to a local SQLite database, so PostgreSQL is not required for this workflow.

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source .venv/bin/activate
```

Then install and run:

```bash
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` requests to the backend at `http://localhost:8000`.

## Included features

- Dashboard metrics for total applications, interviews, offers, and response rate
- Dedicated analytics page with pipeline distribution, monthly activity, deadlines, and strongest matches
- Cross-application AI assistant for prioritisation, skill gaps, progress reviews, and weekly planning
- Profile and password management, AI connection status, portable JSON export, and secure account deletion
- Registration, login, persistent sessions, and logout
- Argon2 password hashing and signed JWT access tokens
- Per-user application ownership and API-level data isolation
- Responsive Kanban workflow: Saved → Applied → Assessment → Interview → Offer → Rejected
- Native drag-and-drop status updates
- Create, edit and delete applications
- Full application workspace with notes and job-description storage
- Automatic activity timeline for status and detail changes
- Private PDF/DOCX CV upload, replacement, download, deletion, and text extraction
- Explainable CV-to-job skill matching with deterministic coverage scores
- Optional OpenAI Structured Outputs for richer extraction and recommendations
- Saved application toolkit with a tailored cover letter and elevator pitch
- Six role-aware interview questions with answer frameworks and talking points
- Four thoughtful questions to ask the employer
- Automatic stale-content warnings after the CV, job description, company, role, or analysis changes
- Alembic migration history for reproducible database changes
- Automated backend API tests with isolated test data
- GitHub Actions CI for migrations, tests, linting, and production builds
- Search by company or role
- FastAPI CRUD endpoints with automatic Swagger docs
- PostgreSQL in Docker and SQLite for quick local development
- Seed data for an immediately useful first run

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service and database health |
| `POST` | `/api/auth/register` | Create an account and receive a token |
| `POST` | `/api/auth/login` | Sign in and receive a token |
| `GET` | `/api/auth/me` | Read the authenticated user |
| `GET` | `/api/settings` | Read profile and AI configuration status |
| `PATCH` | `/api/settings/profile` | Update the authenticated user's name and email |
| `POST` | `/api/settings/password` | Change the authenticated user's password |
| `GET` | `/api/settings/export` | Export all account and application data as JSON |
| `DELETE` | `/api/settings/account` | Permanently delete the authenticated account |
| `GET` | `/api/applications` | List applications |
| `POST` | `/api/applications` | Create an application |
| `GET` | `/api/applications/{id}` | Read one application |
| `PATCH` | `/api/applications/{id}` | Update an application or status |
| `DELETE` | `/api/applications/{id}` | Delete an application |
| `GET` | `/api/applications/{id}/activities` | Read an application's activity timeline |
| `GET` | `/api/applications/{id}/documents/cv` | Read CV metadata |
| `POST` | `/api/applications/{id}/documents/cv` | Upload or replace a PDF/DOCX CV |
| `GET` | `/api/applications/{id}/documents/cv/download` | Download the authenticated user's CV |
| `DELETE` | `/api/applications/{id}/documents/cv` | Remove a CV |
| `GET` | `/api/applications/{id}/analysis` | Read the saved match analysis |
| `POST` | `/api/applications/{id}/analysis` | Analyse the CV against the job description |
| `GET` | `/api/applications/{id}/application-kit` | Read the saved cover letter and interview toolkit |
| `POST` | `/api/applications/{id}/application-kit` | Generate or refresh the application toolkit |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/analytics` | Read private pipeline analytics and ranked applications |
| `POST` | `/api/assistant` | Ask a question across the user's application data |

## Project structure

```text
ai-job-application-tracker/
├── .vscode/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── styles.css
│   │   └── types.ts
│   ├── Dockerfile
│   └── package.json
├── .env.example
├── .github/workflows/ci.yml
├── docker-compose.yml
└── README.md
```

## Tests and database migrations

Run the backend checks from `backend/`:

```bash
pytest
alembic check
```

Create a migration after changing a SQLAlchemy model:

```bash
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

Run the frontend checks from `frontend/`:

```bash
npm run lint
npm run build
```

GitHub Actions runs all of these checks automatically for every pull request and every push to `main`.

## Next milestones

1. Deployment and a public demo environment
2. Expanded browser-level end-to-end tests
3. Optional email reminders for deadlines and follow-ups
