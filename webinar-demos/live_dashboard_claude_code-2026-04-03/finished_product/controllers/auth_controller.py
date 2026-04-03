from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user


class AuthController:
    """Handles HTTP concerns for auth. Delegates logic to AuthService."""

    def __init__(self, auth_service):
        self._auth = auth_service

    def login_page(self):
        return render_template("login.html")

    def login_submit(self):
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = self._auth.login(username, password)
        if user is None:
            flash("Invalid username or password.", "error")
            return render_template("login.html"), 401

        login_user(user)
        return redirect(url_for("dashboard.dashboard_page"))

    def logout(self):
        logout_user()
        return redirect(url_for("auth.login_page"))
