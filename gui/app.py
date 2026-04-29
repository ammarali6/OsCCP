"""
Main GUI Application for OS Scheduler.
Tkinter-based interface for process scheduling simulation with real-time visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import fcfs, sjf, priority, round_robin, mlfq
from metrics import MetricsCalculator
from adaptive import AdaptiveScheduler
from gui.gantt import GanttChart


class OSSchedulerGUI:
    """
    Main GUI application for OS Scheduler simulation.
    
    Features:
    - Dynamic process input (arrival, burst, priority)
    - Multiple algorithm selection
    - Real-time simulation with pause/resume
    - Live Gantt chart visualization
    - Metrics calculation and display
    - Adaptive algorithm recommendations
    """
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("OS Scheduler Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize data structures
        self.processes = []
        self.process_counter = 0
        self.current_algorithm = 'fcfs'
        self.simulation_state = 'idle'  # idle, running, paused
        self.results = None
        self.gantt_data = None
        self.gantt_chart = None
        self.adaptive = AdaptiveScheduler()
        
        # Color palette for processes
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AED6F1',
            '#FF8C94', '#A8E6CF', '#FFD3B6', '#FFAAA5', '#AA96DA'
        ]
        
        # Setup GUI layout
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Create main frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input and controls
        left_frame = ttk.LabelFrame(self.main_frame, text="Process Management", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Right panel - Results and visualization
        right_frame = ttk.LabelFrame(self.main_frame, text="Simulation Results", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._setup_input_panel(left_frame)
        self._setup_results_panel(right_frame)
        
    def _setup_input_panel(self, parent):
        """Setup the input panel for process creation."""
        # Process input section
        input_frame = ttk.LabelFrame(parent, text="Add Process", padding=8)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Arrival Time:").pack(anchor=tk.W)
        self.arrival_input = ttk.Entry(input_frame, width=20)
        self.arrival_input.pack(fill=tk.X, pady=(0, 5))
        self.arrival_input.insert(0, "0")
        
        ttk.Label(input_frame, text="Burst Time:").pack(anchor=tk.W)
        self.burst_input = ttk.Entry(input_frame, width=20)
        self.burst_input.pack(fill=tk.X, pady=(0, 5))
        self.burst_input.insert(0, "5")
        
        ttk.Label(input_frame, text="Priority (1=High):").pack(anchor=tk.W)
        self.priority_input = ttk.Entry(input_frame, width=20)
        self.priority_input.pack(fill=tk.X, pady=(0, 10))
        self.priority_input.insert(0, "1")
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="Add Process", command=self._add_process).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self._clear_processes).pack(side=tk.LEFT)
        
        # Process list
        list_frame = ttk.LabelFrame(parent, text="Processes", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.process_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, bg='white')
        self.process_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_list.yview)
        
        # Remove button
        ttk.Button(parent, text="Remove Selected", command=self._remove_process).pack(fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(parent, text="Algorithm Selection", padding=8)
        algo_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.algo_var = tk.StringVar(value='fcfs')
        algorithms = [
            ('FCFS', 'fcfs'),
            ('SJF (Non-Preemptive)', 'sjf'),
            ('Priority', 'priority'),
            ('Round Robin', 'round_robin'),
            ('MLFQ', 'mlfq')
        ]
        
        for label, value in algorithms:
            ttk.Radiobutton(algo_frame, text=label, variable=self.algo_var, value=value,
                          command=self._on_algorithm_change).pack(anchor=tk.W)
        
        # Quantum (for Round Robin/MLFQ)
        ttk.Label(algo_frame, text="Time Quantum (RR/MLFQ):").pack(anchor=tk.W, pady=(10, 0))
        self.quantum_input = ttk.Entry(algo_frame, width=10)
        self.quantum_input.pack(anchor=tk.W)
        self.quantum_input.insert(0, "2")
        
        # Simulation controls
        control_frame = ttk.LabelFrame(parent, text="Simulation Control", padding=8)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(fill=tk.X, pady=(0, 5))
        
        self.start_btn = ttk.Button(button_frame2, text="▶ Start", command=self._start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(button_frame2, text="⏸ Pause", command=self._pause_simulation, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.resume_btn = ttk.Button(button_frame2, text="▶ Resume", command=self._resume_simulation, state=tk.DISABLED)
        self.resume_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_btn = ttk.Button(button_frame2, text="🔄 Reset", command=self._reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Idle", foreground='blue')
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Adaptive recommendations
        rec_frame = ttk.LabelFrame(parent, text="AI Recommendations", padding=8)
        rec_frame.pack(fill=tk.X)
        
        self.recommendation_text = tk.Text(rec_frame, height=6, width=30, wrap=tk.WORD, bg='white')
        self.recommendation_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(rec_frame, text="Get Recommendations", command=self._show_recommendations).pack(fill=tk.X, pady=(5, 0))
        
    def _setup_results_panel(self, parent):
        """Setup the results display panel."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="📊 Metrics")
        self._setup_metrics_tab(metrics_frame)
        
        # Gantt chart tab
        gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(gantt_frame, text="📈 Gantt Chart")
        self._setup_gantt_tab(gantt_frame)
        
        # Process details tab
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="📋 Details")
        self._setup_details_tab(details_frame)
        
    def _setup_metrics_tab(self, parent):
        """Setup metrics display tab."""
        self.metrics_text = tk.Text(parent, wrap=tk.WORD, bg='white', font=('Courier', 10))
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.metrics_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_text.config(yscrollcommand=scrollbar.set)
        
    def _setup_gantt_tab(self, parent):
        """Setup Gantt chart display tab."""
        self.gantt_label = ttk.Label(parent, text="Run simulation to generate Gantt chart", 
                                     foreground='gray', font=('Arial', 10))
        self.gantt_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Show Gantt Chart", command=self._show_gantt_chart).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save Chart", command=self._save_gantt_chart).pack(side=tk.LEFT, padx=2)
        
    def _setup_details_tab(self, parent):
        """Setup process details tab."""
        self.details_text = tk.Text(parent, wrap=tk.WORD, bg='white', font=('Courier', 9))
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.details_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=scrollbar.set)
        
    def _add_process(self):
        """Add a new process to the list."""
        try:
            arrival = int(self.arrival_input.get())
            burst = int(self.burst_input.get())
            priority = int(self.priority_input.get())
            
            if burst <= 0:
                messagebox.showerror("Error", "Burst time must be positive")
                return
                
            self.process_counter += 1
            pid = f"P{self.process_counter}"
            color = self.colors[self.process_counter % len(self.colors)]
            
            process = {
                'pid': pid,
                'arrival': arrival,
                'burst': burst,
                'priority': priority,
                'color': color
            }
            
            self.processes.append(process)
            self.process_list.insert(tk.END, f"{pid}: Arr={arrival}, Burst={burst}, Pri={priority}")
            
            # Clear inputs
            self.arrival_input.delete(0, tk.END)
            self.burst_input.delete(0, tk.END)
            self.arrival_input.insert(0, str(arrival + 1))
            self.burst_input.insert(0, "5")
            self.priority_input.insert(0, "1")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            
    def _remove_process(self):
        """Remove selected process from list."""
        selection = self.process_list.curselection()
        if selection:
            idx = selection[0]
            self.process_list.delete(idx)
            self.processes.pop(idx)
            
    def _clear_processes(self):
        """Clear all processes."""
        self.process_list.delete(0, tk.END)
        self.processes.clear()
        self.process_counter = 0
        
    def _on_algorithm_change(self):
        """Handle algorithm selection change."""
        self.current_algorithm = self.algo_var.get()
        
    def _start_simulation(self):
        """Start the simulation."""
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process")
            return
            
        try:
            algo = self.current_algorithm
            quantum = int(self.quantum_input.get()) if algo in ['round_robin', 'mlfq'] else None
            
            # Run selected algorithm
            if algo == 'fcfs':
                result, gantt = fcfs.run_fcfs(self.processes)
            elif algo == 'sjf':
                result, gantt = sjf.run_sjf_non_preemptive(self.processes)
            elif algo == 'priority':
                result, gantt = priority.run_priority(self.processes)
            elif algo == 'round_robin':
                result, gantt = round_robin.run_round_robin(self.processes, quantum=quantum)
            elif algo == 'mlfq':
                result, gantt = mlfq.run_mlfq(self.processes, q0=quantum, q1=quantum*2)
            else:
                raise ValueError("Unknown algorithm")
                
            self.results = result
            self.gantt_data = gantt
            self.simulation_state = 'running'
            
            # Display results
            self._display_metrics()
            self._display_details()
            
            # Update UI
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Simulation Complete ✓", foreground='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
            
    def _pause_simulation(self):
        """Pause the simulation."""
        self.simulation_state = 'paused'
        self.status_label.config(text="Status: Paused", foreground='orange')
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.NORMAL)
        
    def _resume_simulation(self):
        """Resume the simulation."""
        self.simulation_state = 'running'
        self.status_label.config(text="Status: Running", foreground='blue')
        self.resume_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        
    def _reset_simulation(self):
        """Reset the simulation."""
        self.results = None
        self.gantt_data = None
        self.simulation_state = 'idle'
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete('1.0', tk.END)
        self.metrics_text.config(state=tk.DISABLED)
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.config(state=tk.DISABLED)
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle", foreground='blue')
        
    def _display_metrics(self):
        """Display calculated metrics."""
        if not self.results:
            return
            
        try:
            calc = MetricsCalculator(self.results)
            metrics = calc.get_all_metrics()
            
            report = calc.get_summary_report()
            
            self.metrics_text.config(state=tk.NORMAL)
            self.metrics_text.delete('1.0', tk.END)
            self.metrics_text.insert('1.0', report)
            self.metrics_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Metrics calculation failed: {str(e)}")
            
    def _display_details(self):
        """Display detailed process information."""
        if not self.results:
            return
            
        details = f"{'PID':<6} {'Arr':<5} {'Burst':<6} {'Start':<7} {'Finish':<8} {'Wait':<6} {'TAT':<6}\n"
        details += "─" * 50 + "\n"
        
        for p in self.results:
            details += f"{p['pid']:<6} {p['arrival']:<5} {p['burst']:<6} {p['start']:<7} {p['finish']:<8} {p['waiting']:<6} {p['turnaround']:<6}\n"
            
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details)
        self.details_text.config(state=tk.DISABLED)
        
    def _show_gantt_chart(self):
        """Display the Gantt chart."""
        if not self.gantt_data:
            messagebox.showwarning("Warning", "Run a simulation first")
            return
            
        try:
            gantt = GanttChart(f"{self.current_algorithm.upper()} - Gantt Chart")
            gantt.add_processes(self.gantt_data)
            gantt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display Gantt chart: {str(e)}")
            
    def _save_gantt_chart(self):
        """Save the Gantt chart as an image."""
        if not self.gantt_data:
            messagebox.showwarning("Warning", "Run a simulation first")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filename:
            try:
                gantt = GanttChart(f"{self.current_algorithm.upper()} - Gantt Chart")
                gantt.add_processes(self.gantt_data)
                gantt.render(save_path=filename)
                messagebox.showinfo("Success", f"Chart saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart: {str(e)}")
                
    def _show_recommendations(self):
        """Show AI-based algorithm recommendations."""
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process")
            return
            
        try:
            analysis = self.adaptive.analyze_workload(self.processes)
            recommendations = analysis.get('recommendations', [])
            
            rec_text = "🤖 AI Algorithm Recommendations:\n"
            rec_text += "─" * 40 + "\n\n"
            rec_text += f"Workload Characteristics:\n"
            for char in analysis['characteristics']:
                rec_text += f"  • {char}\n"
                
            rec_text += f"\nTop Recommendations:\n"
            for i, rec in enumerate(recommendations[:3], 1):
                algo_info = self.adaptive.get_algorithm_info(rec['algorithm'])
                rec_text += f"\n{i}. {algo_info.get('name', rec['algorithm'])} (Score: {rec['score']*100:.0f}%)\n"
                rec_text += f"   {rec['reason']}\n"
                
            self.recommendation_text.config(state=tk.NORMAL)
            self.recommendation_text.delete('1.0', tk.END)
            self.recommendation_text.insert('1.0', rec_text)
            self.recommendation_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate recommendations: {str(e)}")


def main():
    """Launch the application."""
    root = tk.Tk()
    app = OSSchedulerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
