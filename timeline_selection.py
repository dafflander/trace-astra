"""Versioned presentation policy, fixed independently of user responses."""
from datetime import datetime

POLICY={'version':'trace-selection-0.1.0','max_cards':4,'max_duration_days':120,
        'min_duration_days':1,'method':'equal_time_bins_nearest_midpoint',
        'notice':'Editorial coverage selection, not predictive strength. No answer-dependent ranking.'}

def select_timeline(western,start,end,max_cards=None):
    limit=max_cards or POLICY['max_cards']
    first=datetime.fromisoformat(start+'T00:00:00+00:00')
    last=datetime.fromisoformat(end+'T00:00:00+00:00')
    if first>=last:raise ValueError('Ordered nonempty interval required')
    candidates=western['candidates'];eligible=[];excluded=[]
    group_ids={wid:i for i,g in enumerate(western['overlap_groups']) for wid in g['window_ids']}
    for c in candidates:
        w=c['evidence'];a=datetime.fromisoformat(w['entry_utc']);b=datetime.fromisoformat(w['exit_utc'])
        duration=(b-a).total_seconds()/86400
        if a<first or b>last or not POLICY['min_duration_days']<=duration<=POLICY['max_duration_days']:
            excluded.append({'content_id':c['content_id'],'reason':'outside_interval_or_duration_policy'});continue
        eligible.append((c,a,b))
    selected=[];used_groups=set();used_events=set()
    span=(last-first)/limit
    for i in range(limit):
        left=first+span*i;right=first+span*(i+1);mid=left+span/2
        options=sorted((x for x in eligible if left<=datetime.fromisoformat(x[0]['evidence']['closest_utc'])<right),
            key=lambda x:(abs((datetime.fromisoformat(x[0]['evidence']['closest_utc'])-mid).total_seconds()),x[0]['content_id']))
        for c,a,b in options:
            group=group_ids.get(c['evidence']['window_id']);event=c['rule']['event_family']
            if group in used_groups or event in used_events:continue
            selected.append({'content_id':c['content_id'],'start_utc':a.isoformat(),'end_utc':b.isoformat(),
                             'title':c['rule']['theme'],'past':'Una posibilidad para contrastar en este período: '+c['rule']['theme']+'. No implica que haya ocurrido.', 'future':'Un tema que podrías observar durante este período: '+c['rule']['theme']+'. Es una posibilidad interpretativa, no un acontecimiento asegurado.',
                             'counts':c['rule']['counts'],'does_not_count':c['rule']['does_not_count'],
                             'evaluate_after_utc':c['evaluate_after_utc'],'detail':c})
            used_groups.add(group);used_events.add(event);break
    picked={c['content_id'] for c in selected}
    return {'policy':{**POLICY,'max_cards':limit},'cards':selected,'candidate_count':len(candidates),
            'omitted_count':len(candidates)-len(selected),'excluded':excluded,
            'remaining_candidate_ids':[c['content_id'] for c in candidates if c['content_id'] not in picked],
            'notice':'Original dates preserved. Missing bins stay empty. Repeated events and overlapping groups are not multiple confirmations.'}
