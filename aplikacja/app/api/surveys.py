from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.user import db
from app.models.survey import Survey
from app.models.internship import Internship
from app.api.errors import NotFoundError, ValidationError
from app.auth.decorators import role_required
from app.models.survey import Survey
from sqlalchemy import text
from flask import send_file
import io
from app.utils.pdf_base import BasePDF

surveys_bp = Blueprint("surveys", __name__, url_prefix="/api/surveys")


def _survey_to_dict(s):
    d = {
        "id": s.id,
        "internship_id": s.internship_id,
        "status": s.status,
        "remarks": s.remarks or "",
        "submitted_at": str(s.submitted_at) if s.submitted_at else None,
    }
    for i in range(1, 15):
        d[f"q{i}"] = getattr(s, f"q{i}")
    return d


def _apply_answers(survey, data):
    survey.remarks = data.get("remarks", "")
    for i in range(1, 15):
        val = data.get(f"q{i}")
        if val is not None:
            setattr(survey, f"q{i}", int(val))


# GET /api/surveys/internship/<internship_id>
@surveys_bp.route("/by-internship/<int:internship_id>", methods=["GET"])
@login_required
@role_required("student", "uopz", "zopz", "sekretariat", "administrator")
def get_survey(internship_id):
    survey = Survey.query.filter_by(internship_id=internship_id).first()
    if not survey:
        return jsonify({}), 200
    return jsonify(_survey_to_dict(survey)), 200


# POST /api/surveys
@surveys_bp.route("", methods=["POST"])
@login_required
@role_required("student")
def create_survey():
    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych.")

    internship_id = data.get("internship_id")
    if not internship_id:
        raise ValidationError("Brak internship_id.")

    internship = Internship.query.get(internship_id)
    if not internship:
        raise NotFoundError("Praktyka", internship_id)
    if internship.student_id != current_user.id:
        raise ValidationError("Brak dostępu do tej praktyki.")

    existing = Survey.query.filter_by(internship_id=internship_id).first()
    if existing:
        raise ValidationError("Ankieta już istnieje — użyj PUT żeby ją zaktualizować.")

    survey = Survey(internship_id=internship_id, status="draft")
    _apply_answers(survey, data)

    if data.get("status") == "submitted":
        _validate_answers(data)
        survey.status = "submitted"
        survey.submitted_at = datetime.utcnow()

    db.session.add(survey)
    db.session.commit()
    return jsonify(_survey_to_dict(survey)), 201


# PUT /api/surveys/<id>
@surveys_bp.route("/<int:survey_id>", methods=["PUT"])
@login_required
@role_required("student")
def update_survey(survey_id):
    survey = Survey.query.get(survey_id)
    if not survey:
        raise NotFoundError("Ankieta", survey_id)

    internship = Internship.query.get(survey.internship_id)
    if internship.student_id != current_user.id:
        raise ValidationError("Brak dostępu.")

    if survey.status == "submitted":
        raise ValidationError("Ankieta jest już przesłana i nie można jej edytować.")

    data = request.get_json()
    if not data:
        raise ValidationError("Brak danych.")

    _apply_answers(survey, data)

    if data.get("status") == "submitted":
        _validate_answers(data)
        survey.status = "submitted"
        survey.submitted_at = datetime.utcnow()
    else:
        survey.status = "draft"

    db.session.commit()
    return jsonify(_survey_to_dict(survey)), 200


def _validate_answers(data):
    missing = [i for i in range(1, 15) if not data.get(f"q{i}")]
    if missing:
        raise ValidationError(
            f"Brak odpowiedzi na pytania: {missing}. Wypełnij wszystkie 14 pytań."
        )


@surveys_bp.route("/internship/<int:internship_id>", methods=["GET"])
@login_required
def get_survey_by_internship(internship_id):

    survey = Survey.query.filter_by(internship_id=internship_id).first()

    if not survey:
        return jsonify({}), 200

    return jsonify(_survey_to_dict(survey)), 200


@surveys_bp.route("/generate-pdf/survey/<int:internship_id>", methods=["GET"])
@login_required
def generate_survey_pdf(internship_id):
    sql = text("""
        SELECT u.index_number, u.study_year, u.study_field, u.study_form, u.semester,
               i.working_days,
               s.q1, s.q2, s.q3, s.q4, s.q5, s.q6, s.q7,
               s.q8, s.q9, s.q10, s.q11, s.q12, s.q13, s.q14,
               s.remarks
        FROM survey s
        JOIN internship i ON s.internship_id = i.id
        JOIN users u ON i.student_id = u.id
        WHERE i.id = :id
    """)
    data = db.session.execute(sql, {"id": internship_id}).mappings().fetchone()

    if not data:
        return "Brak ankiety dla tej praktyki", 404

    pdf = BasePDF(doc_number="5")
    pdf.add_page()

    pdf.set_font("Cambria", "B", 12)
    pdf.multi_cell(
        0,
        6,
        "Kwestionariusz ankiety oceniający przebieg praktyk zawodowych realizowanych w ramach programów studiów w Instytucie Informatyki Stosowanej im. K. Brzeskiego w Elblągu",
        align="C",
    )
    pdf.ln(5)

    pdf.set_font("Cambria", "", 10)
    intro_text = "W trosce o stałe podnoszenie jakości przebiegu praktyk zawodowych zwracamy się do Pani/Pana z prośbą o wypełnienie anonimowej ankiety dotyczącej praktyk zawodowych, w której należy określić w jakim stopniu zgadza się Pan/Pani z poniższymi stwierdzeniami."
    pdf.multi_cell(0, 5, intro_text)
    pdf.ln(5)

    pdf.multi_cell(
        0, 5, "Prosimy zaznaczyć przy każdym pytaniu X w wybranym polu odpowiedzi."
    )

    pdf.ln(6)

    col_w = [8, 82, 14, 14, 14, 14, 14]

    pdf.set_font("Cambria", "B", 6)

    start_y = pdf.get_y()
    start_x = pdf.get_x()

    headers = [
        "",
        "",
        "Zdecydo-\nwanie\ntak",
        "Raczej\ntak",
        "Trudno\npowie-\ndzieć",
        "Raczej\nnie",
        "Zdecydo-\nwanie\nnie",
    ]

    header_h = 13

    for i, h_text in enumerate(headers):
        current_x = start_x + sum(col_w[:i])

        pdf.set_xy(current_x, start_y)
        pdf.cell(col_w[i], header_h, "", border=1)

        if h_text:
            pdf.set_xy(current_x, start_y + 2.5)
            pdf.multi_cell(col_w[i], 3, h_text, align="C")

    pdf.set_y(start_y + header_h)
    pdf.set_x(start_x)

    questions = [
        "Poznałam/poznałem zasady funkcjonowania instytucji, w której odbywałam/odbywałem praktyki zawodowe.",
        "Poznałam/poznałem strukturę oraz regulamin organizacyjny instytucji, w której odbywałam/odbywałem praktyki zawodowe.",
        "Praktyki zawodowe umożliwiły mi pełną realizację ramowego programu praktyk zawodowych przewidzianego w ramach mojego kierunku studiów.",
        "Podczas praktyk zawodowych zwracano uwagę na przestrzeganie zasad etyki i tajemnicy zawodowej.",
        "Podczas praktyk miałam/miałem możliwość praktycznego zastosowania wiedzy teoretycznej zdobytej na zajęciach.",
        "Praktyki zawodowe przyczyniły się do pogłębienia mojej wiedzy i umiejętności zdobytych w trakcie studiów.",
        "Mogłem liczyć na wsparcie merytoryczne Opiekuna zakładowego praktyk.",
        "Mogłem liczyć na wsparcie merytoryczne Opiekuna uczelnianego praktyk.",
        "Opiekun zakładowy odpowiedzialny za praktyki zawodowe w miejscu ich odbywania potrafił prawidłowo zorganizować ich przebieg.",
        "Podczas praktyk zawodowych miałam/miałem możliwość pozyskiwania materiałów niezbędnych do przygotowania mojej pracy dyplomowej.",
        "Praktyki zawodowe rozwinęły moje umiejętności skutecznego komunikowania się w sytuacjach zawodowych i pracy w zespole.",
        "Praktyki zawodowe nauczyły mnie samodzielności i odpowiedzialności podczas wykonywania pracy.",
        "Liczba godzin realizowana w ramach praktyk zawodowych jest wystarczająca.",
        "Czy po zakończeniu praktyki zawodowej chciałaby/chciałby Pani/Pan współpracować z instytucją, w której Pani/Pan zrealizowała/zrealizował praktykę?",
    ]

    pdf.set_font("Cambria", "", 10)

    for i, question in enumerate(questions):
        answer_val = data.get(f"q{i+1}")

        if pdf.get_y() > 230:
            pdf.add_page()

        y_start = pdf.get_y()
        x_start = pdf.get_x()

        pdf.set_xy(x_start + col_w[0], y_start)
        pdf.multi_cell(col_w[1], 5, question, border=0)
        y_end = pdf.get_y()

        row_h = y_end - y_start

        pdf.set_xy(x_start, y_start)

        pdf.cell(col_w[0], row_h, str(i + 1), border=1, align="C")

        pdf.cell(col_w[1], row_h, "", border=1)

        for j in range(1, 6):
            mark = "X" if answer_val == (6 - j) else ""
            pdf.cell(col_w[j + 1], row_h, mark, border=1, align="C")

        pdf.set_y(y_start + row_h)

    pdf.ln(5)

    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, "Dodatkowe uwagi dotyczące przebiegu praktyki zawodowej:", ln=True)
    pdf.set_font("Cambria", "", 10)
    pdf.multi_cell(0, 6, str(data["remarks"] or "Brak uwag."))
    pdf.ln(10)

    if pdf.get_y() > 210:
        pdf.add_page()

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(0, 6, "Metryczka", ln=True, align="C")

    hours = (data["working_days"] or 120) * 8

    metryczka_data = [
        ("Rok akademicki", str(data["study_year"] or "")),
        ("Kierunek studiów", str(data["study_field"] or "")),
        ("Forma studiów", str(data["study_form"] or "stacjonarne / niestacjonarne")),
        ("Semestr studiów", str(data["semester"] or "")),
        ("Liczba godzin zrealizowanej praktyki zawodowej", f"{hours} h"),
    ]

    for label, value in metryczka_data:
        pdf.cell(90, 7, label, border=1)
        pdf.cell(70, 7, value, border=1, align="C")
        pdf.ln()

    pdf.ln(20)

    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 6, "Dziękujemy za udział w badaniu", ln=True, align="R")

    pdf_bytes = pdf.output(dest="S")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"ankieta_{data['index_number']}.pdf",
        as_attachment=True,
    )
