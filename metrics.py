"""
Metrics Calculator for OS Scheduling Algorithms.
Computes performance metrics such as waiting time, turnaround time, 
CPU utilization, and throughput.
"""


class MetricsCalculator:
    """
    Calculate performance metrics for CPU scheduling algorithms.
    
    Metrics include:
    - Waiting Time (average and per-process)
    - Turnaround Time (average and per-process)
    - CPU Utilization Percentage
    - Throughput (processes per unit time)
    """
    
    def __init__(self, processes):
        """
        Initialize the MetricsCalculator.
        
        Args:
            processes (list): List of completed process dicts with keys:
                             - pid: Process ID
                             - arrival: Arrival time
                             - burst: Burst time (CPU time needed)
                             - start: Start time (when scheduled)
                             - finish: Finish time (when completed)
                             - waiting: Waiting time (optional, calculated if missing)
                             - turnaround: Turnaround time (optional, calculated if missing)
        """
        self.processes = processes
        self._validate_processes()
        self._compute_times()
        
    def _validate_processes(self):
        """Validate that all required fields are present."""
        if not self.processes:
            raise ValueError("Process list cannot be empty")
            
        required_fields = {'pid', 'arrival', 'burst', 'start', 'finish'}
        for i, p in enumerate(self.processes):
            if not isinstance(p, dict):
                raise TypeError(f"Process {i} must be a dictionary")
            missing = required_fields - set(p.keys())
            if missing:
                raise ValueError(f"Process {i} missing fields: {missing}")
                
    def _compute_times(self):
        """Calculate waiting and turnaround times if not already present."""
        for p in self.processes:
            if 'waiting' not in p:
                p['waiting'] = p['start'] - p['arrival']
            if 'turnaround' not in p:
                p['turnaround'] = p['finish'] - p['arrival']
                
    def get_waiting_times(self):
        """
        Get waiting time for each process.
        
        Returns:
            list: List of dicts with format [{'pid': ..., 'waiting_time': ...}, ...]
        """
        return [
            {'pid': p['pid'], 'waiting_time': p['waiting']}
            for p in self.processes
        ]
        
    def get_average_waiting_time(self):
        """
        Calculate average waiting time across all processes.
        
        Returns:
            float: Average waiting time
        """
        if not self.processes:
            return 0
        total_waiting = sum(p['waiting'] for p in self.processes)
        return round(total_waiting / len(self.processes), 2)
        
    def get_turnaround_times(self):
        """
        Get turnaround time for each process.
        
        Returns:
            list: List of dicts with format [{'pid': ..., 'turnaround_time': ...}, ...]
        """
        return [
            {'pid': p['pid'], 'turnaround_time': p['turnaround']}
            for p in self.processes
        ]
        
    def get_average_turnaround_time(self):
        """
        Calculate average turnaround time across all processes.
        
        Returns:
            float: Average turnaround time
        """
        if not self.processes:
            return 0
        total_turnaround = sum(p['turnaround'] for p in self.processes)
        return round(total_turnaround / len(self.processes), 2)
        
    def get_cpu_utilization(self):
        """
        Calculate CPU utilization percentage.
        
        CPU Utilization = (Total CPU Busy Time / Total Available Time) * 100%
        
        Returns:
            float: CPU utilization percentage (0-100)
        """
        if not self.processes:
            return 0
            
        # Total CPU busy time (sum of all burst times)
        total_busy_time = sum(p['burst'] for p in self.processes)
        
        # Total available time (from first arrival to last finish)
        first_arrival = min(p['arrival'] for p in self.processes)
        last_finish = max(p['finish'] for p in self.processes)
        total_available_time = last_finish - first_arrival
        
        if total_available_time == 0:
            return 0
            
        utilization = (total_busy_time / total_available_time) * 100
        return round(utilization, 2)
        
    def get_throughput(self):
        """
        Calculate throughput (processes completed per unit time).
        
        Throughput = Number of Processes / Total Execution Time
        
        Returns:
            float: Throughput (processes per unit time)
        """
        if not self.processes:
            return 0
            
        num_processes = len(self.processes)
        
        # Total execution time (from first arrival to last finish)
        first_arrival = min(p['arrival'] for p in self.processes)
        last_finish = max(p['finish'] for p in self.processes)
        total_time = last_finish - first_arrival
        
        if total_time == 0:
            return 0
            
        throughput = num_processes / total_time
        return round(throughput, 4)
        
    def get_all_metrics(self):
        """
        Get all metrics in a single dictionary.
        
        Returns:
            dict: Comprehensive metrics dictionary with all calculations
        """
        metrics = {
            'algorithm_info': {
                'total_processes': len(self.processes),
                'total_cpu_time': sum(p['burst'] for p in self.processes),
            },
            'waiting_time': {
                'per_process': self.get_waiting_times(),
                'average': self.get_average_waiting_time(),
            },
            'turnaround_time': {
                'per_process': self.get_turnaround_times(),
                'average': self.get_average_turnaround_time(),
            },
            'cpu_utilization': self.get_cpu_utilization(),
            'throughput': self.get_throughput(),
            'process_details': self._get_detailed_process_info(),
        }
        return metrics
        
    def _get_detailed_process_info(self):
        """
        Get detailed information for each process.
        
        Returns:
            list: List of process details
        """
        return [
            {
                'pid': p['pid'],
                'arrival': p['arrival'],
                'burst': p['burst'],
                'start': p['start'],
                'finish': p['finish'],
                'waiting': p['waiting'],
                'turnaround': p['turnaround'],
            }
            for p in self.processes
        ]
        
    def get_summary_report(self):
        """
        Get a human-readable summary report.
        
        Returns:
            str: Formatted summary report
        """
        avg_wt = self.get_average_waiting_time()
        avg_tat = self.get_average_turnaround_time()
        cpu_util = self.get_cpu_utilization()
        throughput = self.get_throughput()
        
        report = f"""
╔══════════════════════════════════════════════════╗
║           SCHEDULING METRICS REPORT              ║
╚══════════════════════════════════════════════════╝

📊 Process Summary:
   Total Processes: {len(self.processes)}
   Total CPU Time:  {sum(p['burst'] for p in self.processes)} units

⏱️  Waiting Time:
   Average Waiting Time: {avg_wt} units

📈 Turnaround Time:
   Average Turnaround Time: {avg_tat} units

💻 CPU Utilization:
   Utilization: {cpu_util}%

🚀 Throughput:
   Processes/Time Unit: {throughput}

─────────────────────────────────────────────────────
Process Details:
"""
        
        for p in self.processes:
            report += f"\n   {p['pid']:>4} | Arrival: {p['arrival']:>3} | Burst: {p['burst']:>3} | "
            report += f"Start: {p['start']:>3} | Finish: {p['finish']:>3} | "
            report += f"Waiting: {p['waiting']:>3} | Turnaround: {p['turnaround']:>3}"
            
        return report


# Example usage and testing
if __name__ == "__main__":
    # Test data from a scheduling algorithm
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 8, 'start': 0, 'finish': 8},
        {'pid': 'P2', 'arrival': 1, 'burst': 4, 'start': 8, 'finish': 12},
        {'pid': 'P3', 'arrival': 2, 'burst': 2, 'start': 12, 'finish': 14},
        {'pid': 'P4', 'arrival': 3, 'burst': 1, 'start': 14, 'finish': 15},
    ]
    
    # Create calculator and get metrics
    calculator = MetricsCalculator(processes)
    metrics = calculator.get_all_metrics()
    
    # Print summary report
    print(calculator.get_summary_report())
    
    # Access individual metrics
    print("\n📋 All Metrics (as dictionary):")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
