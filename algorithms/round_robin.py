# Round Robin Scheduling Algorithm
# ─────────────────────────────────────────────
#  Round Robin Scheduling
#  Preemptive — configurable time quantum
# ─────────────────────────────────────────────

def run_round_robin(processes, quantum=2):
    """
    Round Robin Scheduling.
    Each process gets a fixed time slice (quantum). If not finished, goes back to queue.
    Args:
        processes: list of dicts with keys: pid, arrival, burst, priority, color
        quantum:   int — time slice each process gets per turn
    Returns:
        result, gantt
    """
    procs = [p.copy() for p in processes]
    for p in procs:
        p['remaining'] = p['burst']
        p['start']     = -1

    procs_sorted = sorted(procs, key=lambda x: x['arrival'])

    queue    = []
    done     = []
    gantt    = []
    time_now = 0
    idx      = 0  # pointer into procs_sorted

    # Add processes that arrive at time 0
    while idx < len(procs_sorted) and procs_sorted[idx]['arrival'] <= time_now:
        queue.append(procs_sorted[idx])
        idx += 1

    while queue or idx < len(procs_sorted):
        # CPU idle — jump to next arrival
        if not queue:
            time_now = procs_sorted[idx]['arrival']
            while idx < len(procs_sorted) and procs_sorted[idx]['arrival'] <= time_now:
                queue.append(procs_sorted[idx])
                idx += 1

        p = queue.pop(0)

        # Record first time this process gets CPU
        if p['start'] == -1:
            p['start'] = time_now

        # Run for min(quantum, remaining)
        run_time = min(quantum, p['remaining'])

        gantt.append({
            'pid':   p['pid'],
            'start': time_now,
            'end':   time_now + run_time,
            'color': p['color']
        })

        time_now       += run_time
        p['remaining'] -= run_time

        # Add newly arrived processes to queue
        while idx < len(procs_sorted) and procs_sorted[idx]['arrival'] <= time_now:
            queue.append(procs_sorted[idx])
            idx += 1

        if p['remaining'] > 0:
            # Not done — go back to end of queue
            queue.append(p)
        else:
            # Done
            p['finish']     = time_now
            p['turnaround'] = p['finish'] - p['arrival']
            p['waiting']    = p['turnaround'] - p['burst']
            done.append(p)

    return done, gantt