# Personal Business Dashboard

**Webinar Project** — Build a personal business command center with Claude Code. Manage leads, invoices, and projects across all your businesses from one dashboard, powered by Google Drive, Google Sheets, OpenAI, Gmail, and Google Calendar.

---

## The Idea

You're an entrepreneur running multiple businesses. Your data lives in scattered spreadsheets, inboxes, and folders. This project turns all of that into one dashboard where you can:

- **See everything** — Leads, invoices, projects, revenue, all in one place
- **Auto-organize** — Drop a spreadsheet into a Google Drive folder and the pipeline normalizes it into your master database
- **Cross-reference** — Upload an invoice for "Acme Corp" and the system automatically finds the matching lead and updates their status to "converted"
- **Take action** — Email a lead or send an invoice directly from the dashboard
- **Stay on top of payments** — Set Google Calendar reminders for invoice due dates with one click

---

## How It Works

```
Google Drive Folders (/leads, /invoices, /projects)
    ↓ syncs locally via Drive desktop app
    ↓
ETL Pipeline scans for new spreadsheets
    ↓
OpenAI normalizes messy data → consistent schema
    ↓
OpenAI cross-references: links leads ↔ invoices ↔ projects
    ↓
Google Sheets (master datastore — single source of truth)
    ↓
Dashboard (view + act)
   ├── Send emails via Gmail
   └── Schedule reminders via Google Calendar
```

---

## Quick Start

```bash
cd finished_product
./start.sh
```

Opens your browser to **http://localhost:3456**. Login: **admin** / **demo123**.

The script installs dependencies, kills anything on port 3456, starts Flask, and opens the browser. Ctrl+C to stop.

---

## The Five APIs (One OAuth)

| API | Role | Auth |
|-----|------|------|
| **Google Drive** | File intake — scan folders for new spreadsheets | OAuth 2.0 |
| **Google Sheets** | Primary datastore — reads and writes all business data | OAuth 2.0 |
| **Gmail** | Send emails to leads and invoice contacts | OAuth 2.0 |
| **Google Calendar** | Create payment reminders and follow-up events | OAuth 2.0 |
| **OpenAI** | Normalize messy spreadsheets + fuzzy-match across objects | API key |

Drive, Sheets, Gmail, and Calendar share one `credentials.json`. One auth flow unlocks all four. OpenAI just needs an API key in `.env`.

---

## Data Objects

The system manages three object types. Each has a canonical schema that all data gets normalized into:

| Object | Key Fields | Actions |
|--------|-----------|---------|
| **Lead** | name, email, company, source, stage | Email, view linked projects/invoices |
| **Invoice** | invoice_number, client, amount, due_date, status | Send via email, set calendar reminder |
| **Project** | name, client, budget, total_billed, deadline, status | View linked leads/invoices, track budget |

**Cross-referencing:** When an invoice arrives for "Acme Corp", the pipeline automatically finds the matching lead ("Acme Corporation") and project, updates the lead's stage to "converted", and adds the invoice amount to the project's total billed. OpenAI handles the fuzzy matching.

---

## Dashboard Pages

| URL | What It Shows |
|-----|--------------|
| `/login` | Username/password (admin / demo123) |
| `/dashboard` | Overview — metrics, revenue chart, recent activity, "Sync Drive" button |
| `/leads` | Lead table with stage badges, email buttons, filters |
| `/invoices` | Invoice table with status badges, "Send Invoice" and "Set Reminder" buttons |
| `/projects` | Project cards with budget progress bars, linked lead/invoice counts |

---

## Project Documentation

| Document | Who It's For | Purpose |
|----------|-------------|---------|
| **CLAUDE.md** | Claude Code | Project briefing — Claude reads this automatically. Defines schemas, architecture, cross-reference rules, and commands. |
| **Design.md** | Presenters & Builders | UI/UX spec — every page layout, color palette, component design, and the exact Claude Code prompts to build each page. |
| **Web_Architecture.md** | Everyone | Full system diagram — how data flows from Drive through OpenAI to Sheets to the dashboard, plus auth architecture and all request flows. |
| **API_Design.md** | Builders & Debuggers | Every API interaction — Drive, Sheets, Gmail, Calendar, OpenAI. Includes request/response examples, error tables, data contracts, and cross-reference rules. |
| **Coding_Style_Guide.md** | Non-technical / First-timers | How to read Python, where to find things, how to read error messages, and how to ask Claude Code for help. Includes a full lookup table for "if X breaks, look in Y." |
| **ETL_Pipeline.md** | Everyone | The data pipeline — how Drive folders become structured data. Covers scanning, normalization, cross-reference reconciliation, and loading. Shows before/after examples. |
| **Getting_Started.md** | Attendees following along | Prerequisites, Google Cloud setup, Drive folder creation, master Sheet setup, OpenAI key, and running the app. Every step has a "what can go wrong" section. |
| **Working_With_Claude_Code.md** | Everyone | Phase-by-phase prompts for building the project, the Golden Formula for prompting, debugging strategies, and live demo tips. |

---

## Architecture

Clean architecture with SOLID principles. Every request flows through four layers:

```
Route → Controller → Service → Repository
(URL)    (HTTP)       (Logic)   (Data I/O)
```

```
finished_product/
├── start.sh                    ← Run this
├── app.py                      ← Wires all layers together
├── config.py                   ← Environment + constants
│
├── routes/                     ← URL → controller (thin)
│   ├── auth_routes.py          ←   /login, /logout
│   ├── dashboard_routes.py     ←   /dashboard, /leads, /invoices, /projects
│   ├── api_routes.py           ←   /api/data, /api/sync
│   ├── email_routes.py         ←   /api/email/send
│   └── calendar_routes.py      ←   /api/calendar/remind
│
├── controllers/                ← Request/response handling
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── api_controller.py
│   ├── email_controller.py
│   └── calendar_controller.py
│
├── services/                   ← Business logic + API calls
│   ├── auth_service.py
│   ├── data_service.py
│   ├── drive_service.py        ←   Google Drive scanning
│   ├── sheets_service.py       ←   Google Sheets read/write
│   ├── openai_service.py       ←   Normalization + reconciliation
│   ├── gmail_service.py        ←   Send emails
│   ├── calendar_service.py     ←   Create calendar events
│   └── etl_service.py          ←   Full pipeline orchestration
│
├── repositories/               ← Data access
│   ├── user_repository.py
│   └── data_repository.py
│
├── models/
│   └── user.py
│
├── scripts/                    ← Standalone ETL scripts
│   ├── sync_drive.py
│   ├── normalize.py
│   └── full_pipeline.py
│
├── templates/                  ← HTML pages
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── leads.html
│   ├── invoices.html
│   ├── projects.html
│   └── email_compose.html
│
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
│
└── data/                       ← Local pipeline state
    └── sync_state.json
```

---

## Prerequisites

- **Python 3.10+**
- **Google Cloud credentials** (OAuth Desktop app — see Getting_Started.md)
- **Google Drive for Desktop** syncing your BusinessHub folders
- **OpenAI API key** (platform.openai.com)
- **A master Google Sheet** with Leads, Invoices, Projects tabs

---

## Commands

| Command | What It Does |
|---------|-------------|
| `./start.sh` | Install deps + start app + open browser |
| `python3 app.py` | Start Flask server only |
| `python3 scripts/full_pipeline.py` | Run full ETL: scan → normalize → reconcile → load |
| `python3 scripts/sync_drive.py` | Scan Drive folders for new files only |
| `python3 scripts/normalize.py` | Normalize + reconcile only |

---

## For the Webinar

| Phase | What You Build Live | Time |
|-------|-------------------|------|
| 1 | Google OAuth + Drive folders + Sheets setup | 15 min |
| 2 | ETL pipeline: Drive → OpenAI → Sheets | 15 min |
| 3 | Dashboard with cross-referenced data | 15 min |
| 4 | Gmail: email a lead from the dashboard | 5 min |
| 5 | Calendar: set an invoice reminder | 5 min |
| 6 | Q&A | 5 min |

**Key teaching moments:**
- The credentials.json download warning (say it twice — "you won't see this again")
- Before/after of OpenAI normalization (messy columns → clean schema)
- Cross-reference reconciliation (invoice auto-updates lead status)
- Describing a bug in plain English and letting Claude Code fix it
- "You don't need to understand the code — you need to understand what you want"
