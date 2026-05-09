# Proposed Addition: Genetic Algorithm for TSPN Path Planning

## Overview

A useful future improvement for this project would be adding a **Genetic Algorithm** for the TSPN drone path-planning problem.

The current project already compares heuristic methods such as center-based planning, boundary sampling, and the hybrid algorithm. A genetic algorithm would add a different style of optimization because it searches through many possible solutions instead of building only one greedy route.

The main idea is to create a population of possible drone paths, evaluate how good they are, and repeatedly improve them over several generations.

This proposed addition would be especially useful for larger or more complex test cases where greedy choices may not always lead to the best final route.

---

## Main Idea

A genetic algorithm is inspired by natural selection.

Instead of creating one path directly, the algorithm creates many candidate paths. Each candidate path is treated like an individual in a population.

Better paths are more likely to be selected and combined to create new paths. Over time, the population should improve.

For this project, a candidate solution could represent:

- the order in which sensors are visited,
- the selected waypoint for each sensor,
- and optionally whether the waypoint is a center point or a boundary point.

The goal is to evolve paths that are shorter while still covering every sensor.

---

## Why This Fits the Project

The TSPN problem is difficult because the drone does not need to visit exact sensor centers. It only needs to enter each sensor s coverage area.

This creates many possible valid routes.

A genetic algorithm fits this situation well because it can explore many different route orders and waypoint choices. Unlike nearest-neighbor methods, it does not commit to one route too early.

It can also be combined with ideas already used in the project, especially boundary sampling and 2-opt optimization.

---

## Proposed Algorithm Design

### 1. Create an Initial Population

The algorithm starts by generating multiple possible routes.

Each route contains all sensors in a specific order.

For example:

```text
Route 1: Sensor 0 -> Sensor 3 -> Sensor 1 -> Sensor 2
Route 2: Sensor 2 -> Sensor 0 -> Sensor 3 -> Sensor 1
Route 3: Sensor 1 -> Sensor 2 -> Sensor 0 -> Sensor 3
```

The initial population can be created using:

- random sensor orderings,
- nearest-neighbor routes,
- center-based routes,
- or routes based on the hybrid algorithm.

Including some good heuristic solutions at the beginning may help the genetic algorithm improve faster.

---

### 2. Select Waypoints

After a sensor order is created, the algorithm chooses a waypoint for each sensor.

There are two possible simple approaches:

| Approach | Description |
|---------|-------------|
| **Center-based waypoint** | Uses the sensor center as the waypoint |
| **Boundary-aware waypoint** | Chooses a point on or inside the sensor s coverage circle |

The boundary-aware version would fit the TSPN problem better because the drone only needs to reach the coverage area.

A simple version could reuse the project s boundary sampling logic to choose candidate points.

---

### 3. Evaluate Fitness

Each route needs a fitness score.

The fitness function should reward shorter paths and penalize invalid solutions.

A possible fitness formula is:

```text
fitness = path_length + coverage_penalty
```

Where:

```text
coverage_penalty = large penalty if one or more sensors are not covered
```

Since the goal is to minimize path length, lower fitness values are better.

The fitness function could consider:

- total path length,
- whether all sensors are covered,
- execution time,
- and number of waypoints.

The most important requirement is that a route with incomplete coverage should not be considered better just because it is short.

---

### 4. Selection

Selection chooses which routes are allowed to become parents for the next generation.

Better routes should have a higher chance of being selected.

Possible selection methods include:

- **tournament selection**
- **rank-based selection**
- **roulette-wheel selection**

For this project, tournament selection would be a good simple choice.

In tournament selection, a few routes are chosen randomly, and the best one among them becomes a parent.

This keeps the algorithm easy to implement while still favoring stronger solutions.

---

### 5. Crossover

Crossover combines two parent routes to create a child route.

Because each sensor must appear exactly once, normal crossover cannot be used directly. The algorithm must avoid duplicate sensors and missing sensors.

A suitable crossover method would be **ordered crossover**.

Example:

```text
Parent 1: 0 -> 1 -> 2 -> 3 -> 4
Parent 2: 3 -> 4 -> 1 -> 0 -> 2

Child:    0 -> 1 -> 4 -> 3 -> 2
```

The child keeps part of one parent s ordering and fills the rest using the other parent.

This allows the algorithm to mix useful route sections from different solutions.

---

### 6. Mutation

Mutation adds randomness so the population does not become too similar too quickly.

For this project, mutation could be very simple.

Examples:

| Mutation Type | Description |
|--------------|-------------|
| **Swap mutation** | Swap two sensors in the route |
| **Reverse mutation** | Reverse a small section of the route |
| **Waypoint mutation** | Choose a different boundary point for one sensor |

Mutation helps the algorithm explore new paths that crossover alone might not create.

---

### 7. Optional 2-opt Cleanup

After crossover and mutation, the algorithm could optionally apply 2-opt to the best route in each generation or only to the final best route.

This would combine global search from the genetic algorithm with local improvement from 2-opt.

The genetic algorithm would explore many route possibilities, while 2-opt would clean up inefficient local choices.

---

## Algorithm Steps

### Step 1: Generate Population

Create a population of candidate routes.

Each route is a full ordering of all sensors.

---

### Step 2: Convert Routes to Paths

For each route, choose actual path points.

These points may be sensor centers or selected boundary points.

---

### Step 3: Measure Fitness

Calculate the path length and validate coverage.

Routes with shorter paths and full coverage receive better scores.

---

### Step 4: Select Parents

Choose stronger routes from the population using a selection method such as tournament selection.

---

### Step 5: Create New Routes

Use crossover and mutation to generate a new population.

This creates new route combinations while still preserving all sensors.

---

### Step 6: Repeat for Multiple Generations

Continue evaluating, selecting, crossing, and mutating routes.

The best solution should gradually improve over time.

---

### Step 7: Return Best Path

After the final generation, return the best path found and its total length.

---

## Key Characteristics

| Aspect | Details |
|--------|---------|
| **Algorithm type** | Population-based optimization |
| **Main goal** | Search for shorter valid TSPN paths |
| **Uses randomness** | Yes |
| **Uses sensor radii** | Yes, if combined with boundary-aware waypoints |
| **Expected quality** | Potentially strong, especially on harder cases |
| **Execution time** | Higher than greedy algorithms |
| **Best use case** | Larger or more complex instances |

---

## Advantages

### Strengths

- Explores many possible routes instead of only one greedy route
- Can escape some poor local choices
- Works naturally with route-ordering problems
- Can be combined with boundary sampling
- Can be improved further with 2-opt
- Provides a new algorithm category for comparison

---

## Limitations

### Weaknesses

- Slower than center-based and boundary-sampling methods
- Requires parameter tuning
- Results may vary because of randomness
- Does not guarantee the globally optimal solution
- More complex to implement and explain
- Needs careful handling to avoid invalid routes with repeated or missing sensors

---

## Suggested Parameters

| Parameter | Meaning |
|----------|---------|
| `population_size` | Number of candidate routes in each generation |
| `generations` | Number of improvement cycles |
| `mutation_rate` | Probability of applying mutation |
| `crossover_rate` | Probability of combining two parent routes |
| `tournament_size` | Number of candidates compared during tournament selection |
| `use_boundary_points` | Whether to use boundary-aware waypoint selection |
| `use_2opt` | Whether to apply 2-opt improvement |

Example starting values:

| Parameter | Suggested Value |
|----------|-----------------|
| `population_size` | 50 |
| `generations` | 100 |
| `mutation_rate` | 0.1 |
| `crossover_rate` | 0.8 |
| `tournament_size` | 3 |

These values are simple enough for testing but can be adjusted later for performance experiments.

---

## Expected Benchmark Behavior

The Genetic Algorithm would likely be slower than the existing algorithms, but it may produce better paths on difficult instances.

Expected results:

- **Path Length:** Could be shorter than boundary sampling and sometimes competitive with hybrid
- **Execution Time:** Higher because many candidate routes are evaluated
- **Coverage:** Should be close to 100% if coverage validation is built into the fitness function
- **Path Points:** Usually one waypoint per sensor
- **Consistency:** May vary between runs unless a random seed is used

The algorithm would be most useful for:

- large test cases,
- clustered sensor layouts,
- dense coverage cases,
- and cases where greedy routes perform poorly.

---

## Comparison with Existing Algorithms

| Feature | Center-Based | Boundary Sampling | Hybrid | Genetic Algorithm |
|---------|--------------|------------------|--------|------------------|
| Uses sensor radii | No | Yes | Yes | Yes, if boundary-aware |
| Uses randomness | No | No or limited | Limited | Yes |
| Uses population search | No | No | No | Yes |
| Uses local optimization | No | No | Yes | Optional |
| Expected speed | Fastest | Fast | Moderate | Slowest |
| Expected quality | Basic | Improved | Strong | Potentially strong |
| Implementation difficulty | Low | Medium | Higher | Higher |

The Genetic Algorithm would not replace the existing methods. Instead, it would provide another comparison point in the benchmark suite.

---

## Possible File Structure

If implemented, the new algorithm could be placed in:

```text
genetic_algorithm.py
```

The file could include functions such as:

```text
create_initial_population()
evaluate_fitness()
tournament_selection()
ordered_crossover()
mutate_route()
genetic_algorithm()
```

It could reuse existing project utilities from:

```text
core_utils.py
```

Useful shared functions may include:

- distance calculation,
- path length calculation,
- tour length calculation,
- boundary point selection,
- and coverage validation.

---

## Pseudocode

```text
function genetic_algorithm(instance):
    population = create_initial_population(instance)

    for generation in range(max_generations):
        fitness_scores = evaluate_all_routes(population)

        new_population = []

        while new_population is not full:
            parent_1 = select_parent(population, fitness_scores)
            parent_2 = select_parent(population, fitness_scores)

            child = crossover(parent_1, parent_2)
            child = mutate(child)

            new_population.append(child)

        population = new_population

    best_route = route with best fitness
    path = convert_route_to_waypoints(best_route)

    if use_2opt:
        path = apply_2opt(path)

    return path, path_length(path)
```

---

## Summary

A Genetic Algorithm would be a strong proposed addition because it introduces a population-based search strategy to the project.

Instead of relying only on greedy decisions, it would evolve many possible drone paths and gradually improve them. When combined with boundary-aware waypoint selection and optional 2-opt refinement, it could become a powerful algorithm for solving larger or more complicated TSPN instances.

The main trade-off is execution time. However, as a proposed future improvement, it would make the project more complete by adding a different optimization approach to compare against the current algorithms.

