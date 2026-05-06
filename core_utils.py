"""
TSPN Drone Data Collection - Core Utilities and Data Structures
Shared utilities across all algorithms.
"""

import math
import numpy as np
from dataclasses import dataclass


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class Sensor:
    def __init__(self, id: int, x: float, y: float, radius: float):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius

    def __repr__(self):
        return f"Sensor(id={self.id}, x={self.x:.2f}, y={self.y:.2f}, r={self.radius:.2f})"

    def covers(self, point: tuple) -> bool:
        """Check if a point is within the sensor's coverage radius."""
        return math.dist((self.x, self.y), point) <= self.radius + 1e-9


class Instance:
    """A test instance containing sensors."""
    def __init__(self, sensors: list, name: str = "instance"):
        self.sensors = sensors
        self.n = len(sensors)
        self.name = name


@dataclass
class AlgorithmResult:
    """Result from running an algorithm."""
    algorithm: str
    instance_name: str
    path: list
    length: float
    coverage: dict
    time: float = 0.0


# =============================================================================
# INSTANCE GENERATOR
# =============================================================================

def generate_instance(
    n_sensors: int,
    space_size: float = 100.0,
    radius_range: tuple = (3.0, 12.0),
    distribution: str = "uniform",
    seed: int = 42,
    name: str = "instance"
) -> Instance:
    """
    Generate a test instance with random sensors.

    Args:
        n_sensors:    Number of sensors to place.
        space_size:   Side length of the square environment.
        radius_range: (min_radius, max_radius) for sensor coverage.
        distribution: 'uniform' | 'clustered' spatial layout.
        seed:         Random seed for reproducibility.
        name:         Name of the instance.

    Returns:
        Instance with the generated sensors.
    """
    rng = np.random.default_rng(seed)

    if distribution == "uniform":
        positions = rng.uniform(0, space_size, (n_sensors, 2))

    elif distribution == "clustered":
        n_clusters = max(2, n_sensors // 5)
        centers = rng.uniform(10, space_size - 10, (n_clusters, 2))
        positions = []
        for i in range(n_sensors):
            center = centers[i % n_clusters]
            offset = rng.normal(0, space_size / 10, 2)
            pos = np.clip(center + offset, 0, space_size)
            positions.append(pos)
        positions = np.array(positions)

    else:
        raise ValueError(f"Unknown distribution: '{distribution}'")

    radii = rng.uniform(radius_range[0], radius_range[1], n_sensors)

    sensors = [
        Sensor(i, positions[i, 0], positions[i, 1], radii[i])
        for i in range(n_sensors)
    ]
    return Instance(sensors, name=name)


# =============================================================================
# DISTANCE UTILITIES
# =============================================================================

def euclidean(a: tuple, b: tuple) -> float:
    """Calculate Euclidean distance between two points."""
    return math.dist(a, b)


def path_length(path: list[tuple]) -> float:
    """Total Euclidean length of an ordered OPEN path."""
    if len(path) < 2:
        return 0.0
    return sum(euclidean(path[i], path[i + 1]) for i in range(len(path) - 1))


def tour_length(path: list[tuple]) -> float:
    """Total length of a CLOSED tour, returning to the first point."""
    if len(path) < 2:
        return 0.0
    return path_length(path) + euclidean(path[-1], path[0])


# =============================================================================
# SHARED HELPERS
# =============================================================================

def nearest_neighbor_order_indices(points: list[tuple], start_idx: int = 0) -> list:
    """Return point indices in nearest-neighbor order."""
    if not points:
        return []

    unvisited = list(range(len(points)))
    order = [start_idx]
    unvisited.remove(start_idx)

    while unvisited:
        current = order[-1]
        nearest = min(unvisited, key=lambda j: euclidean(points[current], points[j]))
        order.append(nearest)
        unvisited.remove(nearest)

    return order


def nearest_neighbor_tour(points: list[tuple], start_idx: int = 0) -> list[tuple]:
    """Greedy nearest-neighbor heuristic for an ordered path."""
    return [points[i] for i in nearest_neighbor_order_indices(points, start_idx)]


def boundary_sample(sensor: Sensor, n_points: int = 12) -> list[tuple]:
    """Sample candidate points evenly around a sensor's boundary circle."""
    angles = np.linspace(0, 2 * math.pi, n_points, endpoint=False)
    return [
        (sensor.x + sensor.radius * math.cos(a),
         sensor.y + sensor.radius * math.sin(a))
        for a in angles
    ]


def choose_boundary_point(sensor: Sensor, previous_point: tuple = None, n_boundary: int = 12) -> tuple:
    """
    Choose one boundary point for a sensor.
    Returns the closest boundary point to the previous point.
    """
    candidates = boundary_sample(sensor, n_boundary)
    if previous_point is None:
        return candidates[0]
    return min(candidates, key=lambda p: euclidean(previous_point, p))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_path(path: list[tuple], instance: Instance) -> dict:
    """
    Check that every sensor is covered by at least one path point.
    Returns a dict with coverage results.
    """
    results = {}
    for sensor in instance.sensors:
        covered = any(sensor.covers(p) for p in path)
        results[sensor.id] = covered
    n_covered = sum(results.values())
    return {
        "per_sensor": results,
        "n_covered": n_covered,
        "n_total": instance.n,
        "all_covered": n_covered == instance.n,
    }

