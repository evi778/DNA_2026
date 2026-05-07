# Center Based Algorithm

## Overview
The **Center-Based Algorithm** is a simple heuristic for the TSPN (Traveling Salesman Problem with Neighborhoods) problem. It treats sensor centers as TSP cities and finds an optimal tour through them using a greedy nearest-neighbor approach, ignoring sensor coverage radii entirely.

## Algorithm Steps

### 1. Extract Sensor Centers
- Takes all sensors and ignores their coverage radii
- Creates a list of just the center coordinates `(x, y)` for each sensor
- Result: A list of points representing only the sensor locations

### 2. Apply Nearest-Neighbor TSP
- Treats the sensor centers as cities in a classic Traveling Salesman Problem
- Uses a greedy nearest-neighbor heuristic:
  - Start from sensor 0 (or a specified starting index)
  - Repeatedly visit the closest unvisited sensor
  - Continue until all sensors are visited
- Result: An ordered path through all sensor centers with minimal distance

### 3. Calculate Path/Tour Length
- If `closed=True`: Returns the total distance as a **closed tour** (includes return to starting sensor)
- If `closed=False`: Returns the total distance as an **open path** (no return to start)

## Key Characteristics

| Aspect | Details |
|--------|---------|
| **Simplicity** | Ignores sensor coverage areas completely—only connects center points |
| **Time Complexity** | O(n²) where n is the number of sensors |
| **Quality** | Fast but often suboptimal for coverage problems |
| **Purpose** | Serves as a baseline to compare against more sophisticated algorithms |
| **Coverage** | May or may not cover all sensors depending on sensor arrangement and radii |

## Example

```
3 sensors at: 
  - Sensor 1: center (10, 10), radius 5
  - Sensor 2: center (50, 50), radius 10
  - Sensor 3: center (30, 80), radius 12

Algorithm execution:
  1. Extract centers: [(10,10), (50,50), (30,80)]
  2. Nearest-neighbor order: (10,10) → (30,80) → (50,50)
  3. Path length ≈ distance(10,10 → 30,80) + distance(30,80 → 50,50)
  4. If closed: add distance(50,50 → 10,10) back to start
```

## Advantages & Disadvantages

### Advantages ✓
- Very fast — O(n²) algorithm
- Easy to implement
- Provides a quick baseline solution
- Deterministic and reproducible

### Disadvantages ✗
- Ignores sensor coverage radii — suboptimal for coverage
- Greedy approach may miss better global solutions
- No guarantee of sensor coverage
- Does not account for drone mission requirements

## Comparison with Other Algorithms

The Center-Based Algorithm is typically compared against:
- **Boundary-Sampling Algorithm**: Samples boundary points around sensors for better coverage
- **Hybrid Algorithm**: Combines center-based and boundary-based approaches for improved solutions

## Implementation

The algorithm is implemented in `center_based_algorithm.py` and uses core utilities from `core_utils.py`:
- `nearest_neighbor_tour()`: Performs the greedy nearest-neighbor traversal
- `path_length()` / `tour_length()`: Calculates the final path distance
