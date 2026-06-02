import os
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

from app.models.user import db, User
from app.auth import auth_bp
from .students import students_bp
from .internships import internships_bp
from .documents import documents_bp
from .reports import reports_bp
from .surveys import surveys_bp
from .diary import diary_bp
from .card import card_bp
from .program_schedule import program_schedule_bp
from .learning_outcomes import learning_outcomes_bp
from app.api.errors import register_error_handlers

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/praktyki"
    )

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(internships_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(surveys_bp)
    app.register_blueprint(learning_outcomes_bp)
    app.register_blueprint(card_bp)
    app.register_blueprint(program_schedule_bp)

    register_error_handlers(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    return app
