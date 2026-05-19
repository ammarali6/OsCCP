Operating Systems
BS (AI)-6(A)
CCP Deliverable 3: Concurrency, IPC & Final Performance Evaluation 
Focus
Extending the simulator with concurrency models, IPC mechanisms, and comparative performance analysis.
Objectives
    • Implement concurrent execution models 
    • Introduce IPC mechanisms 
    • Compare multi-threading vs multi-processing 
    • Generate final performance analysis reports 
Implementation Requirements
1. Concurrency Module
Implement:
Multi-threading
    • Simulate processes using threads 
Multi-processing
    • Simulate processes using: 
fork()
Comparative Analysis
Compare:
    • Execution speed 
    • Context switching overhead 
    • Resource sharing 
    • CPU utilization 

2. Inter-Process Communication (IPC)
Implement at least TWO IPC techniques:
    • Pipes 
    • Shared Memory 
    • Message Queues 
Usage
Use IPC for:
    • Communication between scheduler and worker processes 
    • Sharing scheduling statistics 
    • Updating visualization modules 

3. Advanced Scheduling Experiments
Perform experiments for:
Different Workloads
    • CPU-bound processes 
    • I/O-bound processes 
    • Mixed workloads 
Different Algorithms
Compare:
    • FCFS 
    • SJF 
    • RR 
    • Priority Scheduling 
    • MLFQ 

4. Comparative Performance Evaluation
Students must compare:
Comparison Area	Required Analysis
Algorithms	Waiting time, turnaround time
Threads vs Processes	Overhead & performance
Host vs Docker	Resource usage
Low vs High Memory	Scheduling impact
CPU Limits	Throughput effects

5. Final Reporting & Visualization
Generate:
    • Performance graphs 
    • Comparison charts 
    • Gantt charts 
    • Memory utilization charts 
Final Report Should Include
    • Architecture diagram 
    • Scheduling comparison 
    • Docker experimentation 
    • Memory management observations 
    • IPC explanation 
    • Concurrency analysis 
    • Challenges faced 
    • Conclusion 

Deliverable Output
Students must submit:
1. Final Working Application
Including:
    • Scheduling simulator 
    • Docker integration 
    • Memory management module 
    • IPC implementation 
    • Concurrency support 
2. Source Code
Well-structured and documented.
3. Demonstration
Students must demonstrate:
    • Thread vs process execution 
    • IPC communication 
    • Dockerized execution 
    • Resource-constrained experiments 
4. Final Project Report
Include:
    • Screenshots 
    • Experiment results 
    • Graphs/charts 
    • Comparative analysis 
    • Conclusion 
Suggested Simplification for One-Week Timeline
To keep workload manageable, students may:
    • Use simple GUI frameworks 
    • Simulate memory management visually instead of implementing full virtual memory 
    • Implement only basic Docker commands 
    • Use only two IPC mechanisms 
    • Perform limited experiments with small datasets 
    • Use static graphs/charts if real-time analytics become difficult 
