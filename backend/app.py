from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVE_FILE = os.path.join(BASE_DIR, "..", "outputs", "live_trains.json")
LIVE_BLOCK_FILE = os.path.join(BASE_DIR, "..", "outputs", "live_blocks.json")
LIVE_EDGE_FILE = os.path.join(BASE_DIR, "..", "outputs", "live_edges.json")
import pandas as pd

RESULT_FILE = os.path.join(BASE_DIR, "..", "outputs", "simulation_results.csv")

@app.route("/metrics")
def metrics():

    if not os.path.exists(RESULT_FILE):
        return jsonify({})

    df = pd.read_csv(RESULT_FILE)

    if df.empty:
        return jsonify({})

    latest = df.iloc[-1]

    return jsonify({
        "active_trains": int(latest["active_trains"]),
        "avg_speed": round(latest["avg_speed"],2),
        "congestion": round(latest["congestion_index"],2),
        "conflicts": int(latest["junction_conflicts"])
    })

@app.route("/edges")
def edges():

    if not os.path.exists(LIVE_EDGE_FILE):
        return jsonify([])

    with open(LIVE_EDGE_FILE) as f:
        data = json.load(f)

    return jsonify(data)


@app.route("/trains")
def trains():

    try:

        if not os.path.exists(LIVE_FILE):
            return jsonify([])

        with open(LIVE_FILE,"r") as f:
            data = json.load(f)

        return jsonify(data)

    except Exception as e:

        print("TRAIN API ERROR:", e)
        return jsonify([])
import json

@app.route("/tracks")
def tracks():


    with open("../outputs/tracks.geojson") as f:
        data = json.load(f)

    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000)