from flask import Blueprint


def create_auth_blueprint(auth_controller):
    bp = Blueprint("auth", __name__)

    @bp.route("/login", methods=["GET"])
    def login_page():
        return auth_controller.login_page()

    @bp.route("/login", methods=["POST"])
    def login_submit():
        return auth_controller.login_submit()

    @bp.route("/logout")
    def logout():
        return auth_controller.logout()

    return bp
