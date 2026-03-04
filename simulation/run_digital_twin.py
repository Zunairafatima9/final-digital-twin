import os
import sys
import traci
import pandas as pd
import statistics
import csv

# =====================================================
# CONFIG
# =====================================================

SUMO_BINARY = "sumo-gui"
SUMO_CONFIG = "sumo.sumocfg"
LIVE_FILE = "../outputs/live_status.csv"

MAX_SIM_TIME = 3500
SPAWN_INTERVAL = 5
BLOCK_LENGTH = 800
RESULT_CSV = "../outputs/simulation_results.csv"

spawn_queue = []
block_occupancy = {}
junction_locks = {}
overtake_events = []
dynamic_switches = []

metrics_log = []

# =====================================================
# PRIORITY SYSTEM
# =====================================================

PRIORITY = {
    "SUPERFAST": 5,
    "EXPRESS": 4,
    "PASSENGER": 3,
    "EMU": 2,
    "FREIGHT": 1
}

BASE_SPEED = {
    "SUPERFAST": 44,
    "EXPRESS": 36,
    "PASSENGER": 30,
    "EMU": 28,
    "FREIGHT": 22
}

# =====================================================
# CLASSIFICATION
# =====================================================

def classify(train_id):
    num = int(train_id)

    if 37000 <= num < 38000:
        return "EMU"
    elif 15000 <= num < 16000:
        return "PASSENGER"
    elif 13000 <= num < 14000:
        return "EXPRESS"
    elif 22000 <= num < 23000:
        return "SUPERFAST"
    elif 63000 <= num < 64000:
        return "FREIGHT"
    return "EXPRESS"

def detect_direction(lat):
    return "UP" if lat > 22.8 else "DOWN"

def assign_route(train_type, direction):

    if direction == "UP":
        if train_type in ["EMU","FREIGHT","PASSENGER"]:
            return "UP_SLOW"
        else:
            return "UP_FAST"
    else:
        if train_type in ["EMU","FREIGHT","PASSENGER"]:
            return "DOWN_SLOW"
        else:
            return "DOWN_FAST"

# =====================================================
# BLOCK SIGNALING
# =====================================================

def get_block_id(vehicle):
    pos = traci.vehicle.getLanePosition(vehicle)
    edge = traci.vehicle.getRoadID(vehicle)
    return f"{edge}_{int(pos//BLOCK_LENGTH)}"

def enforce_blocks():
    block_occupancy.clear()
    vehicles = traci.vehicle.getIDList()

    for v in vehicles:
        block = get_block_id(v)
        if block not in block_occupancy:
            block_occupancy[block] = v
        else:
            traci.vehicle.setSpeed(v, 0)

# =====================================================
# JUNCTION INTERLOCKING WITH PRIORITY
# =====================================================

CRITICAL_JUNCTION_EDGES = [
    "44629483",
    "44629484",
    "44629491"
]

def enforce_junction_locking():
    conflicts = 0

    vehicles = traci.vehicle.getIDList()

    for v in vehicles:
        edge = traci.vehicle.getRoadID(v)

        if edge in CRITICAL_JUNCTION_EDGES:

            v_type = classify(v)
            v_priority = PRIORITY[v_type]

            if edge not in junction_locks:
                junction_locks[edge] = v
            else:
                locked_train = junction_locks[edge]
                locked_priority = PRIORITY[classify(locked_train)]

                if v_priority > locked_priority:
                    traci.vehicle.setSpeed(locked_train, 0)
                    junction_locks[edge] = v
                else:
                    traci.vehicle.setSpeed(v, 0)
                    conflicts += 1

    # release locks
    for edge in list(junction_locks.keys()):
        if junction_locks[edge] not in vehicles:
            junction_locks.pop(edge)

    return conflicts

# =====================================================
# OVERTAKING ZONES
# =====================================================

OVERTAKE_EDGES = [
    "521712768",
    "385081047"
]

def detect_overtakes():
    vehicles = traci.vehicle.getIDList()

    for v in vehicles:
        leader = traci.vehicle.getLeader(v, 200)

        if leader:
            leader_id, gap = leader
            if gap < 80:

                v_priority = PRIORITY[classify(v)]
                leader_priority = PRIORITY[classify(leader_id)]

                if v_priority > leader_priority:
                    traci.vehicle.setSpeed(leader_id, BASE_SPEED[classify(leader_id)] * 0.6)
                    overtake_events.append((v, leader_id))

# =====================================================
# DYNAMIC LINE SWITCHING
# =====================================================

def dynamic_line_switch(congestion):

    switches = 0

    if congestion <= 0.5:
        return 0

    vehicles = traci.vehicle.getIDList()

    for v in vehicles:

        ttype = classify(v)

        if ttype != "EXPRESS":
            continue

        try:
            current_route_id = traci.vehicle.getRouteID(v)
            current_edge = traci.vehicle.getRoadID(v)

            # Determine alternate route
            if "FAST" in current_route_id:
                new_route_id = current_route_id.replace("FAST", "SLOW")
            else:
                continue

            new_route_edges = traci.route.getEdges(new_route_id)

            # CRITICAL SAFETY CHECK
            if current_edge in new_route_edges:

                traci.vehicle.setRouteID(v, new_route_id)
                dynamic_switches.append((v, current_route_id, new_route_id))
                switches += 1

        except:
            continue

    return switches

# =====================================================
# START SUMO
# =====================================================

sumoCmd = [SUMO_BINARY,"-c",SUMO_CONFIG,"--start","--quit-on-end"]

print("🚆 Starting Advanced Railway Digital Twin")


try:
    traci.start(sumoCmd)
    
    
except:
    print("Failed to start SUMO")
    sys.exit()

step = 0
last_modified = 0
next_spawn_step = 0

while step < MAX_SIM_TIME:

    traci.simulationStep()

    # LIVE INJECTION
    if os.path.exists(LIVE_FILE):
        mod = os.path.getmtime(LIVE_FILE)

        if mod != last_modified:
            last_modified = mod
            df = pd.read_csv(LIVE_FILE)
            spawn_queue.clear()

            for _,row in df.iterrows():
                train_id = str(int(float(row["train_id"])))
                lat = float(row["latitude"])
                delay = float(row.get("delay_minutes",0))

                ttype = classify(train_id)
                direction = detect_direction(lat)
                route = assign_route(ttype,direction)

                spawn_queue.append((train_id,route,ttype))

    if spawn_queue and step >= next_spawn_step:

        train_id,route,ttype = spawn_queue.pop(0)

        if train_id not in traci.vehicle.getIDList():
            try:
                traci.vehicle.add(train_id, route, typeID="LIVE_RAIL")
                traci.vehicle.setMaxSpeed(train_id, BASE_SPEED[ttype])
            except:
                pass

        next_spawn_step = step + SPAWN_INTERVAL

    # CONTROL LAYERS
    enforce_blocks()
    junction_conflicts = enforce_junction_locking()
    detect_overtakes()

    vehicles = traci.vehicle.getIDList()
    count = len(vehicles)

    if count > 0:
        speeds = [traci.vehicle.getSpeed(v) for v in vehicles]
        avg_speed = statistics.mean(speeds)
        congestion = 1 - (avg_speed/44)
    else:
        avg_speed = 0
        congestion = 0

    switches = dynamic_line_switch(congestion)

    metrics_log.append([
        step,
        count,
        avg_speed,
        congestion,
        len(overtake_events),
        junction_conflicts,
        switches
    ])

    if step % 50 == 0:
        print(f"📊 Active:{count} | AvgSpeed:{round(avg_speed,2)} | Cong:{round(congestion,3)}")

    step += 1

traci.close()

# SAVE RESULTS

with open(RESULT_CSV,"w",newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "step",
        "active_trains",
        "avg_speed",
        "congestion_index",
        "overtake_events",
        "junction_conflicts",
        "dynamic_switches"
    ])
    writer.writerows(metrics_log)

print("🚆 Simulation Complete — Results Saved")
