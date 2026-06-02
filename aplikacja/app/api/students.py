from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.user import User, db
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from app.models.internship import Internship

students_bp = Blueprint("students", __name__, url_prefix="/api/students")

REQUIRED_FIELDS = ["first_name", "last_name", "index_number", "email"]


def _validate_student(data):
    for field in REQUIRED_FIELDS:
        if not data.get(field) or not str(data[field]).strip():
            raise ValidationError(f"Pole '{field}' jest wymagane.")
    if "@" not in data["email"]:
        raise ValidationError("Nieprawidłowy adres e-mail.")
    index = str(data["index_number"]).strip()
    if not index.isdigit() or len(index) != 5:
        raise ValidationError("Numer indeksu musi składać się z dokładnie 5 cyfr.")


def _student_to_dict(user):
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "index_number": user.index_number,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "study_field": user.study_field,
        "study_year": user.study_year,
        "study_form": user.study_form,
        "semester": user.semester,
    }


@students_bp.route("", methods=["GET"])
@login_required
@role_required("uopz", "zopz", "sekretariat", "administrator")
def get_students():
    query = User.query.filter_by(role="student")

    if current_user.role == "uopz":
        query = (
            query.join(Internship, User.id == Internship.student_id)
            .filter(Internship.uopz_id == current_user.id)
            .distinct()
        )

    elif current_user.role == "zopz":
        query = (
            query.join(Internship, User.id == Internship.student_id)
            .filter(Internship.zopz_id == current_user.id)
            .distinct()
        )

    students = query.all()
    return jsonify([_student_to_dict(s) for s in students]), 200


# GET /api/students/<id>
@students_bp.route("/<int:student_id>", methods=["GET"])
@login_required
@role_required("student", "uopz", "sekretariat", "administrator")
def get_student(student_id):
    student = User.query.filter_by(id=student_id, role="student").first()
    if not student:
        raise NotFoundError("Student", student_id)
    return jsonify(_student_to_dict(student)), 200


# POST /api/students
@students_bp.route("", methods=["POST"])
@login_required
@role_required("sekretariat", "administrator")
def create_student():
    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych w żądaniu.")
    _validate_student(data)

    if User.query.filter_by(email=data["email"]).first():
        raise ValidationError("Użytkownik z tym e-mailem już istnieje.")
    if User.query.filter_by(index_number=str(data["index_number"]).strip()).first():
        raise ValidationError("Użytkownik z tym numerem indeksu już istnieje.")

    student = User(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        email=data["email"].strip(),
        index_number=str(data["index_number"]).strip(),
        role="student",
        is_active=True,
        auth_provider="manual",
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(_student_to_dict(student)), 201


# PUT /api/students/<id>
@students_bp.route("/<int:student_id>", methods=["PUT"])
@login_required
def update_student(student_id):
    is_staff = current_user.role in ["sekretariat", "administrator"]
    is_owner = current_user.id == student_id

    if not (is_staff or is_owner):
        return jsonify({"error": "Brak uprawnień"}), 403

    student = User.query.filter_by(id=student_id, role="student").first()
    if not student:
        raise NotFoundError("Student", student_id)

    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych w żądaniu.")

    if "study_field" in data:
        student.study_field = data["study_field"]
    if "study_year" in data:
        student.study_year = data["study_year"]
    if "study_form" in data:
        student.study_form = data["study_form"]
    if "semester" in data:
        student.semester = int(data["semester"])

    if is_staff:
        if "first_name" in data:
            student.first_name = data["first_name"].strip()
        if "last_name" in data:
            student.last_name = data["last_name"].strip()
        if "email" in data:
            student.email = data["email"].strip()
        if "index_number" in data:
            student.index_number = str(data["index_number"]).strip()
        if "is_active" in data:
            student.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify(_student_to_dict(student)), 200


# DELETE /api/students/<id>
@students_bp.route("/<int:student_id>", methods=["DELETE"])
@login_required
@role_required("administrator")
def delete_student(student_id):
    student = User.query.filter_by(id=student_id, role="student").first()
    if not student:
        raise NotFoundError("Student", student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"Student id={student_id} został usunięty."}), 200


# GET /api/students/list/pending
@students_bp.route("/list/pending", methods=["GET"])
@login_required
@role_required("administrator")
def get_pending():
    users = User.query.filter_by(role="pending", is_active=False).all()
    return jsonify([_student_to_dict(u) for u in users]), 200


# PUT /api/students/<id>/approve
@students_bp.route("/<int:student_id>/approve", methods=["PUT"])
@login_required
@role_required("administrator")
def approve_user(student_id):
    user = User.query.get(student_id)
    if not user:
        raise NotFoundError("Użytkownik", student_id)

    data = request.get_json()
    allowed_roles = ["student", "uopz", "zopz", "sekretariat", "administrator"]
    role = data.get("role", "student")
    if role not in allowed_roles:
        raise ValidationError(f"Nieprawidłowa rola. Dozwolone: {allowed_roles}")

    if role == "student":
        index = str(data.get("index_number", "")).strip()
        if not index.isdigit() or len(index) != 5:
            raise ValidationError("Numer indeksu studenta musi mieć dokładnie 5 cyfr.")
        if User.query.filter(User.index_number == index, User.id != student_id).first():
            raise ValidationError(f"Numer indeksu {index} jest już zajęty.")
        user.index_number = index

    user.role = role
    user.is_active = True
    db.session.commit()
    return jsonify(_student_to_dict(user)), 200


# GET /api/students/list/supervisors
@students_bp.route("/list/supervisors", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_supervisors():
    role = request.args.get("role")
    roles = ["uopz", "zopz"]
    if role in ("uopz", "zopz"):
        roles = [role]
    users = User.query.filter(User.role.in_(roles), User.is_active == True).all()
    return (
        jsonify(
            [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": u.role,
                }
                for u in users
            ]
        ),
        200,
    )
