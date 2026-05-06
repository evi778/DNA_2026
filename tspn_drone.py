"""
TSPN Drone Data Collection - Base Code
Optimizing a continuous path for drone data collection via
spatial clustering and graph search.

Authors: E. Dimitrievska, M. Peeva, F. Petrovski
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.cluster import KMeans, DBSCAN
from itertools import permutations
import random
import math


# Fractional inset applied to sensor radius when sampling boundary points so
# that floating-point arithmetic in cos/sin never pushes a sample point
# outside the sensor's coverage area.
_BOUNDARY_INSET = 1e-9


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
        #Check if a point is within the sensor's coverage radius.
        return math.dist((self.x, self.y), point) <= self.radius


class Instance:
    #A test instance containing sensors.
    def __init__(self, sensors: list[Sensor]):
        self.sensors = sensors
        self.n = len(sensors)


# =============================================================================
# INSTANCE GENERATOR
# =============================================================================

def generate_instance(
    n_sensors: int,
    space_size: float = 100.0,
    radius_range: tuple = (3.0, 12.0),
    distribution: str = "uniform",
    seed: int = 42
) -> Instance:
    """
    Generate a test instance with random sensors.

    Args:
        n_sensors:    Number of sensors to place.
        space_size:   Side length of the square environment.
        radius_range: (min_radius, max_radius) for sensor coverage.
        distribution: 'uniform' | 'clustered' spatial layout.
        seed:         Random seed for reproducibility.

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
    return Instance(sensors)


# =============================================================================
# CANDIDATE POINT GENERATION
# =============================================================================

def boundary_sample(sensor: Sensor, n_points: int = 12) -> list[tuple]:
    """Sample candidate points evenly around a sensor's boundary circle.

    Points are placed at (1 - _BOUNDARY_INSET) * radius so that floating-point
    arithmetic in the trigonometric functions never pushes a point
    outside the coverage area, ensuring sensor.covers(p) is always True
    for every returned point.
    """
    angles = np.linspace(0, 2 * math.pi, n_points, endpoint=False)
    r = sensor.radius * (1 - _BOUNDARY_INSET)
    return [
        (sensor.x + r * math.cos(a),
         sensor.y + r * math.sin(a))
        for a in angles
    ]


# =============================================================================
# DISTANCE UTILITIES
# =============================================================================

def euclidean(a: tuple, b: tuple) -> float:
    return math.dist(a, b)


def path_length(path: list[tuple]) -> float:
    #Total Euclidean length of an ordered path (open tour).
    return sum(euclidean(path[i], path[i + 1]) for i in range(len(path) - 1))


def tour_length(path: list[tuple]) -> float:
    #Total length of a closed tour (returns to start).
    return path_length(path) + euclidean(path[-1], path[0])


# =============================================================================
# ALGORITHM 1: CENTER-BASED HEURISTIC (Baseline)
# =============================================================================

def nearest_neighbor_tour(points: list[tuple], start_idx: int = 0) -> list[tuple]:
    """Greedy nearest-neighbor heuristic for TSP."""
    unvisited = list(range(len(points)))
    tour = [start_idx]
    unvisited.remove(start_idx)

    while unvisited:
        current = tour[-1]
        nearest = min(unvisited, key=lambda j: euclidean(points[current], points[j]))
        tour.append(nearest)
        unvisited.remove(nearest)

    return [points[i] for i in tour]


def center_based_heuristic(instance: Instance) -> tuple[list[tuple], float]:
    """
    Algorithm 1: Ignore radii, treat sensor centers as TSP cities.
    Returns (path, length).
    """
    centers = [(s.x, s.y) for s in instance.sensors]
    path = nearest_neighbor_tour(centers)
    return path, tour_length(path)


# =============================================================================
# ALGORITHM 2: BOUNDARY SAMPLING
# =============================================================================

def boundary_sampling(instance: Instance, n_boundary: int = 12) -> tuple[list[tuple], float]:
    """
    Algorithm 2: Generate candidate points on each sensor boundary,
    then solve an approximate TSPN with nearest-neighbor.
    Returns (path, length).
    """
    # For each sensor, pick the single boundary point closest to the
    # nearest-neighbor tour order.
    centers = [(s.x, s.y) for s in instance.sensors]
    nn_order = nearest_neighbor_tour(centers)

    # Map ordered centers back to sensors
    center_to_sensor = {(s.x, s.y): s for s in instance.sensors}

    path = []
    for center in nn_order:
        sensor = center_to_sensor[center]
        candidates = boundary_sample(sensor, n_boundary)
        if not path:
            path.append(candidates[0])
        else:
            best = min(candidates, key=lambda p: euclidean(path[-1], p))
            path.append(best)

    return path, tour_length(path)


# =============================================================================
# ALGORITHM 3: HYBRID CLUSTERING + BOUNDARY SAMPLING + 2-OPT
# =============================================================================

def cluster_sensors(instance: Instance, method: str = "kmeans", n_clusters: int = None):
    """
    Cluster sensors spatially.
    Returns dict: {cluster_id: [Sensor, ...]}
    """
    coords = np.array([[s.x, s.y] for s in instance.sensors])

    if method == "kmeans":
        k = n_clusters or max(2, instance.n // 5)
        labels = KMeans(n_clusters=k, random_state=42, n_init="auto").fit_predict(coords)

    elif method == "dbscan":
        eps = 15.0
        labels = DBSCAN(eps=eps, min_samples=2).fit_predict(coords)
        # Noise points (-1) become their own single-sensor clusters
        max_label = labels.max()
        for i, lbl in enumerate(labels):
            if lbl == -1:
                max_label += 1
                labels[i] = max_label

    else:
        raise ValueError(f"Unknown clustering method: '{method}'")

    clusters = {}
    for sensor, label in zip(instance.sensors, labels):
        clusters.setdefault(int(label), []).append(sensor)
    return clusters


def centroid(sensors: list[Sensor]) -> tuple:
    return (
        sum(s.x for s in sensors) / len(sensors),
        sum(s.y for s in sensors) / len(sensors),
    )


def two_opt(path: list[tuple], max_iter: int = 1000) -> list[tuple]:
    """2-opt local search to shorten a tour."""
    best = list(path)
    improved = True
    iteration = 0
    while improved and iteration < max_iter:
        improved = False
        iteration += 1
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                # Reverse segment [i..j]
                new = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if tour_length(new) < tour_length(best):
                    best = new
                    improved = True
    return best


def hybrid_algorithm(
    instance: Instance,
    cluster_method: str = "kmeans",
    n_clusters: int = None,
    n_boundary: int = 12,
    use_2opt: bool = True,
) -> tuple[list[tuple], float]:
    """
    Algorithm 3: Hybrid Spatial Clustering + Boundary Sampling + 2-opt.

    Steps:
      1. Cluster sensors spatially.
      2. Build global route over cluster centroids (nearest-neighbor).
      3. Within each cluster, pick the closest boundary point per sensor so
         every sensor contributes at least one waypoint to the path.
      4. Concatenate local paths into a full drone path.
      5. Optionally refine with 2-opt.
      6. Validate coverage; insert best-insertion waypoints for any sensor
         that remains uncovered and report results.

    Returns (path, length).
    """
    # Step 1: Cluster
    clusters = cluster_sensors(instance, method=cluster_method, n_clusters=n_clusters)

    # Step 2: Global route over centroids
    cluster_ids = list(clusters.keys())
    centroids = {cid: centroid(clusters[cid]) for cid in cluster_ids}
    centroid_points = [centroids[cid] for cid in cluster_ids]
    global_order_points = nearest_neighbor_tour(centroid_points)

    # Map centroid points back to cluster ids
    point_to_cid = {centroids[cid]: cid for cid in cluster_ids}
    global_order = [point_to_cid[p] for p in global_order_points]

    # Step 3 & 4: Local boundary sampling per cluster, stitch together.
    # For each sensor pick the single boundary point closest to the current
    # path tail so that every sensor is guaranteed to contribute one waypoint.
    full_path = []
    for cid in global_order:
        sensors_in_cluster = clusters[cid]

        for sensor in sensors_in_cluster:
            candidates = boundary_sample(sensor, n_boundary)
            if not full_path:
                chosen = candidates[0]
            else:
                chosen = min(candidates, key=lambda p: euclidean(full_path[-1], p))
            full_path.append(chosen)

    # Step 5: 2-opt refinement
    if use_2opt and len(full_path) > 3:
        full_path = two_opt(full_path)

    # Step 6: Validate coverage; insert extra waypoints for uncovered sensors.
    coverage = validate_path(full_path, instance)
    if not coverage["all_covered"]:
        uncovered_ids = [sid for sid, ok in coverage["per_sensor"].items() if not ok]
        print(
            f"[hybrid_algorithm] Warning: {len(uncovered_ids)} sensor(s) uncovered "
            f"after 2-opt: {uncovered_ids}. Inserting coverage points."
        )
        sensor_map = {s.id: s for s in instance.sensors}
        for sid in uncovered_ids:
            sensor = sensor_map[sid]
            candidates = boundary_sample(sensor, n_boundary)
            best_point = None
            best_pos = 0
            best_cost = float("inf")
            for pt in candidates:
                for i in range(len(full_path)):
                    a = full_path[i]
                    b = full_path[(i + 1) % len(full_path)]
                    cost = euclidean(a, pt) + euclidean(pt, b) - euclidean(a, b)
                    if cost < best_cost:
                        best_cost = cost
                        best_point = pt
                        best_pos = i + 1
            if best_point is not None:
                full_path.insert(best_pos, best_point)

        final_coverage = validate_path(full_path, instance)
        print(
            f"[hybrid_algorithm] Coverage after fix: "
            f"{final_coverage['n_covered']}/{final_coverage['n_total']} sensors covered."
        )
        if not final_coverage["all_covered"]:
            still_uncovered = [
                sid for sid, ok in final_coverage["per_sensor"].items() if not ok
            ]
            print(f"[hybrid_algorithm] Still uncovered: {still_uncovered}")
    else:
        print(
            f"[hybrid_algorithm] Coverage: "
            f"{coverage['n_covered']}/{coverage['n_total']} sensors covered."
        )

    return full_path, tour_length(full_path)


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


# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_instance_and_path(
    instance: Instance,
    path: list[tuple],
    title: str = "Drone Path",
    clusters: dict = None,
):
    """Plot sensors, their coverage radii, and the drone path."""
    fig, ax = plt.subplots(figsize=(9, 9))
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
        ax.plot(sensor.x, sensor.y, 'o', color=colors[cid % len(colors)], markersize=5)
        ax.annotate(str(sensor.id), (sensor.x, sensor.y), fontsize=7, ha='center', va='bottom')

    if path:
        xs, ys = zip(*path)
        ax.plot(xs, ys, '-', color='black', linewidth=1.0, alpha=0.7, label='Drone path')
        ax.plot(xs[0], ys[0], 'g^', markersize=10, label='Start')
        ax.plot(xs[-1], ys[-1], 'rs', markersize=8, label='End')

    ax.set_title(f"{title}\nPath length: {tour_length(path):.2f}")
    ax.set_aspect('equal')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{title.replace(' ', '_')}.png", dpi=150)
    plt.show()
    print(f"Saved: {title}")


# =============================================================================
# BENCHMARK RUNNER
# =============================================================================

def run_benchmark(
    n_sensors_list: list[int] = [10, 20, 50],
    distributions: list[str] = ["uniform", "clustered"],
    seed: int = 42,
):
    """
    Run all three algorithms across instance sizes and distributions.
    Prints a comparison table.
    """
    print(f"{'n':>5} {'dist':>10} {'center':>12} {'boundary':>12} {'hybrid':>12}")
    print("-" * 58)

    for n in n_sensors_list:
        for dist in distributions:
            inst = generate_instance(n, distribution=dist, seed=seed)

            _, c_len  = center_based_heuristic(inst)
            _, b_len  = boundary_sampling(inst)
            _, h_len  = hybrid_algorithm(inst)

            print(f"{n:>5} {dist:>10} {c_len:>12.2f} {b_len:>12.2f} {h_len:>12.2f}")

