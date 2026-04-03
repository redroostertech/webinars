import sys

from flask import Flask, redirect, url_for
from flask_login import LoginManager

import config
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.sheets_service import SheetsService
from services.drive_service import DriveService
from services.openai_service import OpenAIService
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.etl_service import ETLService
from services.data_service import DataService
from controllers.auth_controller import AuthController
from controllers.dashboard_controller import DashboardController
from controllers.api_controller import APIController
from controllers.email_controller import EmailController
from controllers.calendar_controller import CalendarController
from controllers.upload_controller import UploadController
from services.document_service import DocumentService
from routes.auth_routes import create_auth_blueprint
from routes.dashboard_routes import create_dashboard_blueprint
from routes.api_routes import create_api_blueprint
from routes.email_routes import create_email_blueprint
from routes.calendar_routes import create_calendar_blueprint
from routes.upload_routes import create_upload_blueprint


def create_app():
    app = Flask(__name__)
    app.secret_key = config.FLASK_SECRET_KEY

    # --- Repository layer ---
    user_repo = UserRepository(config.DEMO_USERNAME, config.DEMO_PASSWORD)

    # --- Service layer ---
    auth_service = AuthService(user_repo)
    sheets_service = SheetsService()
    drive_service = DriveService()
    openai_service = OpenAIService()
    gmail_service = GmailService()
    calendar_service = CalendarService()
    etl_service = ETLService(drive_service, sheets_service, openai_service)
    data_service = DataService(sheets_service)

    # --- Controller layer ---
    auth_ctrl = AuthController(auth_service)
    dashboard_ctrl = DashboardController(data_service)
    api_ctrl = APIController(data_service, etl_service)
    email_ctrl = EmailController(gmail_service)
    calendar_ctrl = CalendarController(calendar_service)
    document_service = DocumentService(openai_service, data_service)
    upload_ctrl = UploadController(document_service, data_service)

    # --- Flask-Login setup ---
    login_manager = LoginManager()
    login_manager.login_view = "auth.login_page"
    login_manager.login_message = "Please log in to access the dashboard."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return auth_service.load_user(user_id)

    # --- Route layer ---
    app.register_blueprint(create_auth_blueprint(auth_ctrl))
    app.register_blueprint(create_dashboard_blueprint(dashboard_ctrl))
    app.register_blueprint(create_api_blueprint(api_ctrl))
    app.register_blueprint(create_email_blueprint(email_ctrl))
    app.register_blueprint(create_calendar_blueprint(calendar_ctrl))
    app.register_blueprint(create_upload_blueprint(upload_ctrl))

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard_page"))

    # --- File watcher (if enabled) ---
    watch_enabled = config.WATCH_ENABLED or "--watch" in sys.argv
    if watch_enabled and config.DRIVE_SYNC_PATH:
        from services.watcher_service import start_watcher

        def _sync_callback():
            with app.app_context():
                etl_service.run_full_pipeline()

        start_watcher(config.DRIVE_SYNC_PATH, _sync_callback)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=config.PORT)
