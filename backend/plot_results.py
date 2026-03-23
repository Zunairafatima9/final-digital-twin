import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../outputs/simulation_results.csv")

# 1️⃣ Congestion over time
plt.figure()
plt.plot(df["step"], df["congestion_index"])
plt.xlabel("Time Step")
plt.ylabel("Congestion")
plt.title("Congestion Over Time")
plt.savefig("../outputs/congestion.png")


# 2️⃣ Average Speed
plt.figure()
plt.plot(df["step"], df["avg_speed"])
plt.xlabel("Time Step")
plt.ylabel("Speed")
plt.title("Average Speed Over Time")
plt.savefig("../outputs/speed.png")


# 3️⃣ Predicted Delay
plt.figure()
plt.plot(df["step"], df["avg_predicted_delay"])
plt.xlabel("Time Step")
plt.ylabel("Delay")
plt.title("Predicted Delay Over Time")
plt.savefig("../outputs/delay.png")

import matplotlib.pyplot as plt

no_ai = pd.read_csv("../outputs/simulation_results_no_ai.csv")
ai = pd.read_csv("../outputs/simulation_results.csv")

# Congestion comparison
plt.figure()
plt.plot(no_ai["step"], no_ai["congestion_index"], label="Without AI")
plt.plot(ai["step"], ai["congestion_index"], label="With AI")
plt.legend()
plt.title("Congestion Comparison")
plt.xlabel("Time")
plt.ylabel("Congestion")
plt.savefig("../outputs/congestion_comparison.png")


# Speed comparison
plt.figure()
plt.plot(no_ai["step"], no_ai["avg_speed"], label="Without AI")
plt.plot(ai["step"], ai["avg_speed"], label="With AI")
plt.legend()
plt.title("Speed Comparison")
plt.xlabel("Time")
plt.ylabel("Speed")
plt.savefig("../outputs/speed_comparison.png")

print("✅ Graphs saved")