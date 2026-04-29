# Priority Scheduling Algorithm
# ─────────────────────────────────────────────
#  Priority Scheduling
#  Non-Preemptive (lower number = higher priority)
# ─────────────────────────────────────────────

def run_priority(processes):
    """
    Priority Scheduling (Non-Preemptive).
    At each decision point, pick the available process with lowest priority number.
    Lower priority number = Higher priority (e.g., priority 1 runs before priority 5).
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

        # Pick highest priority (lowest number)
        p = min(available, key=lambda x: x['priority'])

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