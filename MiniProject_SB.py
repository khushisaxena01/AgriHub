# Mini Project - SB

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
        return farm.farmer_id
    
    def register_resource_center(self, center: ResourceCenter) -> str:
        """Register a new resource center"""
        self.resource_centers[center.center_id] = center
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
        return geopy.distance.geodesic(
            (point1.latitude, point1.longitude),
            (point2.latitude, point2.longitude)
        ).kilometers
    
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
        return [center for _, center in nearby_centers]
    
    def generate_farm_map(self, farmer_id: str, include_centers: bool = True) -> str:
        """Generate an interactive map for a specific farm"""
        farm = self.farms.get(farmer_id)
        if not farm:
            raise ValueError(f"Farm not found for farmer ID: {farmer_id}")
            
        # Create map centered on farm
        m = folium.Map(
            location=[farm.location.latitude, farm.location.longitude],
            zoom_start=12
        )
        
        # Add farm marker
        folium.Marker(
            [farm.location.latitude, farm.location.longitude],
            popup=f"Farm ID: {farmer_id}\nArea: {farm.area} ha\nCrops: {', '.join(farm.crop_types)}",
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        # Add resource centers if requested
        if include_centers:
            for center in self.resource_centers.values():
                distance = self.calculate_distance(farm.location, center.location)
                folium.Marker(
                    [center.location.latitude, center.location.longitude],
                    popup=f"Center ID: {center.center_id}\nServices: {', '.join(center.services)}\nDistance: {distance:.2f} km",
                    icon=folium.Icon(color='red')
                ).add_to(m)
        
        return m._repr_html_()
    
    def export_farm_data(self, farmer_id: str) -> Dict:
        """Export farm GIS data in GeoJSON format"""
        farm = self.farms.get(farmer_id)
        if not farm:
            raise ValueError(f"Farm not found for farmer ID: {farmer_id}")
            
        return {
            "type": "Feature",
            "properties": {
                "farmer_id": farmer_id,
                "area": farm.area,
                "crop_types": farm.crop_types,
                "soil_type": farm.soil_type,
                "registration_date": farm.registration_date.isoformat()
            },
            "geometry": {
                "type": "Point",
                "coordinates": [farm.location.longitude, farm.location.latitude]
            }
        }
    
    def calculate_coverage_statistics(self) -> Dict:
        """Calculate coverage statistics for resource centers"""
        total_farms = len(self.farms)
        farms_within_10km = 0
        farms_within_25km = 0
        
        for farm in self.farms.values():
            nearest_centers = self.find_nearest_centers(farm.location, radius=25)
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
            "coverage_25km_percent": (farms_within_25km / total_farms * 100) if total_farms > 0 else 0
        }