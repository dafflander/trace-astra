"""Shared editorial cover, drawn locally without external requests."""
from pathlib import Path
from math import cos,sin,pi
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4

def draw_cover(c, result, total, synthetic=False):
    w,h=A4
    paper=HexColor('#f6f3ec');blue=HexColor('#244e70');ink=HexColor('#292d32')
    assets=Path(__file__).parent/'natal-web'
    if not assets.is_dir():assets=Path(__file__).parent
    c.setFillColor(paper);c.rect(0,0,w,h,fill=1,stroke=0)
    c.drawImage(str(assets/'galaxy.jpg'),0,245,width=w,height=397)
    # Fade the photograph into the page so its rectangular edge disappears.
    c.saveState();c.setFillColor(paper)
    for i in range(350):
        c.setFillAlpha(1-i/350);c.rect(0,642-(i+1)*.2,w,.2,fill=1,stroke=0)
        c.rect(0,245+i*.2,w,.2,fill=1,stroke=0)
    c.restoreState()
    def text(x,y,t,size=11,font='Helvetica',color=ink):
        c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,t)
    # Small eight-point compass, matching the web identity.
    p=c.beginPath()
    for i in range(32):
        a=pi/2+i*pi/16;r=18 if i%4==0 else 6
        x=65+cos(a)*r;y=775+sin(a)*r
        if i==0:p.moveTo(x,y)
        else:p.lineTo(x,y)
    p.close();c.setFillColor(blue);c.drawPath(p,fill=1,stroke=0)
    text(96,766,'TraceAstra',28,'Times-Roman',blue)
    text(48,692,'TU CARTA NATAL',10,color=blue)
    text(48,626,'Tu carta',47,'Times-Roman')
    text(48,572,'y tu recorrido.',47,'Times-Roman')
    text(50,530,'Un punto de partida para explorar tu cielo.',12,color=blue)
    c.setStrokeColor(blue);c.setLineWidth(.7)
    p=c.beginPath();p.moveTo(48,300);p.curveTo(300,290,465,360,548,496);c.drawPath(p)
    for t in [.03,.2,.4,.6,.8]:
        u=1-t;x=u**3*48+3*u*u*t*300+3*u*t*t*465+t**3*548
        y=u**3*300+3*u*u*t*290+3*u*t*t*360+t**3*496
        c.setFillColor(paper);c.circle(x,y,3,fill=1,stroke=1)
    for x,y in [(402,446),(511,381),(338,345)]:
        p=c.beginPath();p.moveTo(x,y+7);p.lineTo(x+2,y+2);p.lineTo(x+6,y);p.lineTo(x+2,y-2);p.lineTo(x,y-7);p.lineTo(x-2,y-2);p.lineTo(x-6,y);p.lineTo(x-2,y+2);p.close();c.setFillColor(blue);c.drawPath(p,fill=1,stroke=0)
    positions={p['id']:p for p in result['planets']}
    for i,(label,pos) in enumerate([('Sol',positions['Sun']),('Luna',positions['Moon']),('Ascendente',result['ascendant'])]):
        x=48+i*170;c.setStrokeColor(HexColor('#cbd1d3'));c.line(x,255,x+150,255)
        text(x,232,label,10,color=blue);text(x,203,pos['sign'],23,'Times-Roman')
    text(48,164,'Una lectura para explorar, no una certeza.',10,color=blue)
    text(48,34,'Copia personal'+(' · EJEMPLO FICTICIO' if synthetic else ''),9)
    text(w-76,34,'1 / '+str(total),9)
    c.showPage()
