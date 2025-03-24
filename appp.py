import streamlit as st
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Load datasets
crop_file_path = "crop_optimization_dataset.csv"  # Update with correct path
subsidy_file_path = "government_subsidies.csv"  # Update with correct path

df = pd.read_csv(crop_file_path)
subsidy_df = pd.read_csv(subsidy_file_path)

# Define all states in India
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Get available states in subsidy dataset
subsidy_states = subsidy_df["State"].unique().tolist()

# UI Title
st.title("🌾 Smart Crop Resource Optimization")

# **Step 1: User selects the state**
selected_state = st.selectbox("Select your state:", INDIAN_STATES)

# Get subsidized crops for the selected state
subsidized_crops = []
if selected_state in subsidy_states:
    subsidized_crops = subsidy_df[subsidy_df["State"] == selected_state]["Crop"].unique().tolist()

# **Step 2: User selects crops to grow**
all_crops = df["Crop"].unique().tolist()

# Ensure subsidized crops are selected
selected_crops = st.multiselect(
    "Select crops you want to grow:",
    all_crops,
    default=subsidized_crops if subsidized_crops else all_crops[:5]
)

# Check if the user removed a subsidized crop and show a warning
for crop in subsidized_crops:
    if crop not in selected_crops:
        st.warning(f"⚠️ {crop} is subsidized in {selected_state}. It is recommended to include it.")

# **Step 3: User inputs resource constraints**
total_land = st.number_input("Enter total available land (in hectares):", min_value=1, value=100)
total_water = st.number_input("Enter total available water (in liters):", min_value=1, value=500000)
total_fertilizer = st.number_input("Enter total available fertilizer (in kg):", min_value=1, value=10000)

if st.button("Optimize Crop Allocation"):

    # Filter dataset for selected crops
    df_selected = df[df["Crop"].isin(selected_crops)]

    # Define LP Problem
    model = LpProblem("Crop_Optimization", LpMaximize)

    # Decision Variables (land allocated per crop)
    land_alloc = {row.Crop: LpVariable(f"land_{row.Crop}", lowBound=0) for _, row in df_selected.iterrows()}

    # Objective Function: Maximize yield
    model += lpSum(land_alloc[crop] * df_selected[df_selected.Crop == crop]["Yield_kg_per_hectare"].values[0] for crop in land_alloc)

    # Constraints
    model += lpSum(land_alloc[crop] for crop in land_alloc) <= total_land  # Land constraint
    model += lpSum(land_alloc[crop] * df_selected[df_selected.Crop == crop]["Water_liters_per_hectare"].values[0] for crop in land_alloc) <= total_water  # Water constraint
    model += lpSum(land_alloc[crop] * df_selected[df_selected.Crop == crop]["Fertilizer_kg_per_hectare"].values[0] for crop in land_alloc) <= total_fertilizer  # Fertilizer constraint

    # Diversification Constraint: No single crop gets more than 50% of total land
    for crop in land_alloc:
        model += land_alloc[crop] <= 0.5 * total_land

    # Solve LP Problem
    model.solve()

    # Display Results
    st.subheader("🌱 Optimal Land Allocation per Crop (in hectares):")
    for crop in land_alloc:
        st.write(f"**{crop}**: {land_alloc[crop].varValue:.2f} hectares")

    st.subheader("📊 Total Optimized Yield:")
    st.write(f"**{model.objective.value():.2f} kg**")

