# Test Case Documentation

## Overview
The test suite contains 26 different test cases that systematically vary **problem size**, **sensor distribution**, and **coverage characteristics** to comprehensively evaluate algorithm performance.

---

## Test Case Categories

### 1. **Scalability Testing** (Size Variation)

These test cases vary the **number of sensors** to measure algorithm performance across different problem sizes.

| Test Case | Sensors | Space | Radii | Distribution | Purpose |
|-----------|---------|-------|-------|--------------|---------|
| `small_uniform_10` | **10** | 100×100 | 3-8 | Uniform | Baseline small problem |
| `small_clustered_10` | **10** | 100×100 | 4-10 | Clustered | Small with grouped sensors |
| `medium_uniform_20` | **20** | 100×100 | 3-8 | Uniform | Medium-scale problem |
| `medium_clustered_20` | **20** | 100×100 | 4-10 | Clustered | Medium with groups |
| `large_uniform_50` | **50** | 150×150 | 3-8 | Uniform | Large-scale problem |
| `large_clustered_50` | **50** | 150×150 | 4-10 | Clustered | Large with clusters |
| `xlarge_uniform_100` | **100** | 200×200 | 3-8 | Uniform | Very large problem |
| `xlarge_clustered_100` | **100** | 200×200 | 4-10 | Clustered | Very large with clusters |

**Variables Changed:** `n_sensors`, `space_size`

**Why Needed:** Tests how algorithms scale with problem difficulty. Execution time and path quality typically worsen as the number of sensors increases.

**What It Tests:**
- Algorithm runtime performance over different sizes
- Memory efficiency
- Path quality degradation at scale
- Whether solutions remain valid for large problems

---

### 2. **Coverage Density Testing** (Radius Variation)

These test cases vary the **sensor coverage radius** to test algorithm behavior under different coverage conditions.

| Test Case | Sensors | Space | Radii | Distribution | Purpose |
|-----------|---------|-------|-------|--------------|---------|
| `sparse_20` | 20 | 100×100 | **2-4** (small) | Uniform | Minimal coverage |
| `dense_20` | 20 | 100×100 | **8-15** (large) | Uniform | Extensive overlap |

**Variables Changed:** `radius_range`

**Why Needed:** 
- **Sparse (2-4):** Tests algorithms when sensors have minimal coverage areas, requiring precise path planning
- **Dense (8-15):** Tests algorithms when there's significant overlap, potentially allowing shortcuts

**What It Tests:**
- Path length changes with coverage density
- Whether algorithms exploit overlapping coverage
- Algorithm robustness under extreme coverage conditions

---

### 3. **Spatial Distribution Testing** (Clustered vs Uniform)

These test cases vary how sensors are **distributed spatially** to test algorithms on different real-world scenarios.

| Test Case | Pattern | Sensors | Space | Purpose |
|-----------|---------|---------|-------|---------|
| Any with `uniform` | Randomly spread | Various | Various | Sensors evenly dispersed |
| Any with `clustered` | Groups of sensors | Various | Various | Sensors concentrate in regions |
| `tight_clusters_30` | Dense clusters | 30 | 100×100 | Extreme clustering |
| `very_large_space_30` | Sparse spread | 30 | **300×300** | Very spread out |

**Variables Changed:** `distribution`, `space_size`

**Why Needed:**
- **Uniform:** Tests baseline algorithm performance on well-distributed problems
- **Clustered:** Tests algorithms' ability to recognize and exploit regional grouping
- **Tight clusters:** Tests extreme local optimization needs
- **Large space:** Tests long-distance planning and connectivity

**What It Tests:**
- Whether clustering algorithms effectively identify sensor groups
- Quality of within-cluster vs between-cluster routing
- Path efficiency on different spatial patterns
- Algorithm adaptability to distribution patterns

---

### 4. **Uniform Radius Testing** (All Sensors Same Size)

These test cases use **identical coverage radii** for all sensors to isolate the effect of sensor placement.

| Test Case | Sensors | Radii | Space | Distribution |
|-----------|---------|-------|-------|--------------|
| `uniform_radii_small_10` | 10 | **6.0 (all)** | 100×100 | Uniform |
| `uniform_radii_small_clustered_10` | 10 | **6.0 (all)** | 100×100 | Clustered |
| `uniform_radii_medium_20` | 20 | **5.0 (all)** | 100×100 | Uniform |
| `uniform_radii_medium_clustered_20` | 20 | **5.0 (all)** | 100×100 | Clustered |
| `uniform_radii_large_50` | 50 | **4.0 (all)** | 150×150 | Uniform |
| `uniform_radii_large_clustered_50` | 50 | **4.0 (all)** | 150×150 | Clustered |

**Variables Changed:** `radius_range` (min = max), keeping both `distribution` variations

**Why Needed:** Eliminates radius variance to focus on how sensor **placement** affects solutions. This makes it easier to measure pure algorithm performance without coverage-size interference.

**What It Tests:**
- Algorithm behavior when coverage is predictable and uniform
- Pure spatial optimization performance
- Whether boundary-sampling algorithms improve when radii are consistent
- Easier baseline for comparing distribution effects

---

## Summary of Variables

### Primary Variables Modified

| Variable | Test Categories | Range |
|----------|-----------------|-------|
| **n_sensors** | Scalability | 10 → 100 |
| **space_size** | Spatial Distribution | 100×100 → 300×300 |
| **radius_range** | Coverage Density | (2-4) → (8-15) |
| **distribution** | Spatial Distribution | "uniform" vs "clustered" |
| **seed** | Reproducibility | 42-59 (unique per case) |

---

## Test Case Selection Strategy

### For Algorithm Development
- Start with **small cases** (10 sensors) for quick iteration
- Use **uniform distribution** first for baseline validation
- Test with **uniform radii** to debug placement logic

### For Performance Benchmarking
- Include all **scalability sizes** (10, 20, 50, 100)
- Include both **distributions** for each size
- Test **extreme cases** (sparse, dense, very large space)

### For Real-World Validation
- Use **clustered cases** (realistic drone scenarios)
- Test multiple **radius ranges** (deployment variations)
- Compare **uniform vs clustered** at same scale

---

## Usage Examples

### Load a Single Test Case
```python
from test_cases import load_test_case
instance = load_test_case("medium_uniform_20")
```

### Group Test Cases by Category
```python
from test_cases import (
    get_small_test_cases,
    get_clustered_test_cases,
    get_large_test_cases
)

small = get_small_test_cases()      # All small instances
clustered = get_clustered_test_cases()  # All clustered distributions
large = get_large_test_cases()      # All large instances
```

### Run All Test Cases
```python
from test_cases import get_all_test_cases
all_instances = get_all_test_cases()

for name, instance in all_instances.items():
    print(f"Testing {name}: {instance.n} sensors")
```

---

## Key Insights

1. **Scalability Challenge:** As sensors increase (10→100), algorithms must handle quadratic growth in problem complexity
2. **Distribution Matters:** Clustered cases often require different strategies than uniform distributions
3. **Radius Sensitivity:** Sparse vs dense coverage significantly affects path quality and algorithm effectiveness
4. **Trade-offs:** Larger spaces and more sensors increase execution time but provide optimization opportunities
5. **Reproducibility:** Each test case has a fixed seed for consistent, reproducible results
