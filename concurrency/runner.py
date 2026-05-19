import time
import threading
import multiprocessing
import os

TIME_SCALE = 0.1


def _execute_process(burst, io_burst, result_dict, idx):
    start = time.time()
    time.sleep(burst * TIME_SCALE)
    if io_burst > 0:
        time.sleep(io_burst * TIME_SCALE)
    end = time.time()
    result_dict[idx] = {
        "start": round(start, 4),
        "end": round(end, 4),
        "elapsed": round(end - start, 4),
    }


def run_with_threads(workload):
    results = {}
    threads = []
    start_time = time.time()

    for i, p in enumerate(workload):
        t = threading.Thread(
            target=_execute_process,
            args=(p["burst"], p.get("io_burst", 0), results, i),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    return {
        "method": "threads",
        "elapsed": round(end_time - start_time, 4),
        "process_count": len(workload),
        "per_process": results,
    }


def run_with_processes(workload):
    if os.name == "posix":
        multiprocessing.set_start_method("fork", force=True)

    manager = multiprocessing.Manager()
    results = manager.dict()
    processes = []
    start_time = time.time()

    for i, p in enumerate(workload):
        proc = multiprocessing.Process(
            target=_execute_process,
            args=(p["burst"], p.get("io_burst", 0), results, i),
        )
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    end_time = time.time()

    return {
        "method": "processes",
        "elapsed": round(end_time - start_time, 4),
        "process_count": len(workload),
        "per_process": dict(results),
    }
