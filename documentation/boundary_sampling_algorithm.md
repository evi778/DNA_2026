# Boundary Sampling Algorithm

## Overview

The **Boundary Sampling Algorithm** is a heuristic approach for the TSPN (Traveling Salesman Problem with Neighborhoods) problem that uses the coverage areas of sensors instead of only their center points.

Unlike the center-based method, which visits each sensor’s exact location, this algorithm tries to find a shorter route by choosing points on or near each sensor’s coverage boundary. Since the drone only needs to enter a sensor’s coverage area, not necessarily fly directly over the sensor, boundary sampling can reduce the overall path length.

This makes the algorithm more realistic for drone-based sensor coverage missions, where the goal is to visit every sensor neighborhood as efficiently as possible.

---

## Main Idea

Each sensor is represented as a circular coverage area:

- The center is the physical sensor location.
- The radius is the communication or coverage range.
- Any point inside the circle can count as covering that sensor.

Instead of treating the center as the only valid waypoint, the algorithm samples several candidate points around each sensor boundary and chooses points that create a shorter route.

---

## Algorithm Steps

### 1. Generate Boundary Points

For every sensor, the algorithm creates a set of sample points around the edge of its coverage circle.

These points are usually evenly spaced around the circle using angles from `0` to `2*pi`.

For a sensor with center `(x, y)` and radius `r`, a boundary point can be calculated as:

```text
sample_x = x + r × cos(angle)
sample_y = y + r × sin(angle)
```

The result is a group of possible visiting points for each sensor.

---

### 2. Choose Candidate Visit Points

After generating boundary samples, the algorithm selects one point per sensor as the waypoint for the drone path.

The purpose is to choose points that are still inside or on the edge of sensor coverage areas while also reducing the distance between consecutive waypoints.

#### This allows the drone to avoid unnecessary travel to exact sensor centers.
---

### 3. Build a Tour

Once candidate points are selected, the algorithm constructs a route through them.

The project can reuse common helper functions such as nearest-neighbor ordering and path length calculation from the utility code.

The route can be handled as:

- an **open path**, where the drone does not return to the start, or
- a **closed tour**, where the drone returns to the starting point.

---

### 4. Validate Coverage

The final path must be checked to make sure every sensor is covered.

A sensor is considered covered if at least one path point lies within that sensor’s radius.

This step is important because boundary-based methods may choose points that are close to the edge, where small numerical or implementation errors can affect coverage.

---

## Key Characteristics

| Aspect | Details |
|--------|---------|
| **Uses radii** | Takes sensor coverage radius into account |
| **Goal** | Reduce path length by visiting coverage areas instead of exact centers |
| **Sampling style** | Generates candidate points around each sensor boundary |
| **Speed** | Slower than center-based, but still practical for benchmark cases |
| **Path quality** | Usually better than center-based when radii are useful |
| **Risk** | Needs coverage validation because edge points may be sensitive |

---

## Why Boundary Sampling Helps

The TSPN problem does not require visiting the center of every neighborhood. It only requires the path to intersect each neighborhood.

For example, if two sensors have overlapping or nearby coverage circles, the drone may be able to visit points near the edges and avoid flying deep into each circle.

This can lead to:

- shorter paths,
- better use of coverage overlap,
- more realistic drone movement,
- and improved performance compared to center-only baselines.

---

## Advantages

### Strengths

- Uses sensor radius information instead of ignoring it
- Can produce shorter routes than center-based planning
- Simple enough to understand and implement
- Works well as a middle-ground algorithm between basic and advanced methods
- More connected to the real TSPN problem definition

---

## Limitations

### Weaknesses

- Quality depends on the number of boundary samples
- More samples can improve the solution but increase runtime
- Boundary points may be less stable than center points
- Does not always find the globally best path
- Requires validation to confirm every sensor is actually covered

---

## Comparison with Center-Based Algorithm

The center-based algorithm treats each sensor like a normal TSP city. This is fast, but it does not take advantage of the fact that sensors have coverage areas.

Boundary sampling improves on this by allowing the drone to visit alternative points around each sensor. These alternatives can reduce travel distance, especially when the radii are large or sensor areas overlap.

However, boundary sampling has extra computational cost because it must generate and evaluate multiple possible points for each sensor.

| Feature | Center-Based | Boundary Sampling |
|---------|--------------|------------------|
| Uses sensor centers | Yes | Not directly |
| Uses coverage radii | No | Yes |
| Expected speed | Faster | Slightly slower |
| Expected path length | Longer | Usually shorter |
| Coverage validation needed | Useful | Very important |
| TSPN realism | Basic baseline | More realistic |

