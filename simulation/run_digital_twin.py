import os
import sys
import traci
import pandas as pd
import statistics
import csv
import json

# =====================================================
# CONFIG
# =====================================================



SUMO_BINARY = "sumo-gui"
SUMO_CONFIG = "sumo.sumocfg"

LIVE_FILE = "../outputs/live_status.csv"
LIVE_JSON = "../outputs/live_trains.json"
RESULT_CSV = "../outputs/simulation_results.csv"
TRAINING_CSV = "../outputs/ai_training_data.csv"

MAX_SIM_TIME = 3500
SPAWN_INTERVAL = 5

SAFE_HEADWAY = 40
OVERTAKE_DISTANCE = 200

# Passing loop / station edges
PLATFORM_OVERTAKE_EDGES = [
    "521712768",
    "385081047"
]

# Junction conflict edges
CRITICAL_JUNCTION_EDGES = [
    "44629483",
    "44629484",
    "44629491"
]

# =====================================================
# TRAIN PRIORITY
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
# STATE STORAGE
# =====================================================

spawn_queue = []
junction_locks = {}
metrics_log = []
completed_trains = set()
overtake_events = []
dynamic_switches = []

# =====================================================
# TRAIN CLASSIFICATION
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
        if train_type in ["EMU","PASSENGER","FREIGHT"]:
            return "UP_SLOW"
        else:
            return "UP_FAST"
    else:
        if train_type in ["EMU","PASSENGER","FREIGHT"]:
            return "DOWN_SLOW"
        else:
            return "DOWN_FAST"


# =====================================================
# MOVING BLOCK SIGNALING (FIXED)
# =====================================================

def enforce_headway():

    vehicles = traci.vehicle.getIDList()

    for v in vehicles:

        try:

            base = BASE_SPEED[classify(v)]
            leader = traci.vehicle.getLeader(v, SAFE_HEADWAY)

            if leader:

                leader_id, gap = leader

                if gap < SAFE_HEADWAY:

                    new_speed = max(5, gap * 0.8)
                    traci.vehicle.setSpeed(v,new_speed)

                else:

                    traci.vehicle.setSpeed(v,base)

            else:

                traci.vehicle.setSpeed(v,base)

        except:
            pass


# =====================================================
# INTELLIGENT DISPATCHER
# =====================================================

def intelligent_dispatch():

    vehicles = traci.vehicle.getIDList()

    for v in vehicles:

        try:

            leader = traci.vehicle.getLeader(v, 250)

            if not leader:
                continue

            leader_id, gap = leader

            v_priority = PRIORITY[classify(v)]
            leader_priority = PRIORITY[classify(leader_id)]

            if v_priority > leader_priority:

                traci.vehicle.setSpeed(
                    leader_id,
                    BASE_SPEED[classify(leader_id)] * 0.6
                )

        except:
            pass


# =====================================================
# PLATFORM OVERTAKING (SAFE)
# =====================================================

def platform_overtake():

    vehicles = traci.vehicle.getIDList()

    for v in vehicles:

        try:

            edge = traci.vehicle.getRoadID(v)

            if edge not in PLATFORM_OVERTAKE_EDGES:
                continue

            leader = traci.vehicle.getLeader(v, OVERTAKE_DISTANCE)

            if not leader:
                continue

            leader_id, gap = leader

            v_priority = PRIORITY[classify(v)]
            leader_priority = PRIORITY[classify(leader_id)]

            if v_priority <= leader_priority:
                continue

            lane = traci.vehicle.getLaneIndex(v)
            lanes = traci.edge.getLaneNumber(edge)

            if lane < lanes-1 and traci.vehicle.couldChangeLane(v,1):

                traci.vehicle.changeLane(v,lane+1,40)

                overtake_events.append((v,leader_id))

        except:
            pass


# =====================================================
# PREDICTIVE CONGESTION RELIEF
# =====================================================

def predictive_congestion():

    vehicles = traci.vehicle.getIDList()

    if not vehicles:
        return 0

    speeds = [traci.vehicle.getSpeed(v) for v in vehicles]
    avg_speed = statistics.mean(speeds)

    congestion_index = 1 - (avg_speed / 44)

    if congestion_index < 0.4:
        return 0

    switches = 0

    for v in vehicles:

        if classify(v) != "EXPRESS":
            continue

        try:

            current_edge = traci.vehicle.getRoadID(v)
            route_id = traci.vehicle.getRouteID(v)

            if "FAST" not in route_id:
                continue

            new_route_id = route_id.replace("FAST","SLOW")
            new_edges = traci.route.getEdges(new_route_id)

            if current_edge not in new_edges:
                continue

            traci.vehicle.setRouteID(v,new_route_id)

            dynamic_switches.append((v,route_id,new_route_id))

            switches += 1

        except:
            pass

    return switches


# =====================================================
# JUNCTION INTERLOCKING (DEADLOCK SAFE)
# =====================================================

def enforce_junctions():

    conflicts = 0
    vehicles = traci.vehicle.getIDList()

    for v in vehicles:

        try:

            edge = traci.vehicle.getRoadID(v)

            if edge not in CRITICAL_JUNCTION_EDGES:
                continue

            priority = PRIORITY[classify(v)]

            if edge not in junction_locks:

                junction_locks[edge] = v

            else:

                locked = junction_locks[edge]

                if locked not in vehicles:
                    junction_locks[edge] = v
                    continue

                locked_priority = PRIORITY[classify(locked)]

                if priority > locked_priority:

                    traci.vehicle.setSpeed(locked,5)
                    junction_locks[edge] = v

                else:

                    traci.vehicle.setSpeed(v,5)
                    conflicts += 1

        except:
            pass

    # auto release
    for edge in list(junction_locks.keys()):

        locked = junction_locks[edge]

        if locked not in vehicles:
            junction_locks.pop(edge)

    return conflicts


# =====================================================
# START SUMO
# =====================================================

sumoCmd = [SUMO_BINARY,"-c",SUMO_CONFIG,"--start","--quit-on-end"]

print("🚆 Starting Railway Digital Twin")

try:
    traci.start(sumoCmd)
except:
    print("SUMO failed to start")
    sys.exit()

step = 0
last_modified = 0
next_spawn = 0


# =====================================================
# SIMULATION LOOP
# =====================================================

while step < MAX_SIM_TIME:

    traci.simulationStep()

    # LIVE TRAIN INJECTION

    if os.path.exists(LIVE_FILE):

        mod = os.path.getmtime(LIVE_FILE)

        if mod != last_modified:

            last_modified = mod
            df = pd.read_csv(LIVE_FILE)

            spawn_queue.clear()

            for _,row in df.iterrows():
                arrived = traci.simulation.getArrivedIDList()

                for t in arrived:
                    completed_trains.add(t)

                train_id = str(int(float(row["train_id"])))
                lat = float(row["latitude"])

                ttype = classify(train_id)
                direction = detect_direction(lat)
                route = assign_route(ttype,direction)

                spawn_queue.append((train_id,route,ttype))


    if spawn_queue and step >= next_spawn:

        train_id,route,ttype = spawn_queue.pop(0)

        if train_id not in traci.vehicle.getIDList():

            try:

                first_edge = traci.route.getEdges(route)[0]

                if traci.edge.getLastStepVehicleNumber(first_edge) < 2:

                    traci.vehicle.add(train_id,route,typeID="LIVE_RAIL")

                    traci.vehicle.setMaxSpeed(
                        train_id,
                        BASE_SPEED[ttype]
                    )

            except:
                pass

        next_spawn = step + SPAWN_INTERVAL


    # CONTROL LAYERS

    enforce_headway()
    intelligent_dispatch()
    platform_overtake()

    junction_conflicts = enforce_junctions()
    switches = predictive_congestion()

    vehicles = traci.vehicle.getIDList()


    # EXPORT LIVE TRAIN POSITIONS

    live_trains = []

    for v in vehicles:

        try:

        # 📍 Position
            x,y = traci.vehicle.getPosition(v)
            lon,lat = traci.simulation.convertGeo(x,y)


        # 📦 Output

            live_trains.append({
                "id": str(v),
                "lat": float(lat),
                "lon": float(lon),
            })

        except:
            pass

    with open(LIVE_JSON,"w") as f:
        json.dump(live_trains,f)


    # METRICS

    if vehicles:

        speeds = [traci.vehicle.getSpeed(v) for v in vehicles]

        avg_speed = statistics.mean(speeds)

        congestion = 1 - (avg_speed/44)

    else:

        avg_speed = 0
        congestion = 0


    metrics_log.append([
    step,
    len(vehicles),
    avg_speed,
    congestion,
    len(overtake_events),
    junction_conflicts,
    switches,
])


    if step % 50 == 0:

        print(
        f"📊 Active:{len(vehicles)} | "
        f"AvgSpeed:{round(avg_speed,2)} | "
        f"Cong:{round(congestion,3)}"
        )

    step += 1


traci.close()


# =====================================================
# SAVE RESULTS
# =====================================================

with open(RESULT_CSV,"w",newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
    "step",
    "active_trains",
    "avg_speed",
    "congestion_index",
    "overtake_events",
    "junction_conflicts",
    "dynamic_switches",

])

    writer.writerows(metrics_log)


print("🚆 Simulation Complete — Results Saved")