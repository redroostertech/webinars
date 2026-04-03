# Getting Started

Step-by-step setup guide. Follow this in order. If you get stuck, the "What can go wrong" section below each step has you covered.

---

## Prerequisites Checklist

- [ ] **Python 3.10+** — Run `python3 --version` in your terminal
- [ ] **pip** — Run `pip3 --version` (comes with Python)
- [ ] **Claude Code** — Installed and authenticated. Run `claude` in your terminal.
- [ ] **A Google account** — For Drive, Sheets, Gmail, and Calendar access
- [ ] **Google Drive for Desktop** — Installed and syncing (drive.google.com/download)
- [ ] **An OpenAI account** — For the data normalization API (platform.openai.com)

**Don't have Python?** Download from python.org. Mac users on macOS 12.3+ need to install manually.

---

## Step 1: Set Up Google Cloud Credentials

One set of credentials unlocks all four Google APIs (Drive, Sheets, Gmail, Calendar).

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. **Enable these APIs** (APIs & Services > Library):
   - Google Drive API
   - Google Sheets API
   - Gmail API
   - Google Calendar API
4. Go to **APIs & Services > Credentials**
5. Click **+ Create Credentials > OAuth client ID**
6. Set Application type: **Desktop app**
7. Name it (e.g., "Business Dashboard")
8. Click **Create**
9. **Download the JSON immediately** — the client secret is NOT shown again
10. Rename to `credentials.json` and move to the `finished_product/` directory

**Also configure the OAuth consent screen:**
1. APIs & Services > OAuth consent screen
2. Choose **External**
3. Fill in app name and your email
4. Add scopes: `drive.readonly`, `spreadsheets`, `gmail.send`, `calendar.events`
5. Add yourself as a test user

**What can go wrong:**
- "OAuth consent screen not configured" → Complete step above
- Forgot to download JSON → Go back to Credentials, click the download icon
- "Access blocked" on first auth → Add your email as a test user in OAuth consent screen

---

## Step 2: Set Up Google Drive Folders

1. Open Google Drive (drive.google.com)
2. Create a folder called **BusinessHub** (or whatever you prefer)
3. Inside it, create three subfolders:
   - `leads`
   - `invoices`
   - `projects`
4. Get each folder's ID from the URL. When you open a folder, the URL looks like:
   ```
   https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs
   ```
   The long string after `/folders/` is the folder ID.

5. Make sure **Google Drive for Desktop** is installed and syncing these folders locally.

---

## Step 3: Create the Master Google Sheet

1. Create a new Google Spreadsheet called **Business Dashboard Master**
2. Create three tabs (sheets) at the bottom:
   - **Leads** — with headers: `name, email, company, source, stage, created_at`
   - **Invoices** — with headers: `invoice_number, client, amount, due_date, status, email`
   - **Projects** — with headers: `name, client, budget, total_billed, deadline, status`
3. Get the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/edit
   ```
   The string between `/d/` and `/edit` is the ID.

You can add some sample data to each tab or leave them empty — the pipeline will populate them.

---

## Step 4: Get Your OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** (left sidebar)
4. Click **Create new secret key**
5. Copy it immediately — it's shown only once
6. Save it for the next step

**Cost:** We use `gpt-4o-mini`. A full pipeline run costs under $0.01.

---

## Step 5: Create Your .env File

Create a file called `.env` in the `finished_product/` directory:

```
# Google
MASTER_SHEET_ID=your_master_spreadsheet_id
DRIVE_LEADS_FOLDER=your_leads_folder_id
DRIVE_INVOICES_FOLDER=your_invoices_folder_id
DRIVE_PROJECTS_FOLDER=your_projects_folder_id

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Flask
FLASK_SECRET_KEY=any-random-string-here
```

**What can go wrong:**
- Token has extra spaces or quotes → Values should be plain text, no quotes
- Wrong folder ID → Open the folder in Drive, copy the ID from the URL
- Wrong sheet ID → Open the spreadsheet, copy from URL

---

## Step 6: Install Dependencies

```bash
cd finished_product
pip3 install -r requirements.txt
```

**What can go wrong:**
- `pip3: command not found` → Try `python3 -m pip install -r requirements.txt`
- Permission errors → Add `--user` flag

---

## Step 7: First Auth Run

The first time you interact with Google APIs, a browser window will open asking you to authorize the app. This is expected.

```bash
python3 scripts/sync_drive.py
```

1. Browser opens → sign in with your Google account
2. Click "Allow" for each permission
3. A `token.json` file is created in the project
4. Every future run is silent — no browser prompt

**What can go wrong:**
- "Access blocked: app not verified" → Add yourself as a test user in Cloud Console OAuth consent screen
- Browser doesn't open → Copy the URL from the terminal and paste it manually
- Wrong Google account → Sign out of other accounts first, or use an incognito window

---

## Step 8: Test the Pipeline

```bash
# Drop a test spreadsheet into your Drive /leads folder first, then:
python3 scripts/full_pipeline.py
```

You should see output like:
```
Scanning Google Drive...
Found 1 new file in /leads
Normalizing with OpenAI...
Cross-referencing...
Writing to master sheet...
Done. 3 leads added.
```

Check your master Google Sheet — the Leads tab should have data.

---

## Step 9: Start the Dashboard

```bash
./start.sh
```

Opens your browser to **http://localhost:3456**. Login: **admin / demo123**.

---

## Step 10: Iterate with Claude Code

Now you can ask Claude Code to modify anything:

> "Add a 'Send Email' button to each lead row that opens a compose modal"

> "The invoice amounts aren't formatting as currency — fix the Invoices table"

> "Add a chart showing revenue by month from paid invoices"

See `Working_With_Claude_Code.md` for detailed prompting strategies.

---

## Folder Structure After Setup

```
finished_product/
├── .env                    ← API keys and IDs (NEVER share)
├── credentials.json        ← Google OAuth (NEVER share)
├── token.json              ← Auto-generated after first auth
├── start.sh                ← One-command launcher
├── app.py
├── config.py
├── requirements.txt
├── routes/
├── controllers/
├── services/
├── repositories/
├── models/
├── scripts/
├── templates/
├── static/
└── data/
    └── sync_state.json     ← Pipeline state tracking
```
