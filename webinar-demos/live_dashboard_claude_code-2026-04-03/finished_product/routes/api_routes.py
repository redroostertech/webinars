from flask import Blueprint
from flask_login import login_required


def create_api_blueprint(api_controller):
    bp = Blueprint("api", __name__, url_prefix="/api")

    @bp.route("/data", methods=["GET"])
    @login_required
    def get_data():
        return api_controller.get_data()

    @bp.route("/sync", methods=["POST"])
    @login_required
    def sync_data():
        return api_controller.sync_data()

    @bp.route("/leads/<int:index>", methods=["PUT"])
    @login_required
    def update_lead(index):
        return api_controller.update_lead(index)

    @bp.route("/invoices/<int:index>", methods=["PUT"])
    @login_required
    def update_invoice(index):
        return api_controller.update_invoice(index)

    @bp.route("/projects/<int:index>", methods=["PUT"])
    @login_required
    def update_project(index):
        return api_controller.update_project(index)

    return bp
