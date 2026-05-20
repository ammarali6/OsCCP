import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_algorithm_comparison(comparison_data, save_path):
    algorithms = list(comparison_data.keys())
    workloads = ["cpu_bound", "io_bound", "mixed"]
    labels = ["CPU-Bound", "I/O-Bound", "Mixed"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for metric_idx, metric in enumerate(["avg_waiting", "avg_turnaround"]):
        ax = axes[metric_idx]
        x = np.arange(len(algorithms))
        width = 0.25

        for i, wl in enumerate(workloads):
            values = []
            for algo in algorithms:
                wl_data = comparison_data[algo]["workloads"].get(wl, {})
                values.append(wl_data.get(metric, 0))
            ax.bar(x + i * width, values, width, label=labels[i])

        ax.set_xlabel("Algorithm")
        title = "Waiting Time" if metric == "avg_waiting" else "Turnaround Time"
        ax.set_ylabel(title)
        ax.set_title(f"{title} by Algorithm and Workload")
        ax.set_xticks(x + width)
        ax.set_xticklabels(
            [comparison_data[a]["algorithm"] for a in algorithms], rotation=15
        )
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close("all")
    return save_path


def plot_concurrency_comparison(comparison_data, save_path):
    labels = ["Threads", "Processes"]
    values = [
        comparison_data["threads"]["elapsed"],
        comparison_data["processes"]["elapsed"],
    ]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#4ECDC4", "#FF6B6B"])
    plt.ylabel("Execution Time (seconds)")
    plt.title("Threads vs Processes: Execution Time")
    for bar, v in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.4f}s",
            ha="center",
            fontweight="bold",
        )
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close("all")
    return save_path


def plot_memory_comparison(memory_data, save_path):
    algorithms = list(memory_data["low_memory"].keys())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, metric in enumerate(["avg_waiting", "avg_turnaround"]):
        ax = axes[idx]
        x = np.arange(len(algorithms))
        width = 0.35

        low_vals = []
        high_vals = []
        for a in algorithms:
            lm = memory_data["low_memory"][a]
            hm = memory_data["high_memory"][a]
            if metric in lm and isinstance(lm[metric], dict):
                low_vals.append(lm[metric].get("average", 0))
            else:
                low_vals.append(lm.get(metric, 0))
            if metric in hm and isinstance(hm[metric], dict):
                high_vals.append(hm[metric].get("average", 0))
            else:
                high_vals.append(hm.get(metric, 0))

        ax.bar(
            x - width / 2, low_vals, width, label="Low Memory (256)", color="#FF6B6B"
        )
        ax.bar(
            x + width / 2, high_vals, width, label="High Memory (1024)", color="#4ECDC4"
        )

        ax.set_xlabel("Algorithm")
        title = "Waiting Time" if metric == "avg_waiting" else "Turnaround Time"
        ax.set_ylabel(title)
        ax.set_title(f"{title}: Low vs High Memory")
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close("all")
    return save_path


def plot_cpu_limits_comparison(cpu_data, save_path):
    limits = sorted(cpu_data.keys())

    plt.figure(figsize=(8, 5))
    statuses = [cpu_data[k].get("status", "unknown") for k in limits]
    colors = ["#4ECDC4" if s == "completed" else "#FF6B6B" for s in statuses]
    plt.bar(limits, [1] * len(limits), color=colors)
    plt.xlabel("CPU Cores Limit")
    plt.ylabel("Status")
    plt.title("Docker CPU Limit Experiments")
    plt.ylim(0, 1.5)
    for i, key in enumerate(limits):
        status = cpu_data[key].get("status", "unknown")
        plt.text(i, 0.5, f"{key} CPUs\n{status}", ha="center", fontweight="bold")
    plt.yticks([])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close("all")
    return save_path
