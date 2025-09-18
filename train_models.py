#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv('E0.csv')

# ============================================================
# Step 1: Calculate Form (rolling points over last 5 matches)
# ============================================================
def get_points(row, venue):
    if venue == "home":
        if row["FTHG"] > row["FTAG"]:
            return 3
        elif row["FTHG"] == row["FTAG"]:
            return 1
        else:
            return 0
    else:  # away
        if row["FTAG"] > row["FTHG"]:
            return 3
        elif row["FTAG"] == row["FTHG"]:
            return 1
        else:
            return 0

# Match points
df["HOME_POINTS"] = df.apply(lambda row: get_points(row, "home"), axis=1)
df["AWAY_POINTS"] = df.apply(lambda row: get_points(row, "away"), axis=1)

# Rolling form (last 5 matches)
df["HOME_FORM"] = (
    df.groupby("HomeTeam")["HOME_POINTS"]
      .transform(lambda x: x.rolling(5, min_periods=1).sum())
)

df["AWAY_FORM"] = (
    df.groupby("AwayTeam")["AWAY_POINTS"]
      .transform(lambda x: x.rolling(5, min_periods=1).sum())
)

# ============================================================
# Step 2: Average Goals (last 5 matches)
# ============================================================
df["HOME_GOALS"] = df["FTHG"]
df["AWAY_GOALS"] = df["FTAG"]

# Rolling average goals scored
df["HOME_AVG_GOALS"] = (
    df.groupby("HomeTeam")["HOME_GOALS"]
      .transform(lambda x: x.rolling(5, min_periods=1).mean())
)

df["AWAY_AVG_GOALS"] = (
    df.groupby("AwayTeam")["AWAY_GOALS"]
      .transform(lambda x: x.rolling(5, min_periods=1).mean())
)

# ============================================================
# Step 3: Create Target Variables (Markets)
# ============================================================
def get_hda(row):
    if row["FTHG"] > row["FTAG"]:
        return 1   # Home win
    elif row["FTHG"] == row["FTAG"]:
        return 0   # Draw
    else:
        return -1  # Away win

df["HDA"] = df.apply(get_hda, axis=1)
df["OVER25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)
df["BTTS"] = ((df["FTHG"] > 0) & (df["FTAG"] > 0)).astype(int)
df["DOUBLE_CHANCE"] = ((df["FTHG"] >= df["FTAG"])).astype(int)

# ============================================================
# Step 4: Train Models for Each Market
# ============================================================
features = ["HOME_FORM", "AWAY_FORM", "HOME_AVG_GOALS", "AWAY_AVG_GOALS"]

markets = {
    "HDA": df["HDA"],
    "OVER25": df["OVER25"],
    "BTTS": df["BTTS"],
    "DOUBLE_CHANCE": df["DOUBLE_CHANCE"],
}

models = {}

for market, target in markets.items():
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], target, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"===== {market} =====")
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, f"MODEL_{market}.pkl")
    models[market] = model


# In[5]:


print(df.head(20))


# In[ ]:




