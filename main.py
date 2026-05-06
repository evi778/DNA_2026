# --- Generate a small test instance ---
from tspn_drone import *

inst = generate_instance(
    n_sensors=20,
    space_size=100.0,
    radius_range=(4.0, 10.0),
    distribution="clustered",
    seed=7,
)
print(f"Generated instance with {inst.n} sensors.\n")

# --- Run all algorithms ---
path_c, len_c = center_based_heuristic(inst)
path_b, len_b = boundary_sampling(inst)
path_h, len_h = hybrid_algorithm(inst, cluster_method="kmeans", n_clusters=4, use_2opt=True)

print(f"Center-based heuristic : length = {len_c:.2f}")
print(f"Boundary sampling      : length = {len_b:.2f}")
print(f"Hybrid (kmeans + 2-opt): length = {len_h:.2f}\n")

# --- Validate coverage ---
v = validate_path(path_h, inst)
print(f"Hybrid coverage: {v['n_covered']}/{v['n_total']} sensors covered.")
if not v["all_covered"]:
    uncovered = [sid for sid, ok in v["per_sensor"].items() if not ok]
    print(f"  Uncovered sensor IDs: {uncovered}")

# --- Visualize ---
clusters = cluster_sensors(inst, method="kmeans", n_clusters=4)
plot_instance_and_path(inst, path_h, title="Hybrid Algorithm", clusters=clusters)

# --- Benchmark across sizes ---
print("\n=== Benchmark ===")
run_benchmark(n_sensors_list=[10, 20, 50])