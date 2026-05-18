#!/bin/bash
# Process Isolation Demonstration Script
# Shows PID namespace differences between host and containers

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        PROCESS ISOLATION DEMO - PID NAMESPACES             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

echo "📍 STEP 1: Host Process Information"
echo "───────────────────────────────────────────────────────────────"
echo "Host PID: $$"
echo ""
echo "Host processes (first 10):"
ps aux | head -11
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 2: Container with Default PID Namespace (isolated)"
echo "───────────────────────────────────────────────────────────────"
echo "Running: docker run --rm scheduler-sim ps aux"
docker run --rm scheduler-sim ps aux 2>/dev/null || echo "(Container not built yet - build with: docker build -t scheduler-sim .)"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 3: Container with Host PID Namespace (--pid=host)"
echo "───────────────────────────────────────────────────────────────"
echo "Running: docker run --rm --pid=host scheduler-sim ps aux | head -15"
docker run --rm --pid=host scheduler-sim ps aux 2>/dev/null | head -15 || echo "(Container not built yet)"
echo ""
echo "💡 Observation: With --pid=host, the container sees host PIDs."
echo "   Without it, the container only sees its own processes."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 4: Two Independent Container Instances"
echo "───────────────────────────────────────────────────────────────"
echo "Starting two containers simultaneously to show independence..."

# Start two background containers
CONTAINER1=$(docker run -d --name sim-instance-1 scheduler-sim sleep 30 2>/dev/null)
CONTAINER2=$(docker run -d --name sim-instance-2 scheduler-sim sleep 30 2>/dev/null)

if [ ! -z "$CONTAINER1" ] && [ ! -z "$CONTAINER2" ]; then
    echo "Container 1 ID: $CONTAINER1"
    echo "Container 2 ID: $CONTAINER2"
    echo ""
    echo "Container 1 PIDs:"
    docker exec sim-instance-1 ps aux 2>/dev/null || echo "(Could not exec)"
    echo ""
    echo "Container 2 PIDs:"
    docker exec sim-instance-2 ps aux 2>/dev/null || echo "(Could not exec)"
    echo ""
    echo "💡 Observation: Each container has its own PID 1 (init process)"
    echo "   and cannot see the other's processes."

    # Cleanup
    echo ""
    echo "Cleaning up containers..."
    docker stop sim-instance-1 sim-instance-2 >/dev/null 2>&1
    docker rm sim-instance-1 sim-instance-2 >/dev/null 2>&1
else
    echo "⚠️  Could not start containers. Make sure image is built:"
    echo "   docker build -t scheduler-sim ."
fi

echo ""
echo "📍 STEP 5: PID Namespace Tree"
echo "───────────────────────────────────────────────────────────────"
echo "Host PID tree (showing Docker daemon and container processes):"
pstree -p 2>/dev/null || ps -ef --forest 2>/dev/null || echo "(pstree/ps not available)"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETE                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Key Takeaways:"
echo "  • Each Docker container gets its own PID namespace"
echo "  • Container processes are isolated from the host and other containers"
echo "  • --pid=host removes this isolation (use with caution)"
echo "  --pid=container:<name> shares PID namespace between containers"
