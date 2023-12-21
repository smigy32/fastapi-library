from celery import Celery
from fpdf import FPDF

celery_app = Celery("tasks", broker="redis://redis:6379")


@celery_app.task
def generate_pdf(items: list, type: str):
    pdf = FPDF()
    pdf.set_font("helvetica", size=16)
    for item in items:
        if type == "books":
            pdf.add_page()
            pdf.set_font(size=24, style="B")
            pdf.cell(text=f"{item['title']}", ln=True)
            pdf.set_font(size=16, style="I")
            pdf.cell(text="Description:", ln=True)
            pdf.set_font(style="")
            pdf.multi_cell(text=f"{item['description']}", w=0)
    pdf.output("attachments/catalog.pdf")
