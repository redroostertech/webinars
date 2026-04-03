from flask import Blueprint
from flask_login import login_required


def create_dashboard_blueprint(dashboard_controller):
    bp = Blueprint("dashboard", __name__)

    @bp.route("/dashboard")
    @login_required
    def dashboard_page():
        return dashboard_controller.dashboard_page()

    @bp.route("/reddit")
    @login_required
    def reddit_page():
        return dashboard_controller.reddit_page()

    @bp.route("/summary")
    @login_required
    def summary_page():
        return dashboard_controller.summary_page()

    return bp
