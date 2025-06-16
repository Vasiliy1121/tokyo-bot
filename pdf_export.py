from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import re

def clean_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (ссылка: \2)', text)
    return text

def itinerary_to_pdf(itinerary_text, filename):
    pdf = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))
    pdf.setFont('Arial', 12)

    clean_text = clean_markdown(itinerary_text)
    lines = clean_text.split('\n')
    y = height - 40
    line_height = 16

    for line in lines:
        if not line.strip():
            y -= line_height
            continue

        if line.startswith("📅"):
            pdf.setFont('Arial', 14)
            y -= 10
        elif line.startswith(("🌅", "🏙️", "🌃")):
            pdf.setFont('Arial', 13)
            y -= 6
        else:
            pdf.setFont('Arial', 12)

        if y < 40:
            pdf.showPage()
            pdf.setFont('Arial', 12)
            y = height - 40

        pdf.drawString(40, y, line.strip())
        y -= line_height

    pdf.save()
