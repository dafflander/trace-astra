"""Traceable thematic comparisons; never infer a second person's natal chart."""
import json
from pathlib import Path

SOURCE = Path(__file__).parent / 'compatibility_profiles.es.json'
FIELDS = {'Sun': 'goal', 'Moon': 'need', 'Mercury': 'speech', 'Venus': 'affection'}


def load_compatibility():
    return json.loads(SOURCE.read_text())


def link(library, left, right):
    profiles = library['profiles']
    key = '|'.join(sorted([profiles[left]['element'], profiles[right]['element']]))
    return key, library['element_links'][key]


def compatibility_section(positions, sign, library=None):
    library = library if library is not None else load_compatibility()
    profiles = library['profiles']; other = profiles[sign]
    paragraphs = []; refs = []; evidence = []
    for body in FIELDS:
        if body in positions:
            p = positions[body]
            refs.append(f"compat.v{library['version']}.{body}.{p['sign']}.{sign}")
            evidence.append(f"{p['name']} en {p['sign']} · {p['degree_in_sign']:.2f}° / referencia solar de {sign}")
    if 'Sun' in positions:
        own = profiles[positions['Sun']['sign']]
        key, relation = link(library, positions['Sun']['sign'], sign)
        refs.append('compat.elements.' + key)
        paragraphs.append(f"Con {sign}, el tema a explorar es {other['goal']}. " + relation['affinity'])
    if 'Moon' in positions:
        own = profiles[positions['Moon']['sign']]
        key, relation = link(library, positions['Moon']['sign'], sign)
        refs.append('compat.elements.' + key)
        paragraphs.append(f"En lo emocional, al explorar el vínculo con {sign}: " + relation['friction'])
    if 'Venus' in positions:
        own = profiles[positions['Venus']['sign']]
        paragraphs.append(f"Para compartir tiempo con {sign}, una propuesta es {other['practice']}.")
    if 'Mercury' in positions:
        own = profiles[positions['Mercury']['sign']]
        paragraphs.append(f"Al conversar con {sign}, conviene {other['boundary']}. " + link(library, positions['Mercury']['sign'], sign)[1]['bridge'])
    return {'kind': 'compatibility', 'title': 'Compatibilidad con ' + sign,
            'paragraphs': paragraphs, 'rule_ids': list(dict.fromkeys(refs)),
            'evidence': evidence, 'editorial_version': library['version']}


def internal_bridge(positions, library=None):
    """Explain the native's own two themes once, not twelve times."""
    if not all(body in positions for body in ('Sun', 'Moon')):
        return None
    library = library if library is not None else load_compatibility()
    sun, moon = positions['Sun'], positions['Moon']
    profiles = library['profiles']
    key, relation = link(library, sun['sign'], moon['sign'])
    return {'kind': 'natal', 'title': 'Cómo conviven tus objetivos y tus necesidades',
            'evidence': [f"Sol en {sun['sign']}", f"Luna en {moon['sign']}"],
            'rule_ids': [f"compat.internal.{sun['sign']}.{moon['sign']}", 'compat.elements.' + key],
            'paragraphs': [f"La lectura del Sol plantea {profiles[sun['sign']]['goal']}, mientras la Luna introduce la necesidad de {profiles[moon['sign']]['need']}. Son dos dimensiones de tu propia carta, no descripciones de dos personas. " + relation['affinity'], relation['friction'] + ' ' + relation['bridge'],
            'Este cruce relaciona temas por signo; no calcula un aspecto angular ni demuestra un conflicto o una cualidad personal.']}


def compatibility_intro(positions, base, library=None):
    library = library if library is not None else load_compatibility()
    labels = {'Sun': ('Tu Sol', 'goal'), 'Moon': ('Tu Luna', 'need'),
              'Mercury': ('Tu Mercurio', 'speech'), 'Venus': ('Tu Venus', 'affection')}
    descriptions = []
    for body, (label, field) in labels.items():
        if body not in positions:
            continue
        sign = positions[body]['sign']
        descriptions.append(f"{label} en {sign} se asocia con {library['profiles'][sign][field]}.")
    return {**base, 'paragraphs': [*base['paragraphs'],
        'El punto de partida de estas comparaciones es tu propia carta: ' + ' '.join(descriptions),
        'Esta base es común a los doce cruces. A continuación nos centramos en lo que cambia con cada signo; las coincidencias de elemento pueden compartir temas. Son propuestas para conversar, no características atribuidas a alguien que no conocemos.']}
