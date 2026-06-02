from flask import Blueprint, render_template
from flask_login import login_required
from app.auth.decorators import role_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/internship")
@login_required
@role_required("student")
def internship():
    return render_template("student/internship.html")


@student_bp.route("/diary")
@login_required
@role_required("student")
def diary():
    return render_template("student/diary.html")


@student_bp.route("/report")
@login_required
@role_required("student")
def report():
    return render_template("student/report.html")


@student_bp.route("/documents")
@login_required
@role_required("student")
def documents():
    return render_template("student/documents.html")


@student_bp.route("/survey")
@login_required
@role_required("student")
def survey():
    return render_template("student/survey.html")


@student_bp.route("/program")
@login_required
@role_required("student")
def program():
    return render_template("student/program.html")
