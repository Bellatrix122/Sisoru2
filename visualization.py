import pandas as pd
import plotly.graph_objects as go
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

def cost_prediction_chart(n_cost=20, p_cost=25, k_cost=18):
    df_cost = df_sample.copy()

    # Compute total fertilizer cost per hectare
    df_cost["Nitrogen Cost (Rs/ha)"] = df_cost["nitrogen_per_ha_of_nca_kg_per_ha"] * n_cost
    df_cost["Phosphate Cost (Rs/ha)"] = df_cost["phosphate_per_ha_of_nca_kg_per_ha"] * p_cost
    df_cost["Potash Cost (Rs/ha)"] = df_cost["potash_per_ha_of_nca_kg_per_ha"] * k_cost

    # Aggregate yearly averages
    df_plot = df_cost.groupby("year")[["Nitrogen Cost (Rs/ha)", "Phosphate Cost (Rs/ha)", "Potash Cost (Rs/ha)"]].mean().reset_index()

    # Melt for plotting
    df_melted = df_plot.melt(id_vars=["year"], var_name="Fertilizer Type", value_name="Cost (Rs/ha)")

    # Create line chart
    fig = px.line(
        df_melted, 
        x="year", 
        y="Cost (Rs/ha)", 
        color="Fertilizer Type",
        markers=True,
        title="Fertilizer Cost Trend Over Time",
        labels={"year": "Year", "Cost (Rs/ha)": "Cost per Hectare (Rs)"},
    )

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
    irrigated_cols = [col for col in df_sample.columns if col.endswith("_irrigated_area_1000_ha")]

    if not irrigated_cols:
        return "<p style='color:red;'>No irrigation data available for visualization.</p>"

    shortages = []
    recent_years = df_sample["year"].max() - 2
    df_recent = df_sample[df_sample["year"] >= recent_years]

    for col in irrigated_cols:
        crop_name = col.replace("_irrigated_area_1000_ha", "").replace("_", " ").title()
        recent_avg = df_recent[col].mean()
        past_avg = df_sample[col].mean()
        shortage_pct = 100 * (1 - recent_avg / past_avg) if past_avg > 0 else 0
        shortages.append((crop_name, shortage_pct))

    shortage_df = pd.DataFrame(shortages, columns=["Crop", "Shortage %"])
    shortage_df.sort_values("Shortage %", ascending=False, inplace=True)

    fig = px.bar(
        shortage_df,
        x="Shortage %",
        y="Crop",
        orientation="h",
        title="Irrigation Shortages (3-Year Avg vs Overall Avg)",
        labels={"Shortage %": "Irrigation Shortage (%)"},
        color="Shortage %",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        height=600,  # Set a fixed height
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(automargin=True)  # Ensure labels fit
    )

    return f"""
    <div style="overflow-y: auto; height: 600px;">
        {fig.to_html(full_html=False)}
    </div>
    """
