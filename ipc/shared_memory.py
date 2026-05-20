import multiprocessing
from multiprocessing.shared_memory import SharedMemory
import multiprocessing.shared_memory
import time
import numpy as np

TIME_SCALE = 0.05


def _worker_shm(proc_index, burst, io_burst, shm_name, size):
    time.sleep(burst * TIME_SCALE)
    if io_burst > 0:
        time.sleep(io_burst * TIME_SCALE)
    existing_shm = SharedMemory(name=shm_name)
    arr = np.ndarray((size,), dtype=np.int32, buffer=existing_shm.buf)
    arr[proc_index] = 1
    existing_shm.close()


def run_shared_memory_scheduler(processes):
    size = len(processes)
    shm = SharedMemory(create=True, size=size * 4)
    arr = np.ndarray((size,), dtype=np.int32, buffer=shm.buf)
    arr[:] = 0

    procs = []
    for i, p in enumerate(processes):
        proc = multiprocessing.Process(
            target=_worker_shm,
            args=(i, p["burst"], p.get("io_burst", 0), shm.name, size),
        )
        procs.append(proc)
        proc.start()

    start_time = time.time()

    for proc in procs:
        proc.join()

    end_time = time.time()

    completed = list(arr)
    shm.close()
    shm.unlink()

    return {
        "method": "shared_memory",
        "elapsed": round(end_time - start_time, 4),
        "process_count": size,
        "completed": completed,
    }
