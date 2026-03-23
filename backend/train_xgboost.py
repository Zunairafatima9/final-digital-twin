import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib

# ============================
# LOAD DATA
# ============================

df = pd.read_csv("../outputs/synthetic_training_data.csv")

print("Dataset shape:", df.shape)


# ============================
# FEATURES & TARGET
# ============================

X = df.drop(columns=["delay"])
y = df["delay"]


# ============================
# TRAIN TEST SPLIT
# ============================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ============================
# MODEL
# ============================

model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)


# ============================
# EVALUATION
# ============================

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n📊 Model Performance:")
print("MAE:", round(mae, 3))
print("R2 Score:", round(r2, 3))


# ============================
# FEATURE IMPORTANCE
# ============================

importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
}).sort_values(by="importance", ascending=False)

print("\n🔥 Feature Importance:")
print(importance)


# ============================
# SAVE MODEL
# ============================

joblib.dump(model, "../outputs/xgb_model.pkl")

print("\n✅ Model saved as xgb_model.pkl")