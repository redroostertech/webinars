# Prompts By Phase

Copy-paste these prompts into Claude Code at each phase of the webinar. They follow the Golden Formula: Context + Goal + Constraints.

---

## Phase 1: Project Scaffold

### Prompt 1.1 — Initialize the project
```
Create a new Flask project following the structure in CLAUDE.md. Set up the app factory pattern in app.py with Flask-Login. Create the route → controller → service → repository directory structure with __init__.py files. Add a config.py that reads from .env using python-dotenv. Add a hardcoded demo user (admin/demo123). Create requirements.txt with Flask, Flask-Login, google-auth, google-auth-oauthlib, google-api-python-client, openai, and python-dotenv.
```

### Prompt 1.2 — Auth + login page
```
Create the login page at /login. Use Flask-Login with session-based auth. The login form should have username and password fields. On successful login, redirect to /dashboard. On failure, show "Invalid username or password" as a flash message. Protect all routes except /login with @login_required. Create a base.html template with a top nav bar showing the app name, nav links, and a logout button.
```

---

## Phase 2: Google Sheets Service

### Prompt 2.1 — Sheets service
```
Create services/sheets_service.py. It should authenticate with Google using credentials.json in the project root and the OAuth scopes from CLAUDE.md. Implement these methods: read_tab(tab_name) that reads all rows from a tab in the master spreadsheet, and write_tab(tab_name, rows) that writes rows to a tab. Get the master spreadsheet ID from config. Handle token refresh automatically and the first-run browser auth flow.
```

### Prompt 2.2 — Drive service
```
Create services/drive_service.py. It should use the Google Drive API to scan three folders (IDs from .env: DRIVE_LEADS_FOLDER, DRIVE_INVOICES_FOLDER, DRIVE_PROJECTS_FOLDER). List all Google Spreadsheets in each folder. Compare modification times against a last_synced timestamp stored in data/sync_state.json. Return a list of new or updated files with their IDs, names, and which folder they came from.
```

---

## Phase 3: ETL Pipeline

### Prompt 3.1 — OpenAI normalization service
```
Create services/openai_service.py with two methods. First: normalize(headers, rows, object_type) — sends raw spreadsheet data to OpenAI gpt-4o-mini with the canonical schema for the given object type (lead, invoice, or project — schemas are in CLAUDE.md) and returns clean structured JSON using JSON response format. Second: reconcile(new_data, existing_leads, existing_invoices, existing_projects) — cross-references new records against existing data using fuzzy company name matching and returns a list of updates to apply. Use the cross-reference rules from CLAUDE.md.
```

### Prompt 3.2 — ETL orchestration
```
Create services/etl_service.py that orchestrates the full pipeline. It should: 1) Use drive_service to scan for new files, 2) Use sheets_service to read each new spreadsheet's content, 3) Use openai_service to normalize each file based on which folder it came from, 4) Use openai_service to reconcile new records across all three object types, 5) Use sheets_service to write everything back to the master sheet. Also create scripts/full_pipeline.py as a standalone CLI entry point that runs the full pipeline and prints results.
```

### Prompt 3.3 — Wire up the sync endpoint
```
Create an API endpoint at POST /api/sync that triggers the full ETL pipeline. Follow the route → controller → service pattern. The controller should call etl_service.run_full_pipeline() and return JSON with status, counts of records added/updated, and any errors. Add a "Sync Drive" button to the dashboard that calls this endpoint and shows the result.
```

---

## Phase 4: Dashboard Pages

### Prompt 4.1 — Main dashboard
```
Build the /dashboard page. Read all data from the Sheets service via data_service. Show 4 summary metric cards at the top: total leads, outstanding invoice amount (sum of unpaid), active projects count, and total revenue this month (sum of paid invoices). Below that, add a Chart.js bar chart showing paid invoices over time grouped by month. Below the chart, add a recent activity feed showing the last 10 records added or updated across all three objects. Add a "Sync Drive" button in the page header that calls POST /api/sync. Use the color palette from Design.md.
```

### Prompt 4.2 — Leads page
```
Build the /leads page. Show metric cards for: total leads, new this week, contacted, and converted. Below that, a data table with columns: name, email, company, source, stage, and created_at. Show stage as a colored badge (new=blue, contacted=amber, converted=green). Add an "Email" button on each row that has an email address — clicking it should open an email compose modal pre-filled with the lead's email. Make the table filterable by stage using buttons above the table.
```

### Prompt 4.3 — Invoices page
```
Build the /invoices page. Show metric cards for: total invoiced, total paid, total outstanding, and overdue count. Below that, a data table with columns: invoice_number, client, amount (formatted as currency), due_date, and status. Status should be a colored badge (draft=gray, sent=blue, paid=green, overdue=red). Add a "Send Invoice" button per row that opens the email compose modal pre-filled with the invoice details. Add a "Set Reminder" button per row that calls POST /api/calendar/remind with the invoice due date and details.
```

### Prompt 4.4 — Projects page
```
Build the /projects page. Use a card layout instead of a table. Each card shows: project name, client, status badge (active=green, completed=blue, on_hold=amber), a budget progress bar showing total_billed / budget as a percentage (green under 75%, amber 75-90%, red above 90%), linked leads count, linked invoices count, and deadline with days remaining. Cards should expand on click to show the associated leads and invoices inline.
```

---

## Phase 5: Gmail Integration

### Prompt 5.1 — Gmail service
```
Create services/gmail_service.py with a send_email(to, subject, body) method that sends an email using the Gmail API. Use the same OAuth credentials as the other Google services. The scope should be gmail.send (send-only — no inbox read access). Build the email using Python's email.mime.text module and base64 encode it for the API.
```

### Prompt 5.2 — Email route + controller
```
Create routes/email_routes.py and controllers/email_controller.py. Add a POST /api/email/send endpoint that accepts {to, subject, body} in the request JSON, calls gmail_service.send_email(), and returns {status: "sent", message_id: "..."} on success or {status: "error", message: "..."} on failure. Register the blueprint in app.py.
```

### Prompt 5.3 — Email compose modal
```
Add an email compose modal to base.html that can be triggered from any page. It should have fields for To (pre-filled), Subject (pre-filled based on context), and Body (textarea). A "Send" button that POSTs to /api/email/send via fetch. Show a success or error toast after sending. Add JavaScript that opens the modal when any "Email" or "Send Invoice" button is clicked, passing the recipient email and context into the modal fields.
```

---

## Phase 6: Calendar Integration

### Prompt 6.1 — Calendar service
```
Create services/calendar_service.py with a create_reminder(title, date, description) method. It should create an all-day Google Calendar event on the specified date using the Calendar API v3. Set reminders to 24 hours before (1440 minutes) with both popup and email notification methods. Return the event ID and the htmlLink so the user can click through to the event.
```

### Prompt 6.2 — Calendar route + controller
```
Create routes/calendar_routes.py and controllers/calendar_controller.py. Add a POST /api/calendar/remind endpoint that accepts {title, date, description} and calls calendar_service.create_reminder(). Return {status: "created", event_link: "https://..."} on success. Register the blueprint in app.py. Wire up the "Set Reminder" buttons on the invoices page to call this endpoint with the invoice due date, number, client, and amount pre-filled.
```

---

## Debugging Prompts (for when things break live)

### Auth issues
```
The fetch_sheets.py script is returning a 401 error. The token.json file exists but might be expired. Can you add logic to detect an expired token and re-trigger the auth flow automatically?
```

### Data not showing
```
The /leads page loads but the table is empty. The master Google Sheet has data in the Leads tab. Check the flow: sheets_service → data_service → dashboard_controller → template. Something is breaking between reading the data and rendering it.
```

### Cross-reference not working
```
I uploaded an invoice for "Acme Corporation" but the matching lead "Acme Corp" wasn't updated to "converted". Check the reconciliation logic in openai_service.reconcile(). The fuzzy matching might not be working correctly.
```

### Gmail 403
```
When I click "Send Email" on a lead, I get a 403 Forbidden error in the terminal. The Gmail API is enabled in my Google Cloud Console. I think the OAuth token might be missing the gmail.send scope. Can you check the scopes and re-auth if needed?
```

### OpenAI bad output
```
The normalization step is putting the company name in the email field and the email in the company field. The raw data headers are "Business Name" and "Email Address". Check the normalization prompt in openai_service.normalize() — the schema description might need to be more explicit about which field maps where.
```

---

## Iteration Prompts (for after the core build)

### Add dark mode
```
Add a dark mode toggle to the top nav bar. When clicked, switch the dashboard to a dark theme. Save the preference in localStorage so it persists across page loads.
```

### Add CSV export
```
Add an "Export CSV" button to each data page (leads, invoices, projects) that downloads the current table data as a .csv file. Use JavaScript to generate the CSV from the table DOM — no server-side endpoint needed.
```

### Add search
```
Add a global search bar to the top nav. When the user types, filter all visible data (leads, invoices, or projects depending on current page) by matching against any field. Show results in real time as they type.
```
