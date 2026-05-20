import subprocess
import os

from .runner import run_all_experiments
from headless import run_headless_simulation, PRESET_WORKLOADS


def compare_algorithms(experiment_results):
    comparison = {}
    for workload_name, results in experiment_results.items():
        for r in results:
            key = r["algorithm"]
            if key not in comparison:
                comparison[key] = {
                    "algorithm": r["algorithm_name"],
                    "workloads": {},
                }
            comparison[key]["workloads"][workload_name] = {
                "avg_waiting": r["metrics"]["waiting_time"]["average"],
                "avg_turnaround": r["metrics"]["turnaround_time"]["average"],
                "cpu_util": r["metrics"]["cpu_utilization"],
                "throughput": r["metrics"]["throughput"],
                "total_io": r["metrics"].get("io", {}).get("total_io_time", 0),
            }
    return comparison


def compare_host_vs_docker(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    host_results, _ = run_all_experiments(output_dir)

    try:
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{os.path.abspath(output_dir)}:/app/output",
            "scheduler-sim:latest",
            "python",
            "main.py",
            "--headless",
        ]
        subprocess.run(docker_cmd, capture_output=True, text=True, timeout=60)
        print("Docker execution completed")
    except Exception as e:
        print(f"Docker execution skipped: {e}")
        return {"host": host_results, "docker": None, "error": str(e)}

    return {"host": host_results, "docker": None}


def compare_memory_limits(low=256, high=1024, output_dir="output"):
    low_results = {}
    high_results = {}

    for algo in ["fcfs", "sjf", "priority", "round_robin", "mlfq"]:
        procs = [p.copy() for p in PRESET_WORKLOADS["mixed"]]
        low_res = run_headless_simulation(
            algo, procs, memory_total=low, output_dir=output_dir
        )
        high_res = run_headless_simulation(
            algo, procs, memory_total=high, output_dir=output_dir
        )
        low_results[algo] = low_res["metrics"]
        high_results[algo] = high_res["metrics"]

    return {"low_memory": low_results, "high_memory": high_results}


def compare_cpu_limits(output_dir="output"):
    limits = [0.25, 0.5, 1.0]
    results = {}

    for limit in limits:
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--cpus",
                str(limit),
                "-v",
                f"{os.path.abspath(output_dir)}:/app/output",
                "scheduler-sim:latest",
                "python",
                "main.py",
                "--headless",
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results[str(limit)] = {"cpus": limit, "status": "completed"}
        except Exception as e:
            results[str(limit)] = {"cpus": limit, "status": "failed", "error": str(e)}

    return results
