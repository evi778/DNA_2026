# Benchmark Parameters and Metrics

## Overview
The benchmark suite systematically measures **four key parameters** for each algorithm across all test cases to evaluate performance comprehensively.

---

## Primary Benchmark Parameters

### 1. **Path Length** ⚡
**Definition:** Total Euclidean distance the drone must travel

**Formula:**
```
Path Length = Σ distance(point_i, point_{i+1}) for all consecutive path points
```

**Why It Matters:**
- **Primary Optimization Objective**: This is what we minimize in the TSPN problem
- **Resource Consumption**: Longer paths = higher fuel consumption, battery drain
- **Mission Duration**: Path length directly correlates with mission time
- **Real-World Impact**: Determines drone endurance and coverage capacity
- **Quality Metric**: The single best indicator of solution quality

**Measurement Method:**
```
# For open paths
path_length = sum(euclidean(path[i], path[i+1]) for i in range(len(path)-1))

# For closed tours
tour_length = path_length + euclidean(path[-1], path[0])
```

**Target:** Lower is better. Best algorithms achieve 15-30% reduction over baselines.

---

### 2. **Execution Time** ⏱️
**Definition:** Computational time required to compute the solution

**Why It Matters:**
- **Practical Feasibility**: Must be fast enough for real-time deployment
- **Computational Cost**: More expensive algorithms can't be used on resource-constrained drones
- **Planning Horizon**: Quick algorithms allow replanning when conditions change
- **Scalability**: Shows how algorithm performance degrades with problem size
- **Trade-off Analysis**: Balances solution quality vs. computational resources

**Measurement Method:**
```
start_time = time.time()
path, length = algorithm(instance)
execution_time = time.time() - start_time
```

**Typical Ranges (26 test cases):**
| Algorithm | Min | Max | Avg |
|-----------|-----|-----|-----|
| Center-Based | ~0.0001s | ~0.001s | ~0.0004s |
| Boundary Sampling | ~0.001s | ~0.01s | ~0.005s |
| Hybrid | ~0.01s | ~0.5s | ~0.08s |

**Target:** Fast enough for real-time planning (< 1s for typical instances)

---

### 3. **Coverage** 🎯
**Definition:** What fraction of sensors get visited/covered by the path

**Formula:**
```
Coverage = (Number of covered sensors / Total sensors) × 100%
```

**Why It Matters:**
- **Mission Success**: 100% coverage is typically required for sensor networks
- **Algorithm Correctness**: Low coverage indicates algorithm failure
- **Boundary Sampling Effectiveness**: Tests if boundary points actually cover sensors
- **Guarantee of Solution**: All three algorithms should achieve ~100%

**Measurement Method:**
```
coverage = validate_path(path, instance)
# Returns: {
#     "per_sensor": {sensor_id: bool, ...},
#     "n_covered": int,
#     "n_total": int,
#     "all_covered": bool
# }
```

**Expected Results:**
- **Center-Based**: ~100% (visits sensor centers directly)
- **Boundary Sampling**: ~95-100% (visits boundary points)
- **Hybrid**: ~98-100% (combines clustering + boundary sampling)

**Target:** 100% coverage (mission requirement)

---

### 4. **Path Points (Waypoints)** 📍
**Definition:** Number of intermediate points in the computed path

**Why It Matters:**
- **Path Complexity**: More waypoints = more complex flight path
- **Implementation Efficiency**: Fewer waypoints = simpler drone program
- **Robustness**: Fewer points = fewer opportunities for path deviation
- **Communication Overhead**: Each waypoint must be transmitted to drone
- **Comparison Baseline**: Shows how algorithms differ in point selection

**Measurement Method:**
```
path_points = len(path)  # Simply the length of the path list
```

**Typical Ranges:**
| Instance Size | Points Range |
|---------------|--------------|
| 10 sensors | 10-50 points |
| 20 sensors | 20-100 points |
| 50 sensors | 50-150 points |
| 100 sensors | 100-200 points |

**Why Different Algorithms Differ:**
- **Center-Based**: Exactly N points (one per sensor center)
- **Boundary Sampling**: Exactly N points (one per sensor boundary)
- **Hybrid**: N points + 2-opt optimizations (may add/remove intermediate points)

---

## Derived Metrics (Calculated from Primary Parameters)

### Efficiency Score
**Definition:** Path quality relative to computational cost

```
Efficiency = (Average Path Length) / (Average Execution Time)
```

**Interpretation:**
- High score = Good quality solutions computed quickly
- Low score = Either poor solutions or slow computation
- Used to identify best balance between quality and speed

### Scalability Factor
**Definition:** How performance changes with problem size

```
Scalability = (Metric at 100 sensors) / (Metric at 10 sensors)
```

**For Path Length:**
```
Path Scalability = Length(100 sensors) / Length(10 sensors)
Expected: ~3-5x growth (sublinear with instance size)
```

**For Execution Time:**
```
Time Scalability = Time(100 sensors) / Time(10 sensors)
Expected: ~100-1000x growth (near-quadratic)
```

### Quality over Speed Trade-off
**Definition:** Path quality improvement vs. time investment

**Visualization:**
- X-axis: Execution Time (log scale)
- Y-axis: Normalized Path Length (0-1)
- Points: Each algorithm-instance combination

**Interpretation:**
- Upper left: Fast but poor quality
- Lower right: Slow but excellent quality
- Optimal: High quality with reasonable time

---

## Benchmark Data Collection

### Data Flow

```
Test Case Instance
    ↓
Run Algorithm
    ├─ Measure: execution_time
    ├─ Get: path
    ├─ Calculate: path_length
    └─ Validate: coverage
    ↓
Store Results
    ├─ algorithm_name
    ├─ instance_name
    ├─ length
    ├─ time
    ├─ coverage (dict)
    └─ path_points
    ↓
JSON Summary
    ↓
Analysis & Graphs
```

### JSON Result Structure
```json
{
  "test_case_name": {
    "algorithm_name": {
      "algorithm": "Algorithm Full Name",
      "length": 149.32,
      "time": 0.005123,
      "coverage": {
        "per_sensor": {"0": true, "1": true, "2": true},
        "n_covered": 20,
        "n_total": 20,
        "all_covered": true
      },
      "path_points": 20
    }
  }
}
```

---

## Benchmark Analysis Outputs

### 1. Path Length Comparison Graph
**Shows:** Bar chart of path lengths across all test cases
**Why:** Directly compares solution quality between algorithms

### 2. Execution Time Comparison Graph
**Shows:** Bar chart of execution times across all test cases
**Why:** Compares computational efficiency

### 3. Coverage Comparison Graph
**Shows:** Coverage percentage for each algorithm on each test
**Why:** Verifies all algorithms meet mission requirements

### 4. Scalability - Path Length
**Shows:** Line graph of path length vs. number of sensors
**Why:** Shows how solutions degrade with problem size
**Pattern:** Should be roughly linear to sublinear in n

### 5. Scalability - Execution Time
**Shows:** Line graph of execution time vs. number of sensors
**Why:** Shows computational complexity growth
**Pattern:** Should be quadratic or better (O(n²) or better)

### 6. Quality vs. Speed Trade-off
**Shows:** Scatter plot: execution time vs. normalized path length
**Why:** Visualizes algorithm trade-offs
**Insight:** Shows which algorithms are efficient (lower left) vs. high-quality (lower right)

### 7. Performance Heatmap
**Shows:** 3×3 grid of normalized metrics per algorithm
**Metrics:** Execution Time | Path Length | Coverage
**Why:** Quick visual summary of overall performance

---

## Benchmark Execution Process

### Step 1: Algorithm Execution
```
for test_case in all_test_cases:
    for algorithm in [center_based, boundary_sampling, hybrid]:
        Run algorithm on test_case
        Record: time, path, length, coverage
```

### Step 2: Results Storage
```
# Store in memory and save to JSON
benchmark_results[test_case][algorithm] = {
    "length": <calculated_value>,
    "time": <measured_value>,
    "coverage": <validated_dict>,
    "path_points": <point_count>
}
```

### Step 3: Data Analysis
```
For each algorithm and metric:
  - Calculate averages across all test cases
  - Identify best/worst performers
  - Compute scalability factors
  - Generate comparison graphs
```

### Step 4: Report Generation
```
Create outputs:
  - 7 Analysis Graphs (PNG)
  - Markdown Report with insights
  - Performance summary tables
```

---

## Benchmark Interpretation Guidelines

### Path Length Analysis
- **10-20% difference**: Significant but not major
- **20-40% difference**: Substantial improvement
- **40%+ difference**: Major algorithmic advantage

### Time Comparison
- **< 0.001s difference**: Microsecond-level, practically equivalent
- **0.001-0.01s difference**: Perceptible, may matter for real-time
- **> 0.1s difference**: Significant practical difference

### Coverage Results
- **100% coverage**: Algorithm is correct
- **95-99% coverage**: Minor edge cases (acceptable if documented)
- **< 95% coverage**: Algorithm failure, investigate bug

### Scalability Assessment
- **Path length scales sub-linearly**: Good algorithm design
- **Path length scales linearly**: Acceptable for this problem
- **Path length scales super-linearly**: Poor algorithm behavior
- **Time scales O(n²)**: Expected for nearest-neighbor methods
- **Time scales O(n³) or worse**: Algorithm needs optimization

---

## Performance Baselines

### Expected Results Summary

| Metric | Center-Based | Boundary Sampling | Hybrid |
|--------|-------------|------------------|--------|
| **Avg Path Length** | 100% (baseline) | 85-95% | 70-85% |
| **Avg Time** | < 0.001s | 0.001-0.01s | 0.01-0.1s |
| **Coverage** | ~100% | ~99% | ~100% |
| **Quality/Speed** | Best speed | Moderate | Best quality |

### Success Criteria
✓ All algorithms achieve > 95% coverage  
✓ Hybrid produces 15-30% shorter paths than Center-Based  
✓ Execution times remain < 1 second for 100 sensors  
✓ Time scales no worse than O(n²)  

---

## Usage Examples

### Load and Analyze Results
```
import json

# Load benchmark results
with open("results/benchmark_results.json") as f:
    results = json.load(f)

# Analyze specific test case
test_case = "medium_clustered_20"
for algo, data in results[test_case].items():
    print(f"{algo}:")
    print(f"  Path Length: {data['length']:.2f}")
    print(f"  Time: {data['time']:.6f}s")
    print(f"  Coverage: {data['coverage']['n_covered']}/{data['coverage']['n_total']}")
```

### Calculate Improvement
```
# Hybrid vs Center-Based improvement
cb_length = results[test_case]["center_based"]["length"]
hybrid_length = results[test_case]["hybrid"]["length"]
improvement = (cb_length - hybrid_length) / cb_length * 100
print(f"Improvement: {improvement:.1f}%")
```

---

## Conclusion

**Benchmark parameters form a complete evaluation framework:**

1. **Path Length**: Measures solution quality (optimization objective)
2. **Execution Time**: Measures computational efficiency (feasibility)
3. **Coverage**: Validates algorithm correctness (mission requirement)
4. **Path Points**: Measures solution complexity (implementability)

Together, these metrics provide a 360° view of algorithm performance across quality, speed, correctness, and practicality dimensions.

