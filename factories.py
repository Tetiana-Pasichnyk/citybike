from datetime import datetime
from models import (
    Bike, ClassicBike, ElectricBike, 
    User, CasualUser, MemberUser, 
    Station, Trip, MaintenanceRecord
)

def create_bike(data: dict) -> Bike:
    bike_type = data.get("bike_type", "").lower().strip()
    bike_id = data.get("bike_id")

    if not bike_id:
        raise ValueError("Bike ID is required")

    if bike_type == "classic":
        return ClassicBike(
            bike_id=bike_id, 
            gear_count=int(data.get("gear_count", 7))
        )
    elif bike_type == "electric":
        return ElectricBike(
            bike_id=bike_id,
            battery_level=float(data.get("battery_level", 100.0)),
            max_range_km=float(data.get("max_range_km", 50.0))
        )
    else:
        raise ValueError(f"Unknown bike_type: {bike_type!r}")

def create_user(data: dict) -> User:
    user_type = data.get("user_type", "").lower().strip()
    user_id = data.get("user_id")
    name = data.get("name", "Unknown")
    email = data.get("email", "unknown@example.com")

    if not user_id:
        raise ValueError("User ID is required")

    if user_type == "casual":
        return CasualUser(
            user_id=user_id, 
            name=name, 
            email=email, 
            day_pass_count=int(data.get("day_pass_count", 0))
        )
    elif user_type == "member":
        return MemberUser(
            user_id=user_id, 
            name=name, 
            email=email, 
            tier=data.get("tier", "basic")
        )
    else:
        raise ValueError(f"Unknown user_type: {user_type!r}")

def create_station(data: dict) -> Station:
    return Station(
        station_id=data["station_id"],
        name=data["station_name"],
        capacity=int(data["capacity"]),
        latitude=float(data["lat"]),
        longitude=float(data["lon"])
    )

def create_trip(data: dict, user: User, bike: Bike, 
                start_station: Station, end_station: Station) -> Trip:
    fmt = "%Y-%m-%d %H:%M:%S"
    return Trip(
        trip_id=data["trip_id"],
        user=user,
        bike=bike,
        start_station=start_station,
        end_station=end_station,
        start_time=datetime.strptime(data["start_time"], fmt),
        end_time=datetime.strptime(data["end_time"], fmt),
        distance_km=float(data["distance_km"])
    )

def create_maintenance_record(data: dict, bike: Bike) -> MaintenanceRecord:
    return MaintenanceRecord(
        record_id=data["record_id"],
        bike=bike,
        date=datetime.strptime(data["maintenance_date"], "%Y-%m-%d"),
        maintenance_type=data["maintenance_type"],
        cost=float(data["cost"]),
        description=data["description"]
    )