# API Design

This document covers every API interaction in the project: the five external APIs we consume, the internal Flask endpoints, the data contracts between objects, and the cross-reference reconciliation logic.

---

## Part 1: External APIs

### Google Drive API v3

**What it does:** Scans Drive folders for new or updated spreadsheets.

**Base URL:** `https://www.googleapis.com/drive/v3`

**Auth:** OAuth 2.0 (shared credentials.json with Sheets/Gmail/Calendar)

**The calls we make:**

**List files in a folder:**
```python
service.files().list(
    q="'FOLDER_ID' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc"
)
```

**What comes back:**
```json
{
  "files": [
    {
      "id": "1abc...xyz",
      "name": "Q2 Leads - Acme",
      "modifiedTime": "2026-04-03T10:00:00.000Z"
    }
  ]
}
```

**Reading spreadsheet content:** We don't use Drive to read content — once we have the file ID, we switch to the Sheets API (which can read any Google Spreadsheet by ID). Drive is just the index.

**Common errors:**
| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token expired | Delete token.json, re-run auth |
| 404 | Folder ID is wrong | Double-check the folder IDs in .env |
| 403 | Drive API not enabled | Enable it in Google Cloud Console |

---

### Google Sheets API v4

**What it does:** Reads and writes the master spreadsheet (primary datastore).

**Base URL:** `https://sheets.googleapis.com/v4/spreadsheets`

**Auth:** OAuth 2.0 (same credentials.json)

**Reading a tab:**
```python
service.spreadsheets().values().get(
    spreadsheetId=MASTER_SHEET_ID,
    range="Leads!A1:Z1000"
)
```

**Writing/updating a tab:**
```python
service.spreadsheets().values().update(
    spreadsheetId=MASTER_SHEET_ID,
    range="Leads!A1",
    valueInputOption="USER_ENTERED",
    body={"values": rows}
)
```

**Appending new rows:**
```python
service.spreadsheets().values().append(
    spreadsheetId=MASTER_SHEET_ID,
    range="Leads!A1",
    valueInputOption="USER_ENTERED",
    body={"values": new_rows}
)
```

**Master spreadsheet structure:**
| Tab Name | Contains |
|----------|---------|
| Leads | All normalized leads |
| Invoices | All normalized invoices |
| Projects | All normalized projects |

**Key details:**
- All values come back as strings — cast numbers and dates in the normalization step
- Empty cells are omitted, so row lengths can vary
- Rate limit: 60 requests/min per user, 300/min per project
- First row of each tab is always headers matching the canonical schema

**Common errors:**
| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token expired | Delete token.json, re-auth |
| 404 | Wrong spreadsheet ID | Check MASTER_SHEET_ID in .env |
| 429 | Rate limit | Wait 60s. Add exponential backoff for automation. |

---

### OpenAI API

**What it does:** Two jobs — normalize messy spreadsheet data into canonical schemas, and fuzzy-match records across tables for cross-referencing.

**Base URL:** `https://api.openai.com/v1`

**Auth:** API key in .env as `OPENAI_API_KEY`

**Model:** `gpt-4o-mini` — cheap (~$0.15/1M input tokens), fast, and more than capable for structured extraction.

**Call 1 — Normalize a spreadsheet:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": "You normalize spreadsheet data into a canonical schema. Return valid JSON only."
        },
        {
            "role": "user",
            "content": f"""Normalize this spreadsheet data into the Lead schema.

Schema: name (string), email (string), company (string), source (string), stage (string: new/contacted/converted), created_at (string: YYYY-MM-DD)

Raw headers: {headers}
Raw rows: {rows}

Return JSON: {{"leads": [...]}}"""
        }
    ]
)
```

**What comes back:**
```json
{
  "leads": [
    {
      "name": "Jane Smith",
      "email": "jane@acme.com",
      "company": "Acme Corp",
      "source": "Referral",
      "stage": "new",
      "created_at": "2026-04-01"
    }
  ]
}
```

**Call 2 — Cross-reference reconciliation:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": "You cross-reference business data objects. Match by company/client name using fuzzy matching. Return updates as JSON."
        },
        {
            "role": "user",
            "content": f"""New invoices were added:
{new_invoices}

Existing leads:
{existing_leads}

Existing projects:
{existing_projects}

For each new invoice, find matching leads and projects by client/company name.
Consider name variations (abbreviations, capitalization, typos).

Return JSON:
{{
  "lead_updates": [{{"lead_index": 0, "new_stage": "converted", "matched_invoice": "INV-0042"}}],
  "project_updates": [{{"project_index": 0, "add_to_billed": 4500, "matched_invoice": "INV-0042"}}]
}}"""
        }
    ]
)
```

**Cost estimate for a demo:**
- Normalizing 25 rows: ~500 tokens input, ~300 tokens output = ~$0.0001
- Cross-referencing 25 records: ~1000 tokens = ~$0.0002
- Full pipeline run: under $0.01

**Common errors:**
| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Bad API key | Check OPENAI_API_KEY in .env |
| 429 | Rate limit | You're unlikely to hit this. If so, add a 1s delay between calls. |
| 500 | OpenAI outage | Retry once. If it persists, the pipeline still has the raw data — just skip normalization. |

---

### Google Gmail API

**What it does:** Sends emails from the user's Gmail account.

**Auth:** OAuth 2.0 (same credentials.json, scope: `gmail.send`)

**The one call we make:**
```python
import base64
from email.mime.text import MIMEText

message = MIMEText(body)
message["to"] = to_address
message["subject"] = subject
raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

service.users().messages().send(
    userId="me",
    body={"raw": raw}
).execute()
```

**What comes back:**
```json
{
  "id": "18f1a2b3c4d5e6f7",
  "threadId": "18f1a2b3c4d5e6f7",
  "labelIds": ["SENT"]
}
```

**Key details:**
- Scope `gmail.send` is send-only — the app cannot read the user's inbox
- Rate limit: 2,000 emails/day for regular accounts (irrelevant for a demo)
- The "From" address is automatically the authenticated Google account

**Common errors:**
| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token missing send scope | Delete token.json, re-auth with updated scopes |
| 403 | Gmail API not enabled | Enable it in Google Cloud Console |

---

### Google Calendar API v3

**What it does:** Creates reminder events on the user's Google Calendar.

**Auth:** OAuth 2.0 (same credentials.json, scope: `calendar.events`)

**The one call we make:**
```python
event = {
    "summary": "Invoice Due: INV-0042 - Acme Corp ($4,500)",
    "description": "Invoice INV-0042 for Acme Corp is due today.",
    "start": {"date": "2026-04-15"},
    "end": {"date": "2026-04-15"},
    "reminders": {
        "useDefault": False,
        "overrides": [
            {"method": "popup", "minutes": 1440},
            {"method": "email", "minutes": 1440}
        ]
    }
}

service.events().insert(
    calendarId="primary",
    body=event
).execute()
```

**What comes back:**
```json
{
  "id": "abc123",
  "htmlLink": "https://calendar.google.com/calendar/event?eid=...",
  "status": "confirmed"
}
```

**Key details:**
- All-day event (no time, just date) — keeps it simple
- Reminder set to 24 hours before (1440 minutes)
- Both popup and email reminders
- Returns a direct link to the event

**Common errors:**
| Error | Meaning | Fix |
|-------|---------|-----|
| 401 | Token missing calendar scope | Delete token.json, re-auth |
| 403 | Calendar API not enabled | Enable in Cloud Console |

---

## Part 2: Internal API Endpoints (Flask)

### GET `/api/data`
Returns the full dataset from all three Sheets tabs as JSON.

**Response:**
```json
{
  "leads": [...],
  "invoices": [...],
  "projects": [...],
  "metadata": {
    "leads_count": 12,
    "invoices_count": 8,
    "projects_count": 5,
    "last_synced": "2026-04-03T10:30:00Z"
  }
}
```

### POST `/api/sync`
Triggers the full ETL pipeline: scan Drive → normalize with OpenAI → reconcile → write to Sheets.

**Response (success):**
```json
{
  "status": "success",
  "message": "Synced. 3 new leads, 2 new invoices, 1 lead updated to converted.",
  "timestamp": "2026-04-03T10:31:00Z"
}
```

### POST `/api/email/send`
Sends an email via Gmail.

**Request:**
```json
{
  "to": "jane@acme.com",
  "subject": "Following up on our conversation",
  "body": "Hi Jane, ..."
}
```

**Response:**
```json
{
  "status": "sent",
  "message_id": "18f1a2b3c4d5e6f7"
}
```

### POST `/api/calendar/remind`
Creates a Google Calendar event.

**Request:**
```json
{
  "title": "Invoice Due: INV-0042 - Acme Corp ($4,500)",
  "date": "2026-04-15",
  "description": "Invoice INV-0042 for Acme Corp is due."
}
```

**Response:**
```json
{
  "status": "created",
  "event_link": "https://calendar.google.com/calendar/event?eid=..."
}
```

---

## Part 3: Data Object Design

### Object Relationship Diagram

```
                    ┌─────────────┐
                    │   Project    │
                    │             │
                    │  sheet_id ──────── Google Sheet
                    │  client ◄────┐
                    └──────┬──────┘
                           │
              linked by company/client name (fuzzy)
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌─────────────┐              ┌─────────────┐
     │    Lead      │              │   Invoice    │
     │             │              │             │
     │  company ───┘              │  client ────┘
     │  project ◄── auto-filled   │
     │  sheet_id ──── Google Sheet │
     └─────────────┘              └─────────────┘
```

### How Objects Relate

The three objects connect through **company/client name**. This is the glue that holds the system together:

- A **Lead** has a `company` field (e.g., "Acme Corp")
- An **Invoice** has a `client` field (e.g., "Acme Corporation")
- A **Project** has a `client` field (e.g., "Acme Corp")

OpenAI handles fuzzy matching so "Acme Corp", "Acme Corporation", and "acme" are all recognized as the same entity.

### The Lifecycle of a Business Relationship

```
1. Lead enters system (stage: "new")
   └── company: "Acme Corp"

2. Project created for that client
   └── Lead.project auto-filled to "Website Redesign"
   └── Lead.stage stays "new" or "contacted"

3. Invoice uploaded for that client
   └── Lead.stage auto-updated to "converted"
   └── Project.total_billed += invoice amount
   └── Invoice linked to both Lead and Project by client name
```

### Canonical Schemas

### Lead
```
Field       Type      Required   Example                    Notes
─────       ────      ────────   ───────                    ─────
name        string    yes        "Jane Smith"               Contact's full name
email       string    no         "jane@acme.com"            Used for Email button
company     string    yes        "Acme Corp"                THE KEY: links to Project + Invoice
source      string    no         "Referral"                 How the lead was found
stage       string    yes        "new"                      new | contacted | converted (auto-updated)
project     string    no         "Website Redesign"         Auto-filled by reconciliation
created_at  string    yes        "2026-04-01"               ISO 8601
sheet_id    string    no         "1zF_vg365..."             Google Sheet this lead came from
```

### Invoice
```
Field           Type      Required   Example                Notes
─────           ────      ────────   ───────                ─────
invoice_number  string    yes        "INV-0042"             Unique identifier
client          string    yes        "Acme Corp"            THE KEY: links to Lead + Project
amount          number    yes        4500.00                Dollar amount
due_date        string    yes        "2026-04-15"           ISO 8601, used for Calendar reminders
status          string    yes        "sent"                 draft | sent | paid | overdue
email           string    no         "billing@acme.com"     Used for Send Invoice button
```

### Project
```
Field          Type      Required   Example                 Notes
─────          ────      ────────   ───────                 ─────
name           string    yes        "Website Redesign"      Project name
client         string    yes        "Acme Corp"             THE KEY: links to Lead + Invoice
budget         number    yes        15000.00                Total project budget
total_billed   number    yes        4500.00                 Auto-updated by reconciliation
deadline       string    no         "2026-06-01"            ISO 8601
status         string    yes        "active"                active | completed | on_hold
sheet_id       string    no         "1-zRobLafq..."         Google Sheet linked to this project
```

### Design Decisions

**Why company/client name as the link (not IDs)?**
Because the data comes from human-created spreadsheets. People don't assign IDs to their leads. They write company names. OpenAI's fuzzy matching handles the variations that would break an ID-based system.

**Why `sheet_id` on Lead and Project?**
Each project can have its own Google Sheet. Leads can be imported from different sheets. The `sheet_id` traces where the data came from and provides a "View Sheet" link in the dashboard.

**Why `project` on Lead is auto-filled?**
When the reconciliation step finds a project whose `client` matches the lead's `company`, it fills in the `project` field automatically. This means leads are tagged with their project without the user doing anything.

**Why `total_billed` on Project is auto-updated?**
When a new invoice arrives for a client that matches a project, the reconciliation adds the invoice amount to `total_billed`. The budget progress bar on the dashboard updates automatically.

---

## Part 4: Cross-Reference Rules

| Trigger | Lookup | Auto-Update |
|---------|--------|-------------|
| New invoice | Match lead by client name | Lead stage → "converted" |
| New invoice | Match project by client name | Project total_billed += invoice amount |
| New lead | Match project by company | Link lead to project |
| New project | Match leads by company | Associate existing leads |
| New project | Match invoices by client | Calculate total billed to date |

**Fuzzy matching examples (handled by OpenAI):**
- "Acme Corp" = "Acme Corporation" = "acme" = "ACME CORP."
- "Jane Smith" = "J. Smith" = "jane smith"
- "INV-42" = "INV-0042" = "Invoice #42"

---

## Part 5: Extending the System

### Adding a new object type (e.g., Expenses, Contracts)
1. Define the canonical schema in this document
2. Create a new Drive folder for intake
3. Add a new tab to the master spreadsheet
4. Update the OpenAI normalization prompt to handle the new type
5. Add cross-reference rules (what does it link to?)
6. Add a Flask route, controller, and template
7. Update the dashboard metrics

**Claude Code prompt:**
> "I want to add an Expenses object to the dashboard. Follow the same pattern as Invoices: add a canonical schema, a Drive folder, a Sheets tab, normalization logic, and a page at /expenses. Cross-reference expenses with projects by client name."
