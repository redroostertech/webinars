"""Extract text from PDF/DOCX files and parse invoice data via OpenAI."""

import json
import os
import logging

import fitz  # PyMuPDF
from docx import Document

import config

logger = logging.getLogger(__name__)


def extract_text(file_path):
    """Extract raw text from a PDF or DOCX file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def _extract_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


class DocumentService:
    """Process uploaded invoice documents through OpenAI extraction."""

    def __init__(self, openai_service, data_service):
        self._openai = openai_service
        self._data = data_service

    def process_invoice_file(self, file_path):
        """Extract invoice data from a file and match against projects/leads.

        Returns the extracted invoice dict and any cross-reference matches.
        """
        # Step 1: Extract text from the document
        text = extract_text(file_path)
        if not text.strip():
            return {"status": "error", "message": "Could not extract text from file"}

        # Step 2: Get existing projects and leads for context
        projects = self._data.get_projects()
        leads = self._data.get_leads()

        project_names = [
            {"name": p.name, "client": p.client} for p in projects
        ]
        lead_names = [
            {"name": l.name, "company": l.company, "email": l.email}
            for l in leads
        ]

        # Step 3: Send to OpenAI for extraction + matching
        result = self._extract_and_match(text, project_names, lead_names)
        return result

    def process_invoice_text(self, text):
        """Same as process_invoice_file but accepts raw text (for uploads)."""
        if not text.strip():
            return {"status": "error", "message": "No text provided"}

        projects = self._data.get_projects()
        leads = self._data.get_leads()

        project_names = [
            {"name": p.name, "client": p.client} for p in projects
        ]
        lead_names = [
            {"name": l.name, "company": l.company, "email": l.email}
            for l in leads
        ]

        return self._extract_and_match(text, project_names, lead_names)

    def _extract_and_match(self, document_text, projects, leads):
        """Use OpenAI to extract invoice fields and match to projects/leads."""
        prompt = (
            "You are an invoice data extraction assistant. "
            "Extract structured invoice data from the following document text, "
            "then match it against the known projects and leads.\n\n"
            "DOCUMENT TEXT:\n"
            f"---\n{document_text[:4000]}\n---\n\n"
            "INVOICE SCHEMA TO EXTRACT:\n"
            "- invoice_number (string): the invoice ID/number\n"
            "- client (string): who the invoice is for\n"
            "- amount (number): total amount in dollars\n"
            "- due_date (string): payment due date in YYYY-MM-DD format\n"
            "- status (string): one of draft, sent, paid, overdue — "
            "  infer from context, default to 'sent'\n"
            "- email (string): billing contact email if found, otherwise empty\n\n"
            "KNOWN PROJECTS (match by client name, fuzzy):\n"
            f"{json.dumps(projects)}\n\n"
            "KNOWN LEADS (match by company name, fuzzy):\n"
            f"{json.dumps(leads)}\n\n"
            "Return a JSON object with:\n"
            "- 'invoice': the extracted invoice matching the schema\n"
            "- 'matched_project': name of the matched project or null\n"
            "- 'matched_leads': array of matched lead names or empty array\n"
            "- 'confidence': 'high', 'medium', or 'low' based on how clearly "
            "  the document contained invoice data\n"
            "- 'metadata': object containing any additional info found in the "
            "  document that doesn't fit the schema — line items, tax info, "
            "  payment terms, addresses, notes, PO numbers, etc. "
            "  Bundle everything extra here as key-value pairs."
        )

        response = self._openai._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        result["status"] = "success"
        return result
