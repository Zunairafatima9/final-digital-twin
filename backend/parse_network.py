import xml.etree.ElementTree as ET
import json

NET_FILE = "../data/network/network.net.xml"
OUTPUT_FILE = "../outputs/tracks.geojson"

tree = ET.parse(NET_FILE)
root = tree.getroot()

features = []

for edge in root.findall("edge"):

    if edge.get("function") == "internal":
        continue

    for lane in edge.findall("lane"):

        shape = lane.get("shape")

        if shape is None:
            continue

        coords = []

        points = shape.split(" ")

        for p in points:

            x,y = map(float,p.split(","))

            coords.append([x,y])

        feature = {
            "type":"Feature",
            "geometry":{
                "type":"LineString",
                "coordinates":coords
            }
        }

        features.append(feature)

geojson = {
    "type":"FeatureCollection",
    "features":features
}

with open(OUTPUT_FILE,"w") as f:
    json.dump(geojson,f)

print("Tracks exported to GeoJSON")