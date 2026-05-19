import os
from datetime import datetime


def generate_final_report(
    experiment_results=None,
    concurrency_data=None,
    ipc_data=None,
    memory_data=None,
    cpu_data=None,
    output_dir="output",
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# OS Scheduler Simulator - Final Project Report

**Date:** {timestamp}
**Deliverable:** 3 - Concurrency, IPC & Final Performance Evaluation
**Course:** Operating Systems - BS (AI)-6(A)

---

## 1. Architecture Overview

The OS Scheduler Simulator is a modular Python application that simulates CPU scheduling
algorithms, memory management, concurrency models, and IPC mechanisms.

### Components

| Module | Description |
|--------|-------------|
| `algorithms/` | FCFS, SJF (NP), Priority, Round Robin, MLFQ |
| `memory/` | Fixed/Variable Partitions, Paging, First/Best/Worst Fit |
| `concurrency/` | Multi-threading and Multi-processing execution |
| `ipc/` | Pipes and Shared Memory communication |
| `experiments/` | Automated comparison across workloads and configurations |
| `reporting/` | Chart generation and final markdown report |

### Architecture Diagram

```
+-------------------+
|     main.py       |  Entry point (CLI)
+--------+----------+
         |
         v
+--------+----------+
|   headless.py     |  Headless simulation runner
+--------+----------+
         |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+--------+--------+  +------+------+  +---------+---------+
|  algorithms/    |  |  memory/    |  |  concurrency/     |
|  - fcfs, sjf,   |  |  partitions |  |  - runner.py      |
|  - priority, rr |  |  - paging   |  |  - comparator.py  |
|  - mlfq         |  |  - vis      |  +---------+---------+
+-----------------+  +-------------+            |
         |                                      |
         v                                      v
+--------+--------+  +---------+--------+  +----+-------------+
|  experiments/   |  |  ipc/            |  |  reporting/      |
|  - workloads    |  |  - pipes.py      |  |  - charts.py     |
|  - runner       |  |  - shared_memory |  |  - generator.py  |
|  - comparisons  |  +------------------+  +------------------+
+-----------------+
```

---

## 2. Scheduling Algorithm Comparison

The following table compares scheduling algorithms across CPU-bound, I/O-bound, and mixed workloads.

"""

    if experiment_results:
        report += "| Algorithm | Workload | Avg Waiting | Avg Turnaround | CPU Util | Throughput | Total I/O |\n"
        report += "|-----------|----------|-------------|----------------|----------|------------|-----------|\n"

        for workload_name in ["cpu_bound", "io_bound", "mixed"]:
            results = experiment_results.get(workload_name, [])
            for r in results:
                m = r["metrics"]
                io = m.get("io", {})
                report += f"| {r['algorithm_name']} | {workload_name} | "
                report += f"{m['waiting_time']['average']} | {m['turnaround_time']['average']} | "
                report += f"{m['cpu_utilization']}% | {m['throughput']} | "
                report += f"{io.get('total_io_time', 0)} |\n"

        report += "\n### Charts\n\n"
        report += "![Algorithm Comparison](compare_algorithms.png)\n\n"

        report += "### Key Observations\n"
        report += (
            "- **CPU-bound workloads**: Longer bursts mean higher CPU utilization. "
        )
        report += "SJF minimizes average waiting time effectively.\n"
        report += "- **I/O-bound workloads**: Short CPU bursts with I/O waits. "
        report += "Round Robin provides fair scheduling.\n"
        report += "- **Mixed workloads**: MLFQ balances responsiveness for I/O-bound processes "
        report += "with throughput for CPU-bound processes.\n"
        report += "- FCFS can cause the convoy effect when a long process blocks many short ones.\n"

    report += "\n---\n\n## 3. Concurrency Analysis: Threads vs Processes\n\n"

    if concurrency_data:
        t = concurrency_data["threads"]
        p = concurrency_data["processes"]
        report += "| Metric | Threads | Processes |\n"
        report += "|--------|---------|-----------|\n"
        report += f"| Execution Time (s) | {t['elapsed']} | {p['elapsed']} |\n"
        report += f"| Process Count | {t['process_count']} | {p['process_count']} |\n"
        report += (
            f"| Overhead Ratio | 1.0 | {concurrency_data.get('ratio', 'N/A')} |\n\n"
        )

        report += "![Concurrency Comparison](compare_concurrency.png)\n\n"

        report += "### Analysis\n"
        report += "- **Threads** share the same memory space, making creation and "
        report += "context switching faster. They are lightweight.\n"
        report += (
            "- **Processes** (created via `fork()`) have separate address spaces. "
        )
        report += "They provide better isolation but have higher creation and switching overhead.\n"
        report += "- The overhead ratio shows how much slower processes are compared to threads "
        report += "for the same workload.\n"
        report += "- Python's Global Interpreter Lock (GIL) affects CPU-bound threads "
        report += "but processes can run in true parallel on multiple cores.\n"

    report += "\n---\n\n## 4. Inter-Process Communication (IPC)\n\n"
    report += (
        "Two IPC mechanisms were implemented: **Pipes** and **Shared Memory**.\n\n"
    )

    report += "### 4.1 Pipes\n"
    report += "- **Implementation:** `multiprocessing.Pipe()` — a duplex communication channel\n"
    report += "- **Mechanism:** The scheduler sends process data through the pipe; "
    report += (
        "the worker reads and simulates execution, then sends completion status back\n"
    )
    report += "- **Use case:** Simple producer-consumer communication\n"
    report += "- **Limitation:** Data must be serialized; limited buffer size\n\n"

    report += "### 4.2 Shared Memory\n"
    report += "- **Implementation:** `multiprocessing.shared_memory.SharedMemory`\n"
    report += (
        "- **Mechanism:** Workers write completion status directly to a shared memory "
    )
    report += "segment that the scheduler can read without kernel intervention\n"
    report += "- **Use case:** High-speed data sharing between related processes\n"
    report += "- **Advantage:** Fastest IPC as data is directly accessible without copying\n\n"

    if ipc_data:
        report += "| Method | Execution Time (s) | Process Count |\n"
        report += "|--------|-------------------|---------------|\n"
        for method, data in ipc_data.items():
            report += f"| {method.title()} | {data['elapsed']} | {data.get('process_count', 'N/A')} |\n"
        report += "\n"

    report += "\n---\n\n## 5. Docker Experimentation\n\n"
    report += "The simulator was containerized using Docker for deployment and resource-constrained testing.\n\n"
    report += "### Host vs Docker Comparison\n"
    report += (
        "- **Host execution:** Direct OS execution with no virtualization overhead\n"
    )
    report += "- **Docker execution:** Containers use the host kernel but provide "
    report += "filesystem and resource isolation via namespaces and cgroups\n"
    report += "- **Observation:** Docker adds minimal overhead while providing "
    report += "consistent environments and process isolation\n"
    report += "- **PID namespaces** ensure processes inside containers cannot see host processes\n\n"

    if cpu_data:
        report += "### CPU Limit Experiments\n\n"
        report += "| CPU Limit | Status |\n"
        report += "|-----------|--------|\n"
        for limit, data in cpu_data.items():
            report += f"| {limit} core(s) | {data.get('status', 'N/A')} |\n"
        report += "\n"
        report += "![CPU Limits](compare_cpu_limits.png)\n\n"
        report += "**Observation:** Docker's `--cpus` flag limits how much CPU time "
        report += (
            "a container can use. Lower CPU limits increase scheduling wait times "
        )
        report += "and reduce throughput.\n"

    report += "\n---\n\n## 6. Memory Management Observations\n\n"
    report += "The simulator implements three memory management techniques:\n\n"
    report += "### 6.1 Fixed Partition Allocation\n"
    report += "- Memory divided into equal-sized partitions\n"
    report += (
        "- Internal fragmentation occurs when a process does not fill its partition\n"
    )
    report += "- Simple to implement but wasteful\n\n"
    report += "### 6.2 Variable Partition Allocation\n"
    report += "- Partitions created dynamically to match process size\n"
    report += (
        "- External fragmentation occurs as processes are allocated and deallocated\n"
    )
    report += "- More memory-efficient than fixed partitions\n\n"
    report += "### 6.3 Allocation Algorithms\n"
    report += "- **First Fit:** Fast, may leave small gaps at start of memory\n"
    report += "- **Best Fit:** Minimizes wasted space but slower\n"
    report += "- **Worst Fit:** Leaves largest remaining blocks\n\n"

    if memory_data:
        report += "### Low Memory vs High Memory Impact\n\n"
        report += "| Algorithm | Low Mem (256) Avg Wait | Low Mem (256) Avg TAT | "
        report += "High Mem (1024) Avg Wait | High Mem (1024) Avg TAT |\n"
        report += "|-----------|----------------------|----------------------|"
        report += "-----------------------|-----------------------|\n"

        for algo in sorted(memory_data.get("low_memory", {}).keys()):
            lm = memory_data["low_memory"][algo]
            hm = memory_data["high_memory"][algo]
            lw = (
                lm["waiting_time"]["average"]
                if isinstance(lm.get("waiting_time"), dict)
                else lm.get("waiting_time", 0)
            )
            lt = (
                lm["turnaround_time"]["average"]
                if isinstance(lm.get("turnaround_time"), dict)
                else lm.get("turnaround_time", 0)
            )
            hw = (
                hm["waiting_time"]["average"]
                if isinstance(hm.get("waiting_time"), dict)
                else hm.get("waiting_time", 0)
            )
            ht = (
                hm["turnaround_time"]["average"]
                if isinstance(hm.get("turnaround_time"), dict)
                else hm.get("turnaround_time", 0)
            )
            report += f"| {algo} | {lw} | {lt} | {hw} | {ht} |\n"

        report += "\n![Memory Comparison](compare_memory.png)\n\n"
        report += "**Observation:** Low memory increases waiting and turnaround times "
        report += "as processes must wait for memory to become available.\n"

    report += "\n---\n\n## 7. Challenges Faced\n\n"
    report += (
        "1. **Balancing realism with simplicity**: Simulating OS behavior accurately "
    )
    report += (
        "while keeping the code understandable required careful abstraction choices.\n"
    )
    report += "2. **Thread vs Process comparison**: Measuring meaningful overhead differences "
    report += "required running real workloads (via `time.sleep()`) rather than pure simulation.\n"
    report += (
        "3. **IPC implementation**: Shared memory required careful synchronization; "
    )
    report += "pipes needed proper handling of bidirectional communication.\n"
    report += "4. **Docker resource limits**: Testing CPU/memory constraints required "
    report += "understanding Docker's cgroups implementation.\n"
    report += (
        "5. **I/O simulation**: Modeling I/O-bound workloads realistically without "
    )
    report += "actual hardware I/O required creative use of sleep timers and burst patterns.\n"

    report += "\n---\n\n## 8. Conclusion\n\n"
    report += (
        "This project successfully demonstrated key operating system concepts:\n\n"
    )
    report += (
        "1. **CPU Scheduling**: Compared FCFS, SJF, Priority, Round Robin, and MLFQ "
    )
    report += "algorithms across different workload types.\n"
    report += (
        "2. **Memory Management**: Implemented fixed and variable partition allocation "
    )
    report += "with multiple allocation strategies.\n"
    report += "3. **Containerization**: Docker integration for isolated, resource-constrained execution.\n"
    report += "4. **Concurrency**: Measured and compared thread vs process execution overhead.\n"
    report += "5. **IPC**: Successfully implemented pipes and shared memory for "
    report += "inter-process communication.\n"
    report += "6. **Performance Analysis**: Generated comprehensive reports with "
    report += "metrics, charts, and comparative analysis.\n\n"
    report += (
        "The simulator provides a practical, hands-on platform for understanding how "
    )
    report += "operating systems manage resources, schedule processes, and enable "
    report += "inter-process communication.\n"

    filepath = os.path.join(output_dir, "FINAL_REPORT.md")
    with open(filepath, "w") as f:
        f.write(report)

    return filepath
