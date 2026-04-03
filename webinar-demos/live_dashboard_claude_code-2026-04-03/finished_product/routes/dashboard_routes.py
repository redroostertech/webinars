from flask import Blueprint
from flask_login import login_required


def create_dashboard_blueprint(dashboard_controller):
    bp = Blueprint("dashboard", __name__)

    @bp.route("/dashboard")
    @login_required
    def dashboard_page():
        return dashboard_controller.dashboard_page()

    @bp.route("/leads")
    @login_required
    def leads_page():
        return dashboard_controller.leads_page()

    @bp.route("/invoices")
    @login_required
    def invoices_page():
        return dashboard_controller.invoices_page()

    @bp.route("/projects")
    @login_required
    def projects_page():
        return dashboard_controller.projects_page()

    return bp
