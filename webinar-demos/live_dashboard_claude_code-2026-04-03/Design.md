# Design Document

## Design Philosophy
This is a personal business dashboard for entrepreneurs who run multiple businesses. Every design decision optimizes for:
1. **Actionability** — Don't just show data. Let the user email a lead, schedule a reminder, or check a project's health in one click.
2. **Clarity** — A non-technical person should understand what they're looking at in under 5 seconds.
3. **Connection** — Data objects (leads, invoices, projects) are visually linked so the user sees how their business fits together.

---

## Pages

### 1. Login Page (`/login`)
**Purpose:** Gate access to the dashboard.

**Layout:**
- Centered card on a neutral background
- App title: "Business Command Center"
- Username field, password field, "Sign In" button
- Error message area below the form

**Claude Code prompt:**
> "Add a login page to the Flask app. Use Flask-Login with a hardcoded user for demo purposes. Username: admin, password: demo123. Redirect to /dashboard after successful login."

---

### 2. Main Dashboard (`/dashboard`)
**Purpose:** High-level snapshot across all business activity.

**Layout:**
- **Top bar:** App title, nav links (Dashboard, Leads, Invoices, Projects), user + logout
- **Summary cards row:**
  - Total Leads (with stage breakdown)
  - Outstanding Invoices (total $ unpaid)
  - Active Projects (count)
  - Revenue This Month (sum of paid invoices)
- **Recent Activity feed:** Last 10 items added/updated across all objects
- **Revenue Chart:** Bar or line chart showing invoices paid over time (Chart.js)
- **Quick Actions:** "Sync Drive" button, "Send Overdue Reminders" button

**Claude Code prompt:**
> "Create the main dashboard page. Read all data from Google Sheets via the data service. Show 4 summary metric cards (total leads, outstanding invoices, active projects, monthly revenue). Add a recent activity feed and a Chart.js bar chart showing paid invoices over time. Include a 'Sync Drive' button that hits POST /api/sync."

---

### 3. Leads Page (`/leads`)
**Purpose:** View and manage all leads across businesses.

**Layout:**
- **Metric cards:** Total leads, new this week, contacted, converted
- **Leads table:** Name, email, company, source, stage, created date
  - Row click expands to show linked projects and invoices
  - "Email" button on each row (opens compose modal if email exists)
  - Stage shown as colored badge (new=blue, contacted=amber, converted=green)
- **Filters:** By stage, by company, by date range

**Claude Code prompt:**
> "Create the leads page at /leads. Read leads from the Sheets data service. Show metric cards for lead stages, a filterable data table, and an 'Email' button per row that opens a compose modal pre-filled with the lead's email address."

---

### 4. Invoices Page (`/invoices`)
**Purpose:** Track all invoices, see what's paid/unpaid/overdue.

**Layout:**
- **Metric cards:** Total invoiced, total paid, total outstanding, overdue count
- **Invoice table:** Invoice #, client, amount, due date, status, linked project
  - Status as colored badge (draft=gray, sent=blue, paid=green, overdue=red)
  - "Send Invoice" button (emails the invoice via Gmail)
  - "Set Reminder" button (creates a Calendar event for the due date)
- **Overdue section:** Highlighted list of overdue invoices with one-click "Send Reminder" action

**Claude Code prompt:**
> "Create the invoices page at /invoices. Show metric cards for invoice totals and statuses. Build a data table with status badges, a 'Send Invoice' button that calls /api/email/send, and a 'Set Reminder' button that calls /api/calendar/remind with the due date."

---

### 5. Projects Page (`/projects`)
**Purpose:** See all projects with their linked leads, invoices, and financial health.

**Layout:**
- **Metric cards:** Active projects, total budget, total billed, budget utilization %
- **Project cards** (not a table — cards work better for projects):
  - Project name, client, status badge
  - Budget bar: visual progress bar showing billed vs. budget
  - Linked leads count, linked invoices count
  - Deadline with days remaining
  - Click to expand: shows associated leads and invoices inline

**Claude Code prompt:**
> "Create the projects page at /projects. Use card layout instead of a table. Each card shows project name, client, status, a budget progress bar (total_billed / budget), linked lead and invoice counts, and deadline. Cards expand on click to show linked data."

---

### 6. Email Compose (`/email/compose` or modal)
**Purpose:** Send an email to a lead or invoice contact directly from the dashboard.

**Layout:**
- To: (pre-filled from lead/invoice email)
- Subject: (pre-filled based on context — e.g., "Invoice INV-0042" or "Following up")
- Body: textarea
- "Send" button → calls Gmail API
- Success/error confirmation

**Claude Code prompt:**
> "Add an email compose modal that can be triggered from the leads or invoices page. Pre-fill the 'to' field from the record's email. Pre-fill the subject based on context. POST to /api/email/send with to, subject, body. Show success/error feedback."

---

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#f5f5f5` | Page background |
| Card | `#ffffff` | All cards and containers |
| Primary | `#2563eb` | Buttons, links, active nav |
| Success | `#16a34a` | Paid, converted, active |
| Warning | `#d97706` | Contacted, sent, approaching deadline |
| Danger | `#dc2626` | Overdue, errors |
| Neutral | `#6b7280` | Secondary text, draft status |
| Text | `#1f2937` | Primary text |

## Status Badge Colors

| Object | Status | Color |
|--------|--------|-------|
| Lead | new | Blue |
| Lead | contacted | Amber |
| Lead | converted | Green |
| Invoice | draft | Gray |
| Invoice | sent | Blue |
| Invoice | paid | Green |
| Invoice | overdue | Red |
| Project | active | Green |
| Project | completed | Blue |
| Project | on_hold | Amber |

---

## Component Design

### Metric Cards
```
┌─────────────────────┐
│  Outstanding         │
│  $12,400             │
│  3 invoices unpaid   │
└─────────────────────┘
```

### Budget Progress Bar
```
┌─────────────────────────────────┐
│ ████████████░░░░░░░░  $4,500 / $15,000 (30%)
└─────────────────────────────────┘
```
- Green when under 75% utilized
- Amber at 75-90%
- Red above 90%

### Activity Feed Item
```
┌─────────────────────────────────────────────┐
│ 🔵 New lead: Jane Smith (Acme Corp)     2h ago │
│ 🟢 Invoice INV-0042 marked as paid     5h ago │
│ 🟠 Project "Rebrand" deadline in 3 days       │
└─────────────────────────────────────────────┘
```

### Charts
- Chart.js (CDN — no build step)
- Revenue over time: bar chart, monthly grouping
- Lead pipeline: horizontal bar chart by stage
- Always labeled axes

---

## Responsive Behavior
- Desktop/laptop optimized (demo context)
- Metric cards and project cards stack vertically below 768px
- Tables scroll horizontally on small screens
- Email compose modal is centered overlay

---

## Interaction with Claude Code
Every prompt follows the **Golden Formula:**

> **Context** + **Goal** + **Constraints**

Example:
> "I'm on the /invoices page [context]. I need a 'Set Reminder' button on each overdue invoice that creates a Google Calendar event for the due date [goal]. Use the existing calendar service and don't change the table layout [constraints]."
