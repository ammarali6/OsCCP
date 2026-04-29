#!/usr/bin/env python3
"""
Test Script for OS Scheduler Simulator

This script demonstrates the capabilities of the OS Scheduler
by running several test scenarios with different algorithms.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms import fcfs, sjf, priority, round_robin, mlfq
from metrics import MetricsCalculator
from adaptive import AdaptiveScheduler


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_results(algorithm_name, result, gantt):
    """Print algorithm results."""
    print(f"\n🔹 Algorithm: {algorithm_name}")
    print("-" * 60)
    
    try:
        calc = MetricsCalculator(result)
        metrics = calc.get_all_metrics()
        
        print(f"Average Waiting Time:    {metrics['waiting_time']['average']:>8.2f} units")
        print(f"Average Turnaround Time: {metrics['turnaround_time']['average']:>8.2f} units")
        print(f"CPU Utilization:         {metrics['cpu_utilization']:>8.2f}%")
        print(f"Throughput:              {metrics['throughput']:>8.4f} processes/unit")
        
        print("\nProcess Details:")
        print(f"{'PID':<6} {'Arr':<5} {'Burst':<6} {'Start':<7} {'Finish':<8} {'Wait':<6} {'TAT':<6}")
        print("-" * 50)
        for p in result:
            print(f"{p['pid']:<6} {p['arrival']:<5} {p['burst']:<6} {p['start']:<7} {p['finish']:<8} {p['waiting']:<6} {p['turnaround']:<6}")
    except Exception as e:
        print(f"Error calculating metrics: {e}")


def test_scenario_1():
    """Test Scenario 1: Uniform Burst Times (Simple Batch)"""
    print_header("TEST SCENARIO 1: Uniform Burst Times")
    
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 5, 'priority': 1, 'color': '#FF6B6B'},
        {'pid': 'P2', 'arrival': 1, 'burst': 5, 'priority': 1, 'color': '#4ECDC4'},
        {'pid': 'P3', 'arrival': 2, 'burst': 5, 'priority': 1, 'color': '#45B7D1'},
        {'pid': 'P4', 'arrival': 3, 'burst': 5, 'priority': 1, 'color': '#FFA07A'},
    ]
    
    print("Processes: 4 jobs with uniform burst time (5 units)")
    print("Workload: Batch processing system\n")
    
    # Test all algorithms
    result, gantt = fcfs.run_fcfs(processes)
    print_results("FCFS", result, gantt)
    
    result, gantt = sjf.run_sjf_non_preemptive(processes)
    print_results("SJF", result, gantt)
    
    result, gantt = priority.run_priority(processes)
    print_results("Priority", result, gantt)
    
    result, gantt = round_robin.run_round_robin(processes, quantum=2)
    print_results("Round Robin (Q=2)", result, gantt)
    
    result, gantt = mlfq.run_mlfq(processes, q0=2, q1=4)
    print_results("MLFQ", result, gantt)
    
    # Adaptive recommendation
    print("\n📊 Adaptive Scheduler Analysis:")
    adaptive = AdaptiveScheduler()
    analysis = adaptive.analyze_workload(processes)
    print(f"Characteristics: {', '.join(analysis['characteristics'])}")
    print(f"Top Recommendation: {analysis['recommendations'][0]['algorithm']} "
          f"({analysis['recommendations'][0]['score']*100:.0f}%)")
    print(f"Reason: {analysis['recommendations'][0]['reason']}")


def test_scenario_2():
    """Test Scenario 2: Short, Varied Jobs"""
    print_header("TEST SCENARIO 2: Short, Varied Jobs")
    
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 3, 'priority': 1, 'color': '#FF6B6B'},
        {'pid': 'P2', 'arrival': 1, 'burst': 1, 'priority': 1, 'color': '#4ECDC4'},
        {'pid': 'P3', 'arrival': 2, 'burst': 4, 'priority': 1, 'color': '#45B7D1'},
        {'pid': 'P4', 'arrival': 4, 'burst': 2, 'priority': 1, 'color': '#FFA07A'},
    ]
    
    print("Processes: 4 jobs with varied burst times (1-4 units)")
    print("Workload: Time-sharing system\n")
    
    result, gantt = fcfs.run_fcfs(processes)
    print_results("FCFS", result, gantt)
    
    result, gantt = sjf.run_sjf_non_preemptive(processes)
    print_results("SJF", result, gantt)
    
    result, gantt = round_robin.run_round_robin(processes, quantum=2)
    print_results("Round Robin (Q=2)", result, gantt)
    
    # Adaptive recommendation
    print("\n📊 Adaptive Scheduler Analysis:")
    adaptive = AdaptiveScheduler()
    analysis = adaptive.analyze_workload(processes)
    print(f"Characteristics: {', '.join(analysis['characteristics'])}")
    print(f"Top Recommendation: {analysis['recommendations'][0]['algorithm']} "
          f"({analysis['recommendations'][0]['score']*100:.0f}%)")
    print(f"Reason: {analysis['recommendations'][0]['reason']}")


def test_scenario_3():
    """Test Scenario 3: Prioritized Workload"""
    print_header("TEST SCENARIO 3: Prioritized Workload")
    
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 5, 'priority': 3, 'color': '#FF6B6B'},
        {'pid': 'P2', 'arrival': 1, 'burst': 3, 'priority': 1, 'color': '#4ECDC4'},
        {'pid': 'P3', 'arrival': 2, 'burst': 8, 'priority': 2, 'color': '#45B7D1'},
        {'pid': 'P4', 'arrival': 4, 'burst': 2, 'priority': 1, 'color': '#FFA07A'},
    ]
    
    print("Processes: 4 jobs with different priorities (1=high, 3=low)")
    print("Workload: Real-time system with priority requirements\n")
    
    result, gantt = priority.run_priority(processes)
    print_results("Priority", result, gantt)
    
    result, gantt = mlfq.run_mlfq(processes, q0=2, q1=4)
    print_results("MLFQ", result, gantt)
    
    result, gantt = round_robin.run_round_robin(processes, quantum=2)
    print_results("Round Robin (Q=2)", result, gantt)
    
    # Adaptive recommendation
    print("\n📊 Adaptive Scheduler Analysis:")
    adaptive = AdaptiveScheduler()
    analysis = adaptive.analyze_workload(processes)
    print(f"Characteristics: {', '.join(analysis['characteristics'])}")
    for i, rec in enumerate(analysis['recommendations'][:2], 1):
        print(f"{i}. {rec['algorithm']} ({rec['score']*100:.0f}%): {rec['reason']}")


def main():
    """Run all tests."""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║    🧪 OS SCHEDULER SIMULATOR - TEST SUITE             ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    print("This script demonstrates the OS Scheduler with three scenarios:")
    print("1. Uniform Burst Times (Batch Processing)")
    print("2. Short, Varied Jobs (Time-sharing)")
    print("3. Prioritized Workload (Real-time)")
    
    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        
        print_header("TEST SUMMARY")
        print("✓ All test scenarios completed successfully!")
        print("✓ To use the interactive GUI, run: python main.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
