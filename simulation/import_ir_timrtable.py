import pandas as pd
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_FILE = os.path.join(CURRENT_DIR, "ir_raw_timetable.csv")
OUTPUT_FILE = os.path.join(CURRENT_DIR, "timetable.csv")

if not os.path.exists(RAW_FILE):
    print("ir_raw_timetable.csv not found")
    exit()

df = pd.read_csv(RAW_FILE)

def hhmm_to_seconds(time_str):
    h, m = map(int, time_str.split(":"))
    return h * 3600 + m * 60

# Convert times
df["scheduled_arrival"] = df["arrival"].apply(hhmm_to_seconds)
df["scheduled_departure"] = df["departure"].apply(hhmm_to_seconds)

# Create SUMO train IDs
df["train_id"] = df["train_no"].astype(str)

# Keep only needed columns
df_final = df[[
    "train_id",
    "station",
    "scheduled_arrival",
    "scheduled_departure"
]]

# Sort properly (VERY IMPORTANT for SUMO stability)
df_final = df_final.sort_values(
    by=["scheduled_arrival"]
)

df_final.to_csv(OUTPUT_FILE, index=False)

print("✅ real_timetable.csv generated successfully")