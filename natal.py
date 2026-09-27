"""Conventional tropical chart, local only. No AI or biographical inference."""
from datetime import datetime
import swisseph as swe
from aspects import ASPECTS, major_aspects, house_by_longitude
from engine import normalize, julian, position, BODIES

SIGNS = ['Aries','Tauro','Géminis','Cáncer','Leo','Virgo','Libra','Escorpio','Sagitario','Capricornio','Acuario','Piscis']
NAMES = dict(zip(BODIES, ['Sol','Luna','Mercurio','Venus','Marte','Júpiter','Saturno','Urano','Neptuno','Plutón']))

def zodiac(longitude):
    value = longitude % 360
    return {'sign': SIGNS[int(value // 30)], 'degree_in_sign': value % 30}

def calculate_natal(profile, system='P'):
    if system not in ('P', 'W'):
        raise ValueError('Elige Placidus o signos enteros.')
    birth = normalize(profile)
    if abs(birth['latitude']) >= 66:
        raise ValueError('Esta primera versión no admite latitudes de 66° o superiores en valor absoluto.')
    utc = datetime.fromisoformat(birth['utc'])
    swe.set_ephe_path('')
    cusps, angles = swe.houses_ex(julian(utc), birth['latitude'], birth['longitude'], system.encode(), 0)
    planets = []
    for key in BODIES:
        p = position(utc, key)
        planets.append({'id':key,'name':NAMES[key],**p,**zodiac(p['longitude_deg']),
                        'house':house_by_longitude(p['longitude_deg'],cusps), 'retrograde':p['longitude_speed_deg_day'] < 0})
    return {'version':'trace-natal-0.2.0','birth':birth,
            'conventions':{'zodiac':'tropical','houses':'Placidus' if system == 'P' else 'Signos enteros',
                           'provider':'Swiss Ephemeris '+swe.version,'backend':'Moshier',
                           'time':'UTC aproximado como UT; sin corrección DUT1',
                           'validation':'Pruebas internas; contraste independiente pendiente'},
            'ascendant':{'longitude_deg':angles[0],**zodiac(angles[0])},
            'midheaven':{'longitude_deg':angles[1],**zodiac(angles[1])},
            'cusps':[{'house':i+1,'longitude_deg':x,**zodiac(x)} for i,x in enumerate(cusps)],
            'planets':planets,'aspects':major_aspects(planets),'aspect_rules':ASPECTS,'house_assignment':'Ecliptic longitude between cusps; planetary latitude ignored'}
