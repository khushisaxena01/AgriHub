# GIS service test (farm registered, farm info, search nearby resource, description of those nearby centers, calculate distance 
# - for 10km and 25km radius & coverage statistics) - with respect to haryana data set 

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import geopy.distance
from geopy.geocoders import Nominatim
import folium
import json
import pandas as pd
import random

@dataclass
class Location:
    latitude: float
    longitude: float
    name: str = ""
    address: str = ""
    district: str = ""
    type: str = ""  # farm, support_center, distribution_center, etc.
    
@dataclass
class Farm:
    location: Location
    area: float  # in hectares
    farmer_id: str
    crop_types: List[str]
    soil_type: str
    season: str
    soil_npk: str
    soil_ph: str
    microbial_solution: str
    water_requirement: str
    registration_date: datetime

@dataclass
class ResourceCenter:
    location: Location
    center_id: str
    services: List[str]
    operating_hours: str
    contact_info: str
    inventory: Dict[str, int]  # resource_name: quantity

class HaryanaGISService:
    def __init__(self):
        self.farms: Dict[str, Farm] = {}
        self.resource_centers: Dict[str, ResourceCenter] = {}
        self.geocoder = Nominatim(user_agent="haryana_agricultural_management_system")
        self.district_coordinates = {
            # Approximate coordinates for Haryana districts
            "Ambala": (30.3752, 76.7821),
            "Bhiwani": (28.7975, 76.1322),
            "Charkhi Dadri": (28.5928, 76.2718),
            "Faridabad": (28.4089, 77.3178),
            "Fatehabad": (29.5152, 75.4555),
            "Gurugram": (28.4595, 77.0266),
            "Hisar": (29.1492, 75.7217),
            "Jhajjar": (28.6162, 76.6499),
            "Jind": (29.3159, 76.3170),
            "Kaithal": (29.8020, 76.3980),
            "Karnal": (29.6857, 76.9905),
            "Kurukshetra": (29.9695, 76.8783),
            "Mahendragarh": (28.2795, 76.1497),
            "Nuh": (28.1043, 77.0015),
            "Palwal": (28.1473, 77.3260),
            "Panchkula": (30.6942, 76.8606),
            "Panipat": (29.3909, 76.9635),
            "Rewari": (28.1994, 76.6194),
            "Rohtak": (28.8955, 76.6066),
            "Sirsa": (29.5321, 75.0318),
            "Sonipat": (28.9931, 77.0151),
            "Yamunanagar": (30.1290, 77.2674)
        }
        
    def load_haryana_data(self, csv_file_path: str):
        """Load data from Haryana agricultural dataset CSV"""
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Successfully loaded data from {csv_file_path}")
            print(f"Total districts: {df['District'].nunique()}")
            
            farmer_id_counter = 1
            for _, row in df.dropna(subset=['District']).iterrows():
                district = row['District']
                if district in self.district_coordinates:
                    # Get district coordinates
                    base_lat, base_lon = self.district_coordinates[district]
                    
                    # Add some random variation to avoid all farms in one district having the same coordinates
                    lat_variance = random.uniform(-0.05, 0.05)
                    lon_variance = random.uniform(-0.05, 0.05)
                    
                    farm_location = Location(
                        latitude=base_lat + lat_variance,
                        longitude=base_lon + lon_variance,
                        district=district,
                        type="farm"
                    )
                    
                    # Extract water requirement as string
                    water_req = str(row['Water Requirement (mm)']) if pd.notna(row['Water Requirement (mm)']) else "N/A"
                    
                    # Create farm object
                    farm = Farm(
                        location=farm_location,
                        area=random.uniform(1.0, 10.0),  # Random area between 1-10 hectares
                        farmer_id=f"F{farmer_id_counter:04d}",
                        crop_types=[row['Crop']] if pd.notna(row['Crop']) else [],
                        soil_type=row['Soil Type'] if pd.notna(row['Soil Type']) else "Unknown",
                        season=row['Season'] if pd.notna(row['Season']) else "Unknown",
                        soil_npk=row['Soil NPK'] if pd.notna(row['Soil NPK']) else "Unknown",
                        soil_ph=row['Soil pH'] if pd.notna(row['Soil pH']) else "Unknown",
                        microbial_solution=row['Microbial Solution'] if pd.notna(row['Microbial Solution']) else "Unknown",
                        water_requirement=water_req,
                        registration_date=datetime.now()
                    )
                    
                    # Register the farm
                    self.register_farm(farm)
                    farmer_id_counter += 1
                    
            print(f"Successfully registered {len(self.farms)} farms")
            
            # Create resource centers (one per district)
            center_id_counter = 1
            for district, coordinates in self.district_coordinates.items():
                base_lat, base_lon = coordinates
                
                # Add some random variation for resource center location
                lat_variance = random.uniform(-0.02, 0.02)
                lon_variance = random.uniform(-0.02, 0.02)
                
                center_location = Location(
                    latitude=base_lat + lat_variance,
                    longitude=base_lon + lon_variance,
                    district=district,
                    type="resource_center"
                )
                
                # Create service list based on main crops in the district
                district_farms = [farm for farm in self.farms.values() if farm.location.district == district]
                district_crops = []
                for farm in district_farms:
                    district_crops.extend(farm.crop_types)
                
                # Default services
                services = ["soil_testing", "equipment_rental", "fertilizer_distribution"]
                
                # Add crop-specific services
                if "Rice" in district_crops:
                    services.append("rice_seed_distribution")
                if "Wheat" in district_crops:
                    services.append("wheat_seed_distribution")
                if "Bajra" in district_crops:
                    services.append("bajra_seed_distribution")
                if "Mustard" in district_crops:
                    services.append("mustard_seed_distribution")
                
                # Create resource center
                center = ResourceCenter(
                    location=center_location,
                    center_id=f"RC{center_id_counter:03d}",
                    services=services,
                    operating_hours="9AM-5PM",
                    contact_info=f"0184-{random.randint(100000, 999999)}",
                    inventory=self.generate_inventory(services)
                )
                
                # Register the resource center
                self.register_resource_center(center)
                center_id_counter += 1
                
            print(f"Successfully registered {len(self.resource_centers)} resource centers")
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def generate_inventory(self, services: List[str]) -> Dict[str, int]:
        """Generate inventory based on services offered"""
        inventory = {}
        
        if "soil_testing" in services:
            inventory["soil_testing_kits"] = random.randint(20, 100)
        
        if "equipment_rental" in services:
            inventory["tractors"] = random.randint(2, 10)
            inventory["power_tillers"] = random.randint(3, 15)
            inventory["harvesters"] = random.randint(1, 5)
        
        if "fertilizer_distribution" in services:
            inventory["urea_bags"] = random.randint(100, 500)
            inventory["dap_bags"] = random.randint(50, 300)
            inventory["potash_bags"] = random.randint(30, 200)
        
        if any(service.endswith("seed_distribution") for service in services):
            inventory["seed_packets"] = random.randint(200, 1000)
        
        return inventory
        
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
        distance = geopy.distance.geodesic(
            (point1.latitude, point1.longitude),
            (point2.latitude, point2.longitude)
        ).kilometers
        return distance
    
    def find_nearest_centers(self, 
                           farm_location: Location, 
                           radius: float,
                           service_type: Optional[str] = None) -> List[Tuple[float, ResourceCenter]]:
        """Find resource centers within specified radius"""
        nearby_centers = []
        
        for center in self.resource_centers.values():
            distance = self.calculate_distance(farm_location, center.location)
            if distance <= radius:
                if service_type is None or service_type in center.services:
                    nearby_centers.append((distance, center))
        
        # Sort by distance
        nearby_centers.sort(key=lambda x: x[0])
        
        return nearby_centers
    
    def display_farm_info(self, farmer_id: str):
        """Display detailed information about a farm"""
        farm = self.farms.get(farmer_id)
        if farm:
            print("\nFarm Information:")
            print(f"Farmer ID: {farm.farmer_id}")
            print(f"District: {farm.location.district}")
            print(f"Location: {farm.location.latitude:.4f}, {farm.location.longitude:.4f}")
            print(f"Area: {farm.area:.2f} hectares")
            print(f"Season: {farm.season}")
            print(f"Crops: {', '.join(farm.crop_types)}")
            print(f"Soil Type: {farm.soil_type}")
            print(f"Soil NPK: {farm.soil_npk}")
            print(f"Soil pH: {farm.soil_ph}")
            print(f"Microbial Solution: {farm.microbial_solution}")
            print(f"Water Requirement: {farm.water_requirement}")
            print(f"Registration Date: {farm.registration_date}")
            
            # Find and display nearby resource centers
            print("\nNearby Resource Centers (10km radius):")
            nearby_centers_10km = self.find_nearest_centers(farm.location, radius=10)
            if nearby_centers_10km:
                for i, (distance, center) in enumerate(nearby_centers_10km, 1):
                    print(f"{i}. Center ID: {center.center_id} (Distance: {distance:.2f} km)")
                    print(f"   District: {center.location.district}")
                    print(f"   Services: {', '.join(center.services)}")
                    print(f"   Operating Hours: {center.operating_hours}")
                    print(f"   Contact: {center.contact_info}")
            else:
                print("No resource centers found within 10km radius.")
                
            print("\nNearby Resource Centers (25km radius):")
            nearby_centers_25km = self.find_nearest_centers(farm.location, radius=25)
            if nearby_centers_25km:
                for i, (distance, center) in enumerate(nearby_centers_25km, 1):
                    if distance > 10:  # Only show centers between 10-25km
                        print(f"{i}. Center ID: {center.center_id} (Distance: {distance:.2f} km)")
                        print(f"   District: {center.location.district}")
                        print(f"   Services: {', '.join(center.services)}")
                        print(f"   Operating Hours: {center.operating_hours}")
                        print(f"   Contact: {center.contact_info}")
            else:
                print("No additional resource centers found within 25km radius.")
        else:
            print(f"Farm not found with ID: {farmer_id}")

    def calculate_coverage_statistics(self) -> Dict:
        """Calculate coverage statistics for resource centers"""
        total_farms = len(self.farms)
        farms_within_10km = 0
        farms_within_25km = 0
        
        district_coverage = {}
        
        for farm in self.farms.values():
            nearest_centers = self.find_nearest_centers(farm.location, radius=25)
            
            # Initialize district coverage if not exists
            district = farm.location.district
            if district not in district_coverage:
                district_coverage[district] = {
                    "total_farms": 0,
                    "farms_within_10km": 0,
                    "farms_within_25km": 0
                }
            
            district_coverage[district]["total_farms"] += 1
            
            if nearest_centers:
                distance_to_nearest = nearest_centers[0][0]  # Get distance from tuple
                if distance_to_nearest <= 10:
                    farms_within_10km += 1
                    district_coverage[district]["farms_within_10km"] += 1
                if distance_to_nearest <= 25:
                    farms_within_25km += 1
                    district_coverage[district]["farms_within_25km"] += 1
        
        # Calculate percentages for each district
        for district in district_coverage:
            district_total = district_coverage[district]["total_farms"]
            if district_total > 0:
                district_coverage[district]["coverage_10km_percent"] = (
                    district_coverage[district]["farms_within_10km"] / district_total * 100
                )
                district_coverage[district]["coverage_25km_percent"] = (
                    district_coverage[district]["farms_within_25km"] / district_total * 100
                )
            else:
                district_coverage[district]["coverage_10km_percent"] = 0
                district_coverage[district]["coverage_25km_percent"] = 0
                    
        return {
            "total_farms": total_farms,
            "farms_within_10km": farms_within_10km,
            "farms_within_25km": farms_within_25km,
            "coverage_10km_percent": (farms_within_10km / total_farms * 100) if total_farms > 0 else 0,
            "coverage_25km_percent": (farms_within_25km / total_farms * 100) if total_farms > 0 else 0,
            "total_resource_centers": len(self.resource_centers),
            "district_coverage": district_coverage
        }
    
    def generate_map(self, output_file: str = "haryana_agricultural_map.html"):
        """Generate an interactive map showing farms and resource centers"""
        # Create a map centered around Haryana
        m = folium.Map(location=[29.0588, 76.0856], zoom_start=8)
        
        # Add farms to the map
        for farm_id, farm in self.farms.items():
            popup_text = f"""
            <b>Farm ID:</b> {farm_id}<br>
            <b>District:</b> {farm.location.district}<br>
            <b>Area:</b> {farm.area:.2f} hectares<br>
            <b>Crop:</b> {', '.join(farm.crop_types)}<br>
            <b>Soil Type:</b> {farm.soil_type}<br>
            <b>Season:</b> {farm.season}
            """
            folium.Marker(
                location=[farm.location.latitude, farm.location.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"Farm: {farm_id}",
                icon=folium.Icon(color='green', icon='leaf', prefix='fa')
            ).add_to(m)
        
        # Add resource centers to the map
        for center_id, center in self.resource_centers.items():
            popup_text = f"""
            <b>Center ID:</b> {center_id}<br>
            <b>District:</b> {center.location.district}<br>
            <b>Services:</b> {', '.join(center.services)}<br>
            <b>Operating Hours:</b> {center.operating_hours}<br>
            <b>Contact:</b> {center.contact_info}
            """
            folium.Marker(
                location=[center.location.latitude, center.location.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"Resource Center: {center_id}",
                icon=folium.Icon(color='red', icon='building', prefix='fa')
            ).add_to(m)
        
        # Save the map
        m.save(output_file)
        print(f"Map generated and saved to {output_file}")

# Test code with the specific file path
def run_haryana_test():
    print("Starting Haryana GIS Service Test...\n")
    
    # Initialize the service
    gis_service = HaryanaGISService()
    
    # Load data from CSV file with the provided path
    file_path = r"C:\Users\KIIT\OneDrive\Desktop\Project\Haryana Agri DataSet.csv"
    gis_service.load_haryana_data(file_path)
    
    # Display coverage statistics
    stats = gis_service.calculate_coverage_statistics()
    print("\nOverall Coverage Statistics:")
    for key, value in stats.items():
        if key == "district_coverage":
            continue  # Skip detailed district coverage for overall summary
        elif "percent" in key:
            print(f"{key}: {value:.1f}%")
        else:
            print(f"{key}: {value}")
    
    # Display district-wise coverage
    print("\nDistrict-wise Coverage Statistics:")
    for district, data in stats["district_coverage"].items():
        print(f"\nDistrict: {district}")
        for key, value in data.items():
            if "percent" in key:
                print(f"  {key}: {value:.1f}%")
            else:
                print(f"  {key}: {value}")
    
    # Display information for a sample farm
    if gis_service.farms:
        sample_farm_id = list(gis_service.farms.keys())[0]
        gis_service.display_farm_info(sample_farm_id)
    
    # Generate interactive map
    gis_service.generate_map()

if __name__ == "__main__":
    run_haryana_test()