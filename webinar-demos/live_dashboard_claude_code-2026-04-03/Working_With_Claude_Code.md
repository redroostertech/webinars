# Working With Claude Code

How to use Claude Code to build, debug, and iterate on this project. Written for people who have never used Claude Code (or any AI coding tool) before.

---

## What is Claude Code?

Claude Code is a command-line tool that runs on your machine. You type instructions in plain English, and it reads your code, writes new code, runs commands, and edits files — all within your project. Think of it as a developer sitting next to you who can read and modify every file in the folder.

**Key difference from ChatGPT/Claude.ai:** Claude Code sees your actual project files. It doesn't guess — it reads.

---

## Starting a Session

```bash
cd ~/Documents/webinar_demo/live_dashboard_claude_code-2026-04-03/finished_product
claude
```

**What happens first:** Claude Code reads `CLAUDE.md` automatically. It now knows the tech stack, data schemas, architecture, and commands before you ask anything.

---

## The Golden Formula

Every prompt follows:

> **Context** + **Goal** + **Constraints**

| Part | What It Does | Example |
|------|-------------|---------|
| Context | Where you are, what's happening | "I'm on the /invoices page" |
| Goal | The outcome you want | "Add a 'Set Reminder' button on overdue invoices" |
| Constraints | What NOT to touch | "Don't change the table layout" |

**Full example:**
> "I'm on the /invoices page [context]. Overdue invoices need a 'Set Reminder' button that creates a Google Calendar event for the due date [goal]. Use the existing calendar_service and keep the table layout as-is [constraints]."

---

## Phase-by-Phase: Building This Project

### Phase 1: Scaffold the App

> "Set up a Flask app with Flask-Login following the architecture in CLAUDE.md. Create the route → controller → service → repository layers. Add routes for /login, /dashboard, /leads, /invoices, /projects. Protect all routes except /login. Use a hardcoded demo user admin/demo123."

**What Claude Code does:**
1. Reads CLAUDE.md
2. Creates all directories and __init__.py files
3. Creates app.py with the app factory pattern
4. Wires up all layers
5. Creates base templates

---

### Phase 2: Google Auth + Sheets Service

> "Create services/sheets_service.py. It should authenticate with Google using credentials.json and the scopes in CLAUDE.md. Implement read_tab(tab_name) and write_tab(tab_name, rows) methods. Read the master sheet ID from config."

Then:

> "Create services/drive_service.py. It should scan the three Drive folders from .env for Google Spreadsheets modified since the last sync. Return a list of file IDs, names, and which folder they came from."

---

### Phase 3: OpenAI Normalization

> "Create services/openai_service.py with two methods: normalize(raw_data, object_type) that maps messy spreadsheet columns to our canonical schema using gpt-4o-mini with JSON response format, and reconcile(new_data, existing_leads, existing_invoices, existing_projects) that cross-references objects by company name with fuzzy matching. Use the schemas and cross-reference rules from CLAUDE.md."

---

### Phase 4: ETL Pipeline Scripts

> "Create scripts/full_pipeline.py that orchestrates the full ETL pipeline: scan Drive with drive_service, read each new spreadsheet with sheets_service, normalize with openai_service, reconcile across all three object types, and write back to the master sheet. Track pipeline state in data/sync_state.json."

---

### Phase 5: Dashboard Pages

> "Build the /dashboard page following Design.md. Show 4 metric cards (total leads, outstanding invoices, active projects, monthly revenue), a recent activity feed, and a Chart.js revenue bar chart. Read all data from the Sheets service."

Then:

> "Build the /leads page. Filterable table with name, email, company, source, stage. Add an 'Email' button per row that opens a compose modal. Stage shown as colored badges."

> "Build the /invoices page. Table with status badges. Add 'Send Invoice' and 'Set Reminder' buttons on each row."

> "Build the /projects page. Card layout with budget progress bars. Show linked leads and invoices counts. Expand on click to show details."

---

### Phase 6: Gmail + Calendar Actions

> "Create services/gmail_service.py with a send_email(to, subject, body) method that sends via the Gmail API. Create an email_controller and email_routes that handle POST /api/email/send. The email compose modal should pre-fill the 'to' field from the lead or invoice record."

> "Create services/calendar_service.py with a create_reminder(title, date, description) method that creates an all-day Google Calendar event with a 24-hour popup and email reminder. Wire it to POST /api/calendar/remind. The 'Set Reminder' button on invoices should pre-fill with the due date and invoice details."

---

### Phase 7: Tie It Together

> "Add a 'Sync Drive' button on the dashboard that calls POST /api/sync to run the full ETL pipeline. Show a loading state while it runs and display the result (how many records were added/updated)."

---

## Debugging With Claude Code

### When something breaks

**Don't try to fix code yourself.** Describe the problem:

> "I clicked 'Send Email' on a lead and got a 403 error in the terminal. The Gmail API is enabled in Cloud Console. What's wrong?"

> "The pipeline ran but the lead stage didn't change to 'converted' even though I uploaded an invoice for the same company. Check the reconciliation logic."

> "The /projects page shows budget progress bars at 0% for all projects even though total_billed has values in the Sheets tab."

### Common debugging prompts

| Situation | What to Say |
|-----------|------------|
| App won't start | "app.py crashes on startup. Read the error and fix it." |
| Page shows no data | "/leads page loads but the table is empty. Master Sheet has data." |
| Email fails | "Send email returns 403. Gmail API is enabled. Check the OAuth scopes." |
| Calendar event not created | "Set Reminder button does nothing. Check the calendar service and route." |
| Pipeline didn't reconcile | "New invoice for Acme Corp didn't update the lead stage. Check the reconciliation prompt." |
| OpenAI returns bad data | "Normalization put the company name in the email field. Check the prompt." |

### The key teaching moment:
> "Watch what I do here — I'm not fixing code. I'm describing the problem in plain English and letting Claude Code figure it out."

---

## Tips for Live Demo

### Keep prompts short
**Not:** "Can you please modify the invoices.html template to include a new column..."
**Instead:** "Add a 'Set Reminder' button to each invoice row. Hit POST /api/calendar/remind."

### Use /plan before big changes
Shows the audience Claude Code's intent before execution.

### Narrate while Claude works
- "It's reading the Sheets service..."
- "Now it's creating the Calendar integration..."
- "It found the bug — the scope was missing..."

### When Claude gets something wrong
Best teaching moment:
> "Not quite — the reminder should use the due_date field, not created_at. Fix that."

---

## Useful Claude Code Commands

| Command | What It Does |
|---------|-------------|
| `/plan` | Shows plan before executing |
| `/help` | Available commands |
| `Ctrl+C` | Cancel current operation |
| `Escape` | Clear input |
