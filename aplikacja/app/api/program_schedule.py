import io
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required
from sqlalchemy import text
from app import db
from app.utils.pdf_base import BasePDF
from app.auth.decorators import role_required

program_schedule_bp = Blueprint(
    "program_schedule", __name__, url_prefix="/api/program_schedule"
)


@program_schedule_bp.route("/<int:internship_id>/program/status", methods=["PUT"])
@login_required
@role_required("uopz")
def update_program_status(internship_id):
    data = request.get_json(force=True)
    status = data.get("status")
    comment = data.get("comment")
    agreed_date = data.get("agreed_date")

    db.session.execute(
        text("""
        UPDATE program_schedule
        SET status = :status,
            uopz_comment = :comment,
            agreed_date = :agreed_date
        WHERE internship_id = :id
    """),
        {
            "status": status,
            "comment": comment,
            "agreed_date": agreed_date,
            "id": internship_id,
        },
    )

    db.session.commit()
    return jsonify({"success": True}), 200


@program_schedule_bp.route("/<int:internship_id>", methods=["GET"])
@login_required
def get_program_schedule(internship_id):
    prog = (
        db.session.execute(
            text("""
        SELECT id, status, uopz_comment, agreed_date
        FROM program_schedule
        WHERE internship_id = :id
    """),
            {"id": internship_id},
        )
        .mappings()
        .fetchone()
    )

    if not prog:
        return (
            jsonify(
                {
                    "status": "draft",
                    "program_tasks": [],
                    "entries": [],
                    "agreed_date": None,
                }
            ),
            200,
        )
    tasks = (
        db.session.execute(
            text(
                "SELECT outcome_number, description FROM program_task WHERE program_id = :p"
            ),
            {"p": prog.id},
        )
        .mappings()
        .fetchall()
    )
    entries = (
        db.session.execute(
            text(
                "SELECT lp, department, planned_days FROM schedule_entry WHERE program_id = :p ORDER BY lp ASC"
            ),
            {"p": prog.id},
        )
        .mappings()
        .fetchall()
    )

    return (
        jsonify(
            {
                "status": prog.status,
                "uopz_comment": prog.uopz_comment or "",
                "agreed_date": prog.agreed_date,
                "program_tasks": [dict(t) for t in tasks],
                "entries": [dict(e) for e in entries],
            }
        ),
        200,
    )


@program_schedule_bp.route("/<int:internship_id>", methods=["POST", "PUT"])
@login_required
def save_program_schedule(internship_id):
    data = request.get_json(force=True)
    agreed_date = data.get("agreed_date")
    try:
        res = db.session.execute(
            text("""
            INSERT INTO program_schedule (internship_id, status, agreed_date)
            VALUES (:id, :s, :date)
            ON CONFLICT (internship_id) DO UPDATE SET
                status = EXCLUDED.status,
                agreed_date = EXCLUDED.agreed_date
            RETURNING id
        """),
            {
                "id": internship_id,
                "s": data.get("status", "draft"),
                "date": agreed_date,
            },
        )

        pid = res.fetchone()[0]
        db.session.execute(
            text("DELETE FROM program_task WHERE program_id = :pid"), {"pid": pid}
        )
        for t in data.get("program_tasks", []):
            db.session.execute(
                text(
                    "INSERT INTO program_task (program_id, outcome_number, description) VALUES (:pid, :n, :d)"
                ),
                {"pid": pid, "n": t["outcome_number"], "d": t["description"]},
            )
        db.session.execute(
            text("DELETE FROM schedule_entry WHERE program_id = :pid"), {"pid": pid}
        )
        for e in data.get("entries", []):
            db.session.execute(
                text(
                    "INSERT INTO schedule_entry (program_id, lp, department, planned_days) VALUES (:pid, :lp, :dep, :days)"
                ),
                {
                    "pid": pid,
                    "lp": e["lp"],
                    "dep": e["department"],
                    "days": e["planned_days"],
                },
            )
        db.session.commit()
        return jsonify({"message": "Zapisano"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@program_schedule_bp.route(
    "/generate-pdf/program_schedule/<int:internship_id>", methods=["GET"]
)
@login_required
def generate_program_pdf(internship_id):
    sql_base = text("""
        SELECT u.first_name, u.last_name, u.index_number, u.study_field, u.study_form, u.study_year,
               i.company_name, i.start_date, i.end_date, i.working_days,
               ps.id as program_id, ps.agreed_date
        FROM internship i
        JOIN users u ON i.student_id = u.id
        LEFT JOIN program_schedule ps ON ps.internship_id = i.id
        WHERE i.id = :id
    """)
    data = db.session.execute(sql_base, {"id": internship_id}).mappings().fetchone()

    if not data:
        return "Brak danych o praktyce", 404

    tasks_dict = {}
    schedule_list = []

    if data.get("program_id"):
        sql_tasks = text(
            "SELECT outcome_number, description FROM program_task WHERE program_id = :pid"
        )
        tasks = (
            db.session.execute(sql_tasks, {"pid": data["program_id"]})
            .mappings()
            .fetchall()
        )
        for t in tasks:
            tasks_dict[t["outcome_number"]] = t["description"]

        sql_schedule = text(
            "SELECT lp, department, planned_days FROM schedule_entry WHERE program_id = :pid ORDER BY lp"
        )
        schedule_list = (
            db.session.execute(sql_schedule, {"pid": data["program_id"]})
            .mappings()
            .fetchall()
        )

    sched_dict = {s["lp"]: s for s in schedule_list}

    pdf = BasePDF(doc_number="2a", display_footer=False)
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
    pdf.cell(25, 7, "Student:  ", ln=0)
    pdf.cell(0, 6, f"{data['first_name']} {data['last_name']}", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Nr albumu:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, str(data["index_number"] or ""), ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(34, 6, "Kierunek studiów:  ", ln=0)
    pdf.set_font("Cambria", "BI", 11)
    pdf.cell(0, 6, "informatyka", ln=True)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(25, 6, "Specjalność: ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 6, str(data["study_field"] or ""), ln=True)

    pdf.ln(4)

    pdf.set_font("Cambria", "", 11)
    pdf.ln(2)
    pdf.cell(60, 7, "Miejsce praktyk (instytucja):", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(data["company_name"] or ""), ln=True)

    pdf.ln(4)

    pdf.set_font("Cambria", "", 11)
    pdf.cell(54, 7, "Termin realizacji praktyki: od ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(25, 7, f"{data['start_date']}", ln=0)
    pdf.set_font("Cambria", "", 11)
    pdf.cell(16, 7, "Do:  ", ln=0)
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(0, 7, str(data["end_date"]), ln=True)

    pdf.ln(4)

    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 6, "PROGRAM PRAKTYKI ZAWODOWEJ", ln=True, align="C")

    pdf.ln(2)

    col1_w = [80, 80]

    pdf.set_font("Cambria", "B", 9)
    start_x = pdf.get_x()
    start_y = pdf.get_y()

    pdf.cell(col1_w[0], 10, "Efekty kształcenia", border=1, align="C")
    pdf.set_xy(start_x + col1_w[0], start_y + 1)
    pdf.multi_cell(
        col1_w[1],
        4,
        "Dział (komórka) / przykładowe prace\nwykonywane przez praktykanta",
        align="C",
    )
    pdf.set_xy(start_x + col1_w[0], start_y)
    pdf.cell(col1_w[1], 10, "", border=1)
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
        num = i + 1
        full_desc = f"{num:02d}. {desc}"
        task_text = tasks_dict.get(num, "")

        if pdf.get_y() > 240:
            pdf.add_page()
            start_x = pdf.get_x()

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.set_xy(x_start, y_start)
        pdf.multi_cell(col1_w[0], 4.5, full_desc, border=0)
        h1 = pdf.get_y() - y_start

        pdf.set_xy(x_start + col1_w[0], y_start)
        pdf.multi_cell(col1_w[1], 4.5, task_text, border=0)
        h2 = pdf.get_y() - y_start

        row_h = max(8, h1, h2)

        pdf.set_xy(x_start, y_start)
        pdf.cell(col1_w[0], row_h, "", border=1)
        pdf.set_xy(x_start + col1_w[0], y_start)
        pdf.cell(col1_w[1], row_h, "", border=1)

        pdf.set_y(y_start + row_h)

    pdf.add_page()
    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 6, "HARMONOGRAM PRAKTYKI ZAWODOWEJ", ln=True, align="C")
    pdf.ln(2)

    col2_w = [15, 115, 30]

    pdf.set_font("Cambria", "B", 9)
    start_x = pdf.get_x()
    start_y = pdf.get_y()

    pdf.cell(col2_w[0], 10, "L.p.", border=1, align="C")

    pdf.set_xy(start_x + col2_w[0], start_y + 1)
    pdf.multi_cell(
        col2_w[1], 4, "Dział / komórka\n(miejsce odbywania praktyki)", align="C"
    )
    pdf.set_xy(start_x + col2_w[0], start_y)
    pdf.cell(col2_w[1], 10, "", border=1)

    pdf.set_xy(start_x + col2_w[0] + col2_w[1], start_y + 1)
    pdf.multi_cell(col2_w[2], 4, "Planowana liczba\ndni roboczych", align="C")
    pdf.set_xy(start_x + col2_w[0] + col2_w[1], start_y)
    pdf.cell(col2_w[2], 10, "", border=1)

    pdf.set_y(start_y + 10)

    total_days = 0
    pdf.set_font("Cambria", "", 9)

    for i in range(1, 14):
        item = sched_dict.get(i)

        dept = item["department"] if item else ""
        days_planned = item["planned_days"] if item else ""

        if item and item["planned_days"]:
            total_days += int(item["planned_days"])

        if pdf.get_y() > 250:
            pdf.add_page()
            start_x = pdf.get_x()

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.set_xy(x_start + col2_w[0], y_start)
        pdf.multi_cell(col2_w[1], 5, dept, border=0)
        row_h = max(8, pdf.get_y() - y_start)

        pdf.set_xy(x_start, y_start)
        pdf.cell(col2_w[0], row_h, str(i), border=1, align="C")

        pdf.set_xy(x_start + col2_w[0], y_start)
        pdf.cell(col2_w[1], row_h, "", border=1)

        pdf.set_xy(x_start + col2_w[0] + col2_w[1], y_start)
        pdf.cell(col2_w[2], row_h, str(days_planned), border=1, align="C")

        pdf.set_y(y_start + row_h)

    pdf.set_font("Cambria", "B", 9)
    pdf.cell(col2_w[0], 8, "", border="LBT")
    pdf.cell(col2_w[1], 8, "Łącznie", border="RBT", align="R")
    pdf.cell(
        col2_w[2],
        8,
        str(total_days) if total_days > 0 else "",
        border=1,
        align="C",
        ln=True,
    )

    pdf.cell(col2_w[0], 8, "", border="LB")
    pdf.cell(col2_w[1], 8, "Wymagana", border="RB", align="R")
    pdf.cell(col2_w[2], 8, "120", border=1, align="C", ln=True)
    pdf.ln(10)

    agreed_d = data.get("agreed_date") or "........................................"
    pdf.set_font("Cambria", "", 10)
    pdf.cell(0, 6, f"Uzgodniono w dniu: {agreed_d}", ln=True)
    pdf.ln(15)

    sig_w = 160 / 3
    pdf.set_font("Cambria", "", 8)

    x_start = pdf.get_x()
    pdf.cell(
        sig_w, 4, ".......................................................", align="C"
    )
    pdf.cell(
        sig_w, 4, ".......................................................", align="C"
    )
    pdf.cell(
        sig_w,
        4,
        ".......................................................",
        align="C",
        ln=True,
    )

    pdf.set_x(x_start)
    pdf.cell(sig_w, 4, "podpis uczelnianego", align="C")
    pdf.cell(sig_w, 4, "podpis zakładowego", align="C")
    pdf.cell(sig_w, 4, "podpis studenta", align="C", ln=True)

    pdf.set_x(x_start)
    pdf.cell(sig_w, 4, "opiekuna praktyki", align="C")
    pdf.cell(sig_w, 4, "opiekuna praktyki", align="C")
    pdf.cell(sig_w, 4, "", align="C", ln=True)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"program_harmonogram_{data['index_number']}.pdf",
        as_attachment=True,
    )
