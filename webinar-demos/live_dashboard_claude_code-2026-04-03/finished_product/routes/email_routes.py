from flask import Blueprint
from flask_login import login_required


def create_email_blueprint(email_controller):
    bp = Blueprint("email", __name__, url_prefix="/api/email")

    @bp.route("/send", methods=["POST"])
    @login_required
    def send_email():
        return email_controller.send_email()

    return bp
