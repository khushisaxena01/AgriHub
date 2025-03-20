# wrt haryana dataset - microbial soln reccomender, location map & crop calender

import pandas as pd
import gdown
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np
import re
import requests
from geopy.geocoders import Nominatim
import folium
import webbrowser
import os
from datetime import datetime
from PIL import Image, ImageTk
import io

# Download the Haryana Agriculture Dataset
drive_url = "https://drive.google.com/uc?id=1ZGISXNO710PORByb5h4FTUOPC8TsIG40"
file_path = "Haryana_Agri_DataSet.csv"

def download_dataset():
    try:
        gdown.download(drive_url, file_path, quiet=False)
        return True
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return False

# Load and preprocess the dataset
def load_dataset():
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
        return df
    except FileNotFoundError:
        if download_dataset():
            return load_dataset()
        else:
            return None
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

# Define seasonal crops based on the dataset
seasonal_crops = {
    "Kharif": ["Rice", "Bajra", "Maize"],
    "Rabi": ["Wheat", "Mustard", "Barley"],
    "Zaid": ["Vegetables", "Cucumber", "Watermelon"],
    "Summer": ["Sunflower", "Groundnut", "Cotton"]
}

# Temperature ranges for different crops
temperature_ranges = {
    "Wheat": {"min": 10, "max": 25},
    "Rice": {"min": 22, "max": 35},
    "Maize": {"min": 18, "max": 32},
    "Bajra": {"min": 20, "max": 35},
    "Mustard": {"min": 10, "max": 25},
    "Barley": {"min": 12, "max": 25},
    "Vegetables": {"min": 15, "max": 30},
    "Cucumber": {"min": 18, "max": 32},
    "Watermelon": {"min": 20, "max": 35},
    "Sunflower": {"min": 18, "max": 30},
    "Groundnut": {"min": 20, "max": 30},
    "Cotton": {"min": 20, "max": 35}
}

# Initialize geolocation service
geolocator = Nominatim(user_agent="haryana_farm_advisor")

def get_coordinates(district, state="Haryana", country="India"):
    try:
        location = geolocator.geocode(f"{district}, {state}, {country}")
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_weather_data(lat, lon):
    # Using OpenWeatherMap free API (replace with actual API key)
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your actual API key
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Weather API Error: {response.status_code}")
            # For demo purposes, return mock data if API fails
            return {
                "main": {"temp": 24.5, "humidity": 65},
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "wind": {"speed": 3.5}
            }
    except Exception as e:
        print(f"Weather API request error: {e}")
        # Mock data for demonstration
        return {
            "main": {"temp": 24.5, "humidity": 65},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 3.5}
        }

def create_map(lat, lon, district):
    map_file = f"{district}_map.html"
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker(
        [lat, lon], 
        popup=f"<i>{district}</i>", 
        tooltip=district
    ).add_to(m)
    
    # Add a circle to indicate the area
    folium.Circle(
        radius=5000,  # 5km radius
        location=[lat, lon],
        color="green",
        fill=True,
        fill_color="green"
    ).add_to(m)
    
    m.save(map_file)
    return map_file

def determine_current_season():
    month = datetime.now().month
    if 6 <= month <= 9:  # June to September
        return "Kharif/Monsoon"
    elif 10 <= month <= 2:  # October to February
        return "Rabi/Winter"
    elif 3 <= month <= 5:  # March to May
        return "Zaid/Summer"
    else:
        return "Transition"

def recommend_crops(temperature, season):
    suitable_crops = []
    
    if season == "Zaid/Summer":
        current_season_crops = seasonal_crops.get("Zaid", []) + seasonal_crops.get("Summer", [])
    else:
        current_season_crops = seasonal_crops.get(season, [])
    
    for crop in current_season_crops:
        temp_range = temperature_ranges.get(crop, {})
        min_temp = temp_range.get("min", 0)
        max_temp = temp_range.get("max", 50)
        
        if min_temp <= temperature <= max_temp:
            suitable_crops.append(crop)
    
    return suitable_crops

def train_models(df):
    # Extract required columns
    required_columns = ['District', 'Crop', 'Soil Type', 'Season', 'Microbial Solution', 'Microbial Solution Dosage']
    df_cleaned = df[required_columns].dropna()
    
    # Create label encoders for categorical variables
    label_encoders = {}
    for col in required_columns:
        le = LabelEncoder()
        df_cleaned[col] = le.fit_transform(df_cleaned[col])
        label_encoders[col] = le
    
    # Define features and targets
    X = df_cleaned[['District', 'Crop', 'Soil Type', 'Season']]
    y_solution = df_cleaned['Microbial Solution']
    y_dosage = df_cleaned['Microbial Solution Dosage']
    
    # Split data for training
    X_train, X_test, y_solution_train, y_solution_test, y_dosage_train, y_dosage_test = train_test_split(
        X, y_solution, y_dosage, test_size=0.2, random_state=42
    )
    
    # Train models
    solution_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dosage_model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    solution_model.fit(X_train, y_solution_train)
    dosage_model.fit(X_train, y_dosage_train)
    
    return solution_model, dosage_model, label_encoders

class HaryanaFarmAdvisor:
    def __init__(self, root):
        self.root = root
        self.root.title("Haryana Farm Advisor")
        self.root.geometry("800x750")
        self.root.configure(bg="#E0F7FA")
        
        # Load dataset
        self.df = load_dataset()
        if self.df is None:
            messagebox.showerror("Error", "Failed to load dataset. Please check your internet connection.")
            self.root.destroy()
            return
        
        # Extract unique values
        self.unique_districts = sorted(self.df['District'].astype(str).unique().tolist())
        self.unique_crops = sorted(self.df['Crop'].astype(str).unique().tolist())
        self.unique_soils = sorted(self.df['Soil Type'].astype(str).unique().tolist())
        self.unique_seasons = sorted(self.df['Season'].astype(str).unique().tolist())
        
        # Train models
        self.solution_model, self.dosage_model, self.label_encoders = train_models(self.df)
        
        # Create variables for input fields
        self.district_var = tk.StringVar()
        self.crop_var = tk.StringVar()
        self.soil_var = tk.StringVar()
        self.season_var = tk.StringVar()
        self.land_size_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="Acre")
        self.result_var = tk.StringVar()
        self.weather_var = tk.StringVar()
        self.map_district_var = tk.StringVar()
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True, fill="both")
        
        # Tab 1: Microbial Solution Recommender
        tab1 = tk.Frame(notebook, bg="#E0F7FA")
        notebook.add(tab1, text="Microbial Solution Recommender")
        
        canvas = tk.Canvas(tab1, bg="#E0F7FA")
        scrollbar = tk.Scrollbar(tab1, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#E0F7FA")
        
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Input fields
        tk.Label(scroll_frame, text="Select Your District:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        district_dropdown = ttk.Combobox(scroll_frame, textvariable=self.district_var, values=self.unique_districts, width=30)
        district_dropdown.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(scroll_frame, text="Select the Crop:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        crop_dropdown = ttk.Combobox(scroll_frame, textvariable=self.crop_var, values=self.unique_crops, width=30)
        crop_dropdown.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(scroll_frame, text="Select Soil Type:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        soil_dropdown = ttk.Combobox(scroll_frame, textvariable=self.soil_var, values=self.unique_soils, width=30)
        soil_dropdown.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(scroll_frame, text="Select Season:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        season_dropdown = ttk.Combobox(scroll_frame, textvariable=self.season_var, values=self.unique_seasons, width=30)
        season_dropdown.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(scroll_frame, text="Enter Land Size:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(scroll_frame, textvariable=self.land_size_var, width=32).grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(scroll_frame, text="Select Land Unit:", bg="#E0F7FA", font=("Arial", 11, "bold")).grid(row=5, column=0, sticky="w", pady=5)
        unit_dropdown = ttk.Combobox(scroll_frame, textvariable=self.unit_var, values=["Acre", "Hectare", "Square Meter"], width=30)
        unit_dropdown.grid(row=5, column=1, padx=10, pady=5)
        
        # Button to get recommendations
        tk.Button(scroll_frame, text="Get Recommendations", command=self.predict_solution, bg="#00796B", fg="white", font=("Arial", 12, "bold"), width=25).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Results display
        result_label = tk.Label(scroll_frame, textvariable=self.result_var, wraplength=550, fg="blue", bg="#E0F7FA", font=("Arial", 12, "bold"))
        result_label.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Weather and crop recommendation section
        tk.Label(scroll_frame, text="Weather and Crop Recommendations", bg="#E0F7FA", font=("Arial", 13, "bold")).grid(row=8, column=0, columnspan=2, pady=10)
        
        weather_label = tk.Label(scroll_frame, textvariable=self.weather_var, wraplength=550, fg="#006064", bg="#E0F7FA", font=("Arial", 11), justify="left")
        weather_label.grid(row=9, column=0, columnspan=2, pady=10, sticky="w")
        
        tk.Button(scroll_frame, text="View Crop Calendar", command=self.show_crop_calendar, bg="#0097A7", fg="white", font=("Arial", 11)).grid(row=10, column=0, columnspan=2, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tab 2: Location Map
        tab2 = tk.Frame(notebook, bg="#E0F7FA")
        notebook.add(tab2, text="Location Map")
        
        tk.Label(tab2, text="Select a district and click 'Show on Map' to view the location", bg="#E0F7FA", font=("Arial", 12)).pack(pady=20)
        
        map_frame = tk.Frame(tab2, bg="#E0F7FA")
        map_frame.pack(pady=10)
        
        tk.Label(map_frame, text="District:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10)
        map_district_dropdown = ttk.Combobox(map_frame, textvariable=self.map_district_var, values=self.unique_districts, width=30)
        map_district_dropdown.grid(row=0, column=1, padx=10)
        
        tk.Button(map_frame, text="Show on Map", command=self.show_map, bg="#00796B", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=10)
        
        # Set default values
        self.season_var.set(determine_current_season())
    
    def predict_solution(self):
        district = self.district_var.get()
        crop = self.crop_var.get()
        soil_type = self.soil_var.get()
        season = self.season_var.get()
        land_size = self.land_size_var.get().strip()
        unit = self.unit_var.get()
        
        if not district or not crop or not soil_type or not season or not land_size or not unit:
            messagebox.showerror("Input Error", "Please fill in all the fields!")
            return
        
        try:
            land_size = float(land_size)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for land size.")
            return
        
        # Convert to hectares if necessary
        if unit == "Hectare":
            land_size_acres = land_size * 2.47105
        elif unit == "Square Meter":
            land_size_acres = land_size * 0.000247105
        else:  # Already in acres
            land_size_acres = land_size
        
        # Encode input data
        try:
            district_encoded = self.label_encoders['District'].transform([district])[0]
            crop_encoded = self.label_encoders['Crop'].transform([crop])[0]
            soil_encoded = self.label_encoders['Soil Type'].transform([soil_type])[0]
            season_encoded = self.label_encoders['Season'].transform([season])[0]
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return
        
        # Predict solution and dosage
        # Create a DataFrame with proper column names
        input_df = pd.DataFrame({'District': [district_encoded],'Crop': [crop_encoded],'Soil Type': [soil_encoded],'Season': [season_encoded]})
        solution_pred = self.solution_model.predict(input_df)[0]
        dosage_pred = self.dosage_model.predict(input_df)[0]
        
        # Transform predictions back to original values
        solution_name = self.label_encoders['Microbial Solution'].inverse_transform([solution_pred])[0]
        dosage_value = self.label_encoders['Microbial Solution Dosage'].inverse_transform([dosage_pred])[0]
        
        # Calculate adjusted dosage
        dosage_numeric = re.findall(r'\d+\.?\d*', dosage_value)
        if dosage_numeric:
            dosage_numeric = float(dosage_numeric[0]) * land_size_acres
            
            if "L water" in dosage_value:
                water_amount = re.findall(r'in (\d+\.?\d*) L', dosage_value)
                if water_amount:
                    water_amount = float(water_amount[0]) * land_size_acres
                    adjusted_dosage = f"{dosage_numeric:.2f} kg in {water_amount:.0f} L water"
                else:
                    adjusted_dosage = f"{dosage_numeric:.2f} kg"
            else:
                adjusted_dosage = f"{dosage_numeric:.2f} kg"
        else:
            adjusted_dosage = f"{dosage_value} (for {land_size} {unit})"
        
        # Display recommendation
        self.result_var.set(f"Recommended Microbial Solution: {solution_name}\nExact Dosage: {adjusted_dosage}")
        
        # Get location and weather data
        self.get_location_weather(district)
    
    def get_location_weather(self, district):
        # Get coordinates
        coords = get_coordinates(district)
        if not coords:
            self.weather_var.set("Location not found. Unable to retrieve weather data.")
            return
        
        lat, lon = coords
        
        # Create and display map
        map_file = create_map(lat, lon, district)
        map_path = os.path.abspath(map_file)
        webbrowser.open("file://" + map_path)
        
        # Get weather data
        weather_data = get_weather_data(lat, lon)
        
        if weather_data:
            temp = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            weather_desc = weather_data["weather"][0]["description"]
            wind_speed = weather_data["wind"]["speed"]
            
            # Determine season and recommend crops
            current_season = determine_current_season()
            suitable_crops = recommend_crops(temp, current_season)
            
            # Get water requirement from dataset for selected crop
            try:
                water_req = self.df[(self.df['District'] == district) & 
                                   (self.df['Crop'] == self.crop_var.get())]['Water Requirement (mm)'].values[0]
            except:
                water_req = "Not available"
            
            weather_info = (
                f"Weather at {district}:\n"
                f"Temperature: {temp}°C\n"
                f"Humidity: {humidity}%\n"
                f"Conditions: {weather_desc}\n"
                f"Wind: {wind_speed} m/s\n\n"
                f"Current Season: {current_season}\n"
                f"Water Requirement for {self.crop_var.get()}: {water_req}\n\n"
                f"Suitable Crops to Plant Now:\n"
                f"{', '.join(suitable_crops) if suitable_crops else 'No suitable crops for current weather'}"
            )
            
            self.weather_var.set(weather_info)
        else:
            self.weather_var.set("Failed to retrieve weather data.")
    
    def show_map(self):
        district = self.map_district_var.get()
        if not district:
            messagebox.showerror("Input Error", "Please select a district")
            return
        
        coords = get_coordinates(district)
        if not coords:
            messagebox.showerror("Error", "Could not find coordinates for the selected district")
            return
        
        map_file = create_map(*coords, district)
        webbrowser.open("file://" + os.path.abspath(map_file))
    
    def show_crop_calendar(self):
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Crop Calendar - Haryana")
        calendar_window.geometry("600x400")
        
        # Create a table showing crops by season
        tk.Label(calendar_window, text="Seasonal Crop Calendar for Haryana", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame = tk.Frame(calendar_window)
        frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Create headers
        seasons = ["Kharif", "Rabi", "Zaid", "Summer"]
        for i, season in enumerate(seasons):
            tk.Label(frame, text=season, font=("Arial", 12, "bold"), bg="#E0F7FA", width=15).grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
        
        # Find the longest list of crops
        max_crops = max([len(seasonal_crops[season]) for season in seasons])
        
        # Fill in the crops
        for row in range(max_crops):
            for col, season in enumerate(seasons):
                if row < len(seasonal_crops[season]):
                    crop = seasonal_crops[season][row]
                    temp_range = temperature_ranges.get(crop, {})
                    temp_text = f"{temp_range.get('min', '?')}°C-{temp_range.get('max', '?')}°C"
                    text = f"{crop}\n{temp_text}"
                    tk.Label(frame, text=text, bg="#FFFFFF", relief="ridge", width=15, height=2).grid(row=row+1, column=col, padx=2, pady=2, sticky="nsew")

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = HaryanaFarmAdvisor(root)
    root.mainloop()