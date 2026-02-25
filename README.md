🚆 Railway Digital Twin using SUMO
Howrah – Bally – Serampore – Chandannagar – Chuchura – Bandel Corridor

📌 Project Overview

This project implements a real-time railway digital twin of the Howrah–Bandel suburban corridor using:
SUMO (Simulation of Urban Mobility)
TraCI (Python control interface)
Live railway API integration
Custom railway control logic

The system models:
✔ Separate UP/DOWN infrastructure
✔ Separate FAST/SLOW lines
✔ Platform capacity constraints
✔ Absolute block signaling
✔ Junction interlocking
✔ Train priority hierarchy
✔ Overtake detection
✔ Dynamic line switching
✔ Delay-aware operations
✔ Live bi-directional train injection
✔ Corridor congestion analytics
✔ CSV-based performance logging

This is a railway-grade operational simulator, not just a traffic animation.

🏗️ 1️⃣ Building the Railway Network
Step 1: Extract Railway Network from OpenStreetMap
Export OSM file covering:
Howrah (HWH)
Bally
Serampore
Chandannagar
Chuchura
Bandel (BDC)

Save as:
data/howrah_bandel.osm
Step 2: Convert OSM → SUMO Network

Use netconvert:

netconvert \
  --osm-files data/howrah_bandel.osm \
  --output-file data/network.net.xml \
  --proj.utm true \
  --railway.topology.repair true \
  --osm.railway.oneway false \
  --osm.railway.guess-signals true \
  --junctions.join true \
  --geometry.remove false

This generates:
network.net.xml

🚄 2️⃣ Route Architecture (FAST / SLOW Segregation)
Routes defined in:
routes.rou.xml
We define:
Direction	Fast Line	Slow Line
UP	UP_FAST	UP_SLOW
DOWN	DOWN_FAST	DOWN_SLOW
Example:
<route id="UP_FAST" edges="1311347647#0 ... 367611317#1"/>
<route id="UP_SLOW" edges="372219772#0 ... 367611317#1"/>
<route id="DOWN_FAST" edges="810347763#1 ... 521495092#13"/>
<route id="DOWN_SLOW" edges="810347762#0 ... 380964042#8"/>
FAST and SLOW diverge at junctions.

🚉 3️⃣ Platform Modeling

Platforms defined as busStops:

<busStop id="HOWRAH_UP_SLOW"
         lane="372172712_0"
         startPos="100"
         endPos="400"/>

<busStop id="BANDEL_UP_SLOW"
         lane="521495092#7_0"
         startPos="200"
         endPos="500"/>

Features:
✔ Separate UP/DOWN platforms
✔ Separate FAST/SLOW platforms
✔ Platform capacity = 1
✔ Headway departure control

🌐 4️⃣ Live Data Integration
live_ir_status.py
Uses Railway API:
BASE_URL = "https://api.railradar.org/api/v1"

Steps:
Fetch trains between HWH ↔ BDC
Fetch live GPS for each train

Extract:
train_id
latitude
longitude
delay_minutes

Save to:
live_status.csv
Example output:

train_id,latitude,longitude,delay_minutes,timestamp
37215,22.8632,88.3421,3,1700000000
Live refresh interval: 90 seconds.

🧠 5️⃣ Digital Twin Engine
Main control file:

run_digital_twin.py
🚦 Core Layers
1️⃣ Live Train Injection
Reads live_status.csv
Classifies train type
Assigns route (FAST/SLOW + UP/DOWN)
Sets max speed based on type

2️⃣ Train Type Classification
Type	Priority	Speed (m/s)
SUPERFAST	5	44
EXPRESS	4	36
PASSENGER	3	30
EMU	2	28
FREIGHT	1	22
3️⃣ Absolute Block Signaling
Block length: 1200m
block_id = f"{edge}_{int(position//BLOCK_LENGTH)}"
Only one train per block.
Prevents rear-end collisions.

4️⃣ Junction Interlocking
Critical junction edges:
CRITICAL_JUNCTION_EDGES = [
    "44629483",
    "44629484",
    "44629491"
]
Logic:
✔ First train locks junction
✔ Higher priority can override
✔ Lower priority halted
This simulates movement authority.

5️⃣ Overtake Detection Engine
At overtaking zones:
OVERTAKE_EDGES = [
    "521712768",
    "385081047"
]
If:
Faster train behind slower train
Gap < 80m
Higher priority
Then:
Slow train forced to reduce speed

6️⃣ Dynamic Line Switching
If congestion > threshold:
✔ EXPRESS may shift FAST → SLOW
✔ Only if current edge exists in new route
✔ Safe route replacement logic
Prevents illegal route changes.

7️⃣ Congestion Index
congestion = 1 - (avg_speed / 44)
Values:
0.0 → Free flow
0.3 → Moderate
0.6 → Heavy
0.8+ → Severe congestion

📊 6️⃣ Output & Analytics
Simulation logs saved to:
simulation_results.csv
Columns:
step,
active_trains,
avg_speed,
congestion_index,
overtake_events,
junction_conflicts,
dynamic_switches

Used for:

✔ Delay propagation analysis
✔ Capacity study
✔ Bottleneck detection
✔ Overtake frequency analysis
✔ Signal performance evaluation

🚀 7️⃣ Running the System
Step 1 — Start Live Poller
python live_ir_status.py
Step 2 — Start Digital Twin
python run_digital_twin.py

SUMO GUI launches automatically.


🧪 Research Capabilities
This system enables:
Railway capacity modeling
Delay amplification studies
Block occupancy analysis
Signal conflict simulation
Junction conflict evaluation
Priority-based dispatch research
Real-time corridor digital twin modeling

🔮 Future Enhancements
Predictive congestion forecasting
AI-based dispatcher
Timetable adherence scoring
Crossover switch modeling
Platform allocation optimizer
Delay ripple propagation matrix

🎯 System Summary
This project evolves from:
OSM railway extraction
→ SUMO network generation
→ FAST/SLOW infrastructure modeling
→ Platform & block logic
→ Live API ingestion
→ Signal + interlocking system
→ Priority-aware dispatch
→ Advanced analytics logging

It is now a multi-layer railway operational digital twin.
