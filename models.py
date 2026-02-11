from abc import ABC, abstractmethod
from datetime import datetime
from utils import validate_email, validate_positive


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class Entity(ABC):
    def __init__(self, entity_id: str, created_at: datetime = None):
        if not entity_id:
            raise ValueError("ID cannot be empty")
        self.id = entity_id
        self.created_at = created_at or datetime.now()

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


# ---------------------------------------------------------------------------
# Bike hierarchy
# ---------------------------------------------------------------------------

class Bike(Entity):
    VALID_STATUSES = {"available", "in_use", "maintenance"}

    def __init__(self, bike_id: str, bike_type: str, status: str = "available"):
        super().__init__(bike_id)

        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid bike status")

        self.bike_type = bike_type
        self.status = status

    def __repr__(self):
        return f"Bike(id='{self.id}', type='{self.bike_type}', status='{self.status}')"


class ClassicBike(Bike):
    def __init__(self, bike_id: str, gear_count: int = 1, status: str = "available"):
        super().__init__(bike_id, "classic", status)

        if gear_count <= 0:
            raise ValueError("gear_count must be positive")

        self.gear_count = gear_count

    def __str__(self):
        return f"Classic Bike {self.id} ({self.gear_count} gears)"


class ElectricBike(Bike):
    def __init__(
        self,
        bike_id: str,
        battery_level: float = 100.0,
        max_range_km: float = 50.0,
        status: str = "available",
    ):
        super().__init__(bike_id, "electric", status)

        if not 0 <= battery_level <= 100:
            raise ValueError("battery_level must be between 0 and 100")
        if max_range_km <= 0:
            raise ValueError("max_range_km must be positive")

        self.battery_level = validate_positive(battery_level, "Battery level")
        self.max_range_km = validate_positive(max_range_km, "Max range")

    def __str__(self):
        return f"Electric Bike {self.id} (Battery: {self.battery_level}%)"


# ---------------------------------------------------------------------------
# User hierarchy
# ---------------------------------------------------------------------------

class User(Entity):
    def __init__(self, user_id: str, name: str, email: str, user_type: str):
        super().__init__(user_id)

        if "@" not in email:
            raise ValueError("Invalid email format")

        self.name = name
        self.email = validate_email(email)
        self.user_type = user_type

    def __str__(self):
        return f"User: {self.name} ({self.email})"

    def __repr__(self):
        return f"User(id='{self.id}', type='{self.user_type}')"


class CasualUser(User):
    def __init__(self, user_id: str, name: str, email: str, day_pass_count: int = 0):
        if day_pass_count < 0:
            raise ValueError("day_pass_count cannot be negative")
        super().__init__(user_id, name, email, "casual")
        self.day_pass_count = day_pass_count

    def __str__(self):
        return f"Casual User: {self.name}"


class MemberUser(User):
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        membership_start: datetime = None,
        membership_end: datetime = None,
        tier: str = "basic",
    ):
        if tier not in {"basic", "premium"}:
            raise ValueError("Invalid tier")

        if membership_start and membership_end and membership_end < membership_start:
            raise ValueError("membership_end must be after membership_start")

        super().__init__(user_id, name, email, "member")

        self.membership_start = membership_start
        self.membership_end = membership_end
        self.tier = tier

    def __str__(self):
        return f"Member User ({self.tier}): {self.name}"


# ---------------------------------------------------------------------------
# Station
# ---------------------------------------------------------------------------

class Station(Entity):
    def __init__(
        self,
        station_id: str,
        name: str,
        capacity: int,
        latitude: float,
        longitude: float,
    ):
        super().__init__(station_id)

        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if not -90 <= latitude <= 90:
            raise ValueError("Invalid latitude")
        if not -180 <= longitude <= 180:
            raise ValueError("Invalid longitude")

        self.name = name
        self.capacity = validate_positive(capacity, "Station capacity")
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return f"Station {self.name} (Capacity: {self.capacity})"

    def __repr__(self):
        return f"Station(id='{self.id}', name='{self.name}')"


# ---------------------------------------------------------------------------
# Trip
# ---------------------------------------------------------------------------

class Trip:
    def __init__(
        self,
        trip_id: str,
        user: User,
        bike: Bike,
        start_station: Station,
        end_station: Station,
        start_time: datetime,
        end_time: datetime,
        distance_km: float,
    ):
        if end_time < start_time:
            raise ValueError("End time before start time")
        if distance_km < 0:
            raise ValueError("distance_km cannot be negative")

        self.trip_id = trip_id
        self.user = user
        self.bike = bike
        self.start_station = start_station
        self.end_station = end_station
        self.start_time = start_time
        self.end_time = end_time
        self.distance_km = distance_km

    @property
    def duration_minutes(self):
        return (self.end_time - self.start_time).total_seconds() / 60

    def __str__(self):
        return f"Trip {self.trip_id}: {self.user.name} ({self.distance_km} km)"

    def __repr__(self):
        return f"Trip(trip_id='{self.trip_id}')"


# ---------------------------------------------------------------------------
# MaintenanceRecord
# ---------------------------------------------------------------------------

class MaintenanceRecord(Entity):
    VALID_TYPES = {
        "tire_repair",
        "brake_adjustment",
        "battery_replacement",
        "chain_lubrication",
        "general_inspection",
    }

    def __init__(
        self,
        record_id: str,
        bike: Bike,
        date: datetime,
        maintenance_type: str,
        cost: float,
        description: str,
    ):
        super().__init__(record_id)

        if maintenance_type not in self.VALID_TYPES:
            raise ValueError("Invalid maintenance type")
        if cost < 0:
            raise ValueError("Maintenance cost cannot be negative")

        self.bike = bike
        self.date = date
        self.maintenance_type = maintenance_type
        self.cost = validate_positive(cost, "Maintenance cost") 
        self.description = description

    def __str__(self):
        return f"Maintenance on {self.bike.id}: {self.maintenance_type} (${self.cost})"

    def __repr__(self):
        return f"MaintenanceRecord(id='{self.id}', bike_id='{self.bike.id}')"
