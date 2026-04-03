from flask import Blueprint
from flask_login import login_required


def create_upload_blueprint(upload_controller):
    bp = Blueprint("upload", __name__, url_prefix="/api")

    @bp.route("/invoices/upload", methods=["POST"])
    @login_required
    def upload_invoice():
        return upload_controller.upload_invoice()

    @bp.route("/invoices/confirm", methods=["POST"])
    @login_required
    def confirm_invoice():
        return upload_controller.confirm_invoice()

    return bp
