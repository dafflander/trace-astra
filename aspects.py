"""Explicit editorial aspect settings, not a predictive model."""
from itertools import combinations
import math
ASPECTS=[
 {'id':'conjunction','name':'Conjunción','angle':0,'orb':8,'color':'#75618b','dash':'2 3'},
 {'id':'sextile','name':'Sextil','angle':60,'orb':4,'color':'#427d80','dash':'3 3'},
 {'id':'square','name':'Cuadratura','angle':90,'orb':6,'color':'#a55349','dash':'5 3'},
 {'id':'trine','name':'Trígono','angle':120,'orb':6,'color':'#346b96','dash':''},
 {'id':'opposition','name':'Oposición','angle':180,'orb':8,'color':'#a55349','dash':''},
]
def major_aspects(planets):
    found=[]
    for a,b in combinations(planets,2):
        for p in (a,b):
            if not math.isfinite(p['longitude_deg']):raise ValueError('Nonfinite longitude')
        separation=abs((a['longitude_deg']-b['longitude_deg']+180)%360-180)
        for rule in ASPECTS:
            orb=abs(separation-rule['angle'])
            if orb<=rule['orb']:
                found.append({'body_a':a['id'],'body_b':b['id'],'name_a':a['name'],'name_b':b['name'],
                              'separation_deg':separation,'orb_deg':orb,**rule})
    return found

def house_by_longitude(longitude,cusps):
    """2D ecliptic cusp membership; ignores planetary latitude."""
    for i,start in enumerate(cusps):
        span=(cusps[(i+1)%12]-start)%360
        if (longitude-start)%360 < span:return i+1
    raise ValueError('Invalid house cusps')
