import pandas as pd
import numpy as np
from pathlib import Path
from utils import (
    VALID_USER_TYPES, VALID_BIKE_TYPES, VALID_MAINTENANCE_TYPES,
    validate_in
)
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

class BikeShareSystem:
    def __init__(self) -> None:
        self.trips: pd.DataFrame | None = None
        self.stations: pd.DataFrame | None = None
        self.maintenance: pd.DataFrame | None = None

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
        self.maintenance["maintenance_date"] = pd.to_datetime(self.maintenance["maintenance_date"], errors="coerce")

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
    #     Analytics examples 
    # ------------------------------------------------------------------
    def total_trips_summary(self) -> dict:
        df = self.trips
        return {
            "total_trips": len(df),
            "total_distance_km": round(df["distance_km"].sum(), 2),
            "avg_duration_min": round(df["duration_minutes"].mean(), 2),
        }

    def top_start_stations(self, n: int = 10) -> pd.DataFrame:
        counts = self.trips["start_station_id"].value_counts().head(n)
        return counts.reset_index().rename(columns={"index": "station_id", "start_station_id": "trip_count"})

    def peak_usage_hours(self) -> pd.Series:
        return self.trips["start_time"].dt.hour.value_counts().sort_index()

    def busiest_day_of_week(self) -> pd.Series:
        return self.trips["start_time"].dt.day_name().value_counts()

    def avg_distance_by_user_type(self) -> pd.Series:
        return self.trips.groupby("user_type")["distance_km"].mean()
