"""Bounded process-local cache of public grid positions, never birth queries."""
from functools import lru_cache
from datetime import timezone
import swisseph as swe
from engine import position,FLAGS

@lru_cache(maxsize=100000)
def _grid_position(body,utc,swiss_version,flags):
    return position(utc,body)['longitude_deg']

def transit_longitude(utc,body,step_hours):
    utc=utc.astimezone(timezone.utc)
    # Only canonical public grid times enter shared memory. Individual boundary
    # refinements go straight to the calculator, without shared retention.
    if utc.minute==0 and utc.second==0 and utc.microsecond==0 and utc.hour%step_hours==0:
        return _grid_position(body,utc,swe.version,FLAGS)
    return position(utc,body)['longitude_deg']

def cache_info():return _grid_position.cache_info()
def clear_cache():_grid_position.cache_clear()
