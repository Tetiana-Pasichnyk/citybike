from analyzer import BikeShareSystem

system = BikeShareSystem()
system.load_data()
system.clean_data()  # если нужно

system.build_station_distance_matrix()
system.add_trip_distances()
system.flag_duration_outliers()
system.compute_fares()
system.save_trips_with_numerical()

print(system.trips[["trip_id","distance","fare","is_outlier"]].head())
