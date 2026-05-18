"""
Paging Memory Simulation.
Implements basic paging with page tables, page faults, and frame allocation.
"""


class PagingMemory:
    """
    Simulates a paging memory management system.

    Attributes:
        physical_size: total physical memory size
        page_size: size of each page/frame
        virtual_size: maximum virtual address space per process
        num_frames: total number of physical frames
    """

    def __init__(self, physical_size=1024, page_size=64, virtual_size=2048):
        self.physical_size = physical_size
        self.page_size = page_size
        self.virtual_size = virtual_size
        self.num_frames = physical_size // page_size

        # Frame table: list of dicts with 'pid' and 'page_num' (None if free)
        self.frames = [{'pid': None, 'page_num': None} for _ in range(self.num_frames)]

        # Page tables: dict mapping pid -> {page_num: frame_num or None}
        self.page_tables = {}

        # Statistics
        self.page_faults = 0
        self.total_accesses = 0

    def allocate(self, pid, num_pages):
        """
        Allocate pages for a process.
        Creates page table entry and allocates frames.
        Returns number of pages successfully allocated.
        """
        if pid not in self.page_tables:
            self.page_tables[pid] = {}

        allocated = 0
        for page_num in range(num_pages):
            if page_num in self.page_tables[pid] and self.page_tables[pid][page_num] is not None:
                continue  # Already allocated

            # Find a free frame
            free_frame = None
            for i, frame in enumerate(self.frames):
                if frame['pid'] is None:
                    free_frame = i
                    break

            if free_frame is None:
                break  # No more free frames

            self.frames[free_frame] = {'pid': pid, 'page_num': page_num}
            self.page_tables[pid][page_num] = free_frame
            allocated += 1

        return allocated

    def deallocate(self, pid):
        """Free all frames and page table entries for a process."""
        if pid not in self.page_tables:
            return False

        # Free frames
        for frame in self.frames:
            if frame['pid'] == pid:
                frame['pid'] = None
                frame['page_num'] = None

        del self.page_tables[pid]
        return True

    def access_page(self, pid, page_num):
        """
        Simulate accessing a page.
        Returns True if page is in memory (hit), False if page fault.
        """
        self.total_accesses += 1

        if pid not in self.page_tables:
            self.page_faults += 1
            return False

        if page_num not in self.page_tables[pid] or self.page_tables[pid][page_num] is None:
            self.page_faults += 1
            return False

        return True

    def get_page_fault_rate(self):
        """Return page fault rate as percentage."""
        if self.total_accesses == 0:
            return 0.0
        return (self.page_faults / self.total_accesses) * 100

    def get_frame_state(self):
        """Return current frame allocation state."""
        return [
            {
                'frame_num': i,
                'pid': f['pid'],
                'page_num': f['page_num'],
                'free': f['pid'] is None
            }
            for i, f in enumerate(self.frames)
        ]

    def get_page_table(self, pid):
        """Return page table for a process."""
        return self.page_tables.get(pid, {}).copy()

    def get_utilization(self):
        """Return physical memory utilization percentage."""
        used_frames = sum(1 for f in self.frames if f['pid'] is not None)
        return (used_frames / self.num_frames) * 100

    def get_free_frames(self):
        """Return number of free frames."""
        return sum(1 for f in self.frames if f['pid'] is None)
