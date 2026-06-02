import io
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required
from sqlalchemy import text
from app import db
from app.utils.pdf_base import BasePDF

card_bp = Blueprint("card", __name__, url_prefix="/api/card")


@card_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_internship_card(id):
    try:
        card = (
            db.session.execute(
                text("SELECT * FROM internship_card WHERE internship_id = :id"),
                {"id": id},
            )
            .mappings()
            .fetchone()
        )

        if not card:
            return (
                jsonify(
                    {
                        "internship_id": id,
                        "zopz_comment": "",
                        "date": "",
                        "status": "draft",
                    }
                ),
                200,
            )

        card_data = dict(card)
        if card_data.get("date"):
            card_data["date"] = str(card_data["date"])
        if card_data.get("created_at"):
            card_data["created_at"] = str(card_data["created_at"])
        if card_data.get("updated_at"):
            card_data["updated_at"] = str(card_data["updated_at"])

        return jsonify(card_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@card_bp.route("/zopz/<int:id>", methods=["PUT", "POST"])
@login_required
def update_zopz_card(id):
    data = request.get_json(force=True)

    zopz_comment = data.get("zopz_comment")
    zopz_grade = data.get("zopz_grade")
    date_val = data.get("date")
    status = data.get("status", "submitted")

    try:
        db.session.execute(
            text("""
                INSERT INTO internship_card (internship_id, zopz_comment, zopz_grade, date, status)
                VALUES (:id, :zopz_comment, :zopz_grade, :date, :status)
                ON CONFLICT (internship_id)
                DO UPDATE SET
                    zopz_comment = EXCLUDED.zopz_comment,
                    zopz_grade = EXCLUDED.zopz_grade,
                    date = EXCLUDED.date,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                "id": id,
                "zopz_comment": zopz_comment,
                "zopz_grade": zopz_grade,
                "date": date_val if date_val else None,
                "status": status,
            },
        )
        db.session.commit()
        return jsonify({"message": "Zaświadczenie wraz z oceną zostało zapisane"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@card_bp.route("/status/<int:id>", methods=["PUT"])
@login_required
def review_internship_card(id):
    data = request.get_json(force=True)

    status = data.get("status")
    uopz_grade = data.get("uopz_grade")
    uopz_comment = data.get("uopz_comment")
    report_grade = data.get("report_grade")

    try:
        db.session.execute(
            text("""
                UPDATE internship_card
                SET status = :status,
                    uopz_grade = :uopz_grade,
                    uopz_comment = :uopz_comment,
                    report_grade = :report_grade,
                    updated_at = CURRENT_TIMESTAMP
                WHERE internship_id = :id
            """),
            {
                "status": status,
                "uopz_grade": uopz_grade,
                "uopz_comment": uopz_comment,
                "report_grade": report_grade,
                "id": id,
            },
        )
        db.session.commit()
        return jsonify({"message": "Status i oceny zaświadczenia zaktualizowane"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@card_bp.route("/generate-pdf/card/<int:internship_id>", methods=["GET"])
@login_required
def generate_card_pdf(internship_id):
    sql = text("""
        SELECT u.first_name, u.last_name, u.index_number, u.study_field, u.study_form,
               i.company_name, i.start_date, i.end_date, i.working_days, i.company_address,
               i.agreement_no, i.agreement_date,
               uopz.first_name as uopz_first_name, uopz.last_name as uopz_last_name,
               zopz.first_name as zopz_first_name, zopz.last_name as zopz_last_name,
               c.zopz_grade, c.zopz_comment, c.uopz_grade, c.uopz_comment, c.report_grade, c.date
        FROM internship i
        JOIN users u ON i.student_id = u.id
        LEFT JOIN users uopz ON i.uopz_id = uopz.id
        LEFT JOIN users zopz ON i.zopz_id = zopz.id
        LEFT JOIN internship_card c ON i.id = c.internship_id
        WHERE i.id = :id
    """)
    data = db.session.execute(sql, {"id": internship_id}).mappings().fetchone()

    if not data:
        return "Brak danych o praktyce", 404

    pdf = BasePDF(doc_number="3", display_footer=False)
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

    pdf.set_font("Cambria", "B", 12)
    pdf.cell(0, 6, "KARTA PRAKTYKI ZAWODOWEJ", ln=True, align="C")
    pdf.ln(5)

    form = data.get("study_form") or "stacjonarne / niestacjonarne*"
    hours = data.get("working_days") or 120
    start_d = data.get("start_date") or "...................."
    end_d = data.get("end_date") or "...................."
    op_ucz = (
        f"{data.get('super_first') or ''} {data.get('super_last') or ''}".strip()
        or "................................................"
    )

    pdf.set_font("Cambria", "B", 11)
    pdf.cell(160, 8, "SKIEROWANIE NA PRAKTYKĘ", border="LTR", align="C", ln=True)

    pdf.set_font("Cambria", "", 10)
    tekst_por = f"Na podstawie porozumienia nr {data.get('agreement_no') or '........'}, z dnia {data.get('agreement_date') or '........'} r., kieruję niżej wymienionego studenta na praktykę zawodową do zakładu pracy:"

    y_start = pdf.get_y()
    x_start = pdf.get_x()
    pdf.set_x(x_start + 1)
    pdf.multi_cell(158, 5, tekst_por, border=0, align="L")
    y_end = pdf.get_y()

    pdf.line(x_start, y_start, x_start, y_end)
    pdf.line(x_start + 160, y_start, x_start + 160, y_end)
    pdf.set_y(y_end)
    pdf.set_x(x_start)

    company_str = data.get("company_name")
    if not company_str or str(company_str).strip() == "":
        company_str = ".........................................................................................."
    else:
        company_str = str(company_str).strip()

    pdf.set_font("Cambria", "B", 11)
    y_start = pdf.get_y()
    pdf.set_x(x_start + 1)
    pdf.multi_cell(158, 6, company_str, border=0, align="C")
    y_end = pdf.get_y()

    pdf.line(x_start, y_start, x_start, y_end)
    pdf.line(x_start + 160, y_start, x_start + 160, y_end)
    pdf.set_y(y_end)
    pdf.set_x(x_start)

    pdf.set_font("Cambria", "", 8)
    pdf.cell(
        160, 4, "(nazwa instytucji / zakładu pracy)", border="LRB", align="C", ln=True
    )

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Imię i nazwisko:", border="LT")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(125, 6, f"{data['first_name']} {data['last_name']}", border="TR", ln=True)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Numer albumu:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(125, 6, str(data["index_number"]), border="R", ln=True)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Studia:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(125, 6, f"inżynierskie {form}", border="R", ln=True)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Kierunek:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(125, 6, "informatyka", border="R", ln=True)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Specjalność:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(
        125,
        6,
        str(data.get("study_field") or "........................................"),
        border="R",
        ln=True,
    )

    pdf.set_font("Cambria", "", 10)
    pdf.cell(45, 6, "Czas trwania praktyki:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(115, 6, f"6 miesięcy ({hours} dni roboczych)", border="R", ln=True)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(75, 6, "Uczelniany opiekun praktyki zawodowej:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(
        85,
        6,
        f"{data.get('uopz_first_name')} {data.get('uopz_last_name')}",
        border="R",
        ln=True,
    )

    pdf.set_font("Cambria", "", 10)
    pdf.cell(35, 6, "Termin praktyki:", border="L")
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(125, 6, f"od {start_d} do {end_d}", border="R", ln=True)

    y_start = pdf.get_y()
    x_start = pdf.get_x()
    box_h = 16

    pdf.set_xy(x_start, y_start)
    pdf.cell(80, box_h, "", border=1)
    pdf.cell(80, box_h, "", border=1)

    pdf.set_xy(x_start, y_start + 3)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(80, 4, "Dyrektor Instytutu", align="C", ln=True)
    pdf.set_x(x_start)
    pdf.cell(80, 4, "lub osoba upoważniona", align="C")

    pdf.set_xy(x_start + 80, y_start + 3)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(
        80,
        4,
        "......................................................................",
        align="C",
        ln=True,
    )
    pdf.set_x(x_start + 80)
    pdf.set_font("Cambria", "BI", 8)
    pdf.cell(80, 4, "(podpis)", align="C")
    pdf.set_y(y_start + box_h)

    pdf.set_font("Cambria", "", 10)
    pdf.cell(160, 6, "Zakładowy opiekun praktyki zawodowej:", border="LTR", ln=True)
    pdf.cell(
        160,
        6,
        "..............................................................................................................................................................................................",
        border="LR",
        align="C",
        ln=True,
    )
    pdf.cell(
        160,
        6,
        "..............................................................................................................................................................................................",
        border="LR",
        align="C",
        ln=True,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(
        160,
        4,
        "(imię i nazwisko, funkcja, zajmowane stanowisko)",
        border="LRB",
        align="C",
        ln=True,
    )

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(
        160,
        8,
        "Potwierdzam zgłoszenie się studenta na praktykę:",
        border="LTR",
        ln=True,
    )
    pdf.set_font("Cambria", "", 10)
    pdf.cell(70, 6, "", border="L")
    pdf.cell(
        90,
        6,
        "........................................................................................",
        border="R",
        align="C",
        ln=True,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(70, 4, "", border="L")
    pdf.cell(
        90,
        4,
        "(data, pieczęć i podpis zakładowego opiekuna praktyki)",
        border="R",
        align="C",
        ln=True,
    )

    pdf.set_font("Cambria", "B", 10)
    pdf.cell(160, 8, "Potwierdzam odbycie szkolenia BHP:", border="LR", ln=True)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(70, 6, "", border="L")
    pdf.cell(
        90,
        6,
        "........................................................................................",
        border="R",
        align="C",
        ln=True,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(70, 4, "", border="LB")
    pdf.cell(
        90,
        4,
        "(data, pieczęć i podpis upoważnionego pracownika zakładu)",
        border="RB",
        align="C",
        ln=True,
    )

    pdf.cell(160, 3, "", border="LTR", ln=True)
    pdf.set_font("Cambria", "BU", 12)
    pdf.cell(
        160,
        8,
        "Zaświadczenie odbycia praktyki zawodowej",
        border="LR",
        align="C",
        ln=True,
    )
    pdf.cell(160, 3, "", border="LR", ln=True)

    x_start = pdf.get_x()
    y_start = pdf.get_y()
    pdf.set_font("Cambria", "", 10)
    pdf.cell(42, 6, "Zaświadczam, że student ", border="L")
    pdf.set_xy(x_start + 42, y_start)
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(85, 5, f"{data['first_name']} {data['last_name']}", align="C")
    pdf.set_xy(x_start + 127, y_start)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(33, 6, " odbył praktykę", border="R", align="R", ln=True)

    pdf.cell(42, 4, "zawodową", border="L")
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(85, 4, "(imię i nazwisko)", align="C")
    pdf.cell(33, 4, "", border="R", ln=True)
    pdf.cell(160, 2, "", border="LR", ln=True)

    x_start = pdf.get_x()
    y_start = pdf.get_y()
    pdf.set_font("Cambria", "", 10)
    pdf.cell(7, 6, "w ", border="L")
    pdf.set_xy(x_start + 7, y_start)
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(146, 5, company_str, align="C")
    pdf.set_xy(x_start + 153, y_start)
    pdf.cell(7, 6, "", border="R", ln=True)
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(7, 4, "", border="L")
    pdf.cell(146, 4, "(nazwa zakładu)", align="C")
    pdf.cell(7, 4, "", border="R", ln=True)
    pdf.cell(160, 2, "", border="LR", ln=True)

    x_start = pdf.get_x()
    y_start = pdf.get_y()
    pdf.set_font("Cambria", "", 10)
    pdf.cell(42, 6, "w okresie (okresach) od ", border="L")
    pdf.set_xy(x_start + 42, y_start)
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(25, 5, str(data.get("start_date") or ""), align="C")

    pdf.set_xy(x_start + 67, y_start)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(8, 6, " do ", align="C")
    pdf.set_xy(x_start + 75, y_start)
    pdf.set_font("Cambria", "B", 10)
    pdf.cell(25, 5, str(data.get("end_date") or ""), align="C")

    pdf.set_xy(x_start + 100, y_start)
    pdf.set_font("Cambria", "", 10)
    pdf.cell(60, 6, " zgodnie z przyjętym", border="R", align="L", ln=True)
    pdf.cell(160, 6, "programem.", border="LR", ln=True)
    pdf.cell(160, 2, "", border="LR", ln=True)

    pdf.cell(
        160,
        6,
        "Uwagi: .......................................................................................................................................................................",
        border="LR",
        ln=True,
    )
    pdf.cell(
        160,
        6,
        ".....................................................................................................................................................................................",
        border="LR",
        ln=True,
    )
    pdf.cell(
        160,
        6,
        ".....................................................................................................................................................................................",
        border="LR",
        ln=True,
    )
    pdf.cell(
        160,
        6,
        ".....................................................................................................................................................................................",
        border="LR",
        ln=True,
    )
    pdf.cell(160, 4, "", border="LR", ln=True)

    pdf.cell(
        80,
        6,
        f"{data.get('company_address')} {data.get('date')}",
        border="L",
        align="C",
    )
    pdf.cell(
        80,
        6,
        "..................................................................",
        border="R",
        align="C",
        ln=True,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.cell(80, 6, "(miejscowość i data)", border="LB", align="C")
    pdf.cell(
        80, 6, "(pieczęć i podpis kierownika zakładu)", border="RB", align="C", ln=True
    )

    W = 160
    x_start = pdf.get_x()

    if pdf.get_y() > 250:
        pdf.add_page()
    else:
        pdf.ln(5)

    pdf.set_font("Cambria", "B", 11)
    pdf.set_x(x_start)
    pdf.cell(W, 8, "Ocena przebiegu praktyki zawodowej", border=1, align="C", ln=1)

    if pdf.get_y() > 200:
        pdf.add_page()

    y_box_start = pdf.get_y()

    pdf.set_font("Cambria", "", 10)
    pdf.ln(3)
    pdf.set_x(x_start)
    pdf.cell(
        W,
        6,
        f"Ocena parametryczna (w skali 2 do 5): {data.get('zopz_grade') or '........................'}",
        border=0,
        align="C",
        ln=1,
    )

    pdf.ln(2)
    pdf.set_x(x_start + 2)
    pdf.cell(W - 4, 5, "Ocena opisowa:", border=0, align="L", ln=1)

    pdf.set_font("Cambria", "B", 10)
    pdf.set_x(x_start + 2)
    zopz_c = str(
        data.get("zopz_comment")
        or "........................................................................................................................................................................................................................................................................................"
    )
    pdf.multi_cell(W - 4, 5, zopz_c, border=0, align="L")

    pdf.ln(6)
    y_sig = pdf.get_y()

    pdf.set_font("Cambria", "", 10)
    pdf.set_xy(x_start + 2, y_sig)
    pdf.cell(80, 5, "Zakładowy opiekun praktyki zawodowej:", border=0, align="L", ln=1)
    pdf.set_x(x_start + 2)
    pdf.cell(
        80,
        5,
        f"{data.get('zopz_first_name')} {data.get('zopz_last_name')}",
        border=0,
        align="L",
    )

    pdf.set_xy(x_start + 80, y_sig)
    pdf.cell(
        78,
        5,
        "..........................................................",
        border=0,
        align="R",
        ln=1,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.set_x(x_start + 80)
    pdf.cell(78, 4, "(data, pieczęć i podpis)", border=0, align="R", ln=1)

    pdf.ln(3)
    y_box_end = pdf.get_y()
    pdf.rect(x_start, y_box_start, W, y_box_end - y_box_start)
    pdf.set_y(y_box_end)

    if pdf.get_y() > 200:
        pdf.add_page()

    y_box_start = pdf.get_y()

    pdf.set_font("Cambria", "", 10)
    pdf.ln(3)
    pdf.set_x(x_start)
    pdf.cell(
        W,
        6,
        f"Ocena parametryczna (w skali 2 do 5): {data.get('uopz_grade') or '........................'}",
        border=0,
        align="C",
        ln=1,
    )

    pdf.ln(2)
    pdf.set_x(x_start + 2)
    pdf.cell(W - 4, 5, "Ocena opisowa:", border=0, align="L", ln=1)

    pdf.set_font("Cambria", "B", 10)
    pdf.set_x(x_start + 2)
    uopz_c = str(
        data.get("uopz_comment")
        or "........................................................................................................................................................................................................................................................................................"
    )
    pdf.multi_cell(W - 4, 5, uopz_c, border=0, align="L")

    pdf.ln(6)
    y_sig = pdf.get_y()

    pdf.set_font("Cambria", "", 10)
    pdf.set_xy(x_start + 2, y_sig)
    pdf.cell(80, 5, "Uczelniany opiekun praktyki zawodowej:", border=0, align="L", ln=1)
    pdf.set_x(x_start + 2)
    pdf.cell(
        80,
        5,
        f"{data.get('uopz_first_name')} {data.get('uopz_last_name')}",
        border=0,
        align="L",
    )

    pdf.set_xy(x_start + 80, y_sig)
    pdf.cell(
        78,
        5,
        "..........................................................",
        border=0,
        align="R",
        ln=1,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.set_x(x_start + 80)
    pdf.cell(78, 4, "(data, pieczęć i podpis)", border=0, align="R", ln=1)

    pdf.ln(3)
    y_box_end = pdf.get_y()
    pdf.rect(x_start, y_box_start, W, y_box_end - y_box_start)
    pdf.set_y(y_box_end)

    if pdf.get_y() > 250:
        pdf.add_page()

    y_box_start = pdf.get_y()
    pdf.ln(4)

    pdf.set_font("Cambria", "B", 10)
    pdf.set_x(x_start + 2)
    pdf.cell(
        30,
        6,
        "Ocena sprawozdania z praktyki (w skali 2 do 5):",
        border=0,
        align="L",
        ln=0,
    )
    pdf.set_font("Cambria", "B", 11)
    pdf.cell(
        56,
        6,
        str(data.get("report_grade") or "........................"),
        border=0,
        align="R",
        ln=1,
    )

    pdf.ln(6)
    pdf.set_x(x_start + 80)
    pdf.cell(
        78,
        5,
        "..........................................................",
        border=0,
        align="R",
        ln=1,
    )
    pdf.set_font("Cambria", "I", 8)
    pdf.set_x(x_start + 80)
    pdf.cell(78, 4, "(data i podpis uczelnianego opiekuna)", border=0, align="R", ln=1)

    pdf.ln(3)
    y_box_end = pdf.get_y()
    pdf.rect(x_start, y_box_start, W, y_box_end - y_box_start)
    pdf.set_y(y_box_end)

    pdf_bytes = pdf.output(dest="S")

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"karta_praktyki_{data['index_number']}.pdf",
        as_attachment=True,
    )
