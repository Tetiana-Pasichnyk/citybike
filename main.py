from analyzer import BikeShareSystem
from pricing import CasualPricing, MemberPricing, PeakHourPricing


def main(): 
    system = BikeShareSystem()

    # Step 1 — Load data
    print("\n>>> Loading data …")
    system.load_data()

    # Step 2 — Clean
    print("\n>>> Cleaning data …")
    system.clean_data() 

    # Step 3 — Analytics
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



    # Step 4 — Report
    print("\n>>> Generating summary report …")
    system.generate_summary_report()


    print("\n>>> Done! Check output/ for results.")

if __name__ == "__main__":
    main()