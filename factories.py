from models import Bike, ClassicBike, ElectricBike, User, CasualUser, MemberUser

class BikeFactory:
   
    @staticmethod
    def create_bike(data: dict) -> Bike:

        bike_type = data.get('bike_type', '').lower().strip()
        bike_id = data.get('bike_id')

        if not bike_id:
            raise ValueError("Bike ID is required")

        if bike_type == 'classic':
          
            gear_count = int(data.get('gear_count', 1))
            return ClassicBike(bike_id, gear_count=gear_count)
            
        elif bike_type == 'electric':
            
            battery = float(data.get('battery_level', 100.0))
            range_km = float(data.get('max_range_km', 50.0))
            return ElectricBike(bike_id, battery_level=battery, max_range_km=range_km)
            
        else:
            raise ValueError(f"Unknown bike type: {bike_type}")

class UserFactory:
   
    @staticmethod
    def create_user(data: dict) -> User:
      
        user_type = data.get('user_type', '').lower().strip()
        user_id = data.get('user_id')
        name = data.get('name', 'Unknown')
        email = data.get('email', 'unknown@example.com')

        if not user_id:
            raise ValueError("User ID is required")

        if user_type == 'casual':
            day_pass = int(data.get('day_pass_count', 0))
            return CasualUser(user_id, name, email, day_pass_count=day_pass)
            
        elif user_type == 'member':
            tier = data.get('tier', 'basic')
            return MemberUser(user_id, name, email, tier=tier)
            
        else:
            raise ValueError(f"Unknown user type: {user_type}")