import multiprocessing
import time

TIME_SCALE = 0.05


def _worker_pipe(conn, worker_id):
    while True:
        msg = conn.recv()
        if msg == "STOP":
            break
        pid = msg["pid"]
        burst = msg["burst"]
        io_burst = msg.get("io_burst", 0)
        time.sleep(burst * TIME_SCALE)
        if io_burst > 0:
            time.sleep(io_burst * TIME_SCALE)
        conn.send({"pid": pid, "worker": worker_id, "done": True})
    conn.close()


def run_pipe_scheduler(processes):
    parent_conn, child_conn = multiprocessing.Pipe()
    worker = multiprocessing.Process(target=_worker_pipe, args=(child_conn, 1))
    worker.start()

    start_time = time.time()

    for p in processes:
        parent_conn.send(
            {
                "pid": p["pid"],
                "burst": p["burst"],
                "io_burst": p.get("io_burst", 0),
            }
        )

    results = []
    for _ in processes:
        result = parent_conn.recv()
        results.append(result)

    parent_conn.send("STOP")
    worker.join()
    end_time = time.time()

    return {
        "method": "pipes",
        "elapsed": round(end_time - start_time, 4),
        "process_count": len(processes),
        "results": results,
    }
