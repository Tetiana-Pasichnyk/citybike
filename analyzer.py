import pandas as pd
import numpy as np
from pathlib import Path
from utils import (
    VALID_USER_TYPES, VALID_BIKE_TYPES, VALID_MAINTENANCE_TYPES,
    validate_in
)
from numerical import (
    station_distance_matrix, trip_duration_stats, detect_outliers_zscore,
    calculate_fares
)


DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

class BikeShareSystem:
    def __init__(self) -> None:
        self.trips: pd.DataFrame | None = None
        self.stations: pd.DataFrame | None = None
        self.maintenance: pd.DataFrame | None = None
        self.stations_ids: np.ndarray | None = None
        self.stations_distances: np.ndarray | None = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_data(self) -> None:
        self.trips = pd.read_csv(DATA_DIR / "trips.csv")
        self.stations = pd.read_csv(DATA_DIR / "stations.csv")
        self.maintenance = pd.read_csv(DATA_DIR / "maintenance.csv")

    # ------------------------------------------------------------------
    # Data cleaning
    # ------------------------------------------------------------------

    def clean_data(self) -> None:
        if self.trips is None or self.stations is None or self.maintenance is None:
            raise RuntimeError("Call load_data() first")

        # ---- Remove duplicates ----
        self.trips = self.trips.drop_duplicates(subset=["trip_id"])
        self.stations = self.stations.drop_duplicates(subset=["station_id"])
        self.maintenance = self.maintenance.drop_duplicates(subset=["record_id"])

        # ---- Parse datetime columns ----
        self.trips["start_time"] = pd.to_datetime(self.trips["start_time"], errors="coerce")
        self.trips["end_time"] = pd.to_datetime(self.trips["end_time"], errors="coerce")
        self.maintenance["maintenance_date"] = pd.to_datetime(self.maintenance["date"], errors="coerce")

        # ---- Convert numeric columns ----
        self.trips["distance_km"] = pd.to_numeric(self.trips["distance_km"], errors="coerce")
        self.trips["duration_minutes"] = pd.to_numeric(self.trips["duration_minutes"], errors="coerce")
        self.stations["capacity"] = pd.to_numeric(self.stations["capacity"], errors="coerce")
        self.maintenance["cost"] = pd.to_numeric(self.maintenance["cost"], errors="coerce")

        # ---- Handle missing values ----
        self.trips = self.trips.dropna(subset=["trip_id", "start_time", "end_time"])
        self.trips["distance_km"] = self.trips["distance_km"].fillna(self.trips["distance_km"].median())
        self.trips["duration_minutes"] = self.trips["duration_minutes"].fillna(self.trips["duration_minutes"].median())

        # ---- Remove invalid trips ----
        self.trips = self.trips[self.trips["end_time"] >= self.trips["start_time"]]

        # ---- Standardize categoricals ----
        self.trips["user_type"] = self.trips["user_type"].str.lower().str.strip()
        self.trips["status"] = self.trips["status"].str.lower().str.strip()
        self.maintenance["maintenance_type"] = self.maintenance["maintenance_type"].str.lower().str.strip()

        # Validate values
        self.trips = self.trips[self.trips["bike_type"].isin(VALID_BIKE_TYPES)]
        self.trips = self.trips[self.trips["user_type"].isin(VALID_USER_TYPES)]
        self.maintenance = self.maintenance[self.maintenance["maintenance_type"].isin(VALID_MAINTENANCE_TYPES)]

        # ---- Export cleaned data ----
        DATA_DIR.mkdir(exist_ok=True)
        self.trips.to_csv(DATA_DIR / "trips_clean.csv", index=False)
        self.stations.to_csv(DATA_DIR / "stations_clean.csv", index=False)
        self.maintenance.to_csv(DATA_DIR / "maintenance_clean.csv", index=False)

        print("Data cleaning complete.")

    # ------------------------------------------------------------------
    # NumPy-based calculations 
    # ------------------------------------------------------------------
    def build_station_distance_matrix(self):
        """Compute pairwise distances between stations."""
        lats = self.stations["latitude"].to_numpy()
        lons = self.stations["longitude"].to_numpy()
        self.station_ids = self.stations["station_id"].to_numpy()
        self.station_distances = station_distance_matrix(lats, lons)

    def add_trip_distances(self):
        """Assign distance to each trip using station distance matrix."""
        id_to_idx = {sid: i for i, sid in enumerate(self.station_ids)}
        start_idx = self.trips["start_station_id"].map(id_to_idx).to_numpy()
        end_idx = self.trips["end_station_id"].map(id_to_idx).to_numpy()
        self.trips["distance"] = self.station_distances[start_idx, end_idx]

    def flag_duration_outliers(self, threshold=3.0):
        """Mark trips with z-score outliers."""
        self.trips["is_outlier"] = detect_outliers_zscore(
            self.trips["duration_minutes"].to_numpy(), threshold
        )

    def compute_fares(self, per_min=0.15, per_km=0.10, unlock_fee=1.0):
        """Compute fares for all trips."""
        self.trips["fare"] = calculate_fares(
            self.trips["duration_minutes"].to_numpy(),
            self.trips["distance"].to_numpy(),
            per_minute=per_min,
            per_km=per_km,
            unlock_fee=unlock_fee
        )

    def save_trips_with_numerical(self, path=DATA_DIR / "trips_clean.csv"):
        """Save trips with added numerical columns to CSV."""
        self.trips.to_csv(path, index=False)
        print(f"[OK] Saved {path}")


    def popular_routes(self, n: int = 10) -> pd.DataFrame:
        """Compute top-N popular routes with station names."""
        # Group by start and end station IDs and count trips
        df = self.trips.groupby(['start_station_id', 'end_station_id']).size().reset_index(name='trip_count')

        # Merge start station names
        df = df.merge(
            self.stations[['station_id', 'station_name']],
            left_on='start_station_id', right_on='station_id', how='left'
        ).rename(columns={'station_name': 'start_station_name'}).drop('station_id', axis=1)

        # Merge end station names
        df = df.merge(
            self.stations[['station_id', 'station_name']],
            left_on='end_station_id', right_on='station_id', how='left'
        ).rename(columns={'station_name': 'end_station_name'}).drop('station_id', axis=1)

        # Sort by trip count descending
        df = df.sort_values('trip_count', ascending=False)

        return df.head(n)


    def maintenance_cost_by_bike_type(self) -> pd.DataFrame:
        """Compute total and average maintenance cost per bike type."""
        # Group maintenance records by bike type and calculate sum and mean
        df = self.maintenance.groupby('bike_type')['cost'].agg(['sum', 'mean']).reset_index()

        # Sort by total cost descending
        df = df.sort_values('sum', ascending=False)

        return df


    def bike_utilization_rate(self) -> pd.DataFrame:
        """Compute number of trips per bike, including bike type."""
        # Count trips per bike
        trips_per_bike = self.trips.groupby('bike_id').size().reset_index(name='num_trips')

        # Merge bike type (avoid duplicates if bike_id is unique)
        trips_per_bike = trips_per_bike.merge(
            self.trips[['bike_id', 'bike_type']].drop_duplicates(),
            on='bike_id'
        )

        # Sort by number of trips descending
        return trips_per_bike.sort_values('num_trips', ascending=False)


    def abandoned_bikes(self) -> pd.DataFrame:
        """Identify bikes with anomalous trips (outliers)."""
        # Filter trips flagged as outliers
        outliers = self.trips[self.trips['is_outlier']]

        # Count number of outlier trips per bike
        df = outliers.groupby('bike_id').size().reset_index(name='num_outliers')

        # Sort descending by number of outliers
        return df.sort_values('num_outliers', ascending=False)


    def average_revenue_per_user(self) -> float:
        """Compute average revenue per user (ARPU)."""
        # Sum fares per user
        user_revenue = self.trips.groupby('user_id')['fare'].sum()

        # Compute mean and round to 2 decimals
        return round(user_revenue.mean(), 2)

    # ------------------------------------------------------------------
    #     Analytics und Summary Reports
    # ------------------------------------------------------------------
    def total_trips_summary(self) -> dict:
        df = self.trips
        return {
            "total_trips": len(df),
            "total_distance_km": round(df["distance_km"].sum(), 2),
            "avg_duration_min": round(df["duration_minutes"].mean(), 2),
        }

    def top_start_stations(self, n: int = 10) -> pd.DataFrame:
        counts = self.trips["start_station_id"].value_counts().head(n).reset_index()
        counts.columns = ["station_id", "trip_count"]
        counts = counts.merge(
            self.stations[["station_id", "station_name"]], 
            on="station_id", 
            how="left"
        )
        return counts[["station_name", "trip_count"]]


    def peak_usage_hours(self) -> pd.Series:
        return self.trips["start_time"].dt.hour.value_counts().sort_index()

    def busiest_day_of_week(self) -> pd.Series:
        return self.trips["start_time"].dt.day_name().value_counts()

    def avg_distance_by_user_type(self) -> pd.Series:
        return self.trips.groupby("user_type")["distance_km"].mean()

    def generate_summary_report(self) -> None:
        """Collects results from all analytics methods and saves them to a text file."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_DIR / "summary_report.txt"

        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("   CityBike — Summary Business Report")
        lines.append("=" * 60)

        # [1] Overall summary
        summary = self.total_trips_summary()
        lines.append(f"\n[1] OVERALL SUMMARY\n    Total trips: {summary['total_trips']} | Distance: {summary['total_distance_km']} km")

        # [2] Top start stations
        lines.append("\n[2] TOP 10 START STATIONS")
        lines.append(self.top_start_stations().to_string(index=False))

        # [3] Peak usage hours
        lines.append("\n[3] PEAK USAGE HOURS")
        lines.append(self.peak_usage_hours().to_string())

        # [4] Busiest day of week
        lines.append("\n[4] BUSIEST DAY OF WEEK")
        lines.append(self.busiest_day_of_week().to_string())

        # [5] Avg distance by user type
        lines.append("\n[5] AVG DISTANCE BY USER TYPE")
        lines.append(self.avg_distance_by_user_type().to_string())

        # [6] Top Popular Routes
        routes = self.popular_routes(5)
        lines.append("\n[6] TOP 5 ROUTES (Start -> End)")
        lines.append(routes[['start_station_name', 'end_station_name', 'trip_count']].to_string(index=False))

        # [7] Maintenance costs
        maint = self.maintenance_cost_by_bike_type()
        lines.append("\n[7] MAINTENANCE COSTS BY TYPE")
        lines.append(maint.to_string(index=False))

        # [8] Bike utilization
        util = self.bike_utilization_rate().head(10)
        lines.append("\n[8] TOP 10 UTILIZED BIKES")
        lines.append(util.to_string(index=False))

        # [9] Anomalies
        abnormal = self.abandoned_bikes().head(5)
        lines.append("\n[9] TOP ANOMALOUS BIKES")
        lines.append(abnormal.to_string(index=False) if not abnormal.empty else "No anomalies detected")

        # [10] Financial Performance
        arpu = self.average_revenue_per_user()
        lines.append(f"\n[10] FINANCIAL PERFORMANCE\n    ARPU: ${arpu}")

        # Финальная запись
        report_text = "\n".join(lines) + "\n"
        report_path.write_text(report_text)
        
        print(f"\n[OK] Full 10-point analytics report created at: {report_path}")