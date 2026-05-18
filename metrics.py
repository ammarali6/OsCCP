"""
Metrics Calculator for OS Scheduling Algorithms.
Computes performance metrics such as waiting time, turnaround time, 
CPU utilization, throughput, and memory utilization.
"""


class MetricsCalculator:
    """
    Calculate performance metrics for CPU scheduling algorithms.
    
    Metrics include:
    - Waiting Time (average and per-process)
    - Turnaround Time (average and per-process)
    - CPU Utilization Percentage
    - Throughput (processes per unit time)
    - Memory Utilization (if memory data present)
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
                             - memory_req: Memory required (optional)
                             - memory_allocated: Whether memory was allocated (optional)
                             - memory_wait: Time waiting for memory (optional)
        """
        self.processes = processes
        if not self.processes:
            # Empty process list — create a safe empty calculator
            self._empty = True
            return
        self._empty = False
        self._validate_processes()
        self._compute_times()
        
    def _validate_processes(self):
        """Validate that all required fields are present."""
        if self._empty:
            return
            
        required_fields = {'pid', 'arrival', 'burst', 'start', 'finish'}
        for i, p in enumerate(self.processes):
            if not isinstance(p, dict):
                raise TypeError(f"Process {i} must be a dictionary")
            missing = required_fields - set(p.keys())
            if missing:
                raise ValueError(f"Process {i} missing fields: {missing}")
                
    def _compute_times(self):
        """Calculate waiting and turnaround times if not already present."""
        if self._empty:
            return
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
        if self._empty:
            return []
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
        if self._empty or not self.processes:
            return 0
        total_waiting = sum(p['waiting'] for p in self.processes)
        return round(total_waiting / len(self.processes), 2)
        
    def get_turnaround_times(self):
        """
        Get turnaround time for each process.
        
        Returns:
            list: List of dicts with format [{'pid': ..., 'turnaround_time': ...}, ...]
        """
        if self._empty:
            return []
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
        if self._empty or not self.processes:
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
        if self._empty or not self.processes:
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
        if self._empty or not self.processes:
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
        
    def get_memory_wait_times(self):
        """
        Get memory wait time for each process.
        
        Returns:
            list: List of dicts with format [{'pid': ..., 'memory_wait': ...}, ...]
        """
        if self._empty:
            return []
        return [
            {'pid': p['pid'], 'memory_wait': p.get('memory_wait', 0)}
            for p in self.processes
        ]
        
    def get_average_memory_wait_time(self):
        """
        Calculate average memory wait time.
        
        Returns:
            float: Average memory wait time
        """
        if self._empty or not self.processes:
            return 0
        total = sum(p.get('memory_wait', 0) for p in self.processes)
        return round(total / len(self.processes), 2)
        
    def get_memory_allocated_count(self):
        """
        Get count of processes that successfully got memory allocated.
        
        Returns:
            tuple: (allocated_count, total_count)
        """
        if self._empty or not self.processes:
            return 0, 0
        allocated = sum(1 for p in self.processes if p.get('memory_allocated'))
        return allocated, len(self.processes)
        
    def get_all_metrics(self):
        """
        Get all metrics in a single dictionary.
        
        Returns:
            dict: Comprehensive metrics dictionary with all calculations
        """
        if self._empty:
            return {
                'algorithm_info': {'total_processes': 0, 'total_cpu_time': 0},
                'waiting_time': {'per_process': [], 'average': 0},
                'turnaround_time': {'per_process': [], 'average': 0},
                'cpu_utilization': 0,
                'throughput': 0,
                'memory': {
                    'avg_memory_wait': 0,
                    'allocated_count': 0,
                    'total_count': 0,
                },
                'process_details': [],
            }
            
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
            'memory': {
                'avg_memory_wait': self.get_average_memory_wait_time(),
                'allocated_count': self.get_memory_allocated_count()[0],
                'total_count': self.get_memory_allocated_count()[1],
            },
            'process_details': self._get_detailed_process_info(),
        }
        return metrics
        
    def _get_detailed_process_info(self):
        """
        Get detailed information for each process.
        
        Returns:
            list: List of process details
        """
        if self._empty:
            return []
        return [
            {
                'pid': p['pid'],
                'arrival': p['arrival'],
                'burst': p['burst'],
                'start': p['start'],
                'finish': p['finish'],
                'waiting': p['waiting'],
                'turnaround': p['turnaround'],
                'memory_req': p.get('memory_req', 0),
                'memory_allocated': p.get('memory_allocated', False),
                'memory_wait': p.get('memory_wait', 0),
            }
            for p in self.processes
        ]
        
    def get_summary_report(self):
        """
        Get a human-readable summary report.
        
        Returns:
            str: Formatted summary report
        """
        if self._empty:
            return "No processes to report."
            
        avg_wt = self.get_average_waiting_time()
        avg_tat = self.get_average_turnaround_time()
        cpu_util = self.get_cpu_utilization()
        throughput = self.get_throughput()
        avg_mem_wait = self.get_average_memory_wait_time()
        alloc_count, total_count = self.get_memory_allocated_count()
        
        report = f"""
╔══════════════════════════════════════════════════╗
║           SCHEDULING METRICS REPORT              ║
╚══════════════════════════════════════════════════╝

📊 Process Summary:
   Total Processes: {len(self.processes)}
   Total CPU Time:  {sum(p['burst'] for p in self.processes)} units
   Memory Allocated: {alloc_count}/{total_count}

⏱️  Waiting Time:
   Average Waiting Time: {avg_wt} units

📈 Turnaround Time:
   Average Turnaround Time: {avg_tat} units

💻 CPU Utilization:
   Utilization: {cpu_util}%

🧠 Memory Metrics:
   Avg Memory Wait: {avg_mem_wait} units
   Allocated: {alloc_count}/{total_count} processes

🚀 Throughput:
   Processes/Time Unit: {throughput}

─────────────────────────────────────────────────────
Process Details:
"""
        
        for p in self.processes:
            mem_info = f"MemReq={p.get('memory_req', 0)}, Alloc={'Yes' if p.get('memory_allocated') else 'No'}"
            report += f"\n   {p['pid']:>4} | Arr: {p['arrival']:>3} | Burst: {p['burst']:>3} | "
            report += f"Start: {p['start']:>3} | Finish: {p['finish']:>3} | "
            report += f"Waiting: {p['waiting']:>3} | TAT: {p['turnaround']:>3} | {mem_info}"
            
        return report


# Example usage and testing
if __name__ == "__main__":
    # Test data from a scheduling algorithm
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 8, 'start': 0, 'finish': 8, 'memory_req': 128, 'memory_allocated': True, 'memory_wait': 0},
        {'pid': 'P2', 'arrival': 1, 'burst': 4, 'start': 8, 'finish': 12, 'memory_req': 64, 'memory_allocated': True, 'memory_wait': 0},
        {'pid': 'P3', 'arrival': 2, 'burst': 2, 'start': 12, 'finish': 14, 'memory_req': 32, 'memory_allocated': True, 'memory_wait': 0},
        {'pid': 'P4', 'arrival': 3, 'burst': 1, 'start': 14, 'finish': 15, 'memory_req': 16, 'memory_allocated': False, 'memory_wait': 5},
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
