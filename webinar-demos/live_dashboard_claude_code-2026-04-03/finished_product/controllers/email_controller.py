from flask import request, jsonify


class EmailController:
    """Handles HTTP concerns for email sending."""

    def __init__(self, gmail_service):
        self._gmail = gmail_service

    def send_email(self):
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON body"}), 400

        to = data.get("to", "").strip()
        subject = data.get("subject", "").strip()
        body = data.get("body", "").strip()

        if not to or not subject:
            return jsonify({
                "status": "error",
                "message": "Both 'to' and 'subject' are required.",
            }), 400

        try:
            message_id = self._gmail.send_email(to, subject, body)
            return jsonify({
                "status": "success",
                "message": f"Email sent to {to}",
                "message_id": message_id,
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
            }), 500
