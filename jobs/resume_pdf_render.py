from io import BytesIO
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa


class ResumePdfRender:
    @staticmethod
    def render(user):
        template = get_template('pdf_template.html')
        html = template.render({'user': user})
        resume_file = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), resume_file, encoding='UTF-8')
        if not pdf.err:
            return resume_file
        return None
