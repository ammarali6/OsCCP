"""
Headless Simulation Runner for OS Scheduler.
Runs scheduling algorithms and memory management without GUI.
Outputs metrics, charts, and logs to files.
"""

import json
import os
from datetime import datetime

from algorithms import fcfs, sjf, priority, round_robin, mlfq
from metrics import MetricsCalculator
from memory import VariablePartitionMemory
from memory.visualizer import MemoryVisualizer
from gui.gantt import GanttChart


def run_headless_simulation(algorithm, processes, memory_total=512,
                           memory_algo='first_fit', output_dir='output',
                           quantum=2):
    """
    Run a headless scheduling simulation with memory constraints.

    Args:
        algorithm: str — 'fcfs', 'sjf', 'priority', 'round_robin', 'mlfq'
        processes: list of dicts with keys: pid, arrival, burst, priority, color, memory_req
        memory_total: int — total memory size in abstract units
        memory_algo: str — 'first_fit', 'best_fit', 'worst_fit'
        output_dir: str — directory to save output files
        quantum: int — time quantum for RR/MLFQ

    Returns:
        dict with results, metrics, memory_state, and output file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize memory manager
    mem = VariablePartitionMemory(total_size=memory_total, algorithm=memory_algo)

    # Add memory constraint fields to processes
    procs = [p.copy() for p in processes]
    for p in procs:
        if 'memory_req' not in p:
            p['memory_req'] = 64  # default
        p['memory_allocated'] = False
        p['memory_wait'] = 0

    # Run scheduling with memory constraints
    result, gantt, memory_log = run_with_memory_constraints(
        algorithm, procs, mem, quantum
    )

    # Calculate metrics only for processes that got CPU time
    completed_processes = [p for p in result if p.get('memory_allocated')]
    if not completed_processes:
        completed_processes = result  # fallback if all allocated
    calc = MetricsCalculator(completed_processes)
    metrics = calc.get_all_metrics()

    # Add memory-specific metrics
    metrics['memory'] = {
        'total': memory_total,
        'algorithm': memory_algo,
        'utilization': round(mem.get_utilization(), 2),
        'free_memory': mem.get_free_memory(),
        'used_memory': mem.get_used_memory(),
        'external_fragmentation': mem.get_fragmentation()[0],
    }

    # Generate memory wait times
    memory_waits = [
        {'pid': p['pid'], 'memory_wait': p.get('memory_wait', 0)}
        for p in result
    ]
    avg_memory_wait = round(
        sum(p.get('memory_wait', 0) for p in result) / len(result), 2
    ) if result else 0
    metrics['memory']['avg_memory_wait'] = avg_memory_wait
    metrics['memory']['per_process_wait'] = memory_waits

    # Save metrics to JSON
    metrics_file = os.path.join(output_dir, f"metrics_{algorithm}_{timestamp}.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Save Gantt chart
    gantt_file = os.path.join(output_dir, f"gantt_{algorithm}_{timestamp}.png")
    try:
        chart = GanttChart(f"{algorithm.upper()} - Gantt Chart")
        chart.add_processes(gantt)
        chart.render(save_path=gantt_file)
    except Exception as e:
        print(f"Warning: Could not save Gantt chart: {e}")
        gantt_file = None

    # Save memory visualization
    mem_file = os.path.join(output_dir, f"memory_{algorithm}_{timestamp}.png")
    try:
        viz = MemoryVisualizer(f"Memory Allocation - {algorithm.upper()}")
        viz.plot_partitions(
            mem.get_block_state(),
            total_size=memory_total,
            save_path=mem_file
        )
    except Exception as e:
        print(f"Warning: Could not save memory visualization: {e}")
        mem_file = None

    # Save process details
    details_file = os.path.join(output_dir, f"details_{algorithm}_{timestamp}.txt")
    with open(details_file, 'w') as f:
        f.write(calc.get_summary_report())
        f.write(f"\n\nMemory Algorithm: {memory_algo}\n")
        f.write(f"Memory Utilization: {metrics['memory']['utilization']}%\n")
        f.write(f"Avg Memory Wait: {avg_memory_wait} units\n")
        f.write("\nProcess Memory Details:\n")
        for p in result:
            f.write(f"  {p['pid']}: req={p.get('memory_req', 0)}, "
                   f"allocated={'Yes' if p.get('memory_allocated') else 'No'}, "
                   f"mem_wait={p.get('memory_wait', 0)}\n")

    return {
        'result': result,
        'gantt': gantt,
        'metrics': metrics,
        'memory_state': mem.get_block_state(),
        'files': {
            'metrics': metrics_file,
            'gantt': gantt_file,
            'memory': mem_file,
            'details': details_file,
        }
    }


def run_with_memory_constraints(algorithm, processes, memory_manager, quantum=2):
    """
    Run scheduling algorithm respecting memory constraints.
    Processes must have memory allocated before running.
    If allocation fails, process waits (memory_wait increments).

    Returns:
        result, gantt, memory_log
    """
    # This is a simplified wrapper that pre-allocates memory before
    # running the standard algorithm, tracking memory wait times.
    # For a fully integrated approach, we'd modify each algorithm loop.

    # Sort by arrival to simulate allocation attempts over time
    procs_sorted = sorted(processes, key=lambda x: x['arrival'])
    time_now = 0
    pending = []  # processes waiting for memory
    ready = []     # processes with memory allocated
    done = []
    gantt = []
    memory_log = []

    # Pre-allocate memory as processes arrive
    for p in procs_sorted:
        allocated = memory_manager.allocate(p['pid'], p['memory_req'])
        if allocated:
            p['memory_allocated'] = True
            ready.append(p)
        else:
            pending.append(p)

    # Try to allocate pending processes as others complete
    # For simplicity, we'll run the algorithm on ready processes first,
    # then try to allocate pending ones after each process finishes.
    # A more accurate simulation would interleave allocation attempts.

    # Run the selected algorithm on ready processes
    if not ready:
        return [], [], memory_log

    if algorithm == 'fcfs':
        result, gantt = fcfs.run_fcfs(ready)
    elif algorithm == 'sjf':
        result, gantt = sjf.run_sjf_non_preemptive(ready)
    elif algorithm == 'priority':
        result, gantt = priority.run_priority(ready)
    elif algorithm == 'round_robin':
        result, gantt = round_robin.run_round_robin(ready, quantum=quantum)
    elif algorithm == 'mlfq':
        result, gantt = mlfq.run_mlfq(ready, q0=quantum, q1=quantum*2)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    # Try to allocate pending processes after main run
    # In a real system, this would happen dynamically
    for p in pending:
        allocated = memory_manager.allocate(p['pid'], p['memory_req'])
        if allocated:
            p['memory_allocated'] = True
            p['memory_wait'] = max(0, time_now - p['arrival'])
            ready.append(p)
        else:
            p['memory_wait'] = max(0, time_now - p['arrival'])

    # If any pending processes got allocated, run them too
    newly_ready = [p for p in pending if p['memory_allocated']]
    if newly_ready:
        pending = [p for p in pending if not p['memory_allocated']]
        if algorithm == 'fcfs':
            nr_result, nr_gantt = fcfs.run_fcfs(newly_ready)
        elif algorithm == 'sjf':
            nr_result, nr_gantt = sjf.run_sjf_non_preemptive(newly_ready)
        elif algorithm == 'priority':
            nr_result, nr_gantt = priority.run_priority(newly_ready)
        elif algorithm == 'round_robin':
            nr_result, nr_gantt = round_robin.run_round_robin(newly_ready, quantum=quantum)
        elif algorithm == 'mlfq':
            nr_result, nr_gantt = mlfq.run_mlfq(newly_ready, q0=quantum, q1=quantum*2)

        result.extend(nr_result)
        gantt.extend(nr_gantt)

    # Mark unallocated processes
    for p in pending:
        p['memory_allocated'] = False
        p['memory_wait'] = max(0, time_now - p['arrival'])
        # Set defaults for metrics calculation
        if 'start' not in p or p.get('start', -1) == -1:
            p['start'] = p['arrival']
        if 'finish' not in p or p.get('finish', 0) == 0:
            p['finish'] = p['arrival']
        if 'waiting' not in p:
            p['waiting'] = 0
        if 'turnaround' not in p:
            p['turnaround'] = 0
        result.append(p)

    return result, gantt, memory_log


# Preset workloads for quick testing
PRESET_WORKLOADS = {
    'simple': [
        {'pid': 'P1', 'arrival': 0, 'burst': 8, 'priority': 1, 'color': '#FF6B6B', 'memory_req': 128},
        {'pid': 'P2', 'arrival': 1, 'burst': 4, 'priority': 2, 'color': '#4ECDC4', 'memory_req': 64},
        {'pid': 'P3', 'arrival': 2, 'burst': 2, 'priority': 1, 'color': '#45B7D1', 'memory_req': 32},
        {'pid': 'P4', 'arrival': 3, 'burst': 1, 'priority': 3, 'color': '#FFA07A', 'memory_req': 16},
    ],
    'memory_stress': [
        {'pid': 'P1', 'arrival': 0, 'burst': 10, 'priority': 1, 'color': '#FF6B6B', 'memory_req': 256},
        {'pid': 'P2', 'arrival': 1, 'burst': 5, 'priority': 2, 'color': '#4ECDC4', 'memory_req': 128},
        {'pid': 'P3', 'arrival': 2, 'burst': 8, 'priority': 1, 'color': '#45B7D1', 'memory_req': 200},
        {'pid': 'P4', 'arrival': 3, 'burst': 3, 'priority': 3, 'color': '#FFA07A', 'memory_req': 64},
        {'pid': 'P5', 'arrival': 4, 'burst': 6, 'priority': 2, 'color': '#98D8C8', 'memory_req': 180},
    ],
    'mixed': [
        {'pid': 'P1', 'arrival': 0, 'burst': 15, 'priority': 2, 'color': '#FF6B6B', 'memory_req': 100},
        {'pid': 'P2', 'arrival': 2, 'burst': 3, 'priority': 1, 'color': '#4ECDC4', 'memory_req': 50},
        {'pid': 'P3', 'arrival': 5, 'burst': 7, 'priority': 3, 'color': '#45B7D1', 'memory_req': 80},
        {'pid': 'P4', 'arrival': 8, 'burst': 2, 'priority': 1, 'color': '#FFA07A', 'memory_req': 30},
        {'pid': 'P5', 'arrival': 10, 'burst': 5, 'priority': 2, 'color': '#98D8C8', 'memory_req': 60},
        {'pid': 'P6', 'arrival': 12, 'burst': 4, 'priority': 4, 'color': '#F7DC6F', 'memory_req': 40},
    ],
}
