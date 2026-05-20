import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .runner import run_with_threads, run_with_processes


def compare_threads_vs_processes(workload):
    thread_result = run_with_threads(workload)
    process_result = run_with_processes(workload)

    return {
        "threads": thread_result,
        "processes": process_result,
        "difference": round(process_result["elapsed"] - thread_result["elapsed"], 4),
        "ratio": round(process_result["elapsed"] / thread_result["elapsed"], 2)
        if thread_result["elapsed"] > 0
        else 0,
    }


def plot_threads_vs_processes(comparison, save_path):
    labels = ["Threads", "Processes"]
    values = [comparison["threads"]["elapsed"], comparison["processes"]["elapsed"]]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#4ECDC4", "#FF6B6B"])
    plt.ylabel("Execution Time (seconds)")
    plt.title("Threads vs Processes: Execution Time Comparison")
    for bar, v in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.4f}s",
            ha="center",
            fontweight="bold",
        )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
