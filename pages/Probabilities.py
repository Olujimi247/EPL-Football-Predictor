import streamlit as st
import pandas as pd
import joblib

# Load models
models = {
    "HDA": joblib.load("MODEL_HDA.pkl"),
    "OVER25": joblib.load("MODEL_OVER25.pkl"),
    "BTTS": joblib.load("MODEL_BTTS.pkl"),
    "DOUBLE_CHANCE": joblib.load("MODEL_DOUBLE_CHANCE.pkl"),
}

st.title("📊 Prediction Probabilities")

# Protected Areas

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in first.")
    st.switch_page("pages/login.py")

# Only admin can see this page
if st.session_state["role"] != "admin":
    st.error("Access denied. Admin only.")
    st.stop()

if st.button("Logout", key="logout_prob"):
    st.session_state["logged_in"] = False
    st.rerun()

# --- Prefill from session_state if available ---
defaults = st.session_state.get("prob_input", {})
home_team_default = st.session_state.get("home_team", "Arsenal")
away_team_default = st.session_state.get("away_team", "Chelsea")

st.sidebar.header("Match Input Features")
home_team = st.sidebar.text_input("🏠 Home Team", value=home_team_default)
away_team = st.sidebar.text_input("🛫 Away Team", value=away_team_default)

home_form = st.sidebar.number_input(
    "Home Form (last 5 points)", min_value=0.0, max_value=15.0,
    value=float(defaults.get("HOME_FORM", 7.0))
)
away_form = st.sidebar.number_input(
    "Away Form (last 5 points)", min_value=0.0, max_value=15.0,
    value=float(defaults.get("AWAY_FORM", 6.0))
)
home_avg_goals = st.sidebar.number_input(
    "Home Avg Goals (last 5)", min_value=0.0, max_value=5.0,
    value=float(defaults.get("HOME_AVG_GOALS", 1.6))
)
away_avg_goals = st.sidebar.number_input(
    "Away Avg Goals (last 5)", min_value=0.0, max_value=5.0,
    value=float(defaults.get("AWAY_AVG_GOALS", 1.2))
)

input_data = pd.DataFrame([{
    "HOME_FORM": home_form,
    "AWAY_FORM": away_form,
    "HOME_AVG_GOALS": home_avg_goals,
    "AWAY_AVG_GOALS": away_avg_goals,
}])

if st.sidebar.button("Show Probabilities"):
    st.subheader(f"{home_team} vs {away_team}")

    for market, model in models.items():
        if not hasattr(model, "predict_proba"):
            st.warning(f"{market}: model has no probability outputs.")
            continue

        probs = model.predict_proba(input_data)[0]
        classes = list(model.classes_)

        # Friendly labels per market
        if market == "HDA":
            label_map = { -1: "Away Win", 0: "Draw", 1: "Home Win" }
        elif market == "OVER25":
            label_map = { 0: "Under 2.5", 1: "Over 2.5" }
        elif market == "BTTS":
            label_map = { 0: "No", 1: "Yes" }
        elif market == "DOUBLE_CHANCE":
            label_map = { 0: "Away Win Only", 1: "Home or Draw" }
        else:
            label_map = {c: str(c) for c in classes}

        labels = [label_map.get(c, str(c)) for c in classes]
        prob_df = pd.DataFrame({"Class": labels, "Probability": probs})

        st.markdown(f"### {market}")
        st.bar_chart(prob_df.set_index("Class"))
