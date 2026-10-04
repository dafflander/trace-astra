"""Local, sequential multi-system research entry point; not a production endpoint."""
from transit_engine import calculate_transits
from timeline_selection import select_timeline
from editorial_reader import temporal_reading,anchor_readings,load_library
from multisystem_reader import calculate_other_systems

def calculate_research_reading(profile,start,end):
    western=calculate_transits(profile,start,end)['record']
    library=load_library()
    candidates=[];partial=[]
    for window in western['astronomical_windows']:
        if window['entry_clipped'] or window['exit_clipped']:
            partial.append(window['window_id'])
        else:
            candidates.append(temporal_reading(window,library))
    others=calculate_other_systems(profile,start+'T00:00:00+00:00',end+'T00:00:00+00:00')
    result = {'version':'trace-research-reading-0.2.0',
            'western':{'candidates':candidates,'partial_window_ids':partial,
                       'overlap_groups':western['overlap_groups'],'natal_context':anchor_readings(western)},
            **others,'probability':None,
            'status':'research_candidates_not_final_forecasts',
            'warning':'No sum of votes across systems. Rule choices are editorial and not validated. Broad periods are not equivalent to brief transits.'}

    result['timeline']=select_timeline(result['western'],start,end)
    result['timeline']['long_term_context']=[*others['jyotisha'],*others['bazi']]
    result['timeline']['bazi_natal']=others['bazi_natal']
    result['timeline']['unavailable']=others['unavailable']
    return result
