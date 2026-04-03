# Coding Style Guide

**Audience:** Non-technical users, first-time coders, and anyone following along with the webinar. This guide is written so you can read the code, find where things happen, and fix problems — even if you've never written Python before.

---

## How to Read Python (The 2-Minute Version)

### Variables — Naming things
```python
company_name = "Acme Corp"
invoice_total = 4500.00
is_overdue = True
```
A variable is a label stuck on a value. Read `=` as "is set to." We use `snake_case` — all lowercase, words separated by underscores.

### Functions — Reusable actions
```python
def get_overdue_invoices():
    # everything indented under here belongs to this function
    all_invoices = sheets_service.read_tab("Invoices")
    return [inv for inv in all_invoices if inv["status"] == "overdue"]
```
`def` means "define a function." The name tells you what it does. `return` is the result.

### If/Else — Making decisions
```python
if invoice["status"] == "overdue":
    send_reminder(invoice)
else:
    skip(invoice)
```
Read as English: "If the invoice is overdue, send a reminder. Otherwise, skip it."

### Imports — Borrowing from libraries
```python
from flask import Flask, render_template
from openai import OpenAI
```
The code saying "I need tools from these libraries."

### Indentation matters
Python uses 4 spaces to show what belongs inside what. Wrong indentation = broken code.

---

## Project Architecture (Route → Controller → Service → Repository)

This project follows a layered pattern. Each layer has one job:

```
routes/          "What URL was hit?"          → picks the right controller
controllers/     "What did the user send?"    → reads the request, calls service
services/        "What should happen?"        → business logic, API calls
repositories/    "Where is the data?"         → reads/writes files or Sheets
```

**Why this matters to you:** When something breaks, you know exactly which layer to look at.

### Following a request through the layers

User clicks "Send Invoice Email" → here's what happens:

```
1. routes/email_routes.py        → POST /api/email/send matched
2. controllers/email_controller.py → reads "to", "subject", "body" from request
3. services/gmail_service.py      → builds the email, calls Gmail API
4. Gmail API                      → email sent
5. Controller                     → returns {"status": "sent"} to browser
```

---

## Project Naming Conventions

### Files
| Pattern | Example | Used For |
|---------|---------|----------|
| `snake_case.py` | `gmail_service.py` | Python modules |
| `snake_case.html` | `invoices.html` | HTML templates |
| `snake_case.js` | `dashboard.js` | JavaScript files |
| `snake_case.css` | `style.css` | Stylesheets |
| `UPPER_CASE.md` | `CLAUDE.md` | Project context docs |
| `Title_Case.md` | `Design.md` | Reference docs |

### Variables and functions
```python
# YES — descriptive snake_case
overdue_invoices = get_invoices_by_status("overdue")
total_billed = sum(inv["amount"] for inv in invoices)

# NO — avoid these
d = get()              # too short
getData = fetch()      # camelCase is JavaScript, not Python
INVOICES = fetch()     # ALL_CAPS is for constants only
```

### Constants
```python
OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_REMINDER_MINUTES = 1440
FLASK_PORT = 3456
```

---

## Where Things Live

**Someone dropped a spreadsheet in Drive and it's not showing up:**
→ Check `scripts/sync_drive.py` — is the folder ID correct in `.env`?

**The data looks wrong on the dashboard:**
→ Check the master Google Sheet directly — is the data correct there?
→ YES → Problem is in the template (`templates/`) or controller
→ NO → Problem is in the pipeline (`scripts/normalize.py`)

**An email didn't send:**
→ Check `services/gmail_service.py`
→ Check the terminal for error output
→ Is `gmail.send` in your OAuth scopes?

**Calendar reminder wasn't created:**
→ Check `services/calendar_service.py`
→ Is `calendar.events` in your OAuth scopes?

**OpenAI returned garbage data:**
→ Check the prompt in `services/openai_service.py`
→ Is the schema description clear? Is the raw data being sent correctly?

### Quick lookup table

| If it touches... | Look in... |
|-------------------|-----------|
| A URL / page | `routes/` |
| Request/response handling | `controllers/` |
| Google Drive | `services/drive_service.py` |
| Google Sheets | `services/sheets_service.py` |
| Gmail | `services/gmail_service.py` |
| Calendar | `services/calendar_service.py` |
| OpenAI | `services/openai_service.py` |
| Data normalization | `services/etl_service.py` |
| File reading/writing | `repositories/data_repository.py` |
| User login | `services/auth_service.py` |
| HTML layout | `templates/` |
| Styling | `static/css/style.css` |
| Charts & buttons | `static/js/dashboard.js` |
| API tokens & config | `.env` + `config.py` |

---

## How to Read Python Error Messages

Read errors **bottom to top**. The last line is the most important.

### Example:
```
Traceback (most recent call last):
  File "services/gmail_service.py", line 23, in send_email
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
  File "...", line 120, in execute
    raise HttpError(resp, content)
googleapiclient.errors.HttpError: <HttpError 403 "Insufficient Permission">
```

**Reading this:**
1. **Bottom:** `HttpError 403 "Insufficient Permission"` — Gmail says you don't have permission
2. **Middle:** It happened in `send_email` at line 23 of `gmail_service.py`
3. **Fix:** Your OAuth token doesn't include `gmail.send` scope. Delete `token.json` and re-auth.

### Common errors:

| Error | Plain English | Likely Fix |
|-------|--------------|------------|
| `FileNotFoundError` | A file is missing | Check the path, or run the pipeline first |
| `KeyError: 'amount'` | Expected a field that's not there | Check the Sheets data or OpenAI output |
| `ModuleNotFoundError` | Library not installed | Run `pip3 install -r requirements.txt` |
| `HttpError 401` | Auth token expired or missing | Delete `token.json`, re-run |
| `HttpError 403` | API not enabled or wrong scope | Check Google Cloud Console |
| `openai.AuthenticationError` | Bad OpenAI key | Check `OPENAI_API_KEY` in `.env` |
| `openai.RateLimitError` | Too many requests | Wait a moment, retry |

---

## How to Ask Claude Code for Help

### Good prompts (describe the problem):
> "The /invoices page loads but the table is empty. The master Google Sheet has data in the Invoices tab. Something is wrong between Sheets and the dashboard."

> "When I click 'Send Email' on a lead, I get a 403 error in the terminal. The Gmail API is enabled in my Cloud Console."

> "The pipeline ran but the lead stage didn't update to 'converted' even though I uploaded an invoice for the same company."

### The Golden Formula
**Context** + **Goal** + **Constraints**

> "I'm on the /projects page [context]. The budget progress bar always shows 0% even though total_billed has data in Sheets [goal: fix the progress bar]. Don't change the card layout [constraint]."

---

## Quick Reference Card

```
Start the app ............... ./start.sh
Install packages ............ pip3 install -r requirements.txt
Run full pipeline ........... python3 scripts/full_pipeline.py
Scan Drive only ............. python3 scripts/sync_drive.py
Normalize only .............. python3 scripts/normalize.py
Dashboard URL ............... http://localhost:3456
Login ....................... admin / demo123
Config ...................... .env (secrets) + config.py (settings)
Architecture ................ route → controller → service → repository
```
