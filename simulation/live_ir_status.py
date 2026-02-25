import requests
import time
import csv

API_KEY = "rr_r2b5uv5yut817x8g7q5ql46sfw1av2sz"
BASE_URL = "https://api.railradar.org/api/v1"

REFRESH_INTERVAL = 90  # seconds

# Fetch both directions
STATION_PAIRS = [
    ("HWH", "BDC"),  # Howrah → Bandel
    ("BDC", "HWH")   # Bandel → Howrah
]


# --------------------------------------------------
# 1️⃣ Get trains running between two stations
# --------------------------------------------------
def fetch_trains_between(from_station, to_station):

    url = f"{BASE_URL}/trains/between"
    headers = {"X-API-Key": API_KEY}
    params = {
        "from": from_station,
        "to": to_station
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()

        if not data.get("success"):
            print(f"Between API unsuccessful for {from_station} → {to_station}")
            return []

        trains = data["data"].get("trains", [])
        train_numbers = [t["trainNumber"] for t in trains]

        print(f"Found {len(train_numbers)} trains between {from_station} and {to_station}")

        return train_numbers

    except Exception as e:
        print("Between API error:", e)
        return []


# --------------------------------------------------
# 2️⃣ Fetch live GPS for each train
# --------------------------------------------------
def fetch_live_train(train_no):

    url = f"{BASE_URL}/trains/{train_no}"
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()

        if not data.get("success"):
            return None

        live = data["data"].get("liveData", {})
        current_loc = live.get("currentLocation", {})

        latitude = current_loc.get("latitude")
        longitude = current_loc.get("longitude")

        if latitude is None or longitude is None:
            return None

        route_list = live.get("route", [])
        delay_minutes = 0

        if route_list:
            latest_stop = route_list[-1]
            delay_minutes = (
                latest_stop.get("delayDepartureMinutes")
                or latest_stop.get("delayArrivalMinutes")
                or 0
            )

        return {
            "train_id": str(train_no),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "delay_minutes": delay_minutes,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"Live fetch error {train_no}:", e)
        return None


# --------------------------------------------------
# Save CSV
# --------------------------------------------------
def save_live_data(data_list):

    with open("../outputs/live_status.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "train_id",
                "latitude",
                "longitude",
                "delay_minutes",
                "timestamp",
            ],
        )
        writer.writeheader()
        writer.writerows(data_list)


# ====================================================
# CONTINUOUS LOOP
# ====================================================
if __name__ == "__main__":

    print("🚆 Corridor Live Digital Twin (Bi-Directional Mode)")

    while True:

        results = []
        all_train_numbers = set()

        # Step 1: Fetch trains for both directions
        for from_station, to_station in STATION_PAIRS:

            trains = fetch_trains_between(from_station, to_station)

            for train_no in trains:
                all_train_numbers.add(train_no)

        print(f"Total unique corridor trains: {len(all_train_numbers)}")

        # Step 2: Fetch live GPS for each unique train
        for train_no in all_train_numbers:

            status = fetch_live_train(train_no)

            if status:
                print("LIVE:", status["train_id"])
                results.append(status)

        # Step 3: Save results
        if results:
            save_live_data(results)
            print(f"Saved {len(results)} live trains")
        else:
            print("No live trains currently active")

        time.sleep(REFRESH_INTERVAL)