"""
TSPN Drone Data Collection - Corrected Version
Optimizing a continuous path for drone data collection via
spatial clustering and graph search.

Authors: E. Dimitrievska, M. Peeva, F. Petrovski

Corrections added by ChatGPT:
- Hybrid algorithm now chooses ONE boundary touch point per sensor instead of
  visiting every sampled boundary candidate.
- Path length is now treated consistently as an OPEN robot path by default.
- 2-opt now optimizes the same open-path cost that is reported and plotted.
- Comments marked "CHANGED" show the important edits.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN


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
        return math.dist((self.x, self.y), point) <= self.radius + 1e-9  # CHANGED: tolerance for boundary floating-point checks.


class Instance:
    """A test instance containing sensors."""
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
    """Sample candidate points evenly around a sensor's boundary circle."""
    angles = np.linspace(0, 2 * math.pi, n_points, endpoint=False)
    return [
        (sensor.x + sensor.radius * math.cos(a),
         sensor.y + sensor.radius * math.sin(a))
        for a in angles
    ]


# =============================================================================
# DISTANCE UTILITIES
# =============================================================================

def euclidean(a: tuple, b: tuple) -> float:
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

def nearest_neighbor_order_indices(points: list[tuple], start_idx: int = 0) -> list[int]:
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


def choose_boundary_point(sensor: Sensor, previous_point: tuple | None, n_boundary: int) -> tuple:
    """
    Choose one boundary point for a sensor.

    CHANGED: This helper guarantees the path gets exactly one touch point per
    sensor, not all sampled points from the boundary.
    """
    candidates = boundary_sample(sensor, n_boundary)
    if previous_point is None:
        return candidates[0]
    return min(candidates, key=lambda p: euclidean(previous_point, p))


# =============================================================================
# ALGORITHM 1: CENTER-BASED HEURISTIC (Baseline)
# =============================================================================

def center_based_heuristic(instance: Instance, closed: bool = False) -> tuple[list[tuple], float]:
    """
    Algorithm 1: Ignore radii, treat sensor centers as TSP cities.

    CHANGED: Default length is now OPEN path length, matching the plotted path.
    Set closed=True if you want to include return-to-start distance.
    """
    centers = [(s.x, s.y) for s in instance.sensors]
    path = nearest_neighbor_tour(centers)
    length = tour_length(path) if closed else path_length(path)
    return path, length


# =============================================================================
# ALGORITHM 2: BOUNDARY SAMPLING
# =============================================================================

def boundary_sampling(
    instance: Instance,
    n_boundary: int = 12,
    closed: bool = False,
) -> tuple[list[tuple], float]:
    """
    Algorithm 2: Generate boundary candidates, but choose ONE contact point per
    sensor using a nearest-neighbor center order.
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
        k = min(k, instance.n)  # CHANGED: avoids invalid k > number of sensors.
        labels = KMeans(n_clusters=k, random_state=42, n_init="auto").fit_predict(coords)

    elif method == "dbscan":
        eps = 15.0
        labels = DBSCAN(eps=eps, min_samples=2).fit_predict(coords)
        # Noise points (-1) become their own single-sensor clusters.
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


def two_opt(path: list[tuple], closed: bool = False, max_iter: int = 1000) -> list[tuple]:
    """
    2-opt local search.

    CHANGED: Uses the same objective that is later reported:
    - path_length for open robot paths
    - tour_length for closed tours
    """
    if len(path) < 4:
        return list(path)

    cost = tour_length if closed else path_length
    best = list(path)
    best_cost = cost(best)

    improved = True
    iteration = 0
    while improved and iteration < max_iter:
        improved = False
        iteration += 1

        # For an open path, keep the start fixed by beginning i at 1.
        # For a closed tour, i could start at 0, but keeping it fixed is harmless.
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                new = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                new_cost = cost(new)
                if new_cost + 1e-9 < best_cost:
                    best = new
                    best_cost = new_cost
                    improved = True
                    break
            if improved:
                break

    return best


def order_sensors_inside_cluster(
    sensors: list[Sensor],
    previous_point: tuple | None = None,
) -> list[Sensor]:
    """
    Order sensors in a cluster by nearest-neighbor over their centers.

    CHANGED: Hybrid now orders actual sensors, then chooses one boundary point
    for each sensor. It no longer orders every boundary sample as if each sample
    were a required city.
    """
    if not sensors:
        return []

    centers = [(s.x, s.y) for s in sensors]

    if previous_point is None:
        start_idx = 0
    else:
        start_idx = min(range(len(sensors)), key=lambda i: euclidean(previous_point, centers[i]))

    order = nearest_neighbor_order_indices(centers, start_idx=start_idx)
    return [sensors[i] for i in order]


def hybrid_algorithm(
    instance: Instance,
    cluster_method: str = "kmeans",
    n_clusters: int = None,
    n_boundary: int = 12,
    use_2opt: bool = True,
    closed: bool = False,
) -> tuple[list[tuple], float]:
    """
    Algorithm 3: Hybrid Spatial Clustering + Boundary Sampling + 2-opt.

    Steps:
      1. Cluster sensors spatially.
      2. Build global route over cluster centroids.
      3. Within each cluster, order sensors by centers.
      4. For each sensor, choose exactly ONE boundary touch point.
      5. Optionally refine the resulting touch-point path with 2-opt.

    Returns (path, length).
    """
    # Step 1: Cluster.
    clusters = cluster_sensors(instance, method=cluster_method, n_clusters=n_clusters)

    # Step 2: Global route over cluster centroids.
    cluster_ids = list(clusters.keys())
    centroids = {cid: centroid(clusters[cid]) for cid in cluster_ids}
    centroid_points = [centroids[cid] for cid in cluster_ids]
    global_order_indices = nearest_neighbor_order_indices(centroid_points)
    global_order = [cluster_ids[i] for i in global_order_indices]

    # Steps 3 & 4: Build one touch point per sensor.
    full_path = []
    for cid in global_order:
        sensors_in_cluster = clusters[cid]
        previous = full_path[-1] if full_path else None

        # CHANGED: Order sensors, not boundary candidates.
        ordered_sensors = order_sensors_inside_cluster(sensors_in_cluster, previous)

        # CHANGED: Choose exactly one boundary point per sensor.
        for sensor in ordered_sensors:
            previous = full_path[-1] if full_path else None
            touch_point = choose_boundary_point(sensor, previous, n_boundary)
            full_path.append(touch_point)

    # Step 5: 2-opt refinement on the actual displayed/reported objective.
    if use_2opt and len(full_path) > 3:
        full_path = two_opt(full_path, closed=closed)

    length = tour_length(full_path) if closed else path_length(full_path)
    return full_path, length


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
    closed: bool = False,
):
    """
    Plot sensors, their coverage radii, and the drone path.

    CHANGED: The title length now matches the chosen open/closed path setting.
    If closed=True, the return-to-start edge is drawn too.
    """
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
        if closed and len(path) > 1:
            ax.plot([xs[-1], xs[0]], [ys[-1], ys[0]], '--', color='black', linewidth=1.0, alpha=0.5, label='Return edge')
        ax.plot(xs[0], ys[0], 'g^', markersize=10, label='Start')
        ax.plot(xs[-1], ys[-1], 'rs', markersize=8, label='End')

    length = tour_length(path) if closed else path_length(path)
    mode = "closed tour" if closed else "open path"
    ax.set_title(f"{title}\n{mode} length: {length:.2f}")
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
    closed: bool = False,
):
    """
    Run all three algorithms across instance sizes and distributions.
    Prints a comparison table.

    CHANGED: Benchmark uses the same open/closed setting for every algorithm.
    """
    print(f"{'n':>5} {'dist':>10} {'center':>12} {'boundary':>12} {'hybrid':>12}")
    print("-" * 58)

    for n in n_sensors_list:
        for dist in distributions:
            inst = generate_instance(n, distribution=dist, seed=seed)

            _, c_len = center_based_heuristic(inst, closed=closed)
            _, b_len = boundary_sampling(inst, closed=closed)
            _, h_len = hybrid_algorithm(inst, closed=closed)

            print(f"{n:>5} {dist:>10} {c_len:>12.2f} {b_len:>12.2f} {h_len:>12.2f}")