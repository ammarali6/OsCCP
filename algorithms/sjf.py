# Shortest Job First (SJF) Scheduling Algorithm
# ─────────────────────────────────────────────
#  MLFQ - Multilevel Feedback Queue
#  3 Queues:
#    Q0 → Round Robin (quantum = q0, default 2)
#    Q1 → Round Robin (quantum = q1, default 4)
#    Q2 → FCFS (runs to completion)
#  Process moves DOWN a queue if it uses full quantum
# ─────────────────────────────────────────────

def run_mlfq(processes, q0=2, q1=4):
    """
    MLFQ Scheduling with 3 levels.
    New processes enter Q0 (highest priority).
    If a process uses its full quantum, it moves to next lower queue.
    Q2 is FCFS — process runs until completion.
    Args:
        processes: list of dicts with keys: pid, arrival, burst, priority, color
        q0: quantum for Queue 0
        q1: quantum for Queue 1
    Returns:
        result, gantt
    """
    procs = [p.copy() for p in processes]
    for p in procs:
        p['remaining'] = p['burst']
        p['level']     = 0          # starts in Q0
        p['start']     = -1

    # 3 queues
    queues = [[], [], []]
    gantt  = []
    done   = []

    time_now     = 0
    procs_sorted = sorted(procs, key=lambda x: x['arrival'])
    idx          = 0

    def add_new_arrivals():
        """Add processes that have arrived by time_now into Q0."""
        nonlocal idx
        while idx < len(procs_sorted) and procs_sorted[idx]['arrival'] <= time_now:
            queues[0].append(procs_sorted[idx])
            idx += 1

    add_new_arrivals()

    while any(queues) or idx < len(procs_sorted):
        # CPU idle — nothing in any queue
        if not any(queues):
            time_now = procs_sorted[idx]['arrival']
            add_new_arrivals()

        # Check queues from highest to lowest priority
        for level in range(3):
            if not queues[level]:
                continue

            p = queues[level].pop(0)

            # Record first CPU time
            if p['start'] == -1:
                p['start'] = time_now

            # Determine quantum for this level
            if level == 0:
                quantum = q0
            elif level == 1:
                quantum = q1
            else:
                quantum = p['remaining']   # Q2 = FCFS, run to completion

            run_time = min(quantum, p['remaining'])

            gantt.append({
                'pid':   p['pid'],
                'start': time_now,
                'end':   time_now + run_time,
                'color': p['color'],
                'level': level              # useful for reporting
            })

            time_now       += run_time
            p['remaining'] -= run_time

            # Add newly arrived processes to Q0
            add_new_arrivals()

            if p['remaining'] > 0:
                # Used full quantum → demote to next lower queue
                next_level  = min(level + 1, 2)
                p['level']  = next_level
                queues[next_level].append(p)
            else:
                # Finished
                p['finish']     = time_now
                p['turnaround'] = p['finish'] - p['arrival']
                p['waiting']    = p['turnaround'] - p['burst']
                done.append(p)

            break   # restart from Q0 after every time slice

    return done, gantt