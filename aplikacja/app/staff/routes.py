from flask import Blueprint, render_template
from flask_login import login_required
from app.auth.decorators import role_required

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/students")
@login_required
@role_required("uopz", "zopz")
def students():
    return render_template("staff/students.html")


@staff_bp.route("/internships")
@login_required
@role_required("uopz", "zopz")
def internships():
    return render_template("staff/internships.html")
