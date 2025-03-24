# updated ML core (microbial vs fertilizer and cost comparison)

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import re
import os

MICROBIAL_PATH = r"C:\Users\KIIT\OneDrive\Desktop\Project\MicrobialSolutionHaryanaDataset.csv"
FERTILIZER_PATH = r"C:\Users\KIIT\OneDrive\Desktop\Project\FertilizerHaryanaDataSet.csv" 

for path in [MICROBIAL_PATH, FERTILIZER_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

df_micro = pd.read_csv(MICROBIAL_PATH)
df_micro.columns = df_micro.columns.str.strip()
df_micro = df_micro.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_micro["District"] = df_micro["District"].ffill()

df_fert = pd.read_csv(FERTILIZER_PATH)
df_fert.columns = df_fert.columns.str.strip()
df_fert = df_fert.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_fert["District"] = df_fert["District"].ffill()

micro_columns = ['District', 'Crop', 'Soil Type', 'Season', 'Microbial Solution', 'Microbial Solution Dosage',
                 'Soil Feritility Increase %', 'Cost (INR/acre)', 'Microbial Solution Content %']
fert_columns = ['District', 'Crop', 'Soil Type', 'Season', 'Fertilizer Solution', 'Fertilizer Solution Dosage',
                'Soil Feritility Increase %', 'Cost (INR/acre)', 'Fertilizer Solution Content %']

df_micro_cleaned = df_micro[micro_columns].dropna()
df_fert_cleaned = df_fert[fert_columns].dropna()

unique_districts = sorted(set(df_micro_cleaned['District'].unique()).union(df_fert_cleaned['District'].unique()))
unique_crops = sorted(set(df_micro_cleaned['Crop'].unique()).union(df_fert_cleaned['Crop'].unique()))
unique_soils = sorted(set(df_micro_cleaned['Soil Type'].unique()).union(df_fert_cleaned['Soil Type'].unique()))
unique_seasons = sorted(set(df_micro_cleaned['Season'].unique()).union(df_fert_cleaned['Season'].unique()))
unit_options = ["Acre", "Hectare", "Square Meter"]

micro_encoders = {}
for col in ['District', 'Crop', 'Soil Type', 'Season', 'Microbial Solution', 'Microbial Solution Dosage']:
    le = LabelEncoder()
    df_micro_cleaned[col] = le.fit_transform(df_micro_cleaned[col])
    micro_encoders[col] = le

X_micro = df_micro_cleaned[['District', 'Crop', 'Soil Type', 'Season']]
y_micro_solution = df_micro_cleaned['Microbial Solution']
y_micro_dosage = df_micro_cleaned['Microbial Solution Dosage']

X_micro_train, X_micro_test, y_micro_solution_train, y_micro_solution_test, y_micro_dosage_train, y_micro_dosage_test = train_test_split(
    X_micro, y_micro_solution, y_micro_dosage, test_size=0.2, random_state=42
)
micro_solution_model = RandomForestClassifier(n_estimators=100, random_state=42)
micro_dosage_model = RandomForestClassifier(n_estimators=100, random_state=42)
micro_solution_model.fit(X_micro_train, y_micro_solution_train)
micro_dosage_model.fit(X_micro_train, y_micro_dosage_train)

fert_encoders = {}
for col in ['District', 'Crop', 'Soil Type', 'Season', 'Fertilizer Solution', 'Fertilizer Solution Dosage']:
    le = LabelEncoder()
    df_fert_cleaned[col] = le.fit_transform(df_fert_cleaned[col])
    fert_encoders[col] = le

X_fert = df_fert_cleaned[['District', 'Crop', 'Soil Type', 'Season']]
y_fert_solution = df_fert_cleaned['Fertilizer Solution']
y_fert_dosage = df_fert_cleaned['Fertilizer Solution Dosage']

X_fert_train, X_fert_test, y_fert_solution_train, y_fert_solution_test, y_fert_dosage_train, y_fert_dosage_test = train_test_split(
    X_fert, y_fert_solution, y_fert_dosage, test_size=0.2, random_state=42
)
fert_solution_model = RandomForestClassifier(n_estimators=100, random_state=42)
fert_dosage_model = RandomForestClassifier(n_estimators=100, random_state=42)
fert_solution_model.fit(X_fert_train, y_fert_solution_train)
fert_dosage_model.fit(X_fert_train, y_fert_dosage_train)

def get_fertility_midpoint(fertility_str):
    try:
        low, high = map(float, re.findall(r'\d+\.?\d*', fertility_str))
        return (low + high) / 2
    except:
        return 0

def predict_solution():
    district = district_var.get()
    crop = crop_var.get()
    soil_type = soil_var.get()
    season = season_var.get()
    land_size = land_size_var.get().strip()
    unit = unit_var.get()

    if not all([district, crop, soil_type, season, land_size, unit]):
        messagebox.showerror("Input Error", "Please fill in all fields!")
        return

    try:
        land_size = float(land_size)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for land size.")
        return

    if unit == "Hectare":
        land_size_in_acres = land_size * 2.471
    elif unit == "Square Meter":
        land_size_in_acres = land_size / 4046.86
    else:
        land_size_in_acres = land_size

    try:
        district_micro_encoded = micro_encoders['District'].transform([district])[0]
        crop_micro_encoded = micro_encoders['Crop'].transform([crop])[0]
        soil_micro_encoded = micro_encoders['Soil Type'].transform([soil_type])[0]
        season_micro_encoded = micro_encoders['Season'].transform([season])[0]

        district_fert_encoded = fert_encoders['District'].transform([district])[0]
        crop_fert_encoded = fert_encoders['Crop'].transform([crop])[0]
        soil_fert_encoded = fert_encoders['Soil Type'].transform([soil_type])[0]
        season_fert_encoded = fert_encoders['Season'].transform([season])[0]
    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input: {e}")
        return

    micro_solution_pred = micro_solution_model.predict(
        [[district_micro_encoded, crop_micro_encoded, soil_micro_encoded, season_micro_encoded]])[0]
    micro_dosage_pred = micro_dosage_model.predict(
        [[district_micro_encoded, crop_micro_encoded, soil_micro_encoded, season_micro_encoded]])[0]

    micro_solution = micro_encoders['Microbial Solution'].inverse_transform([micro_solution_pred])[0]
    micro_dosage = micro_encoders['Microbial Solution Dosage'].inverse_transform([micro_dosage_pred])[0]

    dosage_numeric = re.findall(r'\d+\.?\d*', micro_dosage)
    if dosage_numeric:
        dosage_numeric = float(dosage_numeric[0]) * land_size_in_acres
        if "kg/acre" in micro_dosage and "water" in micro_dosage:
            water_factor = float(re.findall(r'(\d+).*water', micro_dosage)[0]) * land_size_in_acres
            micro_adjusted_dosage = f"{dosage_numeric:.2f} kg in {water_factor:.2f} L water"
        elif "gm/acre" in micro_dosage or "gm/kg" in micro_dosage:
            micro_adjusted_dosage = f"{dosage_numeric:.2f} gm"
        else:
            micro_adjusted_dosage = f"{dosage_numeric:.2f} units"
    else:
        micro_adjusted_dosage = micro_dosage

    micro_match = df_micro[
        (df_micro['Microbial Solution'].str.lower().str.strip() == micro_solution.lower().strip()) &
        (df_micro['Microbial Solution Dosage'].str.lower().str.strip() == micro_dosage.lower().strip())
        ]
    if micro_match.empty:
        micro_fertility = "15-20%"
        micro_cost_range = "550-600"
        micro_content = "Unknown ratio"
    else:
        micro_row = micro_match.iloc[0]
        micro_fertility = micro_row['Soil Feritility Increase %']
        micro_cost_range = micro_row['Cost (INR/acre)']
        micro_content = micro_row['Microbial Solution Content %']
    micro_cost = (float(micro_cost_range.split("-")[0]) + float(
        micro_cost_range.split("-")[1])) / 2 * land_size_in_acres

    fert_solution_pred = \
    fert_solution_model.predict([[district_fert_encoded, crop_fert_encoded, soil_fert_encoded, season_fert_encoded]])[0]
    fert_dosage_pred = \
    fert_dosage_model.predict([[district_fert_encoded, crop_fert_encoded, soil_fert_encoded, season_fert_encoded]])[0]

    fert_solution = fert_encoders['Fertilizer Solution'].inverse_transform([fert_solution_pred])[0]
    fert_dosage = fert_encoders['Fertilizer Solution Dosage'].inverse_transform([fert_dosage_pred])[0]

    print(f"Predicted Fertilizer Solution: '{fert_solution}'")
    print(f"Predicted Fertilizer Dosage: '{fert_dosage}'")
    fert_match_exact = df_fert[
        (df_fert['Fertilizer Solution'].str.lower().str.strip() == fert_solution.lower().strip()) &
        (df_fert['Fertilizer Solution Dosage'].str.lower().str.strip() == fert_dosage.lower().strip())
        ]
    print(f"Exact matches (solution + dosage): {len(fert_match_exact)}")

    if fert_match_exact.empty:
        fert_match_fallback = df_fert[
            (df_fert['Fertilizer Solution'].str.lower().str.strip() == fert_solution.lower().strip())
        ]
        print(f"Fallback matches (solution only): {len(fert_match_fallback)}")
        fert_match = fert_match_fallback if not fert_match_fallback.empty else fert_match_exact
    else:
        fert_match = fert_match_exact

    if fert_match.empty:
        fert_fertility = "20-25%"
        fert_cost_range = "2000-2500"
        fert_content = "Unknown ratio"
        print("No match found, using defaults")
    else:
        fert_row = fert_match.iloc[0]
        fert_fertility = fert_row['Soil Feritility Increase %']
        fert_cost_range = fert_row['Cost (INR/acre)']
        fert_content = fert_row['Fertilizer Solution Content %']
        print(f"Matched row: {fert_row.to_dict()}")

    fert_cost = (float(fert_cost_range.split("-")[0]) + float(fert_cost_range.split("-")[1])) / 2 * land_size_in_acres

    micro_fertility_mid = get_fertility_midpoint(micro_fertility)
    fert_fertility_mid = get_fertility_midpoint(fert_fertility)
    micro_cost_effectiveness = micro_fertility_mid / micro_cost if micro_cost > 0 else 0
    fert_cost_effectiveness = fert_fertility_mid / fert_cost if fert_cost > 0 else 0

    if micro_fertility_mid > fert_fertility_mid and micro_cost <= fert_cost * 1.2:
        better_option = "Microbial Solution"
        why_better = (
            f"The microbial solution ({micro_solution}) is recommended because it offers a higher soil fertility increase "
            f"({micro_fertility}, midpoint {micro_fertility_mid:.1f}%) compared to the fertilizer ({fert_fertility}, midpoint {fert_fertility_mid:.1f}%) "
            f"at a lower or comparable cost (₹{micro_cost:.2f} vs ₹{fert_cost:.2f}). Additionally, microbial solutions are more eco-friendly, promoting sustainable soil health."
        )
    elif fert_fertility_mid > micro_fertility_mid and fert_cost <= micro_cost * 1.2:
        better_option = "Fertilizer Solution"
        why_better = (
            f"The fertilizer solution ({fert_solution}) is recommended because it provides a higher soil fertility increase "
            f"({fert_fertility}, midpoint {fert_fertility_mid:.1f}%) compared to the microbial solution ({micro_fertility}, midpoint {micro_fertility_mid:.1f}%) "
            f"at a lower or comparable cost (₹{fert_cost:.2f} vs ₹{micro_cost:.2f}). Fertilizers also offer faster nutrient availability."
        )
    else:
        if micro_cost_effectiveness > fert_cost_effectiveness:
            better_option = "Microbial Solution"
            why_better = (
                f"The microbial solution ({micro_solution}) is recommended for its better cost-effectiveness "
                f"({micro_fertility_mid:.1f}% fertility increase per ₹{micro_cost:.2f}) compared to the fertilizer "
                f"({fert_fertility_mid:.1f}% per ₹{fert_cost:.2f}). It’s also more sustainable long-term."
            )
        else:
            better_option = "Fertilizer Solution"
            why_better = (
                f"The fertilizer solution ({fert_solution}) is recommended for its better cost-effectiveness "
                f"({fert_fertility_mid:.1f}% fertility increase per ₹{fert_cost:.2f}) compared to the microbial solution "
                f"({micro_fertility_mid:.1f}% per ₹{micro_cost:.2f}). It provides quicker results."
            )

    result = (
        f"For {crop} stubble in {season}, {district} ({soil_type} soil):\n\n"
        f"Microbial Solution:\n{micro_solution}\n"
        f"Content Ratio: {micro_content}\n"
        f"Dosage: {micro_adjusted_dosage}\n"
        f"Fertility Increase: {micro_fertility}\n"
        f"Cost: ₹{micro_cost:.2f}\n\n"
        f"OR\n\n"
        f"Fertilizer Solution:\n{fert_solution}\n"
        f"Content Ratio: {fert_content}\n"
        f"Dosage: {fert_dosage}\n"
        f"Fertility Increase: {fert_fertility}\n"
        f"Cost: ₹{fert_cost:.2f}\n\n"
        f"Recommendation:\n"
        f"Better Option: {better_option}\n"
        f"Why: {why_better}"
    )

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

root = tk.Tk()
root.title("Farm Stubble Management Recommender")
root.geometry("700x800")
root.configure(bg="#E0F7FA")

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="Stubble Management Recommendations", font=("Arial", 16, "bold")).grid(row=0, column=0,
                                                                                                  columnspan=2, pady=10)

input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

labels = ["District:", "Harvested Crop:", "Soil Type:", "Season:", "Land Unit:", "Land Size:"]
vars_list = [tk.StringVar() for _ in range(5)]
options = [unique_districts, unique_crops, unique_soils, unique_seasons, unit_options]

for i, (label, var, opts) in enumerate(zip(labels[:-1], vars_list, options)):
    ttk.Label(input_frame, text=label, font=("Arial", 12)).grid(row=i, column=0, sticky="w", pady=5)
    combo = ttk.Combobox(input_frame, textvariable=var, values=opts, state="readonly", width=30)
    combo.grid(row=i, column=1, sticky="w", pady=5)
    combo.set(opts[0])

ttk.Label(input_frame, text="Land Size:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5)
land_size_var = tk.StringVar()
land_size_entry = ttk.Entry(input_frame, textvariable=land_size_var, width=32)
land_size_entry.grid(row=5, column=1, sticky="w", pady=5)

district_var, crop_var, soil_var, season_var, unit_var = vars_list

ttk.Button(main_frame, text="Get Recommendation", command=predict_solution).grid(row=2, column=0, columnspan=2, pady=20)

result_frame = ttk.LabelFrame(main_frame, text="Recommendation", padding="10")
result_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)

canvas = tk.Canvas(result_frame, height=300)
scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

result_text = tk.Text(scrollable_frame, wrap="word", font=("Arial", 11), height=15, width=80)
result_text.pack(fill="both", expand=True)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", configure_canvas)

main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(3, weight=1)
input_frame.columnconfigure(1, weight=1)

style = ttk.Style()
style.configure("TLabel", background="#E0F7FA")
style.configure("TButton", font=("Arial", 12))
style.configure("TLabelframe.Label", font=("Arial", 12))

root.mainloop()