from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

BASE_DIR = Path(__file__).resolve().parent.parent

font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"

pdfmetrics.registerFont(
    TTFont("ArialUnicode", font_path)
)

styles = getSampleStyleSheet()
styles["Normal"].fontName = "ArialUnicode"

text = """
Аналітичний висновок за вересень 2026 року.

Обсяг виданих кредитів зменшився на 11,11%.

Найбільше падіння спостерігається у джерелі Facebook.

Рекомендується перевірити якість трафіку та конверсію.
"""

pdf = SimpleDocTemplate(
    str(BASE_DIR / "output" / "test_ukrainian.pdf")
)

elements = [
    Paragraph(text.replace("\n", "<br/>"), styles["Normal"])
]

pdf.build(elements)

print("Ukrainian PDF test: PASSED")