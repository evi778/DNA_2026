"""
Visualization utilities for TSPN Drone Path Planning.
"""

import matplotlib.pyplot as plt
from core_utils import Instance, path_length, tour_length


def plot_instance_and_path(
    instance: Instance,
    path: list,
    title: str = "Drone Path",
    clusters: dict = None,
    closed: bool = False,
    save_path: str = None,
):
    """
    Plot sensors, their coverage radii, and the drone path.

    Args:
        instance: Instance with sensors
        path: List of points making up the path
        title: Title for the plot
        clusters: Optional dict of clusters for coloring
        closed: Whether to show return edge
        save_path: Path to save the figure (if None, only displays)
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    colors = plt.cm.tab10.colors

    for sensor in instance.sensors:
        cid = 0
        if clusters:
            for k, v in clusters.items():
                if sensor in v:
                    cid = k % len(colors)
                    break

        circle = plt.Circle(
            (sensor.x, sensor.y), sensor.radius,
            color=colors[cid % len(colors)], alpha=0.2, linewidth=1.2,
            fill=True, edgecolor=colors[cid % len(colors)]
        )
        ax.add_patch(circle)
        ax.plot(sensor.x, sensor.y, 'o', color=colors[cid % len(colors)], markersize=6)
        ax.annotate(str(sensor.id), (sensor.x, sensor.y), fontsize=7, ha='center', va='bottom')

    if path:
        xs, ys = zip(*path)
        ax.plot(xs, ys, '-', color='black', linewidth=1.5, alpha=0.7, label='Drone path')
        if closed and len(path) > 1:
            ax.plot([xs[-1], xs[0]], [ys[-1], ys[0]], '--', color='black', linewidth=1.0, alpha=0.5, label='Return edge')

        # Mark all touch points on sensor circles
        ax.plot(xs, ys, 'ko', markersize=5, alpha=0.6, label='Touch points', zorder=4)

        # Mark start and end separately
        ax.plot(xs[0], ys[0], 'g^', markersize=12, label='Start', zorder=5)
        ax.plot(xs[-1], ys[-1], 'rs', markersize=10, label='End', zorder=5)

    length = tour_length(path) if closed else path_length(path)
    mode = "closed tour" if closed else "open path"
    ax.set_title(f"{title}\n{mode} length: {length:.2f}", fontsize=12, fontweight='bold')
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization: {save_path}")
    else:
        plt.show()

    plt.close()


def create_comparison_plot(
    instance: Instance,
    results: dict,
    title: str = "Algorithm Comparison",
    save_path: str = None,
):
    """
    Create a comparison plot of multiple algorithms on the same instance.

    Args:
        instance: Instance with sensors
        results: Dict of {algorithm_name: (path, length, clusters)}
        title: Title for comparison
        save_path: Path to save figure
    """
    n_algorithms = len(results)
    fig, axes = plt.subplots(1, n_algorithms, figsize=(6 * n_algorithms, 6))

    if n_algorithms == 1:
        axes = [axes]

    colors = plt.cm.tab10.colors

    for idx, (algo_name, (path, length, clusters)) in enumerate(results.items()):
        ax = axes[idx]

        for sensor in instance.sensors:
            cid = 0
            if clusters:
                for k, v in clusters.items():
                    if sensor in v:
                        cid = k % len(colors)
                        break

            circle = plt.Circle(
                (sensor.x, sensor.y), sensor.radius,
                color=colors[cid % len(colors)], alpha=0.2, linewidth=1.2,
                fill=True, edgecolor=colors[cid % len(colors)]
            )
            ax.add_patch(circle)
            ax.plot(sensor.x, sensor.y, 'o', color=colors[cid % len(colors)], markersize=5)

        if path:
            xs, ys = zip(*path)
            ax.plot(xs, ys, '-', color='black', linewidth=1.0, alpha=0.7)
            # Mark all touch points on sensor circles
            ax.plot(xs, ys, 'ko', markersize=4, alpha=0.5, zorder=4)
            # Mark start and end
            ax.plot(xs[0], ys[0], 'g^', markersize=10, zorder=5)
            ax.plot(xs[-1], ys[-1], 'rs', markersize=8, zorder=5)

        ax.set_title(f"{algo_name}\nLength: {length:.2f}", fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved comparison: {save_path}")
    else:
        plt.show()

    plt.close()


