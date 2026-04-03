# Personal Business Dashboard

## What This Project Is
A localhost Python web application that gives entrepreneurs a single dashboard to manage leads, invoices, and projects across all their businesses. Data flows in through Google Drive folders, gets normalized by OpenAI, lives in Google Sheets as the primary datastore, and surfaces in a clean dashboard with the ability to send emails via Gmail and schedule reminders via Google Calendar.

## The Core Idea
```
Google Drive folders (intake)
    ↓
OpenAI API (normalize + cross-reference)
    ↓
Google Sheets (master datastore)
    ↓
Dashboard (view + act)
   ├── Gmail → email leads, send invoices
   └── Calendar → invoice reminders, follow-ups
```

## Tech Stack
- **Language:** Python 3.10+
- **Web Framework:** Flask
- **Frontend:** HTML/CSS/JavaScript (Jinja2 templates, Chart.js for visualizations)
- **Auth:** Flask-Login with session-based authentication
- **APIs:**
  - Google Drive API v3 (file intake + sync)
  - Google Sheets API v4 (primary datastore)
  - Google Gmail API (send emails from dashboard)
  - Google Calendar API v3 (create reminders + events)
  - OpenAI API (data normalization + cross-reference reconciliation)
- **Environment:** Local development only (localhost:3456)

## Google OAuth Scopes (one credentials.json for all four)
```python
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
]
```

## Data Objects (Canonical Schemas)

### Lead
| Field | Type | Example |
|-------|------|---------|
| name | string | "Jane Smith" |
| email | string | "jane@acme.com" |
| company | string | "Acme Corp" |
| source | string | "Referral" |
| stage | string | "new" / "contacted" / "converted" |
| created_at | string | "2026-04-01" |

### Invoice
| Field | Type | Example |
|-------|------|---------|
| invoice_number | string | "INV-0042" |
| client | string | "Acme Corp" |
| amount | number | 4500.00 |
| due_date | string | "2026-04-15" |
| status | string | "draft" / "sent" / "paid" / "overdue" |
| email | string | "billing@acme.com" |

### Project
| Field | Type | Example |
|-------|------|---------|
| name | string | "Website Redesign" |
| client | string | "Acme Corp" |
| budget | number | 15000.00 |
| total_billed | number | 4500.00 |
| deadline | string | "2026-06-01" |
| status | string | "active" / "completed" / "on_hold" |

## Cross-Reference Rules
When new data enters the system, the pipeline reconciles across all three tables:
- **New invoice** → find matching lead by client name → update lead stage to "converted"
- **New invoice** → find matching project by client name → add to project's total_billed
- **New lead** → check if project exists for that company → link them
- **New project** → check for existing leads + invoices by company → associate them

OpenAI handles fuzzy matching ("Acme Corp" = "Acme Corporation" = "acme").

## Project Structure
```
finished_product/
├── start.sh                   # One-command launcher
├── app.py                     # Flask app factory (wires all layers)
├── config.py                  # Environment + constants
├── requirements.txt
├── .env.example
├── routes/                    # URL → controller (thin)
│   ├── auth_routes.py         #   /login, /logout
│   ├── dashboard_routes.py    #   /dashboard, /leads, /invoices, /projects
│   ├── api_routes.py          #   /api/data, /api/sync
│   ├── email_routes.py        #   /api/email/send
│   └── calendar_routes.py     #   /api/calendar/remind
├── controllers/               # HTTP handling
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── api_controller.py
│   ├── email_controller.py
│   └── calendar_controller.py
├── services/                  # Business logic
│   ├── auth_service.py
│   ├── data_service.py
│   ├── drive_service.py       #   Scan Drive folders for new files
│   ├── sheets_service.py      #   Read/write master spreadsheet
│   ├── openai_service.py      #   Normalize + reconcile data
│   ├── gmail_service.py       #   Send emails
│   ├── calendar_service.py    #   Create calendar events
│   └── etl_service.py         #   Orchestrate full pipeline
├── repositories/
│   ├── user_repository.py
│   └── data_repository.py
├── models/
│   └── user.py
├── scripts/
│   ├── sync_drive.py          #   Scan Drive folders + process new files
│   ├── normalize.py           #   OpenAI normalization + reconciliation
│   └── full_pipeline.py       #   Run everything end to end
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html         #   Overview of all businesses
│   ├── leads.html             #   Lead management + email action
│   ├── invoices.html          #   Invoice tracking + calendar action
│   ├── projects.html          #   Project view with linked leads/invoices
│   └── email_compose.html     #   Email composition modal/page
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
└── data/                      #   Local cache (Sheets is source of truth)
```

## Coding Conventions
- **Python style:** PEP 8, 4-space indentation, snake_case for everything
- **Max line length:** 100 characters
- **Imports:** stdlib first, then third-party, then local — separated by blank lines
- **Functions:** Each function does one thing. Docstrings on public functions only.
- **Error handling:** Only at system boundaries (API calls, file I/O). Use clear error messages.
- **No type hints** in this project — keeps it readable for non-technical audiences
- **Comments:** Plain English, explain *why* not *what*
- **Architecture:** route → controller → service → repository (no layer skipping)

## Commands
- **Run the app:** `./start.sh` or `python3 app.py`
- **Sync Drive + normalize:** `python3 scripts/full_pipeline.py`
- **Scan Drive only:** `python3 scripts/sync_drive.py`
- **Normalize only:** `python3 scripts/normalize.py`
- **Install dependencies:** `pip3 install -r requirements.txt`

## Important Rules
- NEVER commit `.env`, `credentials.json`, or `token.json`
- Google Sheets is the single source of truth — dashboard reads from Sheets only
- All external API calls happen in `services/` — controllers never call APIs directly
- Cross-referencing happens during normalization, not at render time
- When something breaks, describe the problem in plain English to Claude Code
