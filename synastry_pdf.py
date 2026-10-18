"""Shared comparison content, PDF generated in memory without retaining profiles."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4


def create_comparison_pdf(reading):
    stream=BytesIO();styles={k:ParagraphStyle(k,fontName='Times-Roman' if k=='title' else 'Helvetica',fontSize=s,leading=s*1.45,textColor=HexColor('#244e70' if k=='title' else '#292d32'),spaceAfter=10) for k,s in [('title',20),('body',10),('small',9)]}
    def p(text,kind='body'):return Paragraph(escape(text),styles[kind])
    story=[p('Dos cartas, una conversación','title'),p(reading['notice'])]
    for i,profile in enumerate(reading['profiles'],1):
        birth=profile['birth'];story.append(p(f"Carta {i}: {birth['local_datetime']} · {birth['timezone']} · Sol en {profile['sun']}, Luna en {profile['moon']}, Ascendente en {profile['ascendant']}.",'small'))
    for section in reading['sections']:
        story.extend([Spacer(1,8),KeepTogether([p(section['title'],'title'),p(section['summary'])]),p(section['question'])])
        for crossing in section['crossings']:
            block=[p(crossing['label'],'small')]
            if crossing['text']!=section['summary']:block.append(p(crossing['text']))
            story.append(KeepTogether(block))
    story.extend([p('Cómo se preparó esta lectura','title'),p(reading['method']),p('Interpretaciones para entretenimiento y reflexión. Las decisiones económicas requieren considerar sus circunstancias reales; esta lectura no sustituye asesoramiento profesional.'),p('Los datos se procesan para preparar esta comparación y la aplicación no los almacena en una base de datos. Los proveedores pueden tratar información técnica de conexión. Esta copia contiene datos de ambas personas: guárdenla en un lugar privado.'),p('Información de uso y privacidad: https://traceastra.com/informacion.html','small')])
    def page(canvas,doc):
        canvas.saveState();canvas.setFillColor(HexColor('#f6f3ec'));canvas.rect(0,0,*A4,fill=1,stroke=0);canvas.setFillColor(HexColor('#244e70'));canvas.setFont('Helvetica',10);canvas.drawString(48,805,'TraceAstra · Comparación de dos cartas');canvas.drawString(48,30,'Copia personal · '+str(doc.page));canvas.restoreState()
    SimpleDocTemplate(stream,pagesize=A4,leftMargin=48,rightMargin=48,topMargin=60,bottomMargin=55,title='Dos cartas, una conversación · TraceAstra').build(story,onFirstPage=page,onLaterPages=page)
    return stream.getvalue()
