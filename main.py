from analyzer import BikeShareSystem
import visualization
from algorithms import benchmark_sort, benchmark_search

def main(): 
    system = BikeShareSystem()

    # Step 1 — Load data
    print("\n>>> Loading data …")
    system.load_data()

    # Step 2 — Clean
    print("\n>>> Cleaning data …")
    system.clean_data() 

    # Step 3 — Algorithms
    print("\n>>> Running algorithm benchmarks (Unit 9) …")
    
    sample_ids = system.trips["trip_id"].head(500).tolist()
    target_id = sample_ids[len(sample_ids) // 2]  # Pick an ID from the middle
    # Benchmark Sorting
    print(f"  Benchmarking Sort on {len(sample_ids)} items:")
    sort_results = benchmark_sort(sample_ids)
    print(f"    Merge Sort:    {sort_results['merge_sort_ms']} ms")
    print(f"    Insertion Sort:{sort_results['insertion_sort_ms']} ms")
    print(f"    Built-in Sort: {sort_results['builtin_sorted_ms']} ms")

    # Benchmark Searching (on sorted data)
    sorted_sample = sorted(sample_ids)
    print(f"  Benchmarking Search for target '{target_id}':")
    search_results = benchmark_search(sorted_sample, target_id)
    print(f"    Binary Search: {search_results['binary_search_ms']} ms")
    print(f"    Linear Search: {search_results['linear_search_ms']} ms")
    print(f"    Built-in 'in': {search_results['builtin_in_ms']} ms")
    
    # Step 4 — Analytics
    print("\n>>> Running analytics …")
    summary = system.total_trips_summary()
    print(f"  Total trips      : {summary['total_trips']}")
    print(f"  Total distance   : {summary['total_distance_km']} km")
    print(f"  Avg duration     : {summary['avg_duration_min']} min")

    print("\n>>> Building distance matrix …")
    system.build_station_distance_matrix()
    system.add_trip_distances()
    system.flag_duration_outliers()

    print("\n>>> Computing fares …")
    system.compute_fares() 
    system.save_trips_with_numerical()

    print("\n--- First 10 trips with fares ---")
    print(system.trips[["trip_id","user_type","start_time","distance","duration_minutes","fare"]].head(10))

    print("\n--- ARPU ---")
    print(system.average_revenue_per_user())

    # Step 5 — Visualizations
    print("\n>>> Generating visualizations (Milestone 7) …")
    visualization.generate_all_plots(system)

    # Step 6 — Report
    print("\n>>> Exporting top stations and top users CSV …")
    system.export_top_csvs()

    print("\n>>> Generating summary report …")
    system.generate_summary_report()


    print("\n>>> Done! Check output/ for results.")

if __name__ == "__main__":
    main()