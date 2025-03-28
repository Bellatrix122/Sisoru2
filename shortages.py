from flask import Blueprint, render_template, request
import pandas as pd

shortages_bp = Blueprint("shortages", __name__, template_folder="templates")

# Load dataset
file_path = "cleaned_data.csv"
df = pd.read_csv(file_path)

@shortages_bp.route("/crop_shortages", methods=["GET", "POST"])
def district_shortage():
    states = df["State Name"].unique().tolist()
    districts_by_state = {state: df[df["State Name"] == state]["Dist Name"].unique().tolist() for state in states}

    if request.method == "POST":
        state = request.form.get("state")
        district = request.form.get("district")

        if not state or not district:
            return render_template("shortages.html", states=states, districts_by_state=districts_by_state, error="Please select both state and district.")

        # Function to detect shortages
        def detect_crop_shortages(state, district, threshold=10):
            district_data = df[(df["State Name"] == state) & (df["Dist Name"] == district)]
            if district_data.empty:
                return {"shortage_crops": [], "alternative_crops": []}

            # Calculate average irrigation levels per crop
            crop_irrigation = district_data.iloc[:, 5:].mean()
            
            # Identify shortage and alternative crops
            shortage_crops = crop_irrigation[crop_irrigation < threshold].index.tolist()
            alternative_crops = crop_irrigation[crop_irrigation >= threshold].index.tolist()

            return {"shortage_crops": shortage_crops, "alternative_crops": alternative_crops}

        # Get results
        result = detect_crop_shortages(state, district)

        return render_template("shortages.html", states=states, districts_by_state=districts_by_state, 
                               shortage_crops=result["shortage_crops"], alternative_crops=result["alternative_crops"])

    return render_template("shortages.html", states=states, districts_by_state=districts_by_state)


