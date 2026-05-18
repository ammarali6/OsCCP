"""
Monitoring Demo Script.
Runs the simulator in headless mode alongside system monitoring,
capturing real Linux metrics side-by-side with simulator-reported metrics.
"""

import subprocess
import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.system import SystemMonitor
from headless import run_headless_simulation, PRESET_WORKLOADS


def run_monitor_demo(algorithm='fcfs', preset='mixed', duration=30,
                     sample_interval=2, output_file='demo/monitor_log.jsonl'):
    """
    Run a monitoring demo that:
    1. Starts a headless simulation
    2. Captures system metrics at regular intervals
    3. Logs both simulator and system metrics side-by-side

    Args:
        algorithm: scheduling algorithm to test
        preset: workload preset
        duration: how long to monitor (seconds)
        sample_interval: seconds between samples
        output_file: path to write JSONL log
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"📊 Starting Monitoring Demo")
    print(f"   Algorithm: {algorithm}")
    print(f"   Preset: {preset}")
    print(f"   Duration: {duration}s")
    print(f"   Sample Interval: {sample_interval}s")
    print(f"   Output: {output_file}")
    print("-" * 60)

    # Get baseline snapshot
    baseline = SystemMonitor.capture_snapshot()
    SystemMonitor.print_snapshot(baseline)

    # Run simulation (in background or sequentially)
    processes = PRESET_WORKLOADS.get(preset, PRESET_WORKLOADS['mixed'])
    sim_result = run_headless_simulation(
        algorithm=algorithm,
        processes=processes,
        output_dir='output'
    )

    # Capture post-simulation snapshot
    post_sim = SystemMonitor.capture_snapshot()
    SystemMonitor.print_snapshot(post_sim)

    # Compare simulator metrics with system metrics
    comparison = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'algorithm': algorithm,
        'preset': preset,
        'simulator_metrics': {
            'cpu_utilization_reported': sim_result['metrics']['cpu_utilization'],
            'throughput_reported': sim_result['metrics']['throughput'],
            'avg_waiting_time': sim_result['metrics']['waiting_time']['average'],
            'avg_turnaround_time': sim_result['metrics']['turnaround_time']['average'],
            'memory_utilization_reported': sim_result['metrics']['memory']['utilization'],
        },
        'system_metrics_before': {
            'cpu_usage_percent': baseline.get('cpu_usage_percent'),
            'memory_usage_percent': baseline.get('memory', {}).get('usage_percent'),
            'loadavg_1min': baseline.get('cpu', {}).get('loadavg_1min'),
        },
        'system_metrics_after': {
            'cpu_usage_percent': post_sim.get('cpu_usage_percent'),
            'memory_usage_percent': post_sim.get('memory', {}).get('usage_percent'),
            'loadavg_1min': post_sim.get('cpu', {}).get('loadavg_1min'),
        },
        'docker_stats_before': baseline.get('docker_stats', []),
        'docker_stats_after': post_sim.get('docker_stats', []),
    }

    # Write to JSONL
    with open(output_file, 'a') as f:
        f.write(json.dumps(comparison) + '\n')

    print(f"\n✅ Demo complete. Log written to {output_file}")
    print(f"\n📈 Comparison Summary:")
    print(f"   Simulator CPU Util:     {comparison['simulator_metrics']['cpu_utilization_reported']}%")
    print(f"   System CPU Before:      {comparison['system_metrics_before']['cpu_usage_percent']}%")
    print(f"   System CPU After:       {comparison['system_metrics_after']['cpu_usage_percent']}%")
    print(f"   Simulator Memory Util:  {comparison['simulator_metrics']['memory_utilization_reported']}%")
    print(f"   System Memory Before:   {comparison['system_metrics_before']['memory_usage_percent']}%")
    print(f"   System Memory After:    {comparison['system_metrics_after']['memory_usage_percent']}%")

    return comparison


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Monitor Demo - System vs Simulator Metrics')
    parser.add_argument('-a', '--algorithm', default='fcfs', choices=['fcfs', 'sjf', 'priority', 'round_robin', 'mlfq'])
    parser.add_argument('-p', '--preset', default='mixed', choices=['simple', 'memory_stress', 'mixed'])
    parser.add_argument('-o', '--output', default='demo/monitor_log.jsonl')
    args = parser.parse_args()

    run_monitor_demo(algorithm=args.algorithm, preset=args.preset, output_file=args.output)
