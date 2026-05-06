"""
Algorithm 2: Boundary Sampling
Generates boundary candidates and chooses ONE contact point per sensor
using nearest-neighbor center ordering.
"""

from core_utils import (
    Instance, nearest_neighbor_order_indices, choose_boundary_point,
    path_length, tour_length
)


def boundary_sampling(
    instance: Instance,
    n_boundary: int = 12,
    closed: bool = False,
) -> tuple:
    """
    Algorithm 2: Generate boundary candidates, but choose ONE contact point per
    sensor using a nearest-neighbor center order.

    Args:
        instance: Instance with sensors
        n_boundary: Number of boundary samples per sensor
        closed: If True, compute closed tour length; if False, compute open path length

    Returns:
        (path, length) where path is list of points and length is path/tour length
    """
    centers = [(s.x, s.y) for s in instance.sensors]
    sensor_order = nearest_neighbor_order_indices(centers)

    path = []
    for idx in sensor_order:
        sensor = instance.sensors[idx]
        previous = path[-1] if path else None
        path.append(choose_boundary_point(sensor, previous, n_boundary))

    length = tour_length(path) if closed else path_length(path)
    return path, length

