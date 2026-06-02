from datetime import date
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from app.models.user import db
from app.models.diary import Diary, DiaryEntry
from app.models.internship import Internship
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from sqlalchemy import text
import io
from app.utils.pdf_base import BasePDF

diary_bp = Blueprint("diary", __name__, url_prefix="/api/diary")


def _entry_to_dict(e):
    return {
        "id": e.id,
        "diary_id": getattr(e, "diary_id", None),
        "day_number": e.day_number,
        "work_date": str(e.work_date),
        "description": e.description,
        "outcome_numbers": e.outcome_numbers or "",
        "confirmed_by_zopz": e.confirmed_by_zopz,
        "confirmed_at": (
            str(e.confirmed_at) if getattr(e, "confirmed_at", None) else None
        ),
        "is_rejected": getattr(e, "is_rejected", False),
    }


def _diary_to_dict(diary):
    return {
        "id": diary.id,
        "internship_id": diary.internship_id,
        "status": diary.status,
        "entries": [_entry_to_dict(e) for e in diary.entries],
    }


def _get_or_create_diary(internship_id):
    diary = Diary.query.filter_by(internship_id=internship_id).first()
    if not diary:
        diary = Diary(internship_id=internship_id, status="draft")
        db.session.add(diary)
        db.session.commit()
    return diary


# GET /api/diary/<internship_id>
@diary_bp.route("/<int:internship_id>", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_diary(internship_id):
    internship = Internship.query.get(internship_id)
    if not internship:
        raise NotFoundError("Praktyka", internship_id)
    diary = _get_or_create_diary(internship_id)
    return jsonify(_diary_to_dict(diary)), 200


# POST /api/diary/<internship_id>/entries
@diary_bp.route("/<int:internship_id>/entries", methods=["POST"])
@login_required
@role_required("student")
def add_entry(internship_id):
    internship = Internship.query.get(internship_id)
    if not internship:
        raise NotFoundError("Praktyka", internship_id)
    if internship.student_id != current_user.id:
        raise ValidationError("Brak dostępu do tej praktyki.")

    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych.")

    day = data.get("day_number")
    if not day or not (1 <= int(day) <= 120):
        raise ValidationError("Numer dnia musi być między 1 a 120.")
    if not data.get("work_date"):
        raise ValidationError("Data jest wymagana.")
    if not data.get("description", "").strip():
        raise ValidationError("Opis prac jest wymagany.")

    try:
        work_date = date.fromisoformat(data["work_date"])
    except ValueError:
        raise ValidationError("Nieprawidłowy format daty.")

    diary = _get_or_create_diary(internship_id)

    if diary.status not in ("draft", "needs_revision"):
        raise ValidationError(
            "Dziennik jest zablokowany — został już przesłany do weryfikacji."
        )

    if DiaryEntry.query.filter_by(diary_id=diary.id).count() >= 120:
        raise ValidationError("Osiągnięto limit 120 wpisów w dzienniku.")

    if DiaryEntry.query.filter_by(diary_id=diary.id, day_number=int(day)).first():
        raise ValidationError(f"Wpis na dzień {day} już istnieje.")

    entry = DiaryEntry(
        diary_id=diary.id,
        day_number=int(day),
        work_date=work_date,
        description=data["description"].strip(),
        outcome_numbers=data.get("outcome_numbers", "").strip(),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(_entry_to_dict(entry)), 201


# PUT /api/diary/entries/<entry_id>/confirm
@diary_bp.route("/entries/<int:entry_id>/confirm", methods=["PUT"])
@login_required
@role_required("zopz")
def confirm_entry(entry_id):
    from app.models.diary import DiaryEntry, Diary
    from app.models.user import db
    from flask import request, jsonify
    from app.api.errors import NotFoundError, ValidationError

    entry = DiaryEntry.query.get(entry_id)
    if not entry:
        raise NotFoundError("Wpis", entry_id)

    data = request.get_json(silent=True)
    action = data.get("action")

    diary = Diary.query.get(entry.diary_id)

    if action == "confirm":
        entry.confirmed_by_zopz = True
        entry.is_rejected = False

        if diary:
            total_entries = DiaryEntry.query.filter_by(diary_id=diary.id).count()
            unconfirmed_count = DiaryEntry.query.filter_by(
                diary_id=diary.id, confirmed_by_zopz=False
            ).count()
            rejected_count = DiaryEntry.query.filter_by(
                diary_id=diary.id, is_rejected=True
            ).count()

            if unconfirmed_count == 0:
                if total_entries >= 120:
                    diary.status = "approved"
                else:
                    diary.status = "draft"

            elif rejected_count == 0 and diary.status == "needs_revision":
                diary.status = "under_review"

    elif action == "reject":
        entry.confirmed_by_zopz = False
        entry.is_rejected = True
        if diary:
            diary.status = "needs_revision"

    else:
        raise ValidationError("Nieprawidłowa akcja. Wymagane: 'confirm' lub 'reject'")

    db.session.commit()
    return jsonify({"message": f"Status zaktualizowany"}), 200


# DELETE /api/diary/entries/<entry_id>
@diary_bp.route("/entries/<int:entry_id>", methods=["DELETE"])
@login_required
@role_required("student")
def delete_entry(entry_id):
    entry = DiaryEntry.query.get(entry_id)
    if not entry:
        raise NotFoundError("Wpis", entry_id)
    diary = Diary.query.get(entry.diary_id)
    if diary.status not in ("draft", "needs_revision"):
        raise ValidationError("Nie można usuwać wpisów — dziennik jest zablokowany.")
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": f"Wpis #{entry_id} usunięty."}), 200


# PUT /api/diary/<internship_id>/submit
@diary_bp.route("/<int:internship_id>/submit", methods=["PUT"])
@login_required
@role_required("student")
def submit_diary(internship_id):
    from app.models.diary import Diary, DiaryEntry

    diary = Diary.query.filter_by(internship_id=internship_id).first()
    if not diary:
        raise NotFoundError("Dziennik", internship_id)

    DiaryEntry.query.filter_by(diary_id=diary.id).update(
        {DiaryEntry.is_rejected: False}
    )

    diary.status = "submitted"

    db.session.commit()
    return jsonify({"message": "Dziennik przesłany do weryfikacji"}), 200


@diary_bp.route("/generate-pdf/diary/<int:internship_id>", methods=["GET"])
@login_required
def generate_diary_pdf(internship_id):
    user_sql = text("""
        SELECT u.first_name, u.last_name, u.index_number, u.study_field, u.study_year, u.study_form, i.company_name, i.start_date, i.end_date
        FROM internship i
        JOIN users u ON i.student_id = u.id
        WHERE i.id = :id
    """)
    user_data = (
        db.session.execute(user_sql, {"id": internship_id}).mappings().fetchone()
    )

    if not user_data:
        return "Brak danych o praktyce", 404

    entries_sql = text("""
        SELECT de.day_number,
               de.work_date AS date,
               de.description,
               de.outcome_numbers AS learning_outcomes
        FROM diary_entry de
        JOIN diary d ON de.diary_id = d.id
        WHERE d.internship_id = :id
        ORDER BY de.day_number ASC
    """)

    entries = (
        db.session.execute(entries_sql, {"id": internship_id}).mappings().fetchall()
    )

    pdf = BasePDF(doc_number="7")

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

    pdf.set_font("Cambria", "B", 14)
    pdf.cell(0, 10, "DZIENNIK PRAKTYKI ZAWODOWEJ", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 7, "Student:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(70, 7, f"{user_data['first_name']} {user_data['last_name']}", ln=0)
    pdf.set_font("Cambria", "", 11)
    pdf.cell(28, 7, "Nr albumu:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(user_data["index_number"]), ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Kierunek:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, "informatyka", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "W zakresie: ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, str(user_data["study_field"] or ""), ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 7, "Studia:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(70, 7, f"{user_data['study_form']}", ln=0)
    pdf.set_font("Cambria", "", 11)
    pdf.cell(28, 7, "Rok ak.:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(user_data["study_year"]), ln=True)

    pdf.ln(4)

    pdf.set_font("Cambria", "", 11)
    pdf.ln(2)
    pdf.cell(60, 7, "Miejsce odbywania praktyki:", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(user_data["company_name"] or ""), ln=True)

    pdf.ln(4)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(48, 7, "Data rozpoczęcia praktyki:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(25, 7, f"{user_data['start_date']}", ln=0)
    pdf.set_font("Cambria", "", 11)
    pdf.cell(48, 7, "Data zakończenia praktyki:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(user_data["end_date"]), ln=True)

    pdf.add_page()

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(
        0,
        7,
        f"{user_data['first_name']} {user_data['last_name']} {user_data['index_number']}",
        ln=True,
        align="R",
    )
    pdf.ln(2)
    pdf.set_font("Cambria", "", 12)
    pdf.cell(0, 8, "DZIENNIK PRAKTYKI ZAWODOWEJ", ln=True, align="C")
    pdf.ln(2)
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(0, 8, user_data["company_name"], ln=True, align="C")

    pdf.set_font("Cambria", "B", 9)
    col_widths = [10, 25, 80, 20, 25]
    headers = ["Dzień", "Data", "Opis prac", "Efekty", "Podpis"]

    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Cambria", "", 8)

    for entry in entries:
        if pdf.get_y() > 250:
            pdf.add_page()

        start_y = pdf.get_y()
        start_x = pdf.get_x()

        pdf.set_xy(start_x + col_widths[0] + col_widths[1], start_y)
        pdf.multi_cell(col_widths[2], 5, str(entry["description"] or ""), border=0)

        y_after_desc = pdf.get_y()

        row_height = max(10, y_after_desc - start_y)

        pdf.set_xy(start_x, start_y)

        pdf.cell(
            col_widths[0], row_height, str(entry["day_number"]), border=1, align="C"
        )
        pdf.cell(col_widths[1], row_height, str(entry["date"]), border=1, align="C")

        pdf.cell(col_widths[2], row_height, "", border=1)

        pdf.cell(
            col_widths[3],
            row_height,
            str(entry["learning_outcomes"] or ""),
            border=1,
            align="C",
        )
        pdf.cell(col_widths[4], row_height, "", border=1)

        pdf.set_y(start_y + row_height)

    pdf_bytes = pdf.output(dest="S")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"dziennik_{user_data['index_number']}.pdf",
        as_attachment=True,
    )
