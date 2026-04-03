# ETL Pipeline

## What is ETL?

ETL stands for **Extract, Transform, Load**. In this project:

1. **Extract** — Scan Google Drive folders for new/updated spreadsheets
2. **Transform** — Send raw data to OpenAI for normalization + cross-reference reconciliation
3. **Load** — Write clean, linked data to the master Google Sheet

---

## The Pipeline at a Glance

```
Google Drive Folders
├── /leads/       ← user drops spreadsheets here
├── /invoices/
└── /projects/
       │
       ▼
  [1] EXTRACT — Drive API scans for new/updated files
       │
       ▼
  [2] READ — Sheets API reads each spreadsheet's content
       │
       ▼
  [3] NORMALIZE — OpenAI maps messy columns → canonical schema
       │
       ▼
  [4] RECONCILE — OpenAI cross-references across all three object types
       │
       ▼
  [5] LOAD — Write normalized, linked data to master Google Sheet
              ├── Leads tab
              ├── Invoices tab
              └── Projects tab
```

---

## Step 1: Extract — Scan Google Drive

**Script:** `scripts/sync_drive.py`

**What it does:**
1. Connects to Google Drive API using OAuth credentials
2. Looks inside three folders (`/leads`, `/invoices`, `/projects`) by folder ID
3. Lists all Google Spreadsheets in each folder
4. Compares modification times against last sync timestamp
5. Returns a list of new/updated files to process

**What "new" means:** Any spreadsheet modified since the last time the pipeline ran. The last sync timestamp is stored in `data/sync_state.json`.

**Example output:**
```json
{
  "new_files": [
    {"id": "1abc...xyz", "name": "Q2 Leads - Acme", "folder": "leads"},
    {"id": "2def...uvw", "name": "April Invoice - Beta", "folder": "invoices"}
  ],
  "last_synced": "2026-04-03T10:30:00Z"
}
```

**Claude Code prompt:**
> "Write scripts/sync_drive.py. Use the Drive API to scan three folders (IDs from .env: DRIVE_LEADS_FOLDER, DRIVE_INVOICES_FOLDER, DRIVE_PROJECTS_FOLDER). List Google Spreadsheets in each, compare against data/sync_state.json for last sync time, and return new/updated files."

---

## Step 2: Read — Pull Spreadsheet Content

**Part of:** `scripts/sync_drive.py` (continuation)

For each new/updated file found in Step 1, the script uses the Sheets API to read its content by spreadsheet ID. This gives us headers and rows.

**Why Sheets API and not Drive API?** Drive tells us *which* files exist. Sheets tells us *what's inside* them. We need both.

**Raw output example (a messy leads spreadsheet):**
```json
{
  "file_id": "1abc...xyz",
  "file_name": "Q2 Leads - Acme",
  "folder": "leads",
  "headers": ["Full Name", "Email Address", "Business Name", "How Found", "Date Added"],
  "rows": [
    ["Jane Smith", "jane@acme.com", "Acme Corporation", "LinkedIn", "April 1, 2026"],
    ["Bob Jones", "", "Beta Inc", "Cold email", "3/28/2026"]
  ]
}
```

Notice: column names don't match our schema, dates are inconsistent, some fields are empty. That's why Step 3 exists.

---

## Step 3: Normalize — OpenAI Structures the Data

**Script:** `scripts/normalize.py`

**What it does:** Sends raw spreadsheet data to OpenAI (`gpt-4o-mini`) with the canonical schema, and gets back clean, structured JSON.

**Before (raw):**
```json
{
  "headers": ["Full Name", "Email Address", "Business Name", "How Found", "Date Added"],
  "rows": [
    ["Jane Smith", "jane@acme.com", "Acme Corporation", "LinkedIn", "April 1, 2026"],
    ["Bob Jones", "", "Beta Inc", "Cold email", "3/28/2026"]
  ]
}
```

**The OpenAI prompt:**
```
Normalize this spreadsheet data into the Lead schema.

Schema:
- name (string): person's full name
- email (string): email address, empty string if missing
- company (string): company/business name
- source (string): how the lead was found
- stage (string): one of "new", "contacted", "converted" — default to "new" if not specified
- created_at (string): date in YYYY-MM-DD format

Raw headers: ["Full Name", "Email Address", "Business Name", "How Found", "Date Added"]
Raw rows: [["Jane Smith", "jane@acme.com", "Acme Corporation", "LinkedIn", "April 1, 2026"], ...]

Return JSON: {"leads": [...]}
```

**After (normalized):**
```json
{
  "leads": [
    {
      "name": "Jane Smith",
      "email": "jane@acme.com",
      "company": "Acme Corporation",
      "source": "LinkedIn",
      "stage": "new",
      "created_at": "2026-04-01"
    },
    {
      "name": "Bob Jones",
      "email": "",
      "company": "Beta Inc",
      "source": "Cold email",
      "stage": "new",
      "created_at": "2026-03-28"
    }
  ]
}
```

**What OpenAI handles that regex can't:**
- "Full Name" → maps to `name`
- "Business Name" → maps to `company`
- "April 1, 2026" → "2026-04-01"
- "3/28/2026" → "2026-03-28"
- Missing email → empty string (not null, not "N/A")
- No stage column → defaults to "new"

**Claude Code prompt:**
> "Write scripts/normalize.py. Read raw data from data/drive_sync.json. For each file, send headers and rows to OpenAI gpt-4o-mini with the canonical schema for that object type (lead/invoice/project). Use JSON response format. Save results to data/normalized.json."

---

## Step 4: Reconcile — Cross-Reference Objects

**Part of:** `scripts/normalize.py` (second pass)

After all objects are normalized, the pipeline makes one more OpenAI call to cross-reference them.

**The reconciliation prompt:**
```
I have three datasets. Cross-reference them by company/client name using fuzzy matching.

NEW DATA JUST ADDED:
Invoices: [{"client": "Acme Corporation", "amount": 4500, "invoice_number": "INV-0042"}]

EXISTING DATA:
Leads: [{"name": "Jane Smith", "company": "Acme Corp", "stage": "contacted"}]
Projects: [{"name": "Website Redesign", "client": "Acme Corp", "budget": 15000, "total_billed": 0}]

Rules:
1. If a new invoice matches a lead by company name → update lead stage to "converted"
2. If a new invoice matches a project by client name → add invoice amount to project total_billed
3. Consider name variations (abbreviations, capitalization, typos)

Return JSON:
{
  "lead_updates": [{"index": 0, "field": "stage", "new_value": "converted", "reason": "matched invoice INV-0042 for Acme Corporation"}],
  "project_updates": [{"index": 0, "field": "total_billed", "new_value": 4500, "reason": "matched invoice INV-0042 for Acme Corporation"}]
}
```

**What comes back:**
```json
{
  "lead_updates": [
    {"index": 0, "field": "stage", "new_value": "converted", "reason": "Invoice INV-0042 for 'Acme Corporation' matches lead company 'Acme Corp'"}
  ],
  "project_updates": [
    {"index": 0, "field": "total_billed", "new_value": 4500, "reason": "Invoice INV-0042 for 'Acme Corporation' matches project client 'Acme Corp'"}
  ]
}
```

**Key teaching point:** This is why we use a language model instead of exact string matching. "Acme Corporation" and "Acme Corp" are obviously the same company to a human — and to a language model. But a `==` comparison says they're different.

---

## Step 5: Load — Write to Master Google Sheet

**Part of:** `scripts/normalize.py` (final step)

After normalization and reconciliation, the pipeline writes everything to the master Google Sheet:

1. Read existing data from each tab (to avoid duplicates)
2. Merge new records with existing records
3. Apply the reconciliation updates (stage changes, billed amounts)
4. Write the full updated dataset back to each tab

**Deduplication:** Match by unique identifiers — `invoice_number` for invoices, `name + company` for leads, `name + client` for projects. If a record already exists, update it. If it's new, append it.

---

## Running the Pipeline

### Full pipeline (all steps):
```bash
python3 scripts/full_pipeline.py
```

### From the dashboard:
Click "Sync Drive" button → hits `POST /api/sync` → runs all steps.

### Individual steps:
```bash
python3 scripts/sync_drive.py      # Scan Drive only
python3 scripts/normalize.py       # Normalize + reconcile + load
```

---

## Pipeline State

The file `data/sync_state.json` tracks pipeline state:
```json
{
  "last_synced": "2026-04-03T10:30:00Z",
  "files_processed": ["1abc...xyz", "2def...uvw"],
  "leads_count": 12,
  "invoices_count": 8,
  "projects_count": 5
}
```

This prevents reprocessing files that haven't changed.

---

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| "No new files found" | Did you add/update a spreadsheet in Drive? | Check the Drive folder IDs in .env |
| Normalization returns wrong schema | Check the OpenAI prompt | Update the schema description in the prompt |
| Cross-reference missed a match | Names too different | OpenAI handles most variations, but very different names may need manual linking |
| Duplicate records in Sheets | Dedup logic may have missed | Check the unique key matching in normalize.py |
| Pipeline runs but dashboard shows old data | Dashboard caches may be stale | Hard refresh the browser (Cmd+Shift+R) |

---

## Key Teaching Point

> The normalization step is where messy, human-created data becomes structured, machine-readable data. The reconciliation step is where isolated data objects start talking to each other. Together, they turn a pile of spreadsheets into an operating system for your business.

This is the "aha" moment in the webinar — the audience sees that the real work isn't writing code, it's defining what your data should look like and how objects relate.
