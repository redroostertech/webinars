from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from repositories.user_repository import UserRepository
from repositories.data_repository import DataRepository
from services.auth_service import AuthService
from services.data_service import DataService
from services.sheets_service import SheetsService
from services.reddit_service import RedditService
from services.etl_service import ETLService
from controllers.auth_controller import AuthController
from controllers.dashboard_controller import DashboardController
from controllers.api_controller import APIController
from routes.auth_routes import create_auth_blueprint
from routes.dashboard_routes import create_dashboard_blueprint
from routes.api_routes import create_api_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Repository layer ---
    user_repo = UserRepository(Config.DEMO_USERNAME, Config.DEMO_PASSWORD)
    data_repo = DataRepository(Config.DATA_DIR)

    # --- Service layer ---
    auth_service = AuthService(user_repo)
    data_service = DataService(data_repo)
    sheets_service = SheetsService(Config.CREDENTIALS_PATH, Config.TOKEN_PATH)
    reddit_service = RedditService(Config.APIFY_TOKEN)
    etl_service = ETLService(sheets_service, reddit_service, data_repo, Config)

    # --- Controller layer ---
    auth_ctrl = AuthController(auth_service)
    dashboard_ctrl = DashboardController(data_service)
    api_ctrl = APIController(data_service, etl_service)

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

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard_page"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=3456)
