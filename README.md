# AI Job Application Tracker

A portfolio-ready full-stack application for tracking job applications on a Kanban board. It includes a responsive React dashboard, secure JWT authentication, private CV upload and text extraction, explainable AI job matching, tailored application toolkits, a FastAPI API, PostgreSQL persistence, demo data, and Docker setup.

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

The app creates its tables and optional demo applications automatically. To stop it, run `docker compose down`. Your PostgreSQL data remains in the `postgres_data` Docker volume.

### Demo account

```text
Email:    demo@applyflow.dev
Password: demo1234
```

You can also register a fresh account. Each account sees only its own applications.

### Optional OpenAI enhancement

The matching and application-toolkit features work without a paid API key using built-in local generators. To add richer structured extraction, recommendations, cover letters, and interview preparation, put an OpenAI API key in `.env`:

```text
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-6-astra
```

The API key stays in the backend and is never sent to the browser. Match percentages remain deterministic even when OpenAI extraction is enabled. When OpenAI mode is enabled, the CV text and job description are sent to the OpenAI API to generate the requested content.

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
pip install -r requirements.txt
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

## Project structure

```text
ai-job-application-tracker/
├── .vscode/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
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
├── docker-compose.yml
└── README.md
```

## Next milestones

1. Automated tests, Alembic migrations, and CI
2. Deployment and a public demo environment
