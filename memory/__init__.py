"""
Memory Management Module for OS Scheduler Simulator.

Provides memory allocation strategies, paging simulation, and visualization
for resource-constrained scheduling analysis.
"""

from .partitions import FixedPartitionMemory, VariablePartitionMemory
from .paging import PagingMemory
from .algorithms import first_fit, best_fit, worst_fit
from .visualizer import MemoryVisualizer

__all__ = [
    'FixedPartitionMemory',
    'VariablePartitionMemory',
    'PagingMemory',
    'first_fit',
    'best_fit',
    'worst_fit',
    'MemoryVisualizer',
]
