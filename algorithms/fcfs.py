# ─────────────────────────────────────────────
#  FCFS - First Come First Served
#  Non-Preemptive only
# ─────────────────────────────────────────────

def run_fcfs(processes):
    """
    FCFS Scheduling Algorithm.
    Processes are executed in order of arrival time.
    Args:
        processes: list of dicts with keys: pid, arrival, burst, priority, color
    Returns:
        result: list of processes with added keys: start, finish, waiting, turnaround
        gantt:  list of dicts with keys: pid, start, end, color
    """
    # Sort by arrival time
    procs = sorted([p.copy() for p in processes], key=lambda x: x['arrival'])

    time_now = 0
    gantt    = []
    result   = []

    for p in procs:
        # CPU idle gap — jump to process arrival
        if time_now < p['arrival']:
            time_now = p['arrival']

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
        result.append(p)

    return result, gantt