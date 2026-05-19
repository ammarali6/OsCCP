from .pipes import run_pipe_scheduler
from .shared_memory import run_shared_memory_scheduler


def run_ipc_demo(workload):
    pipe_result = run_pipe_scheduler(workload)
    shm_result = run_shared_memory_scheduler(workload)
    return {"pipes": pipe_result, "shared_memory": shm_result}
