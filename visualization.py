# visualization.py
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("data/merged_dataset.csv")

# Filter data to the last 10 years for better readability
df = df[df["year"] >= df["year"].max() - 10]

# Reduce data for better aesthetics
df_sample = df.sample(frac=0.05, random_state=42)

def get_available_crops():
    # Extract all columns ending with '_yield_kg_per_ha'
    yield_columns = [col for col in df.columns if col.endswith('_yield_kg_per_ha')]
    return yield_columns


def cost_prediction_chart():
    df_melted = df_sample.melt(id_vars=["year"], 
                             value_vars=["nitrogen_per_ha_of_nca_kg_per_ha", 
                                        "phosphate_per_ha_of_nca_kg_per_ha", 
                                        "potash_per_ha_of_nca_kg_per_ha"], 
                             var_name="Cost Type", value_name="Value")
    
    fig = px.bar(df_melted, x="year", y="Value", color="Cost Type", 
               title="Fertilizer Usage Over Time",
               labels={"Value": "Usage (kg/ha)", "Cost Type": "Fertilizer Type"},
               barmode="group")
    fig.update_layout(width=800)
    return fig.to_html(full_html=False)


def crop_advisor_chart(crop1="rice_yield_kg_per_ha", crop2="wheat_yield_kg_per_ha"):
    # Check if the selected crops exist in the dataset
    if crop1 not in df_sample.columns or crop2 not in df_sample.columns:
        return "<p>Error: Selected crops not found in dataset.</p>"
    
    # Melt the dataframe to make it suitable for a grouped bar chart
    df_melted = df_sample.melt(id_vars=["state_name"], value_vars=[crop1, crop2], 
                               var_name="Crop", value_name="Yield")
    
    # Replace column names for better readability
    df_melted["Crop"] = df_melted["Crop"].str.replace("_yield_kg_per_ha", "").str.title()
    
    # Create bar chart
    fig = px.bar(
        df_melted,
        x="state_name",
        y="Yield",
        color="Crop",
        barmode="group",
        title=f"Comparison of {crop1.replace('_yield_kg_per_ha', '').title()} and {crop2.replace('_yield_kg_per_ha', '').title()} Yield",
        labels={"state_name": "State", "Yield": "Yield (kg/ha)"}
    )
    
    fig.update_layout(width=800)
    return fig.to_html(full_html=False)

def shortages_chart():
    df_sample["total_irrigated_area"] = df_sample[["rice_irrigated_area_1000_ha", 
                                                 "wheat_irrigated_area_1000_ha", 
                                                 "maize_irrigated_area_1000_ha"]].sum(axis=1)
    
    fig = px.bar(df_sample, x="year", y="total_irrigated_area", color="state_name",
               title="Total Irrigated Area Over Time",
               labels={"total_irrigated_area": "Total Irrigated Area (1000 ha)", 
                     "state_name": "State"})
    fig.update_layout(width=800)
    return fig.to_html(full_html=False)