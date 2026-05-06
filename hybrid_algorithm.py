"""
Algorithm 3: Hybrid Clustering + Boundary Sampling + 2-opt
Spatial clustering followed by boundary sampling and local optimization.
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from core_utils import (
    Instance, nearest_neighbor_order_indices, choose_boundary_point,
    path_length, tour_length, euclidean
)


# =============================================================================
# CLUSTERING
# =============================================================================

def cluster_sensors(instance: Instance, method: str = "kmeans", n_clusters: int = None) -> dict:
    """
    Cluster sensors spatially.
    Returns dict: {cluster_id: [Sensor, ...]}
    """
    coords = np.array([[s.x, s.y] for s in instance.sensors])

    if method == "kmeans":
        k = n_clusters or max(2, instance.n // 5)
        k = min(k, instance.n)  # avoid invalid k > number of sensors
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


def centroid(sensors: list) -> tuple:
    """Calculate centroid of sensors."""
    return (
        sum(s.x for s in sensors) / len(sensors),
        sum(s.y for s in sensors) / len(sensors),
    )


# =============================================================================
# 2-OPT OPTIMIZATION
# =============================================================================

def two_opt(path: list[tuple], closed: bool = False, max_iter: int = 1000) -> list[tuple]:
    """
    2-opt local search to improve path.

    Args:
        path: List of points making up the path
        closed: If True, optimize for closed tour; if False, for open path
        max_iter: Maximum iterations

    Returns:
        Optimized path
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

        # For an open path, keep the start fixed by beginning i at 1
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


# =============================================================================
# SENSOR ORDERING WITHIN CLUSTER
# =============================================================================

def order_sensors_inside_cluster(
    sensors: list,
    previous_point: tuple = None,
) -> list:
    """
    Order sensors in a cluster by nearest-neighbor over their centers.

    Args:
        sensors: List of sensors in the cluster
        previous_point: Previous path point for connection optimization

    Returns:
        Ordered list of sensors
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


# =============================================================================
# HYBRID ALGORITHM
# =============================================================================

def hybrid_algorithm(
    instance: Instance,
    cluster_method: str = "kmeans",
    n_clusters: int = None,
    n_boundary: int = 12,
    use_2opt: bool = True,
    closed: bool = False,
) -> tuple:
    """
    Algorithm 3: Hybrid Spatial Clustering + Boundary Sampling + 2-opt.

    Steps:
      1. Cluster sensors spatially.
      2. Build global route over cluster centroids.
      3. Within each cluster, order sensors by centers.
      4. For each sensor, choose exactly ONE boundary touch point.
      5. Optionally refine the resulting touch-point path with 2-opt.

    Args:
        instance: Instance with sensors
        cluster_method: 'kmeans' or 'dbscan'
        n_clusters: Number of clusters (if None, auto-determine)
        n_boundary: Number of boundary samples per sensor
        use_2opt: Whether to apply 2-opt optimization
        closed: If True, optimize for closed tour; if False, for open path

    Returns:
        (path, length) where path is list of points and length is path/tour length
    """
    # Step 1: Cluster
    clusters = cluster_sensors(instance, method=cluster_method, n_clusters=n_clusters)

    # Step 2: Global route over cluster centroids
    cluster_ids = list(clusters.keys())
    centroids = {cid: centroid(clusters[cid]) for cid in cluster_ids}
    centroid_points = [centroids[cid] for cid in cluster_ids]
    global_order_indices = nearest_neighbor_order_indices(centroid_points)
    global_order = [cluster_ids[i] for i in global_order_indices]

    # Steps 3 & 4: Build one touch point per sensor
    full_path = []
    for cid in global_order:
        sensors_in_cluster = clusters[cid]
        previous = full_path[-1] if full_path else None

        # Order sensors, not boundary candidates
        ordered_sensors = order_sensors_inside_cluster(sensors_in_cluster, previous)

        # Choose exactly one boundary point per sensor
        for sensor in ordered_sensors:
            previous = full_path[-1] if full_path else None
            touch_point = choose_boundary_point(sensor, previous, n_boundary)
            full_path.append(touch_point)

    # Step 5: 2-opt refinement
    if use_2opt and len(full_path) > 3:
        full_path = two_opt(full_path, closed=closed)

    length = tour_length(full_path) if closed else path_length(full_path)
    return full_path, length

