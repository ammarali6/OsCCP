# Docker Flags Reference for OS Scheduler Simulator

## Container Resource Limits

### CPU Limits
| Flag | Description | Example |
|------|-------------|---------|
| `--cpus` | Number of CPUs (fractional) | `--cpus="1.5"` |
| `--cpu-period` | CPU CFS period | `--cpu-period=100000` |
| `--cpu-quota` | CPU CFS quota | `--cpu-quota=50000` |
| `--cpuset-cpus` | CPUs to use | `--cpuset-cpus="0,1"` |
| `--cpu-shares` | Relative weight | `--cpu-shares=512` |

### Memory Limits
| Flag | Description | Example |
|------|-------------|---------|
| `--memory` | Hard memory limit | `--memory="512m"` |
| `--memory-swap` | Swap limit | `--memory-swap="1g"` |
| `--memory-reservation` | Soft limit | `--memory-reservation="256m"` |
| `--kernel-memory` | Kernel memory limit | `--kernel-memory="64m"` |
| `--oom-kill-disable` | Disable OOM killer | `--oom-kill-disable` |

### Process Limits
| Flag | Description | Example |
|------|-------------|---------|
| `--pids-limit` | Max processes | `--pids-limit=100` |
| `--ulimit` | Resource limits | `--ulimit nproc=50` |

## PID Namespace Options

| Flag | Description |
|------|-------------|
| (default) | Container gets own PID namespace, PID 1 is init |
| `--pid=host` | Container shares host PID namespace |
| `--pid=container:<name>` | Shares PID namespace with another container |

## Other Isolation Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--network` | Network isolation | `--network=none` |
| `--user` | Run as user | `--user=1000` |
| `--read-only` | Read-only filesystem | `--read-only` |
| `--security-opt` | Security options | `--security-opt=no-new-privileges` |
| `--cap-drop` | Drop capabilities | `--cap-drop=ALL` |
| `--cap-add` | Add capabilities | `--cap-add=NET_BIND_SERVICE` |

## Monitoring Commands

```bash
# Live container stats
docker stats <container>

# Resource usage history
docker stats --no-stream <container>

# Container processes
docker top <container>

# Container details
docker inspect <container>

# Host system stats
top
htop
ps aux
free -m
```

## Quick Reference: Running the Simulator

```bash
# Build image
docker build -t scheduler-sim .

# Run with GUI (requires X11 forwarding)
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix scheduler-sim

# Run headless (default)
docker run scheduler-sim

# Run with limits
docker run --cpus="1.0" --memory="512m" scheduler-sim

# Run multiple instances
docker-compose up

# Scale instances
docker-compose up --scale simulator=3
```
