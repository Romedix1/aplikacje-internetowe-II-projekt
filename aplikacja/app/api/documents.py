from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.user import db
from app.models.document import Document
from app.models.internship import Internship
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from app.api.reports import generate_report_pdf
from app.api.diary import generate_diary_pdf
from app.api.surveys import generate_survey_pdf
from app.api.learning_outcomes import generate_learning_outcomes_pdf
from app.api.card import generate_card_pdf
from app.api.program_schedule import generate_program_pdf

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

REQUIRED_FIELDS = ["internship_id", "name", "doc_type"]
ALLOWED_TYPES = [
    "diary",
    "report",
    "card",
    "program_schedule",
    "learning_outcomes",
    "survey",
    "exam_protocol",
]


def _validate_document(data):
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            raise ValidationError(f"Pole '{field}' jest wymagane.")
    if data["doc_type"] not in ALLOWED_TYPES:
        raise ValidationError(
            f"Nieprawidłowy typ dokumentu. Dozwolone: {ALLOWED_TYPES}"
        )


def _doc_to_dict(d):
    return {
        "id": d.id,
        "internship_id": d.internship_id,
        "name": d.name,
        "doc_type": d.doc_type,
        "status": d.status,
        "submitted_at": str(d.submitted_at) if d.submitted_at else None,
        "supervisor_comment": d.supervisor_comment,
        "created_at": str(d.created_at),
        "content": getattr(d, "content", None),
    }


# GET /api/documents?internship_id=<id>
@documents_bp.route("", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_documents():
    internship_id = request.args.get("internship_id", type=int)
    query = Document.query
    if internship_id:
        query = query.filter_by(internship_id=internship_id)
    return jsonify([_doc_to_dict(d) for d in query.all()]), 200


# GET /api/documents/<id>
@documents_bp.route("/<int:doc_id>", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_document(doc_id):
    d = Document.query.get(doc_id)
    if not d:
        raise NotFoundError("Dokument", doc_id)
    return jsonify(_doc_to_dict(d)), 200


# POST /api/documents
@documents_bp.route("", methods=["POST"])
@login_required
@role_required("student", "uopz", "administrator")
def create_document():
    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych w żądaniu.")
    _validate_document(data)

    if not Internship.query.get(data["internship_id"]):
        raise NotFoundError("Praktyka", data["internship_id"])

    status = data.get("status", "draft")
    if status not in [
        "draft",
        "submitted",
        "under_review",
        "needs_revision",
        "approved",
    ]:
        raise ValidationError("Nieprawidłowy status.")

    d = Document(
        internship_id=data["internship_id"],
        name=data["name"].strip(),
        doc_type=data["doc_type"],
        status=status,
        supervisor_comment=data.get("supervisor_comment", ""),
        content=data.get("content"),
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(_doc_to_dict(d)), 201


# DELETE /api/documents/<id>
@documents_bp.route("/<int:doc_id>", methods=["DELETE"])
@login_required
@role_required("administrator")
def delete_document(doc_id):
    d = Document.query.get(doc_id)
    if not d:
        raise NotFoundError("Dokument", doc_id)
    db.session.delete(d)
    db.session.commit()
    return jsonify({"message": f"Dokument id={doc_id} został usunięty."}), 200


# PUT /api/documents/<id>/status
@documents_bp.route("/<int:doc_id>/status", methods=["PUT"])
@login_required
@role_required("uopz", "zopz", "sekretariat", "administrator")
def update_document_status(doc_id):
    d = Document.query.get(doc_id)
    if not d:
        raise NotFoundError("Dokument", doc_id)

    data = request.get_json()
    if not data or "status" not in data:
        raise ValidationError("Pole 'status' jest wymagane.")

    if data["status"] not in [
        "draft",
        "submitted",
        "under_review",
        "needs_revision",
        "approved",
    ]:
        raise ValidationError("Nieprawidłowy status.")

    d.status = data["status"]
    d.supervisor_comment = data.get("supervisor_comment", d.supervisor_comment)

    db.session.commit()
    return jsonify(_doc_to_dict(d)), 200


# PUT /api/documents/<id>
@documents_bp.route("/<int:doc_id>", methods=["PUT"])
@login_required
@role_required("student", "uopz", "administrator")
def update_document(doc_id):
    d = Document.query.get(doc_id)
    if not d:
        raise NotFoundError("Dokument", doc_id)

    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych w żądaniu.")

    if "status" in data:
        if data["status"] not in [
            "draft",
            "submitted",
            "under_review",
            "needs_revision",
            "approved",
        ]:
            raise ValidationError("Nieprawidłowy status.")
        d.status = data["status"]

    if "content" in data:
        d.content = data["content"]

    db.session.commit()
    return jsonify(_doc_to_dict(d)), 200


@documents_bp.route("/download/<doc_type>/<int:internship_id>", methods=["GET"])
@login_required
def download_document(doc_type, internship_id):
    if doc_type == "report":
        return generate_report_pdf(internship_id)
    elif doc_type == "diary":
        return generate_diary_pdf(internship_id)
    elif doc_type == "survey":
        return generate_survey_pdf(internship_id)
    elif doc_type == "learning_outcomes":
        return generate_learning_outcomes_pdf(internship_id)
    elif doc_type == "card":
        return generate_card_pdf(internship_id)
    elif doc_type == "program_schedule":
        return generate_program_pdf(internship_id)

    return "Dokument nieobsługiwany", 404
