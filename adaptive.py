"""
Adaptive Scheduling Feature Module.
Provides algorithm recommendations and dynamic switching suggestions
based on workload characteristics.
"""


class AdaptiveScheduler:
    """
    Analyzes workload characteristics and provides recommendations
    for optimal scheduling algorithms.
    """
    
    def __init__(self):
        """Initialize the adaptive scheduler with algorithm characteristics."""
        self.algorithm_profiles = {
            'fcfs': {
                'name': 'First Come First Served',
                'best_for': ['uniform burst times', 'fair scheduling'],
                'pros': ['simple', 'fair', 'minimal overhead'],
                'cons': ['convoy effect', 'poor average waiting time'],
                'cpu_io_friendly': False,
            },
            'sjf': {
                'name': 'Shortest Job First',
                'best_for': ['short jobs', 'minimizing waiting time'],
                'pros': ['optimal average waiting time', 'good throughput'],
                'cons': ['starvation risk', 'requires job length prediction'],
                'cpu_io_friendly': True,
            },
            'priority': {
                'name': 'Priority Scheduling',
                'best_for': ['mixed workloads', 'differentiated service'],
                'pros': ['flexible', 'supports differentiation', 'real-time compatible'],
                'cons': ['starvation risk', 'priority assignment complexity'],
                'cpu_io_friendly': True,
            },
            'round_robin': {
                'name': 'Round Robin',
                'best_for': ['timesharing', 'interactive systems', 'fairness'],
                'pros': ['prevents starvation', 'fair', 'responsive'],
                'cons': ['higher overhead', 'poor if quantum too small/large'],
                'cpu_io_friendly': True,
            },
            'mlfq': {
                'name': 'Multi-Level Feedback Queue',
                'best_for': ['mixed workloads', 'adaptive scheduling', 'unknown job lengths'],
                'pros': ['adapts to workload', 'prevents starvation', 'responsive I/O'],
                'cons': ['complex', 'many parameters', 'higher overhead'],
                'cpu_io_friendly': True,
            }
        }
        
    def analyze_workload(self, processes):
        """
        Analyze process characteristics to recommend algorithms.
        
        Args:
            processes (list): List of process dicts with keys: pid, arrival, burst, priority
            
        Returns:
            dict: Analysis results and recommendations
        """
        if not processes:
            return {'error': 'No processes provided'}
            
        analysis = {
            'total_processes': len(processes),
            'burst_times': [p['burst'] for p in processes],
            'arrival_times': [p['arrival'] for p in processes],
            'priorities': [p.get('priority', 0) for p in processes],
        }
        
        # Calculate statistics
        analysis['avg_burst'] = sum(analysis['burst_times']) / len(analysis['burst_times'])
        analysis['max_burst'] = max(analysis['burst_times'])
        analysis['min_burst'] = min(analysis['burst_times'])
        analysis['burst_variance'] = self._calculate_variance(analysis['burst_times'])
        analysis['total_arrival_span'] = max(analysis['arrival_times']) - min(analysis['arrival_times'])
        analysis['has_priorities'] = len(set(analysis['priorities'])) > 1
        
        # Determine workload characteristics
        analysis['characteristics'] = self._identify_characteristics(analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
        
    def _calculate_variance(self, values):
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
        
    def _identify_characteristics(self, analysis):
        """Identify key characteristics of the workload."""
        characteristics = []
        
        # Check for uniform vs varied burst times
        if analysis['burst_variance'] < 2:
            characteristics.append('Uniform burst times')
        elif analysis['burst_variance'] > 50:
            characteristics.append('Highly varied burst times')
        else:
            characteristics.append('Mixed burst times')
            
        # Check for short vs long jobs
        if analysis['avg_burst'] < 5:
            characteristics.append('Short jobs')
        elif analysis['avg_burst'] > 15:
            characteristics.append('Long jobs')
        else:
            characteristics.append('Medium-length jobs')
            
        # Check for arrival pattern
        if analysis['total_arrival_span'] < 5:
            characteristics.append('Clustered arrivals')
        else:
            characteristics.append('Spread arrivals')
            
        # Check for priority differentiation
        if analysis['has_priorities']:
            characteristics.append('Prioritized workload')
        else:
            characteristics.append('Non-prioritized workload')
            
        return characteristics
        
    def _generate_recommendations(self, analysis):
        """Generate algorithm recommendations based on workload."""
        recommendations = []
        
        characteristics = analysis['characteristics']
        
        # Rule 1: Short jobs with varied timing → SJF
        if 'Short jobs' in characteristics and 'Mixed burst times' in characteristics:
            recommendations.append({
                'algorithm': 'sjf',
                'score': 0.95,
                'reason': 'Excellent for short jobs with minimized waiting time'
            })
            
        # Rule 2: Prioritized workload → Priority or MLFQ
        if 'Prioritized workload' in characteristics:
            recommendations.append({
                'algorithm': 'priority',
                'score': 0.90,
                'reason': 'Direct priority handling for differentiated workload'
            })
            recommendations.append({
                'algorithm': 'mlfq',
                'score': 0.85,
                'reason': 'Adaptive scheduling with multi-level priority queues'
            })
            
        # Rule 3: Clustered arrivals with varied times → FCFS or RR
        if 'Clustered arrivals' in characteristics:
            recommendations.append({
                'algorithm': 'fcfs',
                'score': 0.80,
                'reason': 'Fair scheduling for simultaneous arrivals'
            })
            
        # Rule 4: Long jobs with varied times → MLFQ
        if 'Long jobs' in characteristics and 'Highly varied burst times' in characteristics:
            recommendations.append({
                'algorithm': 'mlfq',
                'score': 0.92,
                'reason': 'Prevents starvation and adapts to varying job characteristics'
            })
            
        # Rule 5: Interactive/fair behavior needed → Round Robin
        if 'Spread arrivals' in characteristics:
            recommendations.append({
                'algorithm': 'round_robin',
                'score': 0.88,
                'reason': 'Fair scheduling with prevention of starvation'
            })
            
        # Rule 6: Uniform burst times → FCFS (simple and effective)
        if 'Uniform burst times' in characteristics:
            recommendations.append({
                'algorithm': 'fcfs',
                'score': 0.90,
                'reason': 'Optimal for uniform workloads with minimal overhead'
            })
            
        # Default: MLFQ is always a good choice
        if not recommendations:
            recommendations.append({
                'algorithm': 'mlfq',
                'score': 0.80,
                'reason': 'Adaptive algorithm suitable for general workloads'
            })
            
        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
        
    def suggest_algorithm_switch(self, current_algorithm, processes):
        """
        Suggest if and when to switch algorithms.
        
        Args:
            current_algorithm (str): Currently running algorithm
            processes (list): List of process dicts
            
        Returns:
            dict: Switch recommendation with details
        """
        analysis = self.analyze_workload(processes)
        recommendations = analysis.get('recommendations', [])
        
        if not recommendations:
            return {'should_switch': False, 'reason': 'Current algorithm suitable'}
            
        best = recommendations[0]
        
        if best['algorithm'] == current_algorithm:
            return {
                'should_switch': False,
                'reason': f'Current algorithm ({current_algorithm}) is optimal',
                'score': best['score']
            }
        else:
            return {
                'should_switch': True,
                'current_algorithm': current_algorithm,
                'recommended_algorithm': best['algorithm'],
                'score': best['score'],
                'reason': best['reason'],
                'top_3_recommendations': recommendations[:3]
            }
            
    def get_algorithm_info(self, algorithm):
        """
        Get detailed information about an algorithm.
        
        Args:
            algorithm (str): Algorithm name
            
        Returns:
            dict: Detailed algorithm information
        """
        return self.algorithm_profiles.get(algorithm, {})
        
    def compare_algorithms(self, algorithm_list):
        """
        Compare multiple algorithms.
        
        Args:
            algorithm_list (list): List of algorithm names to compare
            
        Returns:
            dict: Comparison table
        """
        comparison = {
            'algorithms': [],
            'criteria': ['Simplicity', 'Fairness', 'Throughput', 'Response Time', 'Starvation Risk']
        }
        
        scores = {
            'fcfs': {'Simplicity': 5, 'Fairness': 4, 'Throughput': 3, 'Response Time': 2, 'Starvation Risk': 5},
            'sjf': {'Simplicity': 3, 'Fairness': 2, 'Throughput': 5, 'Response Time': 4, 'Starvation Risk': 1},
            'priority': {'Simplicity': 3, 'Fairness': 2, 'Throughput': 4, 'Response Time': 5, 'Starvation Risk': 1},
            'round_robin': {'Simplicity': 4, 'Fairness': 5, 'Throughput': 3, 'Response Time': 5, 'Starvation Risk': 5},
            'mlfq': {'Simplicity': 2, 'Fairness': 4, 'Throughput': 4, 'Response Time': 5, 'Starvation Risk': 5},
        }
        
        for algo in algorithm_list:
            if algo in scores:
                comparison['algorithms'].append({
                    'name': algo,
                    'scores': scores[algo]
                })
                
        return comparison


# Example usage
if __name__ == "__main__":
    adaptive = AdaptiveScheduler()
    
    # Test workload
    processes = [
        {'pid': 'P1', 'arrival': 0, 'burst': 3, 'priority': 1},
        {'pid': 'P2', 'arrival': 1, 'burst': 2, 'priority': 1},
        {'pid': 'P3', 'arrival': 2, 'burst': 5, 'priority': 2},
        {'pid': 'P4', 'arrival': 4, 'burst': 2, 'priority': 1},
    ]
    
    analysis = adaptive.analyze_workload(processes)
    print("Workload Analysis:")
    print(f"  Characteristics: {analysis['characteristics']}")
    print(f"  Top Recommendations: {analysis['recommendations'][:2]}")
    
    suggestion = adaptive.suggest_algorithm_switch('fcfs', processes)
    print("\nSwitch Suggestion:")
    print(f"  Should Switch: {suggestion['should_switch']}")
    if suggestion['should_switch']:
        print(f"  Recommended: {suggestion['recommended_algorithm']}")
        print(f"  Reason: {suggestion['reason']}")
