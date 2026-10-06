"""Bounded astronomical scans, not forecasts chosen from user answers."""
from datetime import date,datetime,timedelta
from research_reading import calculate_research_reading
from timeline_selection import select_timeline

def intervals(profile,kind,anchor):
    if kind not in ('past','future'):raise ValueError('Invalid milestone kind')
    today=date.fromisoformat(anchor)
    if not 1900<=today.year<=2099:raise ValueError('Unsupported anchor')
    birth=datetime.fromisoformat(profile['utc']).date()+timedelta(days=1)
    if birth>=today:raise ValueError('Necesitamos una fecha de nacimiento anterior a hoy.')
    if kind=='future':
        return [(today+timedelta(days=a),today+timedelta(days=b)) for a,b in [(0,90),(90,180),(180,270),(270,365)]]
    span=min((today-birth).days,4380)
    # Geometrically spaced look-back bands: near-present coverage is denser.
    edges=sorted(set([0,max(1,round(span/64)),max(2,round(span/16)),max(3,round(span/4)),span]))
    windows=[]
    for low,high in zip(edges,edges[1:]):
        if high>span:continue
        middle=(low+high)//2;width=min(120,high-low)
        a=max(birth,today-timedelta(days=middle+width//2));b=min(today-timedelta(days=low),a+timedelta(days=width))
        if a<b:windows.append((a,b))
    return sorted(windows)

def calculate_milestones(profile,kind,anchor):
    scans=intervals(profile,kind,anchor);cards=[];families=set();candidates=0;contexts={}
    for a,b in scans:
        record=calculate_research_reading(profile,a.isoformat(),b.isoformat())
        for context in record['timeline'].get('long_term_context',[]):
            key=(context['system'],context['start_utc'],context['end_utc'])
            contexts.setdefault(key,context)
        western=record['western'];candidates+=len(western['candidates'])
        western={**western,'candidates':[c for c in western['candidates'] if c['rule']['event_family'] not in families]}
        picked=select_timeline(western,a.isoformat(),b.isoformat(),max_cards=1)['cards']
        if picked:cards.extend(picked);families.add(picked[0]['detail']['rule']['event_family'])
    return {'cards':cards,'policy':{'version':'milestones-1','max_cards':4,'method':'bounded_geometric_past_quarterly_future'},'candidate_count':candidates,'long_term_context':list(contexts.values()),
            'scanned_intervals':[[a.isoformat(),b.isoformat()] for a,b in scans],
            'notice':'Se exploran intervalos acotados, no cada día de toda tu vida. Las fechas del cálculo se conservan; una ventana sin candidatos queda vacía.'}
