from analyzer import BikeShareSystem

system = BikeShareSystem()
system.load_data()
system.clean_data()  
system.build_station_distance_matrix()
system.add_trip_distances()
system.flag_duration_outliers()
system.compute_fares()
system.save_trips_with_numerical()

popular_routes = system.popular_routes(n=10)
print("\n--- Top 10 Popular Routes ---")
print(popular_routes)

maintenance_cost = system.maintenance_cost_by_bike_type()
print("\n--- Maintenance Cost by Bike Type ---")
print(maintenance_cost)

bike_utilization = system.bike_utilization_rate()
print("\n--- Bike Utilization Rate ---")
print(bike_utilization.head(10))

abandoned = system.abandoned_bikes()
print("\n--- Abandoned / Anomalous Bikes ---")
print(abandoned.head(10))

arpu = system.average_revenue_per_user()
print(f"\n--- Average Revenue per User (ARPU) ---\n${arpu}")

print(system.trips[["trip_id","distance","fare","is_outlier"]].head())
system.generate_summary_report() 

print("\n[FINISH] Script executed successfully.")