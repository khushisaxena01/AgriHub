# GIS service test (farm registered, farm info, search nearby resource, description of those nearby centers, calculate distance 
# - for 10km and 25km radius & coverage statistics)

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import geopy.distance
from geopy.geocoders import Nominatim
import folium
import json

@dataclass
class Location:
    latitude: float
    longitude: float
    name: str = ""
    address: str = ""
    type: str = ""  # farm, support_center, distribution_center, etc.
    
@dataclass
class Farm:
    location: Location
    area: float  # in hectares
    farmer_id: str
    crop_types: List[str]
    soil_type: str
    registration_date: datetime

@dataclass
class ResourceCenter:
    location: Location
    center_id: str
    services: List[str]
    operating_hours: str
    contact_info: str
    inventory: Dict[str, int]  # resource_name: quantity

class GISService:
    def __init__(self):
        self.farms: Dict[str, Farm] = {}
        self.resource_centers: Dict[str, ResourceCenter] = {}
        self.geocoder = Nominatim(user_agent="agricultural_management_system")
        
    def register_farm(self, farm: Farm) -> str:
        """Register a new farm in the system"""
        self.farms[farm.farmer_id] = farm
        print(f"Farm registered successfully! Farmer ID: {farm.farmer_id}")
        return farm.farmer_id
    
    def register_resource_center(self, center: ResourceCenter) -> str:
        """Register a new resource center"""
        self.resource_centers[center.center_id] = center
        print(f"Resource center registered successfully! Center ID: {center.center_id}")
        return center.center_id
    
    def geocode_address(self, address: str) -> Optional[Location]:
        """Convert address to coordinates"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                return Location(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    address=address
                )
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def calculate_distance(self, point1: Location, point2: Location) -> float:
        """Calculate distance between two points in kilometers"""
        distance = geopy.distance.geodesic(
            (point1.latitude, point1.longitude),
            (point2.latitude, point2.longitude)
        ).kilometers
        print(f"Distance calculated: {distance:.2f} km")
        return distance
    
    def find_nearest_centers(self, 
                           farmer_location: Location, 
                           radius: float,
                           service_type: Optional[str] = None) -> List[ResourceCenter]:
        """Find resource centers within specified radius"""
        nearby_centers = []
        
        for center in self.resource_centers.values():
            distance = self.calculate_distance(farmer_location, center.location)
            if distance <= radius:
                if service_type is None or service_type in center.services:
                    nearby_centers.append((distance, center))
        
        # Sort by distance
        nearby_centers.sort(key=lambda x: x[0])
        centers = [center for _, center in nearby_centers]
        
        print(f"\nFound {len(centers)} centers within {radius} km radius:")
        for i, center in enumerate(centers, 1):
            print(f"{i}. Center ID: {center.center_id}")
            print(f"   Services: {', '.join(center.services)}")
            print(f"   Operating Hours: {center.operating_hours}")
            print(f"   Contact: {center.contact_info}\n")
            
        return centers

    def display_farm_info(self, farmer_id: str):
        """Display detailed information about a farm"""
        farm = self.farms.get(farmer_id)
        if farm:
            print("\nFarm Information:")
            print(f"Farmer ID: {farm.farmer_id}")
            print(f"Location: {farm.location.latitude}, {farm.location.longitude}")
            print(f"Area: {farm.area} hectares")
            print(f"Crops: {', '.join(farm.crop_types)}")
            print(f"Soil Type: {farm.soil_type}")
            print(f"Registration Date: {farm.registration_date}")
        else:
            print(f"Farm not found with ID: {farmer_id}")

    def calculate_coverage_statistics(self) -> Dict:
        """Calculate coverage statistics for resource centers"""
        total_farms = len(self.farms)
        farms_within_10km = 0
        farms_within_25km = 0
        
        for farm in self.farms.values():
            nearest_centers = self.find_nearest_centers(farm.location, radius=25, service_type=None)
            if nearest_centers:
                distance_to_nearest = self.calculate_distance(
                    farm.location, 
                    nearest_centers[0].location
                )
                if distance_to_nearest <= 10:
                    farms_within_10km += 1
                if distance_to_nearest <= 25:
                    farms_within_25km += 1
                    
        return {
            "total_farms": total_farms,
            "farms_within_10km": farms_within_10km,
            "farms_within_25km": farms_within_25km,
            "coverage_10km_percent": (farms_within_10km / total_farms * 100) if total_farms > 0 else 0,
            "coverage_25km_percent": (farms_within_25km / total_farms * 100) if total_farms > 0 else 0,
            "total_resource_centers": len(self.resource_centers)
        }

# Test code
def run_test():
    print("Starting GIS Service Test...\n")
    
    # Initialize the service
    gis_service = GISService()
    
    # Register a farm
    farm = Farm(
        location=Location(latitude=12.9716, longitude=77.5946),
        area=5.5,
        farmer_id="F001",
        crop_types=["rice", "wheat"],
        soil_type="clay loam",
        registration_date=datetime.now()
    )
    gis_service.register_farm(farm)
    
    # Register resource centers
    center1 = ResourceCenter(
        location=Location(latitude=12.9816, longitude=77.5846),
        center_id="RC001",
        services=["soil_testing", "equipment_rental"],
        operating_hours="9AM-5PM",
        contact_info="123-456-7890",
        inventory={"soil_testing_kits": 50, "tractors": 5}
    )
    
    center2 = ResourceCenter(
        location=Location(latitude=12.9916, longitude=77.5746),
        center_id="RC002",
        services=["seed_distribution", "soil_testing"],
        operating_hours="8AM-6PM",
        contact_info="987-654-3210",
        inventory={"seeds": 1000, "soil_testing_kits": 30}
    )
    
    gis_service.register_resource_center(center1)
    gis_service.register_resource_center(center2)
    
    # Display farm information
    gis_service.display_farm_info("F001")
    
    # Find nearby centers
    print("\nSearching for nearby resource centers...")
    nearby_centers = gis_service.find_nearest_centers(farm.location, radius=10)
    
    # Calculate coverage statistics
    stats = gis_service.calculate_coverage_statistics()
    print("\nCoverage Statistics:")
    for key, value in stats.items():
        if "percent" in key:
            print(f"{key}: {value:.1f}%")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    run_test()