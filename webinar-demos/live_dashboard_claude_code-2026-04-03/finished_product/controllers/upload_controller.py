"""Handle file uploads for invoice processing."""

import os
import tempfile

from flask import jsonify, request

import config


class UploadController:

    def __init__(self, document_service, data_service):
        self._doc = document_service
        self._data = data_service

    def upload_invoice(self):
        """Accept a file upload, extract invoice data, and return the result."""
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"status": "error", "message": "Empty filename"}), 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".pdf", ".docx", ".doc", ".txt"):
            return jsonify({
                "status": "error",
                "message": f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT."
            }), 400

        # Save to temp file, process, then clean up
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        try:
            file.save(tmp.name)
            tmp.close()
            result = self._doc.process_invoice_file(tmp.name)
        finally:
            os.unlink(tmp.name)

        return jsonify(result)

    def confirm_invoice(self):
        """Save a confirmed extracted invoice to the data store."""
        data = request.get_json()
        if not data or "invoice" not in data:
            return jsonify({"status": "error", "message": "No invoice data"}), 400

        invoice = data["invoice"]
        # Add metadata if present
        if "metadata" in data:
            invoice["_metadata"] = data["metadata"]

        # Read existing invoices, append, write back
        invoices = self._data.get_invoices()
        existing = [inv.to_dict() for inv in invoices]
        existing.append(invoice)

        # Write to sample JSON or Sheets
        result = self._data.save_invoices(existing)
        return jsonify(result)
