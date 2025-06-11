import pdfkit
import markdown
import platform

if platform.system() == 'Windows':
    # Путь для Windows
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
else:
    # Путь по умолчанию для Linux (Render.com)
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

def itinerary_to_pdf(itinerary_text, filename):
    itinerary_html = markdown.markdown(itinerary_text)

    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                line-height: 1.5;
            }}
            h1, h2, h3 {{
                color: #0056b3;
                margin-top: 20px;
            }}
            ul {{
                margin-left: 15px;
                padding-left: 5px;
            }}
            li {{
                margin-bottom: 10px;
            }}
            a {{
                color: #1a73e8;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        {itinerary_html}
    </body>
    </html>
    """

    pdfkit.from_string(html_template, filename, configuration=config)
