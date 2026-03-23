import pandas as pd
import numpy as np

np.random.seed(42)

N = 5000   # number of samples

# ============================
# TRAIN TYPES
# ============================

train_types = ["EMU", "EXPRESS", "SUPERFAST", "FREIGHT"]

type_probs = [0.3, 0.3, 0.2, 0.2]

types = np.random.choice(train_types, size=N, p=type_probs)

# Priority mapping
priority_map = {
    "SUPERFAST": 5,
    "EXPRESS": 4,
    "EMU": 3,
    "FREIGHT": 1
}

priority = np.array([priority_map[t] for t in types])


# ============================
# FEATURES
# ============================

avg_speed = np.random.uniform(5, 40, N)

avg_gap = np.random.uniform(5, 300, N)

avg_congestion = np.random.uniform(0, 1, N)

avg_waiting = np.random.uniform(0, 600, N)

distance_remaining = np.random.uniform(0, 1, N)

# ============================
# DELAY FUNCTION (REALISTIC)
# ============================

delay = (
    (1 - avg_speed / 50) * 20 +
    (1 / (avg_gap + 1)) * 200 +
    avg_congestion * 30 +
    avg_waiting * 0.05 +
    (5 - priority) * 2
)

# Add noise
delay += np.random.normal(0, 2, N)

# No negative delays
delay = np.clip(delay, 0, None)
delay += (1 - distance_remaining) * 10


# ============================
# CREATE DATAFRAME
# ============================

df = pd.DataFrame({
    "avg_speed": avg_speed,
    "avg_gap": avg_gap,
    "avg_congestion": avg_congestion,
    "avg_waiting": avg_waiting,
    "type": types,
    "distance_remaining": distance_remaining,
    "delay": delay
})


# ============================
# ENCODING
# ============================

df = pd.get_dummies(df, columns=["type"])


# ============================
# SAVE
# ============================

df.to_csv("../outputs/synthetic_training_data.csv", index=False)

print("✅ Synthetic dataset created!")
print("Shape:", df.shape)
print(df.head())