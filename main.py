"""
OS Scheduler Simulator - Main Entry Point

This is the main application launcher for the OS Scheduler Simulator.
It orchestrates all components including:
- Scheduling Algorithms (FCFS, SJF, Priority, Round Robin, MLFQ)
- GUI Interface (Tkinter)
- Gantt Chart Visualization (Matplotlib)
- Performance Metrics Calculation
- Adaptive Algorithm Recommendations
- Headless Mode (Docker/container-friendly CLI)
- Memory Management Integration

Usage:
    python main.py                    # Launch GUI
    python main.py --headless         # Run headless simulation
    python main.py --headless --algorithm fcfs --preset simple
    python main.py --headless --algorithm mlfq --preset memory_stress --memory-total 512 --memory-algo best_fit
"""

import sys
import os
import argparse

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """Print application banner."""
    banner = """
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║       🖥️  OS SCHEDULER SIMULATOR - DELIVERABLE 2      ║
    ║                                                        ║
    ║  A comprehensive CPU scheduling simulation platform   ║
    ║  with memory management, Docker support, and         ║
    ║  resource-constrained scheduling analysis            ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    
    Available Scheduling Algorithms:
    • FCFS (First Come First Served)
    • SJF (Shortest Job First - Non-Preemptive)
    • Priority Scheduling (Non-Preemptive)
    • Round Robin (Preemptive)
    • MLFQ (Multi-Level Feedback Queue)
    
    Memory Management:
    • Fixed & Variable Partition Allocation
    • Paging Simulation
    • First Fit, Best Fit, Worst Fit Algorithms
    
    Features:
    ✓ Dynamic process input (Arrival, Burst, Priority, Memory)
    ✓ Real-time Gantt chart visualization
    ✓ Performance metrics (Waiting, Turnaround, CPU/Memory Util, Throughput)
    ✓ AI-based algorithm recommendations
    ✓ Simulation control (Start, Pause, Resume, Reset)
    ✓ Export and save results
    ✓ Headless mode for containerized deployment
    ✓ Docker support with CPU/memory limits
    """
    print(banner)


def run_headless(args):
    """Run headless simulation and output results."""
    from headless import run_headless_simulation, PRESET_WORKLOADS

    print("\n📊 Running Headless Simulation...")
    print(f"   Algorithm: {args.algorithm}")
    print(f"   Preset: {args.preset}")
    print(f"   Memory Total: {args.memory_total}")
    print(f"   Memory Algorithm: {args.memory_algo}")
    print(f"   Quantum: {args.quantum}")
    print(f"   Output Directory: {args.output_dir}")
    print("-" * 50)

    processes = PRESET_WORKLOADS.get(args.preset, PRESET_WORKLOADS['simple'])

    result = run_headless_simulation(
        algorithm=args.algorithm,
        processes=processes,
        memory_total=args.memory_total,
        memory_algo=args.memory_algo,
        output_dir=args.output_dir,
        quantum=args.quantum
    )

    print("\n✅ Simulation Complete!")
    print(f"\n📁 Output Files:")
    for name, path in result['files'].items():
        if path:
            print(f"   {name}: {path}")

    print(f"\n📈 Metrics Summary:")
    metrics = result['metrics']
    print(f"   Avg Waiting Time: {metrics['waiting_time']['average']}")
    print(f"   Avg Turnaround Time: {metrics['turnaround_time']['average']}")
    print(f"   CPU Utilization: {metrics['cpu_utilization']}%")
    print(f"   Throughput: {metrics['throughput']}")
    print(f"   Memory Utilization: {metrics['memory']['utilization']}%")
    print(f"   Avg Memory Wait: {metrics['memory']['avg_memory_wait']}")

    print(f"\n📋 Process Details:")
    print(f"   {'PID':<6} {'Arr':<5} {'Burst':<6} {'MemReq':<7} {'Allocated':<10} {'MemWait':<8}")
    print("   " + "-" * 50)
    for p in result['result']:
        alloc = 'Yes' if p.get('memory_allocated') else 'No'
        print(f"   {p['pid']:<6} {p['arrival']:<5} {p['burst']:<6} "
              f"{p.get('memory_req', 0):<7} {alloc:<10} {p.get('memory_wait', 0):<8}")

    return result


def run_gui():
    """Launch the GUI application."""
    from gui.app import main as start_gui

    print("\n📱 Launching GUI Interface...")
    print("   (Use --headless flag for containerized/CLI mode)\n")

    try:
        start_gui()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nPlease ensure all required packages are installed:")
        print("  pip install matplotlib")
        print("  pip install numpy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for the OS Scheduler application.
    Parses arguments and runs either GUI or headless mode.
    """
    parser = argparse.ArgumentParser(
        description="OS Scheduler Simulator - CPU Scheduling with Memory Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Launch GUI
  python main.py --headless               # Run default headless simulation
  python main.py --headless -a fcfs -p simple
  python main.py --headless -a round_robin -p mixed -m 512 --memory-algo best_fit
  python main.py --headless -a mlfq -p memory_stress -m 400 -q 3
        """
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no GUI, output to files)'
    )
    parser.add_argument(
        '-a', '--algorithm',
        choices=['fcfs', 'sjf', 'priority', 'round_robin', 'mlfq'],
        default='fcfs',
        help='Scheduling algorithm to use (default: fcfs)'
    )
    parser.add_argument(
        '-p', '--preset',
        choices=['simple', 'memory_stress', 'mixed'],
        default='simple',
        help='Process workload preset (default: simple)'
    )
    parser.add_argument(
        '-m', '--memory-total',
        type=int,
        default=512,
        help='Total memory size in abstract units (default: 512)'
    )
    parser.add_argument(
        '--memory-algo',
        choices=['first_fit', 'best_fit', 'worst_fit'],
        default='first_fit',
        help='Memory allocation algorithm (default: first_fit)'
    )
    parser.add_argument(
        '-q', '--quantum',
        type=int,
        default=2,
        help='Time quantum for Round Robin / MLFQ (default: 2)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory for headless mode files (default: output)'
    )

    args = parser.parse_args()

    print_banner()

    if args.headless:
        run_headless(args)
    else:
        run_gui()


if __name__ == "__main__":
    main()
