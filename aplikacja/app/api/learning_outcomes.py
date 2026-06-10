from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.user import db
from sqlalchemy import text
from flask import send_file
import io
from app.utils.pdf_base import BasePDF

learning_outcomes_bp = Blueprint("learning_outcomes", __name__)


@learning_outcomes_bp.route("/internship/<int:internship_id>", methods=["GET"])
@login_required
def get_learning_outcomes_by_internship(internship_id):
    result = db.session.execute(
        text("SELECT * FROM learning_outcomes_forms WHERE internship_id = :id"),
        {"id": internship_id},
    ).fetchone()

    if not result:
        return jsonify({"status": "draft", "items": []}), 200

    form_id = result.id
    items_result = db.session.execute(
        text(
            "SELECT outcome_number, achieved FROM learning_outcomes_items WHERE form_id = :form_id"
        ),
        {"form_id": form_id},
    ).fetchall()

    items = [
        {"outcome_number": row.outcome_number, "achieved": row.achieved}
        for row in items_result
    ]

    return (
        jsonify(
            {
                "id": result.id,
                "internship_id": result.internship_id,
                "status": result.status,
                "supervisor_comment_general": result.supervisor_comment_general,
                "items": items,
            }
        ),
        200,
    )


@learning_outcomes_bp.route("", methods=["POST"])
@learning_outcomes_bp.route("/", methods=["POST"])
@login_required
def create_learning_outcomes():
    data = request.get_json(force=True)
    internship_id = data.get("internship_id")
    status = data.get("status", "draft")
    items = data.get("items", [])

    if not internship_id:
        return jsonify({"error": "Brak ID praktyki"}), 400

    try:
        form_result = db.session.execute(
            text("""
                INSERT INTO learning_outcomes_forms (internship_id, status)
                VALUES (:internship_id, :status)
                RETURNING id
            """),
            {"internship_id": internship_id, "status": status},
        )
        new_form_id = form_result.fetchone()[0]

        for item in items:
            db.session.execute(
                text("""
                    INSERT INTO learning_outcomes_items (form_id, outcome_number, achieved)
                    VALUES (:form_id, :outcome_number, :achieved)
                """),
                {
                    "form_id": new_form_id,
                    "outcome_number": item["outcome_number"],
                    "achieved": item["achieved"],
                },
            )

        db.session.commit()
        return jsonify({"message": "Zapisano pomyślnie", "id": new_form_id}), 201

    except Exception as e:
        db.session.rollback()
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@learning_outcomes_bp.route("/<int:form_id>", methods=["PUT"])
@login_required
def update_learning_outcomes(form_id):
    data = request.get_json(force=True)
    new_status = data.get("status", "zopz_approved")
    items = data.get("items", [])

    try:
        db.session.execute(
            text(
                "UPDATE learning_outcomes_forms SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
            ),
            {"status": new_status, "id": form_id},
        )
        db.session.execute(
            text("DELETE FROM learning_outcomes_items WHERE form_id = :form_id"),
            {"form_id": form_id},
        )
        for item in items:
            db.session.execute(
                text("""
                    INSERT INTO learning_outcomes_items (form_id, outcome_number, achieved) 
                    VALUES (:form_id, :outcome_number, :achieved)
                """),
                {
                    "form_id": form_id,
                    "outcome_number": item["outcome_number"],
                    "achieved": item["achieved"],
                },
            )
        db.session.commit()
        return jsonify({"message": "Formularz zaktualizowany"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@learning_outcomes_bp.route("/<int:form_id>/status", methods=["PUT"])
@login_required
def update_learning_outcomes_status(form_id):
    data = request.get_json(force=True)
    new_status = data.get("status")
    comment = data.get("supervisor_comment_general", "")

    if not new_status:
        return jsonify({"error": "Brak statusu"}), 400

    try:
        result = db.session.execute(
            text("""
                UPDATE learning_outcomes_forms
                SET status = :status, supervisor_comment_general = :comment, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {"status": new_status, "comment": comment, "id": form_id},
        )
        if result.rowcount == 0:
            db.session.rollback()
            return jsonify({"error": "Nie znaleziono dokumentu"}), 404

        db.session.commit()
        return jsonify({"message": "Status zaktualizowany"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@learning_outcomes_bp.route(
    "/generate-pdf/learning_outcomes/<int:internship_id>", methods=["GET"]
)
@login_required
def generate_learning_outcomes_pdf(internship_id):
    sql_user = text("""
        SELECT u.first_name, u.last_name, u.index_number, u.study_field,
               i.working_days, lof.id as form_id, lof.supervisor_comment_general
        FROM internship i
        JOIN users u ON i.student_id = u.id
        LEFT JOIN learning_outcomes_forms lof ON lof.internship_id = i.id
        WHERE i.id = :id
    """)
    user_data = (
        db.session.execute(sql_user, {"id": internship_id}).mappings().fetchone()
    )

    if not user_data:
        return "Brak danych o praktyce", 404

    outcomes_dict = {}
    if user_data.get("form_id"):
        sql_items = text(
            "SELECT outcome_number, achieved FROM learning_outcomes_items WHERE form_id = :form_id"
        )
        items = (
            db.session.execute(sql_items, {"form_id": user_data["form_id"]})
            .mappings()
            .fetchall()
        )
        for item in items:
            outcomes_dict[item["outcome_number"]] = item["achieved"]

    pdf = BasePDF(doc_number="4", display_footer=False)
    pdf.add_page()

    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 6, "POTWIERDZENIE UZYSKANIA", ln=True, align="C")
    pdf.cell(
        0, 6, "EFEKTÓW UCZENIA SIĘ W RAMACH PRAKTYKI ZAWODOWEJ", ln=True, align="C"
    )
    pdf.ln(8)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 7, "Student:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(70, 7, f"{user_data['first_name']} {user_data['last_name']}", ln=0)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Nr albumu:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, f"{user_data['index_number']}", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Kierunek:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, "informatyka", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Specjalność: ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, str(user_data["study_field"] or ""), ln=True)

    pdf.ln(4)

    hours = (user_data["working_days"] or 120) * 8
    pdf.set_font("Cambria", "", 11)
    pdf.multi_cell(
        0,
        6,
        f"W ramach praktyki zawodowej zrealizowanego w wymiarze {hours} godzin uzyskał/a zakładane dla praktyki zawodowej efekty uczenia się:",
    )
    pdf.ln(4)

    col_w = [10, 115, 35]

    pdf.set_font("Cambria", "B", 9)
    start_y = pdf.get_y()
    start_x = pdf.get_x()

    pdf.cell(col_w[0] + col_w[1], 10, "Efekty uczenia się", border=1, align="C")

    pdf.set_xy(start_x + col_w[0] + col_w[1], start_y + 1)
    pdf.multi_cell(col_w[2], 4, "Potwierdzenie\nuzyskania efektów", align="C")

    pdf.set_xy(start_x + col_w[0] + col_w[1], start_y)
    pdf.cell(col_w[2], 10, "", border=1)

    pdf.set_y(start_y + 10)

    outcomes_desc = [
        "Ma wiedzę na temat sposobu realizacji zadań inżynierskich dotyczących informatyki z zachowaniem standardów i norm technicznych",
        "Zna technologie, narzędzia, metody, techniki oraz sprzęt stosowane w informatyce",
        "Zna ekonomiczne, prawne skutki własnych działań podejmowanych w ramach praktyki oraz ograniczenia wynikające z prawa autorskiego i kodeksu pracy",
        "Zna zasady bezpieczeństwa pracy i ergonomii w zawodzie informatyka",
        "Pozyskuje informacje odnośnie technologii, metod, technik, sprzętu wymaganego do realizacji powierzonego zadania, posługując się rozmaitymi źródłami literaturowymi i zasobami publikowanymi w języku polskim jak i angielskim",
        "W oparciu o kontakty ze środowiskiem inżynierskim zakładu, potrafi podnieść swoje kompetencje, wiedzę i umiejętności, co najmniej z dwóch zakresów: zadania dotyczące sprzętu i oprogramowania: np.: programowania, administrowanie siecią komputerową, konserwacja sprzętu i oprogramowania, bieżące usuwanie usterek, administrowanie zasobami informatycznymi, zakładu pracy / instytucji, (e)usługami.",
        "Opracowuje dokumentację dotyczącą realizacji podejmowanych zadań w ramach praktyki, a także referuje ustnie prezentowane w niej zagadnienia",
        "Potrafi zidentyfikować problem informatyczny występujący w zakładzie pracy / instytucji, opisać go, przedstawić koncepcję rozwiązania i ją zrealizować.",
        "Potrafi rozwiązać rzeczywiste zadanie inżynierskie z zakresu działalności informatycznej zakładu pracy/instytucji stosując normy i standardy stosowane w informatyce oraz biorąc pod uwagę aspekty środowiskowe i etyczne.",
        "Pracuje w zespole zajmującym się zawodowo branżą IT",
        "Przestrzega zasad etyki zawodowej i zgodnie z tymi zasadami korzysta z wiedzy i pomocy doświadczonych kolegów",
        "Kontaktując się z osobami spoza branży potrafi zarówno pozyskać od nich niezbędne informacje do realizacji planowanego zadania, jak i przekazać im w sposób zrozumiały informacje i opinie z zakresu informatyki",
        "Dostrzega w praktyce tempo deaktualizacji wiedzy informatycznej oraz skutki działalności informatyków w szczególności ekonomiczne i społeczne",
    ]

    pdf.set_font("Cambria", "", 9)

    for i, desc in enumerate(outcomes_desc):
        outcome_num = i + 1

        achieved = outcomes_dict.get(outcome_num)
        if achieved is True:
            status_text = "uzyskał/a"
        elif achieved is False:
            status_text = "nie uzyskał/a"
        else:
            status_text = "uzyskał/a* \n nie uzyskał/a*"

        if pdf.get_y() > 240:
            pdf.add_page()
            start_x = pdf.get_x()

        y_start = pdf.get_y()
        x_start = pdf.get_x()

        pdf.set_xy(x_start + col_w[0], y_start)
        pdf.multi_cell(col_w[1], 4.5, desc, border=0)
        y_end = pdf.get_y()

        row_h = max(10, y_end - y_start)

        pdf.set_xy(x_start, y_start)

        pdf.cell(col_w[0], row_h, f"{outcome_num:02d}.", border=1, align="C")

        pdf.cell(col_w[1], row_h, "", border=1)

        pdf.set_xy(x_start + col_w[0] + col_w[1], y_start + (row_h / 2) - 3)
        pdf.multi_cell(col_w[2], 4, status_text, align="C")

        pdf.set_xy(x_start + col_w[0] + col_w[1], y_start)
        pdf.cell(col_w[2], row_h, "", border=1)

        pdf.set_y(y_start + row_h)

    pdf.ln(5)

    if pdf.get_y() > 200:
        pdf.add_page()

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(0, 6, "Potwierdzenie bezpośredniego opiekuna zakładowego:", ln=True)
    pdf.ln(10)
    pdf.set_font("Cambria", "", 9)
    pdf.cell(0, 5, "………………………….…………………………………..", ln=True, align="R")
    pdf.cell(0, 5, "Data, podpis i pieczęć zakładu pracy", ln=True, align="R")
    pdf.ln(10)

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(0, 6, "Opinia opiekuna uczelnianego", ln=True)
    pdf.set_font("Cambria", "", 10)

    opinion = user_data.get("supervisor_comment_general")
    if opinion:
        pdf.multi_cell(0, 6, opinion)
        pdf.ln(10)
    else:
        pdf.cell(
            0, 6, "…………………………………………………………………………………………..……………………………………………………", ln=True
        )
        pdf.cell(
            0, 6, "………………………………………..………………………………………………………………………………………………………", ln=True
        )
        pdf.cell(
            0, 6, "…...……………………………………..…………………………………………………………………………………………………….", ln=True
        )
        pdf.ln(5)

    pdf.set_font("Cambria", "", 9)
    pdf.cell(0, 5, "………………………….…………………………………..", ln=True, align="R")
    pdf.cell(0, 5, "Data, podpis opiekuna uczelnianego", ln=True, align="R")

    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"efekty_uczenia_sie_{user_data['index_number']}.pdf",
        as_attachment=True,
    )
