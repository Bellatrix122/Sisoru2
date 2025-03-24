import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load dataset
file_path = "prod_clean.csv"
df = pd.read_csv(file_path)

df.columns = df.columns.str.strip().str.lower()

# Extract unique states and corresponding districts
states = sorted(df['state_name'].unique().tolist())  # Sort states alphabetically
state_district_map = {state: sorted(df[df['state_name'] == state]['dist_name'].unique().tolist()) for state in states}  # Sort districts alphabetically

# Extract crops
crop_columns = [col for col in df.columns if col.endswith("_harvest_price_(rs_per_quintal)")]
crop_mapping = {col.replace("_harvest_price_(rs_per_quintal)", ""): col for col in crop_columns}

# Encode categorical features
label_encoders = {col: LabelEncoder() for col in ['state_name', 'dist_name']}
for col in label_encoders:
    df[col] = label_encoders[col].fit_transform(df[col])

df_melted = df.melt(id_vars=['state_name', 'dist_name', 'year'], var_name='crop', value_name='price')
df_melted['crop'] = df_melted['crop'].str.replace("_harvest_price_.*", "", regex=True)
label_encoders['crop'] = LabelEncoder()
df_melted['crop'] = label_encoders['crop'].fit_transform(df_melted['crop'])

# Train XGBoost model
X = df_melted[['state_name', 'dist_name', 'year', 'crop']]
y = df_melted['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100, learning_rate=0.1)
model.fit(X_train, y_train)

def predict_crop_price(state, district, year, crop):
    try:
        state_encoded = label_encoders['state_name'].transform([state])[0]
        district_encoded = label_encoders['dist_name'].transform([district])[0]
        crop_encoded = label_encoders['crop'].transform([crop])[0]
    except ValueError:
        return "Invalid input. Please select valid state, district, and crop."
    input_data = np.array([[state_encoded, district_encoded, year, crop_encoded]])
    return model.predict(input_data)[0]

# Streamlit UI
st.title("Crop Price Prediction")
selected_state = st.selectbox("Select State", states)
districts = state_district_map[selected_state]
selected_district = st.selectbox("Select District", districts)
selected_crop = st.selectbox("Select Crop", sorted(list(crop_mapping.keys())))  # Sort crops alphabetically
selected_year = st.number_input("Enter Year", min_value=1966, max_value=2025, value=2025, step=1)

if st.button("Predict Price"):
    predicted_price = predict_crop_price(selected_state, selected_district, selected_year, selected_crop)
    st.write(f"Predicted Price for {selected_crop} in {selected_district}, {selected_state} for {selected_year}: ₹{predicted_price:.2f}")
