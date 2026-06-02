from flask import Blueprint, render_template
from flask_login import login_required
from app.auth.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/students")
@login_required
@role_required("sekretariat", "administrator")
def students():
    return render_template("admin/students.html")


@admin_bp.route("/internships")
@login_required
@role_required("sekretariat", "administrator")
def internships():
    return render_template("admin/internships.html")


@admin_bp.route("/pending")
@login_required
@role_required("administrator")
def pending():
    return render_template("admin/pending.html")
