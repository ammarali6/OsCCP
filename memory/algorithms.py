"""
Memory Allocation Algorithms.
Implements First Fit, Best Fit, and Worst Fit strategies.
"""


def first_fit(blocks, size):
    """
    First Fit: Allocate the first free block that is large enough.

    Args:
        blocks: list of MemoryBlock objects
        size: requested size

    Returns:
        (index, block) tuple or None if no fit
    """
    for i, block in enumerate(blocks):
        if block.free and block.size >= size:
            return i, block
    return None


def best_fit(blocks, size):
    """
    Best Fit: Allocate the smallest free block that is large enough.
    Minimizes leftover fragmentation.

    Args:
        blocks: list of MemoryBlock objects
        size: requested size

    Returns:
        (index, block) tuple or None if no fit
    """
    best_idx = None
    best_block = None
    best_size = float('inf')

    for i, block in enumerate(blocks):
        if block.free and block.size >= size:
            if block.size < best_size:
                best_size = block.size
                best_idx = i
                best_block = block

    if best_idx is None:
        return None
    return best_idx, best_block


def worst_fit(blocks, size):
    """
    Worst Fit: Allocate the largest free block.
    Leaves the largest possible remaining fragment.

    Args:
        blocks: list of MemoryBlock objects
        size: requested size

    Returns:
        (index, block) tuple or None if no fit
    """
    worst_idx = None
    worst_block = None
    worst_size = -1

    for i, block in enumerate(blocks):
        if block.free and block.size >= size:
            if block.size > worst_size:
                worst_size = block.size
                worst_idx = i
                worst_block = block

    if worst_idx is None:
        return None
    return worst_idx, worst_block
