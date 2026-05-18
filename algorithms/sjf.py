# Shortest Job First (SJF) Scheduling Algorithm
# ─────────────────────────────────────────────
#  SJF - Shortest Job First
#  Both Preemptive (SRTF) and Non-Preemptive
# ─────────────────────────────────────────────

def run_sjf_non_preemptive(processes):
    """
    SJF Non-Preemptive Scheduling.
    At each decision point, pick the available process with shortest burst time.
    Args:
        processes: list of dicts with keys: pid, arrival, burst, priority, color
    Returns:
        result, gantt
    """
    procs    = [p.copy() for p in processes]
    done     = []
    gantt    = []
    result   = []
    time_now = 0

    while len(done) < len(procs):
        # Processes that have arrived and not yet done
        available = [p for p in procs if p['arrival'] <= time_now and p['pid'] not in done]

        if not available:
            time_now += 1
            continue

        # Pick shortest burst
        p = min(available, key=lambda x: x['burst'])

        p['start']      = time_now
        p['finish']     = time_now + p['burst']
        p['waiting']    = p['start'] - p['arrival']
        p['turnaround'] = p['finish'] - p['arrival']

        gantt.append({
            'pid':   p['pid'],
            'start': p['start'],
            'end':   p['finish'],
            'color': p['color']
        })

        time_now = p['finish']
        done.append(p['pid'])
        result.append(p)

    return result, gantt


def run_sjf_preemptive(processes):
    """
    SJF Preemptive (SRTF - Shortest Remaining Time First).
    At every time unit, the process with shortest remaining time runs.
    Args:
        processes: list of dicts with keys: pid, arrival, burst, priority, color
    Returns:
        result, gantt
    """
    procs = [p.copy() for p in processes]
    for p in procs:
        p['remaining'] = p['burst']
        p['start']     = -1

    gantt    = []
    done     = []
    time_now = 0
    last_pid = None
    seg_start = 0

    while len(done) < len(procs):
        available = [p for p in procs if p['arrival'] <= time_now and p['pid'] not in done]

        if not available:
            time_now += 1
            continue

        p = min(available, key=lambda x: x['remaining'])

        # Record first start
        if p['start'] == -1:
            p['start'] = time_now

        # New segment starts when process changes
        if last_pid != p['pid']:
            if last_pid is not None:
                prev = next(x for x in procs if x['pid'] == last_pid)
                gantt.append({
                    'pid':   last_pid,
                    'start': seg_start,
                    'end':   time_now,
                    'color': prev['color']
                })
            seg_start = time_now
            last_pid  = p['pid']

        p['remaining'] -= 1
        time_now       += 1

        if p['remaining'] == 0:
            p['finish']     = time_now
            p['turnaround'] = p['finish'] - p['arrival']
            p['waiting']    = p['turnaround'] - p['burst']
            done.append(p['pid'])
            gantt.append({
                'pid':   p['pid'],
                'start': seg_start,
                'end':   time_now,
                'color': p['color']
            })
            last_pid = None

    result = [p for p in procs if p['pid'] in done]
    return result, gantt
