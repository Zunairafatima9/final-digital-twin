import pandas as pd

# LOAD DATA
no_ai = pd.read_csv("../outputs/simulation_results_no_ai.csv")
ai = pd.read_csv("../outputs/simulation_results.csv")

# ============================
# AVERAGES
# ============================

avg_congestion_no_ai = no_ai["congestion_index"].mean()
avg_congestion_ai = ai["congestion_index"].mean()

avg_speed_no_ai = no_ai["avg_speed"].mean()
avg_speed_ai = ai["avg_speed"].mean()

# ============================
# PERCENT CHANGE
# ============================

congestion_reduction = (
    (avg_congestion_no_ai - avg_congestion_ai) / avg_congestion_no_ai
) * 100

speed_improvement = (
    (avg_speed_ai - avg_speed_no_ai) / avg_speed_no_ai
) * 100

# ============================
# PRINT RESULTS
# ============================

print("\n📊 RESULTS COMPARISON\n")

print(f"Avg Congestion (No AI): {avg_congestion_no_ai:.3f}")
print(f"Avg Congestion (AI): {avg_congestion_ai:.3f}")
print(f"➡️ Congestion Reduction: {congestion_reduction:.2f}%")

print()

print(f"Avg Speed (No AI): {avg_speed_no_ai:.2f}")
print(f"Avg Speed (AI): {avg_speed_ai:.2f}")
print(f"➡️ Speed Improvement: {speed_improvement:.2f}%")