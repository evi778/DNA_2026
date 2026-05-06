# TSPN Drone Path Planning System

## Overview

This project implements and benchmarks three algorithms for solving the **Traveling Salesman Problem with Neighborhood (TSPN)** for autonomous drone sensor data collection. The system finds optimal or near-optimal paths for drones to visit and collect data from distributed sensors with coverage radii.

**Algorithms Implemented:**
1. **Center-Based Heuristic** - Simple baseline treating sensor centers as TSP cities
2. **Boundary Sampling** - Boundary-aware nearest neighbor with coverage consideration
3. **Hybrid Algorithm** - Spatial clustering + boundary sampling + 2-opt optimization

## Project Structure

```
DNA_2026/
├── main.py                          # Main execution file - runs all benchmarks
├── core_utils.py                    # Shared utilities, data structures, validation
├── center_based_algorithm.py         # Algorithm 1 implementation
├── boundary_sampling_algorithm.py    # Algorithm 2 implementation
├── hybrid_algorithm.py              # Algorithm 3 + clustering + 2-opt
├── test_cases.py                    # 12 test scenarios with different characteristics
├── visualization.py                 # Plotting utilities for paths and comparisons
├── benchmark_reporter.py            # Graph generation and report creation
├── tspn_drone.py                   # Original implementation (reference)
│
└── results/                         # Generated results
    ├── BENCHMARK_REPORT.md          # Comprehensive markdown report
    ├── benchmark_results.json       # Raw benchmark data
    ├── individual/                  # Individual algorithm visualizations (36 PNGs)
    ├── comparisons/                 # Side-by-side algorithm comparisons (12 PNGs)
    └── graphs/                      # Analysis graphs (7 PNGs)
```

## Installation

### Prerequisites
- Python 3.8+
- Required packages: numpy, matplotlib, scikit-learn

### Setup

```bash
# Clone/navigate to project directory
cd DNA_2026

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install numpy matplotlib scikit-learn
```

## Usage

### Running the Complete Benchmark

```bash
python main.py
```

This will:
1. Generate 12 diverse test cases
2. Run all three algorithms on each test case
3. Generate visualizations (individual and comparison plots)
4. Save JSON results
5. Print summary statistics

**Output Location:** `results/` directory

### Generating Report and Graphs

```bash
python benchmark_reporter.py results/benchmark_results.json results
```

This will generate:
- 7 comparison and analysis graphs
- Comprehensive markdown report with insights and recommendations

### Using Individual Algorithms

```python
from core_utils import generate_instance
from center_based_algorithm import center_based_heuristic
from boundary_sampling_algorithm import boundary_sampling
from hybrid_algorithm import hybrid_algorithm

# Generate test instance
instance = generate_instance(
    n_sensors=20,
    space_size=100.0,
    radius_range=(4.0, 10.0),
    distribution="clustered",
    seed=42
)

# Run algorithms
path_center, length_center = center_based_heuristic(instance)
path_boundary, length_boundary = boundary_sampling(instance)
path_hybrid, length_hybrid = hybrid_algorithm(instance, use_2opt=True)

print(f"Center-based: {length_center:.2f}")
print(f"Boundary sampling: {length_boundary:.2f}")
print(f"Hybrid: {length_hybrid:.2f}")
```

## Test Cases

The benchmark includes 12 diverse test scenarios:

| Name | Sensors | Distribution | Focus | Radius Range |
|------|---------|--------------|-------|--------------|
| small_uniform_10 | 10 | Uniform | Baseline small | 3-8 |
| small_clustered_10 | 10 | Clustered | Baseline clustered | 4-10 |
| medium_uniform_20 | 20 | Uniform | Medium size | 3-8 |
| medium_clustered_20 | 20 | Clustered | Medium clustered | 4-10 |
| large_uniform_50 | 50 | Uniform | Large scale | 3-8 |
| large_clustered_50 | 50 | Clustered | Large clustered | 4-10 |
| xlarge_uniform_100 | 100 | Uniform | Scalability test | 3-8 |
| xlarge_clustered_100 | 100 | Clustered | Scalability test | 4-10 |
| sparse_20 | 20 | Uniform | Sparse coverage (2-4 radius) | 2-4 |
| dense_20 | 20 | Uniform | Dense coverage (8-15 radius) | 8-15 |
| tight_clusters_30 | 30 | Clustered | Tight clustering | 3-8 |
| very_large_space_30 | 30 | Uniform | Large space coverage | 3-8 |

## Generated Reports and Visualizations

### Individual Visualizations
Each algorithm on each test case showing:
- Sensor locations with coverage circles
- Drone path with start/end markers
- Path length and coverage ratio

### Comparison Visualizations
Side-by-side comparison of all three algorithms for each test case

### Analysis Graphs

1. **Path Length Comparison** - Bar chart comparing path lengths across test cases
2. **Execution Time Comparison** - Bar chart comparing computational efficiency
3. **Coverage Comparison** - Sensor coverage percentages
4. **Scalability: Path Length** - How path length scales with instance size
5. **Scalability: Execution Time** - How computation time scales
6. **Quality vs Speed Trade-off** - Pareto frontier analysis
7. **Performance Heatmap** - Normalized performance metrics

### Markdown Report
Comprehensive report with:
- Algorithm descriptions
- Detailed results analysis
- Performance metrics summary
- Recommendations for algorithm selection
- Performance insights and observations
- Computational complexity analysis

## Key Findings

### Performance Summary (Average across all test cases)

| Algorithm | Avg Path Length | Avg Time | Coverage |
|-----------|-----------------|----------|----------|
| Center-Based | 713.56 | 0.27ms | 100% |
| Boundary Sampling | 603.96 | 0.99ms | 100% |
| Hybrid (KMeans + 2-opt) | 557.38 | 142.14ms | 100% |

### Key Observations

1. **Path Quality:** Hybrid algorithm produces ~8-15% shorter paths than Boundary Sampling
2. **Speed vs Quality:** Hybrid is slower but significantly better quality
3. **Scalability:** All algorithms scale well; clustering amortizes for larger instances
4. **Distribution Impact:** Hybrid shows 20-40% improvement on clustered instances
5. **Coverage:** All algorithms achieve 100% sensor coverage

## Algorithm Details

### 1. Center-Based Heuristic
- **Time Complexity:** O(n²)
- **Space Complexity:** O(n)
- **Best For:** Baseline comparison, quick approximation
- **Description:** Applies nearest-neighbor TSP heuristic to sensor centers, ignoring radii

### 2. Boundary Sampling
- **Time Complexity:** O(n² · b) where b ≈ 12
- **Space Complexity:** O(n·b)
- **Best For:** Medium instances with specific coverage requirements
- **Description:** Samples boundary points around each sensor and selects closest point

### 3. Hybrid Algorithm
- **Time Complexity:** O(n·log(n) + k·(n/k)² + 2opt)
- **Space Complexity:** O(n + k)
- **Best For:** Large instances, high-quality solutions
- **Description:** Combines K-means clustering with boundary sampling and 2-opt local search

## File Descriptions

### Core Files

**core_utils.py**
- Data structures: `Sensor`, `Instance`, `AlgorithmResult`
- Utilities: distance calculations, point sampling, validation

**center_based_algorithm.py**
- `center_based_heuristic()` - Simple TSP on sensor centers

**boundary_sampling_algorithm.py**
- `boundary_sampling()` - Nearest-neighbor with boundary sampling

**hybrid_algorithm.py**
- `cluster_sensors()` - K-means/DBSCAN clustering
- `two_opt()` - Local search optimization
- `hybrid_algorithm()` - Main hybrid algorithm

### Support Files

**test_cases.py**
- `TEST_CASES` - Configuration dictionary
- `load_test_case()` - Generate specific test case
- Helper functions for test case categorization

**visualization.py**
- `plot_instance_and_path()` - Individual visualization
- `create_comparison_plot()` - Side-by-side comparison

**benchmark_reporter.py**
- `generate_benchmark_graphs()` - Create analysis graphs
- `generate_markdown_report()` - Generate markdown report

**main.py**
- Orchestration and benchmark execution
- Result aggregation and summarization

## Configuration

Key parameters in `main.py`:

```python
CLOSED_TOUR = False      # Use open paths vs closed tours
VISUALIZE = True         # Generate visualizations
SAVE_JSON = True         # Save JSON results
OUTPUT_DIR = "results"   # Output directory
```

Modify these as needed for different benchmark configurations.

## Extending the Project

### Adding New Test Cases

Edit `test_cases.py`:
```python
TEST_CASES = {
    "my_test": {
        "n_sensors": 25,
        "space_size": 120.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 100,
    },
    # ... rest of test cases
}
```

### Adding New Algorithms

1. Create `my_algorithm.py`:
```python
def my_algorithm(instance, **kwargs):
    # Implementation
    path = [...]  # List of (x, y) tuples
    length = path_length(path)
    return path, length
```

2. Update `main.py` to include the new algorithm in `run_all_algorithms()`

## Performance Tips

- For faster benchmarking, reduce test case sizes in `test_cases.py`
- Set `VISUALIZE = False` to skip image generation
- Use `xlarge_clustered_100` test case for stress testing

## Troubleshooting

### Import Errors
```bash
pip install numpy matplotlib scikit-learn
```

### No Visualizations Generated
Check if matplotlib backend is installed: `pip install matplotlib --upgrade`

### Out of Memory on Large Test Cases
Reduce instance sizes in `test_cases.py` or increase available memory

## References

- TSP Heuristics: Nearest Neighbor, 2-opt
- Clustering: K-means (scikit-learn)
- Sensor Coverage: Geometric algorithms
- Optimization: Local search metaheuristics

## Authors

- E. Dimitrievska
- M. Peeva  
- F. Petrovski

## License

Academic project - feel free to modify and extend

## Future Improvements

- [ ] Implement genetic algorithms
- [ ] Add parallel algorithm execution
- [ ] Support for 3D drone paths
- [ ] Real-time visualization
- [ ] Web UI for benchmark comparison
- [ ] Additional metaheuristics (ant colony, particle swarm)
- [ ] Integration with real sensor data

---

For detailed benchmark results and analysis, see `results/BENCHMARK_REPORT.md`

