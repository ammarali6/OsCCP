import json
import os
from datetime import datetime

from algorithms import fcfs, sjf, priority, round_robin, mlfq
from metrics import MetricsCalculator
from .workloads import WORKLOAD_TYPES

ALGORITHMS = {
    "fcfs": ("FCFS", lambda p: fcfs.run_fcfs(p)),
    "sjf": ("SJF (NP)", lambda p: sjf.run_sjf_non_preemptive(p)),
    "priority": ("Priority", lambda p: priority.run_priority(p)),
    "round_robin": ("Round Robin", lambda p: round_robin.run_round_robin(p, quantum=2)),
    "mlfq": ("MLFQ", lambda p: mlfq.run_mlfq(p, q0=2, q1=4)),
}


def run_single_experiment(workload_name, processes, algorithm_key, algo_func):
    procs = [p.copy() for p in processes]
    for p in procs:
        if "memory_req" not in p:
            p["memory_req"] = 64

    result, gantt = algo_func(procs)
    calc = MetricsCalculator(result)
    metrics = calc.get_all_metrics()

    # Apply I/O simulation: add io_burst as post-CPU I/O wait time
    io_total = 0
    for p in result:
        io = p.get("io_burst", 0)
        io_total += io

    # Track I/O totals in metrics
    metrics["io"] = {
        "total_io_time": io_total,
        "avg_io_per_process": round(io_total / len(result), 2) if result else 0,
    }

    return {
        "algorithm": algorithm_key,
        "algorithm_name": ALGORITHMS[algorithm_key][0],
        "workload": workload_name,
        "metrics": metrics,
        "gantt": gantt,
    }


def run_all_experiments(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_results = {}

    for workload_name, processes in WORKLOAD_TYPES.items():
        workload_results = []
        for algo_key, (algo_name, algo_func) in ALGORITHMS.items():
            exp = run_single_experiment(workload_name, processes, algo_key, algo_func)
            workload_results.append(exp)
        all_results[workload_name] = workload_results

    filepath = os.path.join(output_dir, f"experiments_{timestamp}.json")
    with open(filepath, "w") as f:
        json.dump(all_results, f, indent=2)

    return all_results, filepath
