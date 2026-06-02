import os
from fpdf import FPDF


class BasePDF(FPDF):
    def __init__(self, doc_number, display_footer=True):
        super().__init__()

        self.doc_number = doc_number
        self.display_footer = display_footer

        self.set_margins(25, 10, 25)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.abspath(
            os.path.join(base_dir, "..", "..", "app", "fonts", "cambria")
        )

        self.add_font("Cambria", "", os.path.join(font_dir, "cambria.ttf"), uni=True)
        self.add_font(
            "Cambria", "B", os.path.join(font_dir, "cambria-bold.ttf"), uni=True
        )
        self.add_font(
            "Cambria", "I", os.path.join(font_dir, "cambria-italic.ttf"), uni=True
        )
        self.add_font(
            "Cambria", "BI", os.path.join(font_dir, "cambria-bold-italic.ttf"), uni=True
        )

    def footer(self):
        if not self.display_footer:
            return

        self.set_y(-30)
        self.set_x(self.l_margin)
        self.set_font("Cambria", "", 10)
        self.cell(0, 5, "……………………………..……………………….", ln=True, align="R")
        self.set_x(self.l_margin)
        self.set_font("Cambria", "", 8)
        self.cell(0, 5, "data i podpis studenta", ln=True, align="R")

    def header(self):
        self.set_font("Cambria", "", 11)
        self.set_x(self.l_margin)
        self.cell(0, 5, f"Załącznik nr {self.doc_number}", ln=True, align="R")
        self.ln(6)
