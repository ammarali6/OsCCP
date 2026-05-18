Operating Systems
BS (AI)-6(A)
CCP Deliverable 2: Containerization, Memory Management & Resource-Constrained Scheduling 
Focus
Integrating Docker-based deployment, memory management concepts, and resource-aware scheduling into the simulator.
Objectives
    • Extend the scheduling simulator into a containerized environment using Docker 
    • Introduce memory management concepts into process scheduling 
    • Analyze scheduling behavior under CPU and memory constraints 
    • Demonstrate process isolation and monitoring in Linux environments 

Implementation Requirements
1. Docker-Based Deployment
Students must:
    • Create a Dockerfile for the simulator 
    • Build and run the simulator inside Docker containers 
    • Execute multiple instances of the simulator simultaneously 
    • Compare execution: 
        ◦ Host machine vs Docker container 
        ◦ Single container vs multiple containers 
Docker Features to Demonstrate
    • Container creation and execution 
    • CPU limitation using Docker flags 
    • Memory limitation using Docker flags 
    • Basic container monitoring 
Example:
docker run --cpus="1.0" --memory="512m" scheduler-sim

2. Memory Management Module
Students will extend the simulator to include memory management visualization and analysis.
Required Features
Implement:
    • Fixed Partition Allocation 
    • Variable Partition Allocation 
    • Paging (basic simulation) 
    • Memory allocation/deallocation during process execution 
Memory Visualization
Display:
    • Memory blocks 
    • Allocated vs free memory 
    • Fragmentation status 
    • Process memory usage 
Allocation Algorithms
At least TWO:
    • First Fit 
    • Best Fit 
    • Worst Fit 

3. Resource-Constrained Scheduling Analysis
Simulate scheduling under:
    • Limited CPU resources 
    • Limited memory resources 
Analyze impact on:
    • Waiting time 
    • Turnaround time 
    • CPU utilization 
    • Throughput 
    • Memory utilization 

4. Linux Monitoring & Validation
Use Linux tools to compare simulator behavior with real OS behavior.
Required Commands
Students should demonstrate:
top
ps
htop
docker stats
Analysis
Compare:
    • Containerized execution 
    • Host execution 
    • CPU throttling effects 
    • Memory pressure effects 

5. Process Isolation Concepts
Demonstrate:
    • PID namespaces 
    • Independent process execution inside containers 
    • Isolation between multiple simulator instances 
Deliverable Output
Students must submit:
1. Updated Source Code
Including:
    • Docker configuration 
    • Memory management module 
    • Resource monitoring integration 
2. Docker Files
    • Dockerfile 
    • docker-compose.yml (optional) 
3. Demonstration
Students should show:
    • Running simulator inside Docker 
    • Applying CPU/memory limits 
    • Memory allocation visualization 
4. Short Technical Report
Include:
    • Docker setup steps 
    • Memory management explanation 
    • Screenshots 
    • Comparison tables 
    • Performance observations 
Expected Learning Outcomes
Students will be able to:
    • Understand OS-level resource management 
    • Use Docker for isolation and deployment 
    • Analyze memory allocation strategies 
    • Observe impact of resource constraints on scheduling 
    • Relate theoretical OS concepts with real systems
