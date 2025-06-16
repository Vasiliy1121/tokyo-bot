from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import re


def clean_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    return text


def itinerary_to_pdf(itinerary_text, filename):
    pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = 'Arial'
    styles["Normal"].fontSize = 12
    styles["Normal"].leading = 15

    story = []
    lines = itinerary_text.split('\n')

    for line in lines:
        if line.startswith("📅"):
            style = styles["Heading1"]
            style.fontName = 'Arial'
            style.fontSize = 16
            story.append(Spacer(1, 0.15 * inch))
        elif line.startswith(("🌅", "🏙️", "🌃")):
            style = styles["Heading2"]
            style.fontName = 'Arial'
            style.fontSize = 14
            story.append(Spacer(1, 0.1 * inch))
        else:
            style = styles["Normal"]

        line = clean_markdown(line)
        paragraph = Paragraph(line, style)
        story.append(paragraph)
        story.append(Spacer(1, 0.05 * inch))

    doc.build(story)
