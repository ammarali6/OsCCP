CPU_BOUND = [
    {
        "pid": "P1",
        "arrival": 0,
        "burst": 10,
        "io_burst": 0,
        "priority": 2,
        "color": "#FF6B6B",
    },
    {
        "pid": "P2",
        "arrival": 1,
        "burst": 8,
        "io_burst": 0,
        "priority": 3,
        "color": "#4ECDC4",
    },
    {
        "pid": "P3",
        "arrival": 2,
        "burst": 12,
        "io_burst": 0,
        "priority": 1,
        "color": "#45B7D1",
    },
    {
        "pid": "P4",
        "arrival": 3,
        "burst": 6,
        "io_burst": 0,
        "priority": 2,
        "color": "#FFA07A",
    },
]

IO_BOUND = [
    {
        "pid": "P1",
        "arrival": 0,
        "burst": 2,
        "io_burst": 6,
        "priority": 2,
        "color": "#FF6B6B",
    },
    {
        "pid": "P2",
        "arrival": 1,
        "burst": 1,
        "io_burst": 5,
        "priority": 1,
        "color": "#4ECDC4",
    },
    {
        "pid": "P3",
        "arrival": 2,
        "burst": 3,
        "io_burst": 8,
        "priority": 3,
        "color": "#45B7D1",
    },
    {
        "pid": "P4",
        "arrival": 3,
        "burst": 1,
        "io_burst": 4,
        "priority": 1,
        "color": "#FFA07A",
    },
]

MIXED = [
    {
        "pid": "P1",
        "arrival": 0,
        "burst": 10,
        "io_burst": 0,
        "priority": 2,
        "color": "#FF6B6B",
    },
    {
        "pid": "P2",
        "arrival": 1,
        "burst": 2,
        "io_burst": 5,
        "priority": 1,
        "color": "#4ECDC4",
    },
    {
        "pid": "P3",
        "arrival": 2,
        "burst": 8,
        "io_burst": 0,
        "priority": 3,
        "color": "#45B7D1",
    },
    {
        "pid": "P4",
        "arrival": 3,
        "burst": 1,
        "io_burst": 6,
        "priority": 1,
        "color": "#FFA07A",
    },
]

WORKLOAD_TYPES = {
    "cpu_bound": CPU_BOUND,
    "io_bound": IO_BOUND,
    "mixed": MIXED,
}
