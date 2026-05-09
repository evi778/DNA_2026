# Hybrid Algorithm

## Overview

The **Hybrid Algorithm** is the most advanced path-planning method in this project. It combines three ideas:

1. **Spatial clustering**
2. **Boundary sampling**
3. **2-opt local optimization**

The goal is to create a shorter and more efficient drone path by first organizing nearby sensors into groups, then selecting useful boundary points for coverage, and finally improving the route through local optimization.

This algorithm is designed to improve on both simpler approaches:

- The **Center-Based Algorithm**, which is fast but ignores sensor radii
- The **Boundary Sampling Algorithm**, which uses radii but does not organize the problem as strongly

By combining these strategies, the hybrid method tries to balance path quality, coverage, and execution time.

---

## Main Idea

The hybrid approach works by breaking the full problem into smaller spatial regions.

Instead of planning one route across all sensors immediately, the algorithm first groups nearby sensors into clusters. It then decides the order in which to visit those clusters, plans the order of sensors inside each cluster, chooses one boundary point per sensor, and finally improves the complete path using 2-opt.

This makes the problem easier to manage because nearby sensors are handled together before the global route is finalized.

---

## Algorithm Components

### 1. Spatial Clustering

The first part of the algorithm groups sensors based on their physical positions.

The project supports clustering methods such as:

- `kmeans`
- `dbscan`

Clustering is useful because many realistic sensor networks are not perfectly uniform. Sensors may appear in groups, especially in drone monitoring or field coverage scenarios.

By identifying these groups, the algorithm can avoid jumping back and forth between distant areas too often.

---

### 2. Cluster Centroids

After clusters are created, the algorithm calculates a centroid for each group.

A centroid is the average position of the sensors in that cluster:

```text
centroid_x = average of sensor x-values
centroid_y = average of sensor y-values
```

The centroid is not necessarily a real sensor. It acts as a representative point for the whole cluster.

The algorithm then builds a global route over these centroids to decide the order in which clusters should be visited.

---

### 3. Sensor Ordering Inside Each Cluster

Once the cluster order is known, the algorithm decides how to visit sensors within each cluster.

Inside a cluster, sensors are ordered using a nearest-neighbor strategy over their center points. If the drone is already coming from a previous cluster, the algorithm can start with the sensor closest to the previous path point.

This helps create smoother transitions between clusters instead of treating every cluster as completely separate.

---

### 4. Boundary Point Selection

For each sensor, the algorithm chooses exactly one boundary touch point.

This is where the hybrid method uses the same main idea as boundary sampling: the drone does not need to fly to the center of a sensor if entering the coverage circle is enough.

A boundary point is selected based on the previous point in the path, so the algorithm tries to choose a point that connects well with the route already being built.

This step helps reduce unnecessary travel distance while still keeping the path valid for coverage.

---

### 5. 2-opt Path Refinement

After the full path is built, the algorithm can optionally apply **2-opt optimization**.

2-opt is a local search technique that improves a path by checking whether reversing a section of the route makes the total distance shorter.

A simplified version of the idea is:

```text
old route: A -> B -> C -> D
new route: A -> C -> B -> D
```

If the new route is shorter, the algorithm keeps the change.

This process repeats until no better local improvement is found or a maximum number of iterations is reached.

---

## Algorithm Steps

### Step 1: Cluster Sensors

The algorithm groups sensors using the selected clustering method.

With `kmeans`, the number of clusters can be given manually or chosen automatically. With `dbscan`, clusters are formed based on spatial density.

The output is a dictionary-like structure where each cluster contains a list of sensors.

---

### Step 2: Build a Global Cluster Route

The algorithm calculates the centroid of each cluster.

Then it applies nearest-neighbor ordering to the centroid points. This creates a rough global route that decides which cluster should be visited first, second, and so on.

This step focuses on large-scale movement across the whole sensor field.

---

### Step 3: Order Sensors Locally

For each cluster in the global route, the algorithm orders the sensors inside that cluster.

This creates a smaller local route before moving on to the next cluster.

The main goal is to keep nearby sensors together and avoid inefficient backtracking.

---

### Step 4: Select Boundary Touch Points

For every ordered sensor, the algorithm selects one boundary point.

The boundary point is chosen using the previous path point when available. This means the algorithm is not just selecting random boundary samples; it is trying to connect each new point smoothly to the current path.

---

### Step 5: Apply 2-opt

If 2-opt is enabled, the algorithm checks the complete path for local improvements.

This can reduce path length by removing unnecessary crossings or poor ordering choices created during the earlier greedy steps.

---

### Step 6: Return Path and Length

Finally, the algorithm calculates the final path length.

If the path is open, it measures the distance between consecutive waypoints.

If the path is closed, it also includes the return distance from the last point back to the first point.

---

## Key Characteristics

| Aspect | Details |
|--------|---------|
| **Main strategy** | Combines clustering, boundary sampling, and 2-opt |
| **Uses sensor radii** | Yes, through boundary touch points |
| **Uses sensor positions** | Yes, for clustering and nearest-neighbor ordering |
| **Optimization level** | Higher than center-based and basic boundary sampling |
| **Execution time** | Usually slower than the simpler algorithms |
| **Expected quality** | Often produces the shortest or near-shortest paths |
| **Best use case** | Medium to large instances, especially clustered layouts |

---

## Why the Hybrid Algorithm Helps

The hybrid method is useful because it handles the TSPN problem at multiple levels.

At the **global level**, it decides how to move between clusters.

At the **local level**, it decides how to visit sensors inside each cluster.

At the **coverage level**, it chooses boundary points instead of always visiting centers.

At the **optimization level**, it uses 2-opt to clean up the final route.

This layered approach gives the algorithm more opportunities to reduce path length than a simple one-step heuristic.

---

## Advantages

### Strengths

- Uses sensor coverage radii instead of ignoring them
- Works well when sensors are naturally grouped
- Reduces unnecessary travel between distant regions
- Can improve the route after construction using 2-opt
- Usually gives better path quality than simpler algorithms
- Flexible because it can use different clustering methods

---

## Limitations

### Weaknesses

- More complex than the center-based and boundary-sampling methods
- Runtime is higher because it performs several stages
- Clustering quality can affect the final route
- Poor cluster choices may lead to less efficient paths
- 2-opt improves locally, but it does not guarantee a globally optimal solution
- Extra parameters, such as number of clusters and boundary samples, may need tuning

---

## Comparison with Other Algorithms

The Hybrid Algorithm is intended to combine the strengths of the other two main approaches.

The center-based method is fast and simple, but it does not use coverage radii. Boundary sampling uses coverage radii, but it does not organize sensors into spatial groups before building the path.

The hybrid method adds this organization step and then applies local optimization afterward.

| Feature | Center-Based | Boundary Sampling | Hybrid |
|---------|--------------|------------------|--------|
| Uses sensor centers | Yes | Partly | Partly |
| Uses coverage radii | No | Yes | Yes |
| Uses clustering | No | No | Yes |
| Uses 2-opt refinement | No | No | Yes |
| Expected speed | Fastest | Moderate | Slowest |
| Expected path quality | Basic baseline | Improved | Usually best |
| Complexity | Low | Medium | Highest |

---

## Expected Benchmark Behavior

The Hybrid Algorithm is expected to perform best in terms of path length, especially on larger or clustered test cases.

Typical expectations:

- **Path Length:** Usually shortest among the three algorithms
- **Execution Time:** Higher than center-based and boundary sampling
- **Coverage:** Expected to be close to or equal to 100%
- **Path Points:** Usually one selected boundary point per sensor
- **Scalability:** More expensive, but still practical for the project s benchmark sizes

The trade-off is clear: the algorithm spends more computation time to produce a better route.

---

## Important Parameters

| Parameter | Meaning |
|----------|---------|
| `cluster_method` | Chooses the clustering method, such as `kmeans` or `dbscan` |
| `n_clusters` | Sets the number of clusters when applicable |
| `n_boundary` | Number of boundary samples considered per sensor |
| `use_2opt` | Enables or disables the 2-opt improvement step |
| `closed` | Determines whether the route returns to the starting point |

These parameters allow the algorithm to be adjusted depending on the test case and desired balance between speed and quality.

---

## Implementation Notes

The algorithm is implemented in:

```text
hybrid_algorithm.py
```

The file includes helper functions for:

- clustering sensors,
- calculating cluster centroids,
- ordering sensors inside clusters,
- applying 2-opt optimization,
- and running the full hybrid algorithm.

It also uses shared utilities from:

```text
core_utils.py
```

Important helper functions include:

- `nearest_neighbor_order_indices()`
- `choose_boundary_point()`
- `path_length()`
- `tour_length()`
- `euclidean()`

The main function returns:

```text
(path, length)
```

where `path` is the list of selected waypoints and `length` is the final open-path or closed-tour distance.

---

## Summary

The Hybrid Algorithm is a stronger and more complete approach for the project s TSPN drone path-planning problem.

It improves the planning process by grouping nearby sensors, selecting boundary points that respect sensor coverage, and refining the final route using 2-opt. Because of this, it is expected to produce better paths than the simpler algorithms, especially when the sensor layout is large, clustered, or has useful coverage overlap.

Its main cost is added complexity and longer execution time, but for many benchmark cases this trade-off is worth it because the path quality is usually better.

