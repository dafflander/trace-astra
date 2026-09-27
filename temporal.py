"""Window detection for a continuous orb function, independent of ephemeris provider.

Discovery uses a finite grid. Refinement precision does not guarantee discovery of
contacts shorter than the grid step or physical accuracy of the underlying model.
"""
from datetime import timedelta


def _boundary(fn, left, right, threshold, tolerance):
    left_inside = fn(left) <= threshold
    if left_inside == (fn(right) <= threshold):
        raise ValueError('Boundary must be bracketed.')
    while (right-left).total_seconds() > tolerance:
        mid = left+(right-left)/2
        if (fn(mid) <= threshold) == left_inside:
            left = mid
        else:
            right = mid
    return left+(right-left)/2


def _minimum(fn, left, right, tolerance):
    # Applied only to a local valley bracket, not to a whole retrograde window.
    ratio = (5**0.5-1)/2
    c = right-(right-left)*ratio
    d = left+(right-left)*ratio
    fc, fd = fn(c), fn(d)
    while (right-left).total_seconds() > tolerance:
        if fc < fd:
            right, d, fd = d, c, fc
            c = right-(right-left)*ratio
            fc = fn(c)
        else:
            left, c, fc = c, d, fd
            d = left+(right-left)*ratio
            fd = fn(d)
    point = left+(right-left)/2
    return point, fn(point)


def find_windows(fn, start, end, threshold=1.0, step_hours=6, tolerance_seconds=1):
    if end < start or not 0 < step_hours <= 24 or threshold <= 0 or tolerance_seconds <= 0:
        raise ValueError('Invalid temporal scan configuration.')
    grid = [start]
    while grid[-1] < end:
        grid.append(min(end, grid[-1]+timedelta(hours=step_hours)))
    values = [fn(t) for t in grid]
    windows = []
    i = 0
    while i < len(grid):
        if values[i] > threshold:
            i += 1
            continue
        first = i
        while i+1 < len(grid) and values[i+1] <= threshold:
            i += 1
        last = i
        entry = grid[first] if first == 0 else _boundary(fn, grid[first-1], grid[first], threshold, tolerance_seconds)
        exit = grid[last] if last == len(grid)-1 else _boundary(fn, grid[last], grid[last+1], threshold, tolerance_seconds)
        points = sorted(set([entry, *grid[first:last+1], exit]))
        orbs = [fn(t) for t in points]
        minima = []
        for j in range(1, len(points)-1):
            if orbs[j] <= orbs[j-1] and orbs[j] <= orbs[j+1] and (orbs[j] < orbs[j-1] or orbs[j] < orbs[j+1]):
                minima.append(_minimum(fn, points[j-1], points[j+1], tolerance_seconds))
        candidates = [*zip(points, orbs), *minima]
        best = min(candidates, key=lambda pair:(pair[1],pair[0]))
        windows.append({'entry_utc':entry.isoformat(), 'exit_utc':exit.isoformat(),
                        'entry_clipped':first == 0, 'exit_clipped':last == len(grid)-1,
                        'closest_utc':best[0].isoformat(), 'minimum_orb_deg':best[1],
                        'local_minima':[{'utc':t.isoformat(),'orb_deg':orb} for t,orb in minima],
                        'discovery_step_hours':step_hours,
                        'refinement_tolerance_seconds':tolerance_seconds})
        i += 1
    return windows
