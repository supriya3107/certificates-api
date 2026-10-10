from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

PRIMARY = colors.HexColor("#1F3A5F")
ACCENT = colors.HexColor("#C9A227")
TEXT = colors.HexColor("#333333")


def generate_certificate_pdf(name: str, course: str, issue_date: date) -> bytes:
    buffer = BytesIO()
    page_size = landscape(A4)
    width, height = page_size
    c = canvas.Canvas(buffer, pagesize=page_size)

    # Double border
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(6)
    c.rect(25, 25, width - 50, height - 50)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.rect(40, 40, width - 80, height - 80)

    # Title
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(width / 2, height - 130, "CERTIFICATE OF COMPLETION")

    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(width / 2 - 120, height - 148, width / 2 + 120, height - 148)

    # Body
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 200, "This is to certify that")

    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-BoldOblique", 34)
    c.drawCentredString(width / 2, height - 255, name)

    c.setFillColor(TEXT)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 300, "has successfully completed the course")

    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 340, course)

    # Footer
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 14)
    c.drawString(90, 90, f"Date: {issue_date.strftime('%B %d, %Y')}")
    c.line(width - 260, 95, width - 90, 95)
    c.drawCentredString(width - 175, 75, "Authorized Signature")

    c.showPage()
    c.save()
    return buffer.getvalue()