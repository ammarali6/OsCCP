"""
Memory Visualizer.
Provides Matplotlib-based visualization of memory allocation state.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


class MemoryVisualizer:
    """
    Visualizes memory allocation using horizontal bar charts.
    Shows allocated vs free blocks, fragmentation, and process distribution.
    """

    def __init__(self, title="Memory Allocation", figsize=(12, 6)):
        self.title = title
        self.figsize = figsize
        self.colors = {
            'free': '#E8E8E8',
            'allocated': '#4ECDC4',
        }
        self.process_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#AED6F1',
            '#FF8C94', '#A8E6CF', '#FFD3B6', '#FFAAA5', '#AA96DA'
        ]

    def _get_process_color(self, pid):
        """Generate consistent color for a process."""
        if pid is None:
            return self.colors['free']
        idx = hash(str(pid)) % len(self.process_colors)
        return self.process_colors[idx]

    def plot_partitions(self, blocks, total_size, save_path=None):
        """
        Plot partition-based memory allocation.

        Args:
            blocks: list of dicts with 'start', 'size', 'pid', 'free'
            total_size: total memory size
            save_path: optional path to save figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        y_pos = 0
        for block in blocks:
            color = self._get_process_color(block['pid'])
            edgecolor = '#333333' if not block['free'] else '#999999'
            linewidth = 2 if not block['free'] else 1

            ax.barh(
                y=y_pos,
                width=block['size'],
                left=block['start'],
                height=0.6,
                color=color,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=0.85
            )

            # Label
            if block['free']:
                label = f"Free\n{block['size']}"
            else:
                label = f"{block['pid']}\n{block['size']}"

            mid = block['start'] + block['size'] / 2
            ax.text(
                mid,
                y_pos,
                label,
                ha='center',
                va='center',
                fontsize=8,
                fontweight='bold',
                color='#333333'
            )

        ax.set_xlim(0, total_size)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel('Memory Address', fontsize=12, fontweight='bold')
        ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')

        # Legend
        free_patch = mpatches.Patch(color=self.colors['free'], label='Free')
        alloc_patch = mpatches.Patch(color=self.colors['allocated'], label='Allocated')
        ax.legend(handles=[free_patch, alloc_patch], loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Memory visualization saved to {save_path}")

        return fig, ax

    def plot_paging(self, frames, page_size, save_path=None):
        """
        Plot paging frame allocation.

        Args:
            frames: list of dicts with 'frame_num', 'pid', 'page_num', 'free'
            page_size: size of each page/frame
            save_path: optional path to save figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        num_frames = len(frames)
        cols = min(16, num_frames)
        rows = (num_frames + cols - 1) // cols

        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols

            color = self._get_process_color(frame['pid'])
            edgecolor = '#333333' if not frame['free'] else '#999999'

            rect = plt.Rectangle(
                (col, rows - row - 1),
                0.9, 0.9,
                facecolor=color,
                edgecolor=edgecolor,
                linewidth=1.5
            )
            ax.add_patch(rect)

            if not frame['free']:
                ax.text(
                    col + 0.45,
                    rows - row - 1 + 0.45,
                    f"{frame['pid']}\nP{frame['page_num']}",
                    ha='center',
                    va='center',
                    fontsize=7,
                    fontweight='bold',
                    color='#333333'
                )
            else:
                ax.text(
                    col + 0.45,
                    rows - row - 1 + 0.45,
                    f"F{i}",
                    ha='center',
                    va='center',
                    fontsize=7,
                    color='#999999'
                )

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)

        # Legend
        free_patch = mpatches.Patch(color=self.colors['free'], label='Free Frame')
        alloc_patch = mpatches.Patch(color=self.colors['allocated'], label='Allocated')
        ax.legend(handles=[free_patch, alloc_patch], loc='upper right',
                  bbox_to_anchor=(1.15, 1))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Paging visualization saved to {save_path}")

        return fig, ax

    def show(self):
        """Display the current figure."""
        plt.show()

    def save(self, path):
        """Save current figure to file."""
        plt.savefig(path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {path}")
