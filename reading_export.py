"""Recalculate only requested completed intervals; never trust client forecast text."""
from datetime import date,datetime,timezone

def export_periods(profile,periods,*,today=None):
    if not isinstance(periods,list) or len(periods)>2:raise ValueError('At most two periods')
    today=today or datetime.now(timezone.utc).date();seen=set();validated=[]
    for p in periods:
        if not isinstance(p,dict) or p.get('kind') not in ('past','future') or p['kind'] in seen:raise ValueError('Invalid period kind')
        seen.add(p['kind'])
        if p.get('status') not in ('ready','unavailable'):raise ValueError('Invalid period status')
        item={'kind':p['kind'],'status':p['status']}
        if item['status']=='ready' and p.get('mode')=='milestones':
            from milestones import intervals
            scans=intervals(profile,item['kind'],p['anchor'])
            if item['kind']=='past' and date.fromisoformat(p['anchor'])>today:raise ValueError('Past anchor in future')
            item.update(mode='milestones',anchor=p['anchor'],start=scans[0][0].isoformat(),end=scans[-1][1].isoformat())
        elif item['status']=='ready':
            a=date.fromisoformat(p['start']);b=date.fromisoformat(p['end'])
            if not 1900<=a.year<=2100 or not 1900<=b.year<=2100 or not 0<(b-a).days<=730:raise ValueError('Unsupported interval')
            # A future interval may now be in the past; preserve the original reading label.
            if item['kind']=='past' and b>today:raise ValueError('Past ends in future')
            item.update(start=a.isoformat(),end=b.isoformat())
        validated.append(item)
    from research_reading import calculate_research_reading
    output=[]
    for p in validated:
        if p['status']=='ready':
            if p.get('mode')=='milestones':
                from milestones import calculate_milestones
                p['timeline']=calculate_milestones(profile,p['kind'],p['anchor'])
            else:p['timeline']=calculate_research_reading(profile,p['start'],p['end'])['timeline']
        output.append(p)
    return output
