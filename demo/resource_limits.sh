#!/bin/bash
# Docker Resource Limits Demonstration Script
# Shows CPU and memory throttling effects using Docker flags

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      RESOURCE LIMITS DEMO - CPU & MEMORY THROTTLING        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if image exists
if ! docker image inspect scheduler-sim >/dev/null 2>&1; then
    echo "⚠️  Image 'scheduler-sim' not found. Building..."
    docker build -t scheduler-sim . || { echo "Build failed"; exit 1; }
fi

echo "📍 STEP 1: Container WITHOUT Resource Limits"
echo "───────────────────────────────────────────────────────────────"
echo "Running: docker run --rm scheduler-sim python main.py --headless -p memory_stress"
time docker run --rm scheduler-sim python main.py --headless -p memory_stress -m 1024 2>&1
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 2: Container with CPU Limit (--cpus='0.5')"
echo "───────────────────────────────────────────────────────────────"
echo "Running: docker run --rm --cpus='0.5' scheduler-sim python main.py --headless -p memory_stress"
time docker run --rm --cpus="0.5" scheduler-sim python main.py --headless -p memory_stress -m 1024 2>&1
echo ""
echo "💡 Observation: CPU limit may slow down computation-intensive tasks."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 3: Container with Memory Limit (--memory='256m')"
echo "───────────────────────────────────────────────────────────────"
echo "Running: docker run --rm --memory='256m' scheduler-sim python main.py --headless -p memory_stress"
docker run --rm --memory="256m" scheduler-sim python main.py --headless -p memory_stress -m 1024 2>&1
echo ""
echo "💡 Observation: Memory limit restricts the container's available RAM."
echo "   If exceeded, the container may be killed by the OOM killer."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📍 STEP 4: Live Docker Stats During Execution"
echo "───────────────────────────────────────────────────────────────"
echo "Starting a container and monitoring with 'docker stats'..."
CONTAINER=$(docker run -d --cpus="0.5" --memory="256m" --name sim-limits scheduler-sim sleep 60 2>/dev/null)

if [ ! -z "$CONTAINER" ]; then
    echo "Container started: $CONTAINER"
    echo ""
    echo "Running 'docker stats' for 5 seconds..."
    timeout 5 docker stats --no-stream sim-limits 2>/dev/null || docker stats sim-limits &
    STATS_PID=$!
    sleep 5
    kill $STATS_PID 2>/dev/null
    echo ""
    echo "Cleaning up..."
    docker stop sim-limits >/dev/null 2>&1
    docker rm sim-limits >/dev/null 2>&1
else
    echo "⚠️  Could not start container"
fi

echo ""
echo "📍 STEP 5: Comparing Multiple Containers"
echo "───────────────────────────────────────────────────────────────"
echo "Starting two containers with different limits side-by-side..."

# Container A: generous limits
A=$(docker run -d --cpus="1.0" --memory="512m" --name sim-generous scheduler-sim sleep 30 2>/dev/null)
# Container B: strict limits
B=$(docker run -d --cpus="0.25" --memory="128m" --name sim-strict scheduler-sim sleep 30 2>/dev/null)

if [ ! -z "$A" ] && [ ! -z "$B" ]; then
    echo ""
    echo "Container A (generous): --cpus=1.0 --memory=512m"
    echo "Container B (strict):   --cpus=0.25 --memory=128m"
    echo ""
    echo "Stats for both:"
    docker stats --no-stream sim-generous sim-strict 2>/dev/null || echo "(Could not get stats)"

    docker stop sim-generous sim-strict >/dev/null 2>&1
    docker rm sim-generous sim-strict >/dev/null 2>&1
else
    echo "⚠️  Could not start comparison containers"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETE                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Key Takeaways:"
echo "  • --cpus limits CPU usage (fractional values supported)"
echo "  • --memory restricts RAM; OOM killer terminates over limit"
echo "  • --memory-swap controls swap space"
echo "  • docker stats shows live resource consumption"
echo "  • Different limits create different performance characteristics"
