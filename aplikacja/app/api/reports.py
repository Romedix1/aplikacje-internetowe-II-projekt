from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.user import db
from app.models.report import Report
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from datetime import datetime
from sqlalchemy import text
from flask import send_file
import io
from app.utils.pdf_base import BasePDF

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _report_to_dict(r):
    return {
        "id": r.id,
        "internship_id": r.internship_id,
        "company_description": r.company_description or "",
        "work_description": r.work_description or "",
        "self_assessment": r.self_assessment or "",
        "status": r.status,
        "submitted_at": str(r.submitted_at) if r.submitted_at else None,
    }


@reports_bp.route("/internship/<int:internship_id>", methods=["GET"])
@login_required
def get_report(internship_id):
    report = Report.query.filter_by(internship_id=internship_id).first()
    if not report:
        return jsonify(None), 200
    return jsonify(_report_to_dict(report)), 200


# POST /api/reports
@reports_bp.route("", methods=["POST"])
@login_required
@role_required("student")
def create_report():
    data = request.get_json()
    if not data or not data.get("internship_id"):
        raise ValidationError("Brak danych lub ID praktyki.")

    report = Report(
        internship_id=data["internship_id"],
        company_description=data.get("company_description", ""),
        work_description=data.get("work_description", ""),
        self_assessment=data.get("self_assessment", ""),
        status=data.get("status", "draft"),
    )
    if report.status == "submitted":
        report.submitted_at = datetime.utcnow()

    db.session.add(report)
    db.session.commit()
    return jsonify(_report_to_dict(report)), 201


# PUT /api/reports/<id>
@reports_bp.route("/<int:report_id>", methods=["PUT"])
@login_required
def update_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        raise NotFoundError("Sprawozdanie", report_id)

    data = request.get_json()

    if "company_description" in data:
        report.company_description = data["company_description"]
    if "work_description" in data:
        report.work_description = data["work_description"]
    if "self_assessment" in data:
        report.self_assessment = data["self_assessment"]

    if "status" in data:
        report.status = data["status"]
        if report.status == "submitted" and not report.submitted_at:
            report.submitted_at = datetime.utcnow()
        if report.status == "approved":
            report.approved_at = datetime.utcnow()

    db.session.commit()
    return jsonify(_report_to_dict(report)), 200


@reports_bp.route("/generate-pdf/report/<int:internship_id>", methods=["GET"])
@login_required
def generate_report_pdf(internship_id):
    sql = text("""
        SELECT s.first_name, s.last_name, s.index_number, s.study_field, s.study_year, s.study_form,
               i.company_name, r.company_description, r.work_description, r.self_assessment
        FROM report r
        JOIN internship i ON r.internship_id = i.id
        JOIN users s ON i.student_id = s.id
        WHERE i.id = :id
    """)
    data = db.session.execute(sql, {"id": internship_id}).mappings().fetchone()

    if not data:
        return "Brak danych", 404

    pdf = BasePDF(doc_number="6")
    pdf.set_auto_page_break(auto=True, margin=35)
    pdf.add_page()

    pdf.set_font("Cambria", "B", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, "Akademia Nauk Stosowanych", ln=True, align="L")
    pdf.cell(0, 6, "w Elblągu", ln=True, align="L")

    pdf.ln(3)

    pdf.set_font("Cambria", "B", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, "Instytut Informatyki Stosowanej", ln=True, align="L")

    pdf.set_font("Cambria", "I", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, "im. Krzysztofa Brzeskiego", ln=True, align="L")

    pdf.ln(8)

    pdf.set_font("Cambria", "", 11)
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(25, 7, "Student:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(70, 7, f"{data['first_name']} {data['last_name']}", ln=0)
    pdf.set_font("Cambria", "", 11)
    pdf.cell(28, 7, "Nr albumu:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(data["index_number"]), ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(25, 6, "Kierunek:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, "informatyka", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(25, 6, "Specjalność: ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, str(data["study_field"] or ""), ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(25, 6, "Studia:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, f"inżynierskie, {data['study_form']}", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(25, 6, "Rok ak.:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, str(data["study_year"] or ""), ln=True)

    pdf.ln(12)

    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 8, "SPRAWOZDANIE STUDENTA", ln=True, align="C")
    pdf.cell(0, 8, "Z  PRAKTYKI  ZAWODOWEJ", ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(18, 7, "odbytej w ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(data["company_name"] or ""), ln=True)

    pdf.ln(6)

    def to_roman(n):
        return {1: "I", 2: "II", 3: "III"}.get(n, str(n))

    sections = [
        (
            "CHARAKTERYSTYKA MIEJSCA ODBYWANIA PRAKTYKI",
            "(Krótki opis instytucji, w której odbywała się praktyka zawodowa)",
            data["company_description"],
        ),
        (
            "OPIS I ANALIZA WYKONYWANYCH PRAC",
            "(Syntetyczny opis wykonanych prac)",
            data["work_description"],
        ),
        (
            "WIEDZA I UMIEJĘTNOŚCI UZYSKANE W TRAKCIE PRAKTYKI",
            "(Samoocena w zakresie nabytych kompetencji oraz osiągniętych efektów uczenia się)",
            data["self_assessment"],
        ),
    ]

    for idx, (title, subtitle, content) in enumerate(sections, start=1):
        pdf.set_font("Cambria", "B", 12)
        pdf.multi_cell(0, 7, f"{to_roman(idx)}.  {title}")

        pdf.set_font("Cambria", "I", 10)
        pdf.set_x(25)
        pdf.multi_cell(150, 5, subtitle)

        pdf.set_font("Cambria", "", 11)
        pdf.ln(2)
        pdf.multi_cell(0, 6, str(content or ""))
        pdf.ln(6)

    pdf_bytes = pdf.output(dest="S")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"sprawozdanie_{data['index_number']}.pdf",
        as_attachment=True,
    )
