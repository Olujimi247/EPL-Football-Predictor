import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
#from werkzeug.security import generate_password_hash, check_password_hash

# ===== Function to Save Predictions =====
def save_prediction_to_csv(features: dict, predictions: dict, filename="predictions_log.csv"):
    if not isinstance(features, dict):
        raise ValueError("Features must be a dictionary")
    if not isinstance(predictions, dict):
        raise ValueError("Predictions must be a dictionary")

    def clean_dict(d):
        return {k: (v.item() if hasattr(v, "item") else v) for k, v in d.items()}

    clean_features = clean_dict(features)
    clean_predictions = clean_dict(predictions)

    # Merge into one row
    record = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    record.update(clean_features)
    record.update(clean_predictions)

    # Desired order for predictions
    prediction_order = ["HDA", "OVER25", "BTTS", "DOUBLE_CHANCE"]

    # Column order: timestamp → home_team → away_team → feature cols → predictions
    col_order = ["timestamp", "home_team", "away_team"]

    # Add feature columns (exclude teams if they exist inside features)
    feature_cols = [col for col in clean_features.keys() if col not in ["home_team", "away_team"]]
    col_order.extend(feature_cols)

    # Add predictions in fixed order (only those present)
    col_order.extend([p for p in prediction_order if p in clean_predictions])

    # Add any extra columns not covered
    col_order.extend([col for col in record.keys() if col not in col_order])

    # Save row in proper order
    df = pd.DataFrame([record])[col_order]

    if os.path.exists(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, mode="w", header=True, index=False)

        
# Load models
models = {
    "HDA": joblib.load("MODEL_HDA.pkl"),
    "OVER25": joblib.load("MODEL_OVER25.pkl"),
    "BTTS": joblib.load("MODEL_BTTS.pkl"),
    "DOUBLE_CHANCE": joblib.load("MODEL_DOUBLE_CHANCE.pkl"),
}

st.set_page_config(page_title="Football Match Predictor", layout="wide")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in first.")
    st.switch_page("pages/login.py")  # redirect to login

# Protected Areas

st.title("⚽ EPL Football Match Predictor")
st.markdown("Predict outcomes for multiple betting markets (HDA, Over 2.5, BTTS, Double Chance).")
st.markdown("👉 Go to **Probabilities Page** (see sidebar menu) to view probability details.")

# Sidebar inputs
st.sidebar.header("Match Input Features")
home_team = st.sidebar.text_input("🏠 Home Team", "Arsenal")
away_team = st.sidebar.text_input("🛫 Away Team", "Chelsea")

home_form = st.sidebar.number_input("Home Form (last 5 matches points)", min_value=0.0, max_value=15.0, value=7.0)
away_form = st.sidebar.number_input("Away Form (last 5 matches points)", min_value=0.0, max_value=15.0, value=6.0)

home_avg_goals = st.sidebar.number_input("Home Avg Goals (last 5 matches)", min_value=0.0, max_value=5.0, value=1.6)
away_avg_goals = st.sidebar.number_input("Away Avg Goals (last 5 matches)", min_value=0.0, max_value=5.0, value=1.2)

# Build dataframe
input_data = pd.DataFrame([{
    "HOME_FORM": home_form,
    "AWAY_FORM": away_form,
    "HOME_AVG_GOALS": home_avg_goals,
    "AWAY_AVG_GOALS": away_avg_goals,
}])

# --- Link & button to Probabilities page ---
st.divider()
st.subheader("📊 Want detailed probabilities?")

# Modern Streamlit (>=1.32) has page_link
if hasattr(st, "page_link"):
    st.page_link("pages/Probabilities.py", label="👉 Open Probabilities Page")

# Session-based navigation (fallback for older versions)
if st.button("Go to Probabilities (carry inputs)"):
    st.session_state["prob_input"] = input_data.to_dict(orient="records")[0]
    st.session_state["home_team"] = home_team
    st.session_state["away_team"] = away_team

    # Try to use switch_page if available
    if "switch_page" in dir(st):
        try:
            st.switch_page("pages/Probabilities.py")
        except Exception:
            st.info("🔗 Please click 'Probabilities' in the sidebar.")
    else:
        st.info("🔗 Please click 'Probabilities' in the sidebar.")



if st.sidebar.button("Predict"):
    st.subheader(f"Predictions: {home_team} vs {away_team}")

    hda_map = {1: "🏠 Home Win", 0: "🤝 Draw", -1: "🛫 Away Win"}
    predictions_dict = {}  # store all model results

    for market, model in models.items():
        pred = model.predict(input_data)[0]

        if market == "HDA":
            result = hda_map[pred]
        elif market == "OVER25":
            result = "✅ Over 2.5 Goals" if pred == 1 else "❌ Under 2.5 Goals"
        elif market == "BTTS":
            result = "✅ Both Teams to Score" if pred == 1 else "❌ No BTTS"
        elif market == "DOUBLE_CHANCE":
            result = "✅ Home or Draw" if pred == 1 else "❌ Away Win Only"
        else:
            result = pred

        st.metric(label=f"{market} Prediction", value=result)

        predictions_dict[market] = result

    # Convert features to dictionary
    features_dict = input_data.to_dict(orient="records")[0]
    features_dict["home_team"] = home_team
    features_dict["away_team"] = away_team

    # Save
    save_prediction_to_csv(features_dict, predictions_dict)
    st.info("✅ Prediction saved to predictions_log.csv")
