# GeoSyn

**GeoSyn** is an event-centric geopolitical intelligence platform that aggregates news, clusters events, and correlates geopolitical shocks with market data.

## 🚀 Quick Start (Locally)

### 1. Requirements
- Python 3.10+
- Node.js 18+
- (Optional) Docker for PostgreSQL

### 2. Backend Setup
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Mac/Linux
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the backend:
    ```bash
    uvicorn app.main:app --reload
    ```
    *By default, the backend will use **SQLite** (creates `geosyn.db`) for zero-config local testing.*

### 3. Frontend Setup
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🐘 Using PostgreSQL (Optional)

If you prefer to use PostgreSQL instead of SQLite:

1.  **With Docker**:
    ```bash
    docker-compose up -d
    ```
2.  **Manually**: Ensure you have a Postgres server running and create a database named `geosyn`.
3.  Configure environment variables in `backend/.env` (see `backend/.env.example`).

---

## 🛠 Features
- **Intake**: News and YouTube link ingestion.
- **Mapping**: Automated event clustering based on time and theme.
- **Veracity**: Narrative claim extraction and automated fact-checking.
- **Markets**: Real-time correlation between geopolitical "shocks" and asset volatility.

## Jira Workflow

This repo includes optional Jira-aware git tooling so commits, branches, and PRs can link cleanly to Jira work items.

Recommended convention:

- Branch: `GEOSYN-0028-short-description`
- Commit: `GEOSYN-0028: Short task description`
- PR title: `GEOSYN-0028: Short task description`

Here `0028` is just a placeholder for the real Jira issue number in zero-padded form, for example `GEOSYN-0027` or `GEOSYN-0028`.

One-time local setup:

```bash
bash scripts/setup_jira_git_workflow.sh
```

See [docs/jira_setup.md](docs/jira_setup.md), [docs/jira_automation_playbook.md](docs/jira_automation_playbook.md), and [docs/jira_backlog.md](docs/jira_backlog.md) for details.
