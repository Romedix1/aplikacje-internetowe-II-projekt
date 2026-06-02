import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

from app.models.user import db, User
from app.auth import auth_bp
from app.api import (
    students_bp,
    internships_bp,
    documents_bp,
    diary_bp,
    reports_bp,
    surveys_bp,
    learning_outcomes_bp,
    card_bp,
    program_schedule_bp,
)
from app.api.errors import register_error_handlers
from app.student import student_bp
from app.admin import admin_bp
from app.staff import staff_bp

load_dotenv()


def init_profile_check(app):
    @app.before_request
    def check_profile_completion():
        if not current_user.is_authenticated or current_user.role != "student":
            return

        if request.endpoint in ["dashboard", "auth.logout", "static", "index"]:
            return

        if request.endpoint and (
            request.endpoint.startswith("students.")
            or request.endpoint.startswith("api.")
        ):
            return

        if not (
            current_user.study_field
            and current_user.study_year
            and current_user.study_form
            and current_user.semester
        ):

            return redirect(url_for("dashboard"))


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/praktyki"
    )

    db.init_app(app)

    init_profile_check(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "index"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(internships_bp, url_prefix="/api/internships")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(diary_bp, url_prefix="/api/diary")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(surveys_bp, url_prefix="/api/surveys")
    app.register_blueprint(learning_outcomes_bp, url_prefix="/api/learning_outcomes")
    app.register_blueprint(card_bp, url_prefix="/api/card")
    app.register_blueprint(program_schedule_bp, url_prefix="/api/program_schedule")

    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)

    register_error_handlers(app)

    @app.route("/")
    def index():
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    return app
