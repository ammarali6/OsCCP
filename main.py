"""
OS Scheduler Simulator - Main Entry Point

This is the main application launcher for the OS Scheduler Simulator.
It orchestrates all components including:
- Scheduling Algorithms (FCFS, SJF, Priority, Round Robin, MLFQ)
- GUI Interface (Tkinter)
- Gantt Chart Visualization (Matplotlib)
- Performance Metrics Calculation
- Adaptive Algorithm Recommendations

Usage:
    python main.py
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import main as start_gui


def print_banner():
    """Print application banner."""
    banner = """
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║       🖥️  OS SCHEDULER SIMULATOR - DELIVERABLE 1      ║
    ║                                                        ║
    ║  A comprehensive CPU scheduling simulation platform   ║
    ║  with multiple algorithms and real-time metrics       ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    
    Available Scheduling Algorithms:
    • FCFS (First Come First Served)
    • SJF (Shortest Job First - Non-Preemptive)
    • Priority Scheduling (Non-Preemptive)
    • Round Robin (Preemptive)
    • MLFQ (Multi-Level Feedback Queue)
    
    Features:
    ✓ Dynamic process input (Arrival, Burst, Priority)
    ✓ Real-time Gantt chart visualization
    ✓ Performance metrics (Waiting Time, Turnaround, CPU Utilization, Throughput)
    ✓ AI-based algorithm recommendations
    ✓ Simulation control (Start, Pause, Resume, Reset)
    ✓ Export and save results
    """
    print(banner)


def main():
    """
    Main entry point for the OS Scheduler application.
    
    Initializes and launches the Tkinter GUI interface.
    """
    print_banner()
    print("\n📱 Launching GUI Interface...\n")
    
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


if __name__ == "__main__":
    main()

