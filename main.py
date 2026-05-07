"""
Main orchestration file for TSPN Drone Path Planning
Runs all three algorithms on all test cases and generates visualizations.
"""

import time
import os
from pathlib import Path
import json

from core_utils import validate_path, AlgorithmResult
from center_based_algorithm import center_based_heuristic
from boundary_sampling_algorithm import boundary_sampling
from hybrid_algorithm import hybrid_algorithm, cluster_sensors
from test_cases import get_all_test_cases, get_test_case_names, get_test_case_config
from visualization import plot_instance_and_path, create_comparison_plot
from benchmark_reporter import generate_benchmark_graphs, generate_markdown_report


# Configuration
OUTPUT_DIR = "results"
CLOSED_TOUR = False  # Use open paths instead of closed tours
VISUALIZE = True
SAVE_JSON = True


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(f"{OUTPUT_DIR}/individual").mkdir(exist_ok=True)
    Path(f"{OUTPUT_DIR}/comparisons").mkdir(exist_ok=True)
    Path(f"{OUTPUT_DIR}/visualizations").mkdir(exist_ok=True)


def run_all_algorithms(test_case_name: str, instance, verbose: bool = True):
    """
    Run all three algorithms on a single test case.

    Args:
        test_case_name: Name of the test case
        instance: Instance to solve
        verbose: Whether to print progress

    Returns:
        Dictionary with results for each algorithm
    """
    results = {}

    if verbose:
        print(f"\n{'='*70}")
        print(f"Test Case: {test_case_name}")
        print(f"  Sensors: {instance.n}")
        print(f"  Distribution: {get_test_case_config(test_case_name).get('distribution')}")
        print(f"{'='*70}")

    # Algorithm 1: Center-based
    if verbose:
        print("Running Center-based Heuristic...", end=" ", flush=True)
    start = time.time()
    path_c, len_c = center_based_heuristic(instance, closed=CLOSED_TOUR)
    time_c = time.time() - start
    validation_c = validate_path(path_c, instance)
    results["center_based"] = AlgorithmResult(
        algorithm="Center-Based Heuristic",
        instance_name=test_case_name,
        path=path_c,
        length=len_c,
        coverage=validation_c,
        time=time_c,
    )
    if verbose:
        print(f"✓ (time: {time_c:.4f}s, length: {len_c:.2f}, coverage: {validation_c['n_covered']}/{validation_c['n_total']})")

    # Algorithm 2: Boundary sampling
    if verbose:
        print("Running Boundary Sampling...", end=" ", flush=True)
    start = time.time()
    path_b, len_b = boundary_sampling(instance, closed=CLOSED_TOUR)
    time_b = time.time() - start
    validation_b = validate_path(path_b, instance)
    results["boundary_sampling"] = AlgorithmResult(
        algorithm="Boundary Sampling",
        instance_name=test_case_name,
        path=path_b,
        length=len_b,
        coverage=validation_b,
        time=time_b,
    )
    if verbose:
        print(f"✓ (time: {time_b:.4f}s, length: {len_b:.2f}, coverage: {validation_b['n_covered']}/{validation_b['n_total']})")

    # Algorithm 3: Hybrid
    if verbose:
        print("Running Hybrid Algorithm...", end=" ", flush=True)
    start = time.time()
    path_h, len_h = hybrid_algorithm(instance, closed=CLOSED_TOUR)
    time_h = time.time() - start
    validation_h = validate_path(path_h, instance)
    results["hybrid"] = AlgorithmResult(
        algorithm="Hybrid (KMeans + 2-opt)",
        instance_name=test_case_name,
        path=path_h,
        length=len_h,
        coverage=validation_h,
        time=time_h,
    )
    if verbose:
        print(f"✓ (time: {time_h:.4f}s, length: {len_h:.2f}, coverage: {validation_h['n_covered']}/{validation_h['n_total']})")

    return results


def visualize_results(test_case_name: str, instance, results):
    """
    Create visualizations for test case results.

    Args:
        test_case_name: Name of the test case
        instance: Instance that was solved
        results: Results dictionary from run_all_algorithms
    """
    # Individual visualization for each algorithm
    for algo_name, result in results.items():
        clusters = None
        if algo_name == "hybrid":
            clusters = cluster_sensors(instance, method="kmeans")

        save_path = f"{OUTPUT_DIR}/individual/{test_case_name}_{algo_name}.png"
        plot_instance_and_path(
            instance,
            result.path,
            title=f"{test_case_name} - {result.algorithm}",
            clusters=clusters,
            closed=CLOSED_TOUR,
            save_path=save_path,
        )

    # Comparison visualization
    comparison_data = {}
    for algo_name, result in results.items():
        clusters = None
        if algo_name == "hybrid":
            clusters = cluster_sensors(instance, method="kmeans")
        comparison_data[result.algorithm] = (result.path, result.length, clusters)

    comp_path = f"{OUTPUT_DIR}/comparisons/{test_case_name}_comparison.png"
    create_comparison_plot(
        instance,
        comparison_data,
        title=f"Algorithm Comparison - {test_case_name}",
        save_path=comp_path,
    )


def save_results_json(all_results: dict):
    """
    Save results to JSON files.

    Args:
        all_results: Dictionary with all benchmark results
    """
    json_results = {}

    for test_case, results_dict in all_results.items():
        json_results[test_case] = {}
        for algo_name, result in results_dict.items():
            json_results[test_case][algo_name] = {
                "algorithm": result.algorithm,
                "length": result.length,
                "time": result.time,
                "coverage": result.coverage,
                "path_points": len(result.path),
            }

    with open(f"{OUTPUT_DIR}/benchmark_results.json", "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"Saved JSON results: {OUTPUT_DIR}/benchmark_results.json")


def create_benchmark_summary(all_results: dict):
    """
    Create a summary of benchmark results.

    Args:
        all_results: Dictionary with all benchmark results
    """
    print("\n" + "="*100)
    print("BENCHMARK SUMMARY")
    print("="*100)

    # Summary per algorithm
    algo_summary = {}
    for test_case, results_dict in all_results.items():
        for algo_name, result in results_dict.items():
            if algo_name not in algo_summary:
                algo_summary[algo_name] = {
                    "lengths": [],
                    "times": [],
                    "coverage_ratios": [],
                }
            algo_summary[algo_name]["lengths"].append(result.length)
            algo_summary[algo_name]["times"].append(result.time)
            algo_summary[algo_name]["coverage_ratios"].append(
                result.coverage["n_covered"] / result.coverage["n_total"]
            )

    print("\n" + "="*100)
    print("ALGORITHM PERFORMANCE SUMMARY")
    print("="*100)
    print(f"{'Algorithm':<35} {'Avg Length':<15} {'Avg Time':<15} {'Avg Coverage':<15}")
    print("-"*100)

    for algo_name in sorted(algo_summary.keys()):
        stats = algo_summary[algo_name]
        avg_length = sum(stats["lengths"]) / len(stats["lengths"])
        avg_time = sum(stats["times"]) / len(stats["times"])
        avg_coverage = sum(stats["coverage_ratios"]) / len(stats["coverage_ratios"])

        result_obj = list(all_results.values())[0][algo_name]  # Get first instance for naming
        print(f"{result_obj.algorithm:<35} {avg_length:>14.2f} {avg_time:>14.6f}s {avg_coverage:>14.1%}")

    print("-"*100)


def main():
    """Main execution function."""
    print("TSPN Drone Path Planning - Comprehensive Benchmark")
    print("="*100)

    # Ensure output directory exists
    ensure_output_dir()

    # Get all test cases
    test_cases = get_all_test_cases()
    test_case_names = get_test_case_names()

    print(f"\nLoaded {len(test_cases)} test cases")
    print(f"Closed tour mode: {CLOSED_TOUR}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Run benchmark
    all_results = {}

    for i, test_case_name in enumerate(test_case_names, 1):
        print(f"\n[{i}/{len(test_case_names)}] Processing: {test_case_name}")

        instance = test_cases[test_case_name]
        results = run_all_algorithms(test_case_name, instance, verbose=True)
        all_results[test_case_name] = results

        # Visualize
        if VISUALIZE:
            print(f"  Generating visualizations...")
            visualize_results(test_case_name, instance, results)

    # Save results
    if SAVE_JSON:
        save_results_json(all_results)

    # Print summary
    create_benchmark_summary(all_results)

    # Generate benchmark report and graphs
    print("\n" + "="*100)
    print("Generating benchmark report and analysis graphs...")
    print("="*100)
    
    json_results_path = f"{OUTPUT_DIR}/benchmark_results.json"
    try:
        generate_benchmark_graphs(json_results_path, OUTPUT_DIR)
        generate_markdown_report(json_results_path, f"{OUTPUT_DIR}/BENCHMARK_REPORT.md")
        print("\n✅ Benchmark report and graphs generated successfully!")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not generate report and graphs: {e}")
        print("   Report and graphs may be outdated.")

    print("\n" + "="*100)
    print("Benchmark complete!")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*100)


if __name__ == "__main__":
    main()
