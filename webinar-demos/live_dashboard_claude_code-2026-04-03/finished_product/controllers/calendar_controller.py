from flask import request, jsonify


class CalendarController:
    """Handles HTTP concerns for calendar event creation."""

    def __init__(self, calendar_service):
        self._calendar = calendar_service

    def create_reminder(self):
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON body"}), 400

        title = data.get("title", "").strip()
        date = data.get("date", "").strip()
        description = data.get("description", "")

        if not title or not date:
            return jsonify({
                "status": "error",
                "message": "Both 'title' and 'date' are required.",
            }), 400

        try:
            event_link = self._calendar.create_reminder(title, date, description)
            return jsonify({
                "status": "success",
                "message": f"Reminder created for {date}",
                "event_link": event_link,
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to create reminder: {str(e)}",
            }), 500
