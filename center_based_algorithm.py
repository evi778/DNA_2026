"""
Algorithm 1: Center-Based Heuristic
Treats sensor centers as TSP cities and finds their nearest-neighbor tour.
"""

from core_utils import Instance, nearest_neighbor_tour, path_length, tour_length


def center_based_heuristic(instance: Instance, closed: bool = False) -> tuple:
    """
    Algorithm 1: Ignore radii, treat sensor centers as TSP cities.

    Args:
        instance: Instance with sensors
        closed: If True, compute closed tour length; if False, compute open path length

    Returns:
        (path, length) where path is list of points and length is path/tour length
    """
    centers = [(s.x, s.y) for s in instance.sensors]
    path = nearest_neighbor_tour(centers)
    length = tour_length(path) if closed else path_length(path)
    return path, length
