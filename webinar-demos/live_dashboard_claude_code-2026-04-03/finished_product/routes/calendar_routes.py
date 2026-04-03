from flask import Blueprint
from flask_login import login_required


def create_calendar_blueprint(calendar_controller):
    bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")

    @bp.route("/remind", methods=["POST"])
    @login_required
    def create_reminder():
        return calendar_controller.create_reminder()

    return bp
