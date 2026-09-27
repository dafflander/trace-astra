"""Three-page vector PDF, rendered in memory; no file or network side effects."""
from io import BytesIO
from math import sin, cos, radians
from xml.sax.saxutils import escape
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4

PAPER=HexColor('#f6f3ec'); BLUE=HexColor('#244e70'); INK=HexColor('#292d32')
SIGNS=['Aries','Tauro','Géminis','Cáncer','Leo','Virgo','Libra','Escorpio','Sagitario','Capricornio','Acuario','Piscis']
GUIDE=[
 ('Sol','Identidad y expresión personal. Se asocia con aquello que buscas desarrollar.','¿Qué actividades te permiten expresarte de una manera propia?'),
 ('Luna','Necesidades emocionales, hábitos y aquello que te hace sentir protegido.','¿Qué te ayuda a recuperar la calma?'),
 ('Ascendente','En astrología se asocia con la manera de empezar algo y presentarte ante los demás.','¿Cómo das el primer paso ante algo desconocido?'),
 ('Mercurio','Comunicación, aprendizaje y manera de organizar ideas.','¿Cómo te resulta más fácil aprender y explicar algo?'),
 ('Venus','Afectos, gustos y aquello que valoras en tus vínculos.','¿Qué valoras al compartir tiempo con alguien?'),
 ('Marte','Iniciativa, deseo, acción y manera de afrontar conflictos.','¿Cómo actúas cuando quieres conseguir algo o poner un límite?')
]
def create_pdf(result, *, synthetic=False):
    stream=BytesIO();c=Canvas(stream,pagesize=A4,pageCompression=1)
    c.setTitle('Tu carta natal | TRACE ASTRA');c.setAuthor('TRACE ASTRA')
    width,height=A4
    aspects=result.get('aspects',[])
    total=3+max(1,(len(aspects)+19)//20)
    def text(x,y,value,size=11,font='Helvetica',color=INK):
        c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,str(value))
    def para(value,x,y,w=499,size=11,color=INK):
        p=Paragraph(escape(str(value)),ParagraphStyle('body',fontName='Helvetica',fontSize=size,leading=size*1.45,textColor=color))
        _,h=p.wrap(w,800);p.drawOn(c,x,y-h);return y-h
    def page(number,kicker,title):
        c.setFillColor(PAPER);c.rect(0,0,width,height,fill=1,stroke=0)
        text(48,799,'TRACE ASTRA',11,color=BLUE);text(48,752,kicker,9,color=BLUE)
        text(48,712,title,32,'Times-Roman')
        text(48,34,'Copia personal'+(' · EJEMPLO FICTICIO' if synthetic else '')+' · Sin IA',9)
        text(width-76,34,str(number)+' / '+str(total),9)
    def degree(p):return p['sign']+' '+format(p['degree_in_sign'],'.2f')+'°'
    page(1,'TU CIELO, UN PUNTO DE PARTIDA','Tu carta natal')
    birth=result['birth']
    para(birth['local_datetime'].replace('T',' · ')+' · '+birth['timezone'],48,679,size=10)
    para('Latitud '+str(birth['latitude'])+' · Longitud '+str(birth['longitude'])+' · Casas: '+result['conventions']['houses'],48,657,size=10)
    asc=result['ascendant']['longitude_deg'];cx=width/2;cy=403
    def xy(deg,r):
        a=radians(180-deg+asc);return cx+r*cos(a),cy+r*sin(a)
    c.setStrokeColor(HexColor('#a4b4bf'));c.setLineWidth(.6)
    for radius in (198,166,116):c.circle(cx,cy,radius,stroke=1,fill=0)
    for i in range(12):
        x1,y1=xy(i*30,166);x2,y2=xy(i*30,198);c.line(x1,y1,x2,y2)
        deg=i*30+15
        x,y=xy(deg,182)
        rotation=(180-deg+asc+90)%360
        if 90<rotation<270:rotation=(rotation+180)%360
        c.saveState();c.translate(x,y);c.rotate(rotation)
        c.setFillColor(BLUE);c.setFont('Helvetica',9.5)
        c.drawCentredString(0,-3,SIGNS[i]);c.restoreState()
    for i,p in enumerate(result['cusps']):
        x,y=xy(p['longitude_deg'],166);x0,y0=xy(p['longitude_deg'],28);c.line(x0,y0,x,y)
        nextdeg=result['cusps'][(i+1)%12]['longitude_deg']
        x,y=xy(p['longitude_deg']+(nextdeg-p['longitude_deg'])%360/2,87)
        text(x-3,y-3,i+1,8)
    for a in aspects:
        pa=next(p for p in result['planets'] if p['id']==a['body_a'])
        pb=next(p for p in result['planets'] if p['id']==a['body_b'])
        x1,y1=xy(pa['longitude_deg'],116);x2,y2=xy(pb['longitude_deg'],116)
        c.setStrokeColor(HexColor(a['color']));c.setLineWidth(.8)
        c.setDash([float(x) for x in a['dash'].split()] if a['dash'] else [])
        c.line(x1,y1,x2,y2)
    c.setDash([])
    placed=[]
    for i,p in enumerate(result['planets']):
        deg=p['longitude_deg'];r=147
        while any(abs((deg-d+180)%360-180)<10 and abs(r-pr)<15 for d,pr in placed):r-=17
        placed.append((deg,r));x,y=xy(deg,r);dx,dy=xy(deg,166)
        c.setStrokeColor(BLUE);c.line(x,y,dx,dy)
        c.setFillColor(PAPER);c.circle(x,y,8,fill=1,stroke=0)
        text(x-(5 if i==9 else 2.5),y-3,i+1,9,color=BLUE)
    for label,deg in [('ASC',asc),('MC',result['midheaven']['longitude_deg'])]:
        x,y=xy(deg,216);text(x-10,y-3,label,9,color=BLUE)
    for i,(label,p) in enumerate([('SOL',result['planets'][0]),('LUNA',result['planets'][1]),('ASCENDENTE',result['ascendant'])]):
        x=48+i*168;text(x,147,label,9,color=BLUE);text(x,121,p['sign'],21,'Times-Roman')
    para('Los números identifican los cuerpos de la tabla de la página 2. ASC = ascendente; MC = medio cielo. Las líneas conectan posiciones: no indican causas ni predicen hechos.',48,88,size=9)
    c.showPage()
    page(2,'LAS POSICIONES Y EL MÉTODO','El mapa en detalle')
    y=675
    for i,p in enumerate(result['planets']):
        text(48,y,str(i+1)+'. '+p['name']+(' · R' if p['retrograde'] else ''),11)
        text(285,y,degree(p)+' · Casa '+str(p.get('house','-')),11);y-=24
    text(48,402,'Las doce casas',23,'Times-Roman')
    for i,p in enumerate(result['cusps']):
        col=i//6;row=i%6;x=48+col*257
        text(x,373-row*23,'Casa '+str(p['house']),10);text(x+64,373-row*23,degree(p),10)
    para('Ascendente: '+degree(result['ascendant'])+' · Medio cielo: '+degree(result['midheaven']),48,211,size=10)
    para('R indica movimiento retrógrado aparente. Los signos son sectores de 30° del zodiaco tropical. Las casas dependen del sistema elegido; las casas planetarias usan longitud entre cúspides, sin latitud planetaria.',48,181,size=10)
    para(result['conventions']['provider']+' · '+result['conventions']['backend']+'. '+result['conventions']['time']+'. '+result['conventions']['validation']+'.',48,128,size=9)
    para('Motor: '+result['version']+' · Guía editorial: natal-pdf-0.1. Datos de nacimiento incluidos: conserva esta copia en un lugar privado.',48,79,size=9)
    c.showPage()
    page(3,'UNA GUÍA PARA EXPLORAR','Los elementos, en palabras simples')
    para('Estos son los temas que la astrología asocia con cada elemento. Son asociaciones culturales, no conclusiones del cálculo ni descripciones comprobadas de tu personalidad.',48,675,size=10)
    y=616
    for label,copy,question in GUIDE:
        text(48,y,label,19,'Times-Roman',BLUE)
        y=para(copy,48,y-12,size=10)
        y=para(question,48,y-7,size=10,color=BLUE)-25
    for chunk in range(max(1,(len(aspects)+19)//20)):
        c.showPage();page(4+chunk,'CONEXIONES ENTRE PLANETAS','Los aspectos mayores')
        para('El orbe mide cuánto se aparta la separación del ángulo exacto. No expresa probabilidad ni fuerza predictiva. Se calculan pares de los diez cuerpos, sin aspectos a los ángulos.',48,677,size=10)
        y=610
        for a in aspects[chunk*20:(chunk+1)*20]:
            text(48,y,a['name_a']+' / '+a['name_b'],10)
            text(245,y,a['name'],10,color=HexColor(a['color']))
            text(360,y,str(a['angle'])+'°',10)
            text(416,y,'Orbe '+format(a['orb_deg'],'.2f')+'°',10);y-=22
        if not aspects:para('No se encontraron aspectos dentro de los márgenes elegidos.',48,y)
        para('Márgenes: conjunción 8°, sextil 4°, cuadratura 6°, trígono 6°, oposición 8°. Convención editorial TRACE 0.1. Conjunción: violeta punteado; sextil: verde punteado; cuadratura: rojo discontinuo; trígono: azul continuo; oposición: rojo continuo.',48,128,size=9)
    c.save()
    return stream.getvalue()

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    parser=argparse.ArgumentParser();parser.add_argument('record');parser.add_argument('output');parser.add_argument('--synthetic',action='store_true')
    a=parser.parse_args();Path(a.output).write_bytes(create_pdf(json.loads(Path(a.record).read_text()),synthetic=a.synthetic))
