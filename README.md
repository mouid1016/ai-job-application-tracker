# AI Job Application Tracker

A portfolio-ready full-stack application for tracking job applications on a Kanban board. It includes a responsive React dashboard, secure JWT authentication, per-user data isolation, a FastAPI API, PostgreSQL persistence, demo data, and Docker setup.

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

1. CV upload and document text extraction
2. Structured AI skill extraction and deterministic match scoring
3. Cover letters and interview questions
4. Automated tests, Alembic migrations, and CI
5. Deployment and a public demo environment
