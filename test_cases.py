"""
Test Cases for TSPN Drone Path Planning
Different scenarios to test algorithms under various conditions.
"""

from core_utils import generate_instance, Instance


# =============================================================================
# TEST CASE CONFIGURATIONS
# =============================================================================

TEST_CASES = {
    # Small instances
    "small_uniform_10": {
        "n_sensors": 10,
        "space_size": 100.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 42,
    },
    "small_clustered_10": {
        "n_sensors": 10,
        "space_size": 100.0,
        "radius_range": (4.0, 10.0),
        "distribution": "clustered",
        "seed": 43,
    },

    # Medium instances
    "medium_uniform_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 44,
    },
    "medium_clustered_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (4.0, 10.0),
        "distribution": "clustered",
        "seed": 45,
    },

    # Large instances
    "large_uniform_50": {
        "n_sensors": 50,
        "space_size": 150.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 46,
    },
    "large_clustered_50": {
        "n_sensors": 50,
        "space_size": 150.0,
        "radius_range": (4.0, 10.0),
        "distribution": "clustered",
        "seed": 47,
    },

    # Very large instances
    "xlarge_uniform_100": {
        "n_sensors": 100,
        "space_size": 200.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 48,
    },
    "xlarge_clustered_100": {
        "n_sensors": 100,
        "space_size": 200.0,
        "radius_range": (4.0, 10.0),
        "distribution": "clustered",
        "seed": 49,
    },

    # Different radius ranges (sparse coverage)
    "sparse_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (2.0, 4.0),
        "distribution": "uniform",
        "seed": 50,
    },

    # Different radius ranges (dense coverage)
    "dense_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (8.0, 15.0),
        "distribution": "uniform",
        "seed": 51,
    },

    # Tightly clustered
    "tight_clusters_30": {
        "n_sensors": 30,
        "space_size": 100.0,
        "radius_range": (3.0, 8.0),
        "distribution": "clustered",
        "seed": 52,
    },

    # Very sparse
    "very_large_space_30": {
        "n_sensors": 30,
        "space_size": 300.0,
        "radius_range": (3.0, 8.0),
        "distribution": "uniform",
        "seed": 53,
    },
    
    # Same radii for all sensors (uniform coverage)
    "uniform_radii_small_10": {
        "n_sensors": 10,
        "space_size": 100.0,
        "radius_range": (6.0, 6.0),  # All sensors have radius = 6.0
        "distribution": "uniform",
        "seed": 54,
    },
    "uniform_radii_small_clustered_10": {
        "n_sensors": 10,
        "space_size": 100.0,
        "radius_range": (6.0, 6.0),  # All sensors have radius = 6.0
        "distribution": "clustered",
        "seed": 55,
    },
    "uniform_radii_medium_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (5.0, 5.0),  # All sensors have radius = 5.0
        "distribution": "uniform",
        "seed": 56,
    },
    "uniform_radii_medium_clustered_20": {
        "n_sensors": 20,
        "space_size": 100.0,
        "radius_range": (5.0, 5.0),  # All sensors have radius = 5.0
        "distribution": "clustered",
        "seed": 57,
    },
    "uniform_radii_large_50": {
        "n_sensors": 50,
        "space_size": 150.0,
        "radius_range": (4.0, 4.0),  # All sensors have radius = 4.0
        "distribution": "uniform",
        "seed": 58,
    },
    "uniform_radii_large_clustered_50": {
        "n_sensors": 50,
        "space_size": 150.0,
        "radius_range": (4.0, 4.0),  # All sensors have radius = 4.0
        "distribution": "clustered",
        "seed": 59,
    },
}


def load_test_case(name: str) -> Instance:
    """
    Load a test case by name and generate the instance.

    Args:
        name: Name of the test case

    Returns:
        Generated Instance
    """
    if name not in TEST_CASES:
        raise ValueError(f"Unknown test case: {name}")

    config = TEST_CASES[name].copy()
    return generate_instance(**config, name=name)


def get_all_test_cases() -> dict:
    """
    Get dictionary of all test case names and their instances.

    Returns:
        Dictionary {name: Instance}
    """
    return {name: load_test_case(name) for name in TEST_CASES.keys()}


def get_test_case_names() -> list:
    """Get list of all test case names."""
    return list(TEST_CASES.keys())


def get_test_case_config(name: str) -> dict:
    """Get configuration of a specific test case."""
    if name not in TEST_CASES:
        raise ValueError(f"Unknown test case: {name}")
    return TEST_CASES[name].copy()


# =============================================================================
# TEST CASE CATEGORIES
# =============================================================================

def get_small_test_cases() -> list:
    """Get test cases with small number of sensors."""
    return [name for name in TEST_CASES.keys() if "small" in name or "sparse" in name or "dense" in name]


def get_medium_test_cases() -> list:
    """Get test cases with medium number of sensors."""
    return [name for name in TEST_CASES.keys() if "medium" in name]


def get_large_test_cases() -> list:
    """Get test cases with large/xlarge instances."""
    return [name for name in TEST_CASES.keys() if "large" in name or "xlarge" in name]


def get_clustered_test_cases() -> list:
    """Get test cases with clustered distribution."""
    return [name for name in TEST_CASES.keys() if "clustered" in name or "tight_clusters" in name]


def get_uniform_test_cases() -> list:
    """Get test cases with uniform distribution."""
    return [name for name in TEST_CASES.keys() if "uniform" in name or "sparse" in name or "dense" in name or "very_large_space" in name]

