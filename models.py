from abc import ABC, abstractmethod
from datetime import datetime

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

class Bike(Entity):
    def __init__(self, bike_id: str, bike_type: str, status: str = "available"):
        super().__init__(bike_id)
        self.bike_type = bike_type
        self.status = status

    def __repr__(self):
        return f"Bike(id='{self.id}', type='{self.bike_type}', status='{self.status}')"

class ClassicBike(Bike):
    def __init__(self, bike_id: str, gear_count: int = 1):
        super().__init__(bike_id, "classic")
        self.gear_count = gear_count

    def __str__(self):
        return f"Classic Bike {self.id} ({self.gear_count} gears)"

class ElectricBike(Bike):
    def __init__(self, bike_id: str, battery_level: float = 100.0, max_range_km: float = 50.0):
        super().__init__(bike_id, "electric")
        self.battery_level = battery_level
        self.max_range_km = max_range_km

    def __str__(self):
        return f"Electric Bike {self.id} (Battery: {self.battery_level}%)"

class User(Entity):
    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id)
        self.name = name
        if "@" not in email:
            raise ValueError("Invalid email format")
        self.email = email

    def __str__(self):
        return f"User: {self.name} ({self.email})"

    def __repr__(self):
        return f"User(id='{self.id}', name='{self.name}')"

class CasualUser(User):
    def __init__(self, user_id: str, name: str, email: str, day_pass_count: int = 0):
        super().__init__(user_id, name, email)
        self.day_pass_count = day_pass_count

    def __str__(self):
        return f"Casual User: {self.name}"

class MemberUser(User):
    def __init__(self, user_id: str, name: str, email: str, tier: str = "basic"):
        super().__init__(user_id, name, email)
        self.tier = tier

    def __str__(self):
        return f"Member User ({self.tier}): {self.name}"

class Station(Entity):
    def __init__(self, station_id: str, name: str, capacity: int, latitude: float, longitude: float):
        super().__init__(station_id)
        self.name = name
        if capacity < 0:
            raise ValueError("Capacity cannot be negative")
        self.capacity = capacity
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return f"Station {self.name} (Capacity: {self.capacity})"

    def __repr__(self):
        return f"Station(id='{self.id}', name='{self.name}')"

class Trip:
    def __init__(self, trip_id: str, user: User, bike: Bike, 
                 start_station: Station, end_station: Station, 
                 start_time: datetime, end_time: datetime, distance_km: float):
        self.trip_id = trip_id
        self.user = user
        self.bike = bike
        self.start_station = start_station
        self.end_station = end_station
        self.start_time = start_time
        self.end_time = end_time
        self.distance_km = distance_km

    def __str__(self):
        return f"Trip {self.trip_id}: {self.user.name} ({self.distance_km} km)"

class MaintenanceRecord(Entity):
    def __init__(self, record_id: str, bike: Bike, date: datetime, 
                 maintenance_type: str, cost: float, description: str):
        super().__init__(record_id)
        self.bike = bike
        self.date = date
        self.maintenance_type = maintenance_type
        if cost < 0:
            raise ValueError("Maintenance cost cannot be negative")
        self.cost = cost
        self.description = description

    def __str__(self):
        return f"Maintenance on {self.bike.id}: {self.maintenance_type} (${self.cost})"

    def __repr__(self):
        return f"MaintenanceRecord(id='{self.id}', bike_id='{self.bike.id}')"
    
