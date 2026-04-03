"""Normalize raw spreadsheet data and cross-reference across business objects."""

import json

from openai import OpenAI

import config

LEAD_SCHEMA = {
    "name": "string",
    "email": "string",
    "company": "string",
    "source": "string",
    "stage": "new | contacted | converted",
    "project": "string (linked project name, empty if none)",
    "created_at": "YYYY-MM-DD",
}

INVOICE_SCHEMA = {
    "invoice_number": "string",
    "client": "string",
    "amount": "number",
    "due_date": "YYYY-MM-DD",
    "status": "draft | sent | paid | overdue",
    "email": "string",
}

PROJECT_SCHEMA = {
    "name": "string",
    "client": "string",
    "budget": "number",
    "total_billed": "number",
    "deadline": "YYYY-MM-DD",
    "status": "active | completed | on_hold",
}

SCHEMAS = {
    "leads": LEAD_SCHEMA,
    "invoices": INVOICE_SCHEMA,
    "projects": PROJECT_SCHEMA,
}


class OpenAIService:

    def __init__(self):
        self._client = OpenAI(api_key=config.OPENAI_API_KEY)

    def normalize(self, headers, rows, object_type):
        """Send raw spreadsheet data to GPT-4o-mini and get back canonical rows."""
        schema = SCHEMAS.get(object_type)
        if not schema:
            raise ValueError(f"Unknown object type: {object_type}")

        raw_data = []
        for row in rows:
            record = {}
            for i, header in enumerate(headers):
                record[header] = row[i] if i < len(row) else ""
            raw_data.append(record)

        if not raw_data:
            return []

        prompt = (
            f"You are a data normalization assistant. "
            f"Convert the following raw records into the canonical schema.\n\n"
            f"Target schema for '{object_type}':\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"Raw data:\n{json.dumps(raw_data, indent=2)}\n\n"
            f"Return a JSON object with a single key 'records' containing an array "
            f"of normalized objects matching the schema exactly. "
            f"Use best judgment to map fields. Fill missing fields with empty string "
            f"or 0 for numbers. Dates should be YYYY-MM-DD format."
        )

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("records", [])

    def reconcile(self, new_data, existing_leads, existing_invoices, existing_projects):
        """Cross-reference new data against existing records using fuzzy matching.

        Returns updated versions of all three lists with cross-references applied.
        """
        prompt = (
            "You are a data reconciliation assistant. "
            "Apply these cross-reference rules:\n"
            "- New invoice -> find matching lead by client/company name -> "
            "  update lead stage to 'converted'\n"
            "- New invoice -> find matching project by client name -> "
            "  add invoice amount to project's total_billed\n"
            "- New lead -> check if project exists for that company -> "
            "  set lead's 'project' field to the project name\n"
            "- New project -> check for existing leads by company -> "
            "  set each matching lead's 'project' field to the project name\n"
            "- New project -> check for existing invoices by company\n\n"
            "Use fuzzy matching on company names "
            "(e.g. 'Acme Corp' = 'Acme Corporation' = 'acme').\n"
            "Every lead MUST have a 'project' field (empty string if no match).\n\n"
            f"New data being added:\n{json.dumps(new_data, indent=2)}\n\n"
            f"Existing leads:\n{json.dumps(existing_leads, indent=2)}\n\n"
            f"Existing invoices:\n{json.dumps(existing_invoices, indent=2)}\n\n"
            f"Existing projects:\n{json.dumps(existing_projects, indent=2)}\n\n"
            "Return a JSON object with three keys: 'leads', 'invoices', 'projects' "
            "— each containing the full updated array after reconciliation. "
            "Include both existing and new records."
        )

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        return {
            "leads": result.get("leads", existing_leads),
            "invoices": result.get("invoices", existing_invoices),
            "projects": result.get("projects", existing_projects),
        }
