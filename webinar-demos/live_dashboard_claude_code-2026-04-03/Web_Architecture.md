# Web Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            YOUR MACHINE                                 │
│                                                                         │
│  Google Drive Desktop App                                               │
│  ┌───────────────────────────────────────┐                             │
│  │ ~/Google Drive/BusinessHub/           │                             │
│  │   ├── /leads/      (spreadsheets)     │                             │
│  │   ├── /invoices/   (spreadsheets)     │                             │
│  │   └── /projects/   (spreadsheets)     │                             │
│  └──────────────────┬────────────────────┘                             │
│                     │ local files                                       │
│                     ▼                                                   │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐  │
│  │ ETL Pipeline (scripts/)      │    │ Flask App (localhost:3456)   │  │
│  │                              │    │                              │  │
│  │ 1. Scan Drive for new files  │    │ Routes → Controllers →      │  │
│  │ 2. Send to OpenAI to parse   │───>│ Services → Repositories     │  │
│  │ 3. Cross-reference objects   │    │                              │  │
│  │ 4. Write to Google Sheets    │    │ Actions:                     │  │
│  └──────────────────────────────┘    │  ├── Send email (Gmail)      │  │
│         │              │             │  └── Set reminder (Calendar)  │  │
│         ▼              ▼             └──────────────┬───────────────┘  │
│  ┌────────────┐ ┌────────────┐                     │                  │
│  │credentials │ │ .env       │                     ▼                  │
│  │.json       │ │ OPENAI_KEY │          ┌──────────────────┐         │
│  │token.json  │ └────────────┘          │ Browser           │         │
│  └────────────┘                         │ localhost:3456    │         │
│                                         └──────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐
│ Google Drive │ │  Google   │ │  Google   │ │   Google     │
│ API v3       │ │  Sheets   │ │  Gmail    │ │   Calendar   │
│ (files)      │ │  API v4   │ │  API      │ │   API v3     │
└──────────────┘ └───────────┘ └───────────┘ └──────────────┘
                       │
                 ┌─────────────┐
                 │  OpenAI API │
                 │  (gpt-4o-   │
                 │   mini)     │
                 └─────────────┘
```

---

## The Five APIs

| API | Role | Auth | When It's Called |
|-----|------|------|-----------------|
| **Google Drive** | Scan folders for new/updated spreadsheets | OAuth 2.0 | During ETL sync |
| **Google Sheets** | Read + write the master spreadsheet (primary datastore) | OAuth 2.0 | ETL writes, dashboard reads |
| **Google Gmail** | Send emails to leads and invoice contacts | OAuth 2.0 | User clicks "Email" or "Send Invoice" |
| **Google Calendar** | Create reminder events for invoice due dates | OAuth 2.0 | User clicks "Set Reminder" |
| **OpenAI** | Normalize messy spreadsheet data + fuzzy-match across objects | API key | During ETL normalization |

**Key insight:** Drive, Sheets, Gmail, and Calendar share one OAuth `credentials.json`. One auth flow, four APIs.

---

## Layer Breakdown

### Layer 1: Data Intake (Google Drive)
Google Drive desktop app syncs a folder structure to your local machine:
```
~/Google Drive/BusinessHub/
├── leads/          ← Drop spreadsheets with lead data here
├── invoices/       ← Drop spreadsheets with invoice data here
└── projects/       ← Drop spreadsheets with project data here
```

- Users can create/upload spreadsheets from any device (phone, web, desktop)
- Drive handles the sync automatically — no custom file watcher needed
- The ETL script scans these folders via the Drive API for new/updated files

### Layer 2: Normalization + Reconciliation (OpenAI)
This is the intelligence layer. OpenAI does two things:

**Normalize:** A user's "leads" spreadsheet might have columns called "Company", "Business Name", or "company_name". OpenAI maps them all to the canonical schema (see CLAUDE.md for schemas).

**Reconcile:** When a new invoice for "Acme Corp" arrives, OpenAI fuzzy-matches it against the leads table ("Acme Corporation", "acme", "ACME") and the projects table. It updates linked records automatically.

### Layer 3: Master Datastore (Google Sheets)
One master spreadsheet with three tabs:

| Tab | Contents | Updated By |
|-----|----------|-----------|
| **Leads** | All leads across all businesses | ETL pipeline |
| **Invoices** | All invoices | ETL pipeline |
| **Projects** | All projects with linked lead/invoice data | ETL pipeline |

Google Sheets is the single source of truth. The dashboard only reads from here. Non-technical users can also open Sheets directly to inspect or edit data.

### Layer 4: Flask Application
The web server. Clean architecture with SOLID principles:

```
Request → Route → Controller → Service → Repository
                                  │
                          ┌───────┴───────┐
                          │               │
                    Sheets API      Gmail/Calendar
                    (read data)     (take action)
```

**It reads from:** Google Sheets (via sheets_service)
**It acts on:** Gmail (send emails), Calendar (create events)
**It never:** Calls OpenAI or Drive directly — that's the ETL pipeline's job

### Layer 5: Frontend
Server-rendered HTML with targeted JavaScript:
- **Jinja2 templates** — pages render with data already embedded
- **Chart.js** (CDN) — revenue charts, pipeline visualizations
- **Fetch API** — async calls for email send, calendar remind, drive sync buttons

---

## Request Flows

### User views `/dashboard`
```
Browser → GET /dashboard
  → Flask: is user logged in?
    → NO → redirect /login
    → YES → sheets_service.read_all_tabs()
           → data_service.compute_metrics()
           → render dashboard.html
```

### User clicks "Email" on a lead
```
Browser → POST /api/email/send { to, subject, body }
  → email_controller.send()
    → gmail_service.send_email(to, subject, body)
      → Gmail API: messages.send()
    → return { status: "sent" }
```

### User clicks "Set Reminder" on an invoice
```
Browser → POST /api/calendar/remind { title, date, description }
  → calendar_controller.create_reminder()
    → calendar_service.create_event(title, date, description)
      → Calendar API: events.insert()
    → return { status: "created", event_link }
```

### User clicks "Sync Drive" (or runs ETL manually)
```
Browser → POST /api/sync  (or terminal: python3 scripts/full_pipeline.py)
  → etl_service.run_full_pipeline()
    → drive_service.scan_folders()
      → Drive API: list files modified since last sync
      → Download new spreadsheet data
    → openai_service.normalize(raw_data, object_type)
      → OpenAI API: parse columns → canonical schema
    → openai_service.reconcile(leads, invoices, projects)
      → OpenAI API: fuzzy-match across tables, update links
    → sheets_service.write_tab("Leads", normalized_leads)
    → sheets_service.write_tab("Invoices", normalized_invoices)
    → sheets_service.write_tab("Projects", normalized_projects)
  → return { status, counts }
```

---

## Cross-Reference Reconciliation Flow

This is the most important data flow in the system:

```
New invoice arrives: { client: "Acme Corporation", amount: 4500 }
    │
    ├── Search Leads tab: fuzzy match "Acme Corporation"
    │   Found: "Acme Corp" (lead, stage: "contacted")
    │   Action: update stage → "converted"
    │
    ├── Search Projects tab: fuzzy match "Acme Corporation"
    │   Found: "Website Redesign" (client: "Acme Corp")
    │   Action: total_billed += 4500
    │
    └── Write invoice to Invoices tab with links
```

OpenAI handles the fuzzy matching via a structured prompt:
```
Given this new invoice for client "Acme Corporation", find matching
records in the leads and projects tables. Consider variations like
abbreviations, capitalization, and common name differences.
Return matched record IDs and suggested updates.
```

---

## Authentication Architecture

### Dashboard Login (Flask-Login)
- Session-based auth with signed cookies
- Hardcoded demo user (admin/demo123)
- Protects all routes except /login

### Google OAuth (one flow for Drive, Sheets, Gmail, Calendar)
- OAuth 2.0 Desktop App flow
- First run: browser consent → writes token.json
- Subsequent runs: uses token.json silently
- Token auto-refreshes when expired
- Scopes cover all four Google APIs

### OpenAI API
- API key in .env as `OPENAI_API_KEY`
- No OAuth, no refresh — just a bearer token
- Model: `gpt-4o-mini` (cheap + fast for structured extraction)

---

## Data Flow Summary

| Step | What Happens | API Used |
|------|-------------|----------|
| 1. Intake | Spreadsheets land in Drive folders | Google Drive |
| 2. Scan | ETL detects new/updated files | Google Drive API |
| 3. Parse | Raw spreadsheet columns → canonical schema | OpenAI |
| 4. Reconcile | Cross-reference leads/invoices/projects | OpenAI |
| 5. Store | Write normalized data to master sheet | Google Sheets API |
| 6. Display | Dashboard reads from master sheet | Google Sheets API |
| 7. Email | User sends email to a contact | Gmail API |
| 8. Remind | User creates calendar reminder | Calendar API |

---

## Port and URL Map

| URL | Method | Auth | Description |
|-----|--------|------|-------------|
| `/login` | GET, POST | No | Login form |
| `/logout` | GET | Yes | Clear session |
| `/dashboard` | GET | Yes | Overview with metrics and charts |
| `/leads` | GET | Yes | Lead management table |
| `/invoices` | GET | Yes | Invoice tracking table |
| `/projects` | GET | Yes | Project cards with linked data |
| `/api/data` | GET | Yes | Full JSON dataset |
| `/api/sync` | POST | Yes | Trigger Drive sync + ETL pipeline |
| `/api/email/send` | POST | Yes | Send email via Gmail |
| `/api/calendar/remind` | POST | Yes | Create Calendar reminder |

---

## Security Notes (Demo Context)
- Hardcoded demo credentials — localhost only
- `.env`, `credentials.json`, `token.json` in `.gitignore`
- OpenAI API key never exposed to frontend
- Gmail sends only — no read access (scope is `gmail.send`)
- Drive is read-only (scope is `drive.readonly`)
- No HTTPS needed — localhost only
