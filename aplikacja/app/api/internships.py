from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import text
from app.models.user import User, db
from app.models.internship import Internship
from app.models.diary import Diary, DiaryEntry
from app.models.document import Document
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from app.models.diary import Diary
from app.models.document import Document
from sqlalchemy import text

internships_bp = Blueprint("internships", __name__, url_prefix="/api/internships")

REQUIRED_FIELDS = ["index_number", "company_name", "start_date", "end_date"]
ALLOWED_STATUSES = ["pending", "active", "completed", "cancelled"]

STATUS_PL = {
    "pending": "Oczekująca",
    "active": "W trakcie",
    "completed": "Zakończona",
    "cancelled": "Anulowana",
}


def _internship_to_dict(i):
    from app.models.user import User

    student = User.query.get(i.student_id)
    return {
        "id": i.id,
        "student_id": i.student_id,
        "student_index": student.index_number if student else None,
        "student_name": student.full_name if student else None,
        "uopz_id": i.uopz_id,
        "zopz_id": i.zopz_id,
        "company_name": i.company_name,
        "company_address": i.company_address,
        "start_date": str(i.start_date),
        "end_date": str(i.end_date),
        "working_days": i.working_days,
        "status": i.status,
        "status_pl": STATUS_PL.get(i.status, i.status),
    }


# GET /api/internships?student_id=<id>
@internships_bp.route("", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_internships():
    from flask_login import current_user

    student_id = request.args.get("student_id", type=int)
    query = Internship.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    elif current_user.role == "uopz":
        query = query.filter_by(uopz_id=current_user.id)
    elif current_user.role == "zopz":
        query = query.filter_by(zopz_id=current_user.id)
    return jsonify([_internship_to_dict(i) for i in query.all()]), 200


# GET /api/internships/<id>
@internships_bp.route("/<int:internship_id>", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_internship(internship_id):
    i = Internship.query.get(internship_id)
    if not i:
        raise NotFoundError("Praktyka", internship_id)
    return jsonify(_internship_to_dict(i)), 200


# POST /api/internships
@internships_bp.route("", methods=["POST"])
@login_required
@role_required("sekretariat", "administrator")
def create_internship():
    data = request.get_json(force=True)

    index_number = data.get("index_number")
    company_name = data.get("company_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    student = db.session.execute(
        text("SELECT id FROM users WHERE index_number = :idx AND role = 'student'"),
        {"idx": index_number},
    ).fetchone()

    if not student:
        return (
            jsonify({"error": f"Student z indeksem {index_number} nie istnieje"}),
            400,
        )

    try:
        db.session.execute(
            text("""
                INSERT INTO internship (
                    student_id, company_name, company_address, start_date, end_date,
                    uopz_id, zopz_id, agreement_no, agreement_date, status
                ) VALUES (
                    :student_id, :company_name, :company_address, :start_date, :end_date,
                    :uopz_id, :zopz_id, :agreement_no, :agreement_date, 'pending'
                )
            """),
            {
                "student_id": student.id,
                "company_name": company_name,
                "company_address": data.get("company_address"),
                "start_date": start_date,
                "end_date": end_date,
                "uopz_id": data.get("uopz_id"),
                "zopz_id": data.get("zopz_id"),
                "agreement_no": data.get("agreement_no"),
                "agreement_date": data.get("agreement_date") or None,
            },
        )
        db.session.commit()
        return jsonify({"message": "Praktyka dodana"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# PUT /api/internships/<id>
@internships_bp.route("/<int:internship_id>", methods=["PUT"])
@login_required
@role_required("uopz", "sekretariat", "administrator")
def update_internship(internship_id):
    i = Internship.query.get(internship_id)
    if not i:
        raise NotFoundError("Praktyka", internship_id)

    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych w żądaniu.")

    if "status" in data:
        if data["status"] not in ALLOWED_STATUSES:
            raise ValidationError(
                f"Nieprawidłowy status. Dozwolone: {ALLOWED_STATUSES}"
            )
        i.status = data["status"]
    if "company_name" in data:
        i.company_name = data["company_name"].strip()
    if "company_address" in data:
        i.company_address = data["company_address"].strip()
    if "uopz_id" in data:
        if data["uopz_id"]:
            uopz = User.query.filter_by(id=data["uopz_id"], role="uopz").first()
            if not uopz:
                raise ValidationError("Opiekun uczelniany o podanym ID nie istnieje.")
        i.uopz_id = data["uopz_id"] or None
    if "zopz_id" in data:
        if data["zopz_id"]:
            zopz = User.query.filter_by(id=data["zopz_id"], role="zopz").first()
            if not zopz:
                raise ValidationError("Opiekun zakładowy o podanym ID nie istnieje.")
        i.zopz_id = data["zopz_id"] or None

    db.session.commit()
    return jsonify(_internship_to_dict(i)), 200


# DELETE /api/internships/<id>
@internships_bp.route("/<int:internship_id>", methods=["DELETE"])
@login_required
@role_required("administrator")
def delete_internship(internship_id):
    i = Internship.query.get(internship_id)
    if not i:
        raise NotFoundError("Praktyka", internship_id)

    diaries = Diary.query.filter_by(internship_id=internship_id).all()

    for diary in diaries:
        DiaryEntry.query.filter_by(diary_id=diary.id).delete()

    Diary.query.filter_by(internship_id=internship_id).delete()
    Document.query.filter_by(internship_id=internship_id).delete()

    db.session.delete(i)
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Praktyka id={internship_id} została usunięta wraz z całą historią."
            }
        ),
        200,
    )
