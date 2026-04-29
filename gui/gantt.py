"""
Gantt Chart visualization module for OS Scheduler.
Provides real-time, color-coded Gantt chart rendering with dynamic updates.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
from datetime import datetime
import numpy as np


class GanttChart:
    """
    A real-time Gantt chart visualization for CPU scheduling processes.
    
    Features:
    - Color-coded process visualization
    - Dynamic updates as processes run
    - Process ID labels and time axis
    - Support for real-time process addition/updates
    - Interactive matplotlib figure with zooming/panning
    """
    
    def __init__(self, title="OS Scheduler - Gantt Chart", figsize=(14, 7)):
        """
        Initialize the Gantt Chart.
        
        Args:
            title (str): Title of the chart
            figsize (tuple): Figure size (width, height)
        """
        self.title = title
        self.figsize = figsize
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.processes = []
        self.process_names = {}  # Maps pid to unique position on y-axis
        self.color_map = {}      # Maps pid to color
        self.y_pos = 0
        self.max_time = 0
        
        # Configure the plot
        self._setup_plot()
        
    def _setup_plot(self):
        """Configure matplotlib plot settings."""
        self.ax.set_xlabel('Time (units)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Process ID', fontsize=12, fontweight='bold')
        self.ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
        self.ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
    def add_process(self, pid, start, end, color=None):
        """
        Add a single process to the Gantt chart.
        
        Args:
            pid (str/int): Process ID
            start (int/float): Start time
            end (int/float): End time
            color (str): Hex color code or matplotlib color name
        """
        if pid not in self.process_names:
            self.process_names[pid] = self.y_pos
            self.y_pos += 1
            
        if color is None:
            # Auto-generate color if not provided
            color = self._get_auto_color(pid)
            
        self.color_map[pid] = color
        self.processes.append({
            'pid': pid,
            'start': start,
            'end': end,
            'color': color
        })
        
        # Update max time for x-axis
        self.max_time = max(self.max_time, end)
        
    def add_processes(self, gantt_data):
        """
        Add multiple processes from gantt data.
        
        Args:
            gantt_data (list): List of dicts with keys: pid, start, end, color
                               Example: [{'pid': 'P1', 'start': 0, 'end': 8, 'color': '#FF5733'}, ...]
        """
        for process in gantt_data:
            self.add_process(
                pid=process['pid'],
                start=process['start'],
                end=process['end'],
                color=process.get('color', None)
            )
            
    def _get_auto_color(self, pid):
        """Generate a unique color for each process."""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AED6F1'
        ]
        pid_hash = hash(str(pid)) % len(colors)
        return colors[pid_hash]
        
    def render(self, save_path=None):
        """
        Render the Gantt chart.
        
        Args:
            save_path (str, optional): Path to save the chart image
        """
        if not self.processes:
            print("No processes to render. Add processes using add_process() or add_processes().")
            return
            
        self.ax.clear()
        self._setup_plot()
        
        # Draw each process as a horizontal bar
        for process in self.processes:
            pid = process['pid']
            y_position = self.process_names[pid]
            duration = process['end'] - process['start']
            
            # Draw the process bar
            self.ax.barh(
                y=y_position,
                width=duration,
                left=process['start'],
                height=0.6,
                color=process['color'],
                edgecolor='black',
                linewidth=1.5,
                alpha=0.85
            )
            
            # Add process ID label in the middle of the bar
            mid_point = process['start'] + duration / 2
            self.ax.text(
                mid_point,
                y_position,
                str(pid),
                ha='center',
                va='center',
                fontweight='bold',
                fontsize=10,
                color='black'
            )
        
        # Set y-axis with process IDs
        y_ticks = list(range(self.y_pos))
        y_labels = [str(pid) for pid in self.process_names.keys()]
        # Sort by y position to display correctly
        sorted_pids = sorted(self.process_names.items(), key=lambda x: x[1])
        y_labels = [str(pid[0]) for pid in sorted_pids]
        
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(y_labels)
        
        # Set x-axis limits with some padding
        self.ax.set_xlim(0, max(self.max_time * 1.1, 10))
        self.ax.set_ylim(-1, self.y_pos)
        
        # Add grid
        self.ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        self.ax.invert_yaxis()  # Invert so first process is at top
        
        # Tight layout
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
            
    def show(self):
        """Display the Gantt chart in a window."""
        self.render()
        plt.show()
        
    def update_process(self, pid, end_time, color=None):
        """
        Update an existing process (for real-time simulation).
        
        Args:
            pid (str/int): Process ID
            end_time (int/float): New end time
            color (str, optional): New color
        """
        for process in self.processes:
            if process['pid'] == pid:
                process['end'] = end_time
                if color:
                    process['color'] = color
                self.max_time = max(self.max_time, end_time)
                return True
        return False
        
    def clear(self):
        """Clear all processes and reset the chart."""
        self.processes = []
        self.process_names = {}
        self.color_map = {}
        self.y_pos = 0
        self.max_time = 0
        self.ax.clear()
        self._setup_plot()
        
    def export_data(self):
        """
        Export the current Gantt data as a list of dictionaries.
        
        Returns:
            list: Gantt data in format [{'pid': ..., 'start': ..., 'end': ..., 'color': ...}, ...]
        """
        return [p.copy() for p in self.processes]
        
    def animate_simulation(self, gantt_data_stream, update_interval=500):
        """
        Animate the Gantt chart with real-time process updates.
        
        Args:
            gantt_data_stream (generator or list): Stream of process data or complete list
            update_interval (int): Milliseconds between updates
        """
        # If it's a list, convert to generator
        if isinstance(gantt_data_stream, list):
            gantt_data = gantt_data_stream
            self.add_processes(gantt_data)
            self.render()
            return
            
        # Otherwise, treat as streaming data
        if callable(gantt_data_stream):
            self.render()
            plt.show()
        
    def get_html_representation(self):
        """
        Get HTML representation of the Gantt chart for web display.
        
        Returns:
            str: HTML table representation
        """
        html = "<table border='1' cellpadding='5'>\n"
        html += "<tr><th>Process ID</th><th>Start Time</th><th>End Time</th><th>Duration</th></tr>\n"
        
        for process in self.processes:
            duration = process['end'] - process['start']
            html += f"<tr><td>{process['pid']}</td><td>{process['start']}</td>"
            html += f"<td>{process['end']}</td><td>{duration}</td></tr>\n"
            
        html += "</table>"
        return html


# Example usage and testing
if __name__ == "__main__":
    # Test data from scheduling algorithms
    gantt_data = [
        {'pid': 'P1', 'start': 0, 'end': 8, 'color': '#FF6B6B'},
        {'pid': 'P2', 'start': 8, 'end': 16, 'color': '#4ECDC4'},
        {'pid': 'P3', 'start': 16, 'end': 24, 'color': '#45B7D1'},
        {'pid': 'P4', 'start': 24, 'end': 27, 'color': '#FFA07A'},
    ]
    
    # Create and render Gantt chart
    gantt = GanttChart("FCFS Scheduling")
    gantt.add_processes(gantt_data)
    gantt.show()
    
    # Print statistics
    print(gantt.get_statistics())
