from sumolib.net import readNet

STATIONS = {
    "HOWRAH": (22.5832, 88.3431),
    "BALLY": (22.6509, 88.3443),
    "SHRIRAMPUR": (22.7522, 88.3436),
    "CHANDANNAGAR": (22.8664, 88.3811),
    "CHUCHURA": (22.8893, 88.3911),
    "BANDEL": (22.9302, 88.3792),
}

net = readNet("../data/network/network.net.xml")

SEARCH_RADII = [1000, 3000, 6000]  # meters (progressive fallback)

station_edges = {}

for name, (lat, lon) in STATIONS.items():
    x, y = net.convertLonLat2XY(lon, lat)

    found = False
    for radius in SEARCH_RADII:
        candidates = net.getNeighboringEdges(x, y, radius)

        if candidates:
            edge, dist = min(candidates, key=lambda e: e[1])
            station_edges[name] = (edge.getID(), dist)
            print(f"✅ {name}: edge={edge.getID()}, dist={dist:.1f} m (r={radius})")
            found = True
            break

    if not found:
        print(f"⚠️ {name}: NO EDGE FOUND even within {SEARCH_RADII[-1]} m")

print("\nFinal station → edge mapping:")
for k, v in station_edges.items():
    print(k, "→", v)
