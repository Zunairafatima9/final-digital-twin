from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json

app = Flask(__name__)
CORS(app)

LIVE_FILE = "../outputs/live_status.csv"


@app.route("/trains")
def trains():

    if not os.path.exists(LIVE_FILE):
        return jsonify([])

    df = pd.read_csv(LIVE_FILE)

    trains = []

    for _,row in df.iterrows():

        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue

        trains.append({
            "id": str(int(row["train_id"])),
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"]),
            "delay": float(row.get("delay_minutes",0))
        })

    return jsonify(trains)
import json

@app.route("/tracks")
def tracks():


    with open("../outputs/tracks.geojson") as f:
        data = json.load(f)

    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000)