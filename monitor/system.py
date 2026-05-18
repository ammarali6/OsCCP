"""
Linux System Monitoring Module.
Provides wrappers for common Linux monitoring tools:
- top, ps, htop (structured output)
- docker stats (container resource usage)
- /proc filesystem parsing (meminfo, cpuinfo)
"""

import subprocess
import re
import os
import json
from datetime import datetime


class SystemMonitor:
    """
    Monitors Linux system resources and Docker container statistics.
    Parses output from standard Linux tools into structured data.
    """

    @staticmethod
    def get_top_processes(n=10):
        """
        Get top CPU-consuming processes using `top`.
        Returns list of dicts with PID, USER, CPU%, MEM%, COMMAND.
        """
        try:
            result = subprocess.run(
                ['top', '-b', '-n', '1'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')

            # Find the header line
            header_idx = None
            for i, line in enumerate(lines):
                if 'PID' in line and 'USER' in line:
                    header_idx = i
                    break

            if header_idx is None:
                return []

            # Parse process lines
            processes = []
            for line in lines[header_idx + 1:header_idx + 1 + n]:
                parts = line.split()
                if len(parts) >= 12:
                    processes.append({
                        'pid': parts[0],
                        'user': parts[1],
                        'pr': parts[2],
                        'ni': parts[3],
                        'virt': parts[4],
                        'res': parts[5],
                        'shr': parts[6],
                        'state': parts[7],
                        'cpu_percent': parts[8],
                        'mem_percent': parts[9],
                        'time': parts[10],
                        'command': ' '.join(parts[11:]),
                    })

            return processes
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return [{'error': str(e)}]

    @staticmethod
    def get_ps_snapshot():
        """
        Get process snapshot using `ps aux`.
        Returns list of dicts with structured process info.
        """
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []

            # Header: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
            processes = []
            for line in lines[1:]:
                parts = line.split(None, 10)  # Split into 11 parts max
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu_percent': parts[2],
                        'mem_percent': parts[3],
                        'vsz': parts[4],
                        'rss': parts[5],
                        'tty': parts[6],
                        'stat': parts[7],
                        'start': parts[8],
                        'time': parts[9],
                        'command': parts[10],
                    })

            return processes
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return [{'error': str(e)}]

    @staticmethod
    def get_docker_stats(container_name=None):
        """
        Get Docker container statistics using `docker stats`.
        If container_name is None, returns stats for all containers.
        """
        try:
            cmd = ['docker', 'stats', '--no-stream', '--format',
                   '{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}']
            if container_name:
                cmd.append(container_name)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            stats = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) >= 6:
                    stats.append({
                        'name': parts[0].strip(),
                        'cpu_percent': parts[1].strip(),
                        'mem_usage': parts[2].strip(),
                        'net_io': parts[3].strip(),
                        'block_io': parts[4].strip(),
                        'pids': parts[5].strip(),
                    })

            return stats
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return [{'error': str(e)}]

    @staticmethod
    def get_memory_info():
        """
        Parse /proc/meminfo for memory statistics.
        Returns dict with total, free, available, used memory in MB.
        """
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()

            meminfo = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    # Extract numeric value in kB
                    num = re.search(r'(\d+)', value)
                    meminfo[key.strip()] = int(num.group(1)) if num else 0

            # Convert to MB
            total_mb = meminfo.get('MemTotal', 0) // 1024
            free_mb = meminfo.get('MemFree', 0) // 1024
            available_mb = meminfo.get('MemAvailable', free_mb) // 1024
            used_mb = total_mb - available_mb

            return {
                'total_mb': total_mb,
                'free_mb': free_mb,
                'available_mb': available_mb,
                'used_mb': used_mb,
                'usage_percent': round((used_mb / total_mb) * 100, 2) if total_mb > 0 else 0,
            }
        except (FileNotFoundError, Exception) as e:
            return {'error': str(e)}

    @staticmethod
    def get_cpu_info():
        """
        Parse /proc/cpuinfo or use lscpu for CPU information.
        Returns dict with CPU count, model, usage info.
        """
        try:
            # Try lscpu first
            result = subprocess.run(
                ['lscpu'],
                capture_output=True,
                text=True,
                timeout=5
            )

            cpu_info = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    cpu_info[key.strip()] = value.strip()

            # Parse /proc/loadavg for load averages
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read().strip().split()
                cpu_info['loadavg_1min'] = loadavg[0] if len(loadavg) > 0 else 'N/A'
                cpu_info['loadavg_5min'] = loadavg[1] if len(loadavg) > 1 else 'N/A'
                cpu_info['loadavg_15min'] = loadavg[2] if len(loadavg) > 2 else 'N/A'

            return cpu_info
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            return {'error': str(e)}

    @staticmethod
    def get_cpu_usage_percent():
        """
        Calculate current CPU usage percentage from /proc/stat.
        """
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()

            fields = line.split()
            if fields[0] != 'cpu':
                return None

            # user, nice, system, idle, iowait, irq, softirq
            values = [int(x) for x in fields[1:]]
            total = sum(values)
            idle = values[3] + values[4]  # idle + iowait

            # Need a second reading for accurate percentage
            import time
            time.sleep(0.5)

            with open('/proc/stat', 'r') as f:
                line2 = f.readline()
            fields2 = line2.split()
            values2 = [int(x) for x in fields2[1:]]
            total2 = sum(values2)
            idle2 = values2[3] + values2[4]

            total_diff = total2 - total
            idle_diff = idle2 - idle

            if total_diff == 0:
                return 0

            usage = ((total_diff - idle_diff) / total_diff) * 100
            return round(usage, 2)
        except (FileNotFoundError, Exception) as e:
            return None

    @staticmethod
    def capture_snapshot():
        """
        Capture a comprehensive system snapshot.
        Returns dict with timestamp and all available metrics.
        """
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
            'memory': SystemMonitor.get_memory_info(),
            'cpu': SystemMonitor.get_cpu_info(),
            'cpu_usage_percent': SystemMonitor.get_cpu_usage_percent(),
            'top_processes': SystemMonitor.get_top_processes(n=5),
            'docker_stats': SystemMonitor.get_docker_stats(),
        }
        return snapshot

    @staticmethod
    def print_snapshot(snapshot):
        """Pretty print a system snapshot."""
        print(f"\n{'='*60}")
        print(f"  SYSTEM SNAPSHOT - {snapshot['timestamp']}")
        print(f"{'='*60}")

        print(f"\n🖥️  Host: {snapshot['hostname']}")

        mem = snapshot.get('memory', {})
        if 'error' not in mem:
            print(f"\n🧠 Memory:")
            print(f"   Total: {mem.get('total_mb', 'N/A')} MB")
            print(f"   Used:  {mem.get('used_mb', 'N/A')} MB")
            print(f"   Free:  {mem.get('free_mb', 'N/A')} MB")
            print(f"   Usage: {mem.get('usage_percent', 'N/A')}%")

        cpu = snapshot.get('cpu', {})
        if 'error' not in cpu:
            print(f"\n💻 CPU:")
            print(f"   Model: {cpu.get('Model name', 'N/A')}")
            print(f"   Cores: {cpu.get('CPU(s)', 'N/A')}")
            print(f"   Load:  {cpu.get('loadavg_1min', 'N/A')} (1min)")
            print(f"   Usage: {snapshot.get('cpu_usage_percent', 'N/A')}%")

        top = snapshot.get('top_processes', [])
        if top and 'error' not in top[0]:
            print(f"\n🔝 Top Processes:")
            for proc in top[:5]:
                print(f"   {proc.get('pid', '?'):>6} | CPU: {proc.get('cpu_percent', '?'):>5} | MEM: {proc.get('mem_percent', '?'):>5} | {proc.get('command', '?')[:30]}")

        docker = snapshot.get('docker_stats', [])
        if docker and 'error' not in docker[0]:
            print(f"\n🐳 Docker Containers:")
            for cont in docker:
                print(f"   {cont.get('name', '?'):<20} | CPU: {cont.get('cpu_percent', '?'):>6} | MEM: {cont.get('mem_usage', '?'):>15}")

        print(f"\n{'='*60}\n")


# Example usage
if __name__ == "__main__":
    snap = SystemMonitor.capture_snapshot()
    SystemMonitor.print_snapshot(snap)
