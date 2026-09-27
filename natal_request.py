"""Validated input boundary for the local natal service."""
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import math
import hashlib
import json
from natal import calculate_natal

class InputError(ValueError):
    def __init__(self, message, field):
        super().__init__(message)
        self.field = field

def calculate_request(body):
    if not isinstance(body, dict):
        raise InputError('El formulario recibido no es válido.', 'form')
    local = body.get('local_datetime')
    try:
        if not isinstance(local, str):
            raise ValueError()
        date = datetime.fromisoformat(local)
        if date.tzinfo is not None or not 1900 <= date.year <= 2100:
            raise ValueError()
    except ValueError:
        raise InputError('Introduce una fecha entre 1900 y 2100 y una hora válida.', 'date')
    zone = body.get('timezone')
    try:
        if not isinstance(zone, str) or not zone:
            raise ValueError()
        ZoneInfo(zone)
    except (ValueError, ZoneInfoNotFoundError):
        raise InputError('Selecciona una ciudad o revisa su zona horaria.', 'timezone')
    for name, limit in [('latitude', 66), ('longitude', 180)]:
        value = body.get(name)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or abs(value) > limit or (name == 'latitude' and abs(value) == 66):
            raise InputError('Revisa la ubicación. Admitimos latitud entre −66° y 66° y longitud entre −180° y 180°.', name)
    if body.get('time_accuracy') != 'recorded':
        raise InputError('Necesitamos la hora registrada para esta versión de la carta.', 'time')
    if 'fold' in body and (type(body['fold']) is not int or body['fold'] not in (0, 1)):
        raise InputError('Elige la primera o segunda ocurrencia de la hora.', 'fold')
    if body.get('house_system', 'P') not in ('P', 'W'):
        raise InputError('Elige uno de los sistemas de casas disponibles.', 'house_system')
    try:
        result=calculate_natal(body, body.get('house_system', 'P'))
        canonical=json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
        result['result_id']=hashlib.sha256(canonical.encode()).hexdigest()
        return result
    except ValueError as exc:
        message = str(exc)
        if 'Ambiguous local time' in message:
            raise InputError('Esa hora ocurrió dos veces por un cambio de horario. Revisa el registro y elige la primera o segunda ocurrencia.', 'fold')
        if 'Nonexistent local time' in message:
            raise InputError('Esa hora no existió en ese lugar por un cambio de horario. Revisa la hora registrada y la ciudad.', 'time')
        raise
