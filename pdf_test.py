from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Spacer
from reportlab.platypus import Table

def create_pdf(report):
    total_applications = report['users'].sum()
    total_issued = report['is_issued'].sum()
    total_conversion = round(
        total_issued / total_applications * 100, 2
    ) if total_applications > 0 else 0

    elements = []

    pdf = SimpleDocTemplate("output/test_report.pdf")
    styles = getSampleStyleSheet()

    data = [
        ['Metric', 'Value'],
        ['Applications', 10000],
        ['Issued', 3500],
        ['Conversion', '35%']
    ]

    table = Table(data)

    elements.append(Paragraph("Key Performance Indicators", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Automated Analytics Report", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Image("output/monthly_amount.png", width=450, height=225))
    elements.append(Spacer(1, 20))
    elements.append(Image("output/conversion_by_source.png", width=450, height=225))
    elements.append(Spacer(1, 20))
    elements.append(Image("output/applications_vs_issued.png", width=450, height=225))

    pdf.build(elements)