from flask import Blueprint
from flask_login import login_required


def create_api_blueprint(api_controller):
    bp = Blueprint("api", __name__, url_prefix="/api")

    @bp.route("/data", methods=["GET"])
    @login_required
    def get_data():
        return api_controller.get_data()

    @bp.route("/refresh", methods=["POST"])
    @login_required
    def refresh_data():
        return api_controller.refresh_data()

    return bp
