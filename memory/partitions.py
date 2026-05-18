"""
Partition-based Memory Allocation.
Implements Fixed and Variable partition allocation schemes.
"""

from .algorithms import first_fit, best_fit, worst_fit


class MemoryBlock:
    """Represents a block of memory (allocated or free)."""
    def __init__(self, start, size, pid=None):
        self.start = start
        self.size = size
        self.pid = pid  # None means free
        self.free = pid is None

    def __repr__(self):
        status = f"Free({self.size})" if self.free else f"PID={self.pid}({self.size})"
        return f"Block[{self.start}-{self.start+self.size}] {status}"


class BaseMemory:
    """Base class for partition memory managers."""

    def __init__(self, total_size, algorithm='first_fit'):
        self.total_size = total_size
        self.algorithm = algorithm
        self.blocks = []
        self.allocated = {}  # pid -> block
        self._init_memory()

    def _init_memory(self):
        """Initialize memory blocks. Override in subclasses."""
        raise NotImplementedError

    def _get_algorithm(self):
        """Return the allocation algorithm function."""
        algo_map = {
            'first_fit': first_fit,
            'best_fit': best_fit,
            'worst_fit': worst_fit,
        }
        return algo_map.get(self.algorithm, first_fit)

    def allocate(self, pid, size):
        """
        Allocate memory for a process.
        Returns True if successful, False otherwise.
        """
        if pid in self.allocated:
            return False  # Already allocated

        algo = self._get_algorithm()
        result = algo(self.blocks, size)

        if result is None:
            return False  # No suitable block found

        idx, block = result

        if block.size == size:
            # Exact fit — just mark as allocated
            block.pid = pid
            block.free = False
        else:
            # Split block: allocated part + remaining free part
            new_block = MemoryBlock(block.start, size, pid)
            remaining = MemoryBlock(block.start + size, block.size - size, None)
            self.blocks[idx] = new_block
            self.blocks.insert(idx + 1, remaining)
            block = new_block

        self.allocated[pid] = block
        return True

    def deallocate(self, pid):
        """
        Free memory allocated to a process.
        Returns True if successful.
        """
        if pid not in self.allocated:
            return False

        block = self.allocated[pid]
        block.pid = None
        block.free = True
        del self.allocated[pid]

        self._merge_adjacent_free()
        return True

    def _merge_adjacent_free(self):
        """Merge adjacent free blocks. Override in subclasses if needed."""
        i = 0
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            next_block = self.blocks[i + 1]
            if current.free and next_block.free:
                current.size += next_block.size
                self.blocks.pop(i + 1)
            else:
                i += 1

    def get_utilization(self):
        """Return memory utilization percentage."""
        used = sum(b.size for b in self.blocks if not b.free)
        return (used / self.total_size) * 100

    def get_free_memory(self):
        """Return total free memory."""
        return sum(b.size for b in self.blocks if b.free)

    def get_used_memory(self):
        """Return total used memory."""
        return sum(b.size for b in self.blocks if not b.free)

    def get_fragmentation(self):
        """
        Calculate fragmentation.
        For variable partition: external fragmentation (free blocks that are too small).
        For fixed partition: internal fragmentation (unused space within allocated blocks).
        Returns tuple (external_frag, internal_frag) in bytes.
        """
        raise NotImplementedError

    def get_block_state(self):
        """Return current block state as list of dicts."""
        return [
            {
                'start': b.start,
                'size': b.size,
                'pid': b.pid,
                'free': b.free
            }
            for b in self.blocks
        ]


class FixedPartitionMemory(BaseMemory):
    """
    Fixed Partition Allocation.
    Memory is divided into fixed-size partitions at initialization.
    Each partition can hold exactly one process.
    """

    def __init__(self, total_size, partition_size, algorithm='first_fit'):
        self.partition_size = partition_size
        super().__init__(total_size, algorithm)

    def _init_memory(self):
        """Pre-split memory into fixed-size partitions."""
        num_partitions = self.total_size // self.partition_size
        for i in range(num_partitions):
            start = i * self.partition_size
            self.blocks.append(MemoryBlock(start, self.partition_size, None))

    def allocate(self, pid, size):
        """
        Allocate a fixed partition to a process.
        A process needs size <= partition_size.
        Internal fragmentation = partition_size - actual_size.
        """
        if size > self.partition_size:
            return False  # Process too large for any partition
        return super().allocate(pid, size)

    def get_fragmentation(self):
        """Calculate internal fragmentation in fixed partitions."""
        internal = 0
        for b in self.blocks:
            if not b.free and b.pid in self.allocated:
                # Internal frag = partition size - requested size
                # We track actual requested size separately if needed
                # For now, assume process uses full partition
                pass
        # More accurate: track requested sizes
        external = sum(b.size for b in self.blocks if b.free and b.size < self.partition_size)
        internal = sum(
            b.size - self._get_requested_size(b.pid)
            for b in self.blocks
            if not b.free and b.pid in self.allocated
        )
        return external, internal

    def _get_requested_size(self, pid):
        """Get the originally requested size for a process."""
        # Store requested sizes
        if not hasattr(self, '_requested_sizes'):
            self._requested_sizes = {}
        return self._requested_sizes.get(pid, 0)

    def allocate(self, pid, size):
        """Override to track requested sizes."""
        if not hasattr(self, '_requested_sizes'):
            self._requested_sizes = {}
        result = super().allocate(pid, size)
        if result:
            self._requested_sizes[pid] = size
        return result

    def deallocate(self, pid):
        if hasattr(self, '_requested_sizes') and pid in self._requested_sizes:
            del self._requested_sizes[pid]
        return super().deallocate(pid)


class VariablePartitionMemory(BaseMemory):
    """
    Variable Partition Allocation.
    Memory starts as one large free block.
    Partitions are created dynamically as processes are allocated.
    Adjacent free blocks are merged on deallocation.
    """

    def _init_memory(self):
        """Start with one large free block."""
        self.blocks = [MemoryBlock(0, self.total_size, None)]

    def get_fragmentation(self):
        """
        External fragmentation = total free memory in blocks too small for typical allocation.
        Internal fragmentation = 0 (variable partitions fit exactly).
        """
        # External: sum of free blocks that are "small" (< 10% of total or arbitrary threshold)
        # For simplicity, all free space not in largest block is external fragmentation
        free_blocks = [b.size for b in self.blocks if b.free]
        if not free_blocks:
            return 0, 0
        largest_free = max(free_blocks)
        total_free = sum(free_blocks)
        external = total_free - largest_free
        return external, 0
